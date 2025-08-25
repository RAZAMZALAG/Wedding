import React, { useRef, useState } from "react";
import {
  Box,
  IconButton,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Fade,
  Paper,
  Tooltip,
  Chip,
  Avatar,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import PhotoCamera from "@mui/icons-material/PhotoCamera";
import { useTranslation } from "react-i18next";
import { useTheme } from "@mui/material/styles";
import api from "../api"; // Add this import at the top
import ReactMarkdown from "react-markdown";

const AIAssistantChat = ({ open, onClose }) => {
  const { t, i18n } = useTranslation();
  const theme = useTheme();
  const direction = theme.direction; // "ltr" or "rtl"
  const [messages, setMessages] = useState([
    { from: "ai", text: t("ai_chat_greeting") },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const [aiTypingText, setAiTypingText] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const messagesEndRef = useRef(null);

  React.useEffect(() => {
    if (open) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  }, [messages, open]);

  // Update greeting when language changes and chat is opened
  React.useEffect(() => {
    if (messages.length === 1 && messages[0].from === "ai") {
      setMessages([{ from: "ai", text: t("ai_chat_greeting") }]);
    }
    // eslint-disable-next-line
  }, [i18n.language, open]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file && file.size <= 10 * 1024 * 1024) {
      // 10MB
      setImageFile(file);
    } else {
      alert(t("ai_chat_image_too_large") || "Image is too large (max 10MB)");
    }
  };

  const handleSend = async () => {
    if (!input.trim() && !imageFile) return;

    // Prepare messages to show immediately
    let newMessages = [];
    if (imageFile) {
      newMessages.push({
        from: "user",
        image: URL.createObjectURL(imageFile),
        text: "", // No text for image-only message
      });
    }
    if (input.trim()) {
      newMessages.push({
        from: "user",
        text: input,
        image: undefined,
      });
    }
    setMessages((prev) => [...prev, ...newMessages]);
    setInput("");
    setImageFile(null); // <-- Immediately clear the image after sending
    setLoading(true);
    setTyping(true);
    setAiTypingText("");

    try {
      let res;
      if (imageFile) {
        const formData = new FormData();
        formData.append("image", imageFile);
        formData.append("lang", i18n.language);
        res = await api.post("/api/ai/ask-image", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else {
        res = await api.post("/api/ai/ask", {
          message: input,
          lang: i18n.language,
        });
      }
      let aiReply = res.data.reply || t("ai_chat_demo_reply");
      const plainReply = stripMarkdownLinks(aiReply);
      let i = 0;
      const typeInterval = setInterval(() => {
        i++;
        setAiTypingText(plainReply.slice(0, i));
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        if (i === plainReply.length) {
          clearInterval(typeInterval);
          setMessages((prev) => [...prev, { from: "ai", text: aiReply }]);
          setTyping(false);
          setLoading(false);
          setAiTypingText("");
          setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
          }, 50);
        }
      }, 30);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { from: "ai", text: t("ai_chat_error") },
      ]);
      setTyping(false);
      setLoading(false);
      setAiTypingText("");
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 50);
      setImageFile(null);
    }
  };

  const handleInputKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (
      file &&
      file.size <= 10 * 1024 * 1024 &&
      file.type.startsWith("image/")
    ) {
      setImageFile(file);
    } else {
      alert(t("ai_chat_image_too_large") || "Image is too large (max 10MB)");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };
  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  if (!open) return null;

  return (
    <Fade in={open}>
      <Paper
        elevation={8}
        sx={{
          position: "fixed",
          bottom: { xs: 16, sm: 32 },
          right: { xs: 16, sm: 32 },
          width: { xs: "95vw", sm: 360 },
          maxWidth: 400,
          maxHeight: "80vh",
          display: "flex",
          flexDirection: "column",
          borderRadius: 2,
          overflow: "hidden",
          zIndex: 2200,
          p: 0,
          border: "2px solid", // Add a subtle border
          boxShadow:
            "0 8px 32px 0 rgba(60,60,60,0.10), 0 1.5px 4px 0 rgba(203,209,143,0.10)", // Softer shadow
          backdropFilter: "blur(2px)", // Optional: subtle glass effect
          background: "#fff", // Ensure background is solid
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            px: 2,
            py: 2,
            borderBottom: "1px solid #eee",
            fontWeight: 700,
            fontFamily: "Assistant, Heebo, Rubik, Arial, sans-serif",
            bgcolor: "#fff",
          }}
        >
          <Typography
            variant="h6"
            sx={{
              flexGrow: 1,
              color: "#222",
              fontFamily: "Assistant, Heebo, Rubik, Arial, sans-serif",
            }}
          >
            {t("ai_chat_title")}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 2,
            bgcolor: "#f9f9f9",
            display: "flex",
            flexDirection: "column",
            minHeight: 200,
            maxHeight: "40vh",
          }}
        >
          {messages.map((msg, idx) => (
            <Box
              key={idx}
              sx={{
                display: "flex",
                justifyContent:
                  msg.from === "user"
                    ? direction === "rtl"
                      ? "flex-start"
                      : "flex-end"
                    : direction === "rtl"
                    ? "flex-end"
                    : "flex-start",
                mb: 0.5,
                flexDirection: "column",
                alignItems:
                  msg.from === "user"
                    ? direction === "rtl"
                      ? "flex-start"
                      : "flex-end"
                    : direction === "rtl"
                    ? "flex-end"
                    : "flex-start",
              }}
            >
              {/* If there's an image, show it above the text */}
              {msg.image && (
                <Box
                  sx={{
                    mb: msg.text ? 0.5 : 0,
                    borderRadius: 2,
                    overflow: "hidden",
                    maxWidth: 180,
                    boxShadow: 1,
                    border: "1px solid #eee",
                    background: "#fff",
                  }}
                >
                  <img
                    src={msg.image}
                    alt="uploaded"
                    style={{
                      display: "block",
                      width: "100%",
                      maxWidth: 180,
                      maxHeight: 140,
                      objectFit: "contain",
                      borderRadius: 8,
                    }}
                  />
                </Box>
              )}
              {msg.text && (
                <Box
                  sx={{
                    px: 2,
                    py: 1,
                    borderRadius: 2,
                    bgcolor:
                      msg.from === "user"
                        ? "primary.main"
                        : "linear-gradient(90deg, #e3b448, #cbd18f, #3a6b35)",
                    color: msg.from === "user" ? "#fff" : "#222",
                    maxWidth: "80%",
                    fontFamily: "Assistant, Heebo, Rubik, Arial, sans-serif",
                    fontSize: 15,
                    boxShadow: msg.from === "ai" ? 1 : 0,
                    whiteSpace: "pre-line",
                  }}
                >
                  <ReactMarkdown
                    components={{
                      p: ({ node, ...props }) => <span {...props} />,
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                </Box>
              )}
            </Box>
          ))}
          <div ref={messagesEndRef} />
          {loading && (
            <Box sx={{ display: "flex", justifyContent: "center", my: 1 }}>
              <CircularProgress size={24} />
            </Box>
          )}
          {typing && (
            <Box
              sx={{
                display: "flex",
                justifyContent: direction === "rtl" ? "flex-end" : "flex-start",
                mb: 0.5,
              }}
            >
              <Box
                sx={{
                  px: 2,
                  py: 1,
                  borderRadius: 2,
                  bgcolor: "linear-gradient(90deg, #e3b448, #cbd18f, #3a6b35)",
                  color: "#222",
                  maxWidth: "80%",
                  fontFamily: "Assistant, Heebo, Rubik, Arial, sans-serif",
                  fontSize: 15,
                  boxShadow: 1,
                  whiteSpace: "pre-line",
                  fontStyle: "italic",
                  opacity: 0.8,
                }}
              >
                {aiTypingText}
              </Box>
            </Box>
          )}
        </Box>
        <Box
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          sx={{
            p: 2,
            borderTop: "1px solid #eee",
            display: "flex",
            alignItems: "center",
            bgcolor: "#fff",
            border: dragActive ? "2px dashed #e3b448" : undefined,
            transition: "border 0.2s",
            position: "relative",
            flexDirection: "column", // Stack preview above input
            gap: 1,
          }}
        >
          {/* Show image preview chip if imageFile is set */}
          {imageFile && (
            <Chip
              avatar={
                <Avatar
                  src={URL.createObjectURL(imageFile)}
                  alt="preview"
                  sx={{ width: 32, height: 32 }}
                />
              }
              label={imageFile.name}
              onDelete={() => setImageFile(null)}
              deleteIcon={
                <CloseIcon
                  sx={{ color: "#d32f2f", fontSize: 22, fontWeight: 700 }}
                />
              }
              sx={{
                mb: 1,
                alignSelf: "flex-start",
                fontWeight: 700,
                fontSize: 15,
                ".MuiChip-deleteIcon": {
                  ml: 1,
                  mr: 0.5,
                  color: "#d32f2f",
                  "&:hover": { color: "#b71c1c", background: "transparent" },
                },
              }}
              variant="outlined"
              color="primary"
            />
          )}

          <Box sx={{ display: "flex", width: "100%", alignItems: "center" }}>
            <TextField
              autoFocus
              fullWidth
              variant="outlined"
              placeholder={t("ai_chat_placeholder")}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleInputKeyDown}
              disabled={loading}
              sx={{ bgcolor: "#fff", borderRadius: 2 }}
            />
            <Button
              onClick={handleSend}
              disabled={(!input.trim() && !imageFile) || loading}
              variant="contained"
              sx={{
                ml: 1,
                background:
                  "linear-gradient(90deg, #4203c9, #16acea, #e8d71e, #d71b3b)",
                color: "#fff",
                fontWeight: 700,
                fontFamily: "Assistant, Heebo, Rubik, Arial, sans-serif",
              }}
            >
              {t("ai_chat_send")}
            </Button>
            <Tooltip
              title={t("ai_chat_image_tooltip")}
              PopperProps={{
                sx: { zIndex: 2500 },
              }}
            >
              <IconButton component="label" disabled={loading} sx={{ ml: 1 }}>
                <PhotoCamera />
                <input
                  accept="image/*"
                  style={{ display: "none" }}
                  id="ai-chat-image-upload"
                  type="file"
                  onChange={handleImageChange}
                />
              </IconButton>
            </Tooltip>
          </Box>
          {dragActive && (
            <Box
              sx={{
                position: "absolute",
                left: 0,
                right: 0,
                bottom: "100%",
                mb: 1,
                color: "#e3b448",
                textAlign: "center",
                fontWeight: 500,
              }}
            >
              {t("Drop image to upload")}
            </Box>
          )}
        </Box>
      </Paper>
    </Fade>
  );
};

function stripMarkdownLinks(text) {
  // Replace [label](url) with just label
  return text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
}

export default AIAssistantChat;
