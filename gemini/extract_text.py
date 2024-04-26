import PyPDF2
import nltk
# nltk.download('punkt')
from nltk.tokenize import word_tokenize


def extract_text_from_pdf(pdf_file):
    # Open the PDF file
    if type(pdf_file)==str:
        with open(pdf_file, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            # Initialize an empty string to store the extracted text
            text = ''
            # Iterate through each page of the PDF
            for page_num in range(len(pdf_reader.pages)):
                # Get the page object
                page = pdf_reader.pages[page_num]
                # Extract text from the page
                text += page.extract_text()
            # Return the extracted text
            return text
    else:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Initialize an empty string to store the extracted text
        text = ''
        # Iterate through each page of the PDF
        for page_num in range(len(pdf_reader.pages)):
            # Get the page object
            page = pdf_reader.pages[page_num]
            # Extract text from the page
            text += page.extract_text()
        # Return the extracted text
        return text



# Function to split tokens into chunks
def split_into_chunks(text):
    tokens = word_tokenize(text)
    chunk_size = 5000
    text_array = []
    for i in range(0, len(tokens), chunk_size):
        text_array.append(' '.join(tokens[i:i + chunk_size]))
    return text_array
