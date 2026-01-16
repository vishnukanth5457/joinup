import axios, { AxiosError } from 'axios';

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

export const handleApiError = (error: any): ApiError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    return {
      message: axiosError.response?.data?.detail || axiosError.message || 'An error occurred',
      status: axiosError.response?.status,
      details: axiosError.response?.data,
    };
  }

  return {
    message: error?.message || 'An unexpected error occurred',
  };
};

export const isNetworkError = (error: any): boolean => {
  return !error.response || error.code === 'ECONNABORTED' || error.code === 'ENOTFOUND';
};

export const isAuthError = (error: any): boolean => {
  return error.response?.status === 401 || error.response?.status === 403;
};

export const isValidationError = (error: any): boolean => {
  return error.response?.status === 400;
};

export const getErrorMessage = (error: any): string => {
  const apiError = handleApiError(error);
  
  if (isNetworkError(error)) {
    return 'Network error. Please check your connection.';
  }
  
  if (isAuthError(error)) {
    return 'Authentication failed. Please login again.';
  }
  
  if (isValidationError(error)) {
    return apiError.message || 'Please check your input and try again.';
  }
  
  return apiError.message || 'Something went wrong. Please try again.';
};
