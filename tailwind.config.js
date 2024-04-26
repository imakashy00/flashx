/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.{html,js,jsx,ts,tsx,vue,css}"],
    theme: {
        extend: {
            maxWidth: {
                '24': '96rem'
            }
        },
    },
    plugins: [],
}