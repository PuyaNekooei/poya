import axios from 'axios'

// Create axios instance
const apiClient = axios.create({
  baseURL: 'http://localhost:4040/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors (but NOT redirect)
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Only clear auth data on 401 for non-login requests
    if (error.response && error.response.status === 401) {
      const isLoginAttempt = error.config?.url?.includes('/auth/login/')
      if (!isLoginAttempt) {
        // Clear auth data for authenticated requests that fail
        localStorage.removeItem('authToken')
        localStorage.removeItem('isAuthenticated')
        localStorage.removeItem('username')
        localStorage.removeItem('userId')
        localStorage.removeItem('role')
        localStorage.removeItem('roles')
        localStorage.removeItem('isAdmin')
        console.log('Authentication expired - please login again')
      }
    }
    
    // Always reject the error so components can handle it
    return Promise.reject(error)
  }
)

// API endpoints configuration
const api = {
  // Direct axios methods
  get: (url, config) => apiClient.get(url, config),
  post: (url, data, config) => apiClient.post(url, data, config),
  put: (url, data, config) => apiClient.put(url, data, config),
  patch: (url, data, config) => apiClient.patch(url, data, config),
  delete: (url, config) => apiClient.delete(url, config),

  // Authentication endpoints
  auth: {
    login: (credentials) => apiClient.post('/auth/login/', credentials),
    logout: () => apiClient.post('/auth/logout/'),
    register: (userData) => apiClient.post('/auth/register/', userData),
    profile: () => apiClient.get('/auth/profile/'),
  },
  
  // Categories endpoints
  categories: {
    list: () => apiClient.get('/categories/'),
    create: (data) => apiClient.post('/categories/', data),
    update: (id, data) => apiClient.put(`/categories/${id}/`, data),
    patch: (id, data) => apiClient.patch(`/categories/${id}/`, data),
    delete: (id) => apiClient.delete(`/categories/${id}/`),
    detail: (id) => apiClient.get(`/categories/${id}/`),
  },
  
  // Menu items endpoints
  menu: {
    list: () => apiClient.get('/menu-items/'),
    withInventory: () => apiClient.get('/menu-items/with_inventory/'),
    create: (data) => apiClient.post('/menu-items/', data),
    update: (id, data) => apiClient.put(`/menu-items/${id}/`, data),
    patch: (id, data) => apiClient.patch(`/menu-items/${id}/`, data),
    delete: (id) => apiClient.delete(`/menu-items/${id}/`),
    detail: (id) => apiClient.get(`/menu-items/${id}/`),
    byCategory: (categoryId) => apiClient.get(`/menu-items/?category=${categoryId}`),
    toggleAvailability: (id) => apiClient.patch(`/menu-items/${id}/`, { is_available: !item.is_available }),
  },
  
  // Inventory endpoints
  inventory: {
    list: () => apiClient.get('/inventory/'),
    byDate: (date) => apiClient.get(`/inventory/?date=${date}`),
    create: (data) => apiClient.post('/inventory/', data),
    update: (id, data) => apiClient.put(`/inventory/${id}/`, data),
    patch: (id, data) => apiClient.patch(`/inventory/${id}/`, data),
    delete: (id) => apiClient.delete(`/inventory/${id}/`),
    detail: (id) => apiClient.get(`/inventory/${id}/`),
    bulkUpdate: (data) => apiClient.post('/inventory/bulk_update/', data),
  },
  
  // Tables endpoints (dine-in tables)
  tables: {
    list: () => apiClient.get('/tables/'),
    active: () => apiClient.get('/tables/?active=true'),
    create: (data) => apiClient.post('/tables/', data),
    update: (id, data) => apiClient.put(`/tables/${id}/`, data),
    patch: (id, data) => apiClient.patch(`/tables/${id}/`, data),
    delete: (id) => apiClient.delete(`/tables/${id}/`),
    detail: (id) => apiClient.get(`/tables/${id}/`),
  },

  // Orders endpoints
  orders: {
    list: () => apiClient.get('/orders/'),
    create: (data) => apiClient.post('/orders/', data),
    update: (id, data) => apiClient.put(`/orders/${id}/`, data),
    patch: (id, data) => apiClient.patch(`/orders/${id}/`, data),
    delete: (id) => apiClient.delete(`/orders/${id}/`),
    detail: (id) => apiClient.get(`/orders/${id}/`),
    today: () => apiClient.get('/orders/today/'),
    pending: () => apiClient.get('/orders/pending/'),
    byStatus: (status) => apiClient.get(`/orders/?status=${status}`),
    byDate: (date) => apiClient.get(`/orders/?date=${date}`),
    updateStatus: (id, status) => apiClient.post(`/orders/${id}/update_status/`, { status }),
    statistics: () => apiClient.get('/orders/statistics/'),
    // Slim, read-only list of today's orders + status (customer/staff viewable)
    statusBoard: () => apiClient.get('/orders/status_board/'),
  },
  
  // Order items endpoints
  orderItems: {
    list: () => apiClient.get('/order-items/'),
    create: (data) => apiClient.post('/order-items/', data),
    update: (id, data) => apiClient.put(`/order-items/${id}/`, data),
    patch: (id, data) => apiClient.patch(`/order-items/${id}/`, data),
    delete: (id) => apiClient.delete(`/order-items/${id}/`),
    detail: (id) => apiClient.get(`/order-items/${id}/`),
    byOrder: (orderId) => apiClient.get(`/order-items/?order=${orderId}`),
  },

  // Analytics endpoints (admin only): statistics + predictions
  analytics: {
    statistics: (days = 30) => apiClient.get(`/analytics/statistics/?days=${days}`),
    predictions: (horizon = 7) => apiClient.get(`/analytics/predictions/?horizon=${horizon}`),
  }
}

export default api