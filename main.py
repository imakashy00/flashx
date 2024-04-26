from typing import Optional, Any
from fastapi import FastAPI, Request, Form, File, UploadFile, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from jose import JWTError
from Mongo.user import get_current_user
from fastapi.middleware.cors import CORSMiddleware
from Mongo import user
from fastapi import Cookie
from Mongo.connection import database
from gemini.extract_text import extract_text_from_pdf, split_into_chunks
from gemini.freeform import generate_flash, generate_quizz, generate_summary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(user.router)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

db = database('flashx')


# ////////////////////////////////////////////////////////////////////////////////////////////////////
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/create")
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})




@app.post("/submit-form")
async def submit_form(topic: Optional[str] = Form(None), file: Optional[UploadFile] = File(None),
                      quantity: int = Form(...), action: str = Form(...)):
    if file and file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file.file)
        tokens = split_into_chunks(text)
        if action == 'quizzes':
            generate_quizz(tokens, True, quantity)

        if action == 'flashes':
            generate_flash(tokens, True, quantity)

        if action == 'summary':
            generate_summary(tokens, True, quantity)

    if topic is not None and len(topic.strip()) > 0:
        if action == 'quizzes':
            generate_quizz(topic, False, quantity)

        if action == 'flashes':
            generate_flash(topic, False, quantity)

        if action == 'summary':
            generate_summary(topic, False, quantity)



@app.get("/quizz", response_class=FileResponse)
async def get_quizz(request: Request):
    return templates.TemplateResponse("quizz.html", {"request": request})


@app.get("/about", response_class=FileResponse)
async def get_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/flash", response_class=FileResponse)
async def get_flash(request: Request):
    return templates.TemplateResponse("flash.html", {"request": request})


@app.get("/summary", response_class=FileResponse)
async def get_summary(request: Request):
    return templates.TemplateResponse("summary.html", {"request": request})


@app.get("/register")
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/quizlist")
async def get_quizzes():
    quizzes_cursor = db.get_collection('quizzes_collection').find()  # Query all quizzes
    quizzes_list = list(quizzes_cursor)  # Convert cursor to list
    for quiz in quizzes_list:
        quiz["_id"] = str(quiz["_id"])  # Convert ObjectId to string for JSON compatibility
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(quizzes_list))


@app.get("/flashlist")
async def get_flashes(request: Request):
    flashes_cursor = db.get_collection('flashcards_collection').find()
    flash_list = list(flashes_cursor)  # Convert cursor to list
    for flash in flash_list:
        flash["_id"] = str(flash["_id"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(flash_list))


@app.get("/summarylist")
async def get_summary():
    summary_cursor = db.get_collection('summaries_collection').find()  # Query all quizzes
    summary_list = list(summary_cursor)  # Convert cursor to list
    for point in summary_list:
        point["_id"] = str(point["_id"])  # Convert ObjectId to string for JSON compatibility
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(summary_list))
