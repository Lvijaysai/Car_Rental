//frontend/src/api/endpoints.js
import apiClient from './client';

// Auth endpoints
export const authAPI = {
  register: (data) => apiClient.post('/api/register/', data),
  login: (data) => apiClient.post('/api/login/', data),
  logout: () => apiClient.post('/api/logout/'),
  currentUser: () => apiClient.get('/api/current-user/'),
};

// Car endpoints
export const carsAPI = {
  list: (params) => apiClient.get('/api/cars/', { params }),
  detail: (slug) => apiClient.get(`/api/cars/${slug}/`),
  search: (term, start, end) => 
    apiClient.get('/api/cars/search/', {
      params: { term, start, end }
    }),
};

// Booking endpoints
export const bookingsAPI = {
  list: (params) => apiClient.get('/api/bookings/', { params }),
  create: (data) => apiClient.post('/api/bookings/create/', data),
  cancel: (id) => apiClient.post(`/api/bookings/${id}/cancel/`),
  active: () => apiClient.get('/api/bookings/active/'),
  history: () => apiClient.get('/api/bookings/history/'),
};

// Dashboard endpoints
export const dashboardAPI = {
  dashboard: () => apiClient.get('/api/dashboard/'),
  history: () => apiClient.get('/api/history/'),
};

// Notification endpoints
export const notificationsAPI = {
  list: (params) => apiClient.get('/api/notifications/', { params }),
  unreadCount: () => apiClient.get('/api/notifications/unread_count/'),
  markRead: (data) => apiClient.post('/api/notifications/mark_read/', data),
  markSingleRead: (id) => apiClient.post(`/api/notifications/${id}/mark_single_read/`),
};
