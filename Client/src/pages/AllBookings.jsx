import React, { useState, useEffect, useRef } from "react";
import {
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Box,
  Button,
  Typography,
  Paper,
  TablePagination,
  TableFooter,
  LinearProgress,
  IconButton,
  TextField,
  MenuItem,
  Menu,
  Select,
  FormControl,
  InputLabel,
  Tab,
  Tabs,
} from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import SortIcon from "@mui/icons-material/Sort";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import EventNoteIcon from "@mui/icons-material/EventNote";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import DeleteIcon from "@mui/icons-material/Delete";
import { useAuth } from "../context/AuthContext.jsx";
import api from "../api.js";
import {
  DEFAULT_PAGE_SIZE,
  EP_BOOKING_APPROVE,
  EP_BOOKING_COLLECT,
  EP_BOOKING_RETURN,
  EP_BOOKING_REJECT,
  EP_BOOKINGS,
  getStatusInfo,
  EP_BOOKING_PENDING,
  EP_BOOKING_END_DATE,
  EP_BOOKING_START_DATE,
} from "../constants.js";
import { useNavigate, useLocation } from "react-router-dom";
import { useShared } from "../context/SharedContext.jsx";
import { HttpStatusCode } from "axios";
import DatePicker from "react-datepicker";
import { useTranslation } from "react-i18next";

const tableHeadings = [
  { title: "all_bookings_user", name: "user_name" },
  { title: "all_bookings_items", name: "items" },
  { title: "all_bookings_total_price", name: "total_price" },
  { title: "all_bookings_status", name: "status" },
  { title: "all_bookings_start_date", name: "start_date" },
  { title: "all_bookings_end_date", name: "end_date" },
  { title: "all_bookings_actions", name: "actions" },
];

const typeMapping = {
  0: "all",        // Show all bookings
  1: "PENDING",    // Pending bookings
  2: "APPROVED",   // Approved bookings
  3: "COLLECTED",  // Collected by customer
  4: "RETURNED",   // Returned and completed
};

