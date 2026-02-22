/**
 * TokenDebugger Component
 * 
 * Add this component to your app to visualize token refresh in real-time.
 * Shows: access token, refresh status, and countdown timer
 * 
 * Usage:
 * import TokenDebugger from './components/TokenDebugger';
 * 
 * // In your App.jsx or Dashboard:
 * <TokenDebugger />
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const TokenDebugger = () => {
  const { isAuthenticated } = useAuth();
  const [tokenInfo, setTokenInfo] = useState({
    accessToken: '',
    lastRefresh: null,
    nextRefresh: null,
  });
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    if (isAuthenticated) {
      // Update token info
      const updateTokenInfo = () => {
        const token = localStorage.getItem('access_token');
        setTokenInfo(prev => ({
          accessToken: token ? token.substring(0, 20) + '...' : 'None',
          lastRefresh: new Date().toLocaleTimeString(),
          nextRefresh: new Date(Date.now() + 25 * 60 * 1000).toLocaleTimeString(),
        }));
      };

      updateTokenInfo();

      // Countdown timer (updates every second)
      const countdownInterval = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 0) return 25 * 60; // Reset to 25 minutes
          return prev - 1;
        });
      }, 1000);

      // Listen for token changes
      const tokenCheckInterval = setInterval(() => {
        const currentToken = localStorage.getItem('access_token');
        if (currentToken !== tokenInfo.accessToken) {
          updateTokenInfo();
          setCountdown(25 * 60); // Reset countdown
        }
      }, 1000);

      return () => {
        clearInterval(countdownInterval);
        clearInterval(tokenCheckInterval);
      };
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) return null;

  const minutes = Math.floor(countdown / 60);
  const seconds = countdown % 60;

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: 'rgba(0, 0, 0, 0.9)',
      color: 'white',
      padding: '15px',
      borderRadius: '8px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 9999,
      minWidth: '300px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
    }}>
      <div style={{ marginBottom: '10px', fontWeight: 'bold', color: '#4ade80' }}>
        🔐 Token Debug Info
      </div>
      
      <div style={{ marginBottom: '8px' }}>
        <span style={{ color: '#94a3b8' }}>Access Token:</span>
        <div style={{ color: '#fbbf24', fontSize: '10px', marginTop: '2px' }}>
          {tokenInfo.accessToken}
        </div>
      </div>

      <div style={{ marginBottom: '8px' }}>
        <span style={{ color: '#94a3b8' }}>Last Refresh:</span>
        <div style={{ color: '#60a5fa', marginTop: '2px' }}>
          {tokenInfo.lastRefresh || 'Not yet'}
        </div>
      </div>

      <div style={{ marginBottom: '8px' }}>
        <span style={{ color: '#94a3b8' }}>Next Refresh:</span>
        <div style={{ color: '#60a5fa', marginTop: '2px' }}>
          {tokenInfo.nextRefresh || 'Calculating...'}
        </div>
      </div>

      <div style={{
        marginTop: '12px',
        padding: '10px',
        background: 'rgba(59, 130, 246, 0.2)',
        borderRadius: '4px',
        textAlign: 'center',
      }}>
        <div style={{ color: '#94a3b8', fontSize: '10px', marginBottom: '4px' }}>
          NEXT AUTO-REFRESH IN
        </div>
        <div style={{
          fontSize: '20px',
          fontWeight: 'bold',
          color: countdown < 60 ? '#ef4444' : '#4ade80',
        }}>
          {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
        </div>
      </div>

      <div style={{
        marginTop: '10px',
        fontSize: '10px',
        color: '#64748b',
        textAlign: 'center',
      }}>
        ✅ Auto-refresh enabled
      </div>
    </div>
  );
};

export default TokenDebugger;
