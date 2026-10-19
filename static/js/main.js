// Utility Functions
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function formatCurrency(amount) {
    if (amount === undefined || amount === null) return '';
    return '₹' + parseFloat(amount).toLocaleString('en-IN');
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div class="text-center p-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>`;
    }
}

function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
    }
}

// 1. Sidebar Toggle
function initSidebar() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.ctb-sidebar');
    const overlay = document.querySelector('.ctb-sidebar-overlay');

    if (toggleBtn && sidebar && overlay) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('show');
        });

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        });
    }
}

// 2. Quantity Controls
function initQuantityControls() {
    document.querySelectorAll('.quantity-control').forEach(ctrl => {
        const minus = ctrl.querySelector('.qty-minus');
        const plus = ctrl.querySelector('.qty-plus');
        const input = ctrl.querySelector('.qty-input');
        
        if (minus && plus && input) {
            minus.addEventListener('click', (e) => {
                e.preventDefault();
                let val = parseInt(input.value) || 0;
                if (val > (parseInt(input.min) || 0)) {
                    input.value = val - 1;
                }
            });
            
            plus.addEventListener('click', (e) => {
                e.preventDefault();
                let val = parseInt(input.value) || 0;
                if (!input.max || val < parseInt(input.max)) {
                    input.value = val + 1;
                }
            });
        }
    });
}

// 3. Tags Input
function initTagsInput() {
    document.querySelectorAll('.tags-input-container').forEach(container => {
        const input = container.querySelector('input[type="text"]');
        const hiddenInput = container.querySelector('input[type="hidden"]');
        
        if (input && hiddenInput) {
            let tags = hiddenInput.value ? hiddenInput.value.split(',').map(t => t.trim()).filter(t => t) : [];
            
            function renderTags() {
                container.querySelectorAll('.tag-chip').forEach(el => el.remove());
                tags.forEach((tag, index) => {
                    const chip = document.createElement('div');
                    chip.className = 'tag-chip';
                    chip.innerHTML = `${tag} <span class="remove-tag" data-index="${index}">&times;</span>`;
                    container.insertBefore(chip, input);
                });
                hiddenInput.value = tags.join(',');
                
                container.querySelectorAll('.remove-tag').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const idx = e.target.getAttribute('data-index');
                        tags.splice(idx, 1);
                        renderTags();
                    });
                });
            }
            
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ',') {
                    e.preventDefault();
                    const val = input.value.trim().replace(/,/g, '');
                    if (val && !tags.includes(val)) {
                        tags.push(val);
                        input.value = '';
                        renderTags();
                    }
                } else if (e.key === 'Backspace' && input.value === '' && tags.length > 0) {
                    tags.pop();
                    renderTags();
                }
            });
            
            renderTags();
        }
    });
}

// 4. OTP Input Auto-Focus
function initOtpInputs() {
    const inputs = document.querySelectorAll('.otp-input-box');
    const hiddenInput = document.getElementById('otp-value');
    
    if (inputs.length > 0 && hiddenInput) {
        inputs.forEach((input, index) => {
            input.addEventListener('input', (e) => {
                if (e.target.value.length > 1) {
                    e.target.value = e.target.value.slice(0, 1);
                }
                
                updateHiddenInput();
                
                if (e.target.value !== '' && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
                
                if (index === inputs.length - 1 && e.target.value !== '') {
                    const form = input.closest('form');
                    if (form) {
                        // Optional auto-submit
                        // form.submit();
                    }
                }
            });
            
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                    inputs[index - 1].focus();
                }
            });
            
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').slice(0, inputs.length).split('');
                pastedData.forEach((char, i) => {
                    if (i < inputs.length) {
                        inputs[i].value = char;
                    }
                });
                updateHiddenInput();
                if (pastedData.length > 0) {
                    const nextIndex = Math.min(pastedData.length, inputs.length - 1);
                    inputs[nextIndex].focus();
                }
            });
        });
        
        function updateHiddenInput() {
            let val = '';
            inputs.forEach(input => val += input.value);
            hiddenInput.value = val;
        }
    }
}

