import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('🔄 AuthContext: Checking for existing token...');

    // Test localStorage functionality
    try {
      localStorage.setItem('test', 'working');
      const testValue = localStorage.getItem('test');
      localStorage.removeItem('test');
      console.log('🧪 localStorage test:', testValue === 'working' ? 'WORKING' : 'FAILED');
    } catch (e) {
      console.error('❌ localStorage not available:', e);
    }

    const token = localStorage.getItem('token');
    console.log('🔍 Found token in localStorage:', token ? 'Yes' : 'No');

    if (token) {
      console.log('🔑 Setting up existing token:', token.substring(0, 20) + '...');
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUser({ token });
    }
    setLoading(false);
    console.log('✅ AuthContext initialization complete');
  }, []);

  const login = async (username, password) => {
    console.log('🚀 Login function called with username:', username);
    
    try {
      // Use URLSearchParams for x-www-form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      console.log('📤 Login request payload:', formData.toString());

      // ✅ Use the configured api instance with proxy
      console.log('📡 Making API request to /auth/token...');
      const response = await api.post(
        '/auth/token',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      console.log('✅ API request successful!');
      console.log('📥 Full response:', response);
      console.log('📋 Response data:', response.data);
      console.log('🔍 Response status:', response.status);

      // Check if response.data exists
      if (!response.data) {
        console.error('❌ No data in response:', response);
        return {
          success: false,
          error: 'No data received from server',
        };
      }

      // Extract access_token
      const { access_token } = response.data;
      console.log('🔑 Extracted access_token:', access_token);

      // Validate token exists
      if (!access_token) {
        console.error('❌ No access_token in response data:', response.data);
        return {
          success: false,
          error: 'No access token received from server',
        };
      }

      console.log('💾 Attempting to store token in localStorage...');
      
      // Test localStorage before storing
      try {
        localStorage.setItem('token', access_token);
        console.log('✅ Token stored successfully');
        
        // Verify it was stored
        const storedToken = localStorage.getItem('token');
        console.log('🔍 Verification - stored token:', storedToken ? 'Found' : 'Not found');
        console.log('🔍 Token matches:', storedToken === access_token ? 'Yes' : 'No');
        
      } catch (storageError) {
        console.error('❌ Failed to store token:', storageError);
        return {
          success: false,
          error: 'Failed to store authentication token',
        };
      }

      console.log('🔗 Setting authorization header...');
      // Set authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      console.log('✅ Authorization header set:', api.defaults.headers.common['Authorization']);

      console.log('👤 Updating user state...');
      // Update user state
      setUser({ token: access_token, username });
      console.log('✅ User state updated successfully');

      console.log('🎉 Login completed successfully!');
      return { success: true };

    } catch (error) {
      console.error('❌ Login error occurred:');
      console.error('Error object:', error);
      console.error('Error message:', error.message);
      console.error('Error response:', error.response);
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Login failed',
      };
    }
  };

  const register = async (username, password) => {
    console.log('📝 Register function called with username:', username);
    try {
      const response = await api.post('/auth/register', { username, password });
      console.log('✅ Registration successful:', response);
      return { success: true };
    } catch (error) {
      console.error('❌ Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };
 
  const getDashboard = async () => {
    console.log('📊 Dashboard function called');
    try {
      // ✅ No need to manually add token - api interceptor handles it
      const response = await api.get("/dashboard/");
      console.log('✅ Dashboard data received:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error("❌ Dashboard fetch error:", error);
      return {
        success: false,
        error: error.response?.data?.detail || "Unauthorized",
      };
    }
  };

  const logout = () => {
    console.log('🚪 Logout function called');
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    console.log('✅ Logout completed');
  };

  const value = {
    user,
    login,
    register,
    logout,
    getDashboard,    
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}