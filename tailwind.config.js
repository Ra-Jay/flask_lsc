/** @type {import('tailwindcss').Config} */
module.exports = {
  purge: ['./templates/index.html'],
  content: [],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
}

