// Placeholder bank app: balance, send money, history.
// Talks to the shell only through window.Phone, so it can be swapped for the real app.
// The screen is built once; refreshes only touch the balance and history, so a person
// typing in the form keeps focus and their message line when someone else pays them.
(function () {
  const root = document.getElementById("app");
  let state = null;
  let recipient = null;
  let ui = null; // elements updated on refresh

  const czk = (n) => `${n.toLocaleString("cs-CZ")} CZK`;
  const nameOf = (id) => state.people.find((p) => p.id === id).name;
  const firstName = (name) => name.split(" ")[0];

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function avatar(person) {
    const a = el("span", "avatar", Phone.initials(person.name));
    a.style.background = Phone.colors[person.id];
    return a;
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
    recipient = others[0].id;

    const card = el("section", "balance-card");
    card.style.setProperty("--accent", Phone.colors[me.id]);
    const balance = el("div", "balance-value");
    card.append(el("div", "balance-label", "Balance"), balance);

    const form = el("form", "send");
    form.append(el("h3", null, "Send money"));
    const chips = el("div", "chips");
    for (const p of others) {
      const chip = el("button", "chip" + (p.id === recipient ? " active" : ""));
      chip.type = "button";
      chip.append(avatar(p), el("span", null, firstName(p.name)));
      chip.addEventListener("click", () => {
        recipient = p.id;
        chips.querySelectorAll(".chip").forEach((c) => c.classList.toggle("active", c === chip));
      });
      chips.append(chip);
    }
    const amount = el("input", "field");
    Object.assign(amount, { type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Amount (CZK)" });
    amount.id = "amount";
    const note = el("input", "field");
    Object.assign(note, { type: "text", maxLength: 80, placeholder: "Note (optional)" });
    note.id = "note";
    const button = el("button", "send-btn", "Send");
    button.type = "submit";
    const msg = el("div", "form-msg");
    form.append(chips, amount, note, button, msg);
    form.addEventListener("submit", (e) => { e.preventDefault(); send(); });

    const historyBox = el("section", "history");
    const historyList = el("div");
    historyBox.append(el("h3", null, "History"), historyList);

    root.replaceChildren(card, form, historyBox);
    ui = { balance, amount, note, button, msg, historyList };
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
    ui.button.disabled = true;
    const amount = ui.amount.value === "" ? null : Number(ui.amount.value);
    try {
      const r = await fetch("/api/payments", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ recipient, amount, note: ui.note.value }),
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
      ui.button.disabled = false;
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
