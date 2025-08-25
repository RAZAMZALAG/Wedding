import React from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import { useShared } from "../context/SharedContext";
import { useTranslation } from "react-i18next";

const OkDialog = () => {
  const { dialogOpen, dialogTitle, dialogMessage, closeDialog } = useShared();
  const { t } = useTranslation();

  return (
    <Dialog open={dialogOpen} onClose={closeDialog}>
      {dialogTitle && <DialogTitle>{dialogTitle}</DialogTitle>}
      <DialogContent>{dialogMessage}</DialogContent>
      <DialogActions>
        <Button onClick={closeDialog} autoFocus>
          {t("ok")}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default OkDialog;
