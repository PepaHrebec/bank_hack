Do jednostránkové HTML aplikace, která simuluje telefon (rámeček s domovskou obrazovkou a aplikacemi, které se vysouvají přes celý displej), přidej aplikaci **Klipy**: svislý feed 13 krátkých „reelů“ s animacemi nakreslenými v canvasu, jedním skutečným videozáznamem, lajky, sledováním a komentáři.

Všechny postavy a motivy jsou originální. Použij vlastní název „Klipy“ a vlastní ikonu. Nepoužívej název, logo ani vzhled existující sociální sítě a nekresli žádné cizí postavy ani meme postavy.

## Předpoklady o okolní aplikaci
- Telefon má obrazovky `<section class="screen" id="...">` s třídou `.open` pro zobrazení (vysouvají se zespodu: `transform:translateY(100%)` → `none`, `visibility:hidden` → `visible`). Ikony na domovské obrazovce mají atribut `data-<app>`, tlačítka „Domů“ a lišta dole mají `data-close`.
- Skript má pomocné funkce `$ = id => document.getElementById(id)`, `esc()` pro bezpečný text, `save()` pro uložení stavu `S` do `localStorage` (vždy v `try/catch`) a stav `S.reels = {liked:{}, follow:{}, com:{}}` (při načtení se doplní, pokud chybí).
- Pokud takové rozhraní neexistuje, vytvoř minimální.
- Do stránky patří pravidlo `[hidden]{display:none!important}`, aby vlastní pravidla `display` nepřebila atribut `hidden`.

## Integrace do telefonu
- **Ikona** „Klipy“ na ploše: čtvercová, přechod fialová → růžová (`#6a4cff` → `#e0457b`), písmeno „K“. Klepnutí přidá obrazovce `#reels` třídu `.open`.
- Obrazovka `#reels`: černé pozadí, bílý text, žádné vnitřní odsazení, `overflow:hidden`. Stavový řádek telefonu je při otevřené obrazovce bílý (`.phone:has(#reels.open) .status{color:#fff}`).
- Nahoře přes feed (`position:absolute; top:42px; z-index:3`) je titulek „Klipy“ vlevo a bílé tlačítko „Domů“ (`data-close`) vpravo.
- Feed `#rfeed`: výška 100 %, `overflow-y:auto`, `scroll-snap-type:y mandatory`, bez viditelné posuvné lišty. Každý klip má výšku feedu, `scroll-snap-align:start; scroll-snap-stop:always`.

## Ovládání feedu
- Kolečko myši a tažení prstem (nativní scroll-snap).
- Šipky nahoru a dolů posunou o výšku feedu (`scrollBy` s `behavior:'smooth'`). Platí jen když je obrazovka otevřená a cílem události není `INPUT`/`TEXTAREA`.
- `IntersectionObserver` (root = feed, `threshold:.6`) přidává viditelnému klipu třídu `.on`. Kreslí se a přehrává jen klip s `.on`.

## Karta klipu
Pozadí `linear-gradient(160deg, var(--a), var(--b))`, barvy z dat klipu. Vrstvy odspodu:
1. `<canvas class="cv" width="360" height="736">` přes celou kartu.
2. U klipu se záznamem také `<video class="vid">` (viz níže).
3. Nadpis `h2.ttl`: vlevo nahoře (`left:14px; right:70px; top:92px`), 26 px, tučně, stín.
4. Vpravo svisle tlačítka: **srdce** (počet lajků, `aria-pressed`, po lajku vyplněné `#ff4d6d`) a **bublina** (počet komentářů). Ikony jsou SVG, 30 px, čára 1,8.
5. Vlevo dole: avatar (barevné kolečko s písmenem), `@handle`, tlačítko **Sledovat / Sleduješ** (po sledování bílé vyplnění) a popisek.
6. Tenký ukazatel průběhu dole (`.pg`): u klipu s `.on` animace šířky 0 → 100 % za 8 s, dokola.
- **Lajk:** tlačítko přepíná. **Dvojklik** na klip dá lajk (jen přidá, neodebere) a ukáže velké srdce uprostřed (animace 0,7 s, po ní se prvek odstraní).
- Počty se zobrazují jako celá čísla (`toLocaleString('cs-CZ')`), ne zkráceně. Lajky = základ z dat + 1, když je klip olajkovaný. Komentáře = počet základních + vlastní.
- **Komentáře:** bublina otevře spodní panel (`#rsheet`, bílý, zaoblené horní rohy, nejvýše 58 % výšky) s nadpisem „Komentáře · <název klipu>“, tlačítkem ✕, seznamem a polem „Přidej komentář…“ (`maxlength=120`) s tlačítkem ↵. Odeslání je Enterem nebo tlačítkem. Vlastní komentáře se ukládají do `S.reels.com[id]`. Seznam se po odeslání odroluje dolů. Texty se vkládají přes `esc()`.
- Stav (lajky, sledování, komentáře) je v `S.reels` klíčovaný **stabilním id klipu**, ne pozicí, a ukládá se přes `save()`.

