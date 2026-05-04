/**
 * Heart Health Module v2 — Futuristic Dashboard JavaScript
 * Handles navigation, API calls, charts, auto-monitoring, Cardia chat
 * Auto-connects and syncs data for a fully automated experience
 */

// Auto-detect base path (supports standalone and sub-app mount at /heart)
const _pathMatch = window.location.pathname.match(/^(\/heart)\//);
const BASE_PATH = _pathMatch ? _pathMatch[1] : '';
const API = `${BASE_PATH}/api/v1`;
const WS_BASE = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${BASE_PATH}/api/v1`;
const USER_ID = 1;

// ═══ State ════════════════════════════════════

let monitoringWs = null;
let jarvisWs = null;
let hrChart = null;
let spo2Chart = null;
const hrData = { labels: [], data: [] };
const spo2Data = { labels: [], data: [] };
let autoSyncInterval = null;

// ═══ Live Clock ═══════════════════════════════

function updateClock() {
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    const clockEl = document.getElementById('liveClock');
    if (clockEl) clockEl.textContent = time;

    const dateEl = document.getElementById('dateDisplay');
    if (dateEl) {
        const dateStr = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
        dateEl.textContent = dateStr.toUpperCase();
    }
}

// ═══ Navigation ═══════════════════════════════

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
    });
});

// ═══ Animated Number Updates ══════════════════

function animateValue(element, newValue, duration = 400) {
    if (!element) return;
    const current = parseFloat(element.textContent) || 0;
    const target = parseFloat(newValue);
    if (isNaN(target)) {
        element.textContent = newValue;
        return;
    }
    
    const startTime = performance.now();
    const isFloat = String(newValue).includes('.');
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = current + (target - current) * eased;
        element.textContent = isFloat ? value.toFixed(1) : Math.round(value);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// ═══ Charts Setup ═════════════════════════════

function initCharts() {
    const gridColor = 'rgba(0, 212, 255, 0.04)';
    const tickColor = '#4a6a8a';
    
    const chartDefaults = {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        scales: {
            x: {
                display: true,
                ticks: { color: tickColor, maxTicksLimit: 8, font: { size: 9, family: 'JetBrains Mono' } },
                grid: { color: gridColor }
            },
            y: {
                ticks: { color: tickColor, font: { size: 9, family: 'JetBrains Mono' } },
                grid: { color: gridColor }
            }
        },
        plugins: {
            legend: { display: false },
        }
    };

    hrChart = new Chart(document.getElementById('hrChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#ff2244',
                backgroundColor: 'rgba(255, 34, 68, 0.08)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                ...chartDefaults.scales,
                y: { ...chartDefaults.scales.y, min: 40, max: 160 }
            }
        }
    });

    spo2Chart = new Chart(document.getElementById('spo2Chart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#00d4ff',
                backgroundColor: 'rgba(0, 212, 255, 0.08)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                ...chartDefaults.scales,
                y: { ...chartDefaults.scales.y, min: 85, max: 100 }
            }
        }
    });
}

function addChartData(chart, label, value, maxPoints = 50) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);
    if (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    chart.update('none');
}

// ═══ Auto-Sync Data Sources ═══════════════════

async function autoSyncSources() {
    const syncDot = document.getElementById('syncDot');
    const syncStatus = document.getElementById('syncStatus');
    
    try {
        if (syncDot) { syncDot.style.display = 'inline-block'; }
        if (syncStatus) { syncStatus.textContent = 'Syncing...'; }
        
        const res = await fetch(`${API}/data/sync/all`, { method: 'POST' });
        const data = await res.json();
        
        if (syncStatus) {
            syncStatus.textContent = `Synced ${data.total_readings || 0} readings`;
        }
        
        // Update dashboard if we got data
        if (data.latest) {
            updateDashboardFromData(data.latest);
        }
    } catch (e) {
        if (syncStatus) { syncStatus.textContent = 'Sync failed'; }
    } finally {
        setTimeout(() => {
            if (syncDot) syncDot.style.display = 'none';
            if (syncStatus) syncStatus.textContent = '';
        }, 3000);
    }
}

function updateDashboardFromData(data) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    if (data.heart_rate) {
        animateValue(document.getElementById('hrValue'), Math.round(data.heart_rate));
        const bpmDisplay = document.getElementById('heartBpmDisplay');
        if (bpmDisplay) bpmDisplay.textContent = `${Math.round(data.heart_rate)} BPM`;
        
        const hrStatus = document.getElementById('hrStatus');
        if (hrStatus) {
            if (data.heart_rate > 100) {
                hrStatus.textContent = '⚠️ Running hot';
                hrStatus.className = 'stat-status warning';
            } else if (data.heart_rate < 60) {
                hrStatus.textContent = '⬇️ Chill mode';
                hrStatus.className = 'stat-status warning';
            } else {
                hrStatus.textContent = '✅ Smooth sailing';
                hrStatus.className = 'stat-status good';
            }
        }
        if (hrChart) addChartData(hrChart, time, data.heart_rate);
    }

    if (data.spo2) {
        animateValue(document.getElementById('spo2Value'), data.spo2.toFixed(1));
        
        const spo2Status = document.getElementById('spo2Status');
        if (spo2Status) {
            if (data.spo2 < 94) {
                spo2Status.textContent = '🚨 Low — get help!';
                spo2Status.className = 'stat-status danger';
            } else if (data.spo2 < 96) {
                spo2Status.textContent = '⬇️ Slightly low';
                spo2Status.className = 'stat-status warning';
            } else {
                spo2Status.textContent = '✅ Looking good';
                spo2Status.className = 'stat-status good';
            }
        }
        if (spo2Chart) addChartData(spo2Chart, time, data.spo2);
    }

    if (data.hrv) {
        animateValue(document.getElementById('hrvValue'), data.hrv.toFixed(1));
        const hrvStatus = document.getElementById('hrvStatus');
        if (hrvStatus) {
            hrvStatus.textContent = data.hrv > 30 ? '✅ Healthy range' : '⬇️ Below average';
            hrvStatus.className = data.hrv > 30 ? 'stat-status good' : 'stat-status warning';
        }
    }

    if (data.steps !== undefined) {
        animateValue(document.getElementById('stepsValue'), data.steps);
        const stepsStatus = document.getElementById('stepsStatus');
        if (stepsStatus) {
            const pct = Math.min(100, ((data.steps / 8000) * 100)).toFixed(0);
            stepsStatus.textContent = data.steps > 8000 ? '🔥 Goal crushed!' : `${pct}% of daily goal`;
            stepsStatus.className = data.steps > 8000 ? 'stat-status good' : 'stat-status';
        }
    }
}

// ═══ Monitoring WebSocket ═════════════════════

function startMonitoring() {
    if (monitoringWs) return;

    const monitorDot = document.getElementById('monitorDot');
    const monitorStatusEl = document.getElementById('monitorStatus');

    monitoringWs = new WebSocket(`${WS_BASE}/monitor/live/${USER_ID}`);

    monitoringWs.onopen = () => {
        if (monitorDot) { monitorDot.className = 'status-dot'; }
        if (monitorStatusEl) { monitorStatusEl.textContent = 'Monitoring Live'; }
    };

    monitoringWs.onmessage = (event) => {
        const d = JSON.parse(event.data);
        updateDashboardFromData(d);

        if (d.alerts && d.alerts.length > 0) {
            d.alerts.forEach(alert => {
                addJarvisMessage(`⚡ ${alert.message}`, false);
            });
        }
    };

    monitoringWs.onclose = () => {
        monitoringWs = null;
        document.getElementById('startMonitoring').disabled = false;
        document.getElementById('stopMonitoring').disabled = true;
        if (monitorDot) { monitorDot.className = 'status-dot offline'; }
        if (monitorStatusEl) { monitorStatusEl.textContent = 'Monitor Idle'; }
    };

    monitoringWs.onerror = () => {
        if (monitorDot) { monitorDot.className = 'status-dot offline'; }
        if (monitorStatusEl) { monitorStatusEl.textContent = 'Monitor Error'; }
    };

    document.getElementById('startMonitoring').disabled = true;
    document.getElementById('stopMonitoring').disabled = false;
}

function stopMonitoring() {
    if (monitoringWs) {
        monitoringWs.close();
        monitoringWs = null;
    }
    document.getElementById('startMonitoring').disabled = false;
    document.getElementById('stopMonitoring').disabled = true;
}

document.getElementById('startMonitoring').addEventListener('click', startMonitoring);
document.getElementById('stopMonitoring').addEventListener('click', stopMonitoring);

// ═══ Time Period Filter ═══════════════════════

let currentTimePeriod = 'today'; // Default: today only

const timePeriodEl = document.getElementById('timePeriodFilter');
if (timePeriodEl) {
    timePeriodEl.addEventListener('change', (e) => {
        currentTimePeriod = e.target.value;
        console.log(`📅 Data period changed to: ${currentTimePeriod}`);
        
        // Show message about data period
        const periodNames = {
            'today': 'TODAY\'S DATA ONLY',
            '7days': 'LAST 7 DAYS',
            '30days': 'LAST 30 DAYS',
            'all': 'ALL TIME DATA'
        };
        
        addJarvisMessage(`📊 Now showing: ${periodNames[currentTimePeriod]}`, false);
        
        // Optionally: Reset charts and refetch data
        hrData.labels = [];
        hrData.data = [];
        spo2Data.labels = [];
        spo2Data.data = [];
        if (hrChart) hrChart.update();
        if (spo2Chart) spo2Chart.update();
    });
}

// ═══ Demo Data Generation ═════════════════════

document.getElementById('generateDemo').addEventListener('click', async () => {
    const btn = document.getElementById('generateDemo');
    btn.textContent = '⏳ Generating...';
    btn.disabled = true;
    try {
        const res = await fetch(`${API}/watch/demo/${USER_ID}?days=7`, { method: 'POST' });
        const data = await res.json();
        btn.textContent = `✅ ${data.count} points generated!`;
        setTimeout(() => {
            btn.textContent = '🧪 Generate Demo Data';
            btn.disabled = false;
            startMonitoring();
        }, 2000);
    } catch (e) {
        btn.textContent = '❌ Error';
        setTimeout(() => { btn.textContent = '🧪 Generate Demo Data'; btn.disabled = false; }, 2000);
    }
});

// ═══ Prediction ═══════════════════════════════

document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
        age: parseInt(document.getElementById('pred-age').value),
        sex: parseInt(document.getElementById('pred-sex').value),
        cp: parseInt(document.getElementById('pred-cp').value),
        trestbps: parseFloat(document.getElementById('pred-trestbps').value),
        chol: parseFloat(document.getElementById('pred-chol').value),
        fbs: parseInt(document.getElementById('pred-fbs').value),
        restecg: parseInt(document.getElementById('pred-restecg').value),
        thalach: parseFloat(document.getElementById('pred-thalach').value),
        exang: parseInt(document.getElementById('pred-exang').value),
        oldpeak: parseFloat(document.getElementById('pred-oldpeak').value),
        slope: parseInt(document.getElementById('pred-slope').value),
        ca: parseInt(document.getElementById('pred-ca').value),
        thal: parseInt(document.getElementById('pred-thal').value),
    };

    try {
        const res = await fetch(`${API}/predict/heart-attack`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        displayPrediction(data);
    } catch (e) {
        alert('Error: ' + e.message);
    }
});

function displayPrediction(data) {
    const resultCard = document.getElementById('predictionResult');
    resultCard.style.display = 'block';

    document.getElementById('riskScore').textContent = `${(data.risk_score * 100).toFixed(1)}%`;
    const labelEl = document.getElementById('riskLabel');
    labelEl.textContent = data.risk_level;
    labelEl.className = `risk-label ${data.risk_level}`;

    document.getElementById('riskSummary').textContent = data.summary;

    const factorsEl = document.getElementById('riskFactors');
    factorsEl.innerHTML = '<h4 style="margin-bottom:8px;font-size:0.65rem;color:#4a6a8a;font-family:Orbitron;letter-spacing:2px;text-transform:uppercase">Contributing Factors</h4>';
    (data.contributing_factors || []).forEach(f => {
        factorsEl.innerHTML += `<div class="factor-item ${f.severity}">
            <strong>${f.factor}</strong>: ${f.explanation}
        </div>`;
    });

    const tipsEl = document.getElementById('riskTips');
    tipsEl.innerHTML = '<h4 style="margin-bottom:8px;font-size:0.65rem;color:#00ff88;font-family:Orbitron;letter-spacing:2px;text-transform:uppercase">Recommendations</h4><ul>';
    (data.tips || []).forEach(t => { tipsEl.innerHTML += `<li>${t}</li>`; });
    tipsEl.innerHTML += '</ul>';

    if (data.jarvis_response) {
        document.getElementById('predJarvis').textContent = data.jarvis_response;
    }

    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ═══ ECG Analysis ═════════════════════════════

document.getElementById('analyzeEcg').addEventListener('click', async () => {
    const text = document.getElementById('ecgText').value;
    const fileInput = document.getElementById('ecgFile');
    const file = fileInput.files[0];

    const formData = new FormData();
    if (text) formData.append('text', text);
    if (file) formData.append('file', file);

    if (!text && !file) { alert('Please enter ECG text or upload a file.'); return; }

    const btn = document.getElementById('analyzeEcg');
    btn.textContent = '⏳ Analyzing...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API}/analyze/ecg`, { method: 'POST', body: formData });
        const data = await res.json();
        const resultEl = document.getElementById('ecgResult');
        resultEl.innerHTML = `<strong>Summary:</strong> ${data.summary}\n\n<strong>Findings:</strong> ${(data.findings || []).join(', ')}\n\n<strong>Recommendations:</strong> ${data.recommendations}\n\n<strong>Cardia says:</strong> ${data.jarvis_response || ''}`;
        resultEl.classList.add('visible');
    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        btn.textContent = '🔍 Analyze ECG';
        btn.disabled = false;
    }
});

