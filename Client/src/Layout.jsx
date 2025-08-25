import React, { useEffect, useState } from "react";
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  IconButton,
  useMediaQuery,
  ButtonGroup,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  useTheme,
  Paper,
  Fade,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import QuestionAnswerIcon from "@mui/icons-material/QuestionAnswer";
import InfoIcon from "@mui/icons-material/Info";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import PersonIcon from "@mui/icons-material/Person";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LibraryBooksIcon from "@mui/icons-material/LibraryBooks";
import GroupIcon from "@mui/icons-material/Group";
import LanguageIcon from "@mui/icons-material/Language";
import { Link, useNavigate, useLocation } from "react-router-dom";
import Logo from "./assets/logo.png";
import { useAuth } from "./context/AuthContext.jsx";
import Badge from "@mui/material/Badge";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import { useShared } from "./context/SharedContext.jsx";
import { useTranslation } from "react-i18next";
import AIAssistantChat from "./components/AIAssistantChat";

function Layout({ children }) {
  const { t, i18n } = useTranslation();
  const { isLoggedIn, permission, logout, userName } = useAuth();
  const { cartCount } = useShared();
  const isMobile = useMediaQuery((theme) => theme.breakpoints.down("md"));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const [chatOpen, setChatOpen] = useState(false);

  const menuOptions = [
    { text: t("menu_catalog"), to: "/catalog", icon: <LibraryBooksIcon /> },
    { text: t("menu_qna"), to: "/qna", icon: <QuestionAnswerIcon /> },
    { text: t("menu_about"), to: "/about", icon: <InfoIcon /> },
  ];

  const extraOptions = [
    isLoggedIn && {
      text: t("menu_my_loans"),
      to: "/bookings/personal",
      icon: <PersonIcon />,
    },
    isLoggedIn && {
      text: t("menu_cart"),
      to: "/cart",
      icon:
        cartCount > 0 ? (
          <Badge badgeContent={cartCount} color="secondary">
            <ShoppingCartIcon />
          </Badge>
        ) : (
          <ShoppingCartIcon />
        ),
    },
    permission > 1 && {
      text: t("menu_admin_loans"),
      to: "/bookings",
      icon: <AdminPanelSettingsIcon />,
    },
    permission > 1 && {
      text: t("menu_admin_users"),
      to: "/users",
      icon: <GroupIcon />,
    },
  ].filter(Boolean);

  const drawerWidth = 220;
  const collapsedWidth = 70;

  // רומנטי לחתונות
  const colors = {
    primary: "#d4578a", // ורוד רומנטי
    secondary: "#f8bbd9", // ורוד פסטל
    accent: "#ff6b9d", // ורוד חי
    light: "#ffeef5", // ורוד בהיר
    dark: "#8b1b47", // ורוד כהה
  };

  const getPermissionBadgeIcon = (permission) => {
    if (permission == 3)
      return <EmojiEventsIcon sx={{ fontSize: 14, color: "#e3b448" }} />;
    if (permission == 2)
      return <MenuBookIcon sx={{ fontSize: 14, color: colors.light }} />;
    return null;
  };

  // Modern glassmorphism sidebar content
  const drawerContent = (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: `linear-gradient(135deg, ${colors.primary}dd 0%, ${colors.secondary}ee 40%, ${colors.dark}f0 100%)`,
        backdropFilter: "blur(20px)",
        position: "relative",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `linear-gradient(45deg, ${colors.accent}20, ${colors.light}15)`,
          zIndex: -1,
        },
      }}
    >
      {/* Logo section */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          py: 3,
          px: 2,
          flexDirection: "column", // Make column to allow username below
        }}
      >
        <Badge
          overlap="circular"
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
          badgeContent={isLoggedIn ? getPermissionBadgeIcon(permission) : null}
          sx={{
            "& .MuiBadge-badge": {
              p: 0.5,
              bgcolor: "rgba(255, 255, 255, 0.9)",
              boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
              borderRadius: "50%",
              minWidth: 0,
              minHeight: 0,
            },
          }}
        >
          <Paper
            elevation={8}
            sx={{
              padding: 1,
              background: `linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%)`,
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(255,255,255,0.2)",
              borderRadius: "20px",
              width: drawerOpen && !isMobile ? 160 : 56,
              height: 56,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.3s cubic-bezier(0.4,0,0.2,1)",
              cursor: "pointer",
              "&:hover": {
                transform: "translateY(-2px)",
                boxShadow: "0 8px 25px rgba(0,0,0,0.15)",
              },
            }}
            component={Link}
            to="/"
            onClick={() => {
              if (isMobile) setMobileDrawerOpen(false);
            }}
          >
            <img
              src={Logo}
              alt="Logo"
              style={{
                height: 40,
                transition: "all 0.3s",
                marginRight: drawerOpen && !isMobile ? 8 : 0,
                marginLeft: drawerOpen && !isMobile ? 8 : 0,
              }}
            />
          </Paper>
        </Badge>
        {/* Show userName under logo if exists */}
        {userName && (
          <Typography
            variant="subtitle2"
            sx={{
              color: "rgba(255,255,255,0.92)",
              mt: 1,
              fontWeight: 500,
              fontSize: "1.05rem", // Always the same size
              textAlign: "center",
              maxWidth: drawerOpen || isMobile ? 140 : 56, // Still adapts width
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              transition: "max-width 0.2s",
              display: "block",
            }}
            title={userName}
          >
            {userName}
          </Typography>
        )}
      </Box>

      <Divider
        sx={{
          backgroundColor: "rgba(255,255,255,0.2)",
          mx: 2,
          borderRadius: "2px",
        }}
      />

      {/* Scrollable menu */}
      <Box sx={{ flexGrow: 1, py: 2, overflowY: "auto", minHeight: 0 }}>
        <List sx={{ px: 1 }}>
          {[...menuOptions, ...extraOptions].map((option, index) => (
            <Fade in={true} timeout={300 + index * 100} key={option.text}>
              <ListItem
                key={option.text}
                component={Link}
                to={option.to}
                selected={location.pathname === option.to}
                onClick={() => {
                  if (isMobile) setMobileDrawerOpen(false);
                }}
                sx={{
                  color: "rgba(255, 255, 255, 0.9)", // צבע טקסט בהיר יותר
                  "&:hover": {
                    backgroundColor: "rgba(255, 255, 255, 0.1)",
                    borderRadius: "8px",
                  },
                  ...(location.pathname === option.to
                    ? {
                        backgroundColor: `${theme.palette.secondary.light} !important`,
                        color: "rgba(0, 0, 0, 0.87)", // צבע טקסט כהה לפריט נבחר
                        borderRadius: "8px",
                      }
                    : {}),
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    pr: 1.5,
                    ml: -0.2,
                    justifyContent: "center",
                    color:
                      location.pathname === option.to
                        ? "rgba(0, 0, 0, 0.87)" // צבע אייקון כהה לפריט נבחר
                        : "rgba(255, 255, 255, 0.9)", // צבע אייקון בהיר יותר
                    transition: "margin 0.2s, color 0.2s",
                  }}
                >
                  {option.icon}
                </ListItemIcon>
                <ListItemText
                  primary={option.text}
                  sx={{
                    minWidth: 0,
                    width: drawerOpen || isMobile ? "120px" : 0,
                    opacity: drawerOpen || isMobile ? 1 : 0,
                    transition: "width 0.2s, opacity 0.2s",
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                    ml: 0,
                    "& .MuiListItemText-primary": {
                      color: "inherit", // ירש את הצבע מה-ListItem
                    },
                  }}
                />
              </ListItem>
            </Fade>
          ))}
        </List>
      </Box>

      {/* Pin login/logout and language selector at the bottom */}
      <Box sx={{ width: "100%" }}>
        <List>
          <ListItem
            component={Link}
            to={isLoggedIn ? undefined : "/login"}
            onClick={() => {
              if (isLoggedIn) {
                logout();
                navigate("/");
              }
              if (isMobile) setMobileDrawerOpen(false);
            }}
            sx={{
              color: "rgba(255, 255, 255, 0.9)", // צבע טקסט בהיר יותר
              "&:hover": {
                backgroundColor: "rgba(255, 255, 255, 0.1)", // רקע קל בהובר
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                pr: 1.5,
                pl: 1,
                ml: -0.2,
                justifyContent: "center",
                color: "rgba(255, 255, 255, 0.9)",
                transition: "margin 0.2s, color 0.2s",
              }}
            >
              <ExitToAppIcon />
            </ListItemIcon>
            <ListItemText
              primary={isLoggedIn ? t("menu_logout") : t("menu_login")}
              sx={{
                minWidth: 0,
                width: drawerOpen || isMobile ? "auto" : 0,
                opacity: drawerOpen || isMobile ? 1 : 0,
                transition: "all 0.3s",
                overflow: "hidden",
                whiteSpace: "nowrap",
                "& .MuiListItemText-primary": {
                  fontSize: "0.95rem",
                  color: "inherit",
                  textShadow: "0 1px 2px rgba(0,0,0,0.3)", // Better contrast
                },
              }}
            />
          </ListItem>
        </List>
        <List sx={{ mb: 1 }}>
          <ListItem
            sx={{
              display: "flex",
              alignItems: "center",
              px: 2.5,
              color: "rgba(255, 255, 255, 0.9)",
            }}
            disableGutters
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                pl: 0.5,
                justifyContent: "center",
                color: "rgba(255, 255, 255, 0.9)", // צבע אייקון בהיר יותר
                transition: "margin 0.2s, color 0.2s",
              }}
            >
              <LanguageIcon sx={{ fontSize: 22 }} />
            </ListItemIcon>
            <ListItemText
              primary={
                <FormControl
                  variant="standard"
                  fullWidth
                  size="small"
                  sx={{
                    minWidth: 80,
                    opacity: drawerOpen || isMobile ? 1 : 0,
                    width: drawerOpen || isMobile ? "80px" : 0,
                    transition: "width 0.2s, opacity 0.2s",
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                    ml: 0,
                  }}
                >
                  <Select
                    value={i18n.language}
                    onChange={(e) => handleLangChange(e.target.value)}
                    disableUnderline
                    sx={{
                      fontSize: "1rem",
                      background: "none",
                      boxShadow: "none",
                      color: "rgba(255, 255, 255, 0.9)", // צבע טקסט בהיר יותר
                      "&:before, &:after": { display: "none" },
                      "& .MuiSelect-select": { pr: 2, pl: 1 },
                      "& .MuiSelect-icon": {
                        color: "rgba(255, 255, 255, 0.7)", // צבע החץ
                      },
                    }}
                  >
                    <MenuItem value="he">עברית</MenuItem>
                    <MenuItem value="ar">العربية</MenuItem>
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="ru">Русский</MenuItem>
                  </Select>
                </FormControl>
              }
              sx={{
                minWidth: 0,
                ml: 0,
                "& .MuiListItemText-primary": {
                  color: "inherit",
                  fontWeight: 500,
                },
              }}
            />
          </ListItem>
        </List>
      </Box>
    </Box>
  );

  const handleLangChange = (lang) => {
    i18n.changeLanguage(lang);
    localStorage.setItem("lang", lang);
  };

  return (
    <Box
      sx={{
        display: "block",
        minHeight: "100vh",
        width: "100%",
        overflowX: "hidden",
        background: `linear-gradient(135deg, ${colors.primary}06 0%, ${colors.secondary}04 50%, ${colors.dark}02 100%)`,
      }}
    >
      {/* Modern AppBar for mobile */}
      {isMobile && (
        <AppBar
          position="fixed"
          sx={{
            zIndex: (theme) => theme.zIndex.drawer + 1,
            background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 70%, ${colors.dark} 100%)`,
            backdropFilter: "blur(20px)",
            boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
            width: "100%",
            left: 0,
            right: 0,
          }}
        >
          <Toolbar
            sx={{
              justifyContent: "space-between",
              width: "100%",
              minWidth: 0,
              overflow: "hidden",
            }}
          >
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setMobileDrawerOpen((prev) => !prev)}
              sx={{
                mr: 1,
                background: "rgba(255,255,255,0.1)",
                "&:hover": {
                  background: "rgba(255,255,255,0.2)",
                },
              }}
            >
              <MenuIcon />
            </IconButton>
            <Paper
              elevation={4}
              sx={{
                padding: 0.5,
                background: "rgba(255,255,255,0.15)",
                backdropFilter: "blur(10px)",
                border: "1px solid rgba(255,255,255,0.2)",
                borderRadius: "16px",
                width: 48,
                height: 48,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
              component={Link}
              to="/"
            >
              <img src={Logo} alt="Logo" style={{ height: 36 }} />
            </Paper>
          </Toolbar>
        </AppBar>
      )}

      {/* Desktop Drawer */}
      {!isMobile && (
        <Drawer
          variant="permanent"
          open={drawerOpen}
          onMouseEnter={() => setDrawerOpen(true)}
          onMouseLeave={() => setDrawerOpen(false)}
          sx={{
            width: drawerOpen ? drawerWidth : collapsedWidth,
            flexShrink: 0,
            position: "fixed",
            zIndex: (theme) => theme.zIndex.appBar - 1,
            "& .MuiDrawer-paper": {
              width: drawerOpen ? drawerWidth : collapsedWidth,
              boxSizing: "border-box",
              transition: "width 0.3s cubic-bezier(0.4,0,0.2,1)",
              overflowX: "hidden",
              position: "fixed",
              top: 0,
              left: 0,
              height: "100vh",
              border: "none",
              boxShadow: "4px 0 20px rgba(0,0,0,0.1)",
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Mobile Drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": {
              width: drawerWidth,
              boxSizing: "border-box",
              top: 64,
              height: "calc(100% - 64px)",
              border: "none",
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Main Content with modern styling */}
      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
          pt: isMobile ? "64px" : 0,
          width: "100%",
          overflowX: "auto",
          ml: !isMobile ? `${collapsedWidth}px` : 0,
          maxWidth: !isMobile ? `calc(100% - ${collapsedWidth}px)` : "100%",
          transition: "all 0.3s cubic-bezier(0.4,0,0.2,1)",
        }}
      >
        <Box
          sx={{
            flexGrow: 1,
            p: 3,
            display: "flex",
            minHeight: "100%",
            flexDirection: "column",
          }}
        >
          {children}
        </Box>

        {/* Modern Footer with different color */}
        <Paper
          elevation={0}
          sx={{
            background: `linear-gradient(135deg, #374151 0%, #1f2937 100%)`, // Gray gradient instead of blue
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: 0,
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: "rgba(255,255,255,0.8)",
              fontWeight: 500,
            }}
          >
            © {new Date().getFullYear()} {t("footer_rights")}
          </Typography>
        </Paper>

        {/* Modern AI Assistant Button */}
        {!chatOpen && (
          <Fade in={true} timeout={1000}>
            <Box
              sx={{
                position: "fixed",
                zIndex: 2000,
                bottom: { xs: 90, sm: 40 },
                right: { xs: 20, sm: 40 },
                display: "flex",
                alignItems: "center",
              }}
            >
              <Paper
                elevation={12}
                sx={{
                  background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.accent} 50%, ${colors.secondary} 100%)`,
                  borderRadius: "50%",
                  width: { xs: 56, sm: 72 },
                  height: { xs: 56, sm: 72 },
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  transition: "all 0.3s cubic-bezier(0.4,0,0.2,1)",
                  "&:hover": {
                    transform: "scale(1.1) rotate(5deg)",
                    boxShadow: `0 12px 40px ${colors.primary}50`,
                  },
                  "&:active": {
                    transform: "scale(0.95)",
                  },
                }}
                onClick={() => setChatOpen(true)}
              >
                <Typography
                  sx={{
                    color: "#fff",
                    fontWeight: 800,
                    fontSize: { xs: 18, sm: 24 },
                    letterSpacing: 1,
                    fontFamily: "'Orbitron', 'Montserrat', monospace",
                    textShadow: "0 2px 8px rgba(0,0,0,0.3)",
                  }}
                >
                  AI
                </Typography>
              </Paper>
            </Box>
          </Fade>
        )}

        <AIAssistantChat open={chatOpen} onClose={() => setChatOpen(false)} />
      </Box>
    </Box>
  );
}

export default Layout;
