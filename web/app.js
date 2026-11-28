// Placeholder bank app.
//   main     balance card with today's change (tap -> history), Friends and QR tiles,
//            chat with Geoff (read-only questions about my payments)
// It also fills the home-screen widget (Phone.widget) with the balance and today's change.
//   groups   Group Settle: every group I'm in, "+ New group"
//   newgroup name a group and tick who's in it
//   group    one group: members, expenses (add / delete own while open), Approve for the creator
//   qr       a fixed QR code with amount and note fields under it (display only)
//   contacts Friends: Group Settle, To be paid, my friends (tap -> pay) and "Přidat přítele"
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
  let accountForm = null; // {account, msg} of the "Zaplatit" view
  let startExpense = null; // {amount, note} a new group starts with (from a card payment), or null

  const ICONS = {
    back: '<svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    chevron: '<svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    contacts: '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.6" fill="currentColor"/><path d="M2.5 19.5c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6z" fill="currentColor"/><circle cx="17" cy="9" r="2.8" fill="currentColor" opacity=".55"/><path d="M15.8 13.7c3.3-.3 5.7 1.9 5.7 5.3h-4.3c0-2-.5-3.8-1.4-5.3z" fill="currentColor" opacity=".55"/></svg>',
    history: '<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.4-5.7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M3.5 4v4.5H8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 7.5V12l3 2" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    request: '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 8h6M9 12h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    qr: '<svg viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></g><g fill="currentColor"><rect x="14" y="14" width="3" height="3"/><rect x="18" y="18" width="3" height="3"/><rect x="18" y="14" width="3" height="2"/><rect x="14" y="19" width="2" height="2"/></g></svg>',
    card: '<svg viewBox="0 0 24 24"><rect x="2.5" y="5" width="19" height="14" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M2.5 10h19" stroke="currentColor" stroke-width="2"/><path d="M6 15h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    arrowin: '<svg viewBox="0 0 24 24"><path d="M12 4v13M6 11.5l6 6 6-6M5 20h14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    settle: '<svg viewBox="0 0 24 24"><path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    personadd: '<svg viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="9.5" cy="8" r="3.4"/><path d="M3 19c0-3.4 2.9-5.5 6.5-5.5S16 15.6 16 19M19 8v6M16 11h6"/></g></svg>',
  };

  const czk = (n) => `${n.toLocaleString("cs-CZ")} Kč`;
  // Today's balance change, e.g. "+250 Kč dnes", with a class for its colour.
  function showChange(e, n) {
    e.textContent = `${n > 0 ? "+" : n < 0 ? "−" : "±"}${czk(Math.abs(n))} dnes`;
    e.classList.toggle("up", n > 0);
    e.classList.toggle("down", n < 0);
  }
  // "2026-11-27T14:05:09" (the server computer's local time) -> "27.11.2026 14:05"
  const stamp = (iso) => `${+iso.slice(8, 10)}.${+iso.slice(5, 7)}.${iso.slice(0, 4)} ${iso.slice(11, 16)}`;
  const nameOf = (id) => state.people.find((p) => p.id === id).name;

  // fetch() rejects with a TypeError on a network failure; its message is English and browser-specific.
  function errText(err, retry = true) {
    if (err instanceof TypeError) return retry ? "Banku se nepodařilo zastihnout. Zkus to znovu." : "Banku se nepodařilo zastihnout.";
    return err.message;
  }

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
    const change = el("div", "balance-change");
    const top = el("div", "balance-top");
    top.append(el("span", "balance-label", "Zůstatek"), icon("history", "balance-history"));
    card.append(top, balance, change);
    card.addEventListener("click", () => show("history"));
    const tiles = el("div", "main-tiles");
    const contactsBtn = button("big-btn", icon("contacts", "big-btn-icon"), el("span", null, "Přátelé"));
    contactsBtn.addEventListener("click", () => show("contacts"));
    const qrBtn = button("big-btn", icon("qr", "big-btn-icon qr-tile-icon"), el("span", null, "QR kód"));
    qrBtn.addEventListener("click", () => show("qr"));
    const payAccountBtn = button("big-btn", icon("card", "big-btn-icon"), el("span", null, "Zaplatit"));
    payAccountBtn.addEventListener("click", () => openAccountPay());
    tiles.append(contactsBtn, qrBtn, payAccountBtn);
    const chat = buildChat();
    const recToggle = button("rec-toggle");
    recToggle.addEventListener("click", toggleRecording);
    const recInfo = el("div", "rec-info");
    recInfo.hidden = true;
    main.append(card, tiles, recToggle, recInfo, chat);
    views.main = main;

    // contacts
    const contacts = el("section", "view");
    const actions = el("div", "quick-actions");
    const toPayBadge = el("span", "badge");
    const toPayIcon = icon("request", "settle-icon");
    toPayIcon.append(toPayBadge);
    const toPayBtn = button("settle", toPayIcon, el("span", null, "K zaplacení"));
    toPayBtn.addEventListener("click", () => show("tobepaid"));
    const settleBtn = button("settle", icon("settle", "settle-icon"), el("span", null, "Skupinové vyrovnání"));
    settleBtn.addEventListener("click", () => show("groups"));
    const addFriendBtn = button("settle", icon("personadd", "settle-icon"), el("span", null, "Přidat přítele"));
    addFriendBtn.addEventListener("click", showAddFriendPopup);
    actions.append(settleBtn, toPayBtn, addFriendBtn);
    const friendList = el("div", "card-list");
    contacts.append(header("Přátelé", "main"), actions, friendList);
    views.contacts = contacts;

    // pay
    const pay = el("section", "view");
    const payHeader = header("Poslat peníze", "contacts");
    const payWho = el("div", "pay-who");
    const modes = el("div", "segmented");
    const modeButtons = {
      payment: button("seg active", "Platba"),
      request: button("seg", "Žádost"),
    };
    for (const [key, b] of Object.entries(modeButtons)) {
      b.addEventListener("click", () => setMode(key));
      modes.append(b);
    }
    const form = el("form", "pay-form");
    const amount = el("input", "field");
    Object.assign(amount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Částka (Kč)" });
    amount.id = "amount";
    const note = el("input", "field");
    Object.assign(note, { type: "text", maxLength: 80, placeholder: "Poznámka (volitelné)" });
    note.id = "note";
    const sendBtn = el("button", "send-btn", "Poslat");
    sendBtn.type = "submit";
    const msg = el("div", "form-msg");
    form.append(modes, amount, note, sendBtn, msg);
    form.addEventListener("submit", (e) => { e.preventDefault(); send(); });
    pay.append(payHeader, payWho, form);
    views.pay = pay;

    // history
    const history = el("section", "view");
    const historyList = el("div", "card-list history-list");
    history.append(header("Historie", "main"), historyList);
    views.history = history;

    // to be paid
    const tobepaid = el("section", "view");
    const tabs = el("div", "segmented");
    const tabButtons = {
      me: button("seg active", "Přijaté žádosti"),
      others: button("seg", "Moje žádosti"),
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
    tobepaid.append(header("K zaplacení", "contacts"), tabs, toPayList, requestedList);
    views.tobepaid = tobepaid;

    // groups
    const groups = el("section", "view");
    const newGroupBtn = button("big-btn", icon("settle", "big-btn-icon"), el("span", null, "Nová skupina"), icon("chevron", "chev"));
    newGroupBtn.addEventListener("click", () => openNewGroup());
    const groupsList = el("div", "groups-list");
    groups.append(header("Skupinové vyrovnání", "contacts"), newGroupBtn, groupsList);
    views.groups = groups;

    // new group
    const newgroup = el("section", "view");
    const ngForm = el("form", "pay-form");
    const ngName = el("input", "field");
    Object.assign(ngName, { type: "text", maxLength: 40, placeholder: "Název skupiny (např. Chata)" });
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
    const ngBtn = el("button", "send-btn", "Vytvořit skupinu");
    ngBtn.type = "submit";
    const ngMsg = el("div", "form-msg");
    const ngExpense = el("div", "ng-expense");
    ngExpense.hidden = true;
    ngForm.append(ngName, ngExpense, el("h3", "topay-section", "Koho pozvat"), ngPeople, ngBtn, ngMsg);
    ngForm.addEventListener("submit", (e) => { e.preventDefault(); createGroup(); });
    newgroup.append(header("Nová skupina", "groups"), ngForm);
    views.newgroup = newgroup;

    // one group
    const group = el("section", "view");
    const groupHeader = header("", "groups");
    const groupInfo = el("div", "group-info");
    const expenseForm = el("form", "pay-form expense-form");
    const exAmount = el("input", "field");
    Object.assign(exAmount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Částka (Kč)" });
    const exDesc = el("input", "field");
    Object.assign(exDesc, { type: "text", maxLength: 60, placeholder: "Za co (např. Chata)" });
    const exBtn = el("button", "send-btn", "Přidat výdaj");
    exBtn.type = "submit";
    const exMsg = el("div", "form-msg");
    expenseForm.append(el("h3", "topay-section", "Zaplaceno mnou"), exAmount, exDesc, exBtn, exMsg);
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
    qrImg.alt = "QR kód";
    const qrCaption = el("div", "qr-caption", "Naskenuj a zaplať");
    const qrAmount = el("input", "field");
    Object.assign(qrAmount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Částka (Kč)" });
    const qrNote = el("input", "field");
    Object.assign(qrNote, { type: "text", maxLength: 80, placeholder: "Poznámka (volitelné)" });
    const updateCaption = () => {
      const amt = Number(qrAmount.value);
      const parts = [];
      if (qrAmount.value !== "" && amt > 0) parts.push(czk(amt));
      if (qrNote.value.trim()) parts.push(qrNote.value.trim());
      qrCaption.textContent = parts.length ? parts.join(" · ") : "Naskenuj a zaplať";
    };
    qrAmount.addEventListener("input", updateCaption);
    qrNote.addEventListener("input", updateCaption);
    qrCard.append(qrImg, qrCaption);
    const qrForm = el("div", "pay-form");
    qrForm.append(qrAmount, qrNote);
    qr.append(header("QR kód", "main"), qrCard, qrForm);
    views.qr = qr;

    // confirm (paying a request); filled in by openConfirm
    const confirm = el("section", "view");
    const confirmHead = el("div", "view-header");
    const confirmBack = button("back-btn", icon("back"));
    confirmBack.addEventListener("click", () => show(confirmReturn));
    confirmHead.append(confirmBack, el("h2", null, "Potvrzení platby"));
    const confirmBody = el("div", "confirm-body");
    const confirmMsg = el("div", "form-msg error");
    const confirmCancel = button("confirm-btn secondary", "Zrušit");
    confirmCancel.addEventListener("click", () => show(confirmReturn));
    const confirmOk = button("confirm-btn", "Potvrdit platbu");
    confirmOk.addEventListener("click", payConfirmed);
    const confirmActions = el("div", "confirm-actions");
    confirmActions.append(confirmCancel, confirmOk);
    confirm.append(confirmHead, confirmBody, confirmMsg, confirmActions);
    views.confirm = confirm;
    views.accountPay = buildAccountPay();

    root.replaceChildren(...Object.values(views));

    // home-screen widget
    const widgetHead = el("div", "widget-head");
    const logo = el("img", "widget-logo");
    logo.src = "/static/icons/geoff.svg";
    logo.alt = "";
    widgetHead.append(logo, el("span", null, "Geoff"));
    const widgetBalance = el("div", "widget-balance");
    const widgetChange = el("div", "widget-change");
    const widgetRecent = el("div", "widget-recent");
    const widgetBody = el("div", "widget-body");
    widgetBody.append(el("div", "widget-label", "Zůstatek"), widgetBalance, widgetChange);
    const wRecToggle = button("rec-toggle widget-rec");
    // The widget opens Geoff on tap; the toggle must not.
    wRecToggle.addEventListener("click", (e) => { e.stopPropagation(); toggleRecording(); });
    const wRecInfo = el("div", "rec-info");
    wRecInfo.hidden = true;
    widgetBody.append(wRecToggle, wRecInfo);
    Phone.widget.replaceChildren(widgetHead, widgetRecent, widgetBody);

    ui = {
      views, friendList, balance, change, recToggles: [recToggle, wRecToggle], recInfos: [recInfo, wRecInfo], widgetBalance, widgetChange, widgetRecent, payWho, amount, note, sendBtn, msg, historyList,
      payTitle: payHeader.querySelector("h2"), modeButtons, toPayList, toPayBadge, requestedList,
      groupsList, ngName, ngExpense, ngPicks, ngBtn, ngMsg,
      groupTitle: groupHeader.querySelector("h2"), groupInfo, expenseForm, exAmount, exDesc, exBtn, exMsg,
      expenseList, approveBox, pickBox,
      confirmBody, confirmMsg, confirmActions, confirmCancel, confirmOk,
    };
    show("main");
  }

  // "Zaplatit": pay to a Czech bank account number; the server decides whether it is valid.
  function buildAccountPay() {
    const view = el("section", "view");
    const account = el("input", "field account-number");
    Object.assign(account, { type: "text", maxLength: 30, inputMode: "text", autocomplete: "off", placeholder: "123456-1234567890" });
    const bank = el("select", "field account-bank");
    bank.append(new Option("Vyber banku", ""));
    // Loaded on demand; a failed fetch is simply retried the next time the form opens.
    let banksLoading = null;
    const loadBanks = () => {
      if (bank.options.length > 1) return Promise.resolve();
      if (banksLoading) return banksLoading;
      return banksLoading = fetch("/api/banks").then((r) => {
        if (!r.ok) throw new Error("banks");
        return r.json();
      }).then((list) => {
        for (const b of list) bank.append(new Option(`${b.code} – ${b.name}`, b.code));
      }).catch(() => {}).finally(() => { banksLoading = null; });
    };
    loadBanks();
    // A pasted "number/bank" is split: the bank code goes into the select (if it is listed).
    const splitPasted = () => {
      const m = account.value.match(/^(.*?)\s*\/\s*(\d{4})\s*$/);
      if (!m) return;
      account.value = m[1];
      if ([...bank.options].some((o) => o.value === m[2])) bank.value = m[2];
    };
    const accountRow = el("div", "account-row");
    accountRow.append(account, el("span", "account-slash", "/"), bank);
    const hint = el("div", "account-hint");
    hint.hidden = true;
    // Bank 0800 is Geoff: say who owns the account, using the people the state already lists.
    const updateHint = () => {
      // Same normalisation as the server: leading zeros of prefix and number are dropped separately.
      const [number, prefix = ""] = account.value.replace(/\s+/g, "").split("-").reverse();
      const strip = (digits) => digits.replace(/^0+/, "");
      const full = `${strip(prefix) ? `${strip(prefix)}-` : ""}${strip(number)}/${bank.value}`;
      const contact = contactName(full);
      if (contact) {
        const opt = [...bank.options].find((o) => o.value === bank.value);
        const bankName = opt ? opt.text.split(" – ").slice(1).join(" – ") : "";
        hint.hidden = false;
        hint.textContent = `${contact} nepoužívá Geoff – platba odejde do banky ${bankName || bank.value}.`;
        return;
      }
      hint.hidden = bank.value !== "0800";
      if (hint.hidden) return;
      const owner = (state?.people || []).find((p) => p.account === full);
      hint.textContent = !account.value.trim() ? "Účet je u Geoff – platba proběhne okamžitě."
        : owner && owner.id === state.me.id ? "To je tvůj vlastní účet"
        : owner ? `${owner.name} používá Geoff – peníze dorazí hned.`
        : "Účet je u Geoff – platba proběhne okamžitě.";
    };
    account.addEventListener("input", () => { splitPasted(); updateHint(); });
    bank.addEventListener("change", updateHint);
    const amount = el("input", "field");
    Object.assign(amount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Částka (Kč)" });
    const note = el("input", "field");
    Object.assign(note, { type: "text", maxLength: 80, placeholder: "Zpráva pro příjemce (volitelné)" });
    const btn = el("button", "send-btn", "Zaplatit");
    btn.type = "submit";
    const msg = el("div", "form-msg");
    const form = el("form", "pay-form");
    form.append(el("label", "form-label", "Číslo účtu"), accountRow, hint, amount, note, btn, msg);
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.className = "form-msg";
      msg.textContent = "";
      splitPasted();
      updateHint();
      if (!bank.value) {
        msg.className = "form-msg error";
        msg.textContent = "Vyber banku";
        return;
      }
      btn.disabled = true;
      try {
        const p = await postJson("/api/account-payments", {
          account: `${account.value.replace(/\s+/g, "")}/${bank.value}`, amount: amount.value === "" ? null : Number(amount.value), note: note.value,
        });
        account.value = amount.value = note.value = "";
        bank.value = "";
        updateHint();
        msg.className = "form-msg ok";
        msg.textContent = p.kind === "transfer" ? `Posláno ${czk(p.amount)} pro ${nameOf(p.recipient)}`
          : `Zaplaceno ${czk(p.amount)} na účet ${p.account}`;
        await load();
      } catch (err) {
        msg.className = "form-msg error";
        msg.textContent = errText(err);
      } finally {
        btn.disabled = false;
      }
    });
    view.append(header("Zaplatit", "main"), form);
    accountForm = {
      account, msg, loadBanks,
      // Prefill from a contact: "number/bank" split into the two fields.
      fill(full) {
        const [number, code] = full.split("/");
        account.value = number;
        bank.value = [...bank.options].some((o) => o.value === code) ? code : "";
        updateHint();
        // The bank list may still be loading: select the bank once it is there.
        if (!bank.value) loadBanks().then(() => { if (!bank.value) { bank.value = code; updateHint(); } });
      },
    };
    return view;
  }

  function openAccountPay(full) {
    accountForm.msg.className = "form-msg";
    accountForm.msg.textContent = "";
    accountForm.loadBanks();
    if (full) accountForm.fill(full);
    show("accountPay");
    if (!full) accountForm.account.focus();
  }

  function show(name) {
    currentView = name;
    for (const [key, view] of Object.entries(ui.views)) view.classList.toggle("active", key === name);
    root.scrollTop = 0;
  }

  // The request being confirmed and the view the back arrow returns to.
  let confirmRequest = null;
  let confirmReturn = "main";
  let confirmDone = false;

  function openConfirm(r) {
    confirmRequest = r;
    confirmDone = false;
    if (currentView !== "confirm") confirmReturn = currentView || "main";
    const body = ui.confirmBody;
    body.className = "confirm-body";
    body.onclick = null;
    const payee = el("div", "confirm-payee");
    payee.append(avatar({ id: r.requester, name: nameOf(r.requester) }), el("div", "pay-name", nameOf(r.requester)));
    body.replaceChildren(payee, el("div", "confirm-amount", czk(r.amount)));
    if (r.note) body.append(el("div", "confirm-note", r.note));
    // The request_received event carries group_id only; the loaded to_pay rows carry the group.
    const group = ((state.to_pay || []).find((x) => x.id === r.id) || r).group;
    if (group) body.append(el("div", "confirm-group", `Skupina: ${group.title}`));
    ui.confirmMsg.textContent = "";
    ui.confirmActions.hidden = false;
    ui.confirmCancel.disabled = false;
    ui.confirmOk.disabled = false;
    show("confirm");
  }

  async function payConfirmed() {
    const r = confirmRequest;
    if (!r || confirmDone) return;
    ui.confirmMsg.textContent = "";
    ui.confirmCancel.disabled = true;
    ui.confirmOk.disabled = true;
    try {
      await postJson(`/api/requests/${r.id}/pay`);
    } catch (e) {
      ui.confirmMsg.textContent = errText(e);
      ui.confirmCancel.disabled = false;
      ui.confirmOk.disabled = false;
      return;
    }
    confirmDone = true;
    ui.confirmActions.hidden = true;
    ui.confirmBody.append(el("div", "confirm-done", "Zaplaceno ✓"));
    const leave = () => {
      if (currentView !== "confirm" || confirmRequest !== r) return;
      confirmRequest = null;
      show("main");
      load();
    };
    ui.confirmBody.onclick = leave;
    setTimeout(leave, 1000);
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
    ui.payTitle.textContent = mode === "payment" ? "Poslat peníze" : "Vyžádat peníze";
    ui.sendBtn.textContent = mode === "payment" ? "Poslat" : "Vyžádat";
    setMsg(null, "");
  }

  // The three latest payments in the home-screen widget, worded like the history list.
  function renderWidgetRecent() {
    const d = new Date(); // local date, like the server's timestamps
    const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    const rows = state.history.slice(0, 3).map((p) => {
      const incoming = p.kind === "income" || (p.kind === "transfer" && p.recipient === state.me.id);
      const label = p.kind === "account" ? accountLabel(p.account)
        : p.kind === "card" ? (p.note || "Platba kartou")
        : p.kind === "income" ? (p.note || "Příchozí platba")
        : `${incoming ? "Od" : "Pro"} ${nameOf(incoming ? p.sender : p.recipient)}`;
      const when = p.created_at.slice(0, 10) === today ? p.created_at.slice(11, 16) : stamp(p.created_at).split(" ")[0];
      const row = el("div", "widget-tx");
      row.append(el("span", "widget-tx-name", label), el("span", "widget-tx-time", when),
        el("span", "widget-tx-amount" + (incoming ? " in" : ""), `${incoming ? "+" : "−"}${czk(p.amount)}`));
      return row;
    });
    ui.widgetRecent.replaceChildren(...rows);
  }

  // Known outside contacts (state.contacts, absent on old servers), by normalised account.
  const contactName = (account) => (state?.contacts || []).find((c) => c.account === account)?.name || "";
  const accountLabel = (account) => contactName(account) ? `Pro ${contactName(account)}` : `Na účet ${account}`;

  const accountOf = (id) => state.people.find((p) => p.id === id)?.account || "";

  // Not yet my friend (and the server does track friends): offer "+ Přítel" / "Přidat do přátel".
  const canbefriend = (id) => Boolean(state.friends) && id !== state.me.id && !state.friends.includes(id);
  const addFriendById = async (id) => {
    await postJson("/api/friends", { account: accountOf(id) });
    await load();
  };

  // Small "+ Přítel" button for a history row; an error replaces it for a moment.
  function befriendButton(id) {
    const btn = button("befriend-btn", "+ Přítel");
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      btn.disabled = true;
      try {
        await addFriendById(id);
      } catch (err) {
        const note = el("span", "befriend-err", errText(err, false));
        btn.replaceWith(note);
        setTimeout(() => { if (note.isConnected) note.replaceWith(btn); btn.disabled = false; }, 3000);
      }
    });
    return btn;
  }

  function refresh() {
    const { me, balance, history } = state;
    ui.balance.textContent = czk(balance);
    ui.widgetBalance.textContent = czk(balance);
    renderFriends();
    showChange(ui.change, state.today_change);
    showChange(ui.widgetChange, state.today_change);
    renderWidgetRecent();
    renderRecording();

    const rows = [];
    if (history.length === 0) rows.push(el("div", "empty", "Zatím žádné platby"));
    for (const p of history) {
      if (p.kind === "account") {
        const row = el("div", "tx");
        const info = el("div", "tx-info");
        const when = stamp(p.created_at);
        info.append(el("div", "tx-name", accountLabel(p.account)), el("div", "tx-meta", p.note ? `${p.note} · ${when}` : when));
        row.append(icon("card", "avatar card-avatar"), info, el("div", "tx-amount out", `−${czk(p.amount)}`));
        rows.push(row);
        continue;
      }
      if (p.kind === "card") {
        const row = el("div", "tx");
        const info = el("div", "tx-info");
        info.append(el("div", "tx-name", p.note ? `Karta · ${p.note}` : "Platba kartou"), el("div", "tx-meta", stamp(p.created_at)));
        row.append(icon("card", "avatar card-avatar"), info, el("div", "tx-amount out", `−${czk(p.amount)}`));
        rows.push(row);
        continue;
      }
      if (p.kind === "income") {
        const row = el("div", "tx");
        const info = el("div", "tx-info");
        info.append(el("div", "tx-name", p.note || "Příchozí platba"), el("div", "tx-meta", stamp(p.created_at)));
        row.append(icon("arrowin", "avatar card-avatar"), info, el("div", "tx-amount in", `+${czk(p.amount)}`));
        rows.push(row);
        continue;
      }
      const outgoing = p.sender === me.id;
      const other = outgoing ? p.recipient : p.sender;
      const row = el("div", "tx");
      const info = el("div", "tx-info");
      // Every transfer is with a Geoff user: say so, and offer to befriend them.
      const name = el("div", "tx-name", `${outgoing ? "Pro" : "Od"} ${nameOf(other)}`);
      name.append(el("span", "geoff-badge", "Geoff"));
      info.append(name);
      const when = stamp(p.created_at);
      // One short line: the note if there is one, else where the money came from.
      const meta = p.note ? `${p.note} · ${when}` : outgoing ? when : `z účtu ${accountOf(p.sender)} · ${when}`;
      info.append(el("div", "tx-meta", meta));
      row.append(avatar({ id: other, name: nameOf(other) }), info,
        el("div", "tx-amount " + (outgoing ? "out" : "in"), `${outgoing ? "−" : "+"}${czk(p.amount)}`));
      if (canbefriend(other)) row.append(befriendButton(other));
      rows.push(row);
    }
    ui.historyList.replaceChildren(...rows);
    renderToPay();
    renderGroups();
    renderGroup();
  }

  // Czech plural: 1 platba, 2-4 platby, 5+ plateb
  const payments = (n) => `${n} ${n === 1 ? "platba" : n >= 2 && n <= 4 ? "platby" : "plateb"}`;

  function renderRecording() {
    const rec = state.recording;
    const mine = state.me.id;
    // Someone else leads this session. Only when the server says so: without `starter` the Stop
    // button must stay, or nobody could end the recording.
    const participant = !!rec && rec.starter != null && rec.starter !== mine;
    for (const b of ui.recToggles) {
      b.hidden = participant;
      b.textContent = rec ? "Ukončit skupinovou platbu" : "Spustit skupinovou platbu";
      b.classList.toggle("recording", !!rec);
    }
    const pending = rec ? [] : state.session_invites || [];
    const answer = async (starter, action, e) => {
      e.stopPropagation(); // the widget tap would otherwise open Geoff
      try {
        await postJson(`/api/recording/invites/${starter}/${action}`);
      } catch (err) {
        Phone.notify({ title: "Geoff", body: errText(err, false), color: "#d93636" });
      }
      await load();
    };
    for (const i of ui.recInfos) {
      i.hidden = !rec && !pending.length;
      if (!rec) {
        i.replaceChildren(...pending.map((inv) => {
          const row = el("div", "rec-invite");
          const decline = button("rec-invite-btn secondary", "Odmítnout");
          decline.addEventListener("click", (e) => answer(inv.starter, "decline", e));
          const accept = button("rec-invite-btn", "Přijmout");
          accept.addEventListener("click", (e) => answer(inv.starter, "accept", e));
          const btns = el("div", "rec-invite-btns");
          btns.append(decline, accept);
          row.append(el("div", "rec-line", `${firstName(inv.starter)} tě zve do skupinové platby`), btns);
          return row;
        }));
        continue;
      }
      const lines = [];
      if (participant) lines.push(el("div", "rec-line rec-leader", `Skupinovou platbu vede ${firstName(rec.starter)}`));
      const count = el("div", "rec-line");
      count.append(el("span", "rec-dot"), el("span", null, `Zaznamenáno: ${payments(rec.payments.length)} · ${czk(rec.total)}`));
      lines.push(count);
      if (participant) {
        const others = (rec.participants || []).filter((id) => id !== mine && id !== rec.starter);
        if (others.length) lines.push(el("div", "rec-line rec-with", `Také: ${others.map(firstName).join(", ")}`));
      } else {
        const others = (rec.participants || []).filter((id) => id !== mine);
        if (others.length) {
          const joined = el("div", "rec-line");
          joined.append(avatars(others));
          lines.push(joined);
        }
        if (rec.invited?.length) lines.push(el("div", "rec-line rec-with", `čeká: ${rec.invited.map(firstName).join(", ")}`));
      }
      i.replaceChildren(...lines);
    }
  }

  // Guards a double tap: the second Stop would toast "no recording" over the popup.
  let toggling = false;
  async function toggleRecording() {
    if (toggling) return;
    toggling = true;
    try {
      if (!state.recording) {
        showStartPopup();
      } else {
        const result = await postJson("/api/recording/stop");
        await load();
        if (result.shared) showSharedStopPopup(result);
        else showStopPopup(result);
      }
    } catch (err) {
      Phone.notify({ title: "Geoff", body: errText(err, false), color: "#d93636" });
      load();
    } finally {
      toggling = false;
    }
  }

  // The Friends list: only people I've befriended (everyone if the server doesn't say).
  function renderFriends() {
    const { me, people, friends } = state;
    const shown = people.filter((p) => p.id !== me.id && (!friends || friends.includes(p.id)));
    if (shown.length === 0) {
      ui.friendList.replaceChildren(el("div", "empty", "Zatím žádní přátelé – přidej je podle čísla účtu."));
      return;
    }
    ui.friendList.replaceChildren(...shown.map((p) => {
      const who = el("span", "contact-who");
      who.append(el("span", "contact-name", p.name), el("span", "contact-account", p.account || ""));
      const row = button("contact", avatar(p), who, icon("chevron", "chev"));
      row.addEventListener("click", () => openPay(p.id));
      return row;
    }));
  }

  // "Přidat přítele": connect by account number; the friend gets a notification.
  function showAddFriendPopup() {
    const input = el("input", "field");
    Object.assign(input, { type: "text", maxLength: 30, autocomplete: "off", placeholder: "2222222222/0800" });
    const msg = el("div", "form-msg error");
    const go = el("button", "send-btn", "Přidat");
    go.type = "button";
    const cancel = el("button", "popup-secondary", "Zrušit");
    cancel.type = "button";
    const close = Phone.popup([
      el("h3", "popup-title", "Přidat přítele"),
      el("div", "popup-sub", "Zadej číslo účtu v Geoff, třeba 2222222222/0800."),
      input, go, msg, cancel,
    ]);
    cancel.addEventListener("click", () => close());
    const submit = async () => {
      if (go.disabled) return;
      go.disabled = true;
      msg.textContent = "";
      try {
        await postJson("/api/friends", { account: input.value });
        close();
        await load();
      } catch (err) {
        msg.textContent = errText(err);
        go.disabled = false;
      }
    };
    go.addEventListener("click", submit);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") submit(); });
    input.focus();
  }

  // Before Start: pick which friends to invite into the shared session (none = solo).
  function showStartPopup() {
    const nodes = [el("h3", "popup-title", "Spustit skupinovou platbu")];
    nodes.push(el("div", "popup-sub", "Koho pozvat? Pozvaní se připojí, až pozvánku přijmou."));
    const picks = {};
    const list = el("div", "pick-list");
    for (const p of state.people.filter((x) => x.id !== state.me.id)) {
      const box = el("input");
      box.type = "checkbox";
      picks[p.id] = box;
      const row = el("label", "pick");
      row.append(box, avatar(p), el("span", "contact-name", p.name));
      list.append(row);
    }
    const msg = el("div", "form-msg error");
    const go = el("button", "send-btn", "Spustit");
    go.type = "button";
    const cancel = el("button", "popup-secondary", "Zrušit");
    cancel.type = "button";
    nodes.push(list, go, msg, cancel);
    const close = Phone.popup(nodes);
    cancel.addEventListener("click", () => close());
    go.addEventListener("click", async () => {
      const invite = Object.entries(picks).filter(([, b]) => b.checked).map(([id]) => Number(id));
      go.disabled = true;
      try {
        await postJson("/api/recording/start", { invite });
        close();
        await load();
      } catch (err) {
        msg.textContent = errText(err);
        go.disabled = false;
      }
    });
  }

  // After Stop of a shared session: payments of everyone, then a group is created from them
  // or nothing happens. Any way out except "Vytvořit" discards the ended session so that
  // nobody stays blocked.
  function showSharedStopPopup(result) {
    const nodes = [el("h3", "popup-title", "Skupinová platba ukončena")];
    const discard = async () => {
      try { await postJson("/api/recording/discard"); } catch { /* already gone */ }
      load();
    };
    let close;
    const name = el("input", "field");
    Object.assign(name, { type: "text", maxLength: 40, value: "Skupinová platba " + new Date().toLocaleDateString("cs-CZ") });
    if (result.payments.length === 0) {
      nodes.push(el("p", "popup-empty", "Během záznamu nebyla žádná platba kartou."));
    } else {
      const list = el("div", "popup-list");
      for (const p of result.payments) {
        const info = el("div", "tx-info");
        info.append(el("div", "tx-name", p.note || "Platba kartou"),
          el("div", "tx-meta", `${firstName(p.person)} · ${stamp(p.created_at)}`));
        const row = el("div", "tx");
        row.append(avatar({ id: p.person, name: nameOf(p.person) }), info, el("div", "tx-amount out", `−${czk(p.amount)}`));
        list.append(row);
      }
      list.append(el("div", "popup-total", `Celkem: ${czk(result.total)}`));
      nodes.push(list);
    }
    const msg = el("div", "form-msg error");
    const create = el("button", "send-btn", "Vytvořit skupinové vyrovnání");
    create.type = "button";
    create.addEventListener("click", async () => {
      create.disabled = true;
      try {
        const g = await postJson("/api/recording/group", { name: name.value });
        close();
        await load();
        Phone.openApp("app");
        openGroup(g.id);
      } catch (err) {
        msg.textContent = errText(err);
        create.disabled = false;
      }
    });
    const nothing = el("button", "popup-secondary", "Nic nedělat");
    nothing.type = "button";
    nothing.addEventListener("click", () => { close(); discard(); });
    nodes.push(name, create, msg, nothing);
    close = Phone.popup(nodes, discard);
  }

  // After Stop: offer a new Group Settle, an existing open group, or nothing.
  function showStopPopup(result) {
    const nodes = [el("h3", "popup-title", "Skupinová platba ukončena")];
    let close;
    if (result.payments.length === 0) {
      nodes.push(el("p", "popup-empty", "Během záznamu nebyla žádná platba kartou."));
    } else {
      const list = el("div", "popup-list");
      for (const p of result.payments) {
        const info = el("div", "tx-info");
        info.append(el("div", "tx-name", p.note || "Platba kartou"), el("div", "tx-meta", stamp(p.created_at)));
        const row = el("div", "tx");
        row.append(info, el("div", "tx-amount out", `−${czk(p.amount)}`));
        list.append(row);
      }
      list.append(el("div", "popup-total", `Celkem: ${czk(result.total)}`));
      nodes.push(list);
      const sources = result.payments.map((p) => ({ kind: "card", id: p.id }));
      const create = el("button", "send-btn", "Vytvořit skupinové vyrovnání");
      create.type = "button";
      create.addEventListener("click", () => {
        close();
        Phone.openApp("app");
        openNewGroup({ sources, payments: result.payments });
      });
      nodes.push(create);
      const open = (state.groups || []).filter((g) => g.status === "open");
      if (open.length) {
        const err = el("div", "form-msg error");
        nodes.push(el("div", "popup-sub", "Nebo přidat do skupiny:"));
        for (const g of open) {
          const b = el("button", "popup-group", g.name);
          b.type = "button";
          b.addEventListener("click", async () => {
            b.disabled = true;
            try {
              await postJson(`/api/groups/${g.id}/expenses`, { sources });
              close();
              await load();
              Phone.openApp("app");
              openGroup(g.id);
            } catch (e) {
              err.textContent = errText(e);
              b.disabled = false;
            }
          });
          nodes.push(b);
        }
        nodes.push(err);
      }
    }
    const nothing = el("button", "popup-secondary", "Nic nedělat");
    nothing.type = "button";
    nothing.addEventListener("click", () => close());
    nodes.push(nothing);
    close = Phone.popup(nodes);
  }

  function renderToPay() {
    const { me } = state;
    const toPay = state.to_pay || []; // older servers don't send it
    ui.toPayBadge.textContent = toPay.length ? String(toPay.length) : "";
    ui.toPayBadge.hidden = toPay.length === 0;

    const individual = toPay.filter((r) => !r.group);
    const group = toPay.filter((r) => r.group);
    const blocks = [];
    if (toPay.length === 0) blocks.push(el("div", "empty topay-empty", "Není co platit 🎉"));
    if (individual.length) {
      blocks.push(el("h3", "topay-section", "Jednotlivé"));
      const box = el("div", "card-list");
      for (const r of individual) box.append(requestRow(r));
      blocks.push(box);
    }
    if (group.length) {
      blocks.push(el("h3", "topay-section", "Skupinové"));
      for (const r of group) {
        const box = el("div", "card-list group-card");
        const g = r.group;
        // A settled group can owe several people; this card is only about what's owed to r.requester.
        const sameBill = g.members.filter((m) => m.requester === r.requester);
        const total = sameBill.reduce((sum, m) => sum + m.amount, 0);
        const head = el("div", "group-head");
        head.append(el("div", "group-title", g.title),
          el("div", "group-meta", `Pro ${nameOf(r.requester)} · celkem ${czk(total)}`));
        const members = el("div", "group-members");
        for (const m of sameBill) {
          const chip = el("span", `member ${m.status}`);
          chip.append(avatar({ id: m.payer, name: nameOf(m.payer) }),
            el("span", null, m.payer === me.id ? "Ty" : nameOf(m.payer).split(" ")[0]),
            el("small", null, m.status === "paid" ? "✓ zaplaceno" : m.status === "declined" ? "odmítnuto" : czk(m.amount)));
          members.append(chip);
        }
        box.append(head, members, requestRow(r, `Tvůj podíl pro ${nameOf(r.requester).split(" ")[0]}`));
        blocks.push(box);
      }
    }
    ui.toPayList.replaceChildren(...blocks);
    renderRequested();
  }

  const STATUS = { open: "Čeká se", paid: "Zaplaceno", declined: "Odmítnuto", cancelled: "Zrušeno" };

  // ---- Group Settle ----

  const firstName = (id) => nameOf(id).split(" ")[0];
  const time = (iso) => iso.slice(11, 16);

  function avatars(ids, pendingIds = []) {
    const row = el("div", "avatar-row");
    for (const id of ids) row.append(avatar({ id, name: nameOf(id) }));
    for (const id of pendingIds) {
      const a = avatar({ id, name: nameOf(id) });
      a.classList.add("pending"); // invited, not yet joined
      row.append(a);
    }
    return row;
  }

  function groupStatus(g) {
    return el("span", `status ${g.status === "open" ? "open" : "paid"}`, g.status === "open" ? "Otevřená" : "Schválená");
  }

  function renderGroups() {
    const list = state.groups || [];
    const cards = [];
    const invites = state.group_invites || [];
    if (invites.length) {
      cards.push(el("h3", "topay-section", "Pozvánky"));
      for (const g of invites) {
        const card = el("div", "group-tile invite-card");
        const top = el("div", "req-top");
        const info = el("div", "tx-info");
        info.append(el("div", "group-title", g.name), el("div", "group-meta", `Zve tě ${firstName(g.creator)}`));
        top.append(info);
        const err = el("div", "form-msg error");
        const answer = (action) => async (e) => {
          const btns = card.querySelectorAll("button");
          btns.forEach((b) => { b.disabled = true; });
          try {
            await postJson(`/api/groups/${g.id}/${action}`);
            await load();
          } catch (ex) {
            err.textContent = errText(ex);
            btns.forEach((b) => { b.disabled = false; });
          }
        };
        const decline = el("button", "popup-secondary invite-btn", "Odmítnout");
        decline.type = "button";
        decline.addEventListener("click", answer("decline"));
        const accept = el("button", "send-btn invite-btn", "Přijmout");
        accept.type = "button";
        accept.addEventListener("click", answer("accept"));
        const row = el("div", "invite-actions");
        row.append(decline, accept);
        card.append(top, avatars(g.members), row, err);
        cards.push(card);
      }
      cards.push(el("h3", "topay-section", "Moje skupiny"));
    }
    if (list.length === 0) cards.push(el("div", "empty topay-empty", "Zatím žádné skupiny"));
    for (const g of list) {
      const card = button("group-tile");
      const top = el("div", "req-top");
      const info = el("div", "tx-info");
      info.append(el("div", "group-title", g.name),
        el("div", "group-meta", g.creator === state.me.id ? "Založeno mnou" : `Přidal(a) ${firstName(g.creator)}`));
      const right = el("div", "req-right");
      right.append(el("div", "tx-amount", czk(g.total)), groupStatus(g));
      top.append(info, right);
      card.append(top, avatars(g.members, g.invited || []));
      card.addEventListener("click", () => openGroup(g.id));
      cards.push(card);
    }
    ui.groupsList.replaceChildren(...cards);
  }

  // prefill is {amount, note} from one card payment, or {sources, payments} from a stopped
  // recording. Either way the group starts with those expenses, paid by me.
  function openNewGroup(prefill) {
    startExpense = prefill || null;
    let name = "";
    let info = "";
    if (prefill && prefill.sources) {
      const total = prefill.payments.reduce((s, p) => s + p.amount, 0);
      name = "Skupinová platba " + new Date().toLocaleDateString("cs-CZ");
      info = `Výdaje: ${payments(prefill.payments.length)} · ${czk(total)}, zaplaceno tebou`;
    } else if (prefill) {
      name = prefill.note.slice(0, 40);
      info = `Výdaj: ${czk(prefill.amount)} · zaplaceno tebou`;
    }
    ui.ngName.value = name;
    ui.ngExpense.hidden = !prefill;
    ui.ngExpense.textContent = info;
    for (const box of Object.values(ui.ngPicks)) box.checked = false;
    ui.ngMsg.className = "form-msg";
    ui.ngMsg.textContent = "";
    show("newgroup");
    ui.ngName.focus();
  }

  const CHIPS = [
    ["Dnes", "Shrň mi dnešní platby."],
    ["Tento měsíc", "Shrň mi platby za tento měsíc."],
    ["Kolik dlužím?", "Komu a kolik dlužím?"],
    ["Kdo dluží mně?", "Kdo a kolik dluží mně?"],
    ["Moje skupiny", "Jak jsou na tom moje skupiny?"],
    ["Moje účty", "Jak jsou na tom moje další účty?"],
    ["Graf výdajů", "Ukaž mi graf výdajů po měsících."],
  ];
  const chatHistory = []; // {role, content}; lives only until reload; errors never enter it

  // ---- Charts in the chat: inline SVG, no library; all text goes in through textContent ----
  const SVG_NS = "http://www.w3.org/2000/svg";
  const CHART_COLORS = ["#3b6fe0", "#e0773b", "#2fa37a", "#b04fc4", "#d6a31f", "#d6486a", "#4aa8c7", "#7a7f8c"];
  const svg = (tag, attrs = {}, text) => {
    const n = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (text !== undefined) n.textContent = text;
    return n;
  };
  const num = (n) => Number(n).toLocaleString("cs-CZ", { maximumFractionDigits: 2 });
  const withUnit = (n, unit) => `${num(n)} ${unit}`;

  // Round gridline values: ~3 steps of 1/2/5 x 10^k covering [lo, hi]
  function niceTicks(lo, hi) {
    if (hi <= lo) hi = lo + 1;
    const raw = (hi - lo) / 3;
    const mag = 10 ** Math.floor(Math.log10(raw));
    const step = [1, 2, 5, 10].map((m) => m * mag).find((s) => s >= raw);
    const ticks = [];
    for (let t = Math.floor(lo / step) * step; t < hi + step - 1e-9; t += step) ticks.push(+t.toFixed(10));
    return ticks;
  }

  function lineChart(c) {
    const W = 300, H = 170, L = 46, R = 10, T = 8, B = 22;
    const unit = c.unit || "Kč";
    const all = c.series.flatMap((s) => s.values);
    const ticks = niceTicks(Math.min(0, ...all), Math.max(0, ...all));
    const lo = ticks[0], hi = ticks[ticks.length - 1];
    const x = (i) => L + (c.labels.length === 1 ? (W - L - R) / 2 : (i * (W - L - R)) / (c.labels.length - 1));
    const y = (v) => T + ((hi - v) / (hi - lo)) * (H - T - B);
    const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, class: "chart-svg", role: "img" });
    root.append(svg("title", {}, c.title));
    for (const t of ticks) {
      root.append(svg("line", { x1: L, x2: W - R, y1: y(t), y2: y(t), class: "chart-grid" }));
      root.append(svg("text", { x: L - 4, y: y(t) + 3, "text-anchor": "end", "font-size": 9 }, num(t)));
    }
    const every = Math.ceil(c.labels.length / 6); // thin the x labels out
    c.labels.forEach((l, i) => {
      // the last label is right-aligned so it is not cut off at the edge
      if (i % every === 0) root.append(svg("text", { x: x(i), y: H - 6, "text-anchor": i === c.labels.length - 1 ? "end" : "middle", "font-size": 9 }, l));
    });
    c.series.forEach((s, k) => {
      const color = CHART_COLORS[k % CHART_COLORS.length];
      root.append(svg("polyline", {
        points: s.values.map((v, i) => `${x(i)},${y(v)}`).join(" "),
        fill: "none", stroke: color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round",
      }));
      s.values.forEach((v, i) => {
        const d = svg("circle", { cx: x(i), cy: y(v), r: 3, fill: color });
        d.append(svg("title", {}, `${s.name}, ${c.labels[i]}: ${withUnit(v, unit)}`));
        root.append(d);
      });
    });
    const parts = [root];
    if (c.series.length > 1) {
      const legend = el("div", "chart-legend");
      c.series.forEach((s, k) => {
        const item = el("span", "chart-legend-item");
        const sw = el("span", "chart-swatch");
        sw.style.background = CHART_COLORS[k % CHART_COLORS.length];
        item.append(sw, el("span", "name", s.name));
        legend.append(item);
      });
      parts.push(legend);
    }
    return parts;
  }

  function pieChart(c) {
    const unit = c.unit || "Kč";
    const total = c.values.reduce((a, b) => a + b, 0);
    const R = 70, SW = 28, C = 2 * Math.PI * R;
    const root = svg("svg", { viewBox: "0 0 200 200", class: "chart-svg", role: "img" });
    root.style.maxWidth = "13em";
    root.style.margin = "0 auto";
    root.append(svg("title", {}, c.title));
    let used = 0;
    c.values.forEach((v, i) => {
      if (!(v > 0)) return;
      const len = (v / total) * C;
      // a stroked circle cut into dashes: a single 100% slice is a full ring, no arc edge cases
      const slice = svg("circle", {
        cx: 100, cy: 100, r: R, fill: "none", stroke: CHART_COLORS[i % CHART_COLORS.length], "stroke-width": SW,
        "stroke-dasharray": `${len} ${C - len}`, "stroke-dashoffset": -used, transform: "rotate(-90 100 100)",
      });
      slice.append(svg("title", {}, `${c.labels[i]}: ${withUnit(v, unit)}`));
      root.append(slice);
      used += len;
    });
    root.append(svg("text", { x: 100, y: 104, "text-anchor": "middle", class: "chart-center" }, withUnit(total, unit)));
    const legend = el("div", "chart-legend pie");
    c.values.forEach((v, i) => {
      const item = el("span", "chart-legend-item");
      const sw = el("span", "chart-swatch");
      sw.style.background = CHART_COLORS[i % CHART_COLORS.length];
      item.append(sw, el("span", "name", c.labels[i]),
        el("span", "val", `${withUnit(v, unit)} · ${Math.round((v / total) * 100)} %`));
      legend.append(item);
    });
    return [root, legend];
  }

  function chartBox(c) {
    const box = el("div", "chat-chart");
    try {
      box.append(el("div", "chart-title", c.title), ...(c.type === "pie" ? pieChart(c) : lineChart(c)));
    } catch { return null; } // a malformed spec must not break the answer text
    return box;
  }

  // Built once in build(); refresh() never touches it, so the conversation survives.
  function buildChat() {
    const chat = el("section", "chat");
    chat.style.setProperty("--accent", Phone.colors[state.me.id]);
    const list = el("div", "chat-list");
    const empty = el("div", "chat-empty", "Zeptej se mě na cokoliv o financích");
    list.append(empty);
    const chips = el("div", "chat-chips");
    const form = el("form", "chat-form");
    const input = el("input", "chat-input");
    input.type = "text";
    input.maxLength = 1000;
    input.placeholder = "Napiš zprávu…";
    const send = button("chat-send", "Poslat");
    send.type = "submit";
    form.append(input, send);
    const controls = [send];

    const bubble = (cls, text) => {
      empty.hidden = true;
      const b = el("div", `chat-msg ${cls}`);
      b.textContent = text;
      list.append(b);
      list.scrollTop = list.scrollHeight;
      return b;
    };
    let busy = false;
    const setBusy = (v) => {
      busy = v;
      for (const c of controls) c.disabled = v;
    };

    async function ask(text) {
      text = text.trim();
      if (!text || busy) return;
      setBusy(true);
      input.value = "";
      chatHistory.push({ role: "user", content: text });
      bubble("chat-user", text);
      const wait = bubble("chat-bot", "…");
      try {
        const r = await fetch("/api/chat", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ messages: chatHistory.slice(-20) }),
        });
        let data = {};
        try { data = await r.json(); } catch { /* non-JSON error page */ }
        if (r.ok && typeof data.reply === "string") {
          // Show the full reply, but keep history within the server's limits (1000 chars, non-empty),
          // otherwise one long answer would make every later request fail with 400.
          const reply = data.reply.trim();
          if (reply) chatHistory.push({ role: "assistant", content: reply.slice(0, 1000) });
          wait.textContent = reply || "Geoff nemá co dodat.";
          // charts hang under the text bubble; they stay in the DOM only, never in chatHistory
          let last = wait;
          for (const spec of Array.isArray(data.charts) ? data.charts : []) {
            const box = chartBox(spec);
            if (box) { last.after(box); last = box; }
          }
        } else {
          chatHistory.pop(); // keep the history ending on a user message that got no answer out
          wait.textContent = typeof data.detail === "string" && data.detail ? data.detail : `Selhalo (${r.status})`;
          wait.classList.add("chat-error");
        }
      } catch {
        chatHistory.pop();
        wait.textContent = "Geoff je nedostupný.";
        wait.classList.add("chat-error");
      }
      list.scrollTop = list.scrollHeight;
      setBusy(false);
    }

    for (const [label, message] of CHIPS) {
      const chip = button("chat-chip", label);
      chip.addEventListener("click", () => ask(message));
      chips.append(chip);
      controls.push(chip);
    }
    form.addEventListener("submit", (e) => { e.preventDefault(); ask(input.value); });
    chat.append(list, chips, form);
    return chat;
  }

  async function postJson(url, body, method = "POST") {
    const r = await fetch(url, {
      method,
      headers: { "content-type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    let data = {};
    try { data = await r.json(); } catch { /* non-JSON error page */ }
    if (!r.ok) throw new Error(data.detail || `Selhalo (${r.status})`);
    return data;
  }

  async function createGroup() {
    const members = Object.entries(ui.ngPicks).filter(([, b]) => b.checked).map(([id]) => Number(id));
    ui.ngBtn.disabled = true;
    try {
      const body = { name: ui.ngName.value, members };
      if (startExpense && startExpense.sources) body.sources = startExpense.sources;
      else if (startExpense) body.expense = { amount: startExpense.amount, description: startExpense.note || "Platba kartou" };
      const g = await postJson("/api/groups", body);
      await load();
      openGroup(g.id);
    } catch (err) {
      ui.ngMsg.className = "form-msg error";
      ui.ngMsg.textContent = errText(err);
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
    meta.append(el("div", "group-meta", g.creator === mine ? "Založeno mnou" : `Založil(a) ${nameOf(g.creator)}`),
      el("div", "group-total", czk(g.total)), el("div", "group-meta", "utraceno společně"));
    top.append(meta, groupStatus(g));
    const people = el("div", "group-members");
    for (const id of g.members) {
      const chip = el("span", "member");
      chip.append(avatar({ id, name: nameOf(id) }), el("span", null, id === mine ? "Ty" : firstName(id)));
      people.append(chip);
    }
    for (const id of g.invited || []) {
      const chip = el("span", "member pending");
      chip.append(avatar({ id, name: nameOf(id) }), el("span", null, id === mine ? "Ty" : firstName(id)),
        el("small", null, "čeká na přijetí"));
      people.append(chip);
    }
    info.append(top, people);
    ui.groupInfo.replaceChildren(info);

    ui.expenseForm.hidden = !isOpen;

    const rows = [];
    rows.push(el("h3", "topay-section", "Výdaje"));
    const box = el("div", "card-list");
    if (g.expenses.length === 0) box.append(el("div", "empty", "Zatím žádné výdaje"));
    for (const e of g.expenses) {
      const row = el("div", "tx");
      const text = el("div", "tx-info");
      text.append(el("div", "tx-name", e.description),
        el("div", "tx-meta", `${e.payer === mine ? "Zaplaceno tebou" : `Zaplaceno: ${nameOf(e.payer)}`} · ${time(e.created_at)}`));
      row.append(avatar({ id: e.payer, name: nameOf(e.payer) }), text, el("div", "tx-amount", czk(e.amount)));
      if (isOpen && e.payer === mine) {
        const del = button("del-btn", "✕");
        del.title = "Smazat";
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
      const btn = button("send-btn approve-btn", "Schválit a vyrovnat");
      const msg = el("div", "form-msg");
      btn.addEventListener("click", () => approveGroup(g.id, btn, msg));
      approve.push(el("div", "approve-hint", "Až všichni přidají, co zaplatili, schval skupinu. Zamkne se a odešlou se žádosti o platbu."), btn, msg);
    } else if (isOpen) {
      approve.push(el("div", "approve-hint", `Čeká se, až skupinu schválí ${firstName(g.creator)}.`));
    } else {
      approve.push(el("div", "approve-hint", g.requests_sent > 0
        ? "Schváleno: žádosti o platbu byly odeslány. Najdeš je v K zaplacení."
        : "Schváleno: všichni jsou už vyrovnaní, žádosti nejsou potřeba."));
    }
    if (g.creator === mine) {
      const del = button("delete-group-btn", "Smazat skupinu");
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
        ? (h.note ? `Karta · ${h.note}` : "Platba kartou")
        : (h.note || `Platba pro ${nameOf(h.recipient)}`);
      info.append(el("div", "tx-name", label), el("div", "tx-meta", stamp(h.created_at)));
      const add = button("add-btn", "Přidat");
      const msg = el("div", "form-msg error");
      add.addEventListener("click", () => addFromHistory(h, add, msg));
      row.append(icon(h.kind === "card" ? "card" : "contacts", "req-icon"), info,
        el("div", "tx-amount", czk(h.amount)), add);
      box.append(row, msg);
    }
    return [el("h3", "topay-section", "Nebo vyber z mých plateb"), box];
  }

  async function addFromHistory(h, btn, msg) {
    btn.disabled = true;
    msg.textContent = "";
    try {
      await postJson(`/api/groups/${openGroupId}/expenses`, { source: { kind: h.kind, id: h.id } });
      await load();
    } catch (err) {
      msg.textContent = errText(err);
      btn.disabled = false;
    }
  }

  async function deleteGroup(g, btn, msg) {
    const sent = g.requests_sent > 0 ? " Nezaplacené žádosti o platbu se zruší." : "";
    if (!window.confirm(`Smazat skupinu „${g.name}“ pro všechny?${sent}`)) return;
    btn.disabled = true;
    try {
      await postJson(`/api/groups/${g.id}`, undefined, "DELETE");
      openGroupId = null;
      show("groups");
      await load();
    } catch (err) {
      msg.className = "form-msg error";
      msg.textContent = errText(err);
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
      ui.exMsg.textContent = errText(err);
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
      msg.textContent = errText(err);
      btn.disabled = false;
    }
  }

  // Requests I made. Group requests come back as one row per member; show one card per group.
  function renderRequested() {
    const mine = state.requested || [];
    const blocks = [];
    if (mine.length === 0) blocks.push(el("div", "empty topay-empty", "Zatím žádné tvoje žádosti"));
    const individual = mine.filter((r) => !r.group);
    if (individual.length) {
      blocks.push(el("h3", "topay-section", "Jednotlivé"));
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
      blocks.push(el("h3", "topay-section", "Skupinové"));
      for (const g of groups.values()) {
        // Only the rows owed to me; a settled group can also hold debts between other members.
        const owedToMe = g.members.filter((m) => m.requester === state.me.id);
        const total = owedToMe.reduce((sum, m) => sum + m.amount, 0);
        const box = el("div", "card-list group-card");
        const head = el("div", "group-head");
        const paid = owedToMe.filter((m) => m.status === "paid").reduce((sum, m) => sum + m.amount, 0);
        head.append(el("div", "group-title", g.title), el("div", "group-meta", `Zaplaceno ${czk(paid)} z ${czk(total)}`));
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
    const decline = button("req-btn decline", "Odmítnout");
    const payBtn = button("req-btn pay", "Zaplatit");
    const msg = el("div", "form-msg error");
    decline.addEventListener("click", () => answer(r.id, "decline", msg, [decline, payBtn]));
    payBtn.addEventListener("click", () => openConfirm(r));
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
        msg.textContent = body.detail || `Selhalo (${r.status})`;
        buttons.forEach((b) => { b.disabled = false; });
        return;
      }
      await load();
    } catch {
      msg.textContent = "Banku se nepodařilo zastihnout. Zkus to znovu.";
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
        setMsg("error", body.detail || `Platba selhala (${r.status})`);
        return;
      }
      ui.amount.value = "";
      ui.note.value = "";
      setMsg("ok", requesting
        ? `Vyžádáno ${czk(body.amount)} od ${nameOf(body.payer)}`
        : `Posláno ${czk(body.amount)} pro ${nameOf(body.recipient)}`);
      await load();
    } catch {
      setMsg("error", "Banku se nepodařilo zastihnout. Zkus to znovu.");
    } finally {
      ui.sendBtn.disabled = false;
    }
  }

  Phone.onEvent((event) => {
    if (event.type === "payment_received") {
      const note = event.payment.note ? `\n${event.payment.note}` : "";
      const sender = event.payment.sender;
      Phone.notify({
        title: event.from, body: event.text + note, color: Phone.colors[sender],
        // A Geoff user I haven't befriended yet can be added right here.
        actions: canbefriend(sender)
          ? [{ label: "Přidat do přátel", onClick: async () => { await addFriendById(sender); return "Přidáno ✓"; } }]
          : undefined,
      });
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
          { label: "Odmítnout", secondary: true, onClick: answer("decline", "Odmítnuto") },
          // Paying needs a deliberate confirmation, so this opens it in Geoff.
          { label: "Zaplatit", onClick: async () => { Phone.closeShade(); Phone.openApp("app"); openConfirm(event.request); return "Otevřeno"; } },
        ] : undefined,
      });
      load();
    } else if (event.type === "geoff_suggestion") {
      const sg = event.suggestion;
      // Czech cases for the four demo people (fall back to the plain name for anyone else).
      const GENITIVE = { "Štěpán Pressl": "Štěpána Pressla", "Jirka Měřínský": "Jirky Měřínského", "Pepa Hřebec": "Pepy Hřebce", "Petr Šafář": "Petra Šafáře" };
      const WITH = { Štěpán: "Štěpánem", Jirka: "Jirkou", Pepa: "Pepou", Petr: "Petrem" };
      let body, confirm, done;
      if (sg.kind === "request") {
        body = `Vyžádat ${czk(sg.amount)} od ${GENITIVE[nameOf(sg.payer)] || nameOf(sg.payer)}${sg.note ? ` (${sg.note})` : ""}?`;
        confirm = () => postJson("/api/requests", { payer: sg.payer, amount: sg.amount, note: sg.note || "" });
        done = "Vyžádáno ✓";
      } else {
        const names = sg.members.map((id) => { const f = nameOf(id).split(" ")[0]; return WITH[f] || f; });
        const who = names.length > 1 ? `${names.slice(0, -1).join(", ")} a ${names[names.length - 1]}` : names[0];
        body = `Založit skupinové vyrovnání „${sg.name}“ s ${who}${sg.amount ? ` · ${czk(sg.amount)}` : ""}?`;
        confirm = () => postJson("/api/groups", {
          name: sg.name, members: sg.members,
          ...(sg.amount ? { expense: { amount: sg.amount, description: sg.note || sg.name } } : {}),
        });
        done = "Skupina založena · pozvánky odeslány ✓";
      }
      Phone.notify({
        title: "Geoff", body, color: "#3b6cff",
        actions: [
          { label: "Zamítnout", secondary: true, onClick: async () => "Zamítnuto" },
          { label: "Potvrdit", onClick: async () => { await confirm(); await load(); return done; } },
        ],
      });
    } else if (event.type === "card_payment") {
      const prefill = { amount: event.payment.amount, note: event.payment.note };
      Phone.notify({
        title: "Geoff", body: event.text, color: "#3b6cff",
        // While recording, the payments are collected and offered together on Stop.
        action: event.recording ? undefined : { label: "Skupinové vyrovnání", onClick: () => openNewGroup(prefill) },
      });
      load();
    } else if (event.type === "group_deleted") {
      Phone.notify({ title: event.from, body: event.text, color: "#8e8e93" });
      load();
    } else if (event.type === "session_invite") {
      const answer = (action, done) => async () => {
        await postJson(`/api/recording/invites/${event.starter}/${action}`);
        await load();
        return done;
      };
      Phone.notify({
        title: event.from, body: event.text, color: Phone.colors[event.starter],
        actions: [
          { label: "Odmítnout", secondary: true, onClick: answer("decline", "Odmítnuto") },
          { label: "Přijmout", onClick: answer("accept", "Přidáno ✓") },
        ],
      });
      load();
    } else if (event.type === "session_ended") {
      Phone.notify({ title: event.from, body: event.text, color: "#8e8e93" });
      load();
    } else if (event.type === "group_invite") {
      const answer = (action, done) => async () => {
        await postJson(`/api/groups/${event.group.id}/${action}`);
        await load();
        return done;
      };
      Phone.notify({
        title: event.from, body: event.text, color: Phone.colors[event.group.creator],
        actions: [
          { label: "Odmítnout", secondary: true, onClick: answer("decline", "Odmítnuto") },
          { label: "Přijmout", onClick: answer("accept", "Přidáno ✓") },
        ],
      });
      load();
    } else if (event.type === "group_added") {
      Phone.notify({ title: event.from, body: event.text, color: Phone.colors[event.group.creator] });
      load();
    } else if (event.type === "friend_added") {
      Phone.notify({ title: event.from, body: event.text, color: Phone.colors[event.from_id ?? state.people.find((p) => p.name === event.from)?.id] });
      load();
    } else if (["friends_changed", "payment_sent", "request_sent", "requests_changed", "group_changed", "recording_changed", "connected"].includes(event.type)) {
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
      demoMsg.textContent = "Zaplaceno";
    } catch (err) {
      demoMsg.className = "demo-msg error";
      demoMsg.textContent = errText(err, false);
    } finally {
      btn.disabled = false;
    }
  });

  Phone.ready.then(load);
})();