## Pořadí a id
Klipy mají pevná id 0–12. Pořadí zobrazení je zvlášť: `ORD = [12, 0, 1, 2, …, 11]`, takže záznam (id 12) je první a uložené lajky a komentáře u starších klipů zůstávají správně. DOM se skládá podle `ORD`. Vše ostatní (plátna, aktualizace počtů) se hledá přes `data-i`, ne přes pozici.

## Data klipů (id: název · autor [třída avataru, písmeno] · barvy a, b, c · lajky · popisek · komentáře)
0. **Večerní tramvaj** · @tereza.mesto [d0, T] · #1b1f4b, #7a3b8f, #ff7ab6 · 12400 · „Poslední spoj domů, město svítí.“ · „Která linka?“, „Tuhle trasu miluju.“
1. **Káva v sedm ráno** · @josef.kava [d3, J] · #3a2412, #a8642a, #ffc27a · 8300 · „Bez kávy se nedá začít.“ · „Jaká pražírna?“, „Dnes už druhá.“
2. **Skatepark o půlnoci** · @stepan_skate [d2, Š] · #0e3b43, #1fb3a8, #c9ff7a · 20100 · „Nový trik konečně sedl.“ · „Ten dopad!“, „Naučíš mě to?“
3. **Pivo po práci** · @jiri.bezi [d1, J] · #3b2a07, #d6951a, #fff0a8 · 5600 · „Útrata se rozúčtuje v bance.“ · „Kdo platí první?“, „Zítra opakovat.“
4. **Zkouška kapely** · @kapela.hluk [d0, K] · #2a0b3b, #e0457b, #6a4cff · 31000 · „Nová písnička je skoro hotová.“ · „Kdy koncert?“, „Pecka.“
5. **Noční běh** · @nocni.bezec [d1, N] · #07152b, #3b6cff, #7af0ff · 9800 · „Deset kilometrů za světla čelovky.“ · „Jaké tempo?“, „Respekt.“
6. **Nedívej se do spirály** · @spirala.cz [d1, S] · #12002b, #4b0f6b, #ff4dd2 · 1482000 · „Ještě jedno scrollnutí a jdu spát.“ · „jdu spát za 5 minut (je 4:12)“, „proč se na to dívám“, „už se mi to točí v hlavě“
7. **Počkej, až trefí roh** · @dvd.cekatel [d2, D] · #06232b, #0b5c63, #7af0ff · 964000 · „Čekám už třetí hodinu.“ · „SKORO!!“, „dívám se 40 minut“, „nikdy to netrefí“
8. **POV: banán tančí ve 3 ráno** · @banan.ve.3.rano [d3, B] · #2b0d3d, #ff7a18, #ffe135 · 2310000 · „Banán ví něco, co ty nevíš.“ · „proč to sleduju“, „dej mu víc ovoce“, „tohle mi změnilo život“
9. **Oči. Všude. Oči.** · @oci.vsude [d0, O] · #0f0f0f, #3a2f7a, #ff4d6d · 733000 · „Koukají. Koukají na tebe.“ · „ten vlevo nahoře mrkl“, „já se jim dívám zpátky“, „nemrkej“
10. **brain.exe neodpovídá** · @mozek.exe [d1, M] · #14052a, #7a1f5c, #7af0ff · 1190000 · „Mozek se zasekl na 99 procentech.“ · „mám to taky“, „restartovat? ne, ještě chvíli“, „zmrzlo mi to v hlavě“
11. **Dnes určitě vyhraju** · @slot.stesti [d2, S] · #2b0a0a, #7a1fe0, #ffe135 · 508000 · „Zase skoro. Příště to vyjde.“ · „SKORO“, „ještě jedno kolo“, „tohle není hazard, jen koukám“
12. **Automat a Běžec** (rozdělený klip se záznamem) · @tunelovy.bezec [d1, T] · #12002b, #4b0f6b, #ffb020 · 48200 · „Nahoře automat, dole záznam z Běžce (hraje autopilot).“ · „Hrál to člověk?“, „Ten skok přes bariéru!“

