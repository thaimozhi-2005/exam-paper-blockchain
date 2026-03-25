const API_BASE_URL = `http://${window.location.hostname}:5000/api`;

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

    // Fetch paper count on load (badge only, list stays collapsed)
    fetchPaperCount();
});

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

// ============= PAPER COUNT (badge only) =============

async function fetchPaperCount() {
    try {
        const sessionToken = localStorage.getItem('session_token');
        const response = await fetch(`${API_BASE_URL}/admin/papers`, {
            method: 'GET',
            headers: { 'Authorization': sessionToken }
        });
        const data = await response.json();
        if (data.success) {
            document.getElementById('totalPapers').textContent = data.data.total;
        }
    } catch (e) {
        console.log('Could not fetch paper count:', e);
    }
}

// ============= PAPER LIST TOGGLE =============

function togglePaperList() {
    const wrap = document.getElementById('paperListWrap');
    const btn = document.getElementById('papersToggleBtn');
    const refreshBtn = document.getElementById('refreshBtn');

    btn.classList.toggle('open');
    wrap.classList.toggle('open');

    if (wrap.classList.contains('open')) {
        refreshBtn.style.display = 'block';
        loadPaperList();
    } else {
        refreshBtn.style.display = 'none';
    }
}

// ============= PDF EDITOR LOGIC =============
// Multi-page scrollable PDF editor with Fabric.js overlay per page

let currentPdfBytes = null;
let editedPdfBytes = null;
let isTextMode = false;
let pageCanvases = [];      // Array of { fabricCanvas, bgImage, pageNum }
let activePageIndex = 0;    // Currently focused page
let totalPages = 0;
const PDF_SCALE = 1.5;
// Robust PDF-Lib extraction
const { PDFDocument, rgb } = (typeof PDFLib !== 'undefined') ? PDFLib : { PDFDocument: null, rgb: null };

// Configure PDF.js worker (local file — works on port 8000 desktop app)
pdfjsLib.GlobalWorkerOptions.workerSrc = 'lib/pdf.worker.min.js?v=5';

function setUploadMode(mode, btnElement) {
    // Update active button styles
    const buttons = document.querySelectorAll('.upload-opt');
    buttons.forEach(btn => btn.classList.remove('active'));
    btnElement.classList.add('active');

    // Update hidden input
    document.getElementById('uploadOptionInput').value = mode;

    const isScratch = (mode === 'scratch');
    const fileGroup = document.getElementById('fileUploadGroup');
    const previewBtn = document.getElementById('previewBtn');

    if (isScratch) {
        fileGroup.style.display = 'none';
        document.getElementById('pdf_file').required = false;
        previewBtn.innerHTML = '✍️ Write & Preview Paper';
    } else {
        fileGroup.style.display = 'block';
        document.getElementById('pdf_file').required = true;
        previewBtn.innerHTML = '👁️ Preview & Edit PDF';
    }

    editedPdfBytes = null;
    currentPdfBytes = null;
    isTextMode = false;
}

// ── Open Editor ──
async function openPdfEditor() {
    const isScratch = document.getElementById('uploadOptionInput').value === 'scratch';

    if (isScratch) {
        openBlankTextEditor();
        return;
    }

    const fileInput = document.getElementById('pdf_file');
    if (!fileInput.files.length) {
        alert('Please select a PDF or TXT file first');
        return;
    }

    const file = fileInput.files[0];
    const fileName = file.name.toLowerCase();

    if (fileName.endsWith('.txt')) {
        openTextEditor(file);
        return;
    }

    if (!fileName.endsWith('.pdf')) {
        alert('Only PDF and TXT files are supported for preview.');
        return;
    }

    currentPdfBytes = await file.arrayBuffer();
    editedPdfBytes = null;
    isTextMode = false;

    // Show editor modal
    document.getElementById('pdfModal').style.display = 'block';
    document.getElementById('editorLoadingOverlay').style.display = 'flex';
    document.getElementById('editorStatusText').textContent = '⏳ Loading PDF...';

    // Attach event listeners
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('paste', handlePaste);

    // Render all pages
    await renderAllPages(currentPdfBytes);
}

