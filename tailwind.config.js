/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')
module.exports = {
  content: ["./templates/*.html", "./static/js/*.js"],
  theme: {
    colors: {
      ...colors,
      'primary': '#1a1a1a',
      'secondary': 'rgba(255,255,255,.15)',
      'tranparent': 'transparent',
      'dark': '#aaa',
    },
    fontFamily: {
      'sans': ['Roboto', 'sans-serif'],
    },
    extend: {},
  },
  plugins: [],
}

