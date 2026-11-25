/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: {
          950: "#030712", // Base deepest black-navy
          900: "#060b19", // Midnight base
          850: "#091124", // Layer 1 glass surface
          800: "#0d1830", // Layer 2 card surface
          700: "#162548", // Border and elevation line
          600: "#1e335f",
        },
        aqua: {
          300: "#67e8f9",
          400: "#22d3ee",
          500: "#06b6d4",
          600: "#0891b2",
        },
        aqi: {
          good: "#10b981",
          moderate: "#eab308",
          sensitive: "#f97316",
          unhealthy: "#ef4444",
          veryUnhealthy: "#a855f7",
          hazardous: "#7f1d1d",
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"SF Pro Display"',
          '"SF Pro Text"',
          '"Segoe UI"',
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          '"SF Mono"',
          "Menlo",
          "Monaco",
          "Consolas",
          '"Liberation Mono"',
          "monospace",
        ],
      },
      boxShadow: {
        "glass-sm": "0 4px 16px -2px rgba(0, 0, 0, 0.4), inset 0 1px 0 0 rgba(255, 255, 255, 0.12)",
        "glass-md": "0 8px 32px -4px rgba(0, 0, 0, 0.5), inset 0 1px 1px 0 rgba(255, 255, 255, 0.16)",
        "glass-lg": "0 20px 48px -8px rgba(0, 0, 0, 0.65), inset 0 1px 1px 0 rgba(255, 255, 255, 0.22)",
        "glow-emerald": "0 0 25px -4px rgba(16, 185, 129, 0.25)",
        "glow-cyan": "0 0 25px -4px rgba(6, 182, 212, 0.25)",
      },
      transitionTimingFunction: {
        apple: "cubic-bezier(0.16, 1, 0.3, 1)",
      },
    },
  },
  plugins: [],
}
