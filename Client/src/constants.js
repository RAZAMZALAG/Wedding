import { useTheme } from "@mui/material/styles";

export const ACCESS_TOKEN = "token";
export const PERMISSION = "permission";
export const REFRESH_TOKEN = "refresh";
export const USER_NAME = "user_name";
export const DEFAULT_PAGE_SIZE = 20;

const API = "/api";
const AUTH = API + "/auth";
export const EP_LOGIN = AUTH + "/login";
export const EP_REGISTER = AUTH + "/register";
export const EP_REFRESH = AUTH + "/refresh";
export const EP_ITEMS = API + "/items/";
export const EP_ITEM = API + "/items";
export const EP_ADD_ITEM = API + "/items/";
export const EP_EDIT_ITEM = API + "/items/";
export const EP_DELETE_ITEM = API + "/items/";
export const EP_BOOKINGS = API + "/bookings/";
export const EP_BOOKING_APPROVE = EP_BOOKINGS + "approve";
export const EP_BOOKING_REJECT = EP_BOOKINGS + "reject";
export const EP_BOOKING_COLLECT = EP_BOOKINGS + "collect";
export const EP_BOOKING_PENDING = EP_BOOKINGS + "pending";
export const EP_BOOKING_RETURN = EP_BOOKINGS + "return";
export const EP_BOOKING_START_DATE = EP_BOOKINGS + "start_date";
export const EP_BOOKING_END_DATE = EP_BOOKINGS + "end_date";
export const EP_BOOKING = EP_BOOKINGS;
export const EP_PERSONAL_BOOKINGS = EP_BOOKINGS + "personal";
export const EP_CART = EP_BOOKINGS + "cart";
export const EP_ADD_TO_CART = EP_BOOKINGS + "cart/add";
export const EP_REMOVE_FROM_CART = EP_BOOKINGS + "cart/remove";
export const EP_USERS = API + "/users/";
export const EP_USERS_UPDATE = EP_USERS + "update/";
export const EP_USERS_BLOCK = EP_USERS + "block/";
export const EP_USERS_DELETE = EP_USERS;
export const EP_USERS_DELETE_NON_ADMINS = EP_USERS + "delete-non-admins";
export const EP_USER_ID_FILE = API + "/users/id";
export const EP_CATEGORIES = API + "/items/categories";

export const getStatusInfo = (status) => {
  const theme = useTheme();
  switch (status) {
    case "PENDING":
      return { label: "ממתין לאישור", color: theme.palette.status.pending };
    case "APPROVED":
      return { label: "הזמנה מאושרת", color: theme.palette.status.approved };
    case "COLLECTED":
      return { label: "נמסר ללקוח", color: theme.palette.status.collected };
    case "RETURNED":
      return { label: "הזמנה הושלמה", color: theme.palette.status.returned };
    case "REJECTED":
      return { label: "הזמנה נדחתה", color: theme.palette.status.rejected };
    default:
      return { label: "לא מוגדר", color: theme.palette.status.undefined };
  }
};
