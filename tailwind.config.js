/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/*.html",  // Scan Flask templates for Tailwind classes
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}