// ── Text Editor Logic ──
function openTextEditor(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('textEditorArea').value = e.target.result;
        document.getElementById('textEditorModal').style.display = 'block';
        isTextMode = true;
        editedPdfBytes = null;
    };
    reader.readAsText(file);
}

function openBlankTextEditor() {
    document.getElementById('textEditorArea').value = '';
    document.getElementById('textEditorModal').style.display = 'block';
    isTextMode = true;
    editedPdfBytes = null;
}

function closeTextEditor() {
    document.getElementById('textEditorModal').style.display = 'none';
    document.getElementById('textEditorArea').value = '';
    isTextMode = false;
}

async function saveTextEdits() {
    const textContent = document.getElementById('textEditorArea').value;
    if (!textContent.trim()) {
        alert('Cannot save an empty paper.');
        return;
    }

    try {
        // Robust jsPDF initialization (handles UMD and global patterns)
        let jsPDFLib;
        if (window.jspdf && window.jspdf.jsPDF) {
            jsPDFLib = window.jspdf.jsPDF;
        } else if (window.jsPDF) {
            jsPDFLib = window.jsPDF;
        } else {
            throw new Error("jsPDF library not found. Please check if jspdf.umd.min.js is loaded.");
        }

        const doc = new jsPDFLib();
        const splitText = doc.splitTextToSize(textContent, 180);

        let cursorY = 20;
        for (let i = 0; i < splitText.length; i++) {
            doc.text(15, cursorY, splitText[i]);
            cursorY += 7;
            if (cursorY >= 280 && i < splitText.length - 1) {
                doc.addPage();
                cursorY = 20;
            }
        }

        const pdfArrayBuffer = doc.output('arraybuffer');
        editedPdfBytes = new Uint8Array(pdfArrayBuffer);

        document.getElementById('textEditorStatusText').textContent = '✅ PDF Generated & Saved!';
        setTimeout(() => {
            alert('✅ Text converted to PDF and saved! Ready for blockchain storage.');
            closeTextEditor();
            document.getElementById('textEditorStatusText').textContent = 'Editing Plain Text';
        }, 500);

    } catch (err) {
        console.error('Text to PDF error:', err);
        document.getElementById('textEditorStatusText').textContent = '❌ Conversion Failed';
        alert('Failed to convert text to PDF: ' + err.message);
    }
}

// ── Close Editor ──
function closePdfEditor() {
    document.getElementById('pdfModal').style.display = 'none';
    window.removeEventListener('keydown', handleKeyDown);
    window.removeEventListener('paste', handlePaste);

    // Dispose all Fabric canvases
    for (const pc of pageCanvases) {
        if (pc.fabricCanvas) pc.fabricCanvas.dispose();
    }
    pageCanvases = [];
    activePageIndex = 0;
    totalPages = 0;

    // Clear workspace HTML
    const workspace = document.getElementById('pdfWorkspace');
    workspace.innerHTML = '';
}

