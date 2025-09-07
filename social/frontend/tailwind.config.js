/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../**/templates/**/*.html", // تمپلیت‌های کل پروژه
    "./templates/**/*.html",     // تمپلیت‌های خود frontend
  ],
  theme: {
    extend: {
      colors: {
        navy: '#0f172a',
        sky: '#38bdf8',
      },
      fontFamily: {
        sans: ['ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
}
