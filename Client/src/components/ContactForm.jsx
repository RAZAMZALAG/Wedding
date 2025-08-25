import React, { useState } from "react";
import { Box, TextField, Button, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

const ContactForm = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = new FormData();
    form.append("entry.1255747714", formData.name);
    form.append("entry.2069698709", formData.email);
    form.append("entry.1046175113", formData.message);

    await fetch(
      "https://docs.google.com/forms/d/e/1FAIpQLScN5LJVimw8hPP_FFgG7XsUcbvo2TOz-nVAS8_9C9eECFt8OA/formResponse",
      {
        method: "POST",
        mode: "no-cors",
        body: form,
      },
    );

    alert("הפנייה נשלחה בהצלחה!");
    setFormData({ name: "", email: "", message: "" });
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        {t("contact_form_title")}
      </Typography>
      <TextField
        label={t("contact_form_name")}
        name="name"
        value={formData.name}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      <TextField
        label={t("contact_form_email")}
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      <TextField
        label={t("contact_form_message")}
        name="message"
        value={formData.message}
        onChange={handleChange}
        fullWidth
        margin="normal"
        multiline
        rows={4}
        required
      />
      <Button variant="contained" type="submit" sx={{ mt: 2 }}>
        {t("contact_form_submit")}
      </Button>
    </Box>
  );
};

export default ContactForm;
