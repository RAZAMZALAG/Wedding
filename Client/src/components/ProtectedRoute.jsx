import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

function ProtectedRoute({ children, accessPermission }) {
  const { isLoggedIn, permission } = useAuth();
  if (!isLoggedIn) {
    return <Navigate to={"/login"} />;
  }
  return permission >= accessPermission ? children : <Navigate to={"/"} />;
}

export default ProtectedRoute;
