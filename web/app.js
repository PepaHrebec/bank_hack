// Placeholder bank app.
//   main     balance card (tap -> history), Contacts button, chat window (empty for now)
//   contacts Group Settle (not implemented yet), To be paid, and the other three people
//            (tap -> pay)
//   pay      Payment (send money) or Request (ask for money) with one contact
//   tobepaid open requests to me: individual ones and shares of group requests
//   history  payments from the database
// Talks to the shell only through window.Phone, so it can be swapped for the real app.
// Every screen is built once; refreshes only touch balance and history, so a person
// typing an amount keeps focus and their message line when someone else pays them.
(function () {
  const root = document.getElementById("app");
  let state = null;
  let ui = null; // elements updated on refresh / navigation
  let payTo = null; // contact id on the pay screen
  let mode = "payment"; // "payment" | "request" on the pay screen

  const ICONS = {
    back: '<svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    chevron: '<svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    contacts: '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.6" fill="currentColor"/><path d="M2.5 19.5c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6z" fill="currentColor"/><circle cx="17" cy="9" r="2.8" fill="currentColor" opacity=".55"/><path d="M15.8 13.7c3.3-.3 5.7 1.9 5.7 5.3h-4.3c0-2-.5-3.8-1.4-5.3z" fill="currentColor" opacity=".55"/></svg>',
    history: '<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.4-5.7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M3.5 4v4.5H8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 7.5V12l3 2" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    request: '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 8h6M9 12h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    settle: '<svg viewBox="0 0 24 24"><path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };

  const czk = (n) => `${n.toLocaleString("cs-CZ")} CZK`;
  const nameOf = (id) => state.people.find((p) => p.id === id).name;

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function icon(name, cls) {
    const i = el("span", "ico " + (cls || ""));
    i.innerHTML = ICONS[name]; // fixed SVG strings above, never user data
    return i;
  }

  function avatar(person) {
    const a = el("span", "avatar", Phone.initials(person.name));
    a.style.background = Phone.colors[person.id];
    return a;
  }

  function button(cls, ...children) {
    const b = el("button", cls);
    b.type = "button";
    b.append(...children);
    return b;
  }

  function header(title, back) {
    const h = el("div", "view-header");
    const b = button("back-btn", icon("back"));
    b.addEventListener("click", () => show(back));
    h.append(b, el("h2", null, title));
    return h;
  }

  async function load() {
    try {
      state = await (await fetch("/api/state")).json();
    } catch {
      return; // server unreachable; the next "connected" event retries
    }
    if (!ui) build();
    refresh();
  }

  function build() {
    const { me, people } = state;
    const others = people.filter((p) => p.id !== me.id);
    const views = {};

    // main
    const main = el("section", "view");
    const card = button("balance-card");
    card.style.setProperty("--accent", Phone.colors[me.id]);
    const balance = el("div", "balance-value");
    const top = el("div", "balance-top");
    top.append(el("span", "balance-label", "Balance"), icon("history", "balance-history"));
    card.append(top, balance);
    card.addEventListener("click", () => show("history"));
    const contactsBtn = button("big-btn", icon("contacts", "big-btn-icon"), el("span", null, "Contacts"), icon("chevron", "chev"));
    contactsBtn.addEventListener("click", () => show("contacts"));
    const chat = el("section", "chat"); // the smart chatbot goes here later
    main.append(card, contactsBtn, chat);
    views.main = main;

    // contacts
    const contacts = el("section", "view");
    const actions = el("div", "quick-actions");
    const toPayBadge = el("span", "badge");
    const toPayIcon = icon("request", "settle-icon");
    toPayIcon.append(toPayBadge);
    const toPayBtn = button("settle", toPayIcon, el("span", null, "To be paid"));
    toPayBtn.addEventListener("click", () => show("tobepaid"));
    actions.append(button("settle", icon("settle", "settle-icon"), el("span", null, "Group Settle")), toPayBtn);
    const list = el("div", "card-list");
    for (const p of others) {
      const row = button("contact", avatar(p), el("span", "contact-name", p.name), icon("chevron", "chev"));
      row.addEventListener("click", () => openPay(p.id));
      list.append(row);
    }
    contacts.append(header("Contacts", "main"), actions, list);
    views.contacts = contacts;

    // pay
    const pay = el("section", "view");
    const payHeader = header("Send money", "contacts");
    const payWho = el("div", "pay-who");
    const modes = el("div", "segmented");
    const modeButtons = {
      payment: button("seg active", "Payment"),
      request: button("seg", "Request"),
    };
    for (const [key, b] of Object.entries(modeButtons)) {
      b.addEventListener("click", () => setMode(key));
      modes.append(b);
    }
    const form = el("form", "pay-form");
    const amount = el("input", "field");
    Object.assign(amount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Amount (CZK)" });
    amount.id = "amount";
    const note = el("input", "field");
    Object.assign(note, { type: "text", maxLength: 80, placeholder: "Note (optional)" });
    note.id = "note";
    const sendBtn = el("button", "send-btn", "Send");
    sendBtn.type = "submit";
    const msg = el("div", "form-msg");
    form.append(modes, amount, note, sendBtn, msg);
    form.addEventListener("submit", (e) => { e.preventDefault(); send(); });
    pay.append(payHeader, payWho, form);
    views.pay = pay;

    // history
    const history = el("section", "view");
    const historyList = el("div", "card-list history-list");
    history.append(header("History", "main"), historyList);
    views.history = history;

    // to be paid
    const tobepaid = el("section", "view");
    const toPayList = el("div", "topay-list");
    tobepaid.append(header("To be paid", "contacts"), toPayList);
    views.tobepaid = tobepaid;

    root.replaceChildren(...Object.values(views));
    ui = {
      views, balance, payWho, amount, note, sendBtn, msg, historyList,
      payTitle: payHeader.querySelector("h2"), modeButtons, toPayList, toPayBadge,
    };
    show("main");
  }

  function show(name) {
    for (const [key, view] of Object.entries(ui.views)) view.classList.toggle("active", key === name);
    root.scrollTop = 0;
  }

  function openPay(id) {
    payTo = id;
    const person = { id, name: nameOf(id) };
    ui.payWho.replaceChildren(avatar(person), el("div", "pay-name", person.name));
    ui.amount.value = "";
    ui.note.value = "";
    setMode("payment");
    show("pay");
    ui.amount.focus();
  }

  function setMode(next) {
    mode = next;
    for (const [key, b] of Object.entries(ui.modeButtons)) b.classList.toggle("active", key === mode);
    ui.payTitle.textContent = mode === "payment" ? "Send money" : "Request money";
    ui.sendBtn.textContent = mode === "payment" ? "Send" : "Request";
    setMsg(null, "");
  }

  function refresh() {
    const { me, balance, history } = state;
    ui.balance.textContent = czk(balance);

    const rows = [];
    if (history.length === 0) rows.push(el("div", "empty", "No payments yet"));
    for (const p of history) {
      const outgoing = p.sender === me.id;
      const other = outgoing ? p.recipient : p.sender;
      const row = el("div", "tx");
      const info = el("div", "tx-info");
      info.append(el("div", "tx-name", `${outgoing ? "To" : "From"} ${nameOf(other)}`));
      const time = p.created_at.slice(11, 16);
      info.append(el("div", "tx-meta", p.note ? `${p.note} · ${time}` : time));
      row.append(avatar({ id: other, name: nameOf(other) }), info,
        el("div", "tx-amount " + (outgoing ? "out" : "in"), `${outgoing ? "−" : "+"}${czk(p.amount)}`));
      rows.push(row);
    }
    ui.historyList.replaceChildren(...rows);
    renderToPay();
  }

  function renderToPay() {
    const { me } = state;
    const toPay = state.to_pay || []; // older servers don't send it
    ui.toPayBadge.textContent = toPay.length ? String(toPay.length) : "";
    ui.toPayBadge.hidden = toPay.length === 0;

    const individual = toPay.filter((r) => !r.group);
    const group = toPay.filter((r) => r.group);
    const blocks = [];
    if (toPay.length === 0) blocks.push(el("div", "empty topay-empty", "Nothing to pay 🎉"));
    if (individual.length) {
      blocks.push(el("h3", "topay-section", "Individual"));
      const box = el("div", "card-list");
      for (const r of individual) box.append(requestRow(r));
      blocks.push(box);
    }
    if (group.length) {
      blocks.push(el("h3", "topay-section", "Group"));
      for (const r of group) {
        const box = el("div", "card-list group-card");
        const g = r.group;
        const head = el("div", "group-head");
        head.append(el("div", "group-title", g.title),
          el("div", "group-meta", `${nameOf(g.requester)} · total ${czk(g.total)}`));
        const members = el("div", "group-members");
        for (const m of g.members) {
          const chip = el("span", `member ${m.status}`);
          chip.append(avatar({ id: m.payer, name: nameOf(m.payer) }),
            el("span", null, m.payer === me.id ? "You" : nameOf(m.payer).split(" ")[0]),
            el("small", null, m.status === "paid" ? "✓ paid" : m.status === "declined" ? "declined" : czk(m.amount)));
          members.append(chip);
        }
        box.append(head, members, requestRow(r, "Your share"));
        blocks.push(box);
      }
    }
    ui.toPayList.replaceChildren(...blocks);
  }

  function requestRow(r, label) {
    const row = el("div", "req");
    const info = el("div", "tx-info");
    info.append(el("div", "tx-name", label || nameOf(r.requester)));
    if (r.note) info.append(el("div", "tx-meta", r.note));
    const top = el("div", "req-top");
    top.append(label ? icon("request", "req-icon") : avatar({ id: r.requester, name: nameOf(r.requester) }),
      info, el("div", "tx-amount", czk(r.amount)));
    const actions = el("div", "req-actions");
    const decline = button("req-btn decline", "Decline");
    const payBtn = button("req-btn pay", "Pay");
    const msg = el("div", "form-msg error");
    decline.addEventListener("click", () => answer(r.id, "decline", msg, [decline, payBtn]));
    payBtn.addEventListener("click", () => answer(r.id, "pay", msg, [decline, payBtn]));
    actions.append(decline, payBtn);
    row.append(top, actions, msg);
    return row;
  }

  async function answer(id, action, msg, buttons) {
    buttons.forEach((b) => { b.disabled = true; });
    msg.textContent = "";
    try {
      const r = await fetch(`/api/requests/${id}/${action}`, { method: "POST" });
      if (!r.ok) {
        let body = {};
        try { body = await r.json(); } catch { /* non-JSON error page */ }
        msg.textContent = body.detail || `Failed (${r.status})`;
        buttons.forEach((b) => { b.disabled = false; });
        return;
      }
      await load();
    } catch {
      msg.textContent = "Can't reach the bank. Try again.";
      buttons.forEach((b) => { b.disabled = false; });
    }
  }

  function setMsg(kind, text) {
    ui.msg.className = "form-msg" + (kind ? ` ${kind}` : "");
    ui.msg.textContent = text;
  }

  async function send() {
    setMsg(null, "");
    ui.sendBtn.disabled = true;
    const amount = ui.amount.value === "" ? null : Number(ui.amount.value);
    try {
      const requesting = mode === "request";
      const r = await fetch(requesting ? "/api/requests" : "/api/payments", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(requesting
          ? { payer: payTo, amount, note: ui.note.value }
          : { recipient: payTo, amount, note: ui.note.value }),
      });
      let body = {};
      try { body = await r.json(); } catch { /* non-JSON error page */ }
      if (!r.ok) {
        setMsg("error", body.detail || `Payment failed (${r.status})`);
        return;
      }
      ui.amount.value = "";
      ui.note.value = "";
      setMsg("ok", requesting
        ? `Requested ${czk(body.amount)} from ${nameOf(body.payer)}`
        : `Sent ${czk(body.amount)} to ${nameOf(body.recipient)}`);
      await load();
    } catch {
      setMsg("error", "Can't reach the bank. Try again.");
    } finally {
      ui.sendBtn.disabled = false;
    }
  }

  Phone.onEvent((event) => {
    if (event.type === "payment_received") {
      const note = event.payment.note ? `\n${event.payment.note}` : "";
      Phone.notify({ title: event.from, body: event.text + note, color: Phone.colors[event.payment.sender] });
      load();
    } else if (event.type === "request_received" || event.type === "request_declined") {
      const sender = event.type === "request_received" ? event.request.requester : event.request.payer;
      const note = event.request.note ? `\n${event.request.note}` : "";
      Phone.notify({ title: event.from, body: event.text + note, color: Phone.colors[sender] });
      load();
    } else if (["payment_sent", "request_sent", "requests_changed", "connected"].includes(event.type)) {
      load();
    }
  });

  Phone.ready.then(load);
})();