// ═══ Angiography Analysis ═════════════════════

document.getElementById('analyzeAngio').addEventListener('click', async () => {
    // Accept ONLY PDF files
    const fileInput = document.getElementById('angioFile');
    const file = fileInput.files[0];

    if (!file) { 
        alert('Please upload an angiography PDF file.'); 
        return; 
    }

    if (!file.type.includes('pdf') && !file.name.endsWith('.pdf')) {
        alert('Please upload a PDF file only.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const btn = document.getElementById('analyzeAngio');
    btn.textContent = '⏳ Analyzing...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API}/analyze/angiography/pdf`, { method: 'POST', body: formData });
        const data = await res.json();
        const resultEl = document.getElementById('angioResult');
        resultEl.innerHTML = `<strong>Summary:</strong> ${data.structured_summary}\n\n<strong>Arteries:</strong> ${(data.artery_locations || []).join(', ')}\n\n<strong>Stents:</strong> ${JSON.stringify(data.stent_details, null, 2)}\n\n<strong>Explanation:</strong> ${data.explanation}\n\n<strong>Follow-up:</strong> ${data.follow_up_instructions}\n\n<strong>Cardia says:</strong> ${data.jarvis_response || ''}`;
        resultEl.classList.add('visible');
    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        btn.textContent = '🔍 Analyze Report';
        btn.disabled = false;
    }
});

// ═══ Heart Sound Analysis ═════════════════════

document.getElementById('analyzeSound').addEventListener('click', async () => {
    const fileInput = document.getElementById('soundFile');
    const file = fileInput.files[0];
    if (!file) { alert('Please select an audio file.'); return; }

    const formData = new FormData();
    formData.append('file', file);

    const btn = document.getElementById('analyzeSound');
    btn.textContent = '⏳ Analyzing...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API}/analyze/heart-sound`, { method: 'POST', body: formData });
        const data = await res.json();
        const resultEl = document.getElementById('soundResult');
        resultEl.innerHTML = `<strong>Classification:</strong> ${data.classification}\n<strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%\n\n<strong>Explanation:</strong> ${data.explanation}\n\n<strong>Recommendation:</strong> ${data.recommendation || 'N/A'}\n\n<strong>Cardia says:</strong> ${data.jarvis_response || ''}`;
        resultEl.classList.add('visible');
    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        btn.textContent = '🔍 Analyze Sound';
        btn.disabled = false;
    }
});

