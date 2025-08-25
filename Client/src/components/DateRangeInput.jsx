import { forwardRef } from "react";
import {
  InputAdornment,
  IconButton,
  OutlinedInput,
  FormControl,
  InputLabel,
} from "@mui/material";
import ClearIcon from "@mui/icons-material/Clear";
import EventIcon from "@mui/icons-material/Event";

const DateRangeInput = forwardRef(
  ({ value, onClick, label, isSmall, setStartDate, setEndDate }, ref) => (
    <FormControl variant="outlined" size="small" fullWidth={isSmall}>
      <InputLabel>{label}</InputLabel>
      <OutlinedInput
        variant="outlined"
        size="small"
        label={label}
        fullWidth={isSmall}
        value={value}
        onClick={onClick}
        inputRef={ref}
        startAdornment={
          <InputAdornment position="start">
            <IconButton
              size="small"
              tabIndex={-1}
              edge="start"
              aria-label="בחר טווח תאריכים"
              disabled
              sx={{ pointerEvents: "none" }}
            >
              <EventIcon fontSize="small" />
            </IconButton>
          </InputAdornment>
        }
        endAdornment={
          <InputAdornment position="end">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                setStartDate(null);
                setEndDate(null);
              }}
              aria-label="נקה תאריכים"
            >
              <ClearIcon fontSize="small" />
            </IconButton>
          </InputAdornment>
        }
        readOnly // Prevent manual typing
      />
    </FormControl>
  ),
);

export default DateRangeInput;
