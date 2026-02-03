// GET.html - Principal Portal JavaScript

const API_BASE_URL = 'http://localhost:5000/api';
let currentPaperData = null;

// Check authentication on page load
window.addEventListener('DOMContentLoaded', () => {
    const sessionToken = localStorage.getItem('session_token');
    const userRole = localStorage.getItem('user_role');
    const userName = localStorage.getItem('user_name');

    if (!sessionToken || userRole !== 'principal') {
        window.location.href = 'login.html';
        return;
    }

    document.getElementById('userName').textContent = userName;
});

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    if (tabName === 'verify') {
        document.getElementById('verifyTab').classList.add('active');
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
    } else {
        document.getElementById('decryptTab').classList.add('active');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
    }
}

async function handleVerify(event) {
    event.preventDefault();

    const paperId = document.getElementById('paper_id_verify').value;

    try {
        const sessionToken = localStorage.getItem('session_token');

        const response = await fetch(`${API_BASE_URL}/principal/verify-paper/${paperId}`, {
            method: 'GET',
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            currentPaperData = data.data;

            // Display paper details
            document.getElementById('detailPaperId').textContent = data.data.paper_id;
            document.getElementById('detailCollegeId').textContent = data.data.college_id;
            document.getElementById('detailSubjectCode').textContent = data.data.subject_code;

            // Format exam datetime
            const examDate = new Date(data.data.exam_datetime * 1000);
            document.getElementById('detailExamDateTime').textContent = examDate.toLocaleString();

            document.getElementById('detailDocHash').textContent = data.data.document_hash;
            document.getElementById('detailVerified').textContent = data.data.verified ? '✅ Yes' : '❌ No';

            // Show time-lock status
            const timeLockDiv = document.getElementById('timeLockStatus');
            if (data.data.exam_time_reached) {
                timeLockDiv.className = 'time-lock-status unlocked';
                timeLockDiv.innerHTML = '✅ Time-Lock: UNLOCKED - You can decrypt this paper';
            } else {
                timeLockDiv.className = 'time-lock-status locked';
                const timeRemaining = examDate - new Date();
                timeLockDiv.innerHTML = `🔒 Time-Lock: LOCKED - Exam time not reached yet<br>Access available at: ${examDate.toLocaleString()}`;
            }

            // Show paper details section
            document.getElementById('paperDetails').style.display = 'block';

            // Auto-fill paper ID in decrypt tab
            document.getElementById('paper_id_decrypt').value = paperId;
            document.getElementById('college_id_decrypt').value = data.data.college_id;

        } else {
            alert('Error: ' + data.error);
        }

    } catch (error) {
        alert('Error connecting to server. Make sure the backend is running.');
        console.error('Verify error:', error);
    }
}

async function handleDecrypt(event) {
    event.preventDefault();

    const paperId = document.getElementById('paper_id_decrypt').value;
    const packageFile = document.getElementById('package_file').files[0];
    const collegeId = document.getElementById('college_id_decrypt').value;

    if (!packageFile) {
        alert('Please select the encrypted package file');
        return;
    }

    // Hide form and show progress
    document.getElementById('decryptForm').style.display = 'none';
    document.getElementById('decryptProgress').style.display = 'block';
    document.getElementById('decryptSuccess').style.display = 'none';
    document.getElementById('decryptError').style.display = 'none';

    // Simulate progress steps
    const steps = ['decrypt-step1', 'decrypt-step2', 'decrypt-step3', 'decrypt-step4', 'decrypt-step5'];
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

        const formData = new FormData();
        formData.append('paper_id', paperId);
        formData.append('package_file', packageFile);
        formData.append('college_id', collegeId);

        const response = await fetch(`${API_BASE_URL}/principal/decrypt-paper`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken
            },
            body: formData
        });

        clearInterval(progressInterval);

        // Mark all steps as completed
        steps.forEach(stepId => {
            const stepElement = document.getElementById(stepId);
            stepElement.classList.remove('active');
            stepElement.classList.add('completed');
            stepElement.querySelector('.step-icon').textContent = '✓';
        });

        if (response.ok) {
            // Download the PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `exam_paper_${paperId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Show success
            setTimeout(() => {
                document.getElementById('decryptProgress').style.display = 'none';
                document.getElementById('decryptSuccess').style.display = 'block';
            }, 1000);

        } else {
            const data = await response.json();

            setTimeout(() => {
                document.getElementById('decryptProgress').style.display = 'none';
                document.getElementById('decryptError').style.display = 'block';
                document.getElementById('decryptErrorMessage').textContent = data.error || 'Decryption failed';
            }, 1000);
        }

    } catch (error) {
        clearInterval(progressInterval);
        document.getElementById('decryptProgress').style.display = 'none';
        document.getElementById('decryptError').style.display = 'block';
        document.getElementById('decryptErrorMessage').textContent =
            'Error connecting to server. Make sure the backend is running.';
        console.error('Decrypt error:', error);
    }
}

function resetDecrypt() {
    document.getElementById('decryptForm').reset();
    document.getElementById('decryptForm').style.display = 'block';
    document.getElementById('decryptProgress').style.display = 'none';
    document.getElementById('decryptSuccess').style.display = 'none';
    document.getElementById('decryptError').style.display = 'none';

    // Reset progress steps
    const steps = ['decrypt-step1', 'decrypt-step2', 'decrypt-step3', 'decrypt-step4', 'decrypt-step5'];
    steps.forEach(stepId => {
        const stepElement = document.getElementById(stepId);
        stepElement.classList.remove('active', 'completed');
        stepElement.querySelector('.step-icon').textContent = '⏳';
    });
}
