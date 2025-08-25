import { createTheme } from "@mui/material/styles";

const theme = {
  direction: "rtl",
  palette: {
    primary: {
      main: "#1565c0",
      light: "#5e92f3",
      dark: "#003c8f",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#90caf9",
      light: "#e3f2fd",
      dark: "#42a5f5",
      contrastText: "#003c8f",
    },
    background: {
      default: "#f4faff",
      paper: "#ffffff",
      secondary: "#e3f2fd",
    },
    text: {
      primary: "#003c8f",
      secondary: "#1565c0",
      disabled: "#9e9e9e",
    },
    accent: {
      main: "#1e88e5",
      contrastText: "#ffffff",
    },
    info: {
      main: "#29b6f6",
      contrastText: "#ffffff",
    },
    success: {
      main: "#4caf50",
      contrastText: "#ffffff",
    },
    error: {
      main: "#e53935",
      contrastText: "#ffffff",
    },
    warning: {
      main: "#fb8c00",
      contrastText: "#ffffff",
    },
    divider: "rgba(21, 101, 192, 0.2)",
    status: {
      pending: "#e3b448",
      approved: "#00ab41",
      collected: "#1d63dc",
      returned: "#c9d5db",
      rejected: "#a0522d",
      undefined: "#000000",
    },
  },
  typography: {
    fontFamily: [
      "Segoe UI",
      "Assistant",
      "Heebo",
      "Rubik",
      "Arial",
      "sans-serif",
    ].join(","),
    h1: {
      fontWeight: 700,
      fontSize: "2.8rem",
      color: "#003c8f",
      letterSpacing: "-0.5px",
      textShadow: "1px 1px 3px rgba(21, 101, 192, 0.1)",
    },
    h2: {
      fontWeight: 600,
      fontSize: "2.4rem",
      color: "#003c8f",
      letterSpacing: "-0.3px",
    },
    h3: {
      fontWeight: 600,
      fontSize: "2rem",
      color: "#1565c0",
    },
    h4: {
      fontWeight: 600,
      fontSize: "1.5rem",
      color: "#1565c0",
    },
    h5: {
      fontWeight: 500,
      fontSize: "1.25rem",
      color: "#1565c0",
    },
    h6: {
      fontWeight: 500,
      fontSize: "1rem",
      color: "#1565c0",
    },
    body1: {
      fontSize: "1rem",
      lineHeight: 1.7,
      color: "#003c8f",
      fontWeight: 400,
    },
    body2: {
      fontSize: "0.875rem",
      lineHeight: 1.6,
      color: "#1565c0",
      fontWeight: 400,
    },
    button: {
      fontWeight: 600,
      textTransform: "none",
      letterSpacing: "0.3px",
      color: "#003c8f",
    },
    caption: {
      fontSize: "0.75rem",
      color: "#5e92f3",
      fontWeight: 400,
    },
    overline: {
      fontSize: "0.75rem",
      color: "#5e92f3",
      fontWeight: 500,
      textTransform: "uppercase",
      letterSpacing: "1px",
    },
  },
  shape: {
    borderRadius: 16,
  },
  shadows: Array.from(
    { length: 25 },
    (_, i) =>
      `0 ${i + 2}px ${i * 2 + 4}px rgba(21, 101, 192, ${0.05 + i * 0.015})`,
  ),
  customProperties: {
    gradients: {
      ocean: "linear-gradient(135deg, #1565c0 0%, #5e92f3 100%)",
      sky: "linear-gradient(135deg, #90caf9 0%, #e3f2fd 100%)",
      deepBlue: "linear-gradient(135deg, #003c8f 0%, #1565c0 100%)",
      frosty:
        "linear-gradient(135deg, rgba(240,248,255,0.8), rgba(173,216,230,0.6))",
      mist: "linear-gradient(135deg, rgba(21, 101, 192, 0.2), rgba(94, 146, 243, 0.2))",
    },
    emojis: {
      primary: "🌊",
      secondary: "💧",
      success: "✅",
      error: "❌",
      warning: "⚠️",
      info: "ℹ️",
      shine: "✨",
      breeze: "🌬️",
      book: "📚",
      home: "🏠",
      recycle: "♻️",
      handshake: "🤝",
      heart: "💙",
    },
  },
};

const getTheme = (direction = "rtl") => createTheme({ ...theme, direction });

export default getTheme;
