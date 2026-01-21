import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useToast } from './use-toast';

/**
 * Enhanced authentication hook with additional utilities
 * Provides common auth-related functions used across components
 */
export const useAuthHelpers = () => {
  const { user, isAuthenticated, login, logout, signup } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  /**
   * Handle login with error handling and navigation
   */
  const handleLogin = async (credentials, redirectTo = '/dashboard') => {
    try {
      await login(credentials);
      toast({
        title: 'Success!',
        description: 'Welcome back!',
      });
      navigate(redirectTo);
      return true;
    } catch (error) {
      toast({
        title: 'Login Failed',
        description: error.message || 'Invalid credentials',
        variant: 'destructive',
      });
      return false;
    }
  };

  /**
   * Handle signup with error handling and navigation
   */
  const handleSignup = async (userData, redirectTo = '/dashboard') => {
    try {
      await signup(userData);
      toast({
        title: 'Success!',
        description: 'Your account has been created',
      });
      navigate(redirectTo);
      return true;
    } catch (error) {
      toast({
        title: 'Signup Failed',
        description: error.message || 'Could not create account',
        variant: 'destructive',
      });
      return false;
    }
  };

  /**
   * Handle logout with navigation
   */
  const handleLogout = async (redirectTo = '/') => {
    try {
      await logout();
      toast({
        title: 'Logged Out',
        description: 'You have been successfully logged out',
      });
      navigate(redirectTo);
      return true;
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to logout properly',
        variant: 'destructive',
      });
      return false;
    }
  };

  /**
   * Require authentication - redirect if not authenticated
   */
  const requireAuth = (redirectTo = '/signin') => {
    if (!isAuthenticated) {
      toast({
        title: 'Authentication Required',
        description: 'Please sign in to access this page',
        variant: 'destructive',
      });
      navigate(redirectTo);
      return false;
    }
    return true;
  };

  /**
   * Get user display name
   */
  const getUserDisplayName = () => {
    if (!user) return 'User';
    return user.username || user.name || user.email?.split('@')[0] || 'User';
  };

  /**
   * Get user initials for avatar
   */
  const getUserInitials = () => {
    if (!user) return 'U';
    
    const name = user.username || user.name;
    if (name) {
      return name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    
    if (user.email) {
      return user.email.substring(0, 2).toUpperCase();
    }
    
    return 'U';
  };

  /**
   * Check if user email is verified
   */
  const isEmailVerified = () => {
    return user?.is_verified || false;
  };

  /**
   * Check if user account is active
   */
  const isAccountActive = () => {
    return user?.is_active || false;
  };

  return {
    // Auth state
    user,
    isAuthenticated,
    
    // Auth actions
    handleLogin,
    handleSignup,
    handleLogout,
    requireAuth,
    
    // User utilities
    getUserDisplayName,
    getUserInitials,
    isEmailVerified,
    isAccountActive,
  };
};
