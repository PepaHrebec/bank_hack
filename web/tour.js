// The guided demo tour (served only by `run.py --demo`). A bubble beside the phone says what to do
// next; only the highlighted element(s) take input, everything else is blocked until the last step.
// It reads the app through window.Phone and the "geoff:state" / "geoff:view" events, and finds
// what to highlight by selector and visible text, so the app itself needs no tour-specific ids.
(function () {
  const screen = document.getElementById("screen");
  const phone = document.querySelector(".phone");
  const WAIT_MS = 12000; // a step waiting on a bot or the model offers "Pokračovat" after this

  const ctx = { state: null, view: "main", events: [] };

  // ---- finding things ----

  const visible = (e) => !!e && e.getClientRects().length > 0;
  const all = (sel, root = document) => [...root.querySelectorAll(sel)].filter(visible);
  const withText = (sel, text, root) => all(sel, root).find((e) => e.textContent.includes(text)) || null;
  const S = () => ctx.state || {};
  const has = (list, id) => (list || []).includes(id);
  const appOpen = (id) => document.getElementById(id).classList.contains("open");
  const atHome = () => screen.classList.contains("at-home");
  const activeView = () => document.querySelector("#app .view.active");
  const backBtn = () => activeView() && activeView().querySelector(".back-btn");
  const popup = (text) => all(".popup-sheet").find((p) => p.textContent.includes(text)) || null;
  const chata = () => (S().groups || []).find((g) => g.name === "Chata");
  const CHAT_QUESTION = "Shrň mi minulý měsíc v platbách mezi všechny obchodníky do grafu";

  // Prefill a field as if typed (the app listens to input / change).
  function setVal(e, v) {
    if (!e) return;
    e.value = v;
    e.dispatchEvent(new Event("input", { bubbles: true }));
    e.dispatchEvent(new Event("change", { bubbles: true }));
  }
  function setChecked(box, on) {
    if (!box || box.checked === on) return;
    box.checked = on;
    box.dispatchEvent(new Event("change", { bubbles: true }));
  }
  const pick = (root, name) => withText("label.pick", name, root)?.querySelector("input");

  // Where to tap to get to a view: `hops` maps a view to the element that leads on from it.
  // From anywhere else, the back arrow; from the home screen, the Geoff icon.
  function route(hops) {
    if (!appOpen("app")) return [document.querySelector('.dock [data-opens="app"]')];
    const hop = hops[ctx.view];
    return [hop ? hop() : backBtn()];
  }
  const tile = (text) => () => withText("#app .view.active .big-btn", text);
  const action = (text) => () => withText("#app .view.active .settle", text);

  // ---- the steps ----
  // text: the bubble; target(): elements that take input; done(): has it happened;
  // button: a bubble button {label, run?} (a card step without target is done when it's tapped);
  // wait: offer "Pokračovat" after WAIT_MS; enter(): runs once when the step starts;
  // fill(target): prefills the target form once (returns false to retry, e.g. while it loads).

  const steps = [
    {
      title: "Vítej v Geoffovi",
      text: "Ahoj Davide! Projdeme spolu, co Geoff umí: od běžných plateb přes přátele a skupinové platby až po AI. Klepej vždy na zvýrazněné místo.",
      button: { label: "Začít" },
    },
    {
      title: "1/6 Základy",
      text: "Nahoře vidíš zůstatek a dnešní změnu. Klepni na kartu se zůstatkem a podívej se do historie.",
      target: () => route({ main: () => document.querySelector("#app .balance-card") }),
      done: () => ctx.view === "history",
    },
    {
      title: "1/6 Základy",
      text: "Tady je každá platba: karta, převody i výplata. Vrať se zpátky šipkou.",
      target: () => [backBtn()],
      done: () => ctx.view === "main",
    },
    {
      title: "1/6 Základy",
      text: "Zaplatit jde na jakýkoli český účet. Klepni na Zaplatit.",
      target: () => route({ main: tile("Zaplatit") }),
      done: () => ctx.view === "accountPay",
    },
    {
      title: "1/6 Základy",
      text: "Zaplať Timothymu za kolo: účet 5555555555, banka 0100 – Komerční banka, částka 500, zpráva „za kolo“. Pak Zaplatit.",
      target: () => ctx.view === "accountPay" ? [activeView().querySelector("form")] : route({ main: tile("Zaplatit") }),
      fill: (form) => {
        const bank = form.querySelector(".account-bank");
        if (!bank || bank.options.length < 2) return false; // banks still loading
        setVal(form.querySelector(".account-number"), "5555555555");
        setVal(bank, "0100");
        setVal(form.querySelector("input[inputmode=decimal]"), "500");
        setVal(form.querySelector("input[placeholder^='Zpráva']"), "za kolo");
        return true;
      },
      done: () => (S().history || []).some((h) => h.kind === "account" && h.amount === 500),
    },
    {
      title: "1/6 Základy",
      text: "Hotovo. Ještě QR kód: tím si necháš zaplatit od kohokoli.",
      target: () => route({ main: tile("QR kód") }),
      done: () => ctx.view === "qr",
    },
    {
      title: "1/6 Základy",
      text: "Částku a poznámku můžeš do QR kódu dopsat. Vrať se zpátky.",
      target: () => [backBtn()],
      done: () => ctx.view === "main",
    },
    {
      title: "2/6 Přátelé",
      text: "Přátelé jsou lidé s účtem v Geoffu (…/0800). Otevři Přátelé.",
      target: () => route({ main: tile("Přátelé") }),
      done: () => ctx.view === "contacts",
    },
    {
      title: "2/6 Přátelé",
      text: "Přidej Štěpána: Přidat přítele a jeho účet 1111111111/0800.",
      target: () => {
        const p = popup("Přidat přítele");
        return p ? [p] : route({ main: tile("Přátelé"), contacts: action("Přidat přítele") });
      },
      fill: (sheet) => {
        if (!sheet.classList.contains("popup-sheet")) return false;
        setVal(sheet.querySelector("input"), "1111111111/0800");
        return true;
      },
      done: () => has(S().friend_requests_sent, 1) || has(S().friends, 1),
    },
    {
      title: "2/6 Přátelé",
      text: "Žádost odešla. Štěpán ji teď potvrzuje na svém telefonu…",
      wait: true,
      done: () => has(S().friends, 1),
    },
    {
      title: "2/6 Přátelé",
      text: "Štěpán je tvůj přítel. Zbytek týmu přidáme najednou: Jirku, Pepu a Petra.",
      button: {
        label: "Přidat zbytek",
        run: async () => {
          for (const id of [2, 3, 4]) {
            await fetch("/api/friends", {
              method: "POST", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ account: `${String(id).repeat(10)}/0800` }),
            }).catch(() => {});
          }
        },
      },
      wait: true,
      done: () => [1, 2, 3, 4].every((id) => has(S().friends, id)),
    },
    {
      title: "2/6 Přátelé",
      text: "Všichni jsou přátelé. Teď si řekni o peníze: klepni na Jirku, přepni na Žádost, 250 Kč, poznámka „kino“ a Vyžádat.",
      target: () => ctx.view === "pay"
        ? [activeView().querySelector("form")]
        : route({ main: tile("Přátelé"), contacts: () => withText("#app .view.active button.contact", "Jirka") }),
      fill: (form) => {
        if (ctx.view !== "pay" || !activeView().querySelector(".pay-who").textContent.includes("Jirka")) return false;
        withText("#app .view.active .seg", "Žádost").click();
        setVal(document.getElementById("amount"), "250");
        setVal(document.getElementById("note"), "kino");
        return true;
      },
      done: () => (S().requested || []).some((r) => r.payer === 2 && r.amount === 250 && r.status === "paid"),
      wait: true,
    },
    {
      title: "2/6 Přátelé",
      text: "Jirka hned zaplatil. A teď naopak: Pepa po tobě chce 320 Kč za pizzu. Otevři K zaplacení.",
      enter: () => fetch("/api/demo/bot-request", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from: 3, amount: 320, note: "pizza" }),
      }).catch(() => {}),
      target: () => route({ main: tile("Přátelé"), contacts: action("K zaplacení") }),
      done: () => ctx.view === "tobepaid",
    },
    {
      title: "2/6 Přátelé",
      text: "Zaplať Pepovi: Zaplatit a potvrď platbu.",
      target: () => {
        if (ctx.view === "confirm") return [withText("#app .view.active .confirm-btn", "Potvrdit")];
        const row = withText("#app .view.active .req", "Pepa");
        return row ? [row.querySelector(".req-btn.pay")] : route({ main: tile("Přátelé"), contacts: action("K zaplacení") });
      },
      done: () => (S().history || []).some((h) => h.kind === "transfer" && h.recipient === 3 && h.amount === 320),
      wait: true, // Pepa's request comes from the server; if it never arrives, don't get stuck
    },
    {
      title: "3/6 Skupinové vyrovnání",
      text: "Společná chata? Založ skupinu: Přátelé → Skupinové vyrovnání → Nová skupina.",
      target: () => route({
        main: tile("Přátelé"), contacts: action("Skupinové vyrovnání"), groups: tile("Nová skupina"),
      }),
      done: () => ctx.view === "newgroup" || !!chata(),
    },
    {
      title: "3/6 Skupinové vyrovnání",
      text: "Pojmenuj ji „Chata“, zaškrtni všechny čtyři a Vytvořit skupinu.",
      target: () => ctx.view === "newgroup" ? [activeView().querySelector("form")] : route({
        main: tile("Přátelé"), contacts: action("Skupinové vyrovnání"), groups: tile("Nová skupina"),
      }),
      fill: (form) => {
        if (ctx.view !== "newgroup") return false;
        setVal(form.querySelector("input[type=text]"), "Chata");
        for (const name of ["Štěpán", "Jirka", "Pepa", "Petr"]) setChecked(pick(form, name), true);
        return true;
      },
      done: () => !!chata(),
    },
    {
      title: "3/6 Skupinové vyrovnání",
      text: "Pozvánky odešly. Kluci je přijímají a přidávají, co zaplatili oni: jídlo, pití, benzín…",
      wait: true,
      done: () => chata() && (chata().invited || []).length === 0 && chata().members.length > 1
        && chata().expenses.filter((e) => e.payer !== 5).length >= 3,
    },
    {
      title: "3/6 Skupinové vyrovnání",
      text: "Ubytování jsi zaplatil ty: přidej výdaj 4 000 Kč „ubytování“.",
      target: () => [document.querySelector("#app .view.active .expense-form") || backBtn()],
      fill: (form) => {
        if (!form.classList.contains("expense-form")) return false;
        const [amount, desc] = form.querySelectorAll("input");
        setVal(amount, "4000");
        setVal(desc, "ubytování");
        return true;
      },
      done: () => chata() && chata().total >= 4000,
    },
    {
      title: "3/6 Skupinové vyrovnání",
      text: "Teď Schválit a vyrovnat. Geoff všechno sečte, rozdělí rovným dílem a pošle žádosti, aby proběhlo co nejméně plateb.",
      target: () => [withText("#app .view.active .approve-btn", "Schválit")],
      done: () => chata() && chata().status !== "open",
    },
    {
      title: "3/6 Skupinové vyrovnání",
      text: "Žádosti odešly všem čtyřem. Sleduj, jak ti chodí peníze…",
      wait: true,
      done: () => {
        const rows = (S().requested || []).filter((r) => r.group && r.group.title === "Chata");
        return rows.length >= 4 && rows.every((r) => r.status === "paid");
      },
    },
    {
      title: "4/6 Skupinová platba",
      text: "Skupinovou platbu spustíš i bez otevírání aplikace, z widgetu. Jdi na plochu.",
      button: { label: "Na plochu", run: () => Phone.openApp(null) },
      done: () => atHome(),
    },
    {
      title: "4/6 Skupinová platba",
      text: "Jdete se Štěpánem na večer. Klepni ve widgetu na Spustit skupinovou platbu.",
      target: () => atHome() ? [document.querySelector("#widget .widget-rec")] : [],
      done: () => !!popup("Koho pozvat") || !!S().recording,
    },
    {
      title: "4/6 Skupinová platba",
      text: "Pozvi jen Štěpána a Spustit.",
      target: () => {
        const p = popup("Koho pozvat");
        if (p) return [p];
        // The popup was closed with Zrušit: start again from the widget.
        return atHome() && !S().recording ? [document.querySelector("#widget .widget-rec")] : [];
      },
      fill: (sheet) => {
        if (!sheet.classList.contains("popup-sheet")) return false;
        for (const name of ["Štěpán", "Jirka", "Pepa", "Petr"]) setChecked(pick(sheet, name), name === "Štěpán");
        return true;
      },
      // Štěpán has to be in it; a session without him still lets the viewer go on after a while.
      done: () => S().recording && (has(S().recording.participants, 1) || has(S().recording.invited, 1)),
      wait: true,
    },
    {
      title: "4/6 Skupinová platba",
      text: "Štěpán se připojuje…",
      wait: true,
      done: () => S().recording && has(S().recording.participants, 1),
    },
    {
      title: "4/6 Skupinová platba",
      text: "Zaplať kartou v Lokálu: terminál vpravo dole (na úzké obrazovce pod 💳) má předvyplněno 1 240 Kč. Zaplatit.",
      target: () => [document.getElementById("demoAside")],
      fill: () => {
        setVal(document.getElementById("demoAmount"), "1240");
        setVal(document.getElementById("demoNote"), "Lokál");
        return true;
      },
      done: () => S().recording && S().recording.payments.some((p) => p.amount === 1240),
    },
    {
      title: "4/6 Skupinová platba",
      text: "Štěpán mezitím platí benzín. Všechno, co během skupinové platby zaplatíte, se počítá dohromady.",
      enter: () => setTimeout(check, 3200),
      done: () => Date.now() - enteredAt > 3000,
    },
    {
      title: "4/6 Skupinová platba",
      text: "Večer skončil. Ve widgetu klepni na Ukončit skupinovou platbu.",
      enter: () => document.getElementById("demoAside").classList.remove("open"),
      target: () => atHome() ? [document.querySelector("#widget .widget-rec")] : [],
      done: () => !!popup("Skupinová platba ukončena"),
    },
    {
      title: "4/6 Skupinová platba",
      text: "Tady jsou platby vás obou. Vytvoř z nich skupinové vyrovnání.",
      target: () => {
        const p = popup("Skupinová platba ukončena");
        if (p) return [withText(".send-btn", "Vytvořit", p)];
        // A session without Štěpán ends in the new-group form instead.
        return ctx.view === "newgroup" ? [activeView().querySelector("form")] : [];
      },
      done: () => (S().groups || []).some((g) => g.name.startsWith("Skupinová platba")),
      wait: true,
    },
    {
      title: "5/6 Geoff AI",
      text: "Geoff zná tvoje finance. Vrať se na hlavní obrazovku a zeptej se ho na minulý měsíc a Poslat.",
      target: () => ctx.view === "main" && appOpen("app")
        ? [document.querySelector("#app .view.active .chat-form")]
        : route({}),
      fill: (form) => {
        if (!form.classList.contains("chat-form")) return false;
        setVal(form.querySelector(".chat-input"), CHAT_QUESTION);
        return true;
      },
      done: () => {
        const bots = all("#app .chat-bot");
        const last = bots[bots.length - 1];
        return !!last && last.textContent.trim() !== "…";
      },
      wait: true,
    },
    {
      title: "6/6 Budoucnost",
      text: "Věříme, že AI bude přímo v telefonu: lokálně uvidí, co děláš, a sama nabídne další krok. Ukážeme ti to na WhatsAppu.",
      button: { label: "Ukázat", run: () => Phone.openApp(null) },
      done: () => atHome(),
    },
    {
      title: "6/6 Budoucnost",
      text: "Otevři WhatsApp.",
      target: () => [document.querySelector('.dock [data-opens="whatsapp"]')],
      done: () => appOpen("whatsapp"),
    },
    {
      title: "6/6 Budoucnost",
      text: "Otevři chat s Jirkou a pošli mu „Dlužíš mi 450 za lístky“.",
      target: () => {
        const wa = document.getElementById("whatsapp");
        if (!appOpen("whatsapp")) return [document.querySelector('.dock [data-opens="whatsapp"]')];
        return wa.classList.contains("in-chat")
          ? [wa.querySelector(".wa-compose")]
          : [withText("#whatsapp .wa-row", "Jirka")];
      },
      fill: (form) => {
        if (!form.classList.contains("wa-compose")) return false;
        setVal(form.querySelector(".wa-input"), "Dlužíš mi 450 za lístky");
        return true;
      },
      done: () => ctx.events.some((e) => e.type === "message" && e.message.sender === 5 && e.message.text.includes("450")),
    },
    {
      title: "6/6 Budoucnost",
      text: "Geoff si zprávy všiml a nabízí poslat Jirkovi žádost. Klepni na Potvrdit.",
      enter: () => Phone.holdBanners(true),
      target: () => {
        const btn = all(".banner .note-action, .shade.open .note-action")
          .find((b) => b.textContent === "Potvrdit" && b.closest(".banner, .shade-item").textContent.includes("450"));
        if (btn) return [btn];
        // The banner is gone: the suggestion waits in the pull-down list.
        return ctx.events.some((e) => e.type === "geoff_suggestion") ? [document.getElementById("pullZone")] : [];
      },
      done: () => (S().requested || []).some((r) => r.payer === 2 && r.amount === 450),
      wait: true,
    },
    {
      title: "Hotovo",
      text: "To je celý Geoff. Teď si to vyzkoušej sám, všechno funguje. Obnovením stránky začneš znovu.",
      enter: () => Phone.holdBanners(false),
      button: { label: "Vyzkoušet" },
    },
  ];

  // ---- the layer ----

  const ring = document.createElement("div");
  ring.className = "tour-ring";
  const bubble = document.createElement("div");
  bubble.className = "tour-bubble";
  document.body.append(ring, bubble);

  let index = -1;
  let enteredAt = 0;
  let tapped = false; // a card step's button was tapped
  let waitTimer = null;
  let targets = [];
  let ended = false;
  let filled = new WeakSet(); // targets this step has prefilled
  let scrolledTo = null;

  function render(step, showContinue) {
    bubble.replaceChildren();
    const title = document.createElement("div");
    title.className = "tour-title";
    title.textContent = step.title;
    const text = document.createElement("div");
    text.className = "tour-text";
    text.textContent = step.text;
    bubble.append(title, text);
    if (step.fill) {
      const note = document.createElement("div");
      note.className = "tour-prefill";
      note.textContent = "✎ Hodnoty předvyplníme za tebe. Zkontroluj je, než odešleš.";
      bubble.append(note);
    }
    const buttons = [];
    if (step.button) buttons.push([step.button.label, async (b) => {
      b.disabled = true;
      tapped = true;
      if (step.button.run) await step.button.run();
      check();
    }]);
    if (showContinue) buttons.push(["Pokračovat", () => next()]);
    if (buttons.length) {
      const row = document.createElement("div");
      row.className = "tour-buttons";
      for (const [label, onClick] of buttons) {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "tour-btn" + (label === "Pokračovat" ? " secondary" : "");
        b.textContent = label;
        b.addEventListener("click", () => onClick(b));
        row.append(b);
      }
      bubble.append(row);
    }
    bubble.classList.toggle("card", !step.target && !step.wait && !!step.button && !step.done);
  }

  function next() {
    clearTimeout(waitTimer);
    index += 1;
    if (index >= steps.length) return finish();
    const step = steps[index];
    enteredAt = Date.now();
    tapped = false;
    filled = new WeakSet();
    render(step, false);
    if (step.wait) waitTimer = setTimeout(() => render(step, true), WAIT_MS);
    if (step.enter) step.enter();
    check();
  }

  function isDone(step) {
    if (step.done) return !!step.done();
    return tapped; // a card step
  }

  let queued = false;
  function check() {
    if (ended || queued) return;
    queued = true;
    queueMicrotask(() => {
      queued = false;
      if (ended || index < 0) return;
      const step = steps[index];
      if (isDone(step)) { next(); return; }
      targets = step.target ? step.target().filter(Boolean) : [];
      const first = targets[0];
      if (first && step.fill && !filled.has(first) && step.fill(first)) filled.add(first);
      // Bring the target into view (a button below the fold, a long form).
      if (first && first !== scrolledTo) {
        scrolledTo = first;
        first.scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    });
  }

  function finish() {
    ended = true;
    clearTimeout(waitTimer);
    Phone.holdBanners(false);
    ring.remove();
    bubble.remove();
    for (const type of BLOCKED) window.removeEventListener(type, block, true);
    window.removeEventListener("wheel", blockWheel, { capture: true });
    observer.disconnect();
  }

  // Keep the ring on the targets and the bubble beside the phone, every frame.
  function place() {
    if (ended) return;
    const rects = targets.filter(visible).map((t) => t.getBoundingClientRect());
    if (rects.length) {
      const pad = 6;
      const left = Math.min(...rects.map((r) => r.left)) - pad;
      const top = Math.min(...rects.map((r) => r.top)) - pad;
      const right = Math.max(...rects.map((r) => r.right)) + pad;
      const bottom = Math.max(...rects.map((r) => r.bottom)) + pad;
      Object.assign(ring.style, { left: `${left}px`, top: `${top}px`, width: `${right - left}px`, height: `${bottom - top}px` });
      ring.classList.add("on");
    } else {
      ring.classList.remove("on");
    }
    const p = phone.getBoundingClientRect();
    const w = bubble.offsetWidth;
    const h = bubble.offsetHeight;
    const gap = 24;
    let x, y;
    // Beside the phone: on the right, unless the target itself is out there (the card terminal).
    const targetRight = rects.some((r) => r.left >= p.right);
    const roomRight = window.innerWidth - p.right >= w + gap * 2;
    const roomLeft = p.left >= w + gap * 2;
    if ((roomRight && !targetRight) || (targetRight && roomLeft)) {
      x = targetRight ? p.left - gap - w : p.right + gap;
      const anchor = rects.length ? (Math.min(...rects.map((r) => r.top)) + Math.max(...rects.map((r) => r.bottom))) / 2 : p.top + p.height / 2;
      y = Math.min(Math.max(anchor - h / 2, 16), window.innerHeight - h - 16);
    } else {
      // Narrow window: along the top or bottom edge, whichever is away from the target.
      x = Math.max(16, (window.innerWidth - w) / 2);
      const low = rects.length && Math.max(...rects.map((r) => r.bottom)) > window.innerHeight / 2;
      y = low ? 16 : window.innerHeight - h - 16;
    }
    bubble.style.left = `${x}px`;
    bubble.style.top = `${y}px`;
    requestAnimationFrame(place);
  }

  // ---- blocking ----

  const BLOCKED = ["pointerdown", "pointerup", "mousedown", "mouseup", "click", "dblclick", "touchstart",
    "touchend", "keydown", "keypress", "submit", "contextmenu"];
  function block(e) {
    if (bubble.contains(e.target)) return;
    if (targets.some((t) => t.contains(e.target))) return;
    // Typing into a focused field of the current target (e.g. Enter in the popup's input) is fine.
    if (e.type.startsWith("key") && targets.some((t) => t.contains(document.activeElement))) return;
    e.preventDefault();
    e.stopImmediatePropagation();
  }
  for (const type of BLOCKED) window.addEventListener(type, block, true);
  // Scrolling is fine, except a wheel/trackpad pull on the top edge, which opens the notification panel.
  function blockWheel(e) {
    if (!e.target.closest || !e.target.closest("#pullZone, .shade")) return;
    if (targets.some((t) => t.contains(e.target))) return;
    e.preventDefault();
    e.stopImmediatePropagation();
  }
  window.addEventListener("wheel", blockWheel, { capture: true, passive: false });

  // ---- what the app tells us ----

  document.addEventListener("geoff:state", (e) => { ctx.state = e.detail; check(); });
  document.addEventListener("geoff:view", (e) => { ctx.view = e.detail; check(); });
  Phone.onEvent((e) => { ctx.events.push(e); check(); });
  const observer = new MutationObserver(() => check());
  observer.observe(screen, { subtree: true, childList: true, attributes: true, attributeFilter: ["class", "hidden"] });
  observer.observe(document.getElementById("demoAside"), { attributes: true, attributeFilter: ["class"] });

  Phone.ready.then(() => {
    next();
    requestAnimationFrame(place);
  });
})();
