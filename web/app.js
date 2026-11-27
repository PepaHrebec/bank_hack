// Placeholder bank app.
//   main     balance card (tap -> history), Contacts and QR tiles, chat window (empty for now)
//   groups   Group Settle: every group I'm in, "+ New group"
//   newgroup name a group and tick who's in it
//   group    one group: members, expenses (add / delete own while open), Approve for the creator
//   qr       a fixed QR code with amount and note fields under it (display only)
//   contacts Group Settle, To be paid, and the other three people
//            (tap -> pay)
//   pay      Payment (send money) or Request (ask for money) with one contact
//   tobepaid "Requested from me": open requests to me (individual and group shares) to pay
//            or decline; "Requested from others": requests I made and their status
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
  let openGroupId = null; // group shown on the group screen
  let currentView = null;
  let startExpense = null; // {amount, note} a new group starts with (from a card payment), or null

  const ICONS = {
    back: '<svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    chevron: '<svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    contacts: '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.6" fill="currentColor"/><path d="M2.5 19.5c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6z" fill="currentColor"/><circle cx="17" cy="9" r="2.8" fill="currentColor" opacity=".55"/><path d="M15.8 13.7c3.3-.3 5.7 1.9 5.7 5.3h-4.3c0-2-.5-3.8-1.4-5.3z" fill="currentColor" opacity=".55"/></svg>',
    history: '<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.4-5.7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M3.5 4v4.5H8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 7.5V12l3 2" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    request: '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 8h6M9 12h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    qr: '<svg viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></g><g fill="currentColor"><rect x="14" y="14" width="3" height="3"/><rect x="18" y="18" width="3" height="3"/><rect x="18" y="14" width="3" height="2"/><rect x="14" y="19" width="2" height="2"/></g></svg>',
    card: '<svg viewBox="0 0 24 24"><rect x="2.5" y="5" width="19" height="14" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M2.5 10h19" stroke="currentColor" stroke-width="2"/><path d="M6 15h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    settle: '<svg viewBox="0 0 24 24"><path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };

  const czk = (n) => `${n.toLocaleString("cs-CZ")} CZK`;
  // "2026-11-27T14:05:09" (the server computer's local time) -> "27.11.2026 14:05"
  const stamp = (iso) => `${+iso.slice(8, 10)}.${+iso.slice(5, 7)}.${iso.slice(0, 4)} ${iso.slice(11, 16)}`;
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
    const tiles = el("div", "main-tiles");
    const contactsBtn = button("big-btn", icon("contacts", "big-btn-icon"), el("span", null, "Contacts"));
    contactsBtn.addEventListener("click", () => show("contacts"));
    const qrBtn = button("big-btn", icon("qr", "big-btn-icon qr-tile-icon"), el("span", null, "QR code"));
    qrBtn.addEventListener("click", () => show("qr"));
    tiles.append(contactsBtn, qrBtn);
    const chat = el("section", "chat"); // the smart chatbot goes here later
    main.append(card, tiles, chat);
    views.main = main;

    // contacts
    const contacts = el("section", "view");
    const actions = el("div", "quick-actions");
    const toPayBadge = el("span", "badge");
    const toPayIcon = icon("request", "settle-icon");
    toPayIcon.append(toPayBadge);
    const toPayBtn = button("settle", toPayIcon, el("span", null, "To be paid"));
    toPayBtn.addEventListener("click", () => show("tobepaid"));
    const settleBtn = button("settle", icon("settle", "settle-icon"), el("span", null, "Group Settle"));
    settleBtn.addEventListener("click", () => show("groups"));
    actions.append(settleBtn, toPayBtn);
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
    const tabs = el("div", "segmented");
    const tabButtons = {
      me: button("seg active", "Requested from me"),
      others: button("seg", "Requested from others"),
    };
    const toPayList = el("div", "topay-list");
    const requestedList = el("div", "topay-list");
    requestedList.hidden = true;
    for (const [key, b] of Object.entries(tabButtons)) {
      b.addEventListener("click", () => {
        for (const [k, x] of Object.entries(tabButtons)) x.classList.toggle("active", k === key);
        toPayList.hidden = key !== "me";
        requestedList.hidden = key !== "others";
      });
      tabs.append(b);
    }
    tobepaid.append(header("To be paid", "contacts"), tabs, toPayList, requestedList);
    views.tobepaid = tobepaid;

    // groups
    const groups = el("section", "view");
    const newGroupBtn = button("big-btn", icon("settle", "big-btn-icon"), el("span", null, "New group"), icon("chevron", "chev"));
    newGroupBtn.addEventListener("click", () => openNewGroup());
    const groupsList = el("div", "groups-list");
    groups.append(header("Group Settle", "contacts"), newGroupBtn, groupsList);
    views.groups = groups;

    // new group
    const newgroup = el("section", "view");
    const ngForm = el("form", "pay-form");
    const ngName = el("input", "field");
    Object.assign(ngName, { type: "text", maxLength: 40, placeholder: "Group name (e.g. Chata)" });
    const ngPeople = el("div", "pick-list");
    const ngPicks = {};
    for (const p of others) {
      const box = el("input");
      box.type = "checkbox";
      ngPicks[p.id] = box;
      const row = el("label", "pick");
      row.append(box, avatar(p), el("span", "contact-name", p.name));
      ngPeople.append(row);
    }
    const ngBtn = el("button", "send-btn", "Create group");
    ngBtn.type = "submit";
    const ngMsg = el("div", "form-msg");
    const ngExpense = el("div", "ng-expense");
    ngExpense.hidden = true;
    ngForm.append(ngName, ngExpense, el("h3", "topay-section", "Who's in"), ngPeople, ngBtn, ngMsg);
    ngForm.addEventListener("submit", (e) => { e.preventDefault(); createGroup(); });
    newgroup.append(header("New group", "groups"), ngForm);
    views.newgroup = newgroup;

    // one group
    const group = el("section", "view");
    const groupHeader = header("", "groups");
    const groupInfo = el("div", "group-info");
    const expenseForm = el("form", "pay-form expense-form");
    const exAmount = el("input", "field");
    Object.assign(exAmount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Amount (CZK)" });
    const exDesc = el("input", "field");
    Object.assign(exDesc, { type: "text", maxLength: 60, placeholder: "What for (e.g. Cabin)" });
    const exBtn = el("button", "send-btn", "Add expense");
    exBtn.type = "submit";
    const exMsg = el("div", "form-msg");
    expenseForm.append(el("h3", "topay-section", "I paid"), exAmount, exDesc, exBtn, exMsg);
    expenseForm.addEventListener("submit", (e) => { e.preventDefault(); addExpense(); });
    const pickBox = el("div", "pick-payments");
    const expenseList = el("div", "group-expenses");
    const approveBox = el("div", "approve-box");
    group.append(groupHeader, groupInfo, expenseForm, pickBox, expenseList, approveBox);
    views.group = group;

    // qr
    const qr = el("section", "view");
    const qrCard = el("div", "qr-card");
    const qrImg = el("img", "qr-img");
    qrImg.src = "/static/qr.svg";
    qrImg.alt = "QR code";
    const qrCaption = el("div", "qr-caption", "Scan to pay");
    const qrAmount = el("input", "field");
    Object.assign(qrAmount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Amount (CZK)" });
    const qrNote = el("input", "field");
    Object.assign(qrNote, { type: "text", maxLength: 80, placeholder: "Note (optional)" });
    const updateCaption = () => {
      const amt = Number(qrAmount.value);
      const parts = [];
      if (qrAmount.value !== "" && amt > 0) parts.push(czk(amt));
      if (qrNote.value.trim()) parts.push(qrNote.value.trim());
      qrCaption.textContent = parts.length ? parts.join(" · ") : "Scan to pay";
    };
    qrAmount.addEventListener("input", updateCaption);
    qrNote.addEventListener("input", updateCaption);
    qrCard.append(qrImg, qrCaption);
    const qrForm = el("div", "pay-form");
    qrForm.append(qrAmount, qrNote);
    qr.append(header("QR code", "main"), qrCard, qrForm);
    views.qr = qr;

    root.replaceChildren(...Object.values(views));
    ui = {
      views, balance, payWho, amount, note, sendBtn, msg, historyList,
      payTitle: payHeader.querySelector("h2"), modeButtons, toPayList, toPayBadge, requestedList,
      groupsList, ngName, ngExpense, ngPicks, ngBtn, ngMsg,
      groupTitle: groupHeader.querySelector("h2"), groupInfo, expenseForm, exAmount, exDesc, exBtn, exMsg,
      expenseList, approveBox, pickBox,
    };
    show("main");
  }

  function show(name) {
    currentView = name;
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
      if (p.kind === "card") {
        const row = el("div", "tx");
        const info = el("div", "tx-info");
        info.append(el("div", "tx-name", p.note ? `Card · ${p.note}` : "Card payment"), el("div", "tx-meta", stamp(p.created_at)));
        row.append(icon("card", "avatar card-avatar"), info, el("div", "tx-amount out", `−${czk(p.amount)}`));
        rows.push(row);
        continue;
      }
      const outgoing = p.sender === me.id;
      const other = outgoing ? p.recipient : p.sender;
      const row = el("div", "tx");
      const info = el("div", "tx-info");
      info.append(el("div", "tx-name", `${outgoing ? "To" : "From"} ${nameOf(other)}`));
      const when = stamp(p.created_at);
      info.append(el("div", "tx-meta", p.note ? `${p.note} · ${when}` : when));
      row.append(avatar({ id: other, name: nameOf(other) }), info,
        el("div", "tx-amount " + (outgoing ? "out" : "in"), `${outgoing ? "−" : "+"}${czk(p.amount)}`));
      rows.push(row);
    }
    ui.historyList.replaceChildren(...rows);
    renderToPay();
    renderGroups();
    renderGroup();
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
        // A settled group can owe several people; this card is only about what's owed to r.requester.
        const sameBill = g.members.filter((m) => m.requester === r.requester);
        const total = sameBill.reduce((sum, m) => sum + m.amount, 0);
        const head = el("div", "group-head");
        head.append(el("div", "group-title", g.title),
          el("div", "group-meta", `To ${nameOf(r.requester)} · total ${czk(total)}`));
        const members = el("div", "group-members");
        for (const m of sameBill) {
          const chip = el("span", `member ${m.status}`);
          chip.append(avatar({ id: m.payer, name: nameOf(m.payer) }),
            el("span", null, m.payer === me.id ? "You" : nameOf(m.payer).split(" ")[0]),
            el("small", null, m.status === "paid" ? "✓ paid" : m.status === "declined" ? "declined" : czk(m.amount)));
          members.append(chip);
        }
        box.append(head, members, requestRow(r, `Your share to ${nameOf(r.requester).split(" ")[0]}`));
        blocks.push(box);
      }
    }
    ui.toPayList.replaceChildren(...blocks);
    renderRequested();
  }

  const STATUS = { open: "Waiting", paid: "Paid", declined: "Declined", cancelled: "Cancelled" };

  // ---- Group Settle ----

  const firstName = (id) => nameOf(id).split(" ")[0];
  const time = (iso) => iso.slice(11, 16);

  function avatars(ids) {
    const row = el("div", "avatar-row");
    for (const id of ids) row.append(avatar({ id, name: nameOf(id) }));
    return row;
  }

  function groupStatus(g) {
    return el("span", `status ${g.status === "open" ? "open" : "paid"}`, g.status === "open" ? "Open" : "Approved");
  }

  function renderGroups() {
    const list = state.groups || [];
    const cards = [];
    if (list.length === 0) cards.push(el("div", "empty topay-empty", "No groups yet"));
    for (const g of list) {
      const card = button("group-tile");
      const top = el("div", "req-top");
      const info = el("div", "tx-info");
      info.append(el("div", "group-title", g.name),
        el("div", "group-meta", g.creator === state.me.id ? "Created by me" : `Added by ${firstName(g.creator)}`));
      const right = el("div", "req-right");
      right.append(el("div", "tx-amount", czk(g.total)), groupStatus(g));
      top.append(info, right);
      card.append(top, avatars(g.members));
      card.addEventListener("click", () => openGroup(g.id));
      cards.push(card);
    }
    ui.groupsList.replaceChildren(...cards);
  }

  // prefill = {amount, note} from a card payment: the group starts with that expense, paid by me.
  function openNewGroup(prefill) {
    startExpense = prefill || null;
    ui.ngName.value = prefill ? prefill.note.slice(0, 40) : "";
    ui.ngExpense.hidden = !prefill;
    ui.ngExpense.textContent = prefill ? `Expense: ${czk(prefill.amount)} · paid by you` : "";
    for (const box of Object.values(ui.ngPicks)) box.checked = false;
    ui.ngMsg.className = "form-msg";
    ui.ngMsg.textContent = "";
    show("newgroup");
    ui.ngName.focus();
  }

  async function postJson(url, body, method = "POST") {
    const r = await fetch(url, {
      method,
      headers: { "content-type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    let data = {};
    try { data = await r.json(); } catch { /* non-JSON error page */ }
    if (!r.ok) throw new Error(data.detail || `Failed (${r.status})`);
    return data;
  }

  async function createGroup() {
    const members = Object.entries(ui.ngPicks).filter(([, b]) => b.checked).map(([id]) => Number(id));
    ui.ngBtn.disabled = true;
    try {
      const body = { name: ui.ngName.value, members };
      if (startExpense) body.expense = { amount: startExpense.amount, description: startExpense.note || "Card payment" };
      const g = await postJson("/api/groups", body);
      await load();
      openGroup(g.id);
    } catch (err) {
      ui.ngMsg.className = "form-msg error";
      ui.ngMsg.textContent = err.message === "Failed to fetch" ? "Can't reach the bank. Try again." : err.message;
    } finally {
      ui.ngBtn.disabled = false;
    }
  }

  function openGroup(id) {
    openGroupId = id;
    ui.exAmount.value = "";
    ui.exDesc.value = "";
    ui.exMsg.className = "form-msg";
    ui.exMsg.textContent = "";
    renderGroup();
    show("group");
  }

  function renderGroup() {
    const g = (state.groups || []).find((x) => x.id === openGroupId);
    if (!g) {
      // The group was deleted (or the data reset) while it was open: back to the list.
      if (currentView === "group") show("groups");
      return;
    }
    const mine = state.me.id;
    const isOpen = g.status === "open";
    ui.groupTitle.textContent = g.name;

    const info = el("div", "card-list group-summary");
    const top = el("div", "req-top");
    const meta = el("div", "tx-info");
    meta.append(el("div", "group-meta", g.creator === mine ? "Created by me" : `Created by ${nameOf(g.creator)}`),
      el("div", "group-total", czk(g.total)), el("div", "group-meta", "spent together"));
    top.append(meta, groupStatus(g));
    const people = el("div", "group-members");
    for (const id of g.members) {
      const chip = el("span", "member");
      chip.append(avatar({ id, name: nameOf(id) }), el("span", null, id === mine ? "You" : firstName(id)));
      people.append(chip);
    }
    info.append(top, people);
    ui.groupInfo.replaceChildren(info);

    ui.expenseForm.hidden = !isOpen;

    const rows = [];
    rows.push(el("h3", "topay-section", "Expenses"));
    const box = el("div", "card-list");
    if (g.expenses.length === 0) box.append(el("div", "empty", "No expenses yet"));
    for (const e of g.expenses) {
      const row = el("div", "tx");
      const text = el("div", "tx-info");
      text.append(el("div", "tx-name", e.description),
        el("div", "tx-meta", `${e.payer === mine ? "You" : nameOf(e.payer)} paid · ${time(e.created_at)}`));
      row.append(avatar({ id: e.payer, name: nameOf(e.payer) }), text, el("div", "tx-amount", czk(e.amount)));
      if (isOpen && e.payer === mine) {
        const del = button("del-btn", "✕");
        del.title = "Delete";
        del.addEventListener("click", () => deleteExpense(e.id, del));
        row.append(del);
      }
      box.append(row);
    }
    rows.push(box);
    ui.expenseList.replaceChildren(...rows);

    ui.pickBox.replaceChildren(...(isOpen ? pickFromHistory(g) : []));

    const approve = [];
    if (isOpen && g.creator === mine) {
      const btn = button("send-btn approve-btn", "Approve and settle");
      const msg = el("div", "form-msg");
      btn.addEventListener("click", () => approveGroup(g.id, btn, msg));
      approve.push(el("div", "approve-hint", "When everyone has added what they paid, approve to lock the group and send the payment requests."), btn, msg);
    } else if (isOpen) {
      approve.push(el("div", "approve-hint", `Waiting for ${firstName(g.creator)} to approve.`));
    } else {
      approve.push(el("div", "approve-hint", g.requests_sent > 0
        ? "Approved: payment requests were sent. Check To be paid."
        : "Approved: everyone is already even, no requests needed."));
    }
    if (g.creator === mine) {
      const del = button("delete-group-btn", "Delete group");
      const msg = el("div", "form-msg");
      del.addEventListener("click", () => deleteGroup(g, del, msg));
      approve.push(del, msg);
    }
    ui.approveBox.replaceChildren(...approve);
  }

  // My outgoing payments (card payments and transfers I sent) not yet in this group.
  function pickFromHistory(g) {
    const mine = state.me.id;
    const used = new Set(g.expenses.filter((e) => e.source_kind).map((e) => `${e.source_kind}:${e.source_id}`));
    const payments = (state.history || []).filter((h) =>
      (h.kind === "card" || (h.kind === "transfer" && h.sender === mine)) && !used.has(`${h.kind}:${h.id}`));
    if (payments.length === 0) return [];
    const box = el("div", "card-list");
    for (const h of payments.slice(0, 6)) {
      const row = el("div", "tx");
      const info = el("div", "tx-info");
      const label = h.kind === "card"
        ? (h.note ? `Card · ${h.note}` : "Card payment")
        : (h.note || `Payment to ${nameOf(h.recipient)}`);
      info.append(el("div", "tx-name", label), el("div", "tx-meta", stamp(h.created_at)));
      const add = button("add-btn", "Add");
      const msg = el("div", "form-msg error");
      add.addEventListener("click", () => addFromHistory(h, add, msg));
      row.append(icon(h.kind === "card" ? "card" : "contacts", "req-icon"), info,
        el("div", "tx-amount", czk(h.amount)), add);
      box.append(row, msg);
    }
    return [el("h3", "topay-section", "Or pick from my payments"), box];
  }

  async function addFromHistory(h, btn, msg) {
    btn.disabled = true;
    msg.textContent = "";
    try {
      await postJson(`/api/groups/${openGroupId}/expenses`, { source: { kind: h.kind, id: h.id } });
      await load();
    } catch (err) {
      msg.textContent = err.message === "Failed to fetch" ? "Can't reach the bank. Try again." : err.message;
      btn.disabled = false;
    }
  }

  async function deleteGroup(g, btn, msg) {
    const sent = g.requests_sent > 0 ? " Payment requests that aren't paid yet will be cancelled." : "";
    if (!window.confirm(`Delete "${g.name}" for everyone?${sent}`)) return;
    btn.disabled = true;
    try {
      await postJson(`/api/groups/${g.id}`, undefined, "DELETE");
      openGroupId = null;
      show("groups");
      await load();
    } catch (err) {
      msg.className = "form-msg error";
      msg.textContent = err.message === "Failed to fetch" ? "Can't reach the bank. Try again." : err.message;
      btn.disabled = false;
    }
  }

  async function addExpense() {
    const amount = ui.exAmount.value === "" ? null : Number(ui.exAmount.value);
    ui.exBtn.disabled = true;
    ui.exMsg.className = "form-msg";
    ui.exMsg.textContent = "";
    try {
      await postJson(`/api/groups/${openGroupId}/expenses`, { amount, description: ui.exDesc.value });
      ui.exAmount.value = "";
      ui.exDesc.value = "";
      await load();
    } catch (err) {
      ui.exMsg.className = "form-msg error";
      ui.exMsg.textContent = err.message === "Failed to fetch" ? "Can't reach the bank. Try again." : err.message;
    } finally {
      ui.exBtn.disabled = false;
    }
  }

  async function deleteExpense(id, btn) {
    btn.disabled = true;
    try {
      await postJson(`/api/groups/${openGroupId}/expenses/${id}`, undefined, "DELETE");
      await load();
    } catch {
      btn.disabled = false;
    }
  }

  async function approveGroup(id, btn, msg) {
    btn.disabled = true;
    try {
      await postJson(`/api/groups/${id}/approve`);
      await load();
    } catch (err) {
      msg.className = "form-msg error";
      msg.textContent = err.message === "Failed to fetch" ? "Can't reach the bank. Try again." : err.message;
      btn.disabled = false;
    }
  }

  // Requests I made. Group requests come back as one row per member; show one card per group.
  function renderRequested() {
    const mine = state.requested || [];
    const blocks = [];
    if (mine.length === 0) blocks.push(el("div", "empty topay-empty", "You haven't requested anything"));
    const individual = mine.filter((r) => !r.group);
    if (individual.length) {
      blocks.push(el("h3", "topay-section", "Individual"));
      const box = el("div", "card-list");
      for (const r of individual) {
        const row = el("div", "req");
        const info = el("div", "tx-info");
        info.append(el("div", "tx-name", nameOf(r.payer)));
        info.append(el("div", "tx-meta", [r.note, r.created_at.slice(11, 16)].filter(Boolean).join(" · ")));
        const right = el("div", "req-right");
        right.append(el("div", "tx-amount", czk(r.amount)), el("span", `status ${r.status}`, STATUS[r.status]));
        const top = el("div", "req-top");
        top.append(avatar({ id: r.payer, name: nameOf(r.payer) }), info, right);
        row.append(top);
        box.append(row);
      }
      blocks.push(box);
    }
    const groups = new Map();
    for (const r of mine) if (r.group && !groups.has(r.group.id)) groups.set(r.group.id, r.group);
    if (groups.size) {
      blocks.push(el("h3", "topay-section", "Group"));
      for (const g of groups.values()) {
        // Only the rows owed to me; a settled group can also hold debts between other members.
        const owedToMe = g.members.filter((m) => m.requester === state.me.id);
        const total = owedToMe.reduce((sum, m) => sum + m.amount, 0);
        const box = el("div", "card-list group-card");
        const head = el("div", "group-head");
        const paid = owedToMe.filter((m) => m.status === "paid").reduce((sum, m) => sum + m.amount, 0);
        head.append(el("div", "group-title", g.title), el("div", "group-meta", `${czk(paid)} of ${czk(total)} paid`));
        const list = el("div", "group-rows");
        for (const m of owedToMe) {
          const row = el("div", "req-top group-row");
          const right = el("div", "req-right");
          right.append(el("div", "tx-amount", czk(m.amount)), el("span", `status ${m.status}`, STATUS[m.status]));
          row.append(avatar({ id: m.payer, name: nameOf(m.payer) }), el("div", "tx-info tx-name", nameOf(m.payer)), right);
          list.append(row);
        }
        box.append(head, list);
        blocks.push(box);
      }
    }
    ui.requestedList.replaceChildren(...blocks);
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
      const id = event.request.id;
      // A request from a friend can be answered right in the notification.
      const answer = (action, done) => async () => {
        await postJson(`/api/requests/${id}/${action}`);
        await load();
        return done;
      };
      Phone.notify({
        title: event.from, body: event.text + note, color: Phone.colors[sender],
        actions: event.type === "request_received" ? [
          { label: "Decline", secondary: true, onClick: answer("decline", "Declined") },
          { label: "Pay", onClick: answer("pay", `Paid ${czk(event.request.amount)} ✓`) },
        ] : undefined,
      });
      load();
    } else if (event.type === "card_payment") {
      const prefill = { amount: event.payment.amount, note: event.payment.note };
      Phone.notify({
        title: "George", body: event.text, color: "#3b6cff",
        action: { label: "Group Settle", onClick: () => openNewGroup(prefill) },
      });
      load();
    } else if (event.type === "group_deleted") {
      Phone.notify({ title: event.from, body: event.text, color: "#8e8e93" });
      load();
    } else if (event.type === "group_added") {
      Phone.notify({ title: event.from, body: event.text, color: Phone.colors[event.group.creator] });
      load();
    } else if (["payment_sent", "request_sent", "requests_changed", "group_changed", "connected"].includes(event.type)) {
      load();
    }
  });

  // Presenter control (outside the phone): pay by card without opening the bank app.
  const demoAside = document.getElementById("demoAside");
  document.getElementById("demoChip").addEventListener("click", () => demoAside.classList.add("open"));
  document.getElementById("demoClose").addEventListener("click", () => demoAside.classList.remove("open"));
  const demoForm = document.getElementById("demoPay");
  const demoMsg = document.getElementById("demoMsg");
  demoForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const amount = document.getElementById("demoAmount");
    const note = document.getElementById("demoNote");
    const btn = demoForm.querySelector("button");
    btn.disabled = true;
    demoMsg.className = "demo-msg";
    demoMsg.textContent = "";
    try {
      await postJson("/api/card-payments", { amount: amount.value === "" ? null : Number(amount.value), note: note.value });
      amount.value = "";
      note.value = "";
      demoMsg.className = "demo-msg ok";
      demoMsg.textContent = "Paid";
    } catch (err) {
      demoMsg.className = "demo-msg error";
      demoMsg.textContent = err.message === "Failed to fetch" ? "Can't reach the bank." : err.message;
    } finally {
      btn.disabled = false;
    }
  });

  Phone.ready.then(load);
})();
