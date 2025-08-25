import React from "react";
import { Backdrop, CircularProgress } from "@mui/material";

const Loading = ({ open }) => {
  return (
    <Backdrop open={open} sx={{ zIndex: 9999 }}>
      <CircularProgress size={100} color="primary" />
    </Backdrop>
  );
};

export default Loading;
