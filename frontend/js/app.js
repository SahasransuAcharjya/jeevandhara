/* ===================================
   JeevanDhara Main Application Logic
   =================================== */

   document.addEventListener('DOMContentLoaded', () => {
    checkAuthOnLoad();
    setupEventListeners();
    loadPageData();
  });
  
  function checkAuthOnLoad() {
    const token = localStorage.getItem('authToken');
    if (!token && !['login.html', 'signup.html'].includes(window.location.pathname.split('/').pop())) {
      window.location.href = 'login.html';
    }
  }
  
  function setupEventListeners() {
    if (document.getElementById('loginForm')) {
      document.getElementById('loginForm').addEventListener('submit', handleLogin);
    }
    if (document.getElementById('signupForm')) {
      document.getElementById('signupForm').addEventListener('submit', handleSignUp);
    }
    if (document.getElementById('bloodRequestForm')) {
      document.getElementById('bloodRequestForm').addEventListener('submit', handleBloodRequest);
    }
    if (document.getElementById('alertForm')) {
      document.getElementById('alertForm').addEventListener('submit', handleEmergencyAlert);
    }
    if (document.getElementById('stock-search')) {
      document.getElementById('stock-search').addEventListener('input', debounce(handleStockSearch, 500));
    }
  }
  
  function loadPageData() {
    const page = window.location.pathname.split('/').pop();
  
    switch (page) {
      case 'donor-dashboard.html':
        loadDonorDashboard();
        break;
      case 'hospital-dashboard.html':
        loadHospitalDashboard();
        break;
      case 'admin-panel.html':
        loadAdminPanel();
        break;
    }
  }
  
  // Authentication handlers
  async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.email.value.trim();
    const password = form.password.value.trim();
  
    try {
      const data = await authAPI.login(email, password);
      localStorage.setItem('authToken', data.token);
      // For simplicity assume role donor or hospital based on blood_type present
      localStorage.setItem('userRole', 'donor');
      window.location.href = 'donor-dashboard.html';
    } catch (err) {
      alert('Login failed: ' + err.message);
    }
  }
  
  async function handleSignUp(event) {
    event.preventDefault();
    const form = event.target;
    const payload = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      password: form.password.value,
      blood_type: form.blood_type.value,
      role: form.role.value
    };
  
    try {
      await authAPI.signup(payload);
      alert("Signup successful. Please log in.");
      window.location.href = 'login.html';
    } catch (err) {
      alert('Signup failed: ' + err.message);
    }
  }
  
  function logout() {
    authAPI.logout();
  }
  
  // Donor Dashboard functions
  async function loadDonorDashboard() {
    try {
      const profile = await donorAPI.getProfile();
      document.getElementById('welcome-name').textContent = `Welcome, ${profile.name}`;
      document.getElementById('blood-type').textContent = profile.blood_type || '-';
      document.getElementById('total-donations').textContent = profile.total_donations || '0';
  
      const appointments = await donorAPI.getAppointments();
      const tbody = document.getElementById('appointments-table-body');
      tbody.innerHTML = '';
      if (appointments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No appointments found.</td></tr>';
      } else {
        appointments.forEach(appt => {
          const row = document.createElement('tr');
          row.innerHTML = `<td>${new Date(appt.date).toLocaleDateString()}</td><td>${appt.location}</td><td>${appt.status}</td>`;
          tbody.appendChild(row);
        });
      }
    } catch (error) {
      alert('Failed to load donor dashboard: ' + error.message);
    }
  }
  
  // Hospital Dashboard functions
  async function loadHospitalDashboard() {
    try {
      const stock = await hospitalAPI.getBloodStock();
      const tbody = document.getElementById('stock-table-body');
      tbody.innerHTML = '';
      if (stock.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No blood stock available.</td></tr>';
      } else {
        stock.forEach(item => {
          const row = document.createElement('tr');
          row.innerHTML = `<td>${item.blood_type}</td><td>${item.units}</td><td>${item.location}</td>`;
          tbody.appendChild(row);
        });
      }
    } catch (error) {
      alert('Failed to load hospital dashboard: ' + error.message);
    }
  }
  
  async function handleBloodRequest(event) {
    event.preventDefault();
    const form = event.target;
    const requestData = {
      hospitalName: form.hospitalName.value.trim(),
      bloodType: form.bloodType.value,
      units: parseInt(form.units.value, 10)
    };
    try {
      await hospitalAPI.requestBlood(requestData);
      alert('Blood request submitted.');
      form.reset();
    } catch (error) {
      alert('Request failed: ' + error.message);
    }
  }
  
  async function handleStockSearch(event) {
    try {
      const query = event.target.value.trim();
      const stock = await hospitalAPI.getBloodStock({ search: query });
      const tbody = document.getElementById('stock-table-body');
      tbody.innerHTML = '';
      stock.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${item.blood_type}</td><td>${item.units}</td><td>${item.location}</td>`;
        tbody.appendChild(row);
      });
    } catch (error) {
      console.error('Stock search failed', error);
    }
  }
  
  // Admin Panel functions
  async function loadAdminPanel() {
    try {
      const bloodUnits = await adminAPI.getBloodUnits();
      const tbody = document.getElementById('blood-units-table-body');
      tbody.innerHTML = '';
      if (bloodUnits.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No blood units found.</td></tr>';
      } else {
        bloodUnits.forEach(unit => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${unit.bag_id}</td>
            <td>${unit.blood_type}</td>
            <td>${new Date(unit.expiry_date).toLocaleDateString()}</td>
            <td>${unit.location}</td>
            <td><button onclick="deleteBloodUnit('${unit._id}')">Delete</button></td>
          `;
          tbody.appendChild(row);
        });
      }
    } catch (error) {
      alert('Failed to load admin panel: ' + error.message);
    }
  }
  
  async function handleEmergencyAlert(event) {
    event.preventDefault();
    const form = event.target;
    const alertData = {
      bloodType: form.bloodType.value,
      region: form.region.value,
      message: form.message.value
    };
    try {
      await adminAPI.sendEmergencyAlert(alertData);
      alert('Emergency alert sent.');
      form.reset();
    } catch (error) {
      alert('Sending alert failed: ' + error.message);
    }
  }
  
  async function deleteBloodUnit(id) {
    if (confirm('Are you sure you want to delete this blood unit?')) {
      try {
        await adminAPI.deleteBloodUnit(id);
        alert('Blood unit deleted.');
        loadAdminPanel();
      } catch (error) {
        alert('Delete failed: ' + error.message);
      }
    }
  }
  
  // Utility functions
  function debounce(func, wait) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }
  
  function logout() {
    authAPI.logout();
  }
  