const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5001';

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
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
}

export default fetchApi;

// Utility function to handle JSON responses
export async function fetchApiJson<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetchApi(endpoint, options);
  return response.json();
}

// Common API endpoints
export const API_ENDPOINTS = {
  WALLET: (address: string) => `/api/wallet/${address}`,
  TRANSACTIONS: (address: string) => `/api/transactions/${address}`,
  MINERS: '/api/miners',
  REGISTER_MINER: '/api/register-miner',
  TRANSACTION: '/api/transaction',
} as const;