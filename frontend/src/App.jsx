import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Import Navbar Aplikasi (Navbar yang dipakai saat sudah login)
import AppNavbar from './components/Navbar';

// Pages
import LandingPage from './pages/LandingPage'; // Gunakan file baru tadi
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import SearchPage from './pages/SearchPage';
import ProjectDetailPage from './pages/ProjectDetailPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* ROUTE PUBLIK (Landing Page punya Navbar sendiri di dalamnya) */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* ROUTE TERPROTEKSI (Dashboard, dll) */}
            {/* Kita bungkus dengan Layout sederhana agar Navbar App muncul di halaman-halaman ini */}
            <Route
              path="/*"
              element={
                <>
                  <AppNavbar /> {/* Navbar khusus user login */}
                  <Routes>
                    <Route
                      path="dashboard"
                      element={
                        <ProtectedRoute>
                          <DashboardPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="upload"
                      element={
                        <ProtectedRoute>
                          <UploadPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="search"
                      element={
                        <ProtectedRoute>
                          <SearchPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="projects/:projectId"
                      element={
                        <ProtectedRoute>
                          <ProjectDetailPage />
                        </ProtectedRoute>
                      }
                    />
                    {/* Redirect unknown routes back to home */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;