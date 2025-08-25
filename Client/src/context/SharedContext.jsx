import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import api from "../api.js";
import { EP_CART } from "../constants.js";
import { useAuth } from "./AuthContext.jsx";

const SharedContext = createContext({
  isLoading: false,
  error: "",
  message: "",
  cartCount: 0,
  dialogOpen: false,
  dialogTitle: "",
  dialogMessage: "",
  setLoading: (loading) => {},
  setErrorMessage: (error) => {},
  clearErrorMessage: () => {},
  setActionMessage: (message) => {},
  clearActionMessage: () => {},
  setCartCount: (count) => {},
  refreshCartCount: () => {},
  openDialog: (title, message) => {},
  closeDialog: () => {},
});

export const useShared = () => {
  return useContext(SharedContext);
};

export const SharedProvider = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [cartCount, setCartCount] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogTitle, setDialogTitle] = useState("");
  const [dialogMessage, setDialogMessage] = useState("");
  const { isLoggedIn } = useAuth();

  const setLoading = (loading) => {
    setIsLoading(loading);
  };

  const setErrorMessage = (errorMessage) => {
    if (errorMessage) {
      setError(errorMessage);
    } else {
      setError("שגיאת מערכת");
    }
  };

  const clearErrorMessage = () => {
    setError("");
  };

  const setActionMessage = (msg) => {
    setMessage(""); // Clear first to ensure Snackbar can re-open
    setTimeout(() => setMessage(msg), 0);
  };

  const clearActionMessage = (message) => {
    setMessage("");
  };

  const openDialog = (title, message) => {
    setDialogTitle(title);
    setDialogMessage(message);
    setDialogOpen(true);
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setDialogTitle("");
    setDialogMessage("");
  };

  // Fetch cart count from server
  const refreshCartCount = useCallback(async () => {
    if (!isLoggedIn) {
      setCartCount(0);
      return;
    }
    try {
      const res = await api.get(EP_CART);
      // Sum all item amounts in the cart
      const count = Array.isArray(res.data.items)
        ? res.data.items.reduce((sum, item) => sum + (item.amount || 1), 0)
        : 0;
      setCartCount(count);
    } catch (e) {
      setCartCount(0);
    }
  }, [isLoggedIn]);

  // On first load
  useEffect(() => {
    refreshCartCount();
  }, [refreshCartCount]);

  return (
    <SharedContext.Provider
      value={{
        isLoading,
        error,
        message,
        cartCount,
        setLoading,
        setErrorMessage,
        clearErrorMessage,
        setActionMessage,
        clearActionMessage,
        setCartCount,
        refreshCartCount,
        dialogOpen,
        dialogTitle,
        dialogMessage,
        openDialog,
        closeDialog,
      }}
    >
      {children}
    </SharedContext.Provider>
  );
};