// ═══ Data Sources / Devices ═══════════════════

async function registerSource(type) {
    try {
        const res = await fetch(`${API}/data/source/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source_type: type, config: {}, priority: 1 })
        });
        const data = await res.json();
        const statusEl = document.getElementById(`status-${type}`);
        if (statusEl) {
            statusEl.textContent = `✅ Connected`;
            statusEl.classList.add('connected');
        }
    } catch (e) {
        alert('Error connecting: ' + e.message);
    }
}

// ═══ Google Fit OAuth Flow ════════════════════

async function connectGoogleFit() {
    try {
        const res = await fetch(`${API}/data/google-fit/auth-url`);
        const data = await res.json();
        
        if (data.auth_url) {
            const popup = window.open(data.auth_url, 'GoogleFitAuth', 'width=600,height=700,scrollbars=yes');
            
            const checkClosed = setInterval(() => {
                if (popup && popup.closed) {
                    clearInterval(checkClosed);
                    const statusEl = document.getElementById('status-google_fit');
                    if (statusEl) {
                        statusEl.textContent = '🔄 Syncing data...';
                    }
                    // Sync after OAuth popup closes
                    setTimeout(async () => {
                        try {
                            const syncRes = await fetch(`${API}/data/sync/all`, { method: 'POST' });
                            const syncData = await syncRes.json();
                            if (statusEl) {
                                statusEl.textContent = `✅ Connected — ${syncData.total_readings || 0} readings synced`;
                                statusEl.classList.add('connected');
                            }
                            if (syncData.latest) {
                                updateDashboardFromData(syncData.latest);
                            }
                        } catch (e) {
                            if (statusEl) {
                                statusEl.textContent = '⚠️ Sync failed — try again';
                            }
                        }
                    }, 2000);
                }
            }, 500);
        } else {
            registerSource('google_fit');
        }
    } catch (e) {
        registerSource('google_fit');
    }
}

async function submitManualEntry() {
    const payload = {};
    const hr = document.getElementById('manual-hr').value;
    const bpSys = document.getElementById('manual-bp-sys').value;
    const bpDia = document.getElementById('manual-bp-dia').value;
    const spo2 = document.getElementById('manual-spo2').value;

    if (hr) payload.heart_rate = parseFloat(hr);
    if (bpSys) payload.blood_pressure_systolic = parseFloat(bpSys);
    if (bpDia) payload.blood_pressure_diastolic = parseFloat(bpDia);
    if (spo2) payload.spo2 = parseFloat(spo2);

    if (Object.keys(payload).length === 0) { alert('Please enter at least one value.'); return; }

    try {
        const res = await fetch(`${API}/data/manual`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        document.getElementById('status-manual').textContent = `✅ Logged!`;
        document.getElementById('status-manual').classList.add('connected');
        ['manual-hr', 'manual-bp-sys', 'manual-bp-dia', 'manual-spo2'].forEach(id => {
            document.getElementById(id).value = '';
        });
        updateDashboardFromData(payload);
        setTimeout(() => {
            document.getElementById('status-manual').textContent = 'Ready';
            document.getElementById('status-manual').classList.remove('connected');
        }, 3000);
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

// ═══ Cardia Chat ══════════════════════════════

const jarvisPanel = document.getElementById('jarvisPanel');
const jarvisToggle = document.getElementById('jarvisToggle');
const jarvisClose = document.getElementById('jarvisClose');
const jarvisInput = document.getElementById('jarvisInput');
const jarvisSend = document.getElementById('jarvisSend');
const jarvisMessages = document.getElementById('jarvisMessages');

jarvisToggle.addEventListener('click', () => jarvisPanel.classList.toggle('open'));
jarvisClose.addEventListener('click', () => jarvisPanel.classList.remove('open'));

function addJarvisMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-msg' : 'jarvis-msg'}`;

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';

    const content = document.createElement('div');
    content.className = 'msg-content';

    // Parse markdown-like bold and line breaks
    const formatted = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    content.innerHTML = `<p>${formatted}</p>`;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(content);
    jarvisMessages.appendChild(msgDiv);
    jarvisMessages.scrollTop = jarvisMessages.scrollHeight;
}

function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'message jarvis-msg';
    typing.id = 'typingIndicator';
    typing.innerHTML = `<div class="msg-avatar">🤖</div><div class="msg-content"><div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>`;
    jarvisMessages.appendChild(typing);
    jarvisMessages.scrollTop = jarvisMessages.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

// ═══ Browser-Native Text-to-Speech ════════════

let currentUtterance = null;

function speakText(text) {
    if (!('speechSynthesis' in window)) {
        console.warn("Browser doesn't support speech synthesis");
        return;
    }
    
    // Stop any currently playing speech
    window.speechSynthesis.cancel();
    
    // Clean text for speech — remove emojis and markdown
    let cleanText = text
        .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2702}-\u{27B0}\u{24C2}-\u{1F251}\u{1FA00}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}\u{1F900}-\u{1F9FF}]/gu, '')
        .replace(/\*\*(.+?)\*\*/g, '$1')
        .replace(/\*(.+?)\*/g, '$1')
        .replace(/#{1,6}\s*/g, '')
        .replace(/\n+/g, '. ')
        .trim();
    
    // Truncate for TTS
    if (cleanText.length > 1500) {
        cleanText = cleanText.substring(0, 1500) + '. And more.';
    }
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.05;
    utterance.volume = 1.0;
    utterance.lang = 'en-US';
    
    // Try to pick a nice voice
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v => 
        v.name.includes('Samantha') || v.name.includes('Karen') || 
        v.name.includes('Google') || v.name.includes('Microsoft Zira') ||
        (v.lang.startsWith('en') && v.localService)
    );
    if (preferred) {
        utterance.voice = preferred;
    }
    
    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
}

