import { Navigate, Route, Routes } from 'react-router-dom';
import PrivateRoute from './components/PrivateRoute';
import PublicRoute from './components/PublicRoute';
import Consultation from './pages/Consultation';
import DashboardHome from './pages/DashboardHome';
import DashboardLayout from './pages/DashboardLayout';
import DiseasePredictionPage from './pages/DiseasePredictionPage';
import HealthReportAnalyzer from './pages/HealthReportAnalyzer';
import HeartHealthModule from './pages/HeartHealthModule';
import Login from './pages/Login';
import Prescription from './pages/Prescription';
import Signup from './pages/Signup';
import { useAuth } from './context/AuthContext';

export default function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
      />

      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
      </Route>

      <Route element={<PrivateRoute />}>
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<DashboardHome />} />
          <Route path="disease" element={<DiseasePredictionPage />} />
          <Route path="consultation" element={<Consultation />} />
          <Route path="prescription" element={<Prescription />} />
          <Route path="health-analyzer" element={<HealthReportAnalyzer />} />
          <Route path="heart-health" element={<HeartHealthModule />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
