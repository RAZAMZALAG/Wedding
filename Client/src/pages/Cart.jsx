import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Typography,
  IconButton,
  Card,
  CardContent,
  CardMedia,
  Grid,
  Divider,
  Button,
  CircularProgress,
} from "@mui/material";
import {
  Delete as DeleteIcon,
  Remove as RemoveIcon,
  Add as AddIcon,
} from "@mui/icons-material";
import { Container, useTheme } from "@mui/system";
import api from "../api.js";
import { EP_BOOKING, EP_CART, EP_REMOVE_FROM_CART } from "../constants.js";
import { useShared } from "../context/SharedContext.jsx";
import { HttpStatusCode } from "axios";
import BookingStepperDialog from "../components/BookingStepperDialog.jsx";
import OrderStepperDialog from "../components/OrderStepperDialog.jsx";
import { useNavigate } from "react-router-dom";
import ItemImage from "../components/ItemImage.jsx";
import { useTranslation } from "react-i18next";

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [orderDialogOpen, setOrderDialogOpen] = useState(false);
  
  // Calculate total price
  const totalPrice = cartItems.reduce((sum, item) => sum + item.item_total, 0);
  const { setErrorMessage, refreshCartCount, openDialog, setCartCount } =
    useShared(); // <-- add setCartCount
  const navigate = useNavigate();
  const { t } = useTranslation();

  const abortControllerRef = useRef(null);

  const fetchItems = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setLoading(true);
      const response = await api.get(EP_CART, {
        signal: controller.signal,
      });
      if (!controller.signal.aborted) {
        if (response.status === HttpStatusCode.Ok) {
          setCartItems(response.data.items);
          refreshCartCount(); // <-- update context count
        }
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const increaseAmount = async (itemId) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await api.put(EP_CART + `/${itemId}/increase`);
      setCartItems((prevItems) =>
        prevItems.map((item) =>
          item.item.id === itemId ? { ...item, amount: item.amount + 1, item_total: item.item.price * (item.amount + 1) } : item,
        ),
      );
      refreshCartCount(); // <-- update context count
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    }
  };

  const decreaseAmount = async (itemId) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await api.put(EP_CART + `/${itemId}/decrease`);
      setCartItems((prevItems) =>
        prevItems.map((item) =>
          item.item.id === itemId ? { ...item, amount: item.amount - 1, item_total: item.item.price * (item.amount - 1) } : item,
        ),
      );
      refreshCartCount(); // <-- update context count
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    }
  };

  const removeItem = async (itemId) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await api.delete(EP_REMOVE_FROM_CART + `/${itemId}`);
      setCartItems((prevItems) =>
        prevItems.filter((item) => item.item.id !== itemId),
      );
      refreshCartCount(); // <-- update context count
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    }
  };

  const handleOrder = () => {
    setOrderDialogOpen(true);
  };

  const handleSubmitOrder = async (startDate, endDate, customerNotes) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setLoading(true);
      const response = await api.post(EP_BOOKING, {
        start_date: startDate,
        end_date: endDate,
        customer_notes: customerNotes || "",
      });
      if (response.status === 200 || response.status === 201) {
        setOrderDialogOpen(false);
        openDialog(
          t("cart_booking_success_title"),
          t("cart_booking_success_message"),
        );
        setCartCount(0);
        navigate("/");
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container
      sx={{ height: "100%", display: "flex", flexDirection: "column" }}
    >
      {/* Page Title */}
      <Typography variant="h4" align="center" sx={{ marginBottom: 3 }}>
        {t("cart_title")}
      </Typography>

      {/* Main Cart Content */}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center">
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ flexGrow: 1, marginTop: "15px" }}>
          {cartItems.length === 0 ? (
            <Typography
              variant="h6"
              color="textSecondary"
              align="center"
              sx={{ marginTop: 3 }}
            >
              {t("cart_empty")}
            </Typography>
          ) : (
            <Box sx={{ padding: 2 }}>
              <Grid container spacing={2}>
                {cartItems.map((item) => (
                  <Grid item xs={12} key={item.id}>
                    <Card
                      sx={{
                        display: { xs: "block", sm: "flex" },
                        maxWidth: 800,
                        margin: "auto",
                        mb: { xs: 2, sm: 0 },
                        p: { xs: 2, sm: 0 },
                        alignItems: "center",
                      }}
                    >
                      <ItemImage
                        item={item.item}
                        maxHeight={200}
                        width={151}
                        sx={{
                          margin: { xs: "0 auto 16px auto", sm: 0 },
                          display: "block",
                        }}
                      />
                      <Box
                        sx={{
                          display: "flex",
                          flexDirection: "column",
                          flexGrow: 1,
                          px: { xs: 0, sm: 2 },
                        }}
                      >
                        <CardContent
                          sx={{ flex: "1 0 auto", p: { xs: 1, sm: 2 } }}
                        >
                          <Typography
                            component="div"
                            variant="h5"
                            sx={{ mb: 1 }}
                          >
                            {t(`items.${item.item.name}`, { defaultValue: item.item.name })}
                          </Typography>
                          <Typography
                            sx={{ direction: "ltr", mb: 1 }}
                            variant="body2"
                            color="text.secondary"
                          >
                            {t("cart_unit_price", { price: item.item.price })}
                          </Typography>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              mt: 1,
                            }}
                          >
                            <Box sx={{ display: "flex", alignItems: "center" }}>
                              <IconButton
                                onClick={() => decreaseAmount(item.item.id)}
                                disabled={item.amount === 1}
                                size="small"
                              >
                                <RemoveIcon />
                              </IconButton>
                              <Typography sx={{ mx: 1 }}>
                                {item.amount}
                              </Typography>
                              <IconButton
                                onClick={() => increaseAmount(item.item.id)}
                                disabled={item.amount === item.item.total_amount}
                                size="small"
                              >
                                <AddIcon />
                              </IconButton>
                            </Box>
                            <IconButton
                              onClick={() => removeItem(item.item.id)}
                              color="error"
                              size="small"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </CardContent>
                      </Box>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Total price and booking button */}
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="h6">
                  {t("cart_total", { count: cartItems.length })}
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                  {t("cart_total_price", { price: totalPrice.toFixed(2) })}
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleOrder}
                >
                  {t("cart_borrow")}
                </Button>
              </Box>
            </Box>
          )}
        </Box>
      )}

      {/* Order Stepper Dialog */}
      <OrderStepperDialog
        openDialog={orderDialogOpen}
        setOpenDialog={setOrderDialogOpen}
        items={cartItems}
        handleSubmitOrder={handleSubmitOrder}
      />
    </Container>
  );
};

export default Cart;