// 5. Role Selector
function initRoleSelector() {
    const cards = document.querySelectorAll('.role-selector-card');
    const hiddenInput = document.getElementById('role-input');
    
    if (cards.length > 0 && hiddenInput) {
        cards.forEach(card => {
            card.addEventListener('click', () => {
                cards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                hiddenInput.value = card.getAttribute('data-role');
            });
        });
    }
}

// 6. Worker Search
async function searchWorkers(filters) {
    try {
        const params = new URLSearchParams(filters);
        const resp = await fetch(`/api/workers/search/?${params}`, {
            credentials: 'same-origin',
            headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await resp.json();
        renderWorkerCards(data.results || data);
    } catch (e) {
        console.error('Error searching workers:', e);
        showToast('Error searching workers', 'error');
    }
}

function renderWorkerCards(workers) {
    const container = document.getElementById('worker-results');
    if (!container) return;
    
    if (workers.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No workers found matching your criteria.</div>';
        return;
    }
    
    container.innerHTML = workers.map(worker => `
        <div class="worker-card fade-in-up">
            <div class="worker-avatar">${worker.name.substring(0, 2).toUpperCase()}</div>
            <div class="worker-details flex-grow-1">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="worker-id-badge">${worker.user_id}</div>
                        <h4 class="mb-1">${worker.name} <span class="badge ${worker.verified ? 'badge-verified' : 'badge-pending'}">${worker.verified ? 'Verified' : 'Unverified'}</span></h4>
                        <div class="mb-2">
                            <span class="profession-tag">${worker.profession}</span>
                            <span class="text-muted">${worker.exp} years exp • ${worker.city}</span>
                        </div>
                    </div>
                    <div class="text-end">
                        <div class="fw-bold mb-1">${formatCurrency(worker.rate)}/day</div>
                        <div class="availability-dot available">Available</div>
                    </div>
                </div>
                <div class="mt-2">
                    ${worker.skills.slice(0, 4).map(skill => `<span class="badge bg-light text-dark border me-1">${skill}</span>`).join('')}
                    ${worker.skills.length > 4 ? `<span class="badge bg-light text-dark border me-1">+${worker.skills.length - 4}</span>` : ''}
                </div>
                <div class="mt-3">
                    <button class="btn btn-ctb-primary btn-sm me-2" onclick="requestQuote('${worker.id}')">Request Quote</button>
                    <button class="btn btn-ctb-outline btn-sm" onclick="viewProfile('${worker.id}')">View Profile</button>
                </div>
            </div>
        </div>
    `).join('');
}

// 7. AI Assistant
async function runAIAssist() {
    const input = document.getElementById('ai-input');
    if (!input) return;
    
    const text = input.value.trim();
    if (!text) return;
    
    showLoading('ai-result');
    try {
        const resp = await fetch('/api/projects/ai-assist/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ text })
        });
        const data = await resp.json();
        hideLoading('ai-result');
        
        if (data.structured) {
            fillFormFromAI(data.structured);
            showToast('Form auto-filled based on your description!', 'success');
        } else {
            showToast('Could not understand details. Please fill manually.', 'warning');
        }
    } catch (e) {
        console.error('AI error:', e);
        hideLoading('ai-result');
        showToast('Error processing text', 'error');
    }
}

function fillFormFromAI(structured) {
    if (structured.bedrooms) setQty('id_bedrooms', structured.bedrooms);
    if (structured.bathrooms) setQty('id_bathrooms', structured.bathrooms);
    if (structured.kitchens) setQty('id_kitchens', structured.kitchens);
    if (structured.halls) setQty('id_halls', structured.halls);
    if (structured.budget) {
        const budgetInput = document.getElementById('id_estimated_budget');
        if (budgetInput) budgetInput.value = structured.budget;
    }
    if (structured.project_type) {
        const typeInput = document.getElementById('id_project_type');
        if (typeInput) typeInput.value = structured.project_type;
    }
}

function setQty(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val;
}

// 8. Quotation Actions
async function quotationAction(quotationId, action) {
    if (action === 'accept' && !confirm('Accept this quotation? Other quotes for this milestone will be rejected.')) return;
    if (action === 'reject' && !confirm('Reject this quotation?')) return;
    
    try {
        const resp = await fetch(`/api/quotations/${quotationId}/action/`, {
            method: 'PATCH',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ action })
        });
        
        if (resp.ok) {
            showToast(`Quote ${action}ed successfully!`, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(`Failed to ${action} quote`, 'error');
        }
    } catch (e) {
        showToast('Network error', 'error');
    }
}

