// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

// Function to refresh access token using HttpOnly cookie
const refreshAccessToken = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',  // ✅ Sends HttpOnly refresh_token cookie
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    
    // Update access token in localStorage
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return data;
  } catch (error) {
    // Refresh failed - clear auth data
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    throw error;
  }
};

// Generic API request handler with 401 interceptor
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const makeRequest = async (isRetry = false) => {
    const config = {
      ...options,
      credentials: 'include',  // ✅ Always include cookies for refresh token
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      // ✅ 401 INTERCEPTOR: Handle token expiration
      if (response.status === 401 && !isRetry && !endpoint.includes('/auth/')) {
        console.log('🔄 Access token expired, attempting refresh...');
        
        try {
          // Refresh the access token
          await refreshAccessToken();
          console.log('✅ Token refreshed successfully, retrying request...');
          
          // Retry the original request with new token
          return makeRequest(true);
        } catch (refreshError) {
          console.error('❌ Token refresh failed:', refreshError);
          // Redirect to login
          localStorage.clear();
          window.location.href = '/signin';
          throw new Error('Session expired. Please login again.');
        }
      }
      
      // Handle different response types
      const contentType = response.headers.get('content-type');
      let data;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        // Extract error message from response
        const errorMessage = data?.detail || data?.message || data || 'An error occurred';
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      // Don't log errors for retry attempts
      if (!isRetry) {
        console.error('API Request Error:', error);
      }
      throw error;
    }
  };
  
  return makeRequest();
};

// Auth API functions
export const authAPI = {
  // Sign up a new user
  signup: async (userData) => {
    const response = await apiRequest('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email: userData.email,
        username: userData.username,
        password: userData.password,
      }),
    });
    
    // Store tokens in localStorage
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  },

  // Login user
  login: async (credentials) => {
    const response = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
    });
    
    // Store tokens in localStorage (refresh_token is in HttpOnly cookie)
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  },

  // Get current user details
  getCurrentUser: async () => {
    // First, try to get from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      return JSON.parse(storedUser);
    }
    return null;
  },

  // Refresh access token using HttpOnly cookie
  refreshToken: async () => {
    return await refreshAccessToken();
  },

  // Logout user
  logout: async () => {
    try {
      await apiRequest('/auth/logout-current', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens from localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Resend verification email
  resendVerification: async () => {
    return await apiRequest('/auth/resend-verification', {
      method: 'POST',
    });
  },

  // Verify email with token
  verifyEmail: async (token) => {
    return await apiRequest(`/auth/verify-email?token=${token}`, {
      method: 'GET',
    });
  },
};

// Pipeline API functions
export const pipelineAPI = {
  // Create a new pipeline
  create: async (pipelineData) => {
    return await apiRequest('/pipelines', {
      method: 'POST',
      body: JSON.stringify(pipelineData),
    });
  },

  // Update an existing pipeline
  update: async (pipelineId, pipelineData) => {
    return await apiRequest(`/pipelines/${pipelineId}`, {
      method: 'PUT',
      body: JSON.stringify(pipelineData),
    });
  },

  // Delete a pipeline
  delete: async (pipelineId) => {
    return await apiRequest(`/pipelines/${pipelineId}`, {
      method: 'DELETE',
    });
  },

  // Get all pipelines for the current user
  getAll: async () => {
    return await apiRequest('/pipelines', {
      method: 'GET',
    });
  },

  // Get a specific pipeline
  getById: async (pipelineId) => {
    return await apiRequest(`/pipelines/${pipelineId}`, {
      method: 'GET',
    });
  },
};

// Asset API functions
export const assetAPI = {
  // Request upload URLs for multiple files
  requestUploadUrls: async (pipelineId, files) => {
    const fileRequests = files.map(file => ({
      filename: file.name,
      content_type: file.type,
      file_size: file.size,
    }));

    return await apiRequest(`/pipelines/${pipelineId}/assets/upload-urls`, {
      method: 'POST',
      body: JSON.stringify({ files: fileRequests }),
    });
  },

  // Upload file directly to S3 using presigned URL
  uploadToS3: async (uploadUrl, uploadFields, file) => {
    const formData = new FormData();
    
    // Add all fields from presigned POST
    Object.entries(uploadFields).forEach(([key, value]) => {
      formData.append(key, value);
    });
    
    // Add file last
    formData.append('file', file);

    // Upload directly to S3 (no auth headers needed)
    const response = await fetch(uploadUrl, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`S3 upload failed: ${response.statusText}`);
    }

    return response;
  },

  // Confirm upload success
  confirmUpload: async (pipelineId, assetId, success = true, errorMessage = null) => {
    return await apiRequest(`/pipelines/${pipelineId}/assets/${assetId}/confirm`, {
      method: 'PATCH',
      body: JSON.stringify({ success, error_message: errorMessage }),
    });
  },

  // Get all assets for a pipeline
  getAssets: async (pipelineId) => {
    return await apiRequest(`/pipelines/${pipelineId}/assets`, {
      method: 'GET',
    });
  },

  // Get download URL for an asset
  getDownloadUrl: async (pipelineId, assetId) => {
    return await apiRequest(`/pipelines/${pipelineId}/assets/${assetId}/download-url`, {
      method: 'GET',
    });
  },

  // Delete an asset
  deleteAsset: async (pipelineId, assetId) => {
    return await apiRequest(`/pipelines/${pipelineId}/assets/${assetId}`, {
      method: 'DELETE',
    });
  },
};

// Pipeline Execution API functions
export const pipelineExecutionAPI = {
  execute: async (pipelineId, payload = {}) => {
    return await apiRequest(`/api/pipelines/${pipelineId}/execute`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  listRuns: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const suffix = query ? `?${query}` : '';
    return await apiRequest(`/api/pipelines/runs${suffix}`, {
      method: 'GET',
    });
  },
  getStats: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const suffix = query ? `?${query}` : '';
    return await apiRequest(`/api/pipelines/stats${suffix}`, {
      method: 'GET',
    });
  },
  getRun: async (runId) => {
    return await apiRequest(`/api/pipelines/runs/${runId}`, {
      method: 'GET',
    });
  },
  getRunLogs: async (runId, params = {}) => {
    const query = new URLSearchParams(params).toString();
    const suffix = query ? `?${query}` : '';
    return await apiRequest(`/api/pipelines/runs/${runId}/logs${suffix}`, {
      method: 'GET',
    });
  },
  getRunOutputs: async (runId) => {
    return await apiRequest(`/api/pipelines/runs/${runId}/outputs`, {
      method: 'GET',
    });
  },
};

export default authAPI;
