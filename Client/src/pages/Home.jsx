import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  CssBaseline,
  Box,
  Card,
  Button,
  Chip,
  Grid,
  Fade,
  Slide,
  Zoom,
  Grow,
} from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import backgroundImage from "../assets/wedding.png";
import api from "../api.js";
import { EP_CATEGORIES } from "../constants.js";
import { useTranslation } from "react-i18next";

// עיצוב בגווני ורוד רומנטי לחתונות
const colors = {
  primary: "#d4578a", // ורוד רומנטי
  secondary: "#f8bbd9", // ורוד פסטל
  accent: "#ff6b9d", // ורוד אקסנט
  lightPink: "#ffeef5", // ורוד בהיר מאוד
  palePink: "#fdf2f8", // ורוד חיוור
  cream: "#fef7f0", // קרם עדין
  softPink: "#fdf2f8", // ורוד רך
  dark: "#1e293b",
  transparent: "rgba(255, 255, 255, 0.1)", // שקיפות עדינה
  glass: "rgba(255, 255, 255, 0.15)", // זכוכית
};

// קומפוננט אייקון צף עדין
const FloatingIcon = ({ icon, delay = 0, duration = 4 }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <Zoom in={visible} timeout={1500}>
      <Box
        sx={{
          position: "absolute",
          fontSize: "1.8rem",
          animation: `gentleFloat ${duration}s ease-in-out infinite`,
          opacity: 0.4,
          filter: "drop-shadow(0 2px 6px rgba(37, 99, 235, 0.2))",
          "@keyframes gentleFloat": {
            "0%, 100%": {
              transform: "translateY(0) scale(1)",
            },
            "50%": {
              transform: "translateY(-15px) scale(1.05)",
            },
          },
          "&:hover": {
            opacity: 0.7,
            transform: "scale(1.2)",
            transition: "all 0.3s ease",
          },
        }}
      >
        {icon}
      </Box>
    </Zoom>
  );
};

// כפתור עדין מעודכן
const SoftButton = ({ children, icon, variant = "contained", ...props }) => {
  return (
    <Button
      {...props}
      variant={variant}
      sx={{
        borderRadius: "20px",
        fontWeight: 500,
        textTransform: "none",
        fontSize: "1.1rem",
        padding: "12px 24px",
        background:
          variant === "contained"
            ? `linear-gradient(135deg, ${colors.primary}dd, ${colors.accent}dd)`
            : "rgba(255, 255, 255, 0.1)",
        backdropFilter: "blur(10px)",
        border:
          variant === "outlined" ? `1px solid ${colors.accent}60` : "none",
        color: variant === "contained" ? "#ffffff" : colors.primary,
        boxShadow: "0 4px 15px rgba(212, 87, 138, 0.15)",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        "&::before": {
          content: icon ? `"${icon}"` : '""',
          marginRight: icon ? "8px" : 0,
          fontSize: "1.2em",
        },
        "&:hover": {
          transform: "translateY(-2px)",
          boxShadow: "0 8px 25px rgba(212, 87, 138, 0.25)",
          background:
            variant === "contained"
              ? `linear-gradient(135deg, ${colors.secondary}, ${colors.primary})`
              : "rgba(255, 255, 255, 0.2)",
        },
        ...props.sx,
      }}
    >
      {children}
    </Button>
  );
};

// קומפוננט סטטיסטיקה עדין
const GentleStat = ({ number, label, icon, delay = 0 }) => {
  const [count, setCount] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(true);
      let start = 0;
      const end = parseInt(number);
      const increment = end / 40;
      const counter = setInterval(() => {
        start += increment;
        if (start >= end) {
          setCount(end);
          clearInterval(counter);
        } else {
          setCount(Math.floor(start));
        }
      }, 40);
    }, delay);
    return () => clearTimeout(timer);
  }, [number, delay]);

  return (
    <Grow in={visible} timeout={1200}>
      <Card
        sx={{
          background: "rgba(255, 255, 255, 0.85)",
          backdropFilter: "blur(15px)",
          borderRadius: "16px",
          textAlign: "center",
          p: 3,
          border: `2px solid rgba(255, 255, 255, 0.9)`,
          transition: "all 0.3s ease",
          boxShadow: "0 8px 25px rgba(0, 0, 0, 0.25)",
          "&:hover": {
            transform: "translateY(-5px)",
            boxShadow: "0 15px 35px rgba(0, 0, 0, 0.35)",
            background: "rgba(255, 255, 255, 0.92)",
            border: `2px solid rgba(255, 255, 255, 0.95)`,
          },
        }}
      >
        <Typography
          variant="h4"
          sx={{
            fontWeight: 600,
            color: colors.primary,
            mb: 1,
          }}
        >
          {count}+
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: colors.secondary,
            fontWeight: 500,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 1,
          }}
        >
          <span>{icon}</span>
          {label}
        </Typography>
      </Card>
    </Grow>
  );
};

