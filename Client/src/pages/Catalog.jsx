import React, { useState, useEffect, useRef } from "react";
import {
  Grid2,
  Card,
  CardContent,
  Typography,
  Container,
  TextField,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Box,
  Checkbox,
  FormControlLabel,
  Pagination,
  CircularProgress,
  CardActions,
  Button,
  CardActionArea,
  IconButton,
  Paper,
  Stack,
  useTheme,
  useMediaQuery,
  InputAdornment,
  OutlinedInput,
  Drawer,
} from "@mui/material";
import api from "../api.js";
import {
  EP_ADD_TO_CART,
  EP_REMOVE_FROM_CART,
  EP_ITEMS,
  EP_ADD_ITEM,
  EP_EDIT_ITEM,
  EP_DELETE_ITEM,
  EP_CATEGORIES,
} from "../constants.js";
import { useShared } from "../context/SharedContext.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useNavigate, useLocation } from "react-router-dom";
import { HttpStatusCode } from "axios";
import AddShoppingCartIcon from "@mui/icons-material/AddShoppingCart";
import InfoIcon from "@mui/icons-material/Info";
import RemoveShoppingCartIcon from "@mui/icons-material/RemoveShoppingCart";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import ItemImage from "../components/ItemImage.jsx";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import DatePicker from "react-datepicker";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { useDropzone } from "react-dropzone";
import SearchIcon from "@mui/icons-material/Search";
import DateRangeInput from "../components/DateRangeInput.jsx";
import CategoryIcon from "@mui/icons-material/Category";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import TuneIcon from "@mui/icons-material/Tune";
import zIndex from "@mui/material/styles/zIndex.js";
import { useTranslation } from "react-i18next";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import CancelIcon from "@mui/icons-material/Cancel";
import ViewListIcon from "@mui/icons-material/ViewList";
import ViewModuleIcon from "@mui/icons-material/ViewModule";

