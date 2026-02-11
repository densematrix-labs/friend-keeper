/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Soft organic palette
        cream: {
          50: '#FFFDF5',
          100: '#FDF8E8',
          200: '#F9EDCC',
          300: '#F5E1B0',
        },
        sage: {
          100: '#E8F0E8',
          200: '#C9DBC9',
          300: '#A8C4A8',
          400: '#7BA67B',
          500: '#5A8A5A',
          600: '#4A7A4A',
        },
        peach: {
          100: '#FFF0EB',
          200: '#FFD6C9',
          300: '#FFBBA7',
          400: '#FF9F85',
          500: '#E88571',
        },
        warmGray: {
          100: '#F5F3F0',
          200: '#E8E4E0',
          300: '#D6D0C8',
          400: '#B8AFA3',
          500: '#9A8F82',
          600: '#6B6158',
          700: '#4A443E',
          800: '#2E2A26',
        }
      },
      fontFamily: {
        display: ['"DM Serif Display"', 'Georgia', 'serif'],
        body: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'soft': '1rem',
        'softer': '1.5rem',
      },
      boxShadow: {
        'soft': '0 4px 20px rgba(107, 97, 88, 0.08)',
        'softer': '0 8px 40px rgba(107, 97, 88, 0.12)',
      }
    },
  },
  plugins: [],
}
