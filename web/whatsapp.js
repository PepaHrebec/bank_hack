// Mock WhatsApp: a chat list with the three friends and one-to-one chats. Messages go through
// the server (/api/messages) and arrive live as "message" events. It only uses window.Phone.
(function () {
  const root = document.getElementById("whatsapp");
  if (!root) return;

  const state = { me: null, chats: [], convs: {}, open: null, seen: {} };
  let seenKey = null;

  root.innerHTML = `
    <div class="wa-view wa-list-view">
      <header class="wa-top"><span class="wa-title">WhatsApp</span></header>
      <div class="wa-tabs"><span class="on">Chaty</span><span>Stavy</span><span>Hovory</span></div>
      <div class="wa-list"></div>
    </div>
    <div class="wa-view wa-chat-view">
      <header class="wa-top wa-chat-top">
        <button type="button" class="wa-back" aria-label="Zpět">&#x2039;</button>
        <span class="wa-avatar"></span>
        <span class="wa-chat-name"></span>
      </header>
      <div class="wa-messages"></div>
      <div class="wa-error" hidden></div>
      <form class="wa-compose">
        <input type="text" class="wa-input" maxlength="1000" placeholder="Zpráva" autocomplete="off">
        <button type="submit" class="wa-send" aria-label="Odeslat">&#x27A4;</button>
      </form>
    </div>`;
  const listView = root.querySelector(".wa-list-view");
  const chatView = root.querySelector(".wa-chat-view");
  const listEl = root.querySelector(".wa-list");
  const messagesEl = root.querySelector(".wa-messages");
  const errorEl = root.querySelector(".wa-error");
  const input = root.querySelector(".wa-input");

  // ---- helpers ----

  const isOpen = () => root.classList.contains("open");

  function loadSeen() {
    try { state.seen = JSON.parse(localStorage.getItem(seenKey)) || {}; } catch { state.seen = {}; }
  }
  function markSeen(id, msgId) {
    if ((state.seen[id] || 0) >= msgId) return;
    state.seen[id] = msgId;
    try { localStorage.setItem(seenKey, JSON.stringify(state.seen)); } catch { /* storage may be blocked */ }
  }

  function stamp(iso) {
    const d = new Date(iso);
    const now = new Date();
    const hm = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
    if (d.toDateString() === now.toDateString()) return hm;
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (d.toDateString() === yesterday.toDateString()) return "včera";
    return `${d.getDate()}. ${d.getMonth() + 1}.`;
  }

  function avatar(id, name, cls) {
    const el = document.createElement("span");
    el.className = cls || "wa-avatar";
    el.style.background = Phone.colors[id] || "#888";
    el.textContent = Phone.initials(name);
    return el;
  }

  const chatOf = (id) => state.chats.find((c) => c.with === id);
  const unread = (c) => Boolean(c.last && c.last.sender !== state.me.id && c.last.id > (state.seen[c.with] || 0));

  // ---- rendering ----

  function renderList() {
    listEl.replaceChildren();
    for (const c of state.chats) {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "wa-row";
      const text = document.createElement("div");
      text.className = "wa-row-text";
      const head = document.createElement("div");
      head.className = "wa-row-head";
      const name = document.createElement("span");
      name.className = "wa-row-name";
      name.textContent = c.name;
      const time = document.createElement("span");
      time.className = "wa-row-time" + (unread(c) ? " unread" : "");
      time.textContent = c.last ? stamp(c.last.created_at) : "";
      head.append(name, time);
      const preview = document.createElement("div");
      preview.className = "wa-row-preview";
      const last = document.createElement("span");
      last.textContent = c.last ? (c.last.sender === state.me.id ? "Ty: " : "") + c.last.text : "Zatím žádné zprávy";
      preview.append(last);
      if (unread(c)) {
        const dot = document.createElement("i");
        dot.className = "wa-dot";
        preview.append(dot);
      }
      text.append(head, preview);
      row.append(avatar(c.with, c.name), text);
      row.addEventListener("click", () => openChat(c.with));
      listEl.append(row);
    }
  }

  function renderChat() {
    const id = state.open;
    if (id === null) return;
    const atBottom = messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 40;
    messagesEl.replaceChildren();
    for (const m of state.convs[id] || []) {
      const bubble = document.createElement("div");
      bubble.className = "wa-bubble " + (m.sender === state.me.id ? "out" : "in");
      const text = document.createElement("span");
      text.className = "wa-text";
      text.textContent = m.text;
      const time = document.createElement("small");
      time.textContent = stamp(m.created_at);
      bubble.append(text, time);
      messagesEl.append(bubble);
    }
    if (atBottom || !messagesEl.dataset.ready) messagesEl.scrollTop = messagesEl.scrollHeight;
    messagesEl.dataset.ready = "1";
  }

  function showView() {
    root.classList.toggle("in-chat", state.open !== null);
    listView.hidden = state.open !== null;
    chatView.hidden = state.open === null;
  }

  // ---- data ----

  async function refetch() {
    try {
      const s = await (await fetch("/api/state")).json();
      state.chats = s.chats;
      if (state.open !== null) {
        const msgs = await (await fetch(`/api/messages?with=${state.open}`)).json();
        if (Array.isArray(msgs)) state.convs[state.open] = msgs;
        const last = (state.convs[state.open] || []).at(-1);
        if (last) markSeen(state.open, last.id);
      }
    } catch { return; }
    renderList();
    renderChat();
  }

  function addMessage(m) {
    const other = m.sender === state.me.id ? m.recipient : m.sender;
    const conv = state.convs[other];
    if (conv && !conv.some((x) => x.id === m.id)) conv.push(m);
    const chat = chatOf(other);
    if (chat && (!chat.last || chat.last.id <= m.id)) chat.last = m;
    state.chats.sort((a, b) => (b.last ? b.last.id : 0) - (a.last ? a.last.id : 0));
    return other;
  }

  async function openChat(id) {
    state.open = id;
    delete messagesEl.dataset.ready;
    const chat = chatOf(id);
    root.querySelector(".wa-chat-name").textContent = chat ? chat.name : "";
    root.querySelector(".wa-chat-top .wa-avatar").replaceWith(avatar(id, chat ? chat.name : "?"));
    errorEl.hidden = true;
    showView();
    state.convs[id] = state.convs[id] || [];
    renderChat();
    await refetch();
    input.focus({ preventScroll: true });
  }

  function closeChat() {
    state.open = null;
    showView();
    renderList();
  }

  async function send(text) {
    errorEl.hidden = true;
    try {
      const r = await fetch("/api/messages", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ recipient: state.open, text }),
      });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail || "Zprávu se nepodařilo odeslat");
      addMessage(body);
      markSeen(state.open, body.id);
      renderChat();
    } catch (err) {
      errorEl.textContent = err.message || "Zprávu se nepodařilo odeslat";
      errorEl.hidden = false;
      input.value = text;
    }
  }

  // ---- events ----

  root.querySelector(".wa-back").addEventListener("click", closeChat);
  root.querySelector(".wa-compose").addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text || state.open === null) return;
    input.value = "";
    send(text);
  });

  Phone.onEvent((ev) => {
    if (ev.type === "connected") { if (state.me) refetch(); return; }
    if (ev.type !== "message" || !state.me) return;
    const m = ev.message;
    const other = addMessage(m);
    const viewing = isOpen() && state.open === other;
    if (viewing) markSeen(other, m.id);
    renderList();
    if (state.open === other) renderChat();
    if (m.sender !== state.me.id && !viewing) {
      const chat = chatOf(other);
      const name = chat ? chat.name : "WhatsApp";
      Phone.notify({
        title: name,
        body: m.text,
        color: Phone.colors[other],
        action: { label: "Otevřít chat", onClick: () => { Phone.openApp("whatsapp"); openChat(other); } },
      });
    }
  });

  root.addEventListener("app-open", () => {
    if (!state.me) return;
    if (state.open !== null) {
      const last = (state.convs[state.open] || []).at(-1);
      if (last) markSeen(state.open, last.id);
    }
    refetch();
  });

  showView();
  Phone.ready.then((me) => {
    state.me = me;
    seenKey = `wa-seen-${me.id}`;
    loadSeen();
    refetch();
  });
})();
