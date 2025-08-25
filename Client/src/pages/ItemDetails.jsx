import React, { useEffect, useRef, useState } from "react";
import {
  Container,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Button,
  CircularProgress,
} from "@mui/material";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api";
import { EP_ADD_TO_CART, EP_ITEM, EP_REMOVE_FROM_CART } from "../constants";
import placeHolderImage from "../assets/tool_placeholder.svg";
import { useShared } from "../context/SharedContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import AddShoppingCartIcon from "@mui/icons-material/AddShoppingCart";
import RemoveShoppingCartIcon from "@mui/icons-material/RemoveShoppingCart";
import { HttpStatusCode } from "axios";
import ItemImage from "../components/ItemImage.jsx";
import { useTranslation } from "react-i18next";

const ItemDetails = () => {
  const { id } = useParams(); // Get item ID from URL
  const [item, setItem] = useState(null);
  const [itemLoading, setItemLoading] = useState(false);
  const [localLoading, setLocalLoading] = useState(true);
  const [error, setError] = useState(null);
  const { setErrorMessage, setLoading, setActionMessage, refreshCartCount } =
    useShared();
  const { permission, isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const abortControllerRef = useRef(null);

  useEffect(() => {
    const fetchItem = async () => {
      try {
        setLocalLoading(true);
        const response = await api.get(`${EP_ITEM}/${id}`);
        setItem(response.data);
      } catch (err) {
        setError("לא ניתן לטעון את פרטי הפריט");
      } finally {
        setLocalLoading(false);
      }
    };
    fetchItem();
  }, [id]);

  const changeCartStatus = async () => {
    // Abort the previous request if any is in progress
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create a new AbortController for the current request
    const controller = new AbortController();
    abortControllerRef.current = controller;
    try {
      setItemLoading(true);
      const response = !item.in_cart
        ? await api.post(EP_ADD_TO_CART + `/${item.id}`, {
            signal: controller.signal,
          })
        : await api.delete(EP_REMOVE_FROM_CART + `/${item.id}`, {
            signal: controller.signal,
          });
      // If the request is not aborted, update state with the response data
      if (!controller.signal.aborted) {
        if (
          response.status === HttpStatusCode.Ok ||
          response.status === HttpStatusCode.Created
        ) {
          setActionMessage(
            !item.in_cart
              ? t("item_added_to_cart", { name: item.name })
              : t("item_removed_from_cart", { name: item.name }),
          );
          setItem((prevItem) => ({
            ...prevItem,
            in_cart: !item.in_cart,
          }));
          refreshCartCount(); // <-- Add this line
        }
      }
    } catch (error) {
      console.log(error);
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    } finally {
      setItemLoading(false);
    }
  };

  if (localLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography variant="h6" color="error" align="center">
        {error}
      </Typography>
    );
  }

  return (
    <Container sx={{ mt: 4 }}>
      <Card
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: 3,
        }}
      >
        <ItemImage item={item} maxHeight={700}></ItemImage>
        <CardContent sx={{ width: "100%" }}>
          <Typography variant="h4" gutterBottom>
            {t(`items.${item.name}`, { defaultValue: item.name })}
          </Typography>
          <Typography variant="body1" gutterBottom>
            <strong>{t("catalog_category_label")}</strong>{" "}
            {t(`categories.${item.category}`, { defaultValue: item.category })}
          </Typography>
          <Typography variant="body1" gutterBottom>
            <strong>{t("catalog_price_label")}</strong> {item.price} ₪
          </Typography>
          <Typography variant="body1" gutterBottom>
            <strong>{t("catalog_in_stock")}</strong> {item.amount}
          </Typography>
          {item.condition && (
            <Typography variant="body1" gutterBottom>
              <strong>מצב:</strong> {item.condition}
            </Typography>
          )}
          {item.description && (
            <Typography variant="body1" gutterBottom>
              <strong>תיאור:</strong> {item.description}
            </Typography>
          )}
          {item.notes && (
            <Typography variant="body1" gutterBottom>
              <strong>הערות:</strong> {item.notes}
            </Typography>
          )}
          <Box display="flex" justifyContent="space-between" mt={3}>
            <Button
              disabled={itemLoading || !isLoggedIn}
              onClick={() => changeCartStatus()}
              variant={item.in_cart ? "contained" : "outlined"}
              startIcon={
                item.in_cart ? (
                  <RemoveShoppingCartIcon />
                ) : (
                  <AddShoppingCartIcon />
                )
              }
            >
              {item.in_cart ? "הסר מהסל" : "הוסף לסל"}
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => navigate("/catalog")}
            >
              חזרה
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default ItemDetails;