## Animace (canvas 360×736, čas `t` v sekundách, země `GY=560`)
Pomocné funkce: `rnd(i)` = deterministický hash `fract(sin(i*127.1)*43758.5)`, `wrap(v,m)` = kladný modulo, `circ(g,x,y,r,barva)`, `stars(g,t)` (40 hvězd, průhlednost plynule kolísá), `cap(g,text,y)` = titulek jako v memech (tučně 900 28px system-ui, bílá výplň, černý obrys 7 px, vystředěný na x=180). Překresluje se jen viditelný klip, jednou za snímek. Při zapnutém `prefers-reduced-motion` se kreslí jen pevný snímek v čase 0.
- **0 Tramvaj:** hvězdy, dvě vrstvy domů (rychlosti 20 a 45 px/s, barvy `#241a45`/`#1a1235`, výšky do 220/300 px, 8 domů po 70 px, perioda 560), na bližší vrstvě rozsvícená okna `#ffd27a`. Tramvaj `#e0457b` 220×80 na (70,470) s lehkým kolébáním `sin(9t)*1.5`, 5 oken `#ffe9a8`, drát ve výšce 420 s ramenem, kolej a dvě kola.
- **1 Káva:** slunce (`#ffc27a55`, r 95) pomalu stoupá a klesá, podšálek, hrnek `#f4efe6` s uchem, káva `#4a2a14`, tři vlnící se čáry páry (`sin`, průhlednost .35–.55).
- **2 Skate:** měsíc, země `#0b2a30` s posouvajícími se čárkami, cyklus 2,2 s: v prvních 60 % času skok do výšky 150 px s otočením prkna o 360°, stín se zmenšuje, ruce se zvedají. Postava v růžové mikině.
- **3 Pivo:** sklenice (lichoběžník 112–248 nahoře, 124–236 dole, 350–560), plní se za 3 s z cyklu 5 s do výšky 200 px, 22 bublinek, pěna z kruhů, která roste, obrys `#fff8`, ucho.
- **4 Kapela:** tři houpající se světelné kužely (bílá 11 % průhlednosti), reproduktor pulzující do rytmu `beat=|sin(2πt)|^6`, 20 sloupců ekvalizéru střídavě `#6a4cff`/`#e0457b`.
- **5 Noční běh:** hvězdy, stromy se paralaxou, cesta s posouvajícími se čárkami, běžec (nohy a ruce `sin(10t)`), kužel světla z čelovky s přechodem do průhledna.
- **6 Spirála:** 64 teček, úhel `i*.34+3t`, poloměr `i*2.8`, velikost `3+i*.17`, barva `hsl((i*7+50t)%360, 90%, 60%)`. Titulky po 1,3 s: SCROLUJ DÁL / NEDÍVEJ SE / JEŠTĚ JEDEN / ZA 5 MIN SPÁT (y=590).
- **7 Odrážející se box:** zaoblený obdélník 110×64 s textem „KLIP“ v rámu (14,164,332,370), rychlosti 95 a 80 px/s, stopa ze 6 průhledných kopií, barva se mění při každém odrazu od stěny. Titulky: ČEKÁM NA ROH / JEŠTĚ KOUSEK / SKORO... NE.
- **8 Banán:** pozadí s pomalu rotujícími výsečemi, banán `#ffe135` nakreslený Bézierovými křivkami se stopkou, oči sledující pohyb, ústa, kolébání těla a pohyb rukou a nohou `sin(6t)`. Titulky: POV: 3 RÁNO / BANÁN TANČÍ / PROČ TO SLEDUJU.
- **9 Oči:** 16 očí na pseudonáhodných pozicích (poloměr 18–46), zorničky sledují červenou tečku pohybující se po elipse, občasné krátké mrknutí. Titulky: OČI VŠUDE / KOUKAJÍ NA TEBE / NEMRKEJ.
- **10 Mozek:** růžový mozek ze dvou elips s rýhami, pulzuje, žluté blesky se mění 2,5× za sekundu, načítací lišta zasekne na 99 %. Titulky: BRAIN.EXE NEODPOVÍDÁ / 99 % – ČEKEJ / NEZAVÍREJ.
- **11 Automat:** tělo `#b01030` (30,200,300,230) se třemi bílými válci se symboly ★ ♥ ♦ ♣ 7 $, cyklus 6 s, válce se zastavují v 1,8 / 2,6 / 3,4 s, každý třetí cyklus je výhra (všechny stejné + žlutý obrys), celé se jemně houpe `sin(3t)*4`. Titulky: DNES VYHRAJU (při točení) / SKORO! / JACKPOT!!! (y=520).
- **12 Rozdělený klip:** automat (scéna 11) zmenšený na 0,62× a posunutý o (68, 20), takže leží v horní polovině. Pod ním (v dolní polovině) je video. Záložní text „Záznam se nenačetl“ leží na plátně pod videem a je vidět jen tehdy, když se video nenačte.

