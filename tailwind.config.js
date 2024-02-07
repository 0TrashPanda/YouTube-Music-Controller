/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html"],
  theme: {
    colors: {
      'primary': '#1a1a1a',
      'secondary': 'rgba(255,255,255,.15)',
      'tranparent': 'transparent',
    },
    fontFamily: {
      'sans': ['Roboto', 'sans-serif'],
    },
    extend: {},
  },
  plugins: [],
}

