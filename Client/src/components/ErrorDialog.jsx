// src/components/ErrorDialog.js
import React, { useEffect } from "react";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
  Typography,
} from "@mui/material";
import ErrorIcon from "@mui/icons-material/Error";
import { useShared } from "../context/SharedContext.jsx"; // Error icon

const ErrorDialog = () => {
  const { error, clearErrorMessage } = useShared();
  const [open, setOpen] = React.useState(false);

  useEffect(() => {
    if (error) {
      setOpen(true);
    }
  }, [error]);

  const handleClose = () => {
    setOpen(false);
    clearErrorMessage();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      sx={{
        "& .MuiDialog-paper": {
          borderRadius: "8px",
          padding: 0,
        },
      }}
    >
      <DialogTitle
        sx={{
          display: "flex",
          alignItems: "center",
          padding: "16px 24px", // Add padding around the title
        }}
      >
        <ErrorIcon fontSize="large" sx={{ marginRight: 1, marginLeft: 1 }} />
        <span>
          <Typography variant={"h4"}>שגיאה</Typography>
        </span>
      </DialogTitle>
      <DialogContent
        sx={{
          padding: "20px", // Add padding for the content area
        }}
      >
        <Typography>{error}</Typography>
      </DialogContent>
      <DialogActions
        sx={{
          // Red background for the actions
          padding: "12px 24px", // Add padding to the actions area
        }}
      >
        <Button variant={"outlined"} onClick={handleClose}>
          סגור
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ErrorDialog;
