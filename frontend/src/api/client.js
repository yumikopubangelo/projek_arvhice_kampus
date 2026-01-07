import axios from 'axios';
import { encryptSensitiveFields } from '../utils/encryption';

// =====================================================
// API BASE URL
// =====================================================
// Use /api for production (nginx), localhost:8000/api for development
const isProduction = import.meta.env.PROD;
const API_BASE_URL = isProduction ? '/api' : 'http://localhost:8000/api';

// =====================================================
// CREATE AXIOS INSTANCE
// =====================================================
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
  withCredentials: true, // PENTING: Untuk mengirim cookies/credentials
});

// =====================================================
// REQUEST INTERCEPTOR - ADD JWT TOKEN & ENCRYPT DATA
// =====================================================
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('token');

    if (token) {
      // Add Authorization header
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Encrypt sensitive data in request body (only for JSON requests)
    if (config.data && typeof config.data === 'object' && config.headers['Content-Type'] === 'application/json') {
      config.data = encryptSensitiveFields(config.data);
    }

    // Debug log (hapus di production)
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      hasToken: !!token,
    });

    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// =====================================================
// RESPONSE INTERCEPTOR - HANDLE ERRORS
// =====================================================
api.interceptors.response.use(
  (response) => {
    // Debug log (hapus di production)
    console.log('✅ API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data,
    });
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
      url: error.config?.url,
    });
    
    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      // Clear token
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Redirect ke login jika belum di halaman login
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;