// ── Core: Render ALL pages ──
async function renderAllPages(pdfBytes) {
    try {
        // Dispose any old canvases
        for (const pc of pageCanvases) {
            if (pc.fabricCanvas) pc.fabricCanvas.dispose();
        }
        pageCanvases = [];

        // Clear workspace
        const workspace = document.getElementById('pdfWorkspace');
        workspace.innerHTML = '';

        // Load PDF
        const uint8 = new Uint8Array(pdfBytes);
        const pdf = await pdfjsLib.getDocument({ data: uint8 }).promise;
        totalPages = pdf.numPages;
        console.log('[Editor] PDF loaded, total pages:', totalPages);

        // Render each page
        for (let i = 1; i <= totalPages; i++) {
            document.getElementById('editorStatusText').textContent =
                `⏳ Rendering page ${i} of ${totalPages}...`;

            const page = await pdf.getPage(i);
            const viewport = page.getViewport({ scale: PDF_SCALE });

            // Create page container
            const pageDiv = document.createElement('div');
            pageDiv.className = 'pdf-page-container';
            pageDiv.id = `pageContainer_${i}`;
            pageDiv.style.cssText = `
                width: ${viewport.width}px;
                height: ${viewport.height}px;
                position: relative;
                margin-bottom: 30px;
                background: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);
            `;

            // Page number label
            const pageLabel = document.createElement('div');
            pageLabel.textContent = `— Page ${i} of ${totalPages} —`;
            pageLabel.style.cssText = 'text-align:center; padding:6px 0; font-size:11px; color:#888; font-weight:600; letter-spacing:1px;';
            workspace.appendChild(pageLabel);

            // Create canvas element for Fabric
            const canvasEl = document.createElement('canvas');
            canvasEl.id = `fabricPage_${i}`;
            canvasEl.width = viewport.width;
            canvasEl.height = viewport.height;
            pageDiv.appendChild(canvasEl);

            workspace.appendChild(pageDiv);

            // Render PDF page to offscreen canvas
            const offscreen = document.createElement('canvas');
            offscreen.width = viewport.width;
            offscreen.height = viewport.height;
            const ctx = offscreen.getContext('2d');
            await page.render({ canvasContext: ctx, viewport }).promise;

            // Initialize Fabric canvas on this page
            const fc = new fabric.Canvas(`fabricPage_${i}`, {
                width: viewport.width,
                height: viewport.height,
                backgroundColor: '#fff'
            });

            // Add PDF page as background image (locked, non-selectable)
            const bgImg = new fabric.Image(offscreen, {
                left: 0, top: 0,
                selectable: false,
                evented: false,
                hasControls: false,
                hasBorders: false,
                lockMovementX: true,
                lockMovementY: true
            });

            fc.add(bgImg);
            fc.sendToBack(bgImg);
            fc.renderAll();

            // Track which page is active when user clicks on it
            const pageIndex = i - 1;
            fc.on('mouse:down', function () {
                activePageIndex = pageIndex;
                updatePageStatus();
            });

            // Store reference
            pageCanvases.push({
                fabricCanvas: fc,
                bgImage: bgImg,
                pageNum: i
            });

            console.log(`[Editor] Page ${i} rendered`);
        }

        // Update status — done
        updatePageStatus();
        document.getElementById('editorLoadingOverlay').style.display = 'none';

    } catch (err) {
        console.error('[Editor] FATAL:', err);
        document.getElementById('editorStatusText').textContent = 'Error: ' + err.message;
        document.getElementById('editorLoadingOverlay').style.display = 'none';
        alert('Failed to load PDF: ' + err.message);
    }
}

function updatePageStatus() {
    document.getElementById('editorStatusText').textContent =
        `Ready — Page ${activePageIndex + 1} of ${totalPages}`;

    // Update page counter in status bar
    const pageSpan = document.querySelector('.office-status-bar span:first-child');
    if (pageSpan) pageSpan.textContent = `Page: ${activePageIndex + 1} of ${totalPages}`;
}

// ── Get the active Fabric canvas ──
function getActiveCanvas() {
    if (pageCanvases.length === 0) return null;
    return pageCanvases[activePageIndex].fabricCanvas;
}

// ── Tool: Add Text ──
function addTextToCanvas() {
    const fc = getActiveCanvas();
    if (!fc) return;

    const textStr = document.getElementById('add_text_input').value || 'New text';

    const text = new fabric.Textbox(textStr, {
        left: 100, top: 100,
        width: 250,
        fontSize: 22,
        fontFamily: 'Arial',
        fill: '#000000',
        cornerColor: '#2b579a',
        cornerSize: 8,
        transparentCorners: false,
        borderColor: '#2b579a',
        editingBorderColor: '#2b579a'
    });

    fc.add(text);
    fc.setActiveObject(text);
    fc.renderAll();
    document.getElementById('add_text_input').value = '';

    scrollToPage(activePageIndex);
    document.getElementById('editorStatusText').textContent =
        `Text added on Page ${activePageIndex + 1} — drag to position`;
}

