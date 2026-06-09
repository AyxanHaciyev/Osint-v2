document.addEventListener("DOMContentLoaded", () => {
    const statusIndicator = document.getElementById("opsecStatus");
    const statusText = statusIndicator.querySelector(".status-text");
    const startBtn = document.getElementById("startBtn");
    const targetForm = document.getElementById("targetForm");
    const terminalLog = document.getElementById("terminalLog");
    const resultsList = document.getElementById("resultsList");
    const totalResultsEl = document.getElementById("totalResults");
    const totalDocsEl = document.getElementById("totalDocs");

    let isVpnActive = false;
    let ws = null;
    let totalResultsCount = 0;
    let totalDocsCount = 0;

    // --- VPN Status Polling ---
    async function checkVpnStatus() {
        try {
            const res = await fetch("/api/opsec/status");
            if (res.ok) {
                const data = await res.json();
                isVpnActive = data.vpn_active;
                
                if (isVpnActive) {
                    statusIndicator.className = "opsec-status safe";
                    statusText.textContent = `VPN Aktiv: ${data.interface}`;
                    startBtn.disabled = false;
                } else {
                    statusIndicator.className = "opsec-status danger";
                    statusText.textContent = "VPN YOXDUR! Təhlükəli!";
                    startBtn.disabled = true;
                }
            }
        } catch (e) {
            console.error("VPN check failed", e);
        }
    }

    // Poll every 3 seconds
    setInterval(checkVpnStatus, 3000);
    checkVpnStatus(); // Initial check


    // --- Terminal Logging ---
    function appendLog(message, type="info") {
        const line = document.createElement("div");
        line.className = `log-line ${type}`;
        
        // Ensure no HTML injection for raw logs, but preserve spacing
        line.textContent = message;
        
        terminalLog.appendChild(line);
        terminalLog.scrollTop = terminalLog.scrollHeight;
    }


    // --- Results Handling ---
    function renderResults(results) {
        resultsList.innerHTML = "";
        totalResultsCount = results.length;
        totalResultsEl.textContent = totalResultsCount;

        let docs = 0;
        results.forEach(res => {
            const li = document.createElement("li");
            li.className = "result-item" + (res.is_document ? " document" : "");
            
            if (res.is_document) docs++;

            const title = document.createElement("div");
            title.className = "result-title";
            title.textContent = res.title || "Adsız Nəticə";

            if (res.is_document) {
                const badge = document.createElement("span");
                badge.className = "doc-badge";
                badge.textContent = res.document_type ? res.document_type.toUpperCase() : "DOC";
                title.appendChild(badge);
            }

            const url = document.createElement("a");
            url.className = "result-url";
            url.href = res.url;
            url.target = "_blank";
            url.textContent = res.url;

            const snippet = document.createElement("div");
            snippet.className = "result-snippet";
            snippet.textContent = res.snippet ? res.snippet.substring(0, 150) + "..." : "";

            li.appendChild(title);
            li.appendChild(url);
            li.appendChild(snippet);
            resultsList.appendChild(li);
        });

        totalDocsCount = docs;
        totalDocsEl.textContent = totalDocsCount;
    }


    // --- Form Submission (Start Campaign) ---
    targetForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        if (!isVpnActive) {
            alert("Mullvad VPN aktiv deyil!");
            return;
        }

        // Collect data
        const targetData = {
            first_name: document.getElementById("firstName").value,
            last_name: document.getElementById("lastName").value,
            middle_name: document.getElementById("middleName").value,
            username: document.getElementById("username").value,
            email: document.getElementById("email").value,
            phone: document.getElementById("phone").value,
            age: document.getElementById("age").value,
            birth_month: document.getElementById("birthMonth").value,
            profession: document.getElementById("profession").value,
            hobbies: document.getElementById("hobbies").value,
            city: document.getElementById("city").value,
            employer: document.getElementById("employer").value,
            country: "Azərbaycan" // default
        };

        // Clean empty fields
        Object.keys(targetData).forEach(k => {
            if (!targetData[k]) delete targetData[k];
        });

        startCampaign(targetData);
    });

    function startCampaign(targetData) {
        startBtn.disabled = true;
        startBtn.innerHTML = "Axtarış Gedir... <span class='spinner'>⏳</span>";
        
        terminalLog.innerHTML = "";
        appendLog("Soket bağlantısı qurulur...", "info");

        // Connect WebSocket
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        ws = new WebSocket(`${protocol}//${window.location.host}/ws/campaign`);

        ws.onopen = () => {
            appendLog("Bağlantı quruldu. Hədəf məlumatları göndərilir.", "success");
            ws.send(JSON.stringify({ target: targetData }));
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                
                if (msg.type === "log" || msg.type === "rule") {
                    // Simple logic to colorize based on content
                    let level = "info";
                    if (msg.content.includes("❌") || msg.content.includes("Xəta")) level = "error";
                    if (msg.content.includes("⚠")) level = "warning";
                    if (msg.content.includes("✅")) level = "success";
                    
                    appendLog(msg.content, level);
                } 
                else if (msg.type === "results") {
                    renderResults(msg.data);
                }
                else if (msg.type === "document") {
                    appendLog(`📄 SƏNƏD TAPILDI: ${msg.data.filename}`, "warning");
                }
                else if (msg.type === "error") {
                    appendLog(msg.content, "error");
                    finishCampaign();
                }
                else if (msg.type === "done") {
                    appendLog("Axtarış kampaniyası müvəffəqiyyətlə başa çatdı.", "success");
                    finishCampaign();
                }
            } catch (err) {
                appendLog(event.data, "info");
            }
        };

        ws.onclose = () => {
            appendLog("Bağlantı bağlandı.", "warning");
            finishCampaign();
        };

        ws.onerror = (err) => {
            appendLog("WebSocket xətası baş verdi.", "error");
            finishCampaign();
        };
    }

    function finishCampaign() {
        if (isVpnActive) {
            startBtn.disabled = false;
            startBtn.innerHTML = "Yenidən Axtar <span class='lock-icon'>🔒</span>";
        }
        if (ws) {
            ws.close();
            ws = null;
        }
    }
});
