import { ACCESS_TOKEN, REFRESH_TOKEN } from "./src/constants.js";

export function isAuthenticated() {
  return (
    !!localStorage.getItem(ACCESS_TOKEN) &&
    !!localStorage.getItem(REFRESH_TOKEN)
  );
}