// 9. Roadmap Loading
async function loadRoadmap(projectId) {
    const container = document.getElementById('roadmap-container');
    if (!container) return;
    
    container.innerHTML = '<div class="text-center"><div class="spinner-border text-primary"></div></div>';
    
    try {
        const resp = await fetch(`/api/projects/${projectId}/milestones/`, { credentials: 'same-origin' });
        const data = await resp.json();
        renderRoadmap(data, container);
    } catch (e) {
        container.innerHTML = '<div class="alert alert-danger">Error loading roadmap</div>';
    }
}

function renderRoadmap(milestones, container) {
    container.innerHTML = `<div class="ctb-roadmap">
        ${milestones.map((m, i) => `
            <div class="roadmap-item">
                <div class="roadmap-dot ${m.status.toLowerCase().replace('_', '-')}"></div>
                ${i < milestones.length - 1 ? '<div class="roadmap-connector"></div>' : ''}
                <div class="ms-4">
                    <h5 class="mb-1">${m.name} <span class="badge badge-${m.status.toLowerCase().replace('_', '-')}">${m.status}</span></h5>
                    ${m.assigned_worker ? `<p class="mb-1 text-muted text-sm">Assigned to: ${m.assigned_worker.name}</p>` : ''}
                    ${m.status === 'IN_PROGRESS' ? `
                        <div class="ctb-progress mt-2 mb-1">
                            <div class="ctb-progress-bar" style="width: ${m.progress}%"></div>
                        </div>
                        <small class="text-muted">${m.progress}% complete</small>
                    ` : ''}
                </div>
            </div>
        `).join('')}
    </div>`;
}

// 10. Progress Update
async function updateMilestoneProgress(milestoneId, progressPercent, notes) {
    try {
        const resp = await fetch(`/api/milestones/${milestoneId}/progress/`, {
            method: 'PATCH',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
            body: JSON.stringify({ progress: progressPercent, notes })
        });
        
        if (resp.ok) {
            showToast('Progress updated', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Failed to update progress', 'error');
        }
    } catch (e) {
        showToast('Network error', 'error');
    }
}

// 15. Filter Debounce
let filterTimeout;
function initFilters() {
    const filterForm = document.getElementById('worker-filters');
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                clearTimeout(filterTimeout);
                filterTimeout = setTimeout(() => {
                    const formData = new FormData(filterForm);
                    const filters = Object.fromEntries(formData.entries());
                    searchWorkers(filters);
                }, 300);
            });
        });
        
        // Initial search
        const formData = new FormData(filterForm);
        searchWorkers(Object.fromEntries(formData.entries()));
    }
}

// 16. Compliance Acknowledgement
function initCompliance() {
    const checks = document.querySelectorAll('.compliance-check');
    const btn = document.getElementById('btn-acknowledge-compliance');
    
    if (checks.length > 0 && btn) {
        function checkAll() {
            let allChecked = true;
            checks.forEach(c => {
                if (!c.checked) allChecked = false;
            });
            btn.disabled = !allChecked;
        }
        
        checks.forEach(c => {
            c.addEventListener('change', checkAll);
        });
        
        checkAll();
    }
}

// 17. initAll
function initAll() {
    initSidebar();
    initQuantityControls();
    initTagsInput();
    initOtpInputs();
    initRoleSelector();
    initFilters();
    initCompliance();
    
    const aiBtn = document.getElementById('btn-ai-assist');
    if (aiBtn) aiBtn.addEventListener('click', runAIAssist);
}

document.addEventListener('DOMContentLoaded', initAll);