// Pre-load voices (some browsers need this)
if ('speechSynthesis' in window) {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => { window.speechSynthesis.getVoices(); };
}

async function sendJarvisMessage(text) {
    if (!text.trim()) return;
    addJarvisMessage(text, true);
    jarvisInput.value = '';
    showTyping();

    const voiceEnabled = document.getElementById('voiceToggle').checked;

    try {
        // Always use /command — browser handles TTS
        const res = await fetch(`${API}/agent/command`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                user_id: USER_ID
            })
        });
        const data = await res.json();
        hideTyping();

        const responseText = data.response || data.error || 'No response';
        addJarvisMessage(responseText);

        // Speak the response using browser TTS
        if (voiceEnabled && responseText) {
            speakText(responseText);
        }

        // Show suggestions
        if (data.suggestions && data.suggestions.length > 0) {
            const lastMsg = jarvisMessages.lastChild;
            const content = lastMsg.querySelector('.msg-content');
            const sugDiv = document.createElement('div');
            sugDiv.className = 'msg-suggestions';
            data.suggestions.forEach(s => {
                const btn = document.createElement('button');
                btn.className = 'suggestion-btn';
                btn.textContent = s;
                btn.addEventListener('click', () => sendJarvisMessage(s));
                sugDiv.appendChild(btn);
            });
            content.appendChild(sugDiv);
        }
        
        // Handle Google Fit connection from chat
        if (text.toLowerCase().includes('connect google fit')) {
            connectGoogleFit();
        }
    } catch (e) {
        hideTyping();
        addJarvisMessage(`Hey, I'm having trouble connecting to the server 😅 Make sure the backend is running. Error: ${e.message}`);
    }
}

