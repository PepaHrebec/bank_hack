// Filler apps on the home screen: a Spotify "now playing" screen that plays the official
// music video from YouTube while it is open. None of this talks to the bank.
(function () {
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

  buildSpotify(document.getElementById("spotify"));
})();
