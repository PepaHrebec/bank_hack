// Phone shell. Gives the app a small API on window.Phone:
//   Phone.notify({title, body, color, action?: {label, onClick}})
//                                       show a banner and add it to the pull-down list;
//                                       the action button runs onClick, then opens George
//   Phone.onEvent(fn)                   receive every event the orchestrator pushes
//   Phone.me / Phone.ready              who this phone belongs to
//   Phone.colors                        person id -> colour
//   Phone.initials(name)                "Petr Šafář" -> "PŠ"
// The shell also owns the home screen. Every `.app-window` opens from the home-screen
// icon whose data-opens is its id, and swiping up from the bottom edge closes it. Windows
// get "app-open" / "app-close" DOM events. Tapping a notification banner opens George.
//   Phone.openApp(id | null)            open a window by id, or go home with null
//   Phone.widget                        the home-screen widget; the app fills it, tapping it opens George
// After every (re)connect handlers get {type: "connected"}, so the app can refetch
// anything it missed while the connection was down.
(function () {
  const PERSON_COLORS = { 1: "#3b6cff", 2: "#2bb673", 3: "#f5a623", 4: "#e5487a" };
  const BANNER_MS = 4000;
  const EMPTY_SLOTS = 3;

  const screen = document.getElementById("screen");
  const shade = document.getElementById("shade");
  const shadeList = document.getElementById("shadeList");
  const pullZone = document.getElementById("pullZone");
  const bannerLayer = document.getElementById("banners");
  const appEl = document.getElementById("app");
  const swipeZone = document.getElementById("swipeZone");
  const windows = [...document.querySelectorAll(".app-window")];

  const handlers = [];
  const notifications = [];

  // ---- clock ----

  function hhmm(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
  }

  function tick() {
    const now = hhmm(new Date());
    document.querySelectorAll(".clock").forEach((el) => { el.textContent = now; });
  }
  tick();
  setInterval(tick, 1000);

  // ---- notifications ----

  function initials(name) {
    return name.trim().split(/\s+/).slice(0, 2).map((w) => w[0]).join("").toUpperCase();
  }

  // Buttons on a notification. `action` (one button) opens George and runs onClick there.
  // `actions` are handled right in the notification: onClick may return a promise; its
  // resolved text (e.g. "Paid ✓") replaces the buttons, a rejection shows its message.
  function noteActions(n) {
    if (n.actions) return n.actions;
    return n.action ? [{ ...n.action, opensApp: true }] : [];
  }

  function runInline(n, a) {
    n.pending = true;
    n.error = null;
    refreshNote(n);
    Promise.resolve()
      .then(() => a.onClick())
      .then((result) => { n.result = result || "Done"; })
      .catch((err) => { n.error = (err && err.message) || "Something went wrong"; })
      .finally(() => { n.pending = false; refreshNote(n); });
  }

  // Re-render a notification wherever it is shown (pull-down list and, if still up, its banner).
  function refreshNote(n) {
    renderShadeList();
    if (n.bannerEl && n.bannerEl.isConnected) n.bannerEl.replaceChildren(...noteContent(n, "now"));
  }

  function noteContent(n, timeText = n.time) {
    const icon = document.createElement("div");
    icon.className = "note-icon";
    icon.style.background = n.color;
    icon.textContent = initials(n.title || "?");

    const text = document.createElement("div");
    text.className = "note-text";
    const head = document.createElement("div");
    head.className = "note-head";
    const title = document.createElement("span");
    title.className = "note-title";
    title.textContent = n.title;
    const time = document.createElement("span");
    time.className = "note-time";
    time.textContent = timeText;
    head.append(title, time);
    const body = document.createElement("div");
    body.className = "note-body";
    body.textContent = n.body;
    text.append(head, body);
    const actions = noteActions(n);
    if (n.result) {
      const done = document.createElement("div");
      done.className = "note-result";
      done.textContent = n.result;
      text.append(done);
    } else if (actions.length) {
      const row = document.createElement("div");
      row.className = "note-actions";
      for (const a of actions) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "note-action" + (a.secondary ? " secondary" : "");
        btn.textContent = a.label;
        btn.disabled = Boolean(n.pending);
        // The button is its own target: neither the banner's tap nor its drag may see it.
        btn.addEventListener("pointerdown", (e) => e.stopPropagation());
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          if (!a.opensApp) {
            runInline(n, a);
            return;
          }
          openApp(appEl);
          try {
            a.onClick();
          } finally {
            setOpen(false);
            bannerLayer.replaceChildren();
          }
        });
        row.append(btn);
      }
      text.append(row);
      if (n.error) {
        const err = document.createElement("div");
        err.className = "note-error";
        err.textContent = n.error;
        text.append(err);
      }
    }

    return [icon, text];
  }

  function renderShadeList() {
    shadeList.replaceChildren();
    for (const n of notifications) {
      const item = document.createElement("div");
      item.className = "shade-item";
      item.append(...noteContent(n));
      shadeList.append(item);
    }
    for (let i = notifications.length; i < EMPTY_SLOTS; i++) {
      const slot = document.createElement("div");
      slot.className = "shade-slot";
      slot.textContent = "notification placeholder";
      shadeList.append(slot);
    }
  }

  function showBanner(n) {
    bannerLayer.replaceChildren();
    const banner = document.createElement("div");
    banner.className = "banner";
    banner.append(...noteContent(n, "now"));
    n.bannerEl = banner;
    bannerLayer.append(banner);

    const hide = () => {
      // Never pull the banner out from under a drag; try again once it's over.
      if (drag) { setTimeout(hide, 500); return; }
      banner.classList.remove("show");
      setTimeout(() => banner.remove(), 450);
    };
    banner.addEventListener("click", () => { hide(); openApp(appEl); });
    // Pulling the banner down opens the panel, like pulling the top edge.
    banner.addEventListener("pointerdown", (e) => startDrag(e, true));
    banner.addEventListener("pointermove", moveDrag);
    banner.addEventListener("pointerup", endDrag);
    banner.addEventListener("pointercancel", endDrag);
    banner.addEventListener("lostpointercapture", endDrag);
    requestAnimationFrame(() => requestAnimationFrame(() => banner.classList.add("show")));
    setTimeout(hide, BANNER_MS);
  }

  function notify({ title, body, color, action, actions }) {
    const n = { title, body, color: color || "#3b6cff", action, actions, time: hhmm(new Date()) };
    notifications.unshift(n);
    renderShadeList();
    if (!shade.classList.contains("open")) showBanner(n);
  }

  renderShadeList();

  // ---- pull-down panel ----

  let drag = null; // { startY, lastY, startOffset, height, moved }

  function setShadeOffset(px) {
    shade.style.transform = `translateY(${px}px)`;
  }

  function startDrag(e, opening) {
    const height = screen.clientHeight;
    drag = { startY: e.clientY, lastY: e.clientY, startOffset: opening ? -height : 0, height, moved: false };
    shade.classList.add("dragging");
    e.currentTarget.setPointerCapture(e.pointerId);
  }

  function moveDrag(e) {
    if (!drag) return;
    drag.lastY = e.clientY;
    const dy = e.clientY - drag.startY;
    if (Math.abs(dy) > 4) drag.moved = true;
    const offset = Math.min(0, Math.max(-drag.height, drag.startOffset + dy));
    setShadeOffset(offset);
  }

  function endDrag() {
    // Uses the last move position: lostpointercapture/pointercancel may report clientY 0.
    if (!drag) return;
    const dy = drag.lastY - drag.startY;
    const offset = Math.min(0, Math.max(-drag.height, drag.startOffset + dy));
    const visible = (drag.height + offset) / drag.height;
    const wasOpen = drag.startOffset === 0;
    // Open if pulled down past 30%; close if pushed up past 30%. A tap changes nothing.
    const open = !drag.moved ? wasOpen : wasOpen ? visible > 0.7 : visible > 0.3;
    drag = null;
    shade.classList.remove("dragging");
    shade.style.transform = "";
    setOpen(open);
  }

  function setOpen(open) {
    shade.classList.toggle("open", open);
    if (open) bannerLayer.replaceChildren();
  }

  pullZone.addEventListener("pointerdown", (e) => startDrag(e, true));
  pullZone.addEventListener("pointermove", moveDrag);
  pullZone.addEventListener("pointerup", endDrag);
  pullZone.addEventListener("pointercancel", endDrag);
  pullZone.addEventListener("lostpointercapture", endDrag);

  shade.addEventListener("pointerdown", (e) => startDrag(e, false));
  shade.addEventListener("pointermove", moveDrag);
  shade.addEventListener("pointerup", endDrag);
  shade.addEventListener("pointercancel", endDrag);
  shade.addEventListener("lostpointercapture", endDrag);

  // If the element that started the drag disappears (e.g. the banner is replaced), its own
  // listeners stop firing; the window still sees the pointer, so finish the drag there.
  window.addEventListener("pointermove", moveDrag);
  window.addEventListener("pointerup", endDrag);
  window.addEventListener("pointercancel", endDrag);
  document.addEventListener("lostpointercapture", endDrag);

  // Trackpad / mouse wheel: scroll down over the top strip opens, scroll up on the panel closes.
  pullZone.addEventListener("wheel", (e) => {
    if (e.deltaY < -10) { e.preventDefault(); setOpen(true); }
  }, { passive: false });
  shade.addEventListener("wheel", (e) => {
    if (e.deltaY > 10 && shadeList.scrollTop <= 0) setOpen(false);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setOpen(false);
  });

  // ---- home screen: swipe up from the bottom edge of an app, tap an icon to open one ----

  let swipe = null; // { startY, lastY, height }
  let current = appEl; // open window, or null on the home screen

  // An app grows out of / shrinks into its icon.
  function originAtIcon(win) {
    const icon = document.querySelector(`.icon[data-opens="${win.id}"]`);
    if (!icon) return;
    const s = screen.getBoundingClientRect();
    const i = icon.getBoundingClientRect();
    win.style.transformOrigin = `${i.left + i.width / 2 - s.left}px ${i.top + i.height / 2 - s.top}px`;
  }

  function openApp(win) {
    const previous = current;
    for (const w of windows) {
      originAtIcon(w);
      w.classList.remove("swiping");
      w.style.transform = "";
      w.style.borderRadius = "";
      w.classList.toggle("open", w === win);
    }
    current = win;
    screen.classList.toggle("at-home", !win);
    screen.classList.toggle("light-status", !win || win.dataset.statusbar === "light");
    if (previous && previous !== win) previous.dispatchEvent(new Event("app-close"));
    if (win && win !== previous) win.dispatchEvent(new Event("app-open"));
  }

  function swipeProgress() {
    return Math.min(1, Math.max(0, (swipe.startY - swipe.lastY) / (swipe.height * 0.6)));
  }

  swipeZone.addEventListener("pointerdown", (e) => {
    if (shade.classList.contains("open") || !current) return;
    swipe = { startY: e.clientY, lastY: e.clientY, height: screen.clientHeight };
    originAtIcon(current);
    current.classList.add("swiping");
    swipeZone.setPointerCapture(e.pointerId);
  });

  function moveSwipe(e) {
    if (!swipe) return;
    swipe.lastY = e.clientY;
    const p = swipeProgress();
    current.style.transform = `scale(${1 - 0.6 * p})`;
    current.style.borderRadius = `${p * 3}em`;
  }

  function endSwipe() {
    if (!swipe) return;
    const home = swipeProgress() > 0.15;
    swipe = null;
    openApp(home ? null : current);
  }

  swipeZone.addEventListener("pointermove", moveSwipe);
  window.addEventListener("pointermove", moveSwipe);
  window.addEventListener("pointerup", endSwipe);
  window.addEventListener("pointercancel", endSwipe);
  document.addEventListener("lostpointercapture", endSwipe);

  document.querySelectorAll("[data-opens]").forEach((icon) => {
    icon.addEventListener("click", () => openApp(document.getElementById(icon.dataset.opens)));
  });

  // ---- connection to the orchestrator ----

  function dispatch(event) {
    for (const fn of handlers) {
      try { fn(event); } catch (err) { console.error(err); }
    }
  }

  function connect() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/ws`);
    ws.addEventListener("open", () => dispatch({ type: "connected" }));
    ws.addEventListener("message", (msg) => {
      let event;
      try { event = JSON.parse(msg.data); } catch { return; }
      dispatch(event);
    });
    ws.addEventListener("close", () => setTimeout(connect, 2000));
  }
  connect();

  // ---- who am I ----

  const Phone = {
    me: null,
    colors: PERSON_COLORS,
    initials,
    openApp: (id) => openApp(id ? document.getElementById(id) : null),
    widget: document.getElementById("widget"),
    notify,
    onEvent(fn) { handlers.push(fn); },
    ready: null,
  };

  // Keep trying until the server answers, so a page opened before the server starts still comes up.
  async function whoAmI() {
    for (;;) {
      try {
        const s = await (await fetch("/api/state")).json();
        Phone.me = s.me;
        document.title = `${s.me.name} · Phone`;
        return s.me;
      } catch {
        await new Promise((r) => setTimeout(r, 2000));
      }
    }
  }
  Phone.ready = whoAmI();
  window.Phone = Phone;
})();
