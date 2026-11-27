// Placeholder bank app.
//   main     balance card (tap -> history), Contacts button, chat window (empty for now)
//   contacts Settle Up and To be paid (requests from Settle Up; both not implemented yet)
//            and the other three people (tap -> pay)
//   pay      send money to one contact
//   history  payments from the database
// Talks to the shell only through window.Phone, so it can be swapped for the real app.
// Every screen is built once; refreshes only touch balance and history, so a person
// typing an amount keeps focus and their message line when someone else pays them.
(function () {
  const root = document.getElementById("app");
  let state = null;
  let ui = null; // elements updated on refresh / navigation
  let payTo = null; // contact id on the pay screen

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
    actions.append(
      button("settle", icon("settle", "settle-icon"), el("span", null, "Settle Up")),
      button("settle", icon("request", "settle-icon"), el("span", null, "To be paid")),
    );
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
    const payWho = el("div", "pay-who");
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
    form.append(amount, note, sendBtn, msg);
    form.addEventListener("submit", (e) => { e.preventDefault(); send(); });
    pay.append(header("Send money", "contacts"), payWho, form);
    views.pay = pay;

    // history
    const history = el("section", "view");
    const historyList = el("div", "card-list history-list");
    history.append(header("History", "main"), historyList);
    views.history = history;

    root.replaceChildren(...Object.values(views));
    ui = { views, balance, payWho, amount, note, sendBtn, msg, historyList };
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
    setMsg(null, "");
    show("pay");
    ui.amount.focus();
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
      const r = await fetch("/api/payments", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ recipient: payTo, amount, note: ui.note.value }),
      });
      let body = {};
      try { body = await r.json(); } catch { /* non-JSON error page */ }
      if (!r.ok) {
        setMsg("error", body.detail || `Payment failed (${r.status})`);
        return;
      }
      ui.amount.value = "";
      ui.note.value = "";
      setMsg("ok", `Sent ${czk(body.amount)} to ${nameOf(body.recipient)}`);
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
    } else if (event.type === "payment_sent" || event.type === "connected") {
      load();
    }
  });

  Phone.ready.then(load);
})();