const Catalog = () => {
  const { t } = useTranslation();
  const [items, setItems] = useState([]); // State to hold fetched items
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [categories, setCategories] = useState([]);
  const [filtersChanged, setFiltersChanged] = useState(true);
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [groupByCategory, setGroupByCategory] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0); // Total items for pagination
  const [itemLoading, setItemLoading] = useState({});
  const itemsPerPage = 20;
  const [catalogLoading, setCatalogLoading] = useState(true);
  const navigate = useNavigate();
  const { setErrorMessage, setLoading, refreshCartCount, setActionMessage } =
    useShared();
  const { permission, isLoggedIn } = useAuth();
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newItem, setNewItem] = useState({
    name: "",
    category: "",
    price: "",
    amount: "",
    hidden: false,
    image: null,
  });
  const [addError, setAddError] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [editImageFile, setEditImageFile] = useState(null);
  const [editError, setEditError] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [addFieldErrors, setAddFieldErrors] = useState({});
  const [itemToDelete, setItemToDelete] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();
  const hasSetCategoryFromUrl = useRef(false);

  // Load categories on component mount
  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    if (hasSetCategoryFromUrl.current) return;
    const params = new URLSearchParams(location.search);
    const cat = params.get("category");
    if (cat && categories.includes(cat)) {
      setCategoryFilter(cat);
      hasSetCategoryFromUrl.current = true;
    } else if (cat && categories.length > 0) {
      setCategoryFilter("");
      hasSetCategoryFromUrl.current = true;
    }
    // eslint-disable-next-line
  }, [location.search, categories]);

  // Add this effect to sync search param from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const searchParam = params.get("search");
    if (searchParam && searchParam !== search) {
      setSearch(searchParam);
    }
    // Optionally: also handle category param here if needed
    // eslint-disable-next-line
  }, [location.search]);

  const {
    getRootProps: getEditRootProps,
    getInputProps: getEditInputProps,
    isDragActive: isEditDragActive,
  } = useDropzone({
    onDrop: (acceptedFiles, fileRejections) => {
      if (acceptedFiles.length) {
        setEditImageFile(acceptedFiles[0]);
        setEditError("");
      } else if (fileRejections.length) {
        if (fileRejections[0].errors[0].code === "file-invalid-type") {
          setEditError("קובץ בפורמט לא תקין. יש להעלות JPG או PNG בלבד.");
        } else {
          setEditError("הקובץ גדול מדי. עד 5MB בלבד.");
        }
      }
    },
    accept: { "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"] },
    maxSize: 5 * 1024 * 1024,
    multiple: false,
  });

  // Ref to keep track of the current fetch request
  const abortControllerRef = useRef(null);

  // פונקציה נפרדת לטעינת קטגוריות
  const fetchCategories = async () => {
    try {
      const response = await api.get(EP_CATEGORIES);
      if (response.status === HttpStatusCode.Ok) {
        const categoriesData = response.data || [];
        setCategories(categoriesData);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
      setCategories([]);
    }
  };

  // Function to fetch items with query params
  const fetchItems = async () => {
    // Abort the previous request if any is in progress
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create a new AbortController for the current request
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const params = new URLSearchParams();
    params.append("page", currentPage);
    params.append("amount_per_page", itemsPerPage);
    params.append("filter_by_name", search);
    params.append("category", categoryFilter);
    params.append("only_available", showAvailableOnly);
    params.append("load_categories", true);
    if (startDate && endDate) {
      const startDateStr = startDate.toISOString().split("T")[0];
      const endDateStr = endDate.toISOString().split("T")[0];
      params.append("start_date", startDateStr);
      params.append("end_date", endDateStr);
      console.log("🗓️ Date range sent to server:", startDateStr, "to", endDateStr);
    } else {
      console.log("❌ No date range selected");
    }
    try {
      setCatalogLoading(true);
      console.log("📡 Fetching items with params:", Object.fromEntries(params));
      const response = await api.get(EP_ITEMS, {
        params,
        signal: controller.signal, // Pass the signal to allow request cancellation
      });

      // If the request is not aborted, update state with the response data
      if (!controller.signal.aborted) {
        if (response.status === HttpStatusCode.Ok) {
          console.log("✅ Items received:", response.data.items?.length, "items");
          console.log("📊 Total items from server:", response.data.total || response.data.total_items);
          // Log first item with available_amount for debugging
          if (response.data.items?.[0]) {
            console.log("🔍 Sample item data:", {
              name: response.data.items[0].name,
              total_amount: response.data.items[0].total_amount || response.data.items[0].amount,
              available_amount: response.data.items[0].available_amount,
              booked_amount: response.data.items[0].booked_amount
            });
          }
          setItems(response.data.items || []);
          setTotalItems(response.data.total || response.data.total_items || 0);
          setCategories(response.data.categories || []);
        }
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    } finally {
      setCatalogLoading(false);
    }
  };

  // Handle the search input change
  const handleSearchChange = (event) => {
    resetPageWithoutFetch();
    setSearch(event.target.value);
  };

  const resetPageWithoutFetch = () => {
    setFiltersChanged(true); // Mark filters as changed
    setCurrentPage(1); // Reset the page
  };

  const changeCartStatus = async (itemId, newStatus) => {
    // Abort the previous request if any is in progress
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create a new AbortController for the current request
    const controller = new AbortController();
    abortControllerRef.current = controller;
    try {
      setItemLoading((prevLoading) => ({ ...prevLoading, [itemId]: true }));
      const response = newStatus
        ? await api.post(EP_ADD_TO_CART + `/${itemId}`, {
            signal: controller.signal,
          })
        : await api.delete(EP_REMOVE_FROM_CART + `/${itemId}`, {
            signal: controller.signal,
          });
      // If the request is not aborted, update state with the response data
      if (!controller.signal.aborted) {
        if (
          response.status === HttpStatusCode.Ok ||
          response.status === HttpStatusCode.Created
        ) {
          setItems((prevItems) =>
            prevItems.map((item) => {
              if (item.id === itemId) {
                setActionMessage(
                  newStatus
                    ? t("item_added_to_cart", { name: item.name })
                    : t("item_removed_from_cart", { name: item.name }),
                );
                return { ...item, in_cart: newStatus };
              }
              return item;
            }),
          );
          refreshCartCount();
        }
      }
    } catch (error) {
      console.log(error);
      if (!controller.signal.aborted) {
        setErrorMessage();
      }
    } finally {
      setItemLoading((prevLoading) => ({ ...prevLoading, [itemId]: false }));
    }
  };

  useEffect(() => {
    console.log("🔄 useEffect triggered. Filters changed:", filtersChanged, {
      startDate: startDate ? startDate.toISOString().split("T")[0] : null,
      endDate: endDate ? endDate.toISOString().split("T")[0] : null,
      debouncedSearch,
      categoryFilter,
      showAvailableOnly,
      currentPage
    });
    
    if (filtersChanged) {
      fetchItems();
      setFiltersChanged(false); // Reset the flag after fetching
    }
  }, [
    debouncedSearch,
    categoryFilter,
    showAvailableOnly,
    currentPage,
    startDate,
    endDate,
  ]);

  // Update `debouncedSearch` after a delay when `search` changes
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search); // Update debounced search
    }, 500); // Adjust the delay as needed (500ms is typical)

    // Cleanup the timeout if `search` changes before the delay ends
    return () => clearTimeout(handler);
  }, [search]);

  // Trigger fetch when the debounced search changes
  useEffect(() => {
    if (debouncedSearch !== "") {
      setFiltersChanged(true); // Mark filters as changed
    }
  }, [debouncedSearch]);

  useEffect(() => {
    if ((startDate && endDate) || (!startDate && !endDate)) {
      setFiltersChanged(true);
      setCurrentPage(1); // Reset to first page when dates change
    }
  }, [startDate, endDate]);

  // Handle page change
  const handlePageChange = (event, value) => {
    setFiltersChanged(true);
    setCurrentPage(value);
    window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
  };

  // Handle "Show Available Only" checkbox change
  const handleShowAvailableOnlyChange = (event) => {
    resetPageWithoutFetch();
    setShowAvailableOnly(event.target.checked); // Update state and trigger fetch
  };

  const handleCategoryFilterChange = (event) => {
    resetPageWithoutFetch();
    setCategoryFilter(event.target.value);

    // Remove 'category' from the URL if it exists
    const params = new URLSearchParams(location.search);
    if (params.has("category")) {
      params.delete("category");
      navigate(
        {
          pathname: location.pathname,
          search: params.toString() ? `?${params.toString()}` : "",
        },
        { replace: true },
      );
    }
  };

  const onDrop = (acceptedFiles, fileRejections) => {
    if (acceptedFiles.length) {
      setImageFile(acceptedFiles[0]);
      setAddError("");
    } else if (fileRejections.length) {
      if (fileRejections[0].errors[0].code === "file-invalid-type") {
        setAddError("קובץ בפורמט לא תקין. יש להעלות JPG או PNG בלבד.");
      } else {
        setAddError("הקובץ גדול מדי. עד 5MB בלבד.");
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"] },
    maxSize: 5 * 1024 * 1024,
    multiple: false,
  });

  // Handle dialog open/close
  const handleOpenAddDialog = () => {
    setAddDialogOpen(true);
    setNewItem({
      name: "",
      category: "",
      price: "",
      amount: "",
      hidden: false,
      image: null,
    });
    setImageFile(null);
    setAddError("");
  };
  const handleCloseAddDialog = () => setAddDialogOpen(false);

  // Handle form field changes
  const handleNewItemChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewItem((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleOpenEditDialog = (item) => {
    setEditItem({
      ...item,
      image: null, // reset image for new upload
    });
    setEditImageFile(null);
    setEditError("");
    setEditDialogOpen(true);
  };

  const handleCloseEditDialog = () => setEditDialogOpen(false);

  const handleEditItemChange = (e) => {
    const { name, value, type, checked } = e.target;
    setEditItem((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleOpenDeleteDialog = (item) => {
    setItemToDelete(item);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setItemToDelete(null);
  };

  const handleAddItem = async () => {
    const errors = {};
    if (!newItem.name) errors.name = "שדה חובה";
    if (!newItem.category) errors.category = "שדה חובה";
    if (!newItem.price) errors.price = "שדה חובה";
    if (!newItem.amount) errors.amount = "שדה חובה";
    if (!imageFile) errors.image = "יש להעלות תמונה";

    setAddFieldErrors(errors);

    if (Object.keys(errors).length > 0) {
      setAddError("יש למלא את כל השדות");
      return;
    }
    const formData = new FormData();
    formData.append("name", newItem.name);
    formData.append("category", newItem.category);
    formData.append("price", newItem.price);
    formData.append("amount", newItem.amount);
    formData.append("hidden", newItem.hidden);
    formData.append("image", imageFile);

    try {
      setLoading(true);
      const response = await api.post(EP_ADD_ITEM, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (response.status === 201) {
        setItems((prev) => [response.data, ...prev]);
        handleCloseAddDialog();
      }
    } catch (error) {
      setAddError("שגיאה בהוספת פריט");
    } finally {
      setLoading(false);
    }
  };

  const handleEditItem = async () => {
    if (
      !editItem.name ||
      !editItem.category ||
      !editItem.price ||
      !editItem.amount
    ) {
      setEditError("יש למלא את כל השדות");
      return;
    }
    const formData = new FormData();
    formData.append("name", editItem.name);
    formData.append("category", editItem.category);
    formData.append("price", editItem.price);
    formData.append("amount", editItem.amount);
    formData.append("hidden", editItem.hidden);
    if (editImageFile) {
      formData.append("image", editImageFile);
    }
    try {
      setLoading(true);
      const response = await api.put(EP_EDIT_ITEM + editItem.id, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (response.status === 200) {
        setItems((prev) =>
          prev.map((item) => (item.id === editItem.id ? response.data : item)),
        );
        handleCloseEditDialog();
      }
    } catch (error) {
      setEditError("שגיאה בעריכת פריט");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async () => {
    if (!itemToDelete) return;
    try {
      setLoading(true);
      const response = await api.delete(EP_DELETE_ITEM + itemToDelete.id);
      if (response.status === 200) {
        setItems((prev) => prev.filter((item) => item.id !== itemToDelete.id));
        handleCloseDeleteDialog();
      }
    } catch (error) {
      setErrorMessage("שגיאה במחיקת פריט");
    } finally {
      setLoading(false);
    }
  };

  // פונקציה לקבץ פריטים לפי קטגוריות
  const groupItemsByCategory = (items) => {
    const grouped = {};
    items.forEach(item => {
      const category = item.category || 'ללא קטגוריה';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(item);
    });
    return grouped;
  };

  const theme = useTheme();
  const isSmall = useMediaQuery(theme.breakpoints.down("sm"));

  const getAvailabilityColor = (amount, total, theme) => {
    if (total === 0) return theme.palette.text.disabled;
    if (amount === total) return "#43a047"; // modern green
    if (amount === 0) return "#e53935"; // modern red
    return "#ffb300"; // modern yellow/orange
  };

  return (
    <Container
      sx={{ height: "100%", display: "flex", flexDirection: "column" }}
    >
      {isSmall && (
        <Box display="flex" justifyContent="center" mb={1}>
          <IconButton
            onClick={() => setDrawerOpen(true)}
            color="primary"
            aria-label={t("catalog_filter")}
            size="large"
            sx={{ border: 1, borderColor: "divider", borderRadius: 2 }}
          >
            <TuneIcon />
            <span style={{ marginRight: 8 }}>{t("catalog_filter")}</span>
            <KeyboardArrowDownIcon />
          </IconButton>
        </Box>
      )}
      <Drawer
        anchor="top"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: {
            borderRadius: "0 0 16px 16px",
            p: 2,
            top: 64,
            height: "calc(100vh - 64px)",
            position: "fixed",
          },
        }}
        ModalProps={{
          keepMounted: true,
        }}
      >
        <Box display="flex" justifyContent="flex-end" mb={2}>
          <Button
            onClick={() => setDrawerOpen(false)}
            variant="contained"
            color="error"
            size="large"
            sx={{
              fontWeight: "bold",
              borderRadius: 2,
              px: 3,
              py: 1,
              boxShadow: 2,
            }}
          >
            {t("catalog_close_filter")}
          </Button>
        </Box>
        <Paper elevation={0} sx={{ p: 0, mb: 0, boxShadow: "none" }}>
          <Stack
            direction="column"
            spacing={2}
            alignItems="stretch"
            flexWrap="wrap"
          >
            <TextField
              label={t("catalog_search_item")}
              variant="outlined"
              value={search}
              onChange={handleSearchChange}
              size="small"
              fullWidth
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            <DateRangeInput
              label={t("catalog_date_range")}
              isSmall={true}
              setStartDate={setStartDate}
              setEndDate={setEndDate}
            />
            <FormControl variant="outlined" size="small" fullWidth>
              <InputLabel>{t("catalog_category")}</InputLabel>
              <Select
                value={categoryFilter}
                onChange={handleCategoryFilterChange}
                label={t("catalog_category")}
                input={
                  <OutlinedInput
                    label={t("catalog_category")}
                    startAdornment={
                      <InputAdornment position="start">
                        <CategoryIcon fontSize="small" />
                      </InputAdornment>
                    }
                  />
                }
              >
                <MenuItem value="">{t("catalog_all")}</MenuItem>
                {categories.length > 0 ? (
                  categories.map((category) => {
                    const trimmed = category.trim();
                    return (
                      <MenuItem key={trimmed} value={trimmed}>
                        {t(`categories.${trimmed}`, { defaultValue: trimmed })}
                      </MenuItem>
                    );
                  })
                ) : (
                  <MenuItem disabled>{t("catalog_no_categories")}</MenuItem>
                )}
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Checkbox
                  checked={showAvailableOnly}
                  onChange={handleShowAvailableOnlyChange}
                  color="primary"
                  size="small"
                />
              }
              label={t("catalog_show_available")}
              sx={{ ml: 0 }}
            />
          </Stack>
        </Paper>
      </Drawer>
      {/* Inline filters for desktop */}
      {!isSmall && (
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
          <Stack
            direction="row"
            spacing={2}
            justifyContent="center"
            alignItems="center"
            flexWrap="wrap"
          >
            <TextField
              label={t("catalog_search_item")}
              variant="outlined"
              value={search}
              onChange={handleSearchChange}
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 200 }}
            />
            <Box sx={{ minWidth: 180 }}>
              <DatePicker
                portalId="root-portal"
                selectsRange
                startDate={startDate}
                endDate={endDate}
                onChange={(dates) => {
                  const [start, end] = dates;
                  console.log("📅 DatePicker onChange:", {
                    start: start ? start.toISOString().split("T")[0] : null,
                    end: end ? end.toISOString().split("T")[0] : null
                  });
                  setStartDate(start);
                  setEndDate(end);
                  // Force filters to update
                  setFiltersChanged(true);
                }}
                withPortal
                minDate={new Date()}
                customInput={
                  <DateRangeInput
                    label={t("catalog_date_range")}
                    isSmall={false}
                    setStartDate={setStartDate}
                    setEndDate={setEndDate}
                  />
                }
              />
            </Box>
            <FormControl variant="outlined" size="small" sx={{ minWidth: 140 }}>
              <InputLabel>{t("catalog_category")}</InputLabel>
              <Select
                value={categoryFilter}
                onChange={handleCategoryFilterChange}
                label={t("catalog_category")}
                input={
                  <OutlinedInput
                    label={t("catalog_category")}
                    startAdornment={
                      <InputAdornment position="start">
                        <CategoryIcon fontSize="small" />
                      </InputAdornment>
                    }
                  />
                }
              >
                <MenuItem value="">{t("catalog_all")}</MenuItem>
                {categories.length > 0 ? (
                  categories.map((category) => {
                    const trimmed = category.trim();
                    return (
                      <MenuItem key={trimmed} value={trimmed}>
                        {t(`categories.${trimmed}`, { defaultValue: trimmed })}
                      </MenuItem>
                    );
                  })
                ) : (
                  <MenuItem disabled>{t("catalog_no_categories")}</MenuItem>
                )}
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Checkbox
                  checked={showAvailableOnly}
                  onChange={handleShowAvailableOnlyChange}
                  color="primary"
                  size="small"
                />
              }
              label={t("catalog_show_available")}
              sx={{ ml: 1 }}
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={groupByCategory}
                  onChange={(e) => setGroupByCategory(e.target.checked)}
                  color="primary"
                  size="small"
                  icon={<ViewModuleIcon />}
                  checkedIcon={<ViewListIcon />}
                />
              }
              label="קבץ לפי קטגוריות"
              sx={{ ml: 1 }}
            />
          </Stack>
        </Paper>
      )}
      {permission > 1 && (
        <Box
          display="flex"
          justifyContent={isSmall ? "stretch" : "center"}
          mb={2}
        >
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenAddDialog}
            size="small"
            sx={{ minWidth: isSmall ? "100%" : 200 }}
            fullWidth={isSmall}
          >
            {t("catalog_add_item")}
          </Button>
        </Box>
      )}
      {catalogLoading ? (
        <Box display="flex" justifyContent="center" alignItems="center">
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ flexGrow: 1, marginTop: "15px" }}>
          {/* Show empty message when no items are available */}
          {items.length === 0 ? (
            <Typography
              variant="h6"
              color="textSecondary"
              align="center"
              sx={{ marginTop: 3 }}
            >
              {t("catalog_no_items")}
            </Typography>
          ) : groupByCategory ? (
            // תצוגה מקובצת לפי קטגוריות
            Object.entries(groupItemsByCategory(items)).map(([category, categoryItems]) => (
              <Box key={category} sx={{ mb: 4 }}>
                <Typography 
                  variant="h5" 
                  component="h2" 
                  sx={{ 
                    mb: 2, 
                    color: 'primary.main', 
                    fontWeight: 'bold',
                    borderBottom: '2px solid',
                    borderColor: 'primary.main',
                    pb: 1
                  }}
                >
                  {category} ({categoryItems.length} מוצרים)
                </Typography>
                <Grid2
                  container
                  spacing={{ xs: 2, md: 3 }}
                  columns={{ xs: 2, sm: 8, md: 16 }}
                >
                  {categoryItems.map((item) => (
                    <Grid2 size={{ xs: 2, sm: 4, md: 4 }} key={item.id}>
                      {/* כאן נשתמש ברכיב Card הקיים */}
                      <Card
                        sx={{
                          maxWidth: { xs: "100%", sm: 300, md: 350 },
                          wordWrap: "break-word",
                          overflow: "hidden",
                          transition: "transform 0.3s ease-in-out",
                          "&:hover": {
                            transform: "scale(1.05)",
                          },
                          border: item.hidden ? 2 : undefined,
                          borderColor: item.hidden ? "text.disabled" : undefined,
                          boxSizing: "border-box",
                        }}
                      >
                        {/* נעתיק את תוכן ה-Card מהתצוגה הרגילה */}
                        {permission > 1 && (
                          <Box
                            display="flex"
                            justifyContent="space-between"
                            alignItems="center"
                            sx={{ p: 1 }}
                          >
                            <IconButton
                              onClick={() => {
                                setEditItem(item);
                                setEditDialogOpen(true);
                              }}
                              size="small"
                              color="primary"
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                            <IconButton
                              onClick={() => {
                                setItemToDelete(item);
                                setDeleteDialogOpen(true);
                              }}
                              size="small"
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Box>
                        )}
                        <CardActionArea>
                          <ItemImage item={item} />
                          <CardContent>
                            <Typography variant="h6" component="div">
                              {item.name}
                            </Typography>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ marginBottom: "10px" }}
                            >
                              <strong>{t("catalog_category")}:</strong> {item.category}
                            </Typography>
                            <Typography
                              variant="h6"
                              component="div"
                              sx={{ marginBottom: "10px", color: "primary.main" }}
                            >
                              ₪{item.price}
                            </Typography>
                            <Typography
                              variant="body2"
                              color="text.primary"
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                transition: "color 0.3s",
                              }}
                            >
                              <strong>{t("catalog_in_stock")}&nbsp;</strong>
                              {item.available_amount !== undefined 
                                ? `${item.available_amount} / ${item.total_amount ?? item.amount}` 
                                : `${item.amount} / ${item.total_amount ?? item.amount}`}
                              {item.date_range && (
                                <span style={{ fontSize: '0.8em', color: '#666', marginLeft: '8px' }}>
                                  ({item.date_range})
                                </span>
                              )}
                            </Typography>
                          </CardContent>
                          <CardActions>
                            <Button
                              variant="outlined"
                              startIcon={<InfoIcon />}
                              onClick={() => navigate(`/item/${item.id}`)}
                            >
                              {t("catalog_more_info")}
                            </Button>
                            {isLoggedIn && (
                              <Button
                                disabled={itemLoading[item.id]}
                                onClick={() =>
                                  changeCartStatus(item.id, !item.in_cart)
                                }
                                variant={item.in_cart ? "contained" : "outlined"}
                                startIcon={
                                  item.in_cart ? (
                                    <RemoveShoppingCartIcon />
                                  ) : (
                                    <AddShoppingCartIcon />
                                  )
                                }
                              >
                                {item.in_cart
                                  ? t("catalog_remove_from_cart")
                                  : t("catalog_add_to_cart")}
                              </Button>
                            )}
                          </CardActions>
                        </CardActionArea>
                      </Card>
                    </Grid2>
                  ))}
                </Grid2>
              </Box>
            ))
          ) : (
            // תצוגה רגילה
            <Grid2
              container
              spacing={{ xs: 2, md: 3 }}
              columns={{ xs: 2, sm: 8, md: 16 }}
            >
              {items.map((item) => (
                <Grid2 size={{ xs: 2, sm: 4, md: 4 }} key={item.id}>
                  <Card
                    sx={{
                      maxWidth: { xs: "100%", sm: 300, md: 350 },
                      wordWrap: "break-word",
                      overflow: "hidden",
                      transition: "transform 0.3s ease-in-out",
                      "&:hover": {
                        transform: "scale(1.05)",
                      },
                      border: item.hidden ? 2 : undefined,
                      borderColor: item.hidden ? "text.disabled" : undefined,
                      boxSizing: "border-box", // ensures border doesn't exceed card size
                    }}
                  >
                    {permission > 1 && (
                      <Box
                        display="flex"
                        justifyContent="space-between"
                        alignItems="center"
                        px={1}
                        pt={1}
                      >
                        {/* Hidden icon on one side */}
                        <Box>
                          {item.hidden && (
                            <VisibilityOffIcon
                              sx={{ color: "text.disabled" }}
                              titleAccess="פריט מוסתר"
                            />
                          )}
                        </Box>
                        {/* Edit/Delete buttons on the other side */}
                        <Box>
                          <IconButton
                            aria-label="ערוך פריט"
                            onClick={() => handleOpenEditDialog(item)}
                            sx={{ color: "#FFC107" }}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            aria-label="מחק פריט"
                            onClick={() => handleOpenDeleteDialog(item)}
                            sx={{ color: "error.main" }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      </Box>
                    )}
                    <ItemImage item={item} maxHeight={500}></ItemImage>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {t(`items.${item.name}`, { defaultValue: item.name })}
                      </Typography>
                      <Typography variant="body1" color="textSecondary">
                        <strong>{t("catalog_category_label")}</strong>{" "}
                        {t(`categories.${item.category}`, {
                          defaultValue: item.category,
                        })}
                      </Typography>
                      <Typography variant="body1" color="textSecondary">
                        <strong>{t("catalog_price_label")}</strong> {item.price}{" "}
                        ₪
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{
                          color: getAvailabilityColor(
                            item.available_amount !== undefined ? item.available_amount : item.amount,
                            item.total_amount ?? item.amount,
                            theme,
                          ),
                          fontWeight: 600,
                          fontSize: "1.1rem",
                          letterSpacing: "0.5px",
                          display: "flex",
                          alignItems: "center",
                          transition: "color 0.3s",
                        }}
                      >
                        {" "}
                        <strong> {t("catalog_in_stock")}&nbsp;</strong>
                        {item.available_amount !== undefined 
                          ? `${item.available_amount} / ${item.total_amount ?? item.amount}` 
                          : `${item.amount} / ${item.total_amount ?? item.amount}`}
                        {item.date_range && (
                          <span style={{ fontSize: '0.8em', color: '#666', marginLeft: '8px' }}>
                            ({item.date_range})
                          </span>
                        )}
                        {" "}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button
                        variant="outlined"
                        startIcon={<InfoIcon />}
                        onClick={() => navigate(`/item/${item.id}`)}
                      >
                        {t("catalog_more_info")}
                      </Button>
                      {isLoggedIn && (
                        <Button
                          disabled={itemLoading[item.id]}
                          onClick={() =>
                            changeCartStatus(item.id, !item.in_cart)
                          }
                          variant={item.in_cart ? "contained" : "outlined"}
                          startIcon={
                            item.in_cart ? (
                              <RemoveShoppingCartIcon />
                            ) : (
                              <AddShoppingCartIcon />
                            )
                          }
                        >
                          {item.in_cart
                            ? t("catalog_remove_from_cart")
                            : t("catalog_add_to_cart")}
                        </Button>
                      )}
                    </CardActions>
                  </Card>
                </Grid2>
              ))}
            </Grid2>
          )}
        </Box>
      )}
      {/* Pagination */}
      {totalItems > itemsPerPage && (
        <Box display="flex" justifyContent="center" mt={4} mb={3}>
          <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
            <Stack spacing={2} alignItems="center">
              <Typography variant="body2" color="text.secondary">
                {t("showing_items", { 
                  start: ((currentPage - 1) * itemsPerPage) + 1,
                  end: Math.min(currentPage * itemsPerPage, totalItems),
                  total: totalItems 
                })}
              </Typography>
              <Pagination
                count={Math.ceil(totalItems / itemsPerPage)}
                page={currentPage}
                onChange={handlePageChange}
                color="primary"
                size="large"
                showFirstButton
                showLastButton
              />
            </Stack>
          </Paper>
        </Box>
      )}
      <Dialog
        open={addDialogOpen}
        onClose={handleCloseAddDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{t("catalog_new_item")}</DialogTitle>
        <DialogContent>
          <TextField
            label={t("catalog_item_name")}
            name="name"
            value={newItem.name}
            onChange={handleNewItemChange}
            fullWidth
            sx={{ mb: 2 }}
            required
            error={!!addFieldErrors.name}
            helperText={addFieldErrors.name}
          />
          <FormControl
            fullWidth
            sx={{ mb: 2 }}
            required
            error={!!addFieldErrors.category}
          >
            <InputLabel>{t("catalog_category")}</InputLabel>
            <Select
              name="category"
              value={newItem.category}
              label={t("catalog_category")}
              onChange={handleNewItemChange}
              required
            >
              {categories.map((cat) => (
                <MenuItem key={cat} value={cat}>
                  {cat}
                </MenuItem>
              ))}
            </Select>
            {addFieldErrors.category && (
              <Typography color="error" variant="caption">
                {addFieldErrors.category}
              </Typography>
            )}
          </FormControl>
          <TextField
            label={t("catalog_item_price")}
            name="price"
            type="number"
            value={newItem.price}
            onChange={handleNewItemChange}
            fullWidth
            sx={{ mb: 2 }}
            required
            error={!!addFieldErrors.price}
            helperText={addFieldErrors.price}
          />
          <TextField
            label={t("catalog_item_amount")}
            name="amount"
            type="number"
            value={newItem.amount}
            onChange={handleNewItemChange}
            fullWidth
            sx={{ mb: 2 }}
            required
            error={!!addFieldErrors.amount}
            helperText={addFieldErrors.amount}
          />
          <TextField
            label={t("catalog_item_total_amount")}
            name="total_amount"
            type="number"
            value={newItem.total_amount ?? newItem.amount}
            onChange={handleNewItemChange}
            fullWidth
            sx={{ mb: 2 }}
            required
          />
          <TextField
            label={t("catalog_item_notes")}
            name="notes"
            value={newItem.notes}
            onChange={handleNewItemChange}
            fullWidth
            sx={{ mb: 2 }}
            multiline
            minRows={2}
          />
          <TextField
            label={t("catalog_item_description")}
            name="description"
            value={newItem.description}
            onChange={handleNewItemChange}
            fullWidth
            sx={{ mb: 2 }}
            multiline
            minRows={2}
          />
          <Box
            {...getRootProps()}
            sx={{
              border: "2px dashed",
              borderColor: addFieldErrors.image ? "error.main" : "primary.main",
              borderRadius: 2,
              p: 2,
              textAlign: "center",
              color: "text.secondary",
              mb: 2,
              cursor: "pointer",
              backgroundColor: isDragActive
                ? "action.hover"
                : "background.default",
            }}
          >
            <input {...getInputProps()} />
            {!imageFile ? (
              <Typography variant="body2">{t("catalog_item_image")}</Typography>
            ) : (
              <Typography variant="body2" color="text.primary">
                {t("catalog_item_image_selected")} {imageFile.name}
              </Typography>
            )}
            {addFieldErrors.image && (
              <Typography color="error" variant="caption">
                {addFieldErrors.image}
              </Typography>
            )}
          </Box>
          {addError && (
            <Typography color="error" variant="body2" sx={{ mb: 2 }}>
              {t("catalog_add_error")}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAddDialog}>
            {t("catalog_item_cancel")}
          </Button>
          <Button onClick={handleAddItem} variant="contained">
            {t("catalog_item_save")}
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={editDialogOpen}
        onClose={handleCloseEditDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{t("catalog_item_edit")}</DialogTitle>
        <DialogContent>
          {editItem && (
            <>
              <TextField
                label={t("catalog_item_name")}
                name="name"
                value={editItem.name}
                onChange={handleEditItemChange}
                fullWidth
                sx={{ mb: 2 }}
                required
              />
              <FormControl fullWidth sx={{ mb: 2 }} required>
                <InputLabel>{t("catalog_category")}</InputLabel>
                <Select
                  name="category"
                  value={editItem.category}
                  label={t("catalog_category")}
                  onChange={handleEditItemChange}
                  required
                >
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label={t("catalog_item_price")}
                name="price"
                type="number"
                value={editItem.price}
                onChange={handleEditItemChange}
                fullWidth
                sx={{ mb: 2 }}
                required
              />
              <TextField
                label={t("catalog_item_amount")}
                name="amount"
                type="number"
                value={editItem.amount}
                onChange={handleEditItemChange}
                fullWidth
                sx={{ mb: 2 }}
                required
              />
              <TextField
                label={t("catalog_item_total_amount")}
                name="total_amount"
                type="number"
                value={editItem.total_amount ?? editItem.amount}
                onChange={handleEditItemChange}
                fullWidth
                sx={{ mb: 2 }}
                required
              />
              <TextField
                label={t("catalog_item_notes")}
                name="notes"
                value={editItem.notes}
                onChange={handleEditItemChange}
                fullWidth
                sx={{ mb: 2 }}
                multiline
                minRows={2}
              />
              <TextField
                label={t("catalog_item_description")}
                name="description"
                value={editItem.description}
                onChange={handleEditItemChange}
                fullWidth
                sx={{ mb: 2 }}
                multiline
                minRows={2}
              />
              <FormControlLabel
                control={
                  <Checkbox
                    name="hidden"
                    checked={editItem.hidden}
                    onChange={handleEditItemChange}
                  />
                }
                label={t("catalog_item_hidden")}
                sx={{ mb: 2 }}
              />
              <Box
                {...getEditRootProps()}
                sx={{
                  border: "2px dashed",
                  borderColor: "primary.main",
                  borderRadius: 2,
                  p: 2,
                  textAlign: "center",
                  color: "text.secondary",
                  mb: 2,
                  cursor: "pointer",
                  backgroundColor: isEditDragActive
                    ? "action.hover"
                    : "background.default",
                }}
              >
                <input {...getEditInputProps()} />
                {!editImageFile ? (
                  <Typography variant="body2">
                    גרור/י תמונה לכאן או לחץ/י לבחירה (JPG/PNG, עד 5MB)
                  </Typography>
                ) : (
                  <Typography variant="body2" color="text.primary">
                    קובץ נבחר: {editImageFile.name}
                  </Typography>
                )}
              </Box>
              {editError && (
                <Typography color="error" variant="body2" sx={{ mb: 2 }}>
                  {editError}
                </Typography>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>
            {t("catalog_item_cancel")}
          </Button>
          <Button onClick={handleEditItem} variant="contained">
            {t("catalog_item_save")}
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>{t("catalog_item_delete")}</DialogTitle>
        <DialogContent>
          <Typography>
            {t("catalog_item_delete_confirm", { name: itemToDelete?.name })}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>
            {t("catalog_item_delete_cancel")}
          </Button>
          <Button onClick={handleDeleteItem} color="error" variant="contained">
            {t("catalog_item_delete_confirm_btn")}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Catalog;
