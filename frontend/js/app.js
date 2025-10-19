/* ===================================
   JeevanDhara - Main Application Logic
   =================================== */

// Global variables
let currentUser = null;
let userType = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadPageSpecificContent();
});

// Initialize application
function initializeApp() {
    // Check if user is logged in
    const token = localStorage.getItem('authToken');
    userType = localStorage.getItem('userType');
    
    if (token && userType) {
        updateNavigation(true);
        loadUserData();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('stock-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchBloodStock, 500));
    }

    // Form submissions
    const bloodRequestForm = document.getElementById('bloodRequestForm');
    if (bloodRequestForm) {
        bloodRequestForm.addEventListener('submit', handleBloodRequest);
    }

    const alertForm = document.getElementById('alertForm');
    if (alertForm) {
        alertForm.addEventListener('submit', handleEmergencyAlert);
    }

    // Modal close events
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            closeModal();
        }
    });
}

// Load page-specific content
function loadPageSpecificContent() {
    const currentPage = window.location.pathname.split('/').pop();
    
    switch(currentPage) {
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

// Donor Dashboard Functions
async function loadDonorDashboard() {
    try {
        showLoading(true);
        
        // Load donor profile
        const profile = await donorAPI.getProfile();
        updateDonorProfile(profile);
        
        // Load appointments
        const appointments = await donorAPI.getAppointments();
        updateAppointmentsTable(appointments);
        
        // Load donation history
        const history = await donorAPI.getDonationHistory();
        updateDonationHistory(history);
        
    } catch (error) {
        showNotification('Failed to load dashboard data', 'error');
    } finally {
        showLoading(false);
    }
}

function updateDonorProfile(profile) {
    document.querySelector('.profile-card h2').textContent = `Welcome, ${profile.name}`;
    document.querySelector('.profile-card p:nth-child(2)').innerHTML = `Blood Type: <b>${profile.bloodType}</b>`;
    document.querySelector('.profile-card p:nth-child(3)').innerHTML = `Total Donations: <b>${profile.totalDonations}</b>`;
}

function updateAppointmentsTable(appointments) {
    const tbody = document.querySelector('.appointments table tbody') || 
                  document.querySelector('.appointments table').getElementsByTagName('tbody')[0];
    
    if (!tbody) return;
    
    tbody.innerHTML = '';
    appointments.forEach(appointment => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${formatDate(appointment.date)}</td>
            <td>${appointment.location}</td>
            <td><span class="status ${appointment.status.toLowerCase()}">${appointment.status}</span></td>
        `;
    });
}

// Hospital Dashboard Functions
async function loadHospitalDashboard() {
    try {
        showLoading(true);
        
        // Load blood stock
        const stockData = await hospitalAPI.getBloodStock();
        updateBloodStockTable(stockData);
        
        // Load hospital requests
        const requests = await hospitalAPI.getRequests();
        updateRequestsHistory(requests);
        
    } catch (error) {
        showNotification('Failed to load hospital dashboard', 'error');
    } finally {
        showLoading(false);
    }
}

function updateBloodStockTable(stockData) {
    const tbody = document.querySelector('.inventory table tbody') || 
                  document.querySelector('.inventory table').getElementsByTagName('tbody')[0];
    
    if (!tbody) return;
    
    tbody.innerHTML = '';
    stockData.forEach(stock => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${stock.bloodType}</td>
            <td>${stock.units}</td>
            <td>${stock.location}</td>
        `;
    });
}

// Admin Panel Functions
async function loadAdminPanel() {
    try {
        showLoading(true);
        
        // Load dashboard stats
        const stats = await adminAPI.getDashboardStats();
        updateAdminStats(stats);
        
        // Load blood units
        const bloodUnits = await adminAPI.getBloodUnits();
        updateBloodUnitsTable(bloodUnits);
        
        // Load pending requests
        const requests = await adminAPI.getRequests();
        updateRequestsManagement(requests);
        
    } catch (error) {
        showNotification('Failed to load admin panel', 'error');
    } finally {
        showLoading(false);
    }
}

// Event Handlers
async function handleBloodRequest(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const requestData = {
        hospitalName: formData.get('hospitalName'),
        bloodType: formData.get('bloodType'),
        units: parseInt(formData.get('units')),
        urgency: formData.get('urgency') || 'normal'
    };
    
    try {
        showLoading(true);
        await hospitalAPI.requestBlood(requestData);
        showNotification('Blood request submitted successfully', 'success');
        e.target.reset();
    } catch (error) {
        showNotification('Failed to submit blood request', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleEmergencyAlert(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const alertData = {
        bloodType: formData.get('bloodType'),
        region: formData.get('region'),
        message: formData.get('message') || 'Emergency blood requirement'
    };
    
    try {
        showLoading(true);
        await adminAPI.sendEmergencyAlert(alertData);
        showNotification('Emergency alert sent successfully', 'success');
        e.target.reset();
    } catch (error) {
        showNotification('Failed to send emergency alert', 'error');
    } finally {
        showLoading(false);
    }
}

// Eligibility Checker Modal
function openEligibilityChecker() {
    const modal = createModal('Eligibility Checker', `
        <form id="eligibilityForm">
            <label>Are you feeling healthy today?</label>
            <select name="health" required>
                <option value="">Select</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
            </select>
            
            <label>Have you donated blood in the last 3 months?</label>
            <select name="lastDonation" required>
                <option value="">Select</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
            </select>
            
            <button type="submit">Check Eligibility</button>
        </form>
    `);
    
    document.getElementById('eligibilityForm').addEventListener('submit', checkEligibility);
}

async function checkEligibility(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const eligibilityData = {
        health: formData.get('health'),
        lastDonation: formData.get('lastDonation')
    };
    
    try {
        const result = await donorAPI.checkEligibility(eligibilityData);
        const message = result.eligible ? 
            'You are eligible to donate blood!' : 
            `You are not eligible: ${result.reason}`;
        
        showNotification(message, result.eligible ? 'success' : 'warning');
        closeModal();
    } catch (error) {
        showNotification('Failed to check eligibility', 'error');
    }
}

// Utility Functions
function showLoading(show) {
    const loader = document.getElementById('loader') || createLoader();
    loader.style.display = show ? 'block' : 'none';
}

function createLoader() {
    const loader = document.createElement('div');
    loader.id = 'loader';
    loader.innerHTML = '<div class="spinner"></div>';
    loader.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.5); z-index: 9999; display: none;
        justify-content: center; align-items: center;
    `;
    document.body.appendChild(loader);
    return loader;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; padding: 1rem 2rem;
        border-radius: 5px; z-index: 10000; color: white;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function createModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${title}</h3>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div class="modal-body">${content}</div>
        </div>
    `;
    
    document.body.appendChild(modal);
    return modal;
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function logout() {
    authAPI.logout();
}

// Search functionality
async function searchBloodStock(e) {
    const query = e.target.value;
    try {
        const stockData = await hospitalAPI.getBloodStock({ search: query });
        updateBloodStockTable(stockData);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

// Add smooth page transitions
function navigateTo(url) {
    document.body.style.opacity = '0';
    setTimeout(() => {
        window.location.href = url;
    }, 300);
}

// Animation on page load
window.addEventListener('load', function() {
    document.body.style.opacity = '1';
    document.body.style.transition = 'opacity 0.3s ease-in-out';
});