const AllBookings = () => {
  const { currentUser } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoadings, setActionLoadings] = useState(() =>
    Array(DEFAULT_PAGE_SIZE).fill(false),
  );
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [totalBookings, setTotalBookings] = useState(0);
  const [perPage, setPerPage] = useState(DEFAULT_PAGE_SIZE);
  const [direction, setDirection] = useState("asc");
  const [orderBy, setOrderBy] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [filterName, setFilterName] = useState("");
  const [filterEmail, setFilterEmail] = useState("");
  const { setErrorMessage } = useShared();
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useTranslation();

  const abortControllerRef = useRef(null);

  const fetchBookings = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setLoading(true);
      const response = await api.get(EP_BOOKINGS, {
        params: {
          page: currentPage,
          per_page: perPage,
          order_by: orderBy,
          direction: direction,
          type: typeMapping[selectedTab],
          filter_by_name: filterName,
          filter_by_email: filterEmail,
        },
        signal: controller.signal,
      });

      if (!controller.signal.aborted && response.status === HttpStatusCode.Ok) {
        setBookings(response.data.bookings);
        setTotalBookings(response.data.meta.total_bookings);
        setTotalPages(response.data.meta.total_pages);
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        if (error.status === HttpStatusCode.Unauthorized) {
          setErrorMessage("אנא התחבר מחדש למערכת");
        } else {
          setErrorMessage();
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const setActionLoading = (loading, index) => {
    setActionLoadings((prevStates) =>
      prevStates.map((actionLoading, i) =>
        i === index ? loading : actionLoading,
      ),
    );
  };

  const setBookingStatus = async (status, bookingIndex) => {
    try {
      setLoading(true);
      setActionLoading(true, bookingIndex);
      
      // Use the correct endpoint format: /bookings/<booking_id>/status/<status>
      const bookingId = bookings[bookingIndex]._id || bookings[bookingIndex].id;
      const url = `${EP_BOOKINGS}${bookingId}/status/${status}`;
      
      console.log(`Updating booking ${bookingId} to status ${status}`);
      
      const response = await api.put(url);

      if (response.status === 200) {
        setBookings((prevState) =>
          prevState.map((booking, i) => {
            if (i === bookingIndex) {
              booking.status = status;
            }
            return booking;
          }),
        );
      }
    } catch (error) {
      console.error("Error updating booking status:", error);
    } finally {
      setActionLoading(false, bookingIndex);
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue); // Update the tab when the user selects a new one
  };

  const handlePageChange = (event, value) => {
    setCurrentPage(value + 1);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && direction === "asc";
    setDirection(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleRowsPerPageChange = (event) => {
    setPerPage(parseInt(event.target.value, 10));
    setCurrentPage(1);
  };

  const updateStartDate = async (date, bookingIndex) => {
    const bookingId = bookings[bookingIndex].cart_id;
    try {
      setLoading(true);
      const response = await api.patch(
        EP_BOOKING_START_DATE + `/${bookingId}`,
        {
          start_date: date.toISOString().split("T")[0], // Format the date as YYYY-MM-DD
        },
      );

      if (response.status === 200) {
        setBookings((prevState) =>
          prevState.map((booking, i) => {
            if (i === bookingIndex) {
              booking.start_date = date;
              booking.total_price = response.data.total_price;
            }
            return booking;
          }),
        );
      }
    } catch (error) {
      setErrorMessage("Failed to update start date");
    } finally {
      setLoading(false);
    }
  };

  const updateEndDate = async (date, bookingIndex) => {
    const bookingId = bookings[bookingIndex].cart_id;
    try {
      setLoading(true);
      const response = await api.patch(EP_BOOKING_END_DATE + `/${bookingId}`, {
        end_date: date.toISOString().split("T")[0], // Format the date as YYYY-MM-DD
      });

      if (response.status === 200) {
        setBookings((prevState) =>
          prevState.map((booking, i) => {
            if (i === bookingIndex) {
              booking.end_date = date;
              booking.total_price = response.data.total_price;
            }
            return booking;
          }),
        );
      }
    } catch (error) {
      setErrorMessage("Failed to update end date");
    } finally {
      setLoading(false);
    }
  };

  const deleteBooking = async (bookingIndex) => {
    const booking = bookings[bookingIndex];
    const bookingId = booking._id || booking.id;
    
    console.log("Starting delete for booking:", {
      bookingIndex,
      bookingId,
      booking,
      EP_BOOKINGS,
      currentUser: currentUser?.permission
    });
    
    // Show confirmation dialog
    const confirmed = window.confirm(
      `האם אתה בטוח שברצונך למחוק את ההזמנה של ${booking.user.first_name} ${booking.user.last_name}?`
    );
    
    if (!confirmed) return;

    try {
      setLoading(true);
      setActionLoading(true, bookingIndex);
      
      const deleteUrl = `${EP_BOOKINGS}${bookingId}`;
      console.log("Making DELETE request to:", deleteUrl);
      console.log("Full URL:", api.defaults.baseURL + deleteUrl);
      console.log("Has token:", !!localStorage.getItem('ACCESS_TOKEN'));
      
      // Delete the booking
      const response = await api.delete(deleteUrl);
      
      console.log("DELETE response:", {
        status: response.status,
        data: response.data
      });

      if (response.status === 200) {
        // Remove the booking from the state
        setBookings((prevState) => 
          prevState.filter((_, index) => index !== bookingIndex)
        );
        
        // Update total bookings count
        setTotalBookings(prev => prev - 1);
        
        // If we're on the last page and it becomes empty, go to previous page
        if (bookings.length === 1 && currentPage > 1) {
          setCurrentPage(currentPage - 1);
        }
      }
    } catch (error) {
      console.error("Error deleting booking:", error);
      console.error("Error name:", error.name);
      console.error("Error message:", error.message);
      console.error("Error config:", error.config);
      console.error("Error response:", error.response);
      console.error("Error response data:", error.response?.data);
      console.error("Error status:", error.response?.status);
      console.error("Error request:", error.request);
      
      if (error.response?.status === 404) {
        setErrorMessage("ההזמנה לא נמצאה");
      } else if (error.response?.status === 403) {
        setErrorMessage("אין הרשאה למחוק הזמנה זו");
      } else {
        setErrorMessage(`שגיאה במחיקת ההזמנה: ${error.response?.data?.error || error.message}`);
      }
    } finally {
      setActionLoading(false, bookingIndex);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, [
    currentPage,
    perPage,
    orderBy,
    direction,
    selectedTab,
    filterName,
    filterEmail,
  ]);

  // Read email from query param on mount
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const email = params.get("email") || "";
    if (email) setFilterEmail(email);
  }, [location.search]);

  const handleSortMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleSortMenuClose = () => {
    setAnchorEl(null);
  };

  const handleSortSelect = (value) => {
    setOrderBy(value);
    handleSortMenuClose();
  };

  const handleFilterNameChange = (e) => {
    setFilterName(e.target.value);

    // Remove 'email' from the URL if it exists
    const params = new URLSearchParams(location.search);
    if (params.has("email")) {
      params.delete("email");
      navigate(
        {
          pathname: location.pathname,
          search: params.toString() ? `?${params.toString()}` : "",
        },
        { replace: true },
      );
    }
  };

  const handleFilterEmailChange = (e) => {
    setFilterEmail(e.target.value);

    // Remove 'email' from the URL if it exists
    const params = new URLSearchParams(location.search);
    if (params.has("email")) {
      params.delete("email");
      navigate(
        {
          pathname: location.pathname,
          search: params.toString() ? `?${params.toString()}` : "",
        },
        { replace: true },
      );
    }
  };

  return (
    <Container
      sx={{ height: "100%", display: "flex", flexDirection: "column" }}
    >
      <Typography variant="h4" align="center" sx={{ marginBottom: 3 }}>
        {t("all_bookings_title")}
      </Typography>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          aria-label="Booking Status Tabs"
          variant="scrollable"
          scrollButtons="auto"
          indicatorColor="secondary"
          textColor="inherit"
        >
          <Tab icon={<EventNoteIcon />} label="כל ההזמנות" />
          <Tab icon={<AccessTimeIcon />} label="ממתין לאישור" />
          <Tab icon={<DoneAllIcon />} label="הזמנות מאושרות" />
          <Tab icon={<CheckCircleIcon />} label="נמסר ללקוח" />
          <Tab icon={<AssignmentTurnedInIcon />} label="הזמנות הושלמו" />
        </Tabs>
      </Box>

      {/* Filter Section */}
      <Box sx={{ mt: 1, display: "flex", gap: 2, mb: 2 }}>
        <TextField
          label={t("all_bookings_filter_name")}
          value={filterName}
          onChange={handleFilterNameChange}
          size="small"
          variant="outlined"
        />
        <TextField
          label={t("all_bookings_filter_email")}
          value={filterEmail}
          onChange={handleFilterEmailChange}
          size="small"
          variant="outlined"
        />
        <Button
          variant="contained"
          onClick={() => {
            setCurrentPage(1);
            fetchBookings();
          }}
        >
          {t("all_bookings_filter_search")}
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <LinearProgress
          sx={{
            "& .MuiLinearProgress-bar": {
              animation: loading ? "" : "none",
            },
          }}
        />
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <IconButton onClick={handleSortMenuOpen}>
                  <SortIcon />
                </IconButton>

                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleSortMenuClose}
                  anchorOrigin={{
                    vertical: "bottom",
                    horizontal: "left",
                  }}
                  transformOrigin={{
                    vertical: "top",
                    horizontal: "left",
                  }}
                >
                  <MenuItem onClick={() => handleSortSelect("late")}>
                    {t("all_bookings_late")}
                  </MenuItem>
                  <MenuItem onClick={() => handleSortSelect(null)}>
                    {t("all_bookings_clear_sort")}
                  </MenuItem>
                </Menu>
              </TableCell>
            </TableRow>
            <TableRow>
              {tableHeadings.map((heading, index) => (
                <TableCell
                  key={index}
                  sortDirection={orderBy === heading.name ? direction : false}
                >
                  <TableSortLabel
                    active={orderBy === heading.name}
                    direction={orderBy === heading.name ? direction : "asc"}
                    onClick={() => handleRequestSort(heading.name)}
                  >
                    {t(heading.title)}
                  </TableSortLabel>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {bookings.map((booking, index) => {
              const isLate =
                new Date() > new Date(booking.end_date) &&
                booking.status === "COLLECTED";

              return (
                <TableRow
                  key={index}
                  sx={{
                    backgroundColor: isLate
                      ? "rgba(255, 0, 0, 0.1)"
                      : "inherit", // Highlight late bookings with a light red background
                  }}
                >
                  {/* Display the user info for the first item */}
                  <TableCell>
                    {booking.user.first_name} {booking.user.last_name} (
                    {booking.user.email})
                  </TableCell>
                  {/* Display compact list of items */}
                  <TableCell>
                    {(booking.cart_items || []).map((cartItem, itemIndex) => (
                      <div key={itemIndex}>
                        <span>
                          <span
                            onClick={() => navigate(`/item/${cartItem.item.id}`)}
                            style={{ cursor: "pointer" }}
                          >
                            {t(`items.${cartItem.item.name}`, {
                              defaultValue: cartItem.item.name,
                            })}
                          </span>{" "}
                          (x{cartItem.amount}) {cartItem.item.price} ₪
                        </span>
                        {itemIndex < (booking.cart_items || []).length - 1 && <br />}
                      </div>
                    ))}
                  </TableCell>
                  {/* Total price */}
                  <TableCell>{booking.total_price} ₪</TableCell>
                  {/* Status dropdown */}
                  <TableCell>
                    <FormControl fullWidth>
                      <InputLabel>סטטוס</InputLabel>
                      <Select
                        value={booking.status}
                        onChange={(e) =>
                          setBookingStatus(e.target.value, index)
                        }
                        sx={{
                          color: getStatusInfo(booking.status).color, // Color for the selected status
                          fontWeight: "bold",
                        }}
                      >
                        {[
                          "PENDING",
                          "APPROVED",
                          "COLLECTED",
                          "RETURNED",
                          "REJECTED",
                        ].map((status) => {
                          const statusInfo = getStatusInfo(status); // Get color and label from getStatusInfo
                          return (
                            <MenuItem
                              key={status}
                              value={status}
                              sx={{
                                color: statusInfo.color, // Color for the status options
                                fontWeight: "bold",
                              }}
                            >
                              {getStatusInfo(status).label}
                            </MenuItem>
                          );
                        })}
                      </Select>
                    </FormControl>
                  </TableCell>
                  {/* Dates */}
                  <TableCell>
                    <DatePicker
                      portalId="root-portal"
                      selected={new Date(booking.start_date)}
                      onChange={(date) => updateStartDate(date, index)}
                      maxDate={new Date(booking.end_date)}
                      dateFormat="yyyy-MM-dd"
                      customInput={
                        <TextField
                          variant="standard"
                          size="small"
                          sx={{
                            width: "120px",
                            padding: "0 8px", // Adjust padding for the text input
                            fontSize: "0.875rem", // Adjust font size
                          }}
                        />
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <DatePicker
                      portalId="root-portal"
                      selected={new Date(booking.end_date)}
                      onChange={(date) => updateEndDate(date, index)}
                      minDate={new Date(booking.start_date)}
                      dateFormat="yyyy-MM-dd"
                      customInput={
                        <TextField
                          variant="standard"
                          size="small"
                          sx={{
                            width: "120px",
                            padding: "0 8px", // Adjust padding for the text input
                            fontSize: "0.875rem", // Adjust font size
                          }}
                        />
                      }
                    />
                  </TableCell>
                  {/* Actions column */}
                  <TableCell>
                    <IconButton
                      onClick={() => {
                        console.log("Delete button clicked for booking index:", index);
                        deleteBooking(index);
                      }}
                      disabled={actionLoadings[index]}
                      color="error"
                      size="small"
                      title="מחק הזמנה"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>

          <TableFooter>
            <TableRow>
              <TablePagination
                rowsPerPageOptions={[5, 10, 20]}
                colSpan={3}
                count={totalBookings}
                rowsPerPage={perPage}
                page={currentPage - 1}
                onPageChange={handlePageChange}
                onRowsPerPageChange={handleRowsPerPageChange}
                labelDisplayedRows={({ from, to, count }) =>
                  t("all_bookings_displayed_rows", {
                    from,
                    to,
                    count,
                    page: currentPage,
                    totalPages,
                  })
                }
                labelRowsPerPage={t("all_bookings_rows_per_page")}
              />
            </TableRow>
          </TableFooter>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default AllBookings;
