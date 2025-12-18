/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'kaygee': {
          'cyan': '#22d3ee',
          'purple': '#a855f7',
          'dark': '#0f172a',
        }
      }
    },
  },
  plugins: [],
}
