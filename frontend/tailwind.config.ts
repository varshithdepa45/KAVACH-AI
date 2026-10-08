import type { Config } from "tailwindcss";

/**
 * KAVACH AI — "Neon Control Room" design tokens.
 * Deep indigo surfaces with bright aqua, lime, orange, and cobalt signals.
 */
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#ffffff",
        surface: {
          DEFAULT: "#ffffff",
          raised: "#fafafa",
          inset: "#f3f4f6",
        },
        line: {
          DEFAULT: "#d8e3ef",
          strong: "#afc1d6",
        },
        ink: {
          DEFAULT: "#15233b",
          muted: "#52647d",
          faint: "#7d8da4",
        },
        signal: {
          DEFAULT: "#078c94",
          dim: "#0b6870",
          glow: "#2ccbd0",
        },
        caution: "#bd7000",
        danger: "#d94747",
        verified: "#5d8f00",
        info: "#1769c2",
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.04em" }],
      },
      boxShadow: {
        panel:
          "0 1px 0 0 rgba(255,255,255,0.9) inset, 0 12px 28px -18px rgba(38,65,96,0.3)",
        glow: "0 0 0 1px rgba(7,140,148,0.3), 0 0 22px -8px rgba(7,140,148,0.35)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(7,140,148,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(23,105,194,0.09) 1px, transparent 1px)",
      },
      keyframes: {
        pulseline: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(400%)" },
        },
        blip: {
          "0%,100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
        flow: {
          "0%": { strokeDashoffset: "24" },
          "100%": { strokeDashoffset: "0" },
        },
        sweep: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        fadein: {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        pulseline: "pulseline 2.2s cubic-bezier(0.4,0,0.2,1) infinite",
        blip: "blip 1.6s ease-in-out infinite",
        flow: "flow 1s linear infinite",
        sweep: "sweep 3.5s linear infinite",
        fadein: "fadein 0.35s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