// ── Tool: Add Image (File Upload) ──
function addImageToCanvas(event) {
    const fc = getActiveCanvas();
    if (!fc) return;

    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        fabric.Image.fromURL(e.target.result, function (img) {
            img.scaleToWidth(200);
            img.set({
                left: 150, top: 150,
                cornerColor: '#2b579a',
                cornerSize: 8,
                transparentCorners: false
            });
            fc.add(img);
            fc.setActiveObject(img);
            fc.renderAll();
            document.getElementById('editorStatusText').textContent =
                `Image added on Page ${activePageIndex + 1}`;
        });
    };
    reader.readAsDataURL(file);
    event.target.value = '';
}

// ── Tool: Paste Image from Clipboard (Ctrl+V) ──
function handlePaste(e) {
    const fc = getActiveCanvas();
    if (!fc) return;

    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    for (const item of items) {
        if (item.type.indexOf('image') !== -1) {
            const blob = item.getAsFile();
            const reader = new FileReader();
            reader.onload = function (evt) {
                fabric.Image.fromURL(evt.target.result, function (img) {
                    img.scaleToWidth(250);
                    img.set({
                        left: 100, top: 100,
                        cornerColor: '#2b579a',
                        cornerSize: 8,
                        transparentCorners: false
                    });
                    fc.add(img);
                    fc.setActiveObject(img);
                    fc.renderAll();
                    document.getElementById('editorStatusText').textContent =
                        `Pasted image on Page ${activePageIndex + 1}`;
                });
            };
            reader.readAsDataURL(blob);
        }
    }
}

// ── Tool: Delete Selected Object ──
function handleKeyDown(e) {
    const fc = getActiveCanvas();
    if (!fc) return;

    if (e.key === 'Delete' || e.key === 'Backspace') {
        const active = fc.getActiveObject();
        const bgRef = pageCanvases[activePageIndex]?.bgImage;
        if (active && !active.isEditing && active !== bgRef) {
            fc.remove(active);
            fc.renderAll();
            document.getElementById('editorStatusText').textContent = 'Object deleted';
        }
    }
}