function sendSuggestion(text) {
    sendJarvisMessage(text);
}

jarvisSend.addEventListener('click', () => sendJarvisMessage(jarvisInput.value));
jarvisInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendJarvisMessage(jarvisInput.value);
});

// ═══ Voice Recognition & Mic Button ═══════════

const voiceBtn = document.getElementById('voiceBtn');
let commandRecognition = null;
let isCommandListening = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    commandRecognition = new SpeechRecognition();
    commandRecognition.continuous = false;
    commandRecognition.interimResults = true;
    commandRecognition.lang = 'en-US';
    commandRecognition.maxAlternatives = 1;

    commandRecognition.onstart = () => {
        isCommandListening = true;
        voiceBtn.classList.add('recording');
        voiceBtn.title = 'Listening... Click to stop';
        jarvisInput.placeholder = "🎤 Listening... speak now";
        
        // Stop any browser TTS to prevent feedback
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    };

    commandRecognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Show interim results live
        if (interimTranscript) {
            jarvisInput.value = interimTranscript;
        }
        
        if (finalTranscript) {
            finalTranscript = finalTranscript.replace(/hi cardia|hey cardia/gi, '').trim();
            if (finalTranscript) {
                jarvisInput.value = finalTranscript;
                sendJarvisMessage(finalTranscript);
            }
        }
    };

    commandRecognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        if (event.error === 'not-allowed') {
            addJarvisMessage("🎤 Mic permission denied. Please allow microphone access in your browser settings.\n\nIn Chrome: click the 🔒 icon in the address bar → Site settings → Microphone → Allow");
        } else if (event.error !== 'no-speech' && event.error !== 'aborted') {
            addJarvisMessage(`🎤 Voice error: ${event.error}. Try clicking the mic button again.`);
        }
        resetMicUI();
    };

    commandRecognition.onend = () => {
        resetMicUI();
    };

    function resetMicUI() {
        isCommandListening = false;
        voiceBtn.classList.remove('recording');
        voiceBtn.title = 'Click to speak';
        jarvisInput.placeholder = "Ask me anything about your heart...";
    }

    // Mic button click — toggle listen
    voiceBtn.addEventListener('click', () => {
        jarvisPanel.classList.add('open');
        
        // Stop TTS first
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }

        if (isCommandListening) {
            commandRecognition.stop();
        } else {
            try {
                commandRecognition.start();
            } catch (e) {
                // If already started, stop and retry
                try {
                    commandRecognition.stop();
                    setTimeout(() => {
                        try { commandRecognition.start(); } catch(e2) {
                            addJarvisMessage("🎤 Couldn't start the microphone. Please check browser mic permissions.");
                        }
                    }, 300);
                } catch (e2) {
                    addJarvisMessage("🎤 Couldn't start the microphone. Please check browser mic permissions.");
                }
            }
        }
    });

} else {
    voiceBtn.addEventListener('click', () => {
        jarvisPanel.classList.add('open');
        addJarvisMessage("🎤 Voice input isn't supported in this browser. Try using Chrome or Edge.");
    });
}

// ═══ Initialize ═══════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    
    // Start live clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Auto-sync data sources every 30 seconds
    autoSyncSources();
    autoSyncInterval = setInterval(autoSyncSources, 30000);
    
    // Auto-start monitoring
    setTimeout(() => {
        startMonitoring();
    }, 1000);
});
