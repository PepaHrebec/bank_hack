// Filler apps on the home screen: Tinder and Grindr mock-ups with drawn (fictional)
// profiles, and a Spotify "now playing" screen that plays the official music video
// from YouTube while it is open. None of this talks to the bank.
(function () {
  // ---- drawn portraits (original flat illustrations, no photos) ----

  const HAIR = {
    short: '<path d="M33 54C31 35 41 29 50 29s19 6 17 25c-3-8-9-12-17-12s-14 4-17 12z"/>',
    quiff: '<path d="M33 54C31 35 41 27 52 26c9 0 17 7 15 28-3-8-9-12-17-12s-14 4-17 12z"/><path d="M44 31c4-8 16-9 21-2-6-2-13-1-21 2z"/>',
    buzz: '<path d="M33.5 52C33 37 42 32 50 32s17 5 16.5 20c-3-7-9-10-16.5-10S36.5 45 33.5 52z" opacity=".75"/>',
    curly: '<g><circle cx="38" cy="40" r="7"/><circle cx="46" cy="34" r="7.5"/><circle cx="55" cy="34" r="7.5"/><circle cx="62" cy="40" r="7"/><circle cx="34" cy="48" r="5"/><circle cx="66" cy="48" r="5"/></g>',
    long: '<path d="M30 57C27 31 41 27 50 27s23 4 20 30l3 37c-8 5-38 5-46 0z"/>',
    bob: '<path d="M31 56C29 31 41 27 50 27s21 4 19 29l1 20c-6 4-34 4-40 0z"/>',
    bun: '<circle cx="50" cy="25" r="8"/><path d="M33 54C31 35 41 30 50 30s19 5 17 24c-3-8-9-12-17-12s-14 4-17 12z"/>',
  };
  const FRINGE = '<path d="M33 52c2-14 10-20 17-20s15 6 17 20c-5-9-12-12-17-12-6 0-12 4-17 12z"/>';

  function portrait(p) {
    const id = `g${Math.random().toString(36).slice(2, 8)}`;
    const back = p.hair === "long" || p.hair === "bob";
    const top = p.tank
      ? `<path d="M8 130C10 99 28 90 50 90s40 9 42 40z" fill="${p.skin}"/><path d="M30 130l4-34c5 3 11 4 16 4s11-1 16-4l4 34z" fill="${p.shirt}"/>`
      : `<path d="M8 130C10 99 28 90 50 90s40 9 42 40z" fill="${p.shirt}"/><path d="M42 91l8 9 8-9z" fill="${p.skin}"/>`;
    return `<svg viewBox="0 0 100 130" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${p.bg[0]}"/><stop offset="1" stop-color="${p.bg[1]}"/></linearGradient></defs>
      <rect width="100" height="130" fill="url(#${id})"/>
      ${back ? `<g fill="${p.hairColor}">${HAIR[p.hair]}</g>` : ""}
      ${top}
      <rect x="44" y="70" width="12" height="22" rx="4" fill="${p.skin}"/>
      <rect x="44" y="72" width="12" height="8" fill="#000" opacity=".08"/>
      <ellipse cx="33" cy="58" rx="3.5" ry="5" fill="${p.skin}"/><ellipse cx="67" cy="58" rx="3.5" ry="5" fill="${p.skin}"/>
      <ellipse cx="50" cy="56" rx="17" ry="20.5" fill="${p.skin}"/>
      ${p.beard ? `<path d="M33.5 57c1 17 9 23.5 16.5 23.5S65.5 74 66.5 57c-3 8-9 11-16.5 11S36.5 65 33.5 57z" fill="${p.hairColor}" opacity="${p.beard === "stubble" ? 0.3 : 0.92}"/>` : ""}
      <g fill="${p.hairColor}">${back ? FRINGE : HAIR[p.hair]}</g>
      <path d="M40 49.5q3.5-2 7 0M53 49.5q3.5-2 7 0" stroke="${p.hairColor}" stroke-width="1.6" fill="none" stroke-linecap="round"/>
      ${p.shades
        ? '<g fill="#111"><rect x="38" y="52" width="10.5" height="7" rx="3"/><rect x="51.5" y="52" width="10.5" height="7" rx="3"/><rect x="48" y="54" width="4" height="1.4"/></g>'
        : '<g fill="#2a2a2a"><ellipse cx="43.5" cy="55.5" rx="1.9" ry="2.2"/><ellipse cx="56.5" cy="55.5" rx="1.9" ry="2.2"/></g>'}
      <path d="M50 58v5.5h-2" stroke="#000" stroke-opacity=".25" stroke-width="1.2" fill="none" stroke-linecap="round"/>
      <path d="M44.5 68q5.5 4 11 0" stroke="${p.lips || "#7a3b2e"}" stroke-width="${p.lips ? 2.2 : 1.6}" fill="none" stroke-linecap="round"/>
      ${p.blush ? '<g fill="#ff7b8a" opacity=".25"><circle cx="39" cy="63" r="3.2"/><circle cx="61" cy="63" r="3.2"/></g>' : ""}
      ${p.earrings ? '<g fill="#ffd34d"><circle cx="33" cy="64.5" r="1.8"/><circle cx="67" cy="64.5" r="1.8"/></g>' : ""}
    </svg>`;
  }

  const SKIN = ["#f6d1b5", "#e9b893", "#d49a6a", "#a86b45", "#7a4a2e", "#f1c6a4"];

  // ---- Tinder ----

  const GIRLS = [
    { name: "Klára", age: 24, km: 2, bio: "Coffee, climbing and terrible puns ☕🧗‍♀️", p: { skin: SKIN[0], hair: "long", hairColor: "#6b3e1f", shirt: "#ff6f91", bg: ["#ffd3e0", "#ff9a8b"], lips: "#d9475f", blush: true, earrings: true } },
    { name: "Tereza", age: 26, km: 5, bio: "Looking for someone to split the bill with 💸", p: { skin: SKIN[1], hair: "bob", hairColor: "#1f1a17", shirt: "#3d5afe", bg: ["#c3d0ff", "#8e7dff"], lips: "#b8325a", shades: true } },
    { name: "Natálie", age: 23, km: 1, bio: "Dog mum 🐕 Will judge your playlist", p: { skin: SKIN[3], hair: "curly", hairColor: "#2b1a12", shirt: "#ffb300", bg: ["#ffe9a8", "#ffb36b"], lips: "#a3324a", earrings: true } },
    { name: "Eliška", age: 27, km: 8, bio: "Data scientist by day, salsa by night 💃", p: { skin: SKIN[5], hair: "bun", hairColor: "#c8812f", shirt: "#26a69a", bg: ["#c7f5e8", "#7fd6c2"], lips: "#cf4a5a", blush: true } },
    { name: "Bára", age: 25, km: 3, bio: "Swipe right if you know a good svíčková", p: { skin: SKIN[2], hair: "long", hairColor: "#e6c36a", shirt: "#7e57c2", bg: ["#e3d4ff", "#b69cff"], lips: "#d64a6b", earrings: true } },
    { name: "Adéla", age: 22, km: 4, bio: "Festival season is a lifestyle 🎶", p: { skin: SKIN[4], hair: "bob", hairColor: "#111", shirt: "#ef5350", bg: ["#ffd0c8", "#ff8a80"], lips: "#8e2440", shades: true } },
  ];

  function buildTinder(root) {
    root.innerHTML = `
      <header class="tin-top"><span class="tin-logo">discover</span></header>
      <div class="tin-stack"></div>
      <div class="tin-actions">
        <button type="button" class="tin-btn nope" aria-label="Nope">✕</button>
        <button type="button" class="tin-btn star" aria-label="Super like">★</button>
        <button type="button" class="tin-btn like" aria-label="Like">♥</button>
      </div>`;
    const stack = root.querySelector(".tin-stack");
    let i = 0;

    function card(girl) {
      const c = document.createElement("div");
      c.className = "tin-card";
      c.innerHTML = portrait(girl.p);
      const info = document.createElement("div");
      info.className = "tin-info";
      const h = document.createElement("div");
      h.className = "tin-name";
      h.innerHTML = `${girl.name} <span>${girl.age}</span>`;
      const km = document.createElement("div");
      km.className = "tin-km";
      km.textContent = `${girl.km} km away`;
      const bio = document.createElement("div");
      bio.className = "tin-bio";
      bio.textContent = girl.bio;
      info.append(h, km, bio);
      c.append(info);
      return c;
    }

    function render() {
      stack.replaceChildren(card(GIRLS[(i + 1) % GIRLS.length]), card(GIRLS[i % GIRLS.length]));
    }

    function swipe(dir) {
      const topCard = stack.lastElementChild;
      if (!topCard || topCard.classList.contains("gone")) return;
      topCard.classList.add("gone", dir);
      setTimeout(() => { i += 1; render(); }, 320);
    }

    root.querySelector(".nope").addEventListener("click", () => swipe("left"));
    root.querySelector(".like").addEventListener("click", () => swipe("right"));
    root.querySelector(".star").addEventListener("click", () => swipe("up"));
    render();
  }

  // ---- Grindr ----

  const GUYS = [
    { name: "Tomáš", m: 80, on: true, p: { skin: SKIN[1], hair: "quiff", hairColor: "#3b2416", beard: "stubble", shirt: "#212121", tank: true, bg: ["#3a3a3a", "#151515"] } },
    { name: "Gym rat 💪", m: 150, on: true, p: { skin: SKIN[2], hair: "buzz", hairColor: "#1a1a1a", beard: "full", shirt: "#d32f2f", tank: true, bg: ["#4a2a2a", "#1a0f0f"] } },
    { name: "Kuba", m: 220, on: false, p: { skin: SKIN[0], hair: "short", hairColor: "#d9a441", shirt: "#1e88e5", bg: ["#29435c", "#101a24"], shades: true } },
    { name: "Matěj", m: 300, on: true, p: { skin: SKIN[4], hair: "curly", hairColor: "#111", beard: "full", shirt: "#fbc02d", tank: true, bg: ["#4d4220", "#1a160a"] } },
    { name: "Ondra 🏳️‍🌈", m: 410, on: true, p: { skin: SKIN[5], hair: "quiff", hairColor: "#6d4c2f", shirt: "#8e24aa", bg: ["#3d2447", "#140b18"] } },
    { name: "Filip", m: 520, on: false, p: { skin: SKIN[3], hair: "short", hairColor: "#1b1b1b", beard: "stubble", shirt: "#00897b", tank: true, bg: ["#1f3d39", "#0b1614"] } },
    { name: "Adam", m: 640, on: true, p: { skin: SKIN[1], hair: "buzz", hairColor: "#5a3a22", beard: "full", shirt: "#424242", bg: ["#353535", "#121212"], shades: true } },
    { name: "Lukáš", m: 780, on: false, p: { skin: SKIN[0], hair: "curly", hairColor: "#a0522d", shirt: "#e64a19", tank: true, bg: ["#4a2b1f", "#170d09"] } },
    { name: "Dan", m: 900, on: true, p: { skin: SKIN[2], hair: "quiff", hairColor: "#222", beard: "stubble", shirt: "#3949ab", bg: ["#262c4d", "#0c0e1a"] } },
    { name: "Vojta", m: 1100, on: true, p: { skin: SKIN[3], hair: "short", hairColor: "#111", shirt: "#43a047", tank: true, bg: ["#23402a", "#0b150e"] } },
    { name: "Marek", m: 1300, on: false, p: { skin: SKIN[5], hair: "buzz", hairColor: "#8d6e63", beard: "full", shirt: "#6d4c41", bg: ["#3e2c26", "#140e0c"] } },
    { name: "Honza", m: 1500, on: true, p: { skin: SKIN[1], hair: "quiff", hairColor: "#f0c060", shirt: "#00acc1", tank: true, bg: ["#1d3f45", "#0a1517"], shades: true } },
  ];

  function buildGrindr(root) {
    root.innerHTML = `
      <header class="gr-top">
        <span class="gr-title">Nearby</span>
        <div class="gr-filters"><span class="on">Online</span><span>Age</span><span>Fresh</span><span>Tags</span></div>
      </header>
      <div class="gr-grid"></div>`;
    const grid = root.querySelector(".gr-grid");
    for (const g of GUYS) {
      const tile = document.createElement("div");
      tile.className = "gr-tile";
      tile.innerHTML = portrait(g.p);
      const label = document.createElement("div");
      label.className = "gr-label";
      const name = document.createElement("span");
      name.textContent = g.name;
      if (g.on) {
        const dot = document.createElement("i");
        dot.className = "gr-dot";
        label.append(dot);
      }
      const dist = document.createElement("small");
      dist.textContent = g.m < 1000 ? `${g.m} m` : `${(g.m / 1000).toFixed(1)} km`;
      label.append(name, dist);
      tile.append(label);
      grid.append(tile);
    }
  }

  // ---- Spotify ----

  // Official music video, embedded from YouTube (needs internet). Loaded on open, unloaded on close.
  const VIDEO = "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&playsinline=1&rel=0";

  function buildSpotify(root) {
    root.innerHTML = `
      <header class="sp-top"><span>PLAYING FROM SEARCH</span><b>Rick Astley</b></header>
      <div class="sp-art"></div>
      <div class="sp-meta"><div><div class="sp-song">Never Gonna Give You Up</div><div class="sp-artist">Rick Astley</div></div><span class="sp-heart">♥</span></div>
      <div class="sp-bar"><i></i></div>
      <div class="sp-times"><span>0:42</span><span>3:33</span></div>
      <div class="sp-controls"><span>⇄</span><span>⏮</span><span class="sp-play">❚❚</span><span>⏭</span><span>↻</span></div>`;
    const art = root.querySelector(".sp-art");
    root.addEventListener("app-open", () => {
      const frame = document.createElement("iframe");
      frame.src = VIDEO;
      frame.title = "Never Gonna Give You Up";
      frame.allow = "autoplay; encrypted-media; picture-in-picture";
      art.replaceChildren(frame);
    });
    root.addEventListener("app-close", () => art.replaceChildren());
  }

  buildTinder(document.getElementById("tinder"));
  buildGrindr(document.getElementById("grindr"));
  buildSpotify(document.getElementById("spotify"));
})();
