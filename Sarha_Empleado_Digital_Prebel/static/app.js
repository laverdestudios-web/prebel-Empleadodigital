const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const suggestionsBar = document.getElementById("suggestionsBar");
const categoriesList = document.getElementById("categoriesList");
const chatMain = document.getElementById("chatMain");
const statusBadge = document.getElementById("statusBadge");
const sidebar = document.getElementById("sidebar");

let currentChannel = "web";
let sessionId = "web-" + Math.random().toString(36).slice(2, 10);
let proceduresCache = [];

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, "<em>$1</em>");
  html = html.replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
  );
  html = html.replace(
    /([a-zA-Z0-9._%+-]+@prebel\.com\.co)/gi,
    '<a href="mailto:$1">$1</a>'
  );

  const lines = html.split("\n");
  const out = [];
  let inUl = false;
  let inOl = false;

  for (const line of lines) {
    const trimmed = line.trim();
    if (/^[-•]\s+/.test(trimmed)) {
      if (inOl) { out.push("</ol>"); inOl = false; }
      if (!inUl) { out.push("<ul>"); inUl = true; }
      out.push(`<li>${trimmed.replace(/^[-•]\s+/, "")}</li>`);
    } else if (/^\d+\.\s+/.test(trimmed)) {
      if (inUl) { out.push("</ul>"); inUl = false; }
      if (!inOl) { out.push("<ol>"); inOl = true; }
      out.push(`<li>${trimmed.replace(/^\d+\.\s+/, "")}</li>`);
    } else {
      if (inUl) { out.push("</ul>"); inUl = false; }
      if (inOl) { out.push("</ol>"); inOl = false; }
      out.push(trimmed ? `<p>${trimmed}</p>` : "");
    }
  }
  if (inUl) out.push("</ul>");
  if (inOl) out.push("</ol>");
  return out.join("");
}

function appendMessage(role, text, sources = []) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  if (role === "user") {
    div.textContent = text;
  } else {
    div.innerHTML = renderMarkdown(text);
    if (sources.length > 0) {
      const details = document.createElement("details");
      details.className = "sources-details";
      const summary = document.createElement("summary");
      summary.textContent = `Fuentes consultadas (${sources.length})`;
      details.appendChild(summary);
      const ul = document.createElement("ul");
      for (const s of sources) {
        const li = document.createElement("li");
        li.textContent = `${s.file} → ${s.section}`;
        ul.appendChild(li);
      }
      details.appendChild(ul);
      div.appendChild(details);
    }
  }
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderSuggestions(items = []) {
  suggestionsBar.innerHTML = "";
  for (const q of items) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "suggestion-chip";
    btn.textContent = q;
    btn.addEventListener("click", () => {
      const numMatch = q.match(/^(\d{1,2})\.\s+/);
      sendMessage(numMatch ? numMatch[1] : q, q);
    });
    suggestionsBar.appendChild(btn);
  }
}

async function sendMessage(text, displayText = null) {
  const trimmed = text.trim();
  if (!trimmed) return;
  appendMessage("user", displayText || trimmed);
  chatInput.value = "";
  renderSuggestions([]);

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmed, channel: currentChannel, session_id: sessionId }),
    });
    const data = await resp.json();
    appendMessage("bot", data.answer, data.sources || []);
    renderSuggestions(data.suggested_questions || []);
  } catch (err) {
    appendMessage("bot", "Ocurrió un error al consultar el servidor. Intenta nuevamente.");
  }
}

