export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        traffic: {
          green: '#10b981',
          yellow: '#f59e0b',
          red: '#ef4444',
        }
      }
    },
  },
  plugins: [],
}