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
  useMediaQuery,
  useTheme,
} from "@mui/material";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import api from "../api.js";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { EP_LOCK_ITEMS, EP_EXTEND_LOCKS, EP_RELEASE_LOCKS, EP_CHECK_AVAILABILITY, EP_AVAILABLE_DATE_RANGES, EP_CHECK_DATE_RANGE } from "../constants.js";

const OrderStepperDialog = ({
  openDialog,
  setOpenDialog,
  items,
  handleSubmitOrder,
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [activeStep, setActiveStep] = useState(0);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [itemsWithOrders, setItemsWithOrders] = useState([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [customerNotes, setCustomerNotes] = useState("");
  const [itemsLocked, setItemsLocked] = useState(false); // Track if items are locked
  const [lockExtensionTimer, setLockExtensionTimer] = useState(null); // Timer for extending locks
  const [availableDates, setAvailableDates] = useState([]); // Available dates for calendar
  const [availabilityLoading, setAvailabilityLoading] = useState(false); // Loading state for availability check
  const [dateRangeValid, setDateRangeValid] = useState(true); // Is the selected date range valid
  const [rangeCheckLoading, setRangeCheckLoading] = useState(false); // Loading state for range validation

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

  // Function to load available dates
  const loadAvailableDates = async () => {
    try {
      setAvailabilityLoading(true);
      
      // Calculate date range (next 6 months)
      const today = new Date();
      const sixMonthsLater = new Date();
      sixMonthsLater.setMonth(today.getMonth() + 6);
      
      const response = await api.post(EP_AVAILABLE_DATE_RANGES, {
        range_start: today.toISOString().split('T')[0],
        range_end: sixMonthsLater.toISOString().split('T')[0]
      });
      
      if (response.status === 200) {
        const availableDateStrings = response.data.available_dates || [];
        // Keep as string array for more consistent comparison
        setAvailableDates(availableDateStrings);
        console.log("📅 Loaded available dates:", availableDateStrings.length, "dates");
        console.log("📅 First few available dates:", availableDateStrings.slice(0, 5));
      }
    } catch (error) {
      console.error("Error loading available dates:", error);
      setAvailableDates([]); // Fallback to no restrictions
    } finally {
      setAvailabilityLoading(false);
    }
  };

  // Function to check if a date range is available for all cart items
  const checkDateRangeAvailability = async (start, end) => {
    if (!start || !end) {
      setDateRangeValid(true);
      return;
    }

    try {
      setRangeCheckLoading(true);
      const response = await api.post(EP_CHECK_DATE_RANGE, {
        start_date: start.toISOString().split('T')[0],
        end_date: end.toISOString().split('T')[0]
      });
      
      if (response.status === 200) {
        setDateRangeValid(response.data.available);
        console.log("📅 Date range check:", response.data.available ? "✅ Available" : "❌ Not available", response.data);
      }
    } catch (error) {
      console.error("Error checking date range:", error);
      setDateRangeValid(false); // Default to not available on error
    } finally {
      setRangeCheckLoading(false);
    }
  };

  // Load available dates when dialog opens and items change
  useEffect(() => {
    if (openDialog && items && items.length > 0) {
      loadAvailableDates();
    }
  }, [openDialog, items]);

  // Check date range availability when dates change
  useEffect(() => {
    if (startDate && endDate) {
      checkDateRangeAvailability(startDate, endDate);
    } else {
      setDateRangeValid(true); // Reset validation when no dates selected
    }
  }, [startDate, endDate]);

  // Function to check if a date is available
  const isDateAvailable = (date) => {
    if (!date || availableDates.length === 0) {
      return true; // If no restrictions loaded, allow all dates (fallback)
    }
    
    // Check if this date is in the available dates list (compare strings)
    const dateString = date.toISOString().split('T')[0];
    return availableDates.includes(dateString);
  };

  // Function to check if a date should be disabled in calendar
  const isDateDisabled = (date) => {
    // Don't allow dates in the past
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (date < today) return true;

    // Don't allow dates too far in the future (1 year)
    const oneYearFromNow = new Date();
    oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);
    if (date > oneYearFromNow) return true;

    // Temporarily disable availability checking to debug the calendar
    // TODO: Re-enable this once calendar works
    // Check availability based on cart items
    // return !isDateAvailable(date);
    
    return false; // Allow all dates for now
  };

  // Reset the dialog state
  const resetDialog = () => {
    setActiveStep(0);
    setStartDate(null);
    setEndDate(null);
    setItemsWithOrders([]);
    setOrdersLoading(false);
    setCustomerNotes("");
    setItemsLocked(false);
    setAvailableDates([]);
    setAvailabilityLoading(false);
    setDateRangeValid(true);
    setRangeCheckLoading(false);
    if (lockExtensionTimer) {
      clearInterval(lockExtensionTimer);
      setLockExtensionTimer(null);
    }
  };

  // When the dialog is closed, reset the state
  const handleCloseDialog = () => {
    if (itemsLocked) {
      releaseLocks();
    }
    setOpenDialog(false);
    resetDialog();
  };

  // Steps
  const steps = [
    t("order_step_date"),
    t("order_step_review"),
    t("order_step_confirm")
  ];

  // Calculate total amount from cart items with rental days
  const calculateTotal = () => {
    if (!startDate || !endDate) return 0;
    
    const timeDiff = endDate.getTime() - startDate.getTime();
    const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1; // +1 to include both start and end days
    
    return items.reduce((total, item) => {
      return total + (item.item.price * item.amount * daysDiff);
    }, 0);
  };

  // Convert date to YYYY-MM-DD format for API
  const getDateOnly = (date) => {
    if (!date) return null;
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Handle order confirmation and pass data back to Cart for submission
  const handleOrder = async () => {
    try {
      await handleSubmitOrder(getDateOnly(startDate), getDateOnly(endDate), customerNotes);
      // Locks will be released automatically when the order is created on the server
      setItemsLocked(false);
      if (lockExtensionTimer) {
        clearInterval(lockExtensionTimer);
        setLockExtensionTimer(null);
      }
      setOpenDialog(false);
    } catch (error) {
      console.error("Error submitting order:", error);
      // Keep locks in case of error, user might want to try again
    }
  };

  // Check if event date is valid (not in the past, not on weekends, etc.)
  const isDateForbidden = (date) => {
    // Use the new availability-based date checking
    return isDateDisabled(date);
  };

  // Validate if we can proceed to next step
  const canProceedToNext = () => {
    switch (activeStep) {
      case 0: // Date selection
        return startDate && endDate && !isDateForbidden(startDate) && !isDateForbidden(endDate) && dateRangeValid && !rangeCheckLoading;
      case 1: // Review step
        return true;
      default:
        return false;
    }
  };

  // Reset dialog when it opens
  useEffect(() => {
    if (openDialog) {
      resetDialog();
    }
  }, [openDialog]);

  return (
    <Dialog
      open={openDialog}
      onClose={handleCloseDialog}
      fullWidth
      maxWidth="md"
      scroll="paper"
    >
      <DialogTitle>
        <Typography variant="h5" component="h2">
          {t("order_title")}
        </Typography>
      </DialogTitle>

      <DialogContent dividers>
        <Box sx={{ width: "100%" }}>
          <Stepper activeStep={activeStep} alternativeLabel={isMobile}>
            {steps.map((label, index) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          <Box sx={{ mt: 3 }}>
            {/* Step 0: Event Date Selection */}
            {activeStep === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  {t("select_event_date")}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {t("select_event_date_desc")}
                </Typography>
                
                {/* Show loading indicator while checking availability */}
                {availabilityLoading && (
                  <Box display="flex" justifyContent="center" alignItems="center" sx={{ mb: 2 }}>
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {t("checking_availability", { defaultValue: "בודק זמינות תאריכים..." })}
                    </Typography>
                  </Box>
                )}
                
                {/* Show availability info */}
                {!availabilityLoading && availableDates.length > 0 && (
                  <Typography variant="body2" color="info.main" sx={{ mb: 2 }}>
                    ✅ {availableDates.length} {t("available_dates_found", { defaultValue: "תאריכים זמינים נמצאו" })}
                  </Typography>
                )}
                
                {!availabilityLoading && availableDates.length === 0 && items.length > 0 && (
                  <Typography variant="body2" color="warning.main" sx={{ mb: 2 }}>
                    ⚠️ {t("no_available_dates", { defaultValue: "לא נמצאו תאריכים זמינים עבור הפריטים הנבחרים" })}
                  </Typography>
                )}

                {items.length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    ℹ️ {t("add_items_first", { defaultValue: "הוסף פריטים לעגלה כדי לראות תאריכים זמינים" })}
                  </Typography>
                )}
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        {t("rental_date_range")}
                      </Typography>
                      <DatePicker
                        selectsRange
                        startDate={startDate}
                        endDate={endDate}
                        onChange={(dates) => {
                          const [start, end] = dates;
                          setStartDate(start);
                          setEndDate(end);
                        }}
                        minDate={new Date()}
                        maxDate={new Date(new Date().setFullYear(new Date().getFullYear() + 2))}
                        filterDate={(date) => {
                          const isDisabled = isDateForbidden(date);
                          // Debug: log some dates to see what's happening
                          if (Math.random() < 0.01) { // Log only 1% of dates to avoid spam
                            console.log("📅 filterDate:", date.toISOString().split('T')[0], "disabled:", isDisabled);
                          }
                          return !isDisabled;
                        }}
                        dateFormat="dd/MM/yyyy"
                        placeholderText={t("select_date_range")}
                        popperProps={{
                          strategy: "fixed",
                          placement: "bottom-start",
                          modifiers: [
                            {
                              name: "preventOverflow",
                              options: {
                                boundary: "viewport",
                                padding: 8,
                              },
                            },
                            {
                              name: "flip",
                              options: {
                                fallbackPlacements: ["top-start", "bottom-end", "top-end"],
                              },
                            },
                            {
                              name: "offset",
                              options: {
                                offset: [0, 4],
                              },
                            },
                          ],
                        }}
                        popperClassName="calendar-popper"
                        customInput={
                          <TextField
                            fullWidth
                            variant="outlined"
                            error={(startDate && isDateForbidden(startDate)) || (endDate && isDateForbidden(endDate)) || !dateRangeValid}
                            helperText={
                              (startDate && isDateForbidden(startDate)) || (endDate && isDateForbidden(endDate)) 
                                ? t("date_not_available") 
                                : !dateRangeValid 
                                  ? t("date_range_not_available", { defaultValue: "טווח התאריכים הנבחר לא זמין עבור כל הפריטים" })
                                  : rangeCheckLoading 
                                    ? t("checking_availability", { defaultValue: "בודק זמינות..." })
                                    : ""
                            }
                          />
                        }
                      />
                    </Box>
                  </Grid>
                </Grid>

                {startDate && endDate && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: "primary.50", borderRadius: 1 }}>
                    <Typography variant="body2" color="primary.main">
                      {t("selected_rental_period")}: {startDate.toLocaleDateString('he-IL')} - {endDate.toLocaleDateString('he-IL')}
                    </Typography>
                    <Typography variant="body2" color="primary.main">
                      {t("rental_duration")}: {Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24)) + 1} {t("days")}
                    </Typography>
                    {rangeCheckLoading ? (
                      <Typography variant="body2" color="warning.main" sx={{ mt: 1 }}>
                        🔄 {t("checking_availability", { defaultValue: "בודק זמינות..." })}
                      </Typography>
                    ) : dateRangeValid ? (
                      <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
                        ✅ {t("date_range_available", { defaultValue: "טווח התאריכים זמין!" })}
                      </Typography>
                    ) : (
                      <Typography variant="body2" color="error.main" sx={{ mt: 1 }}>
                        ❌ {t("date_range_not_available", { defaultValue: "טווח התאריכים לא זמין עבור כל הפריטים" })}
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>
            )}

            {/* Step 1: Review Order */}
            {activeStep === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  {t("review_order")}
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={8}>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>{t("item_name")}</TableCell>
                            <TableCell align="center">{t("quantity")}</TableCell>
                            <TableCell align="right">{t("price_per_day")}</TableCell>
                            <TableCell align="right">{t("total_price")}</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {items.map((item, index) => {
                            const days = startDate && endDate ? Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24)) + 1 : 1;
                            return (
                              <TableRow key={index}>
                                <TableCell>
                                  <Typography variant="body2" fontWeight="medium">
                                    {item.item.name}
                                  </Typography>
                                </TableCell>
                                <TableCell align="center">
                                  <Typography variant="body2">
                                    {item.amount}
                                  </Typography>
                                </TableCell>
                                <TableCell align="right">
                                  <Typography variant="body2">
                                    ₪{item.item.price}/יום
                                  </Typography>
                                </TableCell>
                                <TableCell align="right">
                                  <Typography variant="body2" fontWeight="medium">
                                    ₪{item.item.price * item.amount * days}
                                  </Typography>
                                </TableCell>
                              </TableRow>
                            );
                          })}
                          <TableRow>
                            <TableCell colSpan={3}>
                              <Typography variant="h6" fontWeight="bold">
                                {t("total_amount")}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              <Typography variant="h6" fontWeight="bold" color="primary">
                                ₪{calculateTotal()}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Box sx={{ p: 2, bgcolor: "grey.50", borderRadius: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        {t("order_details")}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>{t("rental_period")}:</strong> {startDate?.toLocaleDateString('he-IL')} - {endDate?.toLocaleDateString('he-IL')}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>{t("rental_duration")}:</strong> {startDate && endDate ? Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24)) + 1 : 0} {t("days")}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>{t("items_count")}:</strong> {items.length}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        <strong>{t("total_amount")}:</strong> ₪{calculateTotal()}
                      </Typography>
                      
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label={t("customer_notes")}
                        placeholder={t("customer_notes_placeholder")}
                        value={customerNotes}
                        onChange={(e) => setCustomerNotes(e.target.value)}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            )}

            {/* Step 2: Confirmation */}
            {activeStep === 2 && (
              <Box textAlign="center">
                <Typography variant="h6" gutterBottom color="success.main">
                  {t("order_confirmation")}
                </Typography>
                <Typography variant="body1" sx={{ mb: 3 }}>
                  {t("order_confirmation_desc")}
                </Typography>
                
                <Box sx={{ p: 3, bgcolor: "success.50", borderRadius: 1, mb: 3 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    {t("order_will_be_processed")}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    {t("you_will_receive_confirmation")}
                  </Typography>
                  <Typography variant="body2">
                    {t("contact_us_for_questions")}
                  </Typography>
                </Box>
                
                <Button
                  variant="contained"
                  color="success"
                  size="large"
                  onClick={handleOrder}
                  sx={{ minWidth: 200 }}
                >
                  {t("confirm_order")}
                </Button>
              </Box>
            )}
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={handleCloseDialog} color="inherit">
          {t("cancel")}
        </Button>
        
        {activeStep > 0 && (
          <Button onClick={handleBack} color="inherit">
            {t("back")}
          </Button>
        )}
        
        {activeStep < steps.length - 1 && (
          <Button
            onClick={handleNext}
            variant="contained"
            disabled={!canProceedToNext()}
          >
            {t("next")}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default OrderStepperDialog;
