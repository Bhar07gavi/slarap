/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#070a13',
          900: '#0b0f19',
          850: '#0f172a',
          800: '#1e293b',
          700: '#334155',
          600: '#475569',
        },
        brand: {
          blue: '#38bdf8',
          green: '#4ade80',
          yellow: '#facc15',
          red: '#f87171',
          purple: '#c084fc',
        }
      },
    },
  },
  plugins: [],
}
