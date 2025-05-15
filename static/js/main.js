document.addEventListener('DOMContentLoaded', function() {
    // File Upload Preview
    const resumeInput = document.getElementById('resumeFile');
    const fileLabel = document.querySelector('.custom-file-label');
    const dropZone = document.getElementById('dropZone');
    const submitButton = document.getElementById('submitBtn');
    const uploadForm = document.getElementById('uploadForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    // Set up file input change handler
    if (resumeInput) {
        resumeInput.addEventListener('change', function() {
            updateFileLabel(this);
            validateForm();
        });
    }
    
    // Set up job description input change handler
    const jobDescInput = document.getElementById('jobDescription');
    if (jobDescInput) {
        jobDescInput.addEventListener('input', validateForm);
    }
    
    // Validate form to enable/disable submit button
    function validateForm() {
        if (submitButton) {
            const fileValid = resumeInput && resumeInput.files.length > 0;
            submitButton.disabled = !fileValid;
        }
    }
    
    // Show selected filename
    function updateFileLabel(input) {
        if (input.files && input.files.length > 0) {
            const fileName = input.files[0].name;
            
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
            
            // Check file type
            const fileExt = fileName.split('.').pop().toLowerCase();
            const validTypes = ['pdf', 'docx', 'txt'];
            
            if (!validTypes.includes(fileExt)) {
                alert('Please upload a PDF, DOCX, or TXT file');
                input.value = '';
                fileLabel.textContent = 'Choose file...';
                validateForm();
            }
        } else if (fileLabel) {
            fileLabel.textContent = 'Choose file...';
        }
    }
    
    // Set up drag and drop functionality
    if (dropZone) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropZone.classList.add('highlight');
        }
        
        function unhighlight() {
            dropZone.classList.remove('highlight');
        }
        
        // Handle dropped files
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                resumeInput.files = files;
                updateFileLabel(resumeInput);
                validateForm();
            }
        }
    }
    
    // Handle form submission with loading state
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            if (loadingSpinner) {
                loadingSpinner.classList.remove('d-none');
            }
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Toggle sections in results page
    const toggleButtons = document.querySelectorAll('.toggle-section');
    if (toggleButtons) {
        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    if (targetElement.classList.contains('d-none')) {
                        targetElement.classList.remove('d-none');
                        this.innerHTML = '<i class="fas fa-chevron-up"></i>';
                    } else {
                        targetElement.classList.add('d-none');
                        this.innerHTML = '<i class="fas fa-chevron-down"></i>';
                    }
                }
            });
        });
    }
});
