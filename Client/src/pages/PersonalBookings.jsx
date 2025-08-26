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
} from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import SortIcon from "@mui/icons-material/Sort";
import api from "../api.js";
import {
  DEFAULT_PAGE_SIZE,
  EP_PERSONAL_BOOKINGS,
  getStatusInfo,
} from "../constants.js";
import { useNavigate } from "react-router-dom";
import { useShared } from "../context/SharedContext.jsx";
import { HttpStatusCode } from "axios";
import { useTranslation } from "react-i18next";

const tableHeadings = [
  { title: "personal_bookings_items", name: "items" },
  { title: "personal_bookings_total_price", name: "total_price" },
  { title: "personal_bookings_status", name: "status" },
  { title: "personal_bookings_start_date", name: "start_date" },
  { title: "personal_bookings_end_date", name: "end_date" },
];

const PersonalBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalBookings, setTotalBookings] = useState(0);
  const [perPage, setPerPage] = useState(DEFAULT_PAGE_SIZE);
  const [direction, setDirection] = useState("asc");
  const [orderBy, setOrderBy] = useState(null);
  const [textFilterOn, setTextFilterOn] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const { setErrorMessage } = useShared();
  const navigate = useNavigate();
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
      const response = await api.get(EP_PERSONAL_BOOKINGS, {
        params: {
          page: currentPage,
          per_page: perPage,
          order_by: orderBy,
          direction: direction,
        },
        signal: controller.signal,
      });

      if (!controller.signal.aborted && response.status === HttpStatusCode.Ok) {
        const data = response.data || {};
        setBookings(data.bookings || []);
        setTotalBookings(data.total || 0);
        setTotalPages(data.total_pages || 0);
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

  useEffect(() => {
    fetchBookings();
  }, [currentPage, perPage, orderBy, direction]);

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

  return (
    <Container
      sx={{ height: "100%", display: "flex", flexDirection: "column" }}
    >
      <Typography variant="h4" align="center" sx={{ marginBottom: 3 }}>
        {t("personal_bookings_title")}
      </Typography>

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
                <IconButton onClick={() => setTextFilterOn(!textFilterOn)}>
                  <FilterListIcon />
                </IconButton>
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
                    {t("personal_bookings_late")}
                  </MenuItem>
                  <MenuItem onClick={() => handleSortSelect(null)}>
                    {t("personal_bookings_clear_sort")}
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
                  {textFilterOn && (
                    <TextField
                      variant="standard"
                      size="small"
                      sx={{ width: "100%" }}
                    />
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {(bookings || []).map((booking, index) => (
              <TableRow key={index}>
                {/* Display compact list of items */}
                <TableCell>
                  {(booking.cart_items || []).map((cartItem, itemIndex) => (
                    <div key={itemIndex}>
                      <span>
                        <span
                          onClick={() => navigate(`/item/${cartItem.item.id}`)}
                          style={{ cursor: "pointer" }}
                        >
                          {t(`items.${cartItem.item.name}`, { defaultValue: cartItem.item.name })}
                        </span>{" "}
                        (x{cartItem.amount}) {cartItem.item.price} ₪
                      </span>
                      {itemIndex < (booking.cart_items || []).length - 1 && <br />}
                    </div>
                  ))}
                </TableCell>
                {/* Total price */}
                <TableCell>{booking.total_price} ₪</TableCell>
                {/* Status */}
                <TableCell
                  sx={{
                    color: getStatusInfo(booking.status).color, // Color for the selected status
                    fontWeight: "bold",
                  }}
                >
                  {t(`booking_status_${booking.status}`)}
                </TableCell>
                {/* Start Date */}
                <TableCell>{booking.start_date}</TableCell>
                {/* End Date */}
                <TableCell>{booking.end_date}</TableCell>
              </TableRow>
            ))}
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
                  t("personal_bookings_displayed_rows", {
                    from,
                    to,
                    count,
                    page: currentPage,
                    totalPages,
                  })
                }
                labelRowsPerPage={t("personal_bookings_rows_per_page")}
              />
            </TableRow>
          </TableFooter>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default PersonalBookings;
