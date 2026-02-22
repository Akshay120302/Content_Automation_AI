import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedUser = localStorage.getItem('user');
        const token = localStorage.getItem('access_token');
        
        if (storedUser && token) {
          setUser(JSON.parse(storedUser));
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        // Clear invalid data
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // ✅ AUTO-REFRESH TIMER: Refresh access token every 20 minutes
  useEffect(() => {
    if (isAuthenticated) {
      console.log('🔄 Starting auto-refresh timer (every 20 minutes)');
      
      const refreshInterval = setInterval(async () => {
        try {
          console.log('⏰ Auto-refreshing access token...');
          const response = await authAPI.refreshToken();
          
          if (response && response.access_token) {
            console.log('✅ Access token refreshed successfully');
            setUser(response.user);
          }
        } catch (error) {
          console.error('❌ Auto-refresh failed:', error);
          // Don't logout immediately - 401 interceptor will handle it on next request
        }
      }, 20 * 60 * 1000); // 20 minutes in milliseconds

      // Cleanup interval on unmount or when auth changes
      return () => {
        console.log('🛑 Stopping auto-refresh timer');
        clearInterval(refreshInterval);
      };
    }
  }, [isAuthenticated]);

  const signup = async (userData) => {
    try {
      const response = await authAPI.signup(userData);
      setUser(response.user);
      setIsAuthenticated(true);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      setUser(response.user);
      setIsAuthenticated(true);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const refreshUser = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      return userData;
    } catch (error) {
      console.error('Error refreshing user:', error);
      throw error;
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    signup,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
