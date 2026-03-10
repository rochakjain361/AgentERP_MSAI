/**
 * Custom hook for health check
 */
import { useState, useCallback } from 'react';
import { healthApi } from '../lib/api';

export const useHealth = () => {
  const [erpStatus, setErpStatus] = useState('disconnected');

  const checkHealth = useCallback(async () => {
    try {
      const response = await healthApi.check();
      if (response.data.status === 'healthy') {
        setErpStatus(response.data.erp_mode === 'mock' ? 'syncing' : 'connected');
      }
    } catch (error) {
      setErpStatus('disconnected');
    }
  }, []);

  return {
    erpStatus,
    checkHealth,
  };
};

export default useHealth;
