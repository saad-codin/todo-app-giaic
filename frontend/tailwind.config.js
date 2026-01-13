/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        priority: {
          high: '#ef4444',    // red-500
          medium: '#f59e0b',  // amber-500
          low: '#22c55e',     // green-500
        },
      },
    },
  },
  plugins: [],
}
