import type { Config } from "tailwindcss";

/**
 * KAVACH AI — "Containment Console" design tokens.
 * Graphite-navy control-room surfaces, signal-teal primary, SOC status semantics.
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
        canvas: "#080B11",
        surface: {
          DEFAULT: "#0E1420",
          raised: "#141C2A",
          inset: "#0A0F18",
        },
        line: {
          DEFAULT: "#1E2A3B",
          strong: "#2A3A50",
        },
        ink: {
          DEFAULT: "#E7EDF5",
          muted: "#8A98AC",
          faint: "#5A6883",
        },
        signal: {
          DEFAULT: "#3DD4C0",
          dim: "#1F6D64",
          glow: "#5EEAD8",
        },
        caution: "#FFB020",
        danger: "#FF4D6D",
        verified: "#34D399",
        info: "#5B9DFF",
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
        panel: "0 1px 0 0 rgba(255,255,255,0.02) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(61,212,192,0.35), 0 0 24px -4px rgba(61,212,192,0.35)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(30,42,59,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(30,42,59,0.35) 1px, transparent 1px)",
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
