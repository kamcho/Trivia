/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./home/templates/**/*.html",
    "./**/templates/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#4a6cf7',
          dark: '#3453e6'
        },
        surface: '#111827'
      }
    }
  },
  plugins: []
}


