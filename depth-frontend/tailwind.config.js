/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#060d1a",
          900: "#0a1628",
          800: "#0d1f3c",
          700: "#102850",
        },
        teal: {
          ocean: "#0d7377",
          deep: "#0a5c60",
        },
        cyan: {
          bio: "#14ffec",
          dim: "#0fd4c4",
        },
      },
      fontFamily: {
        display: ["DM Serif Display", "Georgia", "serif"],
        mono: ["DM Mono", "Courier New", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "sonar-ping": "sonarPing 2s cubic-bezier(0, 0, 0.2, 1) infinite",
        "sonar-ping-delay": "sonarPing 2s cubic-bezier(0, 0, 0.2, 1) infinite 0.75s",
        typewriter: "typewriter 0.05s steps(1) forwards",
        "surface-up": "surfaceUp 0.6s ease-out forwards",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "depth-glow": "depthGlow 3s ease-in-out infinite alternate",
      },
      keyframes: {
        sonarPing: {
          "0%": { transform: "scale(0.8)", opacity: "0.8" },
          "100%": { transform: "scale(2.5)", opacity: "0" },
        },
        surfaceUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        depthGlow: {
          "0%": { boxShadow: "0 0 20px rgba(20, 255, 236, 0.1)" },
          "100%": { boxShadow: "0 0 60px rgba(20, 255, 236, 0.25)" },
        },
      },
    },
  },
  plugins: [],
};
