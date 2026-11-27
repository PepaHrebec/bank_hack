Do jednostránkové HTML aplikace, která simuluje telefon (rámeček s domovskou obrazovkou a aplikacemi, které se vysouvají přes celý displej), přidej hru **Tunelový běžec**: nekonečný běh po třech drahách v pseudo-3D, ovládaný myší a mezerníkem.

Hra je originální. Použij vlastní název a vlastní postavu (např. běžec v růžové mikině, s fialovým batohem a tyrkysovou kšiltovkou, nakreslený kódem v canvasu). Nepoužívej název, postavy ani vzhled existující hry.

## Předpoklady o okolní aplikaci
- Telefon má obrazovky `<section class="screen" id="...">` s třídou `.open` pro zobrazení. Vysouvají se zespodu (`transform:translateY(100%)` → `none`, `visibility:hidden` → `visible`). Ikony na domovské obrazovce mají atribut `data-<app>`, tlačítka „Domů“ a lišta dole mají `data-close`. Skript má pomocnou funkci `$ = id => document.getElementById(id)`.
- Pokud takové rozhraní neexistuje, vytvoř minimální: domovskou obrazovku s ikonami a vysouvací obrazovku pro hru s tlačítkem „Domů“.

## Integrace do telefonu
- **Ikona** na domovské obrazovce: popisek „Běžec“, čtvercová ikona s přechodem (oranžová → růžová) a písmenem „T“. Klepnutí přidá obrazovce hry `.open`.
- **Obrazovka hry** (`id="game"`) má tmavé pozadí (`#0e1118`, světlý text), záhlaví s nadpisem „Tunelový běžec“ a tlačítkem „Domů“ (bílé, tmavý text), pod ním canvas a krátká nápověda: „Myší vybereš dráhu. **Mezerník** nebo klik = skok. Bariéry přeskoč, vysoké bloky objeď.“
- Canvas: `width=360 height=560`, v CSS `width:100%; aspect-ratio:9/14; border-radius:16px; touch-action:none`. Musí se vejít do displeje bez posouvání.
- Když je hra otevřená, stavový řádek telefonu (hodiny) je bílý: `.phone:has(#game.open) .status{color:#fff}`.
- Tlačítko „Domů“ i lišta dole hru zavřou. Zavřená hra se nekreslí ani neaktualizuje (smyčka `requestAnimationFrame` běží dál, ale při zavřené obrazovce nedělá nic), po otevření pokračuje.
- Veškerý kód hry zabal do IIFE, aby se jeho jména (`st`, `hit`, `draw`, `fresh`…) nekolidovala s kódem zbytku aplikace. Vlastní funkci pro nový stav pojmenuj např. `gfresh`.

## Ovládání
- **Dráha:** `pointermove` na canvasu. Dráhu určuje třetina canvasu, nad kterou je kurzor (vlevo / uprostřed / vpravo). `pointerdown` nastaví dráhu i skok (kvůli dotykovým displejům).
- **Skok:** mezerník nebo klik. Skočit lze jen ze země.
- **Start a restart:** klik nebo mezerník. Po konci hry se restart 400 ms ignoruje, aby ho nespustil náhodný skok.
- Mezerník patří hře **jen když je obrazovka hry otevřená a cíl události není `INPUT`/`TEXTAREA`**. Jinak by ostatní aplikace (např. chat) přišly o mezery při psaní. Pro mezerník volej `preventDefault()` a ignoruj `e.repeat`.
- V zabezpečeném rámečku jde klávesnice až po zaměření okna. Na canvas proto přidej `pointerenter → window.focus()`.
- V obsluze klávesy nikdy nevracej `false` (zablokoval by psaní). Používej tvar `e=>{if(...)...}`. Nepoužívej `<form>`.

## Herní mechanika
- Tři dráhy (-1, 0, 1). Pozice runnera `x` se plynule blíží zvolené dráze (`x += (lane-x)*min(1,dt*12)`).
- **Perspektiva:** `proj(d) = 1/(1+d/160)` kde `d` je vzdálenost před runnerem. Obrazové souřadnice: horizont `HOR=170`, runner stojí na `GY=500`, šířka dráhy na úrovni runnera `LW=95`. Pro osu x je `sx(lane,z)=CX+lane*LW*z`, pro osu y `sy(z)=HOR+(GY-HOR)*z`.
- **Fyzika skoku:** počáteční rychlost 620, gravitace 1900, výška `y ≥ 0`.
- **Rychlost:** začíná 260 a roste o 8 za sekundu až na 700. Uražená vzdálenost `dist += speed*dt`.
- **Překážky** se rozmisťují po řadách (další řada o `max(420, 700 - speed*.6)` dál, generují se do vzdálenosti 1600 před runnerem). V každé řadě je jedna **volná dráha**, ve které jsou s pravděpodobností 0,7 čtyři mince po 60. V ostatních drahách je s pravděpodobností 0,45 překážka: **nízká bariéra** (žluto-černá, přeskočitelná) nebo **vysoký blok** (modrošedý s okny, nelze přeskočit, jen objet).
- **Kolize** řeší čistá funkce `hit(o, s)`: překážka je „v rovině“ runnera, když `|o.p - dist| ≤ 18` a `|o.l - x| < .55`. Mince se sebere. Vysoký blok vždy znamená náraz. Nízká bariéra znamená náraz, jen když `y < 38`. Jinak funkce vrací `null`.
- **Skóre:** `floor(dist/10) + 10*mince`. Rekord se ukládá do `localStorage` (vždy v `try/catch`).
- **Stavy:** `ready` → `play` → `over`. V `ready` a `over` se přes scénu kreslí tmavý panel s nadpisem, v `over` navíc „Konec hry“ a skóre, a vždy text „Klikni nebo stiskni mezerník“.

## Vykreslení (jen canvas 2D, bez knihoven)
Fialovo-modrá obloha s přechodem a siluetou města na horizontu, tmavá cesta ve tvaru lichoběžníku se světlými okraji a přerušovanými čarami mezi drahami, které se pohybují podle `dist`. Objekty se řadí od nejvzdálenějších, runner se kreslí mezi objekty před ním a za ním. Runner má stín na zemi, běžící nohy (sinus podle času), mikinu, batoh, hlavu a kšiltovku. Mince se otáčejí (šířka elipsy podle `cos`). Vlevo nahoře „Skóre“ a počet mincí, vpravo nahoře „Rekord“.

## Kontrola
1. Při načtení proběhne `console.assert` s pěti případy pro `hit()`: vysoký blok = náraz, nízká bariéra při skoku (`y=60`) = `null`, nízká bariéra na zemi = náraz, překážka v jiné dráze = `null`, mince = `'coin'`.
2. Playwright v `<iframe sandbox="allow-scripts" srcdoc=...>`: kliknout na ikonu, najet myší na hru, mezerník spustí hru, pohyb myši změní dráhu, druhý mezerník skočí (`y > 0`), po několika sekundách hra skončí nárazem a mezerník ji po 400 ms znovu spustí. Zkontrolovat, že v konzoli nejsou chyby.
3. Otevřít chat nebo jiné pole pro text, napsat „ahoj svete“ a ověřit, že mezery zůstaly a mezerník nespustil hru.

## Co hra nedělá
Žádné zvuky, žádné boosty, žádné skiny, žádný server. Po zavření obrazovky se hra pozastaví a po otevření pokračuje.
