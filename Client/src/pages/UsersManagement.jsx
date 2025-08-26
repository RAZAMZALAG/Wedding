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
  Button,
  TextField,
  MenuItem,
  Menu,
  Tab,
  Tabs,
  DialogTitle,
  DialogContent,
  DialogActions,
  Dialog,
  Select,
  FormControl,
  InputLabel,
} from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import SortIcon from "@mui/icons-material/Sort";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import PersonOffIcon from "@mui/icons-material/PersonOff";
import EventNoteIcon from "@mui/icons-material/EventNote";
import api from "../api.js";
import {
  DEFAULT_PAGE_SIZE,
  EP_USER_ID_FILE,
  EP_BOOKING_START_DATE,
  EP_USERS,
  EP_USERS_UPDATE,
  EP_USERS_BLOCK,
  EP_USERS_UNBLOCK,
  EP_USERS_DELETE,
  EP_USERS_DELETE_NON_ADMINS,
} from "../constants.js";
import { useNavigate } from "react-router-dom";
import { useShared } from "../context/SharedContext.jsx";
import { HttpStatusCode } from "axios";
import DatePicker from "react-datepicker";
import { set } from "react-hook-form";
import { useTranslation } from "react-i18next";

const tableHeadings = [
  { title: "users_management_name", name: "name" },
  { title: "users_management_email", name: "email" },
  { title: "users_management_bookings", name: "bookings" },
  { title: "users_management_phone", name: "phone_number" },
  { title: "users_management_location", name: "location" },
  { title: "users_management_permission", name: "permission" },
  { title: "users_management_id_file", name: "id_file" },
  { title: "מחיקה", name: "delete" }, // עמודת מחיקה חדשה
];

const UsersManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoadings, setActionLoadings] = useState(() =>
    Array(DEFAULT_PAGE_SIZE).fill(false),
  );
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [totalUsers, setTotalUsers] = useState(0);
  const [perPage, setPerPage] = useState(DEFAULT_PAGE_SIZE);
  const [direction, setDirection] = useState("asc");
  const [orderBy, setOrderBy] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [idFile, setIdFile] = useState(null);
  const [idDialogOpen, setIdDialogOpen] = useState(false);
  const { setErrorMessage } = useShared();
  const navigate = useNavigate();
  const [editingUserId, setEditingUserId] = useState(null);
  const [editedUserData, setEditedUserData] = useState({});
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [userToToggleBlock, setUserToToggleBlock] = useState({});
  const { t } = useTranslation();

  const startEditing = (user) => {
    setEditingUserId(user.id);
    setEditedUserData({ ...user }); // Pre-fill with existing data
  };

  const cancelEditing = () => {
    setEditingUserId(null);
    setEditedUserData({});
  };

  const handleFieldChange = (field, value) => {
    setEditedUserData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const abortControllerRef = useRef(null);

  const saveUserChanges = async () => {
    if (!editedUserData.first_name || !editedUserData.email) {
      setErrorMessage('יש למלא לפחות שם פרטי ודוא"ל');
      return;
    }

    const updatedFields = {
      first_name: editedUserData.first_name,
      last_name: editedUserData.last_name || "",
      email: editedUserData.email,
      phone_number: editedUserData.phone_number || "",
      location: editedUserData.location || "",
      permission: editedUserData.permission,
    };

    setLoading(true);
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await api.put(
        EP_USERS_UPDATE + editingUserId,
        updatedFields,
        { signal: controller.signal },
      );

      if (response.status === 200) {
        setUsers((prevUsers) =>
          prevUsers.map((user) =>
            user.id === editingUserId ? { ...user, ...updatedFields } : user,
          ),
        );
        cancelEditing();
      } else {
        setErrorMessage("עדכון המשתמש נכשל");
      }
    } catch (err) {
      if (err.name === "CanceledError") return;

      if (err.response?.data?.detail) {
        setErrorMessage(err.response.data.detail);
      } else {
        setErrorMessage("אירעה שגיאה בעדכון המשתמש");
      }
    } finally {
      setLoading(false);
    }
  };

  // פונקציה למחיקת כל המשתמשים חוץ מאדמינים
  const deleteAllNonAdminUsers = async () => {
    if (!window.confirm("האם אתה בטוח שברצונך למחוק את כל המשתמשים חוץ מאדמינים? פעולה זו בלתי הפיכה!")) {
      return;
    }

    try {
      setLoading(true);
      const response = await api.delete(EP_USERS_DELETE_NON_ADMINS);
      
      if (response.status === 200) {
        alert(`נמחקו ${response.data.deleted_count} משתמשים בהצלחה`);
        fetchUsers(); // רענון הטבלה
      }
    } catch (error) {
      if (error.response && error.response.data) {
        setErrorMessage(error.response.data.error);
      } else {
        setErrorMessage("אירעה שגיאה במחיקת המשתמשים");
      }
    } finally {
      setLoading(false);
    }
  };

  // פונקציה למחיקת משתמש בודד
  const deleteUser = async (userId) => {
    if (!window.confirm("האם אתה בטוח שברצונך למחוק משתמש זה? פעולה זו בלתי הפיכה!")) {
      return;
    }

    try {
      setLoading(true);
      const response = await api.delete(`${EP_USERS_DELETE}${userId}`);
      
      if (response.status === 200) {
        alert("המשתמש נמחק בהצלחה");
        fetchUsers(); // רענון הטבלה
      }
    } catch (error) {
      if (error.response && error.response.data) {
        setErrorMessage(error.response.data.error);
      } else {
        setErrorMessage("אירעה שגיאה במחיקת המשתמש");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      setLoading(true);
      const response = await api.get(EP_USERS, {
        params: {
          page: currentPage,
          per_page: perPage,
          order_by: orderBy,
          direction: direction,
          blocked: selectedTab,
        },
        signal: controller.signal,
      });

      if (!controller.signal.aborted && response.status === HttpStatusCode.Ok) {
        setUsers(response.data.users);
        setTotalUsers(response.data.meta.total_users);
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

  const handleIdDialogOpen = async (user) => {
    setSelectedUser(user);
    try {
      setLoading(true);
      const response = await api.get(`${EP_USER_ID_FILE}/${user.id}`);
      if (response.status === 200) {
        setIdFile(response.data.id_file);
        setIdDialogOpen(true);
      }
    } catch (error) {
      setErrorMessage("לא ניתן להציג את תעודת הזהות");
    } finally {
      setLoading(false);
    }
  };

  const handleIdDialogClose = () => {
    setSelectedUser(null);
    setIdFile(null);
    setIdDialogOpen(false);
  };

  const setActionLoading = (loading, index) => {
    setActionLoadings((prevStates) =>
      prevStates.map((actionLoading, i) =>
        i === index ? loading : actionLoading,
      ),
    );
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
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
    fetchUsers();
  }, [currentPage, perPage, orderBy, direction, selectedTab]);

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
        {t("users_management_title")}
      </Typography>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          aria-label="Users Tabs"
          variant="fullWidth"
          indicatorColor="secondary"
          textColor="inherit"
        >
          <Tab icon={<PeopleAltIcon />} label={t("users_management_active")} />
          <Tab icon={<PersonOffIcon />} label={t("users_management_blocked")} />
        </Tabs>
      </Box>

      {/* כפתור למחיקת כל המשתמשים חוץ מאדמינים */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 2 }}>
        <Button
          variant="contained"
          color="error"
          onClick={deleteAllNonAdminUsers}
          disabled={loading}
          sx={{ 
            backgroundColor: '#d32f2f',
            '&:hover': {
              backgroundColor: '#b71c1c'
            }
          }}
        >
          מחק את כל המשתמשים (חוץ מאדמינים)
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
                  <MenuItem onClick={() => handleSortSelect(null)}>
                    {t("users_management_clear_sort")}
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
            {users.map((user) => {
              const isEditing = editingUserId === user.id;
              const userFullName = `${user.first_name} ${user.last_name}`;
              return (
                <TableRow
                  key={user.id}
                  sx={{
                    backgroundColor:
                      editingUserId === user.id ? "#e3f2fd" : "inherit",
                  }}
                >
                  <TableCell>
                    {isEditing ? (
                      <Box sx={{ display: "flex", gap: 1 }}>
                        <TextField
                          label={t("users_management_name")}
                          value={editedUserData.first_name || ""}
                          onChange={(e) =>
                            handleFieldChange("first_name", e.target.value)
                          }
                          variant="standard"
                          size="small"
                        />
                        <TextField
                          label={t("users_management_name")}
                          value={editedUserData.last_name || ""}
                          onChange={(e) =>
                            handleFieldChange("last_name", e.target.value)
                          }
                          variant="standard"
                          size="small"
                        />
                      </Box>
                    ) : (
                      userFullName
                    )}
                  </TableCell>
                  <TableCell>
                    {isEditing ? (
                      <TextField
                        value={editedUserData.email || ""}
                        onChange={(e) =>
                          handleFieldChange("email", e.target.value)
                        }
                        variant="standard"
                        size="small"
                      />
                    ) : (
                      user.email
                    )}
                  </TableCell>
                  <TableCell>
                    <Button
                      onClick={() =>
                        navigate(
                          `/bookings?email=${encodeURIComponent(user.email)}`,
                        )
                      }
                    >
                      {t("users_management_view")}
                    </Button>
                  </TableCell>
                  <TableCell>
                    {isEditing ? (
                      <TextField
                        value={editedUserData.phone_number || ""}
                        onChange={(e) =>
                          handleFieldChange("phone_number", e.target.value)
                        }
                        variant="standard"
                        size="small"
                      />
                    ) : (
                      user.phone_number
                    )}
                  </TableCell>
                  <TableCell>
                    {editingUserId === user.id ? (
                      <FormControl fullWidth size="small">
                        <InputLabel>
                          {t("users_management_location")}
                        </InputLabel>
                        <Select
                          value={editedUserData.location}
                          label={t("users_management_location")}
                          onChange={(e) =>
                            setEditedUserData((prev) => ({
                              ...prev,
                              location: e.target.value,
                            }))
                          }
                        >
                          <MenuItem value="הדר">הדר</MenuItem>
                          <MenuItem value="מחיפה, לא מהדר">
                            מחיפה, לא מהדר
                          </MenuItem>
                          <MenuItem value="לא מחיפה">לא מחיפה</MenuItem>
                        </Select>
                      </FormControl>
                    ) : (
                      user.location
                    )}
                  </TableCell>
                  <TableCell>
                    {isEditing ? (
                      <FormControl fullWidth size="small">
                        <InputLabel>
                          {t("users_management_permission")}
                        </InputLabel>
                        <Select
                          value={editedUserData.permission ?? 1}
                          label={t("users_management_permission")}
                          onChange={(e) =>
                            handleFieldChange(
                              "permission",
                              Number(e.target.value),
                            )
                          }
                          disabled={user.permission === 3} // Disable for admin
                        >
                          <MenuItem value={1}>
                            {t("users_management_permission_user")}
                          </MenuItem>
                          <MenuItem value={2}>
                            {t("users_management_permission_staff")}
                          </MenuItem>
                        </Select>
                      </FormControl>
                    ) : user.permission === 2 ? (
                      t("users_management_permission_staff")
                    ) : user.permission === 3 ? (
                      t("users_management_permission_admin")
                    ) : (
                      t("users_management_permission_user")
                    )}
                  </TableCell>
                  <TableCell>
                    <Button
                      onClick={() => handleIdDialogOpen(user)}
                      disabled={user.permission === 3} // Disable for admin
                    >
                      {t("users_management_show_id")}
                    </Button>
                  </TableCell>
                  <TableCell>
                    {isEditing ? (
                      <>
                        <Button
                          onClick={saveUserChanges}
                          color="success"
                          disabled={user.permission === 3}
                        >
                          {t("users_management_save")}
                        </Button>
                        <Button onClick={cancelEditing} color="secondary">
                          {t("users_management_cancel")}
                        </Button>
                      </>
                    ) : (
                      <Button
                        onClick={() => startEditing(user)}
                        disabled={user.permission === 3}
                      >
                        {t("users_management_edit")}
                      </Button>
                    )}
                  </TableCell>
                  <TableCell>
                    <Button
                      onClick={() => deleteUser(user.id)}
                      color="error"
                      disabled={user.permission === 3 || loading} // מניעת מחיקת אדמין
                      variant="outlined"
                      size="small"
                    >
                      מחק
                    </Button>
                  </TableCell>
                  <TableCell>
                    <Button
                      onClick={() => {
                        setUserToToggleBlock(user);
                        setConfirmDialogOpen(true);
                      }}
                      color={user.blocked ? "warning" : "error"}
                      disabled={user.permission === 3} // Disable for admin
                    >
                      {user.blocked
                        ? t("users_management_unblock")
                        : t("users_management_block")}
                    </Button>
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
                count={totalUsers}
                rowsPerPage={perPage}
                page={currentPage - 1}
                onPageChange={handlePageChange}
                onRowsPerPageChange={handleRowsPerPageChange}
                labelDisplayedRows={({ from, to, count }) =>
                  t("users_management_displayed_rows", {
                    from,
                    to,
                    count,
                    page: currentPage,
                    totalPages,
                  })
                }
                labelRowsPerPage={t("users_management_rows_per_page")}
              />
            </TableRow>
          </TableFooter>
        </Table>
      </TableContainer>

      {/* Dialog for displaying ID file */}
      <Dialog
        open={idDialogOpen}
        onClose={handleIdDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {selectedUser &&
            t("users_management_id_title", {
              name: `${selectedUser.first_name} ${selectedUser.last_name}`,
            })}
        </DialogTitle>
        <DialogContent>
          {idFile ? (
            <img
              src={`data:image/jpeg;base64,${idFile}`}
              alt="ID File"
              style={{ width: "100%", height: "auto" }}
            />
          ) : (
            <Typography align="center">
              {t("users_management_id_loading")}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleIdDialogClose}>
            {t("users_management_cancel")}
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
      >
        <DialogTitle>
          {userToToggleBlock?.blocked
            ? t("users_management_block_dialog_unblock")
            : t("users_management_block_dialog_block")}
        </DialogTitle>
        <DialogContent>
          <Typography>
            {userToToggleBlock?.blocked
              ? t("users_management_block_dialog_unblock_confirm", {
                  name: `${userToToggleBlock.first_name} ${userToToggleBlock.last_name}`,
                })
              : t("users_management_block_dialog_block_confirm", {
                  name: `${userToToggleBlock.first_name} ${userToToggleBlock.last_name}`,
                })}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>
            {t("users_management_cancel")}
          </Button>
          <Button
            onClick={async () => {
              try {
                const isCurrentlyBlocked = userToToggleBlock.blocked;
                const endpoint = isCurrentlyBlocked 
                  ? `${EP_USERS_UNBLOCK}${userToToggleBlock.id}/unblock`
                  : `${EP_USERS_BLOCK}${userToToggleBlock.id}/block`;
                
                const response = await api.post(endpoint);
                
                if (response.status === 200) {
                  setUsers((prev) =>
                    prev.map((u) =>
                      u.id === userToToggleBlock.id
                        ? { ...u, blocked: !u.blocked }
                        : u,
                    ),
                  );
                }
              } catch {
                setErrorMessage("שגיאה בעדכון חסימת המשתמש");
              } finally {
                setConfirmDialogOpen(false);
              }
            }}
            color={userToToggleBlock?.blocked ? "warning" : "error"}
          >
            {userToToggleBlock?.blocked
              ? t("users_management_unblock")
              : t("users_management_block")}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default UsersManagement;
