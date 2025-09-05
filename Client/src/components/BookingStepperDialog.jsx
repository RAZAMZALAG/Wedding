import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
  Stepper,
  Step,
  StepLabel,
  Grid,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  CircularProgress,
  useMediaQuery, // <-- Add this
  useTheme, // <-- Add this
} from "@mui/material";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import api from "../api.js"; // instead of axios
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { EP_LOCK_ITEMS, EP_EXTEND_LOCKS, EP_RELEASE_LOCKS } from "../constants.js";

const BookingStepperDialog = ({
  openDialog,
  setOpenDialog,
  items,
  handleSubmitBooking,
}) => {
  const { t } = useTranslation();
  const theme = useTheme(); // <-- Add this
  const isMobile = useMediaQuery(theme.breakpoints.down("sm")); // <-- Add this
  const [activeStep, setActiveStep] = useState(0);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [unitCount, setUnitCount] = useState(0); // Number of valid booking days
  const [itemsWithBookings, setItemsWithBookings] = useState([]);
  const [bookingsLoading, setBookingsLoading] = useState(false); // Loading state for bookings
  const [itemsLocked, setItemsLocked] = useState(false); // Track if items are locked
  const [lockExtensionTimer, setLockExtensionTimer] = useState(null); // Timer for extending locks

  // Function to go to the next step
  const handleNext = async () => {
    // If moving from date selection step to review step, lock the items
    if (activeStep === 0 && startDate && endDate && !itemsLocked) {
      try {
        await lockItems();
        setItemsLocked(true);
      } catch (error) {
        console.error("Failed to lock items:", error);
        // You might want to show an error message to the user here
        return; // Don't proceed to next step if locking failed
      }
    }
    setActiveStep((prevStep) => prevStep + 1);
  };

  // Function to go to the previous step
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  // Function to lock items temporarily
  const lockItems = async () => {
    try {
      const response = await api.post(EP_LOCK_ITEMS, {
        start_date: getDateOnly(startDate),
        end_date: getDateOnly(endDate),
        session_id: Date.now().toString() // Simple session ID
      });
      
      if (response.status === 201) {
        console.log("Items locked successfully:", response.data);
        // Set up timer to extend locks every 25 minutes
        setupLockExtensionTimer();
        return response.data;
      }
    } catch (error) {
      console.error("Error locking items:", error);
      throw error;
    }
  };

  // Function to extend lock expiration
  const extendLocks = async () => {
    try {
      await api.post(EP_EXTEND_LOCKS, {
        additional_minutes: 30
      });
      console.log("Locks extended successfully");
    } catch (error) {
      console.error("Error extending locks:", error);
    }
  };

  // Function to release locks
  const releaseLocks = async () => {
    try {
      await api.delete(EP_RELEASE_LOCKS);
      console.log("Locks released successfully");
      setItemsLocked(false);
      if (lockExtensionTimer) {
        clearInterval(lockExtensionTimer);
        setLockExtensionTimer(null);
      }
    } catch (error) {
      console.error("Error releasing locks:", error);
    }
  };

  // Setup timer to extend locks periodically
  const setupLockExtensionTimer = () => {
    if (lockExtensionTimer) {
      clearInterval(lockExtensionTimer);
    }
    
    const timer = setInterval(() => {
      extendLocks();
    }, 25 * 60 * 1000); // Extend every 25 minutes
    
    setLockExtensionTimer(timer);
  };

  // Handle dialog close - release locks
  const handleDialogClose = () => {
    if (itemsLocked) {
      releaseLocks();
    }
    setOpenDialog(false);
  };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (lockExtensionTimer) {
        clearInterval(lockExtensionTimer);
      }
      if (itemsLocked) {
        releaseLocks();
      }
    };
  }, [lockExtensionTimer, itemsLocked]);

  // Function to count the valid booking days (Sunday, Tuesday, Thursday) between start and end dates
  const calculateUnitCount = (start, end) => {
    if (!start || !end) return 0;

    let count = 0;
    let currentDate = new Date(start);
    currentDate.setHours(0, 0, 0, 0); // Normalize the time to midnight for consistency

    while (currentDate <= end) {
      const day = currentDate.getDay(); // 0 = Sunday, 2 = Tuesday, 4 = Thursday
      if (day === 0 || day === 2 || day === 4) {
        count++;
      }
      currentDate.setDate(currentDate.getDate() + 1); // Move to the next day
    }

    return count;
  };

  // Effect to calculate unit count whenever the dates change
  useEffect(() => {
    if (startDate && endDate) {
      const units = calculateUnitCount(startDate, endDate);
      setUnitCount(units);
    }
  }, [startDate, endDate]);

  // Calculate the new total price based on unitCount and item prices
  const calculateTotalPrice = () => {
    return (
      unitCount *
      items.reduce((total, item) => total + item.price * item.amount, 0)
    );
  };

  const getDateOnly = (date) => {
    // Ensure the date is valid
    if (!date) return null;

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0"); // Months are 0-based
    const day = String(date.getDate()).padStart(2, "0"); // Ensure 2-digit day

    // Return the date in YYYY-MM-DD format
    return `${year}-${month}-${day}`;
  };

  // Handle booking confirmation and pass data back to Cart for submission
  const handleBooking = async () => {
    try {
      await handleSubmitBooking(getDateOnly(startDate), getDateOnly(endDate)); // Pass finalPrice to submit the booking
      // Locks will be released automatically when the order is created on the server
      setItemsLocked(false);
      if (lockExtensionTimer) {
        clearInterval(lockExtensionTimer);
        setLockExtensionTimer(null);
      }
      setOpenDialog(false); // Close the dialog after booking
    } catch (error) {
      console.error("Error submitting booking:", error);
      // Keep locks in case of error, user might want to try again
    }
  };

  function isDateForbidden(date, items) {
    // For each item in the cart
    for (const item of items) {
      // item.bookings should be an array of {start_date, end_date, status, amount}
      if (!item.bookings) continue;

      // Sum up the amount booked for this date with relevant statuses
      let bookedAmount = 0;
      for (const booking of item.bookings) {
        if (
          ["PENDING", "APPROVED", "COLLECTED"].includes(
            booking.status?.toUpperCase(),
          ) &&
          booking.start_date &&
          booking.end_date
        ) {
          const start = new Date(booking.start_date);
          const end = new Date(booking.end_date);
          // If the date is within the booking range
          if (date >= start && date <= end) {
            bookedAmount += booking.amount;
          }
        }
      }

      // If the booked amount + cart amount > total available, mark as forbidden
      if (bookedAmount + item.amount > item.total_amount) {
        return true;
      }
    }
    return false;
  }

  function isRangeForbidden(start, end, items) {
    if (!start || !end) return false;
    let current = new Date(start);
    current.setHours(0, 0, 0, 0);
    const last = new Date(end);
    last.setHours(0, 0, 0, 0);

    while (current <= last) {
      // Only check allowed days (Sunday, Tuesday, Thursday)
      const day = current.getDay();
      if (day === 0 || day === 2 || day === 4) {
        if (isDateForbidden(new Date(current), items)) {
          return true;
        }
      }
      current.setDate(current.getDate() + 1);
    }
    return false;
  }

  useEffect(() => {
    if (!items || items.length === 0) return;

    const fetchBookings = async () => {
      setBookingsLoading(true); // <-- set loading before fetch
      try {
        const itemIds = items.map((item) => item.id).join(",");
        const res = await api.get(
          `/api/bookings/item_bookings?item_ids=${itemIds}`,
        );
        const bookingsByItem = res.data;

        // Attach bookings to each item
        const itemsWithBookings = items.map((item) => ({
          ...item,
          bookings: bookingsByItem[item.id] || [],
        }));
        setItemsWithBookings(itemsWithBookings);
      } catch (err) {
        // Optionally handle error
      } finally {
        setBookingsLoading(false); // <-- stop loading after fetch
      }
    };

    fetchBookings();
  }, [items]);

  return (
    <Dialog
      open={openDialog}
      onClose={handleDialogClose}
      fullWidth
      fullScreen={isMobile} // <-- Add this
    >
      <DialogTitle>{t("booking_dialog_title")}</DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mt: 3 }}>
          <Step>
            <StepLabel>{t("booking_step_dates")}</StepLabel>
          </Step>
          <Step>
            <StepLabel>{t("booking_step_review")}</StepLabel>
          </Step>
        </Stepper>

        {/* Step 1: Date Range Selection */}
        {activeStep === 0 && (
          <Grid container spacing={2} sx={{ mt: 3 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle1">
                {t("booking_select_dates")}
              </Typography>
              <div className="customDatePickerWidth">
                {bookingsLoading ? (
                  <Box
                    display="flex"
                    justifyContent="center"
                    alignItems="center"
                    minHeight={56}
                  >
                    <CircularProgress size={28} />
                  </Box>
                ) : (
                  <DatePicker
                    portalId="root-portal"
                    selectsRange={true}
                    startDate={startDate}
                    endDate={endDate}
                    dayClassName={(date) =>
                      isDateForbidden(date, itemsWithBookings)
                        ? "forbidden-date"
                        : undefined
                    }
                    onChange={(update) => {
                      const [start, end] = update;
                      if (start && end) {
                        if (isRangeForbidden(start, end, itemsWithBookings)) {
                          // Optionally show an error message here
                          return; // Do not update selection
                        }
                        setStartDate(start);
                        setEndDate(end);
                      } else {
                        setStartDate(start);
                        setEndDate(end);
                      }
                    }}
                    withPortal
                    minDate={new Date()}
                    customInput={
                      <TextField
                        variant="standard"
                        size="small"
                        sx={{
                          padding: "0 8px",
                          fontSize: "0.875rem",
                        }}
                      />
                    }
                  />
                )}
              </div>
            </Grid>
            <Box
              display="flex"
              justifyContent="space-between"
              mt={3}
              sx={{ width: "100%" }}
            >
              <Button
                variant="outlined"
                onClick={handleBack}
                disabled={activeStep === 0}
                sx={{ width: "48%" }}
              >
                {t("booking_back")}
              </Button>
              <Button
                variant="contained"
                onClick={handleNext}
                sx={{ width: "48%" }}
                disabled={!startDate || !endDate}
              >
                {t("booking_next")}
              </Button>
            </Box>
          </Grid>
        )}

        {/* Step 2: Review and Confirm */}
        {activeStep === 1 && (
          <Grid container spacing={2} sx={{ mt: 3 }}>
            <Grid item xs={12}>
              <Typography variant="h6">{t("booking_review_title")}</Typography>

              {/* Items Table */}
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell align="center">
                        <strong>{t("booking_item_name")}</strong>
                      </TableCell>
                      <TableCell align="center">
                        <strong>{t("booking_item_amount")}</strong>
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell align="center">
                          {t(`items.${item.name}`, { defaultValue: item.name })}
                        </TableCell>
                        <TableCell align="center">{item.amount}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Typography variant="body1" sx={{ mt: 2 }}>
                <strong>{t("booking_dates")}</strong>{" "}
                {startDate ? startDate.toLocaleDateString() : ""} -{" "}
                {endDate ? endDate.toLocaleDateString() : ""}
              </Typography>
              <Typography variant="body1">
                <strong>{t("booking_periods")}</strong> {unitCount}
              </Typography>
              <Typography variant="body1">
                <strong>{t("booking_total_price")}</strong>{" "}
                {calculateTotalPrice()} ₪
              </Typography>
            </Grid>
            <Box
              display="flex"
              justifyContent="space-between"
              mt={3}
              sx={{ width: "100%" }}
            >
              <Button
                variant="outlined"
                onClick={handleBack}
                sx={{ width: "48%" }}
              >
                {t("booking_back")}
              </Button>
              <Button
                variant="contained"
                onClick={handleBooking}
                sx={{ width: "48%" }}
              >
                {t("booking_confirm")}
              </Button>
            </Box>
          </Grid>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleDialogClose} color="primary">
          {t("booking_close")}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BookingStepperDialog;
