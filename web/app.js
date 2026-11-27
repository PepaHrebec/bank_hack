// Placeholder bank app: balance, send money, history.
// Talks to the shell only through window.Phone, so it can be swapped for the real app.
(function () {
  const root = document.getElementById("app");
  let state = null;
  let recipient = null;

  const czk = (n) => `${n.toLocaleString("cs-CZ")} CZK`;
  const nameOf = (id) => state.people.find((p) => p.id === id).name;

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function avatar(person) {
    const a = el("span", "avatar", String(person.id));
    a.style.background = Phone.colors[person.id];
    return a;
  }

  async function load() {
    state = await (await fetch("/api/state")).json();
    render();
  }

  function render() {
    const { me, people, balance, history } = state;
    const others = people.filter((p) => p.id !== me.id);
    if (!others.some((p) => p.id === recipient)) recipient = others[0].id;

    // Keep what's typed in the form across re-renders.
    const prevAmount = root.querySelector("#amount")?.value ?? "";
    const prevNote = root.querySelector("#note")?.value ?? "";

    root.replaceChildren();

    const header = el("header", "app-header");
    header.append(avatar(me), el("div", "hello", `Hi, ${me.name}`));

    const card = el("section", "balance-card");
    card.style.setProperty("--accent", Phone.colors[me.id]);
    card.append(el("div", "balance-label", "Balance"), el("div", "balance-value", czk(balance)));

    const form = el("form", "send");
    form.append(el("h3", null, "Send money"));
    const chips = el("div", "chips");
    for (const p of others) {
      const chip = el("button", "chip" + (p.id === recipient ? " active" : ""));
      chip.type = "button";
      chip.append(avatar(p), el("span", null, p.name));
      chip.addEventListener("click", () => { recipient = p.id; render(); });
      chips.append(chip);
    }
    const amount = el("input", "field");
    Object.assign(amount, { id: "amount", type: "number", min: "1", step: "1", inputMode: "numeric", placeholder: "Amount (CZK)", value: prevAmount });
    const note = el("input", "field");
    Object.assign(note, { id: "note", type: "text", maxLength: 80, placeholder: "Note (optional)", value: prevNote });
    const button = el("button", "send-btn", "Send");
    button.type = "submit";
    const msg = el("div", "form-msg");
    form.append(chips, amount, note, button, msg);
    form.addEventListener("submit", (e) => { e.preventDefault(); send(amount, note, button, msg); });

    const list = el("section", "history");
    list.append(el("h3", null, "History"));
    if (history.length === 0) list.append(el("div", "empty", "No payments yet"));
    for (const p of history) {
      const outgoing = p.sender === me.id;
      const other = outgoing ? p.recipient : p.sender;
      const row = el("div", "tx");
      const info = el("div", "tx-info");
      info.append(el("div", "tx-name", `${outgoing ? "To" : "From"} ${nameOf(other)}`));
      const meta = p.note ? `${p.note} · ${p.created_at.slice(11, 16)}` : p.created_at.slice(11, 16);
      info.append(el("div", "tx-meta", meta));
      row.append(avatar({ id: other }), info,
        el("div", "tx-amount " + (outgoing ? "out" : "in"), `${outgoing ? "−" : "+"}${czk(p.amount)}`));
      list.append(row);
    }

    root.append(header, card, form, list);
  }

  async function send(amountInput, noteInput, button, msg) {
    msg.className = "form-msg";
    msg.textContent = "";
    button.disabled = true;
    const amount = amountInput.value === "" ? null : Number(amountInput.value);
    try {
      const r = await fetch("/api/payments", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ recipient, amount, note: noteInput.value }),
      });
      const body = await r.json();
      if (!r.ok) {
        msg.classList.add("error");
        msg.textContent = body.detail;
        return;
      }
      amountInput.value = "";
      noteInput.value = "";
      await load();
      const done = root.querySelector(".form-msg");
      done.classList.add("ok");
      done.textContent = `Sent ${czk(body.amount)} to ${nameOf(body.recipient)}`;
    } catch {
      msg.classList.add("error");
      msg.textContent = "Can't reach the bank. Try again.";
    } finally {
      button.disabled = false;
    }
  }

  Phone.onEvent((event) => {
    if (event.type === "payment_received") {
      const note = event.payment.note ? `\n${event.payment.note}` : "";
      Phone.notify({ title: event.from, body: event.text + note, color: Phone.colors[event.payment.sender] });
      load();
    } else if (event.type === "payment_sent") {
      load();
    }
  });

  Phone.ready.then(load);
})();
