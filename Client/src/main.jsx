import React, { useMemo } from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import getTheme from "./styles/theme.js";
import App from "./App";
import rtlPlugin from "stylis-plugin-rtl";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";
import { prefixer } from "stylis";
import "./App.css";
import "../i18n.js";
import { useTranslation } from "react-i18next";

// Helper to determine if a language is RTL
const isRTL = (lang) => ["he", "ar"].includes(lang);

// Restore language from localStorage before app renders
const savedLang = localStorage.getItem("lang");
if (savedLang) {
  import("i18next").then((i18next) => {
    i18next.default.changeLanguage(savedLang);
  });
}

function Main() {
  const { i18n } = useTranslation();
  const direction = isRTL(i18n.language) ? "rtl" : "ltr";

  // Create cache for RTL or LTR
  const cache = useMemo(
    () =>
      createCache({
        key: direction === "rtl" ? "mui-rtl" : "mui",
        stylisPlugins: direction === "rtl" ? [prefixer, rtlPlugin] : [prefixer],
      }),
    [direction],
  );

  // Update document direction
  React.useEffect(() => {
    document.body.dir = direction;
  }, [direction]);

  const theme = useMemo(() => getTheme(direction), [direction]);

  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </CacheProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Main />
  </React.StrictMode>,
);