// ── Helper: Scroll to a specific page ──
function scrollToPage(index) {
    const container = document.getElementById(`pageContainer_${index + 1}`);
    if (container) {
        container.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// ── Save: Bake ALL page edits back into the PDF ──
async function savePdfEdits() {
    if (pageCanvases.length === 0 || !currentPdfBytes) {
        alert('No PDF loaded in the editor');
        return;
    }

    try {
        document.getElementById('editorStatusText').textContent = '💾 Baking edits into PDF...';

        const pdfDoc = await PDFDocument.load(currentPdfBytes);
        const pages = pdfDoc.getPages();

        // Process each page's Fabric canvas
        for (let i = 0; i < pageCanvases.length; i++) {
            const { fabricCanvas: fc, bgImage, pageNum } = pageCanvases[i];
            const pdfPage = pages[i];
            if (!pdfPage) continue;

            const { width: pdfW, height: pdfH } = pdfPage.getSize();
            const scale = pdfW / fc.width;

            const objects = fc.getObjects();

            for (const obj of objects) {
                // Skip background image
                if (obj === bgImage) continue;

                if (obj.type === 'textbox' || obj.type === 'text' || obj.type === 'i-text') {
                    const fontSize = (obj.fontSize || 16) * scale;
                    pdfPage.drawText(obj.text || '', {
                        x: obj.left * scale,
                        y: pdfH - (obj.top * scale) - fontSize,
                        size: fontSize,
                        color: rgb(0, 0, 0),
                    });
                } else if (obj.type === 'image' && obj !== bgImage) {
                    try {
                        const imgDataUrl = obj.toDataURL({ format: 'png' });
                        const embeddedImg = await pdfDoc.embedPng(imgDataUrl);
                        const w = obj.getScaledWidth() * scale;
                        const h = obj.getScaledHeight() * scale;

                        pdfPage.drawImage(embeddedImg, {
                            x: obj.left * scale,
                            y: pdfH - (obj.top * scale) - h,
                            width: w,
                            height: h,
                        });
                    } catch (imgErr) {
                        console.warn(`Could not embed image on page ${pageNum}:`, imgErr);
                    }
                }
            }

            document.getElementById('editorStatusText').textContent =
                `💾 Saving page ${i + 1} of ${pageCanvases.length}...`;
        }

        editedPdfBytes = await pdfDoc.save();
        document.getElementById('editorStatusText').textContent = '✅ Saved!';
        alert('✅ Edits saved! The modified PDF will be used for encryption.');
        closePdfEditor();

    } catch (error) {
        console.error('[Editor] Baking error:', error);
        alert('❌ Error saving edits: ' + error.message);
        document.getElementById('editorStatusText').textContent = 'Save failed';
    }
}

// ============= UPLOAD & DATA HANDLING =============

async function handleUpload(event) {
    event.preventDefault();

    const formData = new FormData();
    const isScratch = document.getElementById('uploadOptionInput').value === 'scratch';
    const pdfFile = document.getElementById('pdf_file').files[0];

    // 🚀 NEW: Auto-convert TXT to PDF if uploaded directly without manual edit
    if (!editedPdfBytes && pdfFile && pdfFile.name.toLowerCase().endsWith('.txt')) {
        console.log("📝 Auto-converting raw TXT to PDF before upload...");
        try {
            const textContent = await pdfFile.text();

            // Re-use logic for jsPDF
            let jsPDFLib;
            if (window.jspdf && window.jspdf.jsPDF) {
                jsPDFLib = window.jspdf.jsPDF;
            } else if (window.jsPDF) {
                jsPDFLib = window.jsPDF;
            } else {
                throw new Error("jsPDF library not found");
            }

            const doc = new jsPDFLib();
            const splitText = doc.splitTextToSize(textContent, 180);
            let cursorY = 20;
            for (let i = 0; i < splitText.length; i++) {
                doc.text(15, cursorY, splitText[i]);
                cursorY += 7;
                if (cursorY >= 280 && i < splitText.length - 1) {
                    doc.addPage();
                    cursorY = 20;
                }
            }
            const pdfArrayBuffer = doc.output('arraybuffer');
            const autoConvertedBytes = new Uint8Array(pdfArrayBuffer);

            const blob = new Blob([autoConvertedBytes], { type: 'application/pdf' });
            formData.append('pdf_file', blob, pdfFile.name.replace('.txt', '.pdf'));
            console.log("✅ Auto-conversion successful.");
        } catch (autoErr) {
            console.error("Auto-conversion failed:", autoErr);
            alert("Failed to auto-convert TXT to PDF. Please try 'Preview & Edit' first.");
            return;
        }
    } else if (editedPdfBytes) {
        // Use manually edited/converted bytes
        const blob = new Blob([editedPdfBytes], { type: 'application/pdf' });
        formData.append('pdf_file', blob, 'edited_paper.pdf');
    } else {
        // Direct PDF upload
        formData.append('pdf_file', pdfFile);
    }

    formData.append('college_id', document.getElementById('college_id').value);
    formData.append('subject_code', document.getElementById('subject_code').value);
    formData.append('exam_datetime', document.getElementById('exam_datetime').value);
    formData.append('principal_email', document.getElementById('principal_email').value);

    // Hide form and show progress
    document.getElementById('uploadForm').style.display = 'none';
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';

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
                document.getElementById('progressSection').style.display = 'none';
                document.getElementById('resultSection').style.display = 'block';

                document.getElementById('paperId').textContent = data.data.paper_id;
                document.getElementById('txHash').textContent = data.data.transaction_hash;
                document.getElementById('docHash').textContent = data.data.document_hash;
                document.getElementById('resultCollegeId').textContent = data.data.college_id;
                document.getElementById('resultSubjectCode').textContent = data.data.subject_code;
                document.getElementById('resultExamDateTime').textContent = data.data.exam_datetime;
                document.getElementById('emailStatus').textContent = data.data.email_sent ? '✅ Sent' : '⚠️ Failed';

                // Refresh paper count badge
                fetchPaperCount();

                // Auto-refresh paper list if open
                if (document.getElementById('paperListWrap').classList.contains('open')) {
                    loadPaperList();
                }
            } else {
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

// ============= PAPER LIST =============

async function loadPaperList() {
    const contentDiv = document.getElementById('paperListContent');
    const totalBadge = document.getElementById('totalPapers');

    contentDiv.innerHTML = '<div class="paper-list-loading">⏳ Loading papers from blockchain...</div>';

    try {
        const sessionToken = localStorage.getItem('session_token');

        const response = await fetch(`${API_BASE_URL}/admin/papers`, {
            method: 'GET',
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success) {
            const papers = data.data.papers;
            totalBadge.textContent = data.data.total;

            if (papers.length === 0) {
                contentDiv.innerHTML = `
                    <div class="paper-list-empty">
                        <div class="empty-icon">📭</div>
                        <p>No papers uploaded yet.</p>
                        <p style="font-size:12px; margin-top:6px; opacity:0.6;">Upload your first exam paper using the form above.</p>
                    </div>`;
                return;
            }

            let html = `<table class="paper-table"><thead><tr>
                <th>#</th><th>Paper ID</th><th>Subject</th><th>College</th><th>Exam Date</th><th>Uploaded</th><th>Status</th><th>Actions</th>
            </tr></thead><tbody>`;

            papers.forEach((p, i) => {
                const examDate = new Date(p.exam_datetime * 1000).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
                const uploadDate = new Date(p.timestamp * 1000).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });
                const cls = p.verified ? 'verified' : 'stored';
                const txt = p.verified ? '✅ Verified' : '🔗 Stored';

                // Only show reschedule for non-verified papers
                const actionsHtml = p.verified ?
                    `<span style="color:#aaa; font-size:12px;">No Actions</span>` :
                    `<button class="btn-secondary" onclick="openRescheduleModal(${p.paper_id}, '${new Date(p.exam_datetime * 1000).toISOString().slice(0, 16)}')" style="padding: 4px 10px; font-size:11px;">📅 Reschedule</button>`;

                html += `<tr>
                    <td>${i + 1}</td>
                    <td><strong>${p.paper_id}</strong></td>
                    <td>${p.subject_code}</td>
                    <td>${p.college_id}</td>
                    <td>${examDate}</td>
                    <td>${uploadDate}</td>
                    <td><span class="status-badge ${cls}">${txt}</span></td>
                    <td>${actionsHtml}</td>
                </tr>`;
            });

            html += '</tbody></table>';
            contentDiv.innerHTML = html;
        } else {
            contentDiv.innerHTML = `<div class="paper-list-empty"><div class="empty-icon">⚠️</div><p>${data.error}</p></div>`;
        }
    } catch (error) {
        contentDiv.innerHTML = `<div class="paper-list-empty"><div class="empty-icon">❌</div>
            <p>Could not connect to server.</p>
            <p style="font-size:12px; margin-top:6px; opacity:0.6;">Make sure the backend and Ganache are running.</p></div>`;
        console.error('Paper list error:', error);
    }
}

// ============= RESCHEDULE MODAL =============

function openRescheduleModal(paperId, currentDateTime) {
    document.getElementById('reschedule_paper_id').value = paperId;
    document.getElementById('new_exam_datetime').value = currentDateTime;
    document.getElementById('rescheduleModal').style.display = 'flex';

    // Clear previous messages
    const msgDiv = document.getElementById('rescheduleMessage');
    msgDiv.style.display = 'none';
    msgDiv.className = 'message-toast';
}

function closeRescheduleModal() {
    document.getElementById('rescheduleModal').style.display = 'none';
}

async function submitReschedule() {
    const paperId = document.getElementById('reschedule_paper_id').value;
    const newDateTime = document.getElementById('new_exam_datetime').value;
    const btn = document.getElementById('rescheduleSubmitBtn');
    const msgDiv = document.getElementById('rescheduleMessage');

    if (!newDateTime) {
        alert('Please select a new date and time');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '⏳ Rescheduling on Blockchain...';
    msgDiv.style.display = 'none';

    try {
        const sessionToken = localStorage.getItem('session_token');
        const response = await fetch(`${API_BASE_URL}/admin/reschedule-paper`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paper_id: paperId,
                new_exam_datetime: newDateTime
            })
        });

        const data = await response.json();

        if (data.success) {
            msgDiv.textContent = '✅ Rescheduled Successfully on Blockchain!';
            msgDiv.className = 'message-toast success';
            msgDiv.style.display = 'block';

            // Refresh the list after 1s
            setTimeout(() => {
                loadPaperList();
                closeRescheduleModal();
            }, 1500);
        } else {
            msgDiv.textContent = '❌ Error: ' + data.error;
            msgDiv.className = 'message-toast error';
            msgDiv.style.display = 'block';
        }
    } catch (e) {
        msgDiv.textContent = '❌ Failed to connect to server';
        msgDiv.className = 'message-toast error';
        msgDiv.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.innerHTML = '⛓️ Update Blockchain Logic';
    }
}

