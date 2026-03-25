// GET.html - Principal Portal JavaScript

const API_BASE_URL = `http://${window.location.hostname}:5000/api`;
let currentPaperData = null;

// Configure PDF.js worker
if (window.pdfjsLib) {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'lib/pdf.worker.min.js?v=5';
}

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

            // Format times
            const examDate = new Date(data.data.exam_datetime * 1000);
            const blockchainDate = new Date(data.data.blockchain_time * 1000);

            document.getElementById('detailExamDateTime').textContent = examDate.toLocaleString();
            document.getElementById('detailBlockchainTime').textContent = blockchainDate.toLocaleString();

            document.getElementById('detailDocHash').textContent = data.data.document_hash;
            document.getElementById('detailVerified').textContent = data.data.verified ? '✅ Yes' : '❌ No';

            // Show time-lock status
            const timeLockDiv = document.getElementById('timeLockStatus');

            // 🛡️ SECURITY: Use blockchain time for comparison, NOT browser time
            const isUnlocked = data.data.exam_time_reached || (data.data.blockchain_time >= data.data.exam_datetime);

            if (isUnlocked) {
                timeLockDiv.className = 'time-lock-status unlocked';
                timeLockDiv.innerHTML = '✅ Time-Lock: UNLOCKED - You can decrypt this paper';
            } else {
                timeLockDiv.className = 'time-lock-status locked';
                timeLockDiv.innerHTML = `🔒 Time-Lock: LOCKED - Exam time not reached yet<br>
                    <small style="display:block; margin-top:5px; opacity:0.8;">
                        Blockchain Time: ${blockchainDate.toLocaleString()}<br>
                        Unlocks at: ${examDate.toLocaleString()}
                    </small>`;
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
        alert('Please select the encrypted PDF file');
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
            // Store blob for viewing/downloading later
            window.decryptedPdfBlob = await response.blob();
            window.decryptedPdfPaperId = paperId;

            // Show success
            setTimeout(() => {
                document.getElementById('decryptProgress').style.display = 'none';
                document.getElementById('decryptSuccess').style.display = 'block';
            }, 1000);

        } else {
            const data = await response.json();
            const errorMsg = data.error || 'Decryption failed';

            setTimeout(() => {
                document.getElementById('decryptProgress').style.display = 'none';
                document.getElementById('decryptError').style.display = 'block';

                const msgElement = document.getElementById('decryptErrorMessage');

                // Special handling for Clock Warnings
                if (errorMsg.includes('WARNING')) {
                    const parts = errorMsg.split('\n\n');
                    const warningPart = parts[0];
                    const errorPart = parts[1] || "";

                    msgElement.innerHTML = `
                        <div class="clock-warning">
                            <span>🕒</span>
                            <span>${warningPart}</span>
                        </div>
                        <p style="color: #c53030; font-weight: 600;">${errorPart}</p>
                    `;
                } else {
                    msgElement.textContent = errorMsg;
                }
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

// ── PDF Viewing & Downloading ──
async function viewDecryptedPdf() {
    if (!window.decryptedPdfBlob) return;
    document.getElementById('pdfViewerModal').style.display = 'flex';

    const container = document.getElementById('pdfRenderContainer');

    // Reset container but keep loading text
    container.innerHTML = '<div id="pdfLoadingText" style="color: white; font-family: \'DM Sans\', sans-serif;">⏳ Rebuilding PDF Pages...</div>';

    try {
        const arrayBuffer = await window.decryptedPdfBlob.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise;

        container.innerHTML = ''; // clear loading text

        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const viewport = page.getViewport({ scale: 1.5 });

            const canvas = document.createElement('canvas');
            canvas.style.display = 'block';
            canvas.style.margin = '0 auto 20px auto';
            canvas.style.background = 'white';
            canvas.style.boxShadow = '0 4px 15px rgba(0,0,0,0.5)';
            canvas.style.borderRadius = '4px';
            canvas.width = viewport.width;
            canvas.height = viewport.height;

            container.appendChild(canvas);

            const ctx = canvas.getContext('2d');
            await page.render({ canvasContext: ctx, viewport: viewport }).promise;
        }
    } catch (e) {
        console.error("PDF Rendering error:", e);
        container.innerHTML = '<div style="color: #ff4757; text-align: center;">❌ Error displaying PDF inside the app.<br><br>Please click the Download button above instead.</div>';
    }
}

function closePdfViewer() {
    document.getElementById('pdfViewerModal').style.display = 'none';
    document.getElementById('pdfRenderContainer').innerHTML = ''; // Clear memory
}

function downloadDecryptedPdf() {
    if (!window.decryptedPdfBlob || !window.decryptedPdfPaperId) return;

    const filename = `VERIFIED_ExamPaper_${window.decryptedPdfPaperId}.pdf`;

    // Check if running in PyWebView desktop app
    if (window.pywebview) {
        const reader = new FileReader();
        reader.readAsDataURL(window.decryptedPdfBlob);
        reader.onloadend = async function () {
            const base64data = reader.result.split(',')[1];
            try {
                const result = await window.pywebview.api.save_decrypted_paper(filename, base64data);
                if (result.success) {
                    alert(`✅ File saved to: backend/downloads/${filename}`);
                } else {
                    alert(`❌ Failed to save file: ${result.error}`);
                    downloadBlob(window.decryptedPdfBlob, filename); // Fallback
                }
            } catch (e) {
                console.error("Desktop save failed:", e);
                downloadBlob(window.decryptedPdfBlob, filename);
            }
        }
    } else {
        // Browser download fallback
        downloadBlob(window.decryptedPdfBlob, filename);
    }
}

function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const tempLink = document.createElement('a');
    tempLink.href = url;
    tempLink.download = filename;
    document.body.appendChild(tempLink);
    tempLink.click();
    document.body.removeChild(tempLink);
}
