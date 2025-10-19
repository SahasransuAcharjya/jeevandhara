/* ===================================
   JeevanDhara - API Service Layer
   =================================== */

   const API_BASE_URL = 'http://localhost:5000/api'; // Change to your backend URL

   // Utility function for making API requests
   async function apiRequest(endpoint, options = {}) {
       const url = `${API_BASE_URL}${endpoint}`;
       const defaultOptions = {
           headers: {
               'Content-Type': 'application/json',
           },
       };
   
       // Add authentication token if available
       const token = localStorage.getItem('authToken');
       if (token) {
           defaultOptions.headers['Authorization'] = `Bearer ${token}`;
       }
   
       const config = { ...defaultOptions, ...options };
       
       try {
           const response = await fetch(url, config);
           
           if (!response.ok) {
               throw new Error(`HTTP error! status: ${response.status}`);
           }
           
           return await response.json();
       } catch (error) {
           console.error('API Request failed:', error);
           throw error;
       }
   }
   
   // Authentication APIs
   const authAPI = {
       login: async (email, password) => {
           return apiRequest('/auth/login', {
               method: 'POST',
               body: JSON.stringify({ email, password })
           });
       },
   
       signup: async (userData) => {
           return apiRequest('/auth/signup', {
               method: 'POST',
               body: JSON.stringify(userData)
           });
       },
   
       logout: () => {
           localStorage.removeItem('authToken');
           localStorage.removeItem('userType');
           window.location.href = 'index.html';
       }
   };
   
   // Donor APIs
   const donorAPI = {
       getProfile: async () => {
           return apiRequest('/donor/profile');
       },
   
       updateProfile: async (profileData) => {
           return apiRequest('/donor/profile', {
               method: 'PUT',
               body: JSON.stringify(profileData)
           });
       },
   
       bookAppointment: async (appointmentData) => {
           return apiRequest('/donor/book-appointment', {
               method: 'POST',
               body: JSON.stringify(appointmentData)
           });
       },
   
       getAppointments: async () => {
           return apiRequest('/donor/appointments');
       },
   
       checkEligibility: async (eligibilityData) => {
           return apiRequest('/donor/check-eligibility', {
               method: 'POST',
               body: JSON.stringify(eligibilityData)
           });
       },
   
       getDonationHistory: async () => {
           return apiRequest('/donor/history');
       }
   };
   
   // Hospital APIs
   const hospitalAPI = {
       getBloodStock: async (filters = {}) => {
           const queryParams = new URLSearchParams(filters);
           return apiRequest(`/hospital/blood-stock?${queryParams}`);
       },
   
       requestBlood: async (requestData) => {
           return apiRequest('/hospital/request-blood', {
               method: 'POST',
               body: JSON.stringify(requestData)
           });
       },
   
       getRequests: async () => {
           return apiRequest('/hospital/requests');
       }
   };
   
   // Admin APIs
   const adminAPI = {
       getDashboardStats: async () => {
           return apiRequest('/admin/dashboard-stats');
       },
   
       manageBloodUnit: async (unitData, action = 'create') => {
           const method = action === 'create' ? 'POST' : 'PUT';
           return apiRequest('/admin/blood-units', {
               method,
               body: JSON.stringify(unitData)
           });
       },
   
       getBloodUnits: async () => {
           return apiRequest('/admin/blood-units');
       },
   
       deleteBloodUnit: async (unitId) => {
           return apiRequest(`/admin/blood-units/${unitId}`, {
               method: 'DELETE'
           });
       },
   
       sendEmergencyAlert: async (alertData) => {
           return apiRequest('/admin/emergency-alert', {
               method: 'POST',
               body: JSON.stringify(alertData)
           });
       },
   
       getRequests: async () => {
           return apiRequest('/admin/requests');
       },
   
       updateRequestStatus: async (requestId, status) => {
           return apiRequest(`/admin/requests/${requestId}`, {
               method: 'PUT',
               body: JSON.stringify({ status })
           });
       }
   };
   
   // Export APIs for use in other files
   window.authAPI = authAPI;
   window.donorAPI = donorAPI;
   window.hospitalAPI = hospitalAPI;
   window.adminAPI = adminAPI;
   