import { useState } from "react";
import DashboardNewLayout from "./pages/Dashboard.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import SignupPage from "./pages/SignupPage.tsx";

export default function App() {
  const [currentPage, setCurrentPage] = useState<"login" | "signup" | "dashboard">("login");

  if (currentPage === "dashboard") {
    return <DashboardNewLayout />;
  }
  if (currentPage === "signup") {
    return <SignupPage onNavigate={setCurrentPage} />;
  }
  return <LoginPage onNavigate={setCurrentPage} />;
}