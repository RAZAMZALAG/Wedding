import React, { useState } from "react";
import {
  Button,
  TextField,
  Paper,
  Typography,
  Container,
  Checkbox,
  FormControlLabel,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Link,
  Box,
  CircularProgress,
} from "@mui/material";
import { useDropzone } from "react-dropzone";
import { useForm } from "react-hook-form";
import api from "../api.js";
import { useShared } from "../context/SharedContext.jsx";
import { EP_REGISTER } from "../constants.js";
import { useNavigate } from "react-router-dom";
import { HttpStatusCode } from "axios";
import { useTranslation, Trans } from "react-i18next";

const RegistrationForm = () => {
  const [error, setError] = useState("");
  const [file, setFile] = useState(null);
  const [agreement, setAgreement] = useState(false);
  const [isFileUploading, setIsFileUploading] = useState(false); // <-- NEW
  const [fileUploaded, setFileUploaded] = useState(false); // <-- NEW
  const { setLoading, setErrorMessage, openDialog } = useShared();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const LOCATION_VALUE_MAP = {
    הדר: "הדר",
    Hadar: "הדר",
    هدار: "הדר",
    Адар: "הדר",
    "לא מחיפה": "לא מחיפה",
    "Not from Haifa": "לא מחיפה",
    "ليس من حيفا": "לא מחיפה",
    "Не из Хайфы": "לא מחיפה",
    "מחיפה, לא מהדר": "מחיפה, לא מהדר",
    "From Haifa, not Hadar": "מחיפה, לא מהדר",
    "من حيفا، ليس من هدار": "מחיפה, לא מהדר",
    "Из Хайфы, не из Адара": "מחיפה, לא מהדר",
  };

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  // Simulate file upload/read for indication
  const onDrop = (acceptedFiles) => {
    const uploadedFile = acceptedFiles[0];
    if (uploadedFile) {
      setIsFileUploading(true);
      setFileUploaded(false);
      setFile(uploadedFile);
      setError("");
      // Simulate file reading/uploading
      const reader = new FileReader();
      reader.onload = () => {
        setTimeout(() => {
          setIsFileUploading(false);
          setFileUploaded(true);
        }, 700); // Simulate delay
      };
      reader.onerror = () => {
        setIsFileUploading(false);
        setFileUploaded(false);
        setError(t("register_upload_failed"));
      };
      reader.readAsArrayBuffer(uploadedFile);
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
      "application/pdf": [".pdf"],
    },
    maxSize: 5000000, // 5 MB limit (in bytes)
    onDropRejected: (fileRejections) => {
      setFileUploaded(false);
      setIsFileUploading(false);
      if (fileRejections[0]["errors"][0]["code"] === "file-invalid-type") {
        setError("קובץ בפורמט לא תקין.");
      } else {
        setError("הקובץ גדול מדי. אנא העלה קובץ בגודל של עד 5MB");
      }
    },
  });

  const handleFormSubmit = async (data) => {
    if (!file) {
      setError(t("register_upload_required"));
      return;
    }
    if (!agreement) {
      setError(t("register_agreement_required"));
      return;
    }
    if (isFileUploading) {
      setError(t("register_upload_in_progress"));
      return;
    }
    setError("");
    const locationHeb = LOCATION_VALUE_MAP[data.location] || data.location;
    // Create a FormData object
    const formData = new FormData();
    formData.append("firstName", data.firstName);
    formData.append("lastName", data.lastName);
    formData.append("phone", data.phone);
    formData.append("email", data.email);
    formData.append("password", data.password);
    formData.append("location", locationHeb);
    formData.append("agreement", agreement);
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await api.post(EP_REGISTER, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      if (response.status === HttpStatusCode.Created) {
        navigate("/login");
        openDialog(t("register_success_title"), t("register_success_message"));
      }
    } catch (error) {
      // --- FULL ERROR COVERAGE ---
      let msg = t("register_error_generic");
      if (error.response && error.response.data && error.response.data.error) {
        const err = error.response.data.error;
        console.log(err);
        switch (err) {
          case "ID REQUIRED":
            msg = t("register_upload_required");
            break;
          case "BAD ID FILE TYPE":
            msg = t("register_file_invalid");
            break;
          case "USER_EXISTS":
            msg = t("register_email_exists");
            break;
          case "FIRST_NAME_REQUIRED":
            msg = t("FIRST_NAME_REQUIRED");
            break;
          case "LAST_NAME_REQUIRED":
            msg = t("LAST_NAME_REQUIRED");
            break;
          case "PHONE_NUMBER_ILLEGAL":
            msg = t("PHONE_NUMBER_ILLEGAL");
            break;
          case "EMAIL_REQUIRED":
            msg = t("EMAIL_REQUIRED");
            break;
          case "LOCATION_REQUIRED":
            msg = t("LOCATION_REQUIRED");
            break;
          case "YOU_MUST_AGREE_TO_THE_TERMS_OF_USE":
            msg = t("YOU_MUST_AGREE_TO_THE_TERMS_OF_USE");
            break;
          case "PASSWORD_REQUIRED":
            msg = t("PASSWORD_REQUIRED");
            break;
          default:
            // If the error is a custom validation error from is_valid_* functions
            msg = t(err) !== err ? t(err) : t("register_error_generic");
        }
      }
      setError(msg);
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) {
      if (uploadedFile.size > 5000000) {
        setError("הקובץ גדול מדי. אנא העלה קובץ בגודל של עד 5MB");
        setFileUploaded(false);
        setIsFileUploading(false);
        return;
      }
      setIsFileUploading(true);
      setFileUploaded(false);
      setFile(uploadedFile);
      setError("");
      // Simulate file reading/uploading
      const reader = new FileReader();
      reader.onload = () => {
        setTimeout(() => {
          setIsFileUploading(false);
          setFileUploaded(true);
        }, 700); // Simulate delay
      };
      reader.onerror = () => {
        setIsFileUploading(false);
        setFileUploaded(false);
        setError(t("register_upload_failed"));
      };
      reader.readAsArrayBuffer(uploadedFile);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const uploadedFile = event.dataTransfer.files[0];
    if (uploadedFile) {
      setIsFileUploading(true);
      setFileUploaded(false);
      setFile(uploadedFile);
      setError("");
      // Simulate file reading/uploading
      const reader = new FileReader();
      reader.onload = () => {
        setTimeout(() => {
          setIsFileUploading(false);
          setFileUploaded(true);
        }, 700); // Simulate delay
      };
      reader.onerror = () => {
        setIsFileUploading(false);
        setFileUploaded(false);
        setError(t("register_upload_failed"));
      };
      reader.readAsArrayBuffer(uploadedFile);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  return (
    <Container
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Paper
        sx={{
          padding: 4,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          borderRadius: 2,
          boxShadow: 3,
          backgroundColor: "background.paper",
          width: "100%",
          maxWidth: 600,
        }}
      >
        <Typography
          variant="h5"
          sx={{ marginBottom: 3, color: "primary.main", textAlign: "right" }}
        >
          {t("register_title")}
        </Typography>
        <form onSubmit={handleSubmit(handleFormSubmit)}>
          <TextField
            label={t("register_first_name")}
            variant="outlined"
            {...register("firstName", {
              required: t("register_required_first_name"),
            })}
            sx={{ marginBottom: 2, width: "100%" }}
            error={!!errors.firstName}
            helperText={errors.firstName?.message}
          />
          <TextField
            label={t("register_last_name")}
            variant="outlined"
            {...register("lastName", {
              required: t("register_required_last_name"),
            })}
            sx={{ marginBottom: 2, width: "100%" }}
            error={!!errors.lastName}
            helperText={errors.lastName?.message}
          />
          <TextField
            label={t("register_phone")}
            variant="outlined"
            {...register("phone", { required: t("register_required_phone") })}
            sx={{ marginBottom: 2, width: "100%" }}
            error={!!errors.phone}
            helperText={errors.phone?.message}
          />
          <TextField
            label={t("register_email")}
            variant="outlined"
            type="email"
            {...register("email", { required: t("register_required_email") })}
            sx={{ marginBottom: 2, width: "100%" }}
            error={!!errors.email}
            helperText={errors.email?.message}
          />
          <TextField
            label={t("register_password")}
            variant="outlined"
            type="password"
            autoComplete="new-password"
            {...register("password", {
              required: t("register_required_password"),
            })}
            sx={{ marginBottom: 2, width: "100%" }}
            error={!!errors.password}
            helperText={errors.password?.message}
          />

          <FormControl fullWidth sx={{ marginBottom: 2 }}>
            <InputLabel>{t("register_location")}</InputLabel>
            <Select
              defaultValue={""}
              label={t("register_location")}
              {...register("location", {
                required: t("register_required_location"),
              })}
            >
              <MenuItem value="הדר">
                {t("register_location_option_hadar")}
              </MenuItem>
              <MenuItem value="לא מחיפה">
                {t("register_location_option_not_haifa")}
              </MenuItem>
              <MenuItem value="מחיפה, לא מהדר">
                {t("register_location_option_haifa_not_hadar")}
              </MenuItem>
            </Select>
          </FormControl>

          <Typography
            variant="body2"
            color="textSecondary"
            sx={{ marginBottom: 2 }}
          >
            {t("register_location_info")}
          </Typography>

          {/* Dropzone */}
          <Box
            {...getRootProps()}
            sx={{
              width: "100%",
              height: 150,
              border: "2px dashed",
              borderColor: "primary.main",
              borderRadius: 2,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              backgroundColor: "background.default",
              textAlign: "center",
              color: "text.secondary",
              marginBottom: 2,
              cursor: "pointer",
              position: "relative",
            }}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {!file ? (
              <Typography
                variant="body2"
                sx={{ fontSize: 14, whiteSpace: "pre-line" }}
              >
                {t("register_upload_id")}
              </Typography>
            ) : (
              <Typography
                variant="body2"
                sx={{ fontSize: 14, color: "text.primary" }}
              >
                {t("register_file_attached", { file: file.name })}
              </Typography>
            )}
            <input
              {...getInputProps()}
              type="file"
              accept=".jpg,.jpeg,.png,.pdf"
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                opacity: 0,
                cursor: "pointer",
              }}
              onChange={handleFileUpload}
              disabled={isFileUploading}
            />
            {/* Uploading indicator */}
            {isFileUploading && (
              <Box
                sx={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  bgcolor: "rgba(255,255,255,0.7)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  zIndex: 2,
                  flexDirection: "column",
                }}
              >
                <CircularProgress size={32} sx={{ mb: 1 }} />
              </Box>
            )}
          </Box>

          {error && (
            <Typography
              color="error"
              variant="body2"
              sx={{ marginBottom: 2, textAlign: "right" }}
            >
              {error}
            </Typography>
          )}

          <FormControlLabel
            control={
              <Checkbox
                checked={agreement}
                onChange={() => setAgreement(!agreement)}
                name="agreement"
                color="primary"
              />
            }
            label={
              <span style={{ fontSize: "0.875rem", textAlign: "right" }}>
                <Trans i18nKey="register_agreement">
                  אני מאשר.ת שקראתי והבנתי את{" "}
                  <Link
                    href="https://bit.ly/3KtU1RG"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    תנאי השימוש
                  </Link>{" "}
                  בספריית הציוד.
                </Trans>
              </span>
            }
          />

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ marginTop: 3 }}
            disabled={isFileUploading}
          >
            {isFileUploading ? t("register_uploading") : t("register_submit")}
          </Button>
        </form>
      </Paper>
    </Container>
  );
};

export default RegistrationForm;