// ============= REGISTER PRINCIPAL =============

async function handleRegister(event) {
    event.preventDefault();

    const regBtn = document.getElementById('registerBtn');
    const messageDiv = document.getElementById('registerMessage');

    // Clear previous message
    messageDiv.style.display = 'none';
    messageDiv.className = 'message-toast';

    const payload = {
        register_no: document.getElementById('reg_no').value,
        name: document.getElementById('reg_name').value,
        email: document.getElementById('reg_email').value,
        college_id: document.getElementById('reg_college').value,
        password: document.getElementById('reg_password').value,
        role: 'principal'
    };

    regBtn.disabled = true;
    regBtn.textContent = '⏳ Registering...';

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            messageDiv.textContent = '✅ Principal account created successfully!';
            messageDiv.className = 'message-toast success';
            messageDiv.style.display = 'block';
            messageDiv.style.background = 'rgba(46, 213, 115, 0.15)';
            messageDiv.style.color = '#2ed573';

            // Clear form
            document.getElementById('registerForm').reset();
        } else {
            messageDiv.textContent = '❌ ' + (data.message || data.error);
            messageDiv.className = 'message-toast error';
            messageDiv.style.display = 'block';
            messageDiv.style.background = 'rgba(255, 71, 87, 0.15)';
            messageDiv.style.color = '#ff4757';
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error connecting to server';
        messageDiv.className = 'message-toast error';
        messageDiv.style.display = 'block';
        console.error('Register error:', error);
    } finally {
        regBtn.disabled = false;
        regBtn.textContent = '➕ Add Principal Account';
    }
}

function resetForm() {
    document.getElementById('uploadForm').reset();
    document.getElementById('uploadForm').style.display = 'block';
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';

    // Clear editor state
    currentPdfBytes = null;
    editedPdfBytes = null;

    const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
    steps.forEach(stepId => {
        const stepElement = document.getElementById(stepId);
        stepElement.classList.remove('active', 'completed');
        stepElement.querySelector('.step-icon').textContent = '⏳';
    });
}
