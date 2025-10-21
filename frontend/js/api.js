/* ===================================
   JeevanDhara API Service Layer
   =================================== */

   const API_BASE_URL = 'http://localhost:5000'; 

   async function apiRequest(endpoint, options = {}) {
     const url = `${API_BASE_URL}${endpoint}`;
     const token = localStorage.getItem('authToken');
     const headers = {
       'Content-Type': 'application/json',
       ...(token && { 'Authorization': `Bearer ${token}` })
     };
     
     const config = { headers, ...options };
     if (options.body && typeof options.body !== 'string') {
       config.body = JSON.stringify(options.body);
     }
     
     try {
       const response = await fetch(url, config);
       if (!response.ok) {
         const errorData = await response.json();
         throw new Error(errorData.msg || 'API request failed');
       }
       return await response.json();
     } catch (error) {
       console.error('API Error:', error);
       throw error;
     }
   }
   
   // Auth APIs
   const authAPI = {
     login: (email, password) => apiRequest('/auth/login', { method: 'POST', body: { email, password } }),
     signup: (data) => apiRequest('/auth/signup', { method: 'POST', body: data }),
     logout: () => {
       localStorage.removeItem('authToken');
       localStorage.removeItem('userRole');
       window.location.href = 'login.html';
     }
   };
   
   // Donor APIs
   const donorAPI = {
     getProfile: () => apiRequest('/donor/profile'),
     bookAppointment: (data) => apiRequest('/donor/book-appointment', { method: 'POST', body: data }),
     getAppointments: () => apiRequest('/donor/appointments'),
     checkEligibility: (data) => apiRequest('/donor/check-eligibility', { method: 'POST', body: data }),
     getDonationHistory: () => apiRequest('/donor/history')
   };
   
   // Hospital APIs
   const hospitalAPI = {
     getBloodStock: (filters = {}) => {
       const query = new URLSearchParams(filters).toString();
       return apiRequest(`/hospital/blood-stock?${query}`);
     },
     requestBlood: (data) => apiRequest('/hospital/request-blood', { method: 'POST', body: data }),
     getRequests: () => apiRequest('/hospital/requests')
   };
   
   // Admin APIs
   const adminAPI = {
     getBloodUnits: () => apiRequest('/admin/blood-units'),
     manageBloodUnit: (data, action = 'create') => {
       return apiRequest('/admin/blood-units', {
         method: action === 'create' ? 'POST' : 'PUT',
         body: data
       });
     },
     deleteBloodUnit: (id) => apiRequest(`/admin/blood-units/${id}`, { method: 'DELETE' }),
     getRequests: () => apiRequest('/admin/requests'),
     updateRequestStatus: (id, status) => apiRequest(`/admin/requests/${id}`, { method: 'PUT', body: { status } }),
     sendEmergencyAlert: (data) => apiRequest('/admin/emergency-alert', { method: 'POST', body: data })
   };
   
   // Export globally for use in app.js
   window.authAPI = authAPI;
   window.donorAPI = donorAPI;
   window.hospitalAPI = hospitalAPI;
   window.adminAPI = adminAPI;
   