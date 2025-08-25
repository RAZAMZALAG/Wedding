import { useShared } from "../context/SharedContext.jsx";
import { IconButton, Snackbar, SnackbarContent } from "@mui/material";
import React, { useEffect, useState } from "react";
import CloseIcon from "@mui/icons-material/Close";

const ActionMessage = () => {
  const { message, clearActionMessage } = useShared();
  const [open, setOpen] = useState(true);

  useEffect(() => {
    if (message) {
      setOpen(true);
    }
  }, [message]);

  const handleClose = () => {
    setOpen(false);
  };

  const action = (
    <React.Fragment>
      <IconButton
        size="small"
        aria-label="close"
        color="inherit"
        onClick={handleClose}
      >
        <CloseIcon fontSize="small" />
      </IconButton>
    </React.Fragment>
  );

  return (
    <Snackbar
      open={open}
      onClose={handleClose}
      autoHideDuration={5000}
      anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
      sx={{ backgroundColor: "transparent", boxShadow: "none" }}
    >
      <SnackbarContent
        message={message}
        action={action}
        sx={{
          backgroundColor: (theme) => theme.palette.primary.main,
          color: (theme) => theme.palette.primary.contrastText,
          borderRadius: "8px",
          padding: "10px 20px",
        }}
      />
    </Snackbar>
  );
};

export default ActionMessage;
