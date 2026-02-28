import { Routes, Route, Navigate } from "react-router-dom";
import DashboardNewLayout from "./pages/Dashboard.tsx";
import LoginPage from "./pages/auth/LoginPage.tsx";
import SignupPage from "./pages/auth/SignupPage.tsx";
import AccountProfile from "./pages/accounts/AccountProfile.tsx";
import StrategicInsightsPage from "./pages/accounts/StrategicInsights.tsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/daily" replace />} />
      <Route path="/daily" element={<DashboardNewLayout />} />
      <Route path="/account-360" element={<AccountProfile />} />
      <Route path="/insights" element={<StrategicInsightsPage />} />  



    </Routes>
  );
}