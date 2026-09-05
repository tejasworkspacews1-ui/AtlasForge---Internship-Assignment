/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian: {
          900: "#05070d",
          800: "#0a0e18",
          700: "#0f1422",
          600: "#151b2e",
          500: "#1c2440",
        },
        accent: {
          cyan: "#22d3ee",
          violet: "#a78bfa",
          amber: "#fbbf24",
          emerald: "#34d399",
          rose: "#fb7185",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)",
        glow: "0 0 24px rgba(34,211,238,0.25)",
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at 50% 0%, rgba(34,211,238,0.08), transparent 60%)",
      },
    },
  },
  plugins: [],
};
