// SET.html - Admin Portal JavaScript

const API_BASE_URL = 'http://localhost:5000/api';

// Check authentication on page load
window.addEventListener('DOMContentLoaded', () => {
    const sessionToken = localStorage.getItem('session_token');
    const userRole = localStorage.getItem('user_role');
    const userName = localStorage.getItem('user_name');

    if (!sessionToken || userRole !== 'admin') {
        window.location.href = 'login.html';
        return;
    }

    document.getElementById('userName').textContent = userName;
});

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

async function handleUpload(event) {
    event.preventDefault();

    const formData = new FormData();
    const pdfFile = document.getElementById('pdf_file').files[0];

    if (!pdfFile) {
        alert('Please select a PDF file');
        return;
    }

    formData.append('pdf_file', pdfFile);
    formData.append('college_id', document.getElementById('college_id').value);
    formData.append('subject_code', document.getElementById('subject_code').value);
    formData.append('exam_datetime', document.getElementById('exam_datetime').value);
    formData.append('principal_email', document.getElementById('principal_email').value);

    // Hide form and show progress
    document.getElementById('uploadForm').style.display = 'none';
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';

    // Simulate progress steps
    const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
    let currentStep = 0;

    const progressInterval = setInterval(() => {
        if (currentStep < steps.length) {
            const stepElement = document.getElementById(steps[currentStep]);
            stepElement.classList.add('active');
            currentStep++;
        }
    }, 500);

    try {
        const sessionToken = localStorage.getItem('session_token');

        const response = await fetch(`${API_BASE_URL}/admin/store-paper`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken
            },
            body: formData
        });

        const data = await response.json();

        clearInterval(progressInterval);

        // Mark all steps as completed
        steps.forEach(stepId => {
            const stepElement = document.getElementById(stepId);
            stepElement.classList.remove('active');
            stepElement.classList.add('completed');
            stepElement.querySelector('.step-icon').textContent = '✓';
        });

        setTimeout(() => {
            if (data.success) {
                // Show success result
                document.getElementById('progressSection').style.display = 'none';
                document.getElementById('resultSection').style.display = 'block';

                // Populate result details
                document.getElementById('paperId').textContent = data.data.paper_id;
                document.getElementById('txHash').textContent = data.data.transaction_hash;
                document.getElementById('docHash').textContent = data.data.document_hash;
                document.getElementById('resultCollegeId').textContent = data.data.college_id;
                document.getElementById('resultSubjectCode').textContent = data.data.subject_code;
                document.getElementById('resultExamDateTime').textContent = data.data.exam_datetime;
                document.getElementById('emailStatus').textContent = data.data.email_sent ? '✅ Sent' : '⚠️ Failed';
            } else {
                // Show error
                document.getElementById('progressSection').style.display = 'none';
                document.getElementById('errorSection').style.display = 'block';
                document.getElementById('errorMessage').textContent = data.error;
            }
        }, 1000);

    } catch (error) {
        clearInterval(progressInterval);
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'block';
        document.getElementById('errorMessage').textContent =
            'Error connecting to server. Make sure the backend is running and Ganache is active.';
        console.error('Upload error:', error);
    }
}

function resetForm() {
    document.getElementById('uploadForm').reset();
    document.getElementById('uploadForm').style.display = 'block';
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';

    // Reset progress steps
    const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
    steps.forEach(stepId => {
        const stepElement = document.getElementById(stepId);
        stepElement.classList.remove('active', 'completed');
        stepElement.querySelector('.step-icon').textContent = '⏳';
    });
}
