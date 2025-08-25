import React from "react";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Container,
  Link,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ContactForm from "../components/ContactForm.jsx"; // ← ייבוא מסודר

const QuestionsAndAnswers = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Array of questions and answers using translation keys
  const qaData = [
    {
      question: t("qa_1_q"),
      answer: (
        <>
          {t("qa_1_a").split("קטלוג").length > 1 ? (
            <>
              {t("qa_1_a").split("קטלוג")[0]}
              <Link
                component="button"
                onClick={() => navigate("/catalog")}
                sx={{ cursor: "pointer" }}
              >
                {t("qa_catalog")}
              </Link>
              {t("qa_1_a").split("קטלוג")[1]}
            </>
          ) : (
            t("qa_1_a")
          )}
        </>
      ),
    },
    { question: t("qa_2_q"), answer: t("qa_2_a") },
    { question: t("qa_3_q"), answer: t("qa_3_a") },
    { question: t("qa_4_q"), answer: t("qa_4_a") },
    { question: t("qa_5_q"), answer: t("qa_5_a") },
  ];

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" align="center" sx={{ mb: 4 }}>
        {t("qa_title")}
      </Typography>
      <Box>
        {qaData.map((item, index) => (
          <Accordion key={index}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls={`panel${index}-content`}
              id={`panel${index}-header`}
            >
              <Typography variant="h6">{item.question}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>{item.answer}</Typography>
            </AccordionDetails>
          </Accordion>
        ))}

        {/* ✨ תיבת הפנייה כאן */}
        <ContactForm />
      </Box>
    </Container>
  );
};

export default QuestionsAndAnswers;
