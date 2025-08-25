import React, { useState } from "react";
import {
  Button,
  TextField,
  Paper,
  Typography,
  Container,
  Link,
} from "@mui/material";
import api from "../api.js";
import {
  ACCESS_TOKEN,
  EP_LOGIN,
  PERMISSION,
  REFRESH_TOKEN,
  USER_NAME,
} from "../constants.js";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext.jsx";
import { useShared } from "../context/SharedContext.jsx";
import { Axios, HttpStatusCode } from "axios";
import { useTranslation } from "react-i18next";

const LoginForm = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const { login } = useAuth();
  const { setLoading, setErrorMessage, setActionMessage, refreshCartCount } =
    useShared();

  const handleFormSubmit = async (data) => {
    try {
      setLoading(true);
      const response = await api.post(EP_LOGIN, data);
      if (response.status === HttpStatusCode.Ok) {
        localStorage.setItem(ACCESS_TOKEN, response.data.token);
        localStorage.setItem(REFRESH_TOKEN, response.data.refresh);
        localStorage.setItem(PERMISSION, response.data.permission);
        localStorage.setItem(USER_NAME, response.data.user_name);
        login(response.data.permission, response.data.user_name);
        await refreshCartCount();
        navigate("/");
        setActionMessage(t("login_welcome"));
      }
    } catch (error) {
      if (error.status === HttpStatusCode.BadRequest) {
        if (error.response.data.error === "INVALID_CREDENTIALS") {
          setErrorMessage(t("login_invalid"));
        }
      } else if (
        error.response?.status === HttpStatusCode.Forbidden &&
        error.response.data.error === "EMAIL_NOT_VERIFIED"
      ) {
        setErrorMessage(t("login_email_not_verified")); // ✅ נכון
      } else {
        setErrorMessage();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegistrationRedirect = () => {
    navigate("/register");
  };

  return (
    <Container
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "80vh", // Ensures full viewport height
        flex: 1,
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
          maxWidth: 400,
        }}
      >
        <Typography
          variant="h5"
          sx={{ marginBottom: 3, color: "primary.main", textAlign: "right" }}
        >
          {t("login_title")}
        </Typography>
        <form onSubmit={handleSubmit(handleFormSubmit)}>
          <TextField
            label={t("login_email")}
            variant="outlined"
            type="email"
            {...register("email", { required: t("login_required_email") })}
            sx={{ marginBottom: 2, width: "100%" }}
            error={!!errors.email}
            helperText={errors.email?.message}
          />
          <TextField
            label={t("login_password")}
            variant="outlined"
            type="password"
            autoComplete="current-password"
            {...register("password", {
              required: t("login_required_password"),
            })}
            sx={{ marginBottom: 2, width: "100%" }}
            error={!!errors.password}
            helperText={errors.password?.message}
          />
          <Typography
            variant="body2"
            sx={{ marginBottom: 2, textAlign: "center" }}
          >
            {t("login_not_member")}{" "}
            <span
              onClick={handleRegistrationRedirect}
              style={{
                textDecoration: "underline",
                cursor: "pointer",
                color: "primary.main",
              }}
            >
              {t("login_register")}
            </span>
          </Typography>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ marginTop: 3 }}
          >
            {t("login_submit")}
          </Button>
        </form>
      </Paper>
    </Container>
  );
};

export default LoginForm;
