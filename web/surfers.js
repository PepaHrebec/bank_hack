// Geoff Surfers: endless three-lane pseudo-3D runner. Self-contained; talks to the shell via window.Phone.
(function () {
  const root = document.getElementById("surfers");
  if (!root) return;

  const W = 360, H = 560, CX = W / 2, HOR = 170, GY = 500, LW = 95;
  const KEY = "geoffSurfersBest";
  const proj = (d) => 1 / (1 + d / 160);
  const sx = (lane, z) => CX + lane * LW * z;
  const sy = (z) => HOR + (GY - HOR) * z;

  // Pure collision test. Returns "hit", "coin" or null.
  function hit(o, s) {
    if (Math.abs(o.p - s.dist) > 18 || Math.abs(o.l - s.x) >= 0.55) return null;
    if (o.t === "coin") return "coin";
    if (o.t === "tall") return "hit";
    if (o.t === "low") return s.y < 38 ? "hit" : null;
    return null;
  }
  console.assert(hit({ t: "tall", p: 100, l: 0 }, { dist: 100, x: 0, y: 0 }) === "hit", "tall = hit");
  console.assert(hit({ t: "low", p: 100, l: 0 }, { dist: 100, x: 0, y: 60 }) === null, "low while jumping = null");
  console.assert(hit({ t: "low", p: 100, l: 0 }, { dist: 100, x: 0, y: 0 }) === "hit", "low on ground = hit");
  console.assert(hit({ t: "tall", p: 100, l: 1 }, { dist: 100, x: 0, y: 0 }) === null, "other lane = null");
  console.assert(hit({ t: "coin", p: 100, l: 0 }, { dist: 100, x: 0, y: 0 }) === "coin", "coin = coin");

  const cv = document.createElement("canvas");
  cv.width = W; cv.height = H;
  const c = cv.getContext("2d");

  root.innerHTML =
    '<div class="sf-head"><h2>Geoff Surfers</h2><button class="sf-home" type="button">Domů</button></div>';
  root.appendChild(cv);
  const help = document.createElement("p");
  help.className = "sf-help";
  help.innerHTML = "Myší vybereš dráhu. <b>Mezerník</b> nebo klik = skok. Bariéry přeskoč, vysoké bloky objeď.";
  root.appendChild(help);
  root.querySelector(".sf-home").addEventListener("click", () => {
    if (window.Phone) window.Phone.openApp(null);
  });

  let best = 0;
  try { best = +localStorage.getItem(KEY) || 0; } catch (e) {}

  let st = gfresh();
  let mode = "ready";
  let lane = 0, last = 0, overAt = 0, open = false, ticks = 0;
  window.__surfers = { get st() { return st; }, get mode() { return mode; }, get ticks() { return ticks; }, get lane() { return lane; }, get open() { return open; } };

  function gfresh() {
    return { dist: 0, x: 0, y: 0, vy: 0, speed: 260, coins: 0, objs: [], nextRow: 500, t: 0 };
  }

  function score() { return Math.floor(st.dist / 10) + 10 * st.coins; }

  function genRows() {
    while (st.nextRow < st.dist + 1600) {
      const free = Math.floor(Math.random() * 3) - 1;
      for (let l = -1; l <= 1; l++) {
        if (l === free) {
          if (Math.random() < 0.7) for (let k = 0; k < 4; k++) st.objs.push({ t: "coin", p: st.nextRow + k * 60, l, got: false });
        } else if (Math.random() < 0.45) {
          st.objs.push({ t: Math.random() < 0.5 ? "low" : "tall", p: st.nextRow, l });
        }
      }
      st.nextRow += Math.max(420, 700 - st.speed * 0.6);
    }
  }

  function start() { st = gfresh(); mode = "play"; genRows(); }
  function jump() { if (st.y === 0) st.vy = 620; }
  function action() {
    if (mode === "ready") start();
    else if (mode === "over") { if (performance.now() - overAt > 400) start(); }
    else jump();
  }
  function end() {
    mode = "over"; overAt = performance.now();
    const s = score();
    if (s > best) { best = s; try { localStorage.setItem(KEY, String(best)); } catch (e) {} }
  }

  function update(dt) {
    st.t += dt;
    if (mode !== "play") return;
    st.speed = Math.min(700, st.speed + 8 * dt);
    st.dist += st.speed * dt;
    st.x += (lane - st.x) * Math.min(1, dt * 12);
    if (st.y > 0 || st.vy > 0) {
      st.vy -= 1900 * dt; st.y += st.vy * dt;
      if (st.y <= 0) { st.y = 0; st.vy = 0; }
    }
    genRows();
    for (const o of st.objs) {
      if (o.got) continue;
      const r = hit(o, st);
      if (r === "coin") { o.got = true; st.coins++; }
      else if (r === "hit") { end(); return; }
    }
    st.objs = st.objs.filter((o) => !o.got && o.p > st.dist - 100);
  }

  // ---- drawing ----
  function drawBg() {
    const g = c.createLinearGradient(0, 0, 0, HOR);
    g.addColorStop(0, "#2a1f6b"); g.addColorStop(1, "#8a4fd0");
    c.fillStyle = g; c.fillRect(0, 0, W, HOR);
    c.fillStyle = "#1a1342";
    for (let i = 0; i < 12; i++) {
      const h = 20 + ((i * 37) % 45), x = i * 32 - 10;
      c.fillRect(x, HOR - h, 26, h);
    }
    c.fillStyle = "#16192a"; c.fillRect(0, HOR, W, H - HOR);
    // road
    c.fillStyle = "#262b40";
    c.beginPath();
    c.moveTo(sx(-1.6, 0), HOR); c.lineTo(sx(1.6, 0), HOR);
    c.lineTo(sx(1.6, 1), GY + 60); c.lineTo(sx(-1.6, 1), GY + 60);
    c.closePath(); c.fill();
    c.strokeStyle = "#cfd6ff"; c.lineWidth = 3;
    for (const e of [-1.6, 1.6]) {
      c.beginPath(); c.moveTo(sx(e, 0), HOR); c.lineTo(sx(e, 1.12), GY + 60); c.stroke();
    }
    c.strokeStyle = "rgba(255,255,255,.5)"; c.lineWidth = 2;
    const period = 120, off = st.dist % period;
    for (const e of [-0.5, 0.5]) {
      for (let d = 1600 + period - off; d > -60; d -= period) {
        const d0 = Math.max(0, d), d1 = Math.max(0, d - 50);
        if (d - 50 > 1600) continue;
        const z0 = proj(d0), z1 = proj(d1);
        c.beginPath(); c.moveTo(sx(e, z0), sy(z0)); c.lineTo(sx(e, z1), sy(z1)); c.stroke();
      }
    }
  }

  function drawObj(o) {
    const d = o.p - st.dist;
    if (d < -60 || d > 1600) return;
    const z = proj(Math.max(d, -60)), x = sx(o.l, z), y = sy(z);
    if (o.t === "coin") {
      const w = Math.abs(Math.cos(st.t * 5 + o.p)) * 14 * z + 1.5 * z, r = 14 * z;
      c.fillStyle = "#ffcf3a";
      c.beginPath(); c.ellipse(x, y - 26 * z, w, r, 0, 0, 7); c.fill();
      c.strokeStyle = "#b8860b"; c.lineWidth = 2 * z; c.stroke();
    } else if (o.t === "low") {
      const w = 80 * z, h = 30 * z;
      c.fillStyle = "#ffd21f"; c.fillRect(x - w / 2, y - h, w, h);
      c.fillStyle = "#111";
      for (let i = 0; i < 5; i++) c.fillRect(x - w / 2 + i * w / 5 + w / 10, y - h, w / 10, h);
    } else {
      const w = 74 * z, h = 120 * z;
      c.fillStyle = "#53607d"; c.fillRect(x - w / 2, y - h, w, h);
      c.fillStyle = "#8fa3c9";
      for (let r = 0; r < 4; r++) for (let q = 0; q < 2; q++)
        c.fillRect(x - w / 2 + w * (0.15 + q * 0.45), y - h + h * (0.1 + r * 0.22), w * 0.28, h * 0.12);
    }
  }

  function drawRunner() {
    const x = sx(st.x, 1), y = GY - st.y, run = st.y === 0 && mode === "play" ? Math.sin(st.t * 16) : 0;
    c.fillStyle = "rgba(0,0,0,.35)";
    c.beginPath(); c.ellipse(x, GY + 4, 20 - st.y * 0.08, 6, 0, 0, 7); c.fill();
    c.fillStyle = "#2b2f55"; // legs
    c.fillRect(x - 11, y - 30, 9, 28 + run * 6);
    c.fillRect(x + 2, y - 30, 9, 28 - run * 6);
    c.fillStyle = "#6b3fd0"; c.fillRect(x - 21, y - 78, 12, 34); // backpack
    c.fillStyle = "#ff4fa0"; c.fillRect(x - 14, y - 82, 28, 56); // hoodie
    c.fillStyle = "#f1c9a5"; c.beginPath(); c.arc(x, y - 92, 12, 0, 7); c.fill(); // head
    c.fillStyle = "#14c7c0"; // cap
    c.beginPath(); c.arc(x, y - 95, 12, Math.PI, 0); c.fill();
    c.fillRect(x - 2, y - 97, 18, 5);
  }

  function panel(title, sub) {
    c.fillStyle = "rgba(10,12,22,.78)"; c.fillRect(30, 190, W - 60, 190);
    c.textAlign = "center"; c.fillStyle = "#fff";
    c.font = "800 28px sans-serif"; c.fillText(title, CX, 240);
    c.font = "600 18px sans-serif";
    if (sub) c.fillText(sub, CX, 285);
    c.fillStyle = "#ffb347"; c.font = "600 16px sans-serif";
    c.fillText("Klikni nebo stiskni mezerník", CX, 340);
  }

  function draw() {
    drawBg();
    const near = st.objs.filter((o) => o.p - st.dist >= 0).sort((a, b) => b.p - a.p);
    const past = st.objs.filter((o) => o.p - st.dist < 0);
    near.forEach(drawObj);
    drawRunner();
    past.forEach(drawObj);
    c.textAlign = "left"; c.fillStyle = "#fff"; c.font = "700 16px sans-serif";
    c.fillText("Skóre " + score(), 14, 28);
    c.fillStyle = "#ffcf3a"; c.fillText("Mince " + st.coins, 14, 50);
    c.textAlign = "right"; c.fillStyle = "#fff"; c.fillText("Rekord " + Math.max(best, mode === "over" ? score() : 0), W - 14, 28);
    if (mode === "ready") panel("Geoff Surfers", "");
    else if (mode === "over") panel("Konec hry", "Skóre: " + score());
  }

  function frame(now) {
    requestAnimationFrame(frame);
    if (!open) { last = 0; return; }
    const dt = last ? Math.min(0.05, (now - last) / 1000) : 0;
    last = now;
    ticks++;
    update(dt);
    draw();
  }

  // ---- input ----
  function setLane(e) {
    const r = cv.getBoundingClientRect();
    const f = (e.clientX - r.left) / r.width;
    lane = f < 1 / 3 ? -1 : f > 2 / 3 ? 1 : 0;
  }
  cv.addEventListener("pointermove", setLane);
  cv.addEventListener("pointerenter", () => window.focus());
  cv.addEventListener("pointerdown", (e) => { setLane(e); action(); });
  window.addEventListener("keydown", (e) => {
    if (!open || e.code !== "Space" && e.key !== " ") return;
    const t = e.target && e.target.tagName;
    if (t === "INPUT" || t === "TEXTAREA") return;
    e.preventDefault();
    if (!e.repeat) action();
  });

  root.addEventListener("app-open", () => { open = true; last = 0; draw(); });
  root.addEventListener("app-close", () => { open = false; });
  open = root.classList.contains("open");
  draw();
  requestAnimationFrame(frame);
})();
