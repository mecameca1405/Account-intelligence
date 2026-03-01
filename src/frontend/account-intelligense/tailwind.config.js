/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        app: "var(--bg-app)",
        page: "var(--bg-page)",
        card: "var(--bg-card)",
        hover: "var(--bg-hover)",

        brand: {
          DEFAULT: "var(--brand-primary)",
          dark: "var(--brand-dark)",
          accent: "var(--brand-accent)",
        },

        text: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
          disabled: "var(--text-disabled)",
        },

        success: "var(--success)",
        info: "var(--info)",
        error: "var(--error)",
        warning: "var(--warning)",

        secondaryBtn: "var(--btn-secondary)",
        border: "var(--border)",
      },
    },
  },
  plugins: [],
};
