// Klipy: vertical feed of 13 short clips (canvas scenes plus one real recording). Self-contained; talks to the shell via window.Phone.
(function () {
  const root = document.getElementById("reels");
  if (!root) return;

  const W = 360, H = 736, GY = 560;
  const KEY = "klipy";
  const ORD = [12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
  const REDUCED = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  // id -> clip. Ids are stable (saved state is keyed by them); the display order is ORD.
  const CLIPS = [
    { t: "Večerní tramvaj", h: "tereza.mesto", av: ["d0", "T"], c: ["#1b1f4b", "#7a3b8f", "#ff7ab6"], l: 12400, cap: "Poslední spoj domů, město svítí.", com: ["Která linka?", "Tuhle trasu miluju."] },
    { t: "Káva v sedm ráno", h: "josef.kava", av: ["d3", "J"], c: ["#3a2412", "#a8642a", "#ffc27a"], l: 8300, cap: "Bez kávy se nedá začít.", com: ["Jaká pražírna?", "Dnes už druhá."] },
    { t: "Skatepark o půlnoci", h: "stepan_skate", av: ["d2", "Š"], c: ["#0e3b43", "#1fb3a8", "#c9ff7a"], l: 20100, cap: "Nový trik konečně sedl.", com: ["Ten dopad!", "Naučíš mě to?"] },
    { t: "Pivo po práci", h: "jiri.bezi", av: ["d1", "J"], c: ["#3b2a07", "#d6951a", "#fff0a8"], l: 5600, cap: "Útrata se rozúčtuje v bance.", com: ["Kdo platí první?", "Zítra opakovat."] },
    { t: "Zkouška kapely", h: "kapela.hluk", av: ["d0", "K"], c: ["#2a0b3b", "#e0457b", "#6a4cff"], l: 31000, cap: "Nová písnička je skoro hotová.", com: ["Kdy koncert?", "Pecka."] },
    { t: "Noční běh", h: "nocni.bezec", av: ["d1", "N"], c: ["#07152b", "#3b6cff", "#7af0ff"], l: 9800, cap: "Deset kilometrů za světla čelovky.", com: ["Jaké tempo?", "Respekt."] },
    { t: "Nedívej se do spirály", h: "spirala.cz", av: ["d1", "S"], c: ["#12002b", "#4b0f6b", "#ff4dd2"], l: 1482000, cap: "Ještě jedno scrollnutí a jdu spát.", com: ["jdu spát za 5 minut (je 4:12)", "proč se na to dívám", "už se mi to točí v hlavě"] },
    { t: "Počkej, až trefí roh", h: "dvd.cekatel", av: ["d2", "D"], c: ["#06232b", "#0b5c63", "#7af0ff"], l: 964000, cap: "Čekám už třetí hodinu.", com: ["SKORO!!", "dívám se 40 minut", "nikdy to netrefí"] },
    { t: "POV: banán tančí ve 3 ráno", h: "banan.ve.3.rano", av: ["d3", "B"], c: ["#2b0d3d", "#ff7a18", "#ffe135"], l: 2310000, cap: "Banán ví něco, co ty nevíš.", com: ["proč to sleduju", "dej mu víc ovoce", "tohle mi změnilo život"] },
    { t: "Oči. Všude. Oči.", h: "oci.vsude", av: ["d0", "O"], c: ["#0f0f0f", "#3a2f7a", "#ff4d6d"], l: 733000, cap: "Koukají. Koukají na tebe.", com: ["ten vlevo nahoře mrkl", "já se jim dívám zpátky", "nemrkej"] },
    { t: "brain.exe neodpovídá", h: "mozek.exe", av: ["d1", "M"], c: ["#14052a", "#7a1f5c", "#7af0ff"], l: 1190000, cap: "Mozek se zasekl na 99 procentech.", com: ["mám to taky", "restartovat? ne, ještě chvíli", "zmrzlo mi to v hlavě"] },
    { t: "Dnes určitě vyhraju", h: "slot.stesti", av: ["d2", "S"], c: ["#2b0a0a", "#7a1fe0", "#ffe135"], l: 508000, cap: "Zase skoro. Příště to vyjde.", com: ["SKORO", "ještě jedno kolo", "tohle není hazard, jen koukám"] },
    { t: "Automat a Běžec", h: "tunelovy.bezec", av: ["d1", "T"], c: ["#12002b", "#4b0f6b", "#ffb020"], l: 48200, cap: "Nahoře automat, dole záznam z Geoff Surfers (hraje autopilot).", com: ["Hrál to člověk?", "Ten skok přes bariéru!"], vid: "/static/media/klipy-runner.webm" },
  ];

  // ---- state: {liked:{id:true}, follow:{id:true}, com:{id:[text]}} ----
  const S = { liked: {}, follow: {}, com: {} };
  try {
    const r = JSON.parse(localStorage.getItem(KEY));
    if (r && typeof r === "object") for (const k in S) if (r[k] && typeof r[k] === "object") S[k] = r[k];
  } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }
  const own = (id) => (Array.isArray(S.com[id]) ? S.com[id] : []);

  // ---- DOM ----
  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  const HEART = '<svg viewBox="0 0 24 24"><path d="M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z"/></svg>';
  const BUBBLE = '<svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/></svg>';

  const head = el("div", "kl-head");
  head.append(el("h2", "", "Klipy"));
  const home = el("button", "kl-home", "Domů");
  home.type = "button";
  head.append(home);
  const feed = el("div", "kl-feed");
  feed.id = "rfeed";
  root.append(head, feed);
  home.addEventListener("click", () => { if (window.Phone) window.Phone.openApp(null); });

  function action(cls, svg) {
    const b = el("button", "act " + cls);
    b.type = "button";
    b.innerHTML = svg;
    b.append(el("span", "n"));
    return b;
  }


  const fmt = (n) => n.toLocaleString("cs-CZ");
  const clipEl = (id) => feed.querySelector('.clip[data-i="' + id + '"]');

  const cvs = {}; // id -> {g, clip}
  for (const id of ORD) {
    const d = CLIPS[id];
    const clip = el("section", "clip");
    clip.dataset.i = id;
    clip.style.setProperty("--a", d.c[0]);
    clip.style.setProperty("--b", d.c[1]);
    const cv = el("canvas", "cv");
    cv.width = W; cv.height = H;
    clip.append(cv);
    if (d.vid) {
      const v = el("video", "vid");
      v.muted = true; v.loop = true; v.playsInline = true; v.preload = "auto";
      v.setAttribute("muted", ""); v.setAttribute("loop", ""); v.setAttribute("playsinline", "");
      v.src = d.vid;
      clip.append(v);
    }
    clip.append(el("h2", "ttl", d.t));
    const side = el("div", "side");
    const like = action("like", HEART), cm = action("cmt", BUBBLE);
    side.append(like, cm);
    clip.append(side);
    const by = el("div", "by");
    const av = el("div", "av " + d.av[0], d.av[1]);
    const fol = el("button", "fol");
    fol.type = "button";
    by.append(av, el("span", "hd", "@" + d.h), fol, el("p", "cap", d.cap));
    clip.append(by);
    const pg = el("div", "pg");
    pg.append(el("i"));
    clip.append(pg);
    feed.append(clip);
    cvs[id] = cv.getContext("2d");

    like.addEventListener("click", () => setLike(id, !S.liked[id]));
    cm.addEventListener("click", () => openSheet(id));
    fol.addEventListener("click", () => {
      if (S.follow[id]) delete S.follow[id]; else S.follow[id] = true;
      save(); refresh(id);
    });
    clip.addEventListener("dblclick", (e) => {
      if (e.target.closest("button")) return;
      if (!S.liked[id]) setLike(id, true);
      const b = el("div", "burst");
      b.innerHTML = HEART;
      clip.append(b);
      setTimeout(() => b.remove(), 700);
    });
    refresh(id);
  }

  // Counts, pressed state and follow label of one clip, looked up by id (never by position).
  function refresh(id) {
    const c = clipEl(id), d = CLIPS[id];
    const like = c.querySelector(".like"), fol = c.querySelector(".fol");
    like.setAttribute("aria-pressed", S.liked[id] ? "true" : "false");
    like.querySelector(".n").textContent = fmt(d.l + (S.liked[id] ? 1 : 0));
    c.querySelector(".cmt .n").textContent = fmt(d.com.length + own(id).length);
    fol.setAttribute("aria-pressed", S.follow[id] ? "true" : "false");
    fol.textContent = S.follow[id] ? "Sleduješ" : "Sledovat";
  }

  function setLike(id, on) {
    if (on) S.liked[id] = true; else delete S.liked[id];
    save(); refresh(id);
  }

  // ---- comments sheet ----
  const sheet = el("div", "kl-sheet");
  sheet.id = "rsheet";
  sheet.hidden = true;
  const sh = el("div", "kl-sh");
  const shTitle = el("h3");
  const shX = el("button", "kl-x", "✕");
  shX.type = "button";
  sh.append(shTitle, shX);
  const list = el("ul", "kl-list");
  const add = el("div", "kl-add");
  const input = el("input");
  input.type = "text"; input.maxLength = 120; input.placeholder = "Přidej komentář…";
  input.autocomplete = "off";
  const send = el("button", "", "↵");
  send.type = "button";
  add.append(input, send);
  sheet.append(sh, list, add);
  root.append(sheet);
  let curId = null;

  function renderList() {
    list.textContent = "";
    for (const t of CLIPS[curId].com.concat(own(curId))) list.append(el("li", "", t));
    list.scrollTop = list.scrollHeight;
  }
  function openSheet(id) {
    curId = id;
    shTitle.textContent = "Komentáře · " + CLIPS[id].t;
    renderList();
    sheet.hidden = false;
  }
  function closeSheet() { sheet.hidden = true; curId = null; }
  function submit() {
    const t = input.value.trim();
    if (!t || curId == null) return;
    if (!Array.isArray(S.com[curId])) S.com[curId] = [];
    S.com[curId].push(t.slice(0, 120));
    input.value = "";
    save(); refresh(curId); renderList();
  }
  shX.addEventListener("click", closeSheet);
  send.addEventListener("click", submit);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") submit(); });

  // ---- scenes (time t in seconds, canvas W x H, ground at GY) ----
  const rnd = (i) => { const v = Math.sin(i * 127.1) * 43758.5; return v - Math.floor(v); };
  const wrap = (v, m) => ((v % m) + m) % m;
  function circ(g, x, y, r, col) { g.fillStyle = col; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }
  function stars(g, t) {
    for (let i = 0; i < 40; i++) {
      g.globalAlpha = 0.35 + 0.35 * Math.sin(t * 1.5 + i * 2.3);
      circ(g, rnd(i) * W, rnd(i + 50) * 420, 1 + rnd(i + 99) * 1.6, "#fff");
    }
    g.globalAlpha = 1;
  }
  function cap(g, text, y) {
    g.font = "900 28px system-ui, sans-serif";
    g.textAlign = "center"; g.lineJoin = "round"; g.lineWidth = 7;
    g.strokeStyle = "#000"; g.strokeText(text, 180, y);
    g.fillStyle = "#fff"; g.fillText(text, 180, y);
  }
  function rrect(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }

  const scenes = [
    // 0 tram
    (g, t) => {
      stars(g, t);
      [[20, "#241a45", 220, false], [45, "#1a1235", 300, true]].forEach(([v, col, mh, near]) => {
        for (let i = 0; i < 8; i++) {
          const x = wrap(i * 70 - t * v, 560) - 70, h = 80 + rnd(i + (near ? 10 : 0)) * (mh - 80);
          g.fillStyle = col; g.fillRect(x, GY - h, 62, h);
          if (near) {
            g.fillStyle = "#ffd27a";
            for (let r = 0; r < h / 28 - 1; r++) for (let q = 0; q < 2; q++) if (rnd(i * 31 + r * 7 + q) > 0.45) g.fillRect(x + 10 + q * 28, GY - h + 12 + r * 28, 14, 16);
          }
        }
      });
      g.fillStyle = "#0d0a1f"; g.fillRect(0, GY, W, H - GY);
      g.strokeStyle = "#555"; g.lineWidth = 3; g.beginPath(); g.moveTo(0, 420); g.lineTo(W, 420); g.stroke();
      g.save(); g.translate(180, 520); g.rotate(Math.sin(9 * t) * 0.006);
      g.translate(-180, -520);
      g.fillStyle = "#e0457b"; rrect(g, 70, 470, 220, 80, 10); g.fill();
      g.fillStyle = "#ffe9a8";
      for (let i = 0; i < 5; i++) g.fillRect(82 + i * 41, 485, 30, 26);
      g.strokeStyle = "#ccc"; g.lineWidth = 3;
      g.beginPath(); g.moveTo(180, 470); g.lineTo(195, 421); g.stroke();
      g.restore();
      g.strokeStyle = "#777"; g.lineWidth = 3; g.beginPath(); g.moveTo(0, GY - 2); g.lineTo(W, GY - 2); g.stroke();
      circ(g, 100, 553, 9, "#222"); circ(g, 260, 553, 9, "#222");
    },
    // 1 coffee
    (g, t) => {
      circ(g, 180, 300 + Math.sin(t * 0.5) * 24, 95, "#ffc27a55");
      g.fillStyle = "#e8dfd0"; g.beginPath(); g.ellipse(180, 555, 150, 22, 0, 0, 7); g.fill();
      g.strokeStyle = "#f4efe6"; g.lineWidth = 16; g.beginPath(); g.arc(262, 465, 38, -1.4, 1.6); g.stroke();
      g.fillStyle = "#f4efe6"; rrect(g, 100, 380, 160, 170, [0, 0, 70, 70]); g.fill();
      g.fillStyle = "#4a2a14"; g.beginPath(); g.ellipse(180, 386, 78, 14, 0, 0, 7); g.fill();
      g.lineWidth = 6; g.lineCap = "round";
      for (let i = 0; i < 3; i++) {
        g.strokeStyle = "rgba(255,255,255," + (0.45 + 0.1 * Math.sin(t * 2 + i)) + ")";
        g.beginPath();
        for (let y = 0; y <= 120; y += 8) { const x = 140 + i * 40 + Math.sin(t * 2.2 + y * 0.08 + i) * 12; y ? g.lineTo(x, 360 - y) : g.moveTo(x, 360); }
        g.stroke();
      }
      g.lineCap = "butt";
    },
    // 2 skate
    (g, t) => {
      circ(g, 280, 150, 50, "#f4f1c8");
      g.fillStyle = "#0b2a30"; g.fillRect(0, GY, W, H - GY);
      g.fillStyle = "#1fb3a8";
      for (let i = 0; i < 6; i++) g.fillRect(wrap(i * 70 - t * 160, 420) - 30, GY + 30 + (i % 3) * 22, 36, 4);
      const ph = (t % 2.2) / 2.2, u = ph < 0.6 ? ph / 0.6 : 0, h = 150 * 4 * u * (1 - u), rot = u * Math.PI * 2;
      g.fillStyle = "rgba(0,0,0,.4)"; g.beginPath(); g.ellipse(180, GY + 8, 50 - h * 0.15, 8 - h * 0.03, 0, 0, 7); g.fill();
      const y = GY - 18 - h;
      g.save(); g.translate(180, y); g.rotate(rot);
      g.fillStyle = "#c9ff7a"; rrect(g, -50, -5, 100, 10, 5); g.fill();
      circ(g, -32, 10, 6, "#eee"); circ(g, 32, 10, 6, "#eee");
      g.restore();
      const up = h * 0.2;
      g.fillStyle = "#2b2f55"; g.fillRect(166, y - 70, 12, 66); g.fillRect(184, y - 70, 12, 66);
      g.fillStyle = "#ff4fa0"; g.fillRect(160, y - 140, 42, 72);
      g.strokeStyle = "#ff4fa0"; g.lineWidth = 11; g.lineCap = "round";
      g.beginPath(); g.moveTo(162, y - 130); g.lineTo(125, y - 110 - up * 2); g.moveTo(200, y - 130); g.lineTo(237, y - 110 - up * 2); g.stroke();
      g.lineCap = "butt";
      circ(g, 181, y - 158, 18, "#f1c9a5"); g.fillStyle = "#14c7c0"; g.beginPath(); g.arc(181, y - 162, 18, Math.PI, 0); g.fill();
    },
    // 3 beer
    (g, t) => {
      const f = Math.min(1, (t % 5) / 3), fh = 200 * f;
      const glass = () => { g.beginPath(); g.moveTo(112, 350); g.lineTo(248, 350); g.lineTo(236, 560); g.lineTo(124, 560); g.closePath(); };
      g.strokeStyle = "#fff8"; g.lineWidth = 10; g.beginPath(); g.arc(246, 450, 45, -1.5, 1.5); g.stroke();
      g.save(); glass(); g.clip();
      g.fillStyle = "#f5a623"; g.fillRect(100, 560 - fh, 160, fh);
      if (fh > 10) for (let i = 0; i < 22; i++) {
        const by = 560 - wrap(t * 40 * (0.5 + rnd(i + 30)) + rnd(i + 60) * 200, fh);
        circ(g, 130 + rnd(i) * 100, by, 2 + rnd(i + 9) * 3, "#fff6");
      }
      g.restore();
      for (let i = 0; i < 7; i++) circ(g, 124 + i * 18, 560 - fh - 2 + (i % 2) * 6, 4 + 12 * f, "#fffbe8");
      glass(); g.strokeStyle = "#fff8"; g.lineWidth = 4; g.stroke();
    },
    // 4 band
    (g, t) => {
      for (let i = 0; i < 3; i++) {
        const a = Math.sin(t * 1.2 + i * 2) * 0.35;
        g.save(); g.translate(60 + i * 120, 0); g.rotate(a);
        g.fillStyle = "rgba(255,255,255,.11)";
        g.beginPath(); g.moveTo(-6, 0); g.lineTo(6, 0); g.lineTo(90, 600); g.lineTo(-90, 600); g.closePath(); g.fill();
        g.restore();
      }
      const beat = Math.pow(Math.abs(Math.sin(Math.PI * 2 * t)), 6);
      for (let i = 0; i < 20; i++) {
        const h = 20 + Math.abs(Math.sin(t * 3 + i * 0.9)) * 70 + beat * 20;
        g.fillStyle = i % 2 ? "#e0457b" : "#6a4cff"; g.fillRect(24 + i * 16, 650 - h, 12, h);
      }
      g.fillStyle = "#15131f"; rrect(g, 100, 330, 160, 230, 12); g.fill();
      circ(g, 180, 400, 22, "#333");
      circ(g, 180, 475, 50 + beat * 8, "#222"); circ(g, 180, 475, 30 + beat * 6, "#444"); circ(g, 180, 475, 10, "#111");
    },
    // 5 night run
    (g, t) => {
      stars(g, t);
      g.fillStyle = "#0a1f38"; g.fillRect(0, GY, W, H - GY);
      [[30, "#0b2447", 90], [80, "#0d2d57", 130]].forEach(([v, col, s], k) => {
        for (let i = 0; i < 5; i++) {
          const x = wrap(i * 110 - t * v, 550) - 100;
          g.fillStyle = col; g.beginPath(); g.moveTo(x, GY); g.lineTo(x + s * 0.4, GY - s * 1.6); g.lineTo(x + s * 0.8, GY); g.closePath(); g.fill();
        }
      });
      g.fillStyle = "#3b6cff55";
      for (let i = 0; i < 6; i++) g.fillRect(wrap(i * 80 - t * 220, 480) - 40, GY + 40 + (i % 2) * 30, 40, 4);
      const x = 120, y = GY, sw = Math.sin(t * 10);
      const lg = g.createLinearGradient(x + 10, 0, W, 0);
      lg.addColorStop(0, "rgba(122,240,255,.6)"); lg.addColorStop(1, "rgba(122,240,255,0)");
      g.fillStyle = lg; g.beginPath(); g.moveTo(x + 14, y - 112); g.lineTo(W, y - 190); g.lineTo(W, y - 20); g.closePath(); g.fill();
      g.strokeStyle = "#2b2f55"; g.lineWidth = 11; g.lineCap = "round";
      g.beginPath(); g.moveTo(x - 4, y - 55); g.lineTo(x - 4 + sw * 22, y - 4); g.moveTo(x + 6, y - 55); g.lineTo(x + 6 - sw * 22, y - 4); g.stroke();
      g.strokeStyle = "#ff4fa0"; g.lineWidth = 9;
      g.beginPath(); g.moveTo(x, y - 95); g.lineTo(x - sw * 24 + 6, y - 68); g.moveTo(x, y - 95); g.lineTo(x + sw * 24 + 6, y - 68); g.stroke();
      g.lineCap = "butt";
      g.fillStyle = "#ff4fa0"; g.fillRect(x - 14, y - 110, 28, 58);
      circ(g, x, y - 126, 13, "#f1c9a5"); circ(g, x + 11, y - 128, 4, "#fff");
    },
    // 6 spiral
    (g, t) => {
      for (let i = 0; i < 64; i++) {
        const a = i * 0.34 + 3 * t, r = i * 2.8;
        circ(g, 180 + Math.cos(a) * r, 330 + Math.sin(a) * r, 3 + i * 0.17, "hsl(" + ((i * 7 + 50 * t) % 360) + ",90%,60%)");
      }
      cap(g, ["SCROLUJ DÁL", "NEDÍVEJ SE", "JEŠTĚ JEDEN", "ZA 5 MIN SPÁT"][Math.floor(t / 1.3) % 4], 590);
    },
    // 7 bouncing box
    (g, t) => {
      const X0 = 14, Y0 = 164, FW = 332, FH = 370, bw = 110, bh = 64;
      const fold = (d, R) => { const p = wrap(d, 2 * R); return p > R ? 2 * R - p : p; };
      const at = (tt) => [X0 + fold(95 * tt, FW - bw), Y0 + fold(80 * tt, FH - bh)];
      g.strokeStyle = "#7af0ff"; g.lineWidth = 3; g.strokeRect(X0, Y0, FW, FH);
      const hue = (tt) => (Math.floor(95 * tt / (FW - bw)) + Math.floor(80 * tt / (FH - bh))) * 55 % 360;
      for (let k = 6; k >= 0; k--) {
        const tt = Math.max(0, t - k * 0.07), [x, y] = at(tt);
        g.globalAlpha = k ? 0.13 : 1;
        g.fillStyle = "hsl(" + hue(tt) + ",85%,58%)"; rrect(g, x, y, bw, bh, 12); g.fill();
        if (!k) { g.fillStyle = "#fff"; g.font = "900 26px system-ui, sans-serif"; g.textAlign = "center"; g.fillText("KLIP", x + bw / 2, y + 41); }
      }
      g.globalAlpha = 1;
      cap(g, ["ČEKÁM NA ROH", "JEŠTĚ KOUSEK", "SKORO... NE."][Math.floor(t / 1.3) % 3], 590);
    },
    // 8 banana
    (g, t) => {
      for (let i = 0; i < 12; i++) {
        const a = t * 0.15 + i * Math.PI / 6;
        g.fillStyle = i % 2 ? "#ff7a1833" : "#ffe13522";
        g.beginPath(); g.moveTo(180, 330); g.arc(180, 330, 700, a, a + Math.PI / 12); g.closePath(); g.fill();
      }
      const sw = Math.sin(6 * t);
      g.save(); g.translate(180, 520); g.rotate(sw * 0.07); g.translate(-180, -520);
      g.strokeStyle = "#8a5a00"; g.lineWidth = 10; g.lineCap = "round";
      g.beginPath(); g.moveTo(150, 505); g.lineTo(140 + sw * 12, 555); g.moveTo(205, 505); g.lineTo(215 - sw * 12, 555);
      g.moveTo(120, 380); g.lineTo(80, 340 + sw * 30); g.moveTo(240, 380); g.lineTo(285, 340 - sw * 30); g.stroke();
      g.lineCap = "butt";
      g.fillStyle = "#ffe135"; g.strokeStyle = "#c79a00"; g.lineWidth = 4;
      g.beginPath(); g.moveTo(150, 180);
      g.bezierCurveTo(95, 280, 95, 440, 170, 515);
      g.bezierCurveTo(215, 530, 255, 500, 262, 470);
      g.bezierCurveTo(205, 450, 190, 330, 214, 190);
      g.closePath(); g.fill(); g.stroke();
      g.fillStyle = "#7a4b00"; g.fillRect(148, 160, 64, 28);
      const ex = Math.cos(t * 2) * 4, ey = Math.sin(t * 2) * 3;
      circ(g, 160, 330, 15, "#fff"); circ(g, 200, 328, 15, "#fff");
      circ(g, 160 + ex, 330 + ey, 6, "#111"); circ(g, 200 + ex, 328 + ey, 6, "#111");
      g.strokeStyle = "#7a3b00"; g.lineWidth = 4; g.beginPath(); g.arc(182, 375, 18, 0.1, Math.PI - 0.1); g.stroke();
      g.restore();
      cap(g, ["POV: 3 RÁNO", "BANÁN TANČÍ", "PROČ TO SLEDUJU"][Math.floor(t / 1.3) % 3], 590);
    },
    // 9 eyes
    (g, t) => {
      const dx = 180 + 130 * Math.cos(t * 0.8), dy = 330 + 170 * Math.sin(t * 0.8);
      for (let i = 0; i < 16; i++) {
        const x = 40 + rnd(i) * 280, y = 140 + rnd(i + 20) * 400, r = 18 + rnd(i + 40) * 28;
        const blink = ((t * 0.5 + rnd(i + 70) * 10) % 4) < 0.12;
        const a = Math.atan2(dy - y, dx - x), d = Math.min(r * 0.4, Math.hypot(dx - x, dy - y) / 8);
        g.fillStyle = "#f4f4f4"; g.beginPath(); g.ellipse(x, y, r * 1.25, blink ? r * 0.1 : r, 0, 0, 7); g.fill();
        if (!blink) { circ(g, x + Math.cos(a) * d, y + Math.sin(a) * d, r * 0.5, "#3a2f7a"); circ(g, x + Math.cos(a) * d, y + Math.sin(a) * d, r * 0.22, "#000"); }
      }
      circ(g, dx, dy, 7, "#ff4d6d");
      cap(g, ["OČI VŠUDE", "KOUKAJÍ NA TEBE", "NEMRKEJ"][Math.floor(t / 1.3) % 3], 590);
    },
    // 10 brain
    (g, t) => {
      const sd = Math.floor(t * 2.5);
      g.strokeStyle = "#ffe135"; g.lineWidth = 4; g.lineJoin = "round";
      for (let k = 0; k < 2; k++) {
        g.beginPath(); let x = 70 + rnd(sd * 3 + k) * 220;
        g.moveTo(x, 60);
        for (let y = 100; y <= 210; y += 40) { x += (rnd(sd * 7 + k * 5 + y) - 0.5) * 70; g.lineTo(x, y); }
        g.stroke();
      }
      const p = 1 + 0.03 * Math.sin(6 * t);
      g.save(); g.translate(180, 310); g.scale(p, p);
      g.fillStyle = "#ff8fb8"; g.strokeStyle = "#c9477f"; g.lineWidth = 4;
      for (const dx of [-42, 42]) { g.beginPath(); g.ellipse(dx, 0, 82, 100, 0, 0, 7); g.fill(); g.stroke(); }
      g.lineWidth = 3; g.beginPath();
      g.moveTo(0, -95); g.lineTo(0, 95);
      for (const dx of [-70, -25, 25, 70]) { g.moveTo(dx - 28, -30); g.quadraticCurveTo(dx, -55, dx + 28, -30); g.moveTo(dx - 28, 35); g.quadraticCurveTo(dx, 60, dx + 28, 35); }
      g.stroke(); g.restore();
      const pr = Math.min(0.99, (t % 6) / 3.5);
      g.fillStyle = "#fff3"; rrect(g, 50, 470, 260, 24, 12); g.fill();
      g.fillStyle = "#7af0ff"; rrect(g, 50, 470, Math.max(24, 260 * pr), 24, 12); g.fill();
      cap(g, ["BRAIN.EXE NEODPOVÍDÁ", "99 % – ČEKEJ", "NEZAVÍREJ"][Math.floor(t / 1.3) % 3], 550);
    },
    // 11 slot machine
    (g, t) => {
      const SYM = ["★", "♥", "♦", "♣", "7", "$"], tc = t % 6, cyc = Math.floor(t / 6), win = cyc % 3 === 2;
      const stops = [1.8, 2.6, 3.4];
      g.save(); g.translate(Math.sin(3 * t) * 4, 0);
      g.fillStyle = "#b01030"; rrect(g, 30, 200, 300, 230, 22); g.fill();
      g.fillStyle = "#ffe135"; g.fillRect(150, 210, 60, 10);
      g.fillStyle = "#7a0a20"; rrect(g, 330, 250, 12, 90, 6); g.fill(); circ(g, 336, 246, 14, "#ffe135");
      const done = tc >= stops[2];
      g.textAlign = "center"; g.font = "800 56px system-ui, sans-serif"; g.textBaseline = "middle";
      for (let i = 0; i < 3; i++) {
        const x = 42 + i * 100;
        g.fillStyle = "#fff"; rrect(g, x, 250, 84, 130, 10); g.fill();
        g.save(); rrect(g, x, 250, 84, 130, 10); g.clip();
        const sym = win ? (cyc + 1) % 6 : (cyc * 2 + i * 2 + 1) % 6;
        if (tc >= stops[i]) {
          g.fillStyle = sym % 2 ? "#d01030" : "#222"; g.fillText(SYM[sym], x + 42, 318);
        } else {
          const q = tc * 14 + i * 3, fr = q - Math.floor(q);
          for (let k = -1; k <= 1; k++) {
            g.fillStyle = "#555"; g.fillText(SYM[wrap(Math.floor(q) + k, 6)], x + 42, 318 + (fr + k) * 60);
          }
        }
        g.restore();
      }
      g.textBaseline = "alphabetic";
      if (done && win) { g.strokeStyle = "#ffe135"; g.lineWidth = 6; rrect(g, 36, 244, 288, 142, 14); g.stroke(); }
      g.restore();
      cap(g, !done ? "DNES VYHRAJU" : win ? "JACKPOT!!!" : "SKORO!", 520);
    },
  ];

  function drawScene(id, g, t) {
    g.clearRect(0, 0, W, H);
    g.save();
    g.textBaseline = "alphabetic"; g.lineCap = "butt"; g.lineJoin = "miter"; g.globalAlpha = 1;
    if (id === 12) {
      // split clip: the slot machine small in the top half; the recording (a <video>) covers the bottom half
      g.fillStyle = "#fff9"; g.font = "700 16px system-ui, sans-serif"; g.textAlign = "center";
      g.fillText("Záznam se nenačetl", 180, H * 0.75);
      g.translate(68, 20); g.scale(0.62, 0.62);
      scenes[11](g, t);
    } else scenes[id](g, t);
    g.restore();
  }

  // ---- loop: runs only while the window is open, draws only the .on clip ----
  let open = false, raf = 0, t0 = 0, onId = null;

  function syncVideo() {
    const v = feed.querySelector("video");
    if (!v) return;
    const want = open && onId === 12 && !REDUCED;
    if (want && v.paused) {
      if (!v.dataset.run) { v.currentTime = 0; v.dataset.run = "1"; }
      const p = v.play(); if (p && p.catch) p.catch(() => {});
    } else if (!want) {
      if (!v.paused) v.pause();
      delete v.dataset.run;
    }
  }

  function frame(now) {
    raf = requestAnimationFrame(frame);
    if (onId == null) return;
    if (!t0) t0 = now;
    drawScene(onId, cvs[onId], (now - t0) / 1000);
    syncVideo();
  }
  function startLoop() { if (!raf && !REDUCED) { t0 = 0; raf = requestAnimationFrame(frame); } }
  function stopLoop() { cancelAnimationFrame(raf); raf = 0; }

  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      const id = +e.target.dataset.i;
      if (e.isIntersecting) {
        feed.querySelectorAll(".clip.on").forEach((c) => { if (c !== e.target) c.classList.remove("on"); });
        e.target.classList.add("on");
        onId = id;
        if (REDUCED) drawScene(id, cvs[id], 0); // still frame instead of animation
      } else {
        e.target.classList.remove("on");
        if (onId === id) onId = null;
      }
    }
    syncVideo();
  }, { root: feed, threshold: 0.6 });
  feed.querySelectorAll(".clip").forEach((c) => io.observe(c));

  window.addEventListener("keydown", (e) => {
    if (!open || (e.key !== "ArrowDown" && e.key !== "ArrowUp")) return;
    const t = e.target && e.target.tagName;
    if (t === "INPUT" || t === "TEXTAREA") return;
    e.preventDefault();
    feed.scrollBy({ top: (e.key === "ArrowDown" ? 1 : -1) * feed.clientHeight, behavior: REDUCED ? "auto" : "smooth" });
  });

  root.addEventListener("app-open", () => { open = true; startLoop(); syncVideo(); });
  root.addEventListener("app-close", () => { open = false; stopLoop(); closeSheet(); syncVideo(); });
  open = root.classList.contains("open");
  if (open) startLoop();
})();
