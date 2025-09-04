import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import Layout from "./Layout.jsx";
import About from "./pages/About.jsx";
import QuestionsAndAnswers from "./pages/QuestionsAndAnswers.jsx";
import Catalog from "./pages/Catalog.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { SharedProvider, useShared } from "./context/SharedContext.jsx";
import Loading from "./components/Loading.jsx";
import ErrorDialog from "./components/ErrorDialog.jsx";
import ActionMessage from "./components/ActionMessage.jsx";
import ItemDetails from "./pages/ItemDetails.jsx";
import PersonalBookings from "./pages/PersonalBookings.jsx";
import AllBookings from "./pages/AllBookings.jsx";
import UsersManagement from "./pages/UsersManagement.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import UnauthenticatedRoute from "./components/UnauthenticatedRoute.jsx";
import Cart from "./pages/Cart.jsx";
import OkDialog from "./components/OkDialog";

function App() {
  return (
    <>
      <AuthProvider>
        <SharedProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </SharedProvider>
      </AuthProvider>
    </>
  );
}

function AppRoutes() {
  const { isLoading, message } = useShared();

  return (
    <>
      {isLoading && <Loading open={isLoading} />}
      <ErrorDialog />
      <OkDialog />
      {message && <ActionMessage />}
      <Layout>
        <Routes>
          <Route path={"/"} element={<Home />} />
          <Route
            path={"/login"}
            element={
              <UnauthenticatedRoute>
                <Login />
              </UnauthenticatedRoute>
            }
          />
          <Route
            path={"/register"}
            element={
              <UnauthenticatedRoute>
                <Register />
              </UnauthenticatedRoute>
            }
          />
          <Route path={"/catalog"} element={<Catalog />} />
          <Route path={"/qna"} element={<QuestionsAndAnswers />} />
          <Route path={"/about"} element={<About />} />
          <Route path={"/item/:id"} element={<ItemDetails />} />
          <Route
            path={"/cart"}
            element={
              <ProtectedRoute accessPermission={1}>
                <Cart />
              </ProtectedRoute>
            }
          />
          <Route
            path={"/bookings"}
            element={
              <ProtectedRoute accessPermission={2}>
                <AllBookings />
              </ProtectedRoute>
            }
          />
          <Route
            path={"/users"}
            element={
              <ProtectedRoute accessPermission={3}>
                <UsersManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path={"/bookings/personal"}
            element={
              <ProtectedRoute accessPermission={1}>
                <PersonalBookings />
              </ProtectedRoute>
            }
          />
          <Route path={"*"} element={<NotFound />} />
        </Routes>
      </Layout>
    </>
  );
}

export default App;
