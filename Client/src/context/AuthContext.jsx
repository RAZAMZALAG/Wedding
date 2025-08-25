import { createContext, useContext, useState } from "react";
import { ACCESS_TOKEN, PERMISSION, USER_NAME } from "../constants.js";

const AuthContext = createContext({
  isLoggedIn: false,
  permission: 0,
  userName: "",
  login: (permission, userName) => {},
  logout: () => {},
});

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem(ACCESS_TOKEN),
  );
  const [permission, setPermission] = useState(
    localStorage.getItem(PERMISSION) || 0,
  );
  const [userName, setUserName] = useState(
    localStorage.getItem(USER_NAME) || "",
  );

  const login = (permission, userName) => {
    setIsLoggedIn(true);
    setPermission(permission);
    setUserName(userName);
    localStorage.setItem(PERMISSION, permission);
    localStorage.setItem("user_name", userName);
  };

  const logout = () => {
    localStorage.clear();
    setIsLoggedIn(false);
    setPermission(0);
    setUserName("");
  };

  return (
    <AuthContext.Provider
      value={{ isLoggedIn, permission, userName, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};
