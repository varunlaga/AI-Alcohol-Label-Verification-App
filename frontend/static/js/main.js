/* Global Variables and File Upload Handling */
let selectedFile = null;

// Get DOM elements
const fileInput = document.getElementById('labelImage');
const fileUploadArea = document.getElementById('fileUploadArea');
const uploadTitle = document.getElementById('uploadTitle');
const imagePreviewSection = document.getElementById('imagePreviewSection');
const previewImage = document.getElementById('previewImage');
const previewInfo = document.getElementById('previewInfo');
const removeImageBtn = document.getElementById('removeImageBtn');

// Click to upload
fileUploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File input change event
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

// Drag and drop functionality
fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.classList.add('drag-over');
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.classList.remove('drag-over');
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    if (file && isValidImageFile(file)) {
        // Set the file to the input element
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        
        handleFileSelect(file);
    } else {
        alert('Please upload a valid image file (JPEG or PNG)');
    }
});

// Handle file selection
function handleFileSelect(file) {
    if (!isValidImageFile(file)) {
        alert('Please upload a valid image file (JPEG or PNG)');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
    }
    
    selectedFile = file;
    displayImagePreview(file);
}

// Validate image file
function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    return validTypes.includes(file.type);
}

// Display image preview
function displayImagePreview(file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        
        // Update preview info
        const fileSizeKB = (file.size / 1024).toFixed(2);
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        const sizeText = file.size < 1024 * 1024 
            ? `${fileSizeKB} KB` 
            : `${fileSizeMB} MB`;
        
        previewInfo.innerHTML = `
            <strong>${file.name}</strong> • ${sizeText} • ${file.type.split('/')[1].toUpperCase()}
        `;
        
        // Show preview section
        imagePreviewSection.classList.remove('hidden');
        
        // Update upload area text
        uploadTitle.textContent = 'Image uploaded successfully';
    };
    
    reader.readAsDataURL(file);
}

removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    removeImage();
});

// Remove image
function removeImage() {
    selectedFile = null;
    fileInput.value = '';
    imagePreviewSection.classList.add('hidden');
    previewImage.src = '';
    uploadTitle.textContent = 'Click to upload label image';
}

// Form Submission
const form = document.getElementById('labelVerificationForm');
const submitButton = document.getElementById('submitButton');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const formSection = document.querySelector('.form-section');
const labelVerificationForm = document.getElementById('labelVerificationForm');

form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) {
        return;
    }
    
    // Show loading state
    showLoadingState();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('brandName', document.getElementById('brandName').value.trim());
    formData.append('productType', document.getElementById('productType').value.trim());
    formData.append('alcoholContent', document.getElementById('alcoholContent').value.trim());
    formData.append('netContents', document.getElementById('netContents').value.trim());
    formData.append('labelImage', fileInput.files[0]);
    
    try {
        // Send request to backend API
        const response = await fetch('/api/verify', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        // Hide loading state
        hideLoadingState();
        
        if (response.ok) {
            // Display results
            displayResults(result);
            
            // Scroll to results
            setTimeout(() => {
                resultsSection.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
        } else {
            // Display error
            displayError(result.error || 'An error occurred while processing your request');
        }
        
    } catch (error) {
        console.error('Error:', error);
        hideLoadingState();
        displayError('Network error: Unable to connect to the server. Please try again.');
    }
});

// Validate form
function validateForm() {
    const brandName = document.getElementById('brandName').value.trim();
    const productType = document.getElementById('productType').value.trim();
    const alcoholContent = document.getElementById('alcoholContent').value.trim();
    
    if (!brandName) {
        alert('Please enter the brand name');
        return false;
    }
    
    if (!productType) {
        alert('Please enter the product class/type');
        return false;
    }
    
    if (!alcoholContent) {
        alert('Please enter the alcohol content');
        return false;
    }
    
    const abv = parseFloat(alcoholContent);
    if (isNaN(abv) || abv < 0 || abv > 100) {
        alert('Please enter a valid alcohol content between 0 and 100');
        return false;
    }
    
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please upload a label image');
        return false;
    }
    
    return true;
}

// Show loading state
function showLoadingState() {
    submitButton.disabled = true;
    submitButton.style.opacity = '0.6';
    loadingIndicator.classList.remove('hidden');
    resultsSection.classList.add('hidden');
}

// Hide loading state
function hideLoadingState() {
    submitButton.disabled = false;
    submitButton.style.opacity = '1';
    loadingIndicator.classList.add('hidden');
}

