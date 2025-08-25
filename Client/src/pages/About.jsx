import React from "react";
import { useTranslation } from "react-i18next";
import placeHolderImage from "../assets/tool_placeholder.svg";
// Note: WhatsApp icon removed - using placeholder instead
import {
  Box,
  Typography,
  Container,
  Link,
  ListItem,
  List,
} from "@mui/material";

function About() {
  const { t } = useTranslation();

  return (
    <Box>
      <Container maxWidth="md" sx={{ my: 4 }}>
        {/* First Box - Image Left with Paragraphs */}
        <Box
          sx={{
            backgroundColor: "secondary.main",
            color: "primary.contrastText",
            p: { xs: 2, sm: 3 },
            borderRadius: "8px",
            boxShadow: 2,
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            alignItems: "center",
            justifyContent: "space-between",
            gap: { xs: 2, md: 4 },
            mb: 4,
          }}
        >
          <Box sx={{ flex: 1 }}>
            <Typography sx={{ fontSize: "18px", lineHeight: "1.6", mb: 2 }}>
              {t("about_paragraph_1")}
            </Typography>
            <Typography sx={{ fontSize: "18px", lineHeight: "1.6", mb: 2 }}>
              {t("about_paragraph_2")}
            </Typography>
            <Typography sx={{ fontSize: "18px", lineHeight: "1.6", mb: 2 }}>
              {t("about_paragraph_3")}
            </Typography>
          </Box>
          <Box sx={{ flex: 1 }}>
            <img
              src={placeHolderImage}
              alt="About Us"
              style={{
                width: "100%",
                maxWidth: 300,
                height: "auto",
                borderRadius: "8px",
                display: "block",
                margin: "0 auto",
              }}
            />
            <Typography
              sx={{
                fontSize: "18px",
                lineHeight: "1.6",
                mt: { xs: 2, md: 4 },
              }}
            >
              {t("about_paragraph_4")}
            </Typography>
          </Box>
        </Box>

        {/* Second Box - Image Right */}
        <Box
          sx={{
            backgroundColor: "primary.main",
            color: "primary.contrastText",
            p: { xs: 2, sm: 3 },
            borderRadius: "8px",
            boxShadow: 2,
            display: "flex",
            flexDirection: { xs: "column", md: "row-reverse" },
            alignItems: "center",
            justifyContent: "space-between",
            gap: { xs: 2, md: 4 },
            mb: 4,
          }}
        >
          <Box sx={{ flex: 1 }}>
            <Typography
              sx={{
                fontSize: "18px",
                lineHeight: "1.6",
                color: "primary.contrastText",
              }}
            >
              {t("about_paragraph_5")}
            </Typography>
            <List sx={{ listStyleType: "disc" }}>
              <ListItem sx={{ display: "list-item" }}>
                <Link
                  color={"inherit"}
                  href="https://www.facebook.com/EliyahuToolibrary/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {t("about_link_1")}
                </Link>
              </ListItem>
              <ListItem sx={{ display: "list-item" }}>
                <Link
                  color={"inherit"}
                  href="https://www.facebook.com/hakolboynik/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {t("about_link_2")}
                </Link>
              </ListItem>
              <ListItem sx={{ display: "list-item" }}>
                <Link
                  color={"inherit"}
                  href="https://www.chicagotoollibrary.org/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {t("about_link_3")}
                </Link>
              </ListItem>
            </List>
          </Box>
          <img
            src={placeHolderImage}
            alt="Services"
            style={{
              width: "100%",
              maxWidth: 250,
              height: "auto",
              borderRadius: "8px",
              display: "block",
              margin: "0 auto",
            }}
          />
        </Box>

        {/* Third Box - Image Left */}
        <Box
          sx={{
            backgroundColor: "secondary.main",
            color: "primary.contrastText",
            p: { xs: 2, sm: 3 },
            borderRadius: "8px",
            boxShadow: 2,
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            alignItems: "center",
            gap: { xs: 2, md: 4 },
            mb: 4,
          }}
        >
          <Typography sx={{ fontSize: "18px", lineHeight: "1.6", flex: 1 }}>
            {t("about_paragraph_6")}
          </Typography>
          <img
            src={placeHolderImage}
            alt="Location"
            style={{
              width: "100%",
              maxWidth: 300,
              height: "auto",
              borderRadius: "8px",
              display: "block",
              margin: "0 auto",
            }}
          />
        </Box>

        {/* Footer */}
        <Box
          sx={{
            backgroundColor: "secondary.main",
            color: "primary.contrastText",
            p: { xs: 2, sm: 3 },
            borderRadius: "8px",
            boxShadow: 2,
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            alignItems: "center",
            justifyContent: "space-between",
            mt: 4,
            gap: { xs: 2, md: 0 },
          }}
        >
          {/* Right Section with Activity Hours */}
          <Box
            sx={{
              textAlign: "center",
              flex: 1,
              pr: { xs: 0, md: 5 },
              mb: { xs: 2, md: 0 },
            }}
          >
            <Typography
              sx={{
                fontSize: "24px",
                fontWeight: "bold",
                lineHeight: "1.4",
              }}
            >
              {t("about_hours_title")}
            </Typography>
            <Typography sx={{ fontSize: "20px" }}>
              {t("about_hours_days")}
            </Typography>
            <Typography sx={{ fontSize: "18px" }}>
              {t("about_hours_time")}
            </Typography>
          </Box>

          {/* Middle Section with Contact Info */}
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              gap: "8px",
              pr: { xs: 0, md: "60px" },
              mb: { xs: 2, md: 0 },
            }}
          >
            {/* WhatsApp Row */}
            <Box sx={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <a
                href="https://api.whatsapp.com/send?phone=%E2%81%A6+972532483676&text=%D7%94%D7%99%D7%99%20%D7%A9%D7%95%D7%9C%D7%94!%20%D7%A8%D7%A6%D7%99%D7%AA%D7%99%20%D7%9C%D7%A9%D7%90%D7%95%D7%9C"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  textDecoration: "none",
                }}
              >
                <img
                  src={placeHolderImage}
                  alt="WhatsApp Logo"
                  style={{
                    height: "40px",
                    width: "40px",
                  }}
                />
              </a>
              <a
                href="https://api.whatsapp.com/send?phone=%E2%81%A6+972532483676&text=%D7%94%D7%99%D7%99%20%D7%A9%D7%95%D7%9C%D7%94!%20%D7%A8%D7%A6%D7%99%D7%AA%D7%99%20%D7%9C%D7%A9%D7%90%D7%95%D7%9C"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  fontSize: "18px",
                  color: "inherit",
                  textDecoration: "none",
                }}
              >
                {t("about_contact_whatsapp")}
              </a>
            </Box>

            {/* Facebook Row */}
            <Box sx={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <a
                href="https://www.facebook.com/shula.tveria15"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "flex",
                  alignItems: "center",
                  textDecoration: "none",
                }}
              >
                <img
                  src={placeHolderImage}
                  alt="Facebook Logo"
                  style={{
                    height: "40px",
                    width: "40px",
                  }}
                />
              </a>
              <a
                href="https://www.facebook.com/shula.tveria15"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  fontSize: "18px",
                  color: "inherit",
                  textDecoration: "none",
                }}
              >
                {t("about_contact_facebook")}
              </a>
            </Box>
          </Box>

          {/* Left Section with Logos */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: "16px",
              justifyContent: { xs: "center", md: "flex-end" },
              mt: { xs: 2, md: 0 },
            }}
          >
            <img
              src={placeHolderImage}
              alt="Tiberias Logo"
              style={{
                height: "70px",
                width: "70px",
                borderRadius: "8px",
              }}
            />
            <img
              src={placeHolderImage}
              alt="Hadar Logo"
              style={{
                height: "70px",
                width: "70px",
                borderRadius: "8px",
              }}
            />
          </Box>
        </Box>
      </Container>
    </Box>
  );
}

export default About;
