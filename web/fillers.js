// Filler apps on the home screen: a Spotify "now playing" screen that plays the music video
// (a local file) while it is open. None of this talks to the bank.
(function () {
  // ---- Spotify ----

  // Served from web/media, so it plays offline. Starts on open, stops and rewinds on close.
  const VIDEO = "/static/media/never-gonna-give-you-up.mp4";

  function buildSpotify(root) {
    root.innerHTML = `
      <header class="sp-top"><span>PLAYING FROM SEARCH</span><b>Rick Astley</b></header>
      <div class="sp-art"></div>
      <div class="sp-meta"><div><div class="sp-song">Never Gonna Give You Up</div><div class="sp-artist">Rick Astley</div></div><span class="sp-heart">♥</span></div>
      <div class="sp-bar"><i></i></div>
      <div class="sp-times"><span>0:42</span><span>3:33</span></div>
      <div class="sp-controls"><span>⇄</span><span>⏮</span><span class="sp-play">❚❚</span><span>⏭</span><span>↻</span></div>`;
    const video = document.createElement("video");
    Object.assign(video, { src: VIDEO, loop: true, playsInline: true, preload: "auto" });
    root.querySelector(".sp-art").append(video);
    root.addEventListener("app-open", () => {
      // Opening the app is a tap, so the browser lets it play with sound; fall back to muted.
      video.play().catch(() => { video.muted = true; video.play().catch(() => {}); });
    });
    root.addEventListener("app-close", () => { video.pause(); video.currentTime = 0; });
  }

  buildSpotify(document.getElementById("spotify"));
})();