async function loadInitialState() {
  const [catResp, healthResp, procResp] = await Promise.all([
    fetch("/api/categories"),
    fetch("/health"),
    fetch("/api/self-service/procedures"),
  ]);
  const catData = await catResp.json();
  const healthData = await healthResp.json();
  const procData = await procResp.json();

  statusBadge.textContent = `Conectado · ${healthData.chunks_indexed} secciones (${healthData.mode})`;

  categoriesList.innerHTML = "";
  for (const group of catData.categories || []) {
    const card = document.createElement("div");
    card.className = "cat-group";
    const title = document.createElement("div");
    title.className = "cat-title";
    title.textContent = group.category;
    card.appendChild(title);

    const topicsDiv = document.createElement("div");
    topicsDiv.className = "cat-topics";
    for (const topic of group.topics || []) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "topic-chip";
      chip.textContent = topic;
      chip.addEventListener("click", () => {
        sidebar.classList.remove("open");
        sendMessage(topic);
      });
      topicsDiv.appendChild(chip);
    }
    card.appendChild(topicsDiv);
    categoriesList.appendChild(card);
  }

  proceduresCache = procData.procedures || [];
  const ssProc = document.getElementById("ssProcedure");
  ssProc.innerHTML = "";
  for (const p of proceduresCache) {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.title;
    ssProc.appendChild(opt);
  }
  updateVariants();

  // Initial welcome
  const welcomeResp = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "hola", channel: currentChannel, session_id: sessionId }),
  });
  const welcomeData = await welcomeResp.json();
  appendMessage("bot", welcomeData.answer, []);
  renderSuggestions(welcomeData.suggested_questions || []);
}

function updateVariants() {
  const procId = document.getElementById("ssProcedure").value;
  const proc = proceduresCache.find((p) => p.id === procId);
  const ssVariant = document.getElementById("ssVariant");
  ssVariant.innerHTML = "";
  for (const v of proc?.variants || []) {
    const opt = document.createElement("option");
    opt.value = v.id;
    opt.textContent = v.label;
    ssVariant.appendChild(opt);
  }
}

document.getElementById("ssProcedure").addEventListener("change", updateVariants);

document.getElementById("generateGuideBtn").addEventListener("click", async () => {
  const payload = {
    procedure_id: document.getElementById("ssProcedure").value,
    variant_id: document.getElementById("ssVariant").value,
    employee_name: document.getElementById("ssName").value,
    document_id: document.getElementById("ssDoc").value,
    email: document.getElementById("ssEmail").value,
    phone: document.getElementById("ssPhone").value,
  };
  const resp = await fetch("/api/self-service/guide", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await resp.json();
  document.getElementById("ssResult").classList.remove("hidden");
  document.getElementById("ssResultTitle").textContent = data.title;
  document.getElementById("ssResultContact").textContent = data.contact;
  const ul = document.getElementById("ssResultChecklist");
  ul.innerHTML = "";
  for (const item of data.checklist || []) {
    const li = document.createElement("li");
    li.textContent = item;
    ul.appendChild(li);
  }
  document.getElementById("ssResultTemplate").textContent = data.template;
  document.getElementById("ssResultSource").textContent = `Fuente: ${data.source}`;
});

document.getElementById("copyTemplateBtn").addEventListener("click", async () => {
  const txt = document.getElementById("ssResultTemplate").textContent;
  await navigator.clipboard.writeText(txt);
  const btn = document.getElementById("copyTemplateBtn");
  btn.textContent = "¡Copiado!";
  setTimeout(() => { btn.textContent = "Copiar texto"; }, 1800);
});

document.querySelectorAll(".seg-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".seg-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentChannel = btn.dataset.channel;
    chatMain.classList.toggle("whatsapp-mode", currentChannel === "whatsapp");
  });
});

document.getElementById("openSelfServiceBtn").addEventListener("click", () => {
  document.getElementById("selfServiceModal").classList.remove("hidden");
});
document.getElementById("closeModalBtn").addEventListener("click", () => {
  document.getElementById("selfServiceModal").classList.add("hidden");
});
document.getElementById("menuToggle").addEventListener("click", () => {
  sidebar.classList.toggle("open");
});
document.getElementById("clearChatBtn").addEventListener("click", () => {
  chatMessages.innerHTML = "";
  sessionId = "web-" + Math.random().toString(36).slice(2, 10);
  sendMessage("hola");
});

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(chatInput.value);
});

loadInitialState();
