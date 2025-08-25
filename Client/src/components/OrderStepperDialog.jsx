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

  // Function to go to the next step
  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  // Function to go to the previous step
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  // Reset the dialog state
  const resetDialog = () => {
    setActiveStep(0);
    setStartDate(null);
    setEndDate(null);
    setItemsWithOrders([]);
    setOrdersLoading(false);
    setCustomerNotes("");
  };

  // When the dialog is closed, reset the state
  const handleCloseDialog = () => {
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
      return total + (item.price * item.amount * daysDiff);
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
  const handleOrder = () => {
    handleSubmitOrder(getDateOnly(startDate), getDateOnly(endDate), customerNotes);
    setOpenDialog(false);
  };

  // Check if event date is valid (not in the past, not on weekends, etc.)
  const isDateForbidden = (date) => {
    // Don't allow dates in the past
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (date < today) return true;

    // Don't allow dates too far in the future (optional business rule)
    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() + 2); // 2 years ahead
    if (date > maxDate) return true;

    return false;
  };

  // Validate if we can proceed to next step
  const canProceedToNext = () => {
    switch (activeStep) {
      case 0: // Date selection
        return startDate && endDate && !isDateForbidden(startDate) && !isDateForbidden(endDate);
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
                        filterDate={(date) => !isDateForbidden(date)}
                        dateFormat="dd/MM/yyyy"
                        placeholderText={t("select_date_range")}
                        customInput={
                          <TextField
                            fullWidth
                            variant="outlined"
                            error={(startDate && isDateForbidden(startDate)) || (endDate && isDateForbidden(endDate))}
                            helperText={
                              (startDate && isDateForbidden(startDate)) || (endDate && isDateForbidden(endDate)) 
                                ? t("date_not_available") 
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
                                    {item.name}
                                  </Typography>
                                </TableCell>
                                <TableCell align="center">
                                  <Typography variant="body2">
                                    {item.amount}
                                  </Typography>
                                </TableCell>
                                <TableCell align="right">
                                  <Typography variant="body2">
                                    ₪{item.price}/יום
                                  </Typography>
                                </TableCell>
                                <TableCell align="right">
                                  <Typography variant="body2" fontWeight="medium">
                                    ₪{item.price * item.amount * days}
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
