// Phone shell. Gives the app a small API on window.Phone:
//   Phone.notify({title, body, color})  show a banner and add it to the pull-down list
//   Phone.onEvent(fn)                   receive every event the orchestrator pushes
//   Phone.me / Phone.ready              who this phone belongs to
//   Phone.colors                        person id -> colour
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

  function noteContent(n) {
    const icon = document.createElement("div");
    icon.className = "note-icon";
    icon.style.background = n.color;
    icon.textContent = (n.title || "?").trim().slice(-1);

    const text = document.createElement("div");
    text.className = "note-text";
    const head = document.createElement("div");
    head.className = "note-head";
    const title = document.createElement("span");
    title.className = "note-title";
    title.textContent = n.title;
    const time = document.createElement("span");
    time.className = "note-time";
    time.textContent = n.time;
    head.append(title, time);
    const body = document.createElement("div");
    body.className = "note-body";
    body.textContent = n.body;
    text.append(head, body);

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
    banner.append(...noteContent({ ...n, time: "now" }));
    bannerLayer.append(banner);

    const hide = () => {
      // Never pull the banner out from under a drag; try again once it's over.
      if (drag) { setTimeout(hide, 500); return; }
      banner.classList.remove("show");
      setTimeout(() => banner.remove(), 450);
    };
    banner.addEventListener("click", hide);
    // Pulling the banner down opens the panel, like pulling the top edge.
    banner.addEventListener("pointerdown", (e) => startDrag(e, true));
    banner.addEventListener("pointermove", moveDrag);
    banner.addEventListener("pointerup", endDrag);
    banner.addEventListener("pointercancel", endDrag);
    banner.addEventListener("lostpointercapture", endDrag);
    requestAnimationFrame(() => requestAnimationFrame(() => banner.classList.add("show")));
    setTimeout(hide, BANNER_MS);
  }

  function notify({ title, body, color }) {
    const n = { title, body, color: color || "#3b6cff", time: hhmm(new Date()) };
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