**Bezpečnost pro citlivé diváky:** žádné rychlé blikání (nic nemění barvu celé plochy rychleji než zhruba 3× za sekundu), barvy se mění plynule, titulky se střídají zhruba po sekundě.

## Záznam (dolní polovina klipu 12)
- `<video class="vid" muted loop playsinline preload="auto">`, umístěné `inset:auto 0 0 0; height:50%; object-fit:contain; border-top:2px solid #fff4`. `contain` je důležité: záznam má poměr 9:14 a ukáže se celý včetně skóre.
- **Obsah:** 12 s záznamu hry „Tunelový běžec“ (nekonečný běh po třech drahách) hrané autopilotem, 360×560 px, VP8 webm, asi 320 kB, s údajem o délce.
- **Jak vznikl:** headless Chromium (Playwright, `recordVideo` 360×560) spustil samostatnou stránku s hrou, autopilot v intervalu 16 ms vybíral dráhu (bez bloku `tall` v dohledu 420, mírný bonus za mince, jen o jednu dráhu za krok, aby neprořízl blok) a skákal přes nízké bariéry, když byly blíž než 0,3 s jízdy. Záznam, ve kterém hráč nenarazil a nasbíral aspoň 3 mince, se ostříhal a překódoval: `ffmpeg -ss <začátek> -t 12 -c:v libvpx -b:v 700k -crf 28 -an -pix_fmt yuv420p`, potom `-c copy`, aby soubor dostal délku.
- **Nasazení:** stránka deklaruje capability `assets`, video se nahraje do úložiště stránky a v kódu se odkazuje URL `/_blob/<id>`. Pro lokální test se URL nahradí cestou k souboru vedle stránky.
- **Přehrávání:** video hraje jen když je klip viditelný (`.on`) a aplikace Klipy je otevřená, jinak se pozastaví. Při návratu na klip začíná od nuly (`currentTime=0`). Spouští ho smyčka `requestAnimationFrame` přes `play().catch(()=>{})`.

## Technická omezení
- Stránka běží v zabezpečeném rámečku: nepoužívej `<form>`, `submit`, `confirm()`/`prompt()`. Enter v poli komentáře ošetři přes `keydown` s tvarem `e=>{if(e.key==='Enter')send()}` (nikdy `return false`, zablokoval by psaní).
- Šipky pro posun feedu se nesmí zachytit při psaní do pole.
- Zavřená obrazovka nic nekreslí a nepřehrává.
- Všechny texty z dat a od uživatele vkládej přes `esc()` nebo `textContent`.

## Kontrola (Playwright, chromium)
1. Klipy se otevřou, je jich 13, první v pořadí má id 12 a právě jeden má `.on`.
2. Kolečko myši přeskočí na další klip, šipky nahoru/dolů také. Aktivní klip se mění podle polohy.
3. Lajk přičte 1 a druhé klepnutí vrátí původní číslo. Dvojklik olajkuje a ukáže srdce. Sledování přepíná „Sledovat“ a „Sleduješ“.
4. Komentář s `<b>` se přidá a zobrazí jako text, počet komentářů vzroste.
5. U všech klipů 0–11 se mezi dvěma snímky plátna obraz liší (animuje se).
6. Klip 12: video zabírá přesně dolní polovinu, plátno má obsah jen nahoře (dole jen záložní text), video hraje, při přejetí na jiný klip se zastaví a při návratu začne od začátku, po zavření aplikace stojí.
7. Lajk a sledování přežijí obnovení stránky.
8. Zopakovat hlavní kroky v `<iframe sandbox="allow-scripts" srcdoc=...>` a ověřit, že v konzoli nejsou chyby.

## Co aplikace nedělá
Nemá skutečná videa kromě jednoho záznamu, žádné nahrávání, sdílení ani sdílený stav mezi lidmi. Autoři, lajky a komentáře jsou vymyšlené. Záznam je autopilot, ne člověk.
