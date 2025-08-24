import axios from "axios";

const api = axios.create({
  baseURL: "/api", // Vite proxy -> http://localhost:8000
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Request interceptor: attach token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ Response interceptor: handle expired/invalid token
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Remove stale token
      localStorage.removeItem("token");

      // Optional: redirect user to login
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
