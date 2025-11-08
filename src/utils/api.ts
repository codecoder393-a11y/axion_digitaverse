const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001';
console.log('API_URL:', API_URL); // Debug log to verify the URL being used

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * Generic API fetch function with proper typing
 * @param endpoint - The API endpoint to call (e.g., '/api/wallet/123')
 * @param options - Fetch options including method, headers, body, etc.
 * @returns Promise with the fetch response
 */
async function fetchApi(endpoint: string, options: RequestOptions = {}) {
  try {
    const url = `${API_URL}${endpoint}`;
    console.log('Making API request to:', url);
    console.log('Request options:', options);

    const response = await fetch(url, {
      ...options,
      credentials: 'include',  // Include cookies for cross-origin requests
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
      mode: 'cors'  // Explicitly enable CORS
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Error response:', errorData);
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
}

// Export fetchApi (fetchApiJson is exported where it's declared below)
export { fetchApi };

// Utility function to handle JSON responses
export async function fetchApiJson<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetchApi(endpoint, options);
  return response.json();
}

// Export API_URL for use with image URLs and other direct fetch needs
export { API_URL };

// Common API endpoints
export const API_ENDPOINTS = {
  WALLET: (address: string) => `/api/wallet/${address}`,
  TRANSACTIONS: (address: string) => `/api/transactions/${address}`,
  MINERS: '/api/miners',
  REGISTER_MINER: '/api/register-miner',
  TRANSACTION: '/api/transaction',
  // Profile management
  PROFILE_PIC: (address: string) => `/api/profile-pic/${address}`,
  UPLOAD_PROFILE_PIC: '/api/upload-profile-pic',
  // User management
  CREATE_USER: '/api/create-user',
  LOGIN: '/api/login',
  // Loan management
  CREATE_LOAN: '/api/create-loan',
  APPROVE_LOAN: '/api/approve-loan',
  REQUEST_LOAN: '/api/request-loan',
  REPAY_LOAN: '/api/repay-loan',
  // Chain and IDE
  CHAIN: '/api/chain',
  IDE_LIST: '/api/ide/list',
  IDE_OPEN: '/api/ide/open',
  IDE_SAVE: '/api/ide/save',
  IDE_RUN: '/api/ide/run',
  IDE_CREATE: '/api/ide/create',
  IDE_DELETE: '/api/ide/delete',
  // Contract management
  CONTRACT_DEPLOY: '/api/contract/deploy',
  CONTRACT_CALL: '/api/contract/call',
  // Agent management
  REGISTER_AGENT: '/api/register-agent',
  AGENT_DEPOSIT: '/api/agent-deposit',
  // File storage
  STORE_FILE: '/api/store-file',
  // AI features
  AXION_AI: '/api/axion-ai',
  AXION_AI_DASHBOARD: '/api/axion-ai/dashboard',
} as const;