// Display results
function displayResults(result) {
    resultsSection.classList.remove('hidden');
    
    // Handle error case
    if (result.error) {
        displayError(result.error);
        return;
    }
    
    // Check if all verifications passed
    const allMatch = result.verifications && 
                     result.verifications.every(v => v.status === 'match');
    
    let html = '';
    
    // Overall status banner
    if (allMatch) {
        html += `
            <div class="result-banner result-success">
                <div class="result-icon">✅</div>
                <div class="result-message">
                    <h3>Label Verification Successful</h3>
                    <p>The label matches the form data. All required information is consistent.</p>
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="result-banner result-failure">
                <div class="result-icon">❌</div>
                <div class="result-message">
                    <h3>Label Verification Failed</h3>
                    <p>The label does not match the form. Please review the discrepancies below.</p>
                </div>
            </div>
        `;
    }
    
    // Detailed verification results
    html += `
        <div class="verification-details">
            <h3>📋 Detailed Verification Results</h3>
    `;
    
    if (result.verifications && result.verifications.length > 0) {
        result.verifications.forEach(item => {
            const statusClass = getStatusClass(item.status);
            const statusIcon = getStatusIcon(item.status);
            
            html += `
                <div class="verification-item ${statusClass}">
                    <div class="item-icon">${statusIcon}</div>
                    <div class="item-content">
                        <div class="item-field">${item.field}</div>
                        <div class="item-message">${item.message}</div>
                    </div>
                </div>
            `;
        });
    }
    
    html += `</div>`;
    
    // Show extracted text for transparency
    if (result.extracted_text) {
        const textPreview = result.extracted_text.length > 500 
            ? result.extracted_text.substring(0, 500) + '...'
            : result.extracted_text;
        
        html += `
            <div class="extracted-text-section">
                <h3>Extracted Text from Label</h3>
                <div class="extracted-text-content">
                    <pre>${escapeHtml(textPreview)}</pre>
                </div>
                <p class="text-note">This is the text extracted from your label image using OCR.</p>
            </div>
        `;
    }
    
    resultsContent.innerHTML = html;
}

// Display error message
function displayError(message) {
    resultsSection.classList.remove('hidden');
    
    resultsContent.innerHTML = `
        <div class="result-banner result-error">
            <div class="result-icon">⚠️</div>
            <div class="result-message">
                <h3>Error</h3>
                <p>${escapeHtml(message)}</p>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }, 100);
}

// Get status icon
function getStatusIcon(status) {
    const icons = {
        'match': '✓',
        'mismatch': '✗',
        'not_found': '⚠',
        'warning': '⚠'
    };
    return icons[status] || '•';
}

// Get status class
function getStatusClass(status) {
    const classes = {
        'match': 'status-match',
        'mismatch': 'status-mismatch',
        'not_found': 'status-warning',
        'warning': 'status-warning'
    };
    return classes[status] || '';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Edit form or try new image
function editForm() {
    // Hide results and show form
    resultsSection.classList.add('hidden');
    formSection.classList.remove('hidden');

    // Scroll to the top of the form
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    
    // Optional - hide error messages if they were visible
    if (typeof hideMessage === 'function') {
        hideMessage(); 
    }
}

// Reset Form 
function resetForm() {
    // Clear all text inputs
    if (labelVerificationForm) {
        labelVerificationForm.reset();
    }
    
    // Removes image
    if (typeof removeImage === 'function') {
        removeImage(); 
    }
    
    // Switch views and scroll to top
    editForm();
}

// Inject additional styles for results display
const style = document.createElement('style');
style.textContent = `
    .result-banner {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 25px;
        border-radius: 8px;
        margin-bottom: 30px;
    }
    
    .result-success {
        background: #d4edda;
        border: 2px solid #c3e6cb;
    }
    
    .result-failure {
        background: #f8d7da;
        border: 2px solid #f5c6cb;
    }
    
    .result-error {
        background: #fff3cd;
        border: 2px solid #ffeaa7;
    }
    
    .result-icon {
        font-size: 3rem;
        flex-shrink: 0;
    }
    
    .result-message h3 {
        font-size: 1.5rem;
        margin-bottom: 8px;
        color: #2d3748;
    }
    
    .result-message p {
        font-size: 1rem;
        color: #4a5568;
        margin: 0;
    }
    
    .verification-details {
        background: #f7fafc;
        border-radius: 8px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    .verification-details h3 {
        font-size: 1.25rem;
        color: #2d3748;
        margin-bottom: 20px;
        font-weight: 600;
    }
    
    .verification-item {
        display: flex;
        align-items: flex-start;
        gap: 15px;
        padding: 15px;
        margin-bottom: 12px;
        background: white;
        border-radius: 6px;
        border-left: 4px solid #cbd5e0;
    }
    
    .verification-item:last-child {
        margin-bottom: 0;
    }
    
    .verification-item.status-match {
        border-left-color: #48bb78;
    }
    
    .verification-item.status-mismatch {
        border-left-color: #f56565;
    }
    
    .verification-item.status-warning {
        border-left-color: #ed8936;
    }
    
    .item-icon {
        font-size: 1.5rem;
        font-weight: bold;
        flex-shrink: 0;
        width: 30px;
        text-align: center;
    }
    
    .status-match .item-icon {
        color: #48bb78;
    }
    
    .status-mismatch .item-icon {
        color: #f56565;
    }
    
    .status-warning .item-icon {
        color: #ed8936;
    }
    
    .item-content {
        flex: 1;
    }
    
    .item-field {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 5px;
        font-size: 1rem;
    }
    
    .item-message {
        color: #4a5568;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .extracted-text-section {
        background: #f7fafc;
        border-radius: 8px;
        padding: 25px;
    }
    
    .extracted-text-section h3 {
        font-size: 1.25rem;
        color: #2d3748;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    .extracted-text-content {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 15px;
        max-height: 250px;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    
    .extracted-text-content pre {
        margin: 0;
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
        line-height: 1.6;
        color: #2d3748;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .text-note {
        font-size: 0.875rem;
        color: #718096;
        margin: 0;
        font-style: italic;
    }
`;

document.head.appendChild(style);