const Home = () => {
  const { t } = useTranslation();
  const [showContent, setShowContent] = useState(false);
  const [categories, setCategories] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    setShowContent(true);
    api
      .get(EP_CATEGORIES)
      .then((res) => {
        if (Array.isArray(res.data)) {
          setCategories(res.data);
        } else {
          setCategories([]);
        }
      })
      .catch(() => setCategories([]));
  }, []);

  return (
    <Box sx={{ position: "relative", minHeight: "100vh", overflow: "hidden" }}>
      {/* רקע מטושטש כהה יותר */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          backgroundImage: `url(${backgroundImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          filter: "blur(2px) brightness(0.4) opacity(0.6)",
          zIndex: -2,
        }}
      />

      {/* שכבת גרדיאנט רומנטי */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          background: `linear-gradient(135deg, 
            rgba(139, 27, 71, 0.3) 0%, 
            rgba(212, 87, 138, 0.15) 25%, 
            rgba(248, 187, 217, 0.2) 50%, 
            rgba(255, 107, 157, 0.25) 75%, 
            rgba(139, 27, 71, 0.3) 100%)`,
          zIndex: -1,
        }}
      />

      {/* אייקונים צפים עדינים */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          zIndex: 0,
          pointerEvents: "none",
        }}
      >
        <Box sx={{ position: "absolute", top: "15%", left: "10%", zIndex: 0 }}>
          <FloatingIcon icon="💍" delay={0} duration={5} />
        </Box>
        <Box sx={{ position: "absolute", top: "25%", right: "15%", zIndex: 0 }}>
          <FloatingIcon icon="�" delay={800} duration={4.5} />
        </Box>
        <Box sx={{ position: "absolute", top: "55%", left: "8%", zIndex: 0 }}>
          <FloatingIcon icon="🌸" delay={1600} duration={4} />
        </Box>
        <Box
          sx={{ position: "absolute", bottom: "25%", right: "12%", zIndex: 0 }}
        >
          <FloatingIcon icon="✨" delay={2400} duration={4.2} />
        </Box>
        <Box sx={{ position: "absolute", top: "35%", right: "5%", zIndex: 0 }}>
          <FloatingIcon icon="💕" delay={3200} duration={3.8} />
        </Box>
      </Box>

      <CssBaseline />

      <Container maxWidth="lg" sx={{ position: "relative", zIndex: 1, py: 4 }}>
        {/* כותרת ראשית עם רקע אטום */}
        <Fade in={showContent} timeout={1000}>
          <Card
            sx={{
              background: "rgba(255, 255, 255, 0.55)",
              backdropFilter: "blur(20px)",
              borderRadius: "24px",
              p: 4,
              mb: 4,
              textAlign: "center",
              border: `2px solid rgba(255, 255, 255, 0.9)`,
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
              transition: "all 0.3s ease",
              "&:hover": {
                transform: "translateY(-3px)",
                boxShadow: "0 12px 40px rgba(0, 0, 0, 0.4)",
                background: "rgba(255, 255, 255, 0.55)",
                border: `2px solid rgba(255, 255, 255, 0.95)`,
              },
            }}
          >
            <Slide direction="down" in={showContent} timeout={1200}>
              <Box>
                <Typography
                  variant="h2"
                  component="h1"
                  gutterBottom
                  sx={{
                    fontSize: { xs: "2rem", md: "3rem" },
                    fontWeight: 700,
                    color: colors.dark,
                    mb: 2,
                    textShadow: "none",
                  }}
                >
                  {t("welcome_title")}
                </Typography>

                <Chip
                  label={t("digital_library")}
                  sx={{
                    background: `linear-gradient(135deg, ${colors.primary}dd, ${colors.accent}dd)`,
                    color: "#ffffff",
                    fontWeight: 500,
                    fontSize: "1rem",
                    p: 1,
                    mb: 3,
                    boxShadow: "0 4px 15px rgba(212, 87, 138, 0.2)",
                    backdropFilter: "blur(10px)",
                  }}
                />
              </Box>
            </Slide>
          </Card>
        </Fade>

        {/* תיאור מפורט */}
        <Grid container spacing={4} sx={{ mb: 5 }}>
          <Grid item xs={12} md={8}>
            <Slide direction="left" in={showContent} timeout={1400}>
              <Card
                sx={{
                  background: "rgba(255, 255, 255, 0.85)",
                  backdropFilter: "blur(15px)",
                  borderRadius: "20px",
                  p: 4,
                  border: `2px solid rgba(255, 255, 255, 0.9)`,
                  transition: "all 0.3s ease",
                  boxShadow: "0 8px 25px rgba(0, 0, 0, 0.25)",
                  "&:hover": {
                    transform: "translateY(-5px)",
                    boxShadow: "0 15px 35px rgba(0, 0, 0, 0.35)",
                    background: "rgba(255, 255, 255, 0.92)",
                    border: `2px solid rgba(255, 255, 255, 0.95)`,
                  },
                }}
              >
                <Typography
                  variant="h4"
                  gutterBottom
                  sx={{
                    fontSize: { xs: "1.5rem", md: "2rem" },
                    fontWeight: 600,
                    color: "#64748b", // אפור בהיר יותר
                    mb: 3,
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                  }}
                >
                  <span style={{ fontSize: "2rem" }}>🏠</span>
                  {t("home_headline")}
                </Typography>

                <Typography
                  variant="h6"
                  gutterBottom
                  sx={{
                    fontSize: { xs: "1.1rem", md: "1.3rem" },
                    lineHeight: 1.7,
                    color: "#94a3b8", // אפור בהיר
                    mb: 3,
                    fontWeight: 500,
                  }}
                >
                  {t("home_subheadline")}
                </Typography>

                <Typography
                  variant="body1"
                  sx={{
                    fontSize: { xs: "1rem", md: "1.1rem" },
                    lineHeight: 1.7,
                    color: colors.secondary,
                    fontWeight: 400,
                  }}
                >
                  {t("home_desc")}
                </Typography>
              </Card>
            </Slide>
          </Grid>

          <Grid item xs={12} md={4}>
            <Slide direction="right" in={showContent} timeout={1600}>
              <Card
                sx={{
                  background: "rgba(255, 255, 255, 0.85)",
                  backdropFilter: "blur(15px)",
                  borderRadius: "20px",
                  p: 3,
                  border: `2px solid rgba(255, 255, 255, 0.9)`,
                  textAlign: "center",
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  boxShadow: "0 8px 25px rgba(0, 0, 0, 0.25)",
                  "&:hover": {
                    transform: "translateY(-5px)",
                    boxShadow: "0 15px 35px rgba(0, 0, 0, 0.35)",
                    background: "rgba(255, 255, 255, 0.92)",
                    border: `2px solid rgba(255, 255, 255, 0.95)`,
                  },
                  transition: "all 0.3s ease",
                }}
              >
                <Typography
                  variant="h5"
                  gutterBottom
                  sx={{ color: colors.primary, fontWeight: 600, mb: 3 }}
                >
                  {t("what_can_borrow")}
                </Typography>

                <Box
                  sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}
                >
                  {Array.isArray(categories) && categories.length === 0 ? (
                    <Typography variant="body2" color={colors.secondary}>
                      {t("loading_categories")}
                    </Typography>
                  ) : (
                    (Array.isArray(categories) ? categories : [])
                      .slice(0, 5)
                      .map((cat, index) => (
                        <Grow
                          key={cat}
                          in={showContent}
                          timeout={1800 + index * 200}
                        >
                          <Chip
                            label={t(`categories.${cat}`, { defaultValue: cat })}
                            clickable
                            onClick={() =>
                              navigate(
                                `/catalog?category=${encodeURIComponent(cat)}`,
                              )
                            }
                            sx={{
                              background: "rgba(255, 255, 255, 0.75)",
                              backdropFilter: "blur(10px)",
                              color: colors.primary,
                              fontWeight: 500,
                              border: `2px solid rgba(255, 255, 255, 0.85)`,
                              "&:hover": {
                                background: "rgba(255, 255, 255, 0.85)",
                                transform: "scale(1.03)",
                                boxShadow: "0 4px 15px rgba(37, 99, 235, 0.2)",
                                border: `2px solid rgba(255, 255, 255, 0.95)`,
                              },
                              transition: "all 0.3s ease",
                            }}
                          />
                        </Grow>
                      ))
                  )}
                </Box>
              </Card>
            </Slide>
          </Grid>
        </Grid>

        {/* סטטיסטיקות עדינות */}
        <Fade in={showContent} timeout={2000}>
          <Box sx={{ mb: 5 }}>
            <Typography
              variant="h4"
              textAlign="center"
              gutterBottom
              sx={{
                color: colors.lightBlue, // Wedding Planner במספרים
                fontWeight: 600,
                mb: 4,
                fontSize: { xs: "1.8rem", md: "2.5rem" },
                textShadow: "0 2px 4px rgba(37, 99, 235, 0.1)",
              }}
            >
              {t("stats_title")}
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <GentleStat
                  number="50"
                  label={t("stat_items")}
                  icon="📦"
                  delay={0}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <GentleStat
                  number="150"
                  label={t("stat_members")}
                  icon="👥"
                  delay={200}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <GentleStat
                  number="100"
                  label={t("stat_loans")}
                  icon="🔄"
                  delay={400}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <GentleStat
                  number="95"
                  label={t("stat_satisfaction")}
                  icon="⭐"
                  delay={600}
                />
              </Grid>
            </Grid>
          </Box>
        </Fade>

        {/* כפתורי פעולה עדינים */}
        <Fade in={showContent} timeout={2500}>
          <Card
            sx={{
              background: "rgba(255, 255, 255, 0.85)",
              backdropFilter: "blur(20px)",
              borderRadius: "24px",
              p: 4,
              textAlign: "center",
              border: `2px solid rgba(255, 255, 255, 0.9)`,
              transition: "all 0.3s ease",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
              "&:hover": {
                transform: "translateY(-3px)",
                boxShadow: "0 12px 40px rgba(0, 0, 0, 0.4)",
                background: "rgba(255, 255, 255, 0.92)",
                border: `2px solid rgba(255, 255, 255, 0.95)`,
              },
            }}
          >
            <Typography
              variant="h4"
              gutterBottom
              sx={{
                color: colors.primary,
                fontWeight: 600,
                mb: 4,
                fontSize: { xs: "1.8rem", md: "2.2rem" },
              }}
            >
              {t("ready_title")}
            </Typography>

            <Box
              sx={{
                display: "flex",
                flexDirection: { xs: "column", sm: "row" },
                gap: 3,
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <SoftButton
                component={Link}
                to="/catalog"
                icon="📚"
                variant="contained"
                size="large"
              >
                {t("browse_catalog")}
              </SoftButton>

              <SoftButton
                component={Link}
                to="/about"
                icon="ℹ️"
                variant="contained"
                size="large"
                sx={{
                  background: `linear-gradient(135deg, ${colors.secondary}dd, ${colors.accent}dd)`,
                  "&:hover": {
                    background: `linear-gradient(135deg, ${colors.accent}, ${colors.primary})`,
                  },
                }}
              >
                {t("learn_about")}
              </SoftButton>

              <SoftButton
                component={Link}
                to="/qna"
                icon="💬"
                variant="contained"
                size="large"
                sx={{
                  background: `linear-gradient(135deg, ${colors.secondary}dd, ${colors.accent}dd)`,
                  "&:hover": {
                    background: `linear-gradient(135deg, ${colors.accent}, ${colors.primary})`,
                  },
                }}
              >
                {t("qna")}
              </SoftButton>
            </Box>

            <Typography
              variant="body2"
              sx={{
                mt: 3,
                color: colors.lightBlue,
                fontStyle: "italic",
                fontSize: "1rem",
                fontWeight: 400,
              }}
            >
              {t("home_motto")}
            </Typography>
          </Card>
        </Fade>
      </Container>
    </Box>
  );
};

export default Home;
