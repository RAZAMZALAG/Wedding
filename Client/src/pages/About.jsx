import React from "react";
import { useTranslation } from "react-i18next";
// Note: All placeholder images removed as they were not working
import {
  Box,
  Typography,
  Container,
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
          <Box>
            <Typography sx={{ fontSize: "18px", lineHeight: "1.6", mb: 2 }}>
              {t("about_paragraph_1")}
            </Typography>
            <Typography sx={{ fontSize: "18px", lineHeight: "1.6", mb: 2 }}>
              {t("about_paragraph_2")}
            </Typography>
            <Typography sx={{ fontSize: "18px", lineHeight: "1.6", mb: 2 }}>
              {t("about_paragraph_3")}
            </Typography>
            <Typography
              sx={{
                fontSize: "18px",
                lineHeight: "1.6",
                mt: 2,
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
            mb: 4,
          }}
        >
          <Box>
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
                <Typography color="inherit">
                  {t("about_link_1")}
                </Typography>
              </ListItem>
              <ListItem sx={{ display: "list-item" }}>
                <Typography color="inherit">
                  {t("about_link_2")}
                </Typography>
              </ListItem>
              <ListItem sx={{ display: "list-item" }}>
                <Typography color="inherit">
                  {t("about_link_3")}
                </Typography>
              </ListItem>
            </List>
          </Box>
        </Box>

        {/* Third Box - Image Left */}
        <Box
          sx={{
            backgroundColor: "secondary.main",
            color: "primary.contrastText",
            p: { xs: 2, sm: 3 },
            borderRadius: "8px",
            boxShadow: 2,
            mb: 4,
          }}
        >
          <Typography sx={{ fontSize: "18px", lineHeight: "1.6" }}>
            {t("about_paragraph_6")}
          </Typography>
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
              <Typography
                sx={{
                  fontSize: "18px",
                  color: "inherit",
                }}
              >
                {t("about_contact_whatsapp")}
              </Typography>
            </Box>

            {/* Facebook Row */}
            <Box sx={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <Typography
                sx={{
                  fontSize: "18px",
                  color: "inherit",
                }}
              >
                {t("about_contact_facebook")}
              </Typography>
            </Box>
          </Box>

          {/* Left Section - removed logos */}
        </Box>
      </Container>
    </Box>
  );
}

export default About;
