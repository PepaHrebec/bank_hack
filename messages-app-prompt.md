Do jednostránkové HTML aplikace, která simuluje telefon (rámeček s domovskou obrazovkou), přidej aplikaci **Zprávy**: jednoduchý chat se třemi simulovanými protějšky, přílohami a žádostí o platbu, která se propíše do bankovního účtu v téže aplikaci.

Použij vlastní název a vlastní ikonu (např. modrý přechod s písmenem „Z“). Nepoužívej název ani logo existující aplikace nebo značky.

## Předpoklady
- Aplikace už má bankovní část: stav `S` s `bal[]` (zůstatky v celých CZK; 0 = já, 1–3 = protějšky), historii `S.hist` a funkci `pay(st, from, to, amt, note)`, která vrací text chyby nebo prázdný řetězec. Stav se ukládá do `localStorage` (vždy v `try/catch`) a po načtení se překresluje funkcí `render()`.
- Pokud banka neexistuje, vytvoř minimální verzi s těmito částmi.

## Obrazovky
- Ikona „Zprávy“ na domovské obrazovce otevře přes celý telefon vysouvací obrazovku (stejně jako bankovní aplikace). Tlačítko „Domů“ nebo lišta dole ji zavře.
- **Seznam chatů:** tři kontakty (jména např. Jiří, Štěpán, Josef) s barevným avatarem a číslem. U každého je náhled poslední zprávy (u fotky „Fotka“, u souboru „Soubor: název“, u prázdného chatu „Napiš první zprávu“). Seznam je seřazený podle času poslední zprávy.
- **Chat:** v záhlaví je jméno kontaktu a tlačítko „Zpět“ (z chatu do seznamu, ze seznamu domů). Pod tím je seznam bublin (moje vpravo modře, protějšku vlevo šedě, maximálně 82 % šířky, posuvný, po každé změně odrolovaný dolů). Každá bublina má čas `HH:MM`. Dole je řádek: tlačítko **+**, textové pole „Zpráva“ (`maxlength=200`) a tlačítko ↵.

## Zprávy
- Odeslání: klávesa Enter v poli nebo tlačítko ↵. Prázdný text se ignoruje. Pole se po odeslání vymaže.
- Protějšek je simulovaný: za ~800 ms odpoví jednou z předpřipravených vět (např. „👍“, „Jasně“, „Dobře, díky“, „Super 🙂“). Stav zpráv `S.chat = {1:[],2:[],3:[]}` se ukládá a po načtení se doplní, pokud chybí.
- Všechen text od uživatele se do HTML vkládá přes `esc()` (nebo `textContent`).

## Rozšíření pod tlačítkem + (řádek ikon, slabé šedé dlaždice, SVG ikony, popisky pod ikonou)
1. **Foto:** otevře výběr obrázku (`accept="image/*"`). Obrázek se přes `canvas` zmenší na delší stranu 320 px a uloží jako JPEG data URL (kvalita 0,7). V bublině se ukáže jako náhled. Soubor, který nejde otevřít jako obrázek, ukáže chybu „Tenhle soubor nejde otevřít jako obrázek.“ Protějšek odpoví „Pěkná fotka 👍“.
2. **Soubor:** otevře výběr libovolného souboru. Ukládá se jen název a velikost, v bublině je název tučně a velikost v kB (minimálně 1 kB). Protějšek odpoví „Dostal jsem, díky.“
3. **Platba:** rozbalí řádek s číselným polem „Částka (CZK)“ a tlačítkem „Požádat o platbu“.
- Po výběru foto nebo souboru se panel rozšíření zavře. Pole pro výběr souborů jsou skrytá `<input type="file" hidden>` a spouští se z ikon.

## Žádost o platbu (propojení s bankou)
- Částka musí být celé číslo ≥ 1, jinak hláška „Zadej celou částku větší než 0.“
- Do chatu přijde moje bublina „Pošli mi prosím X CZK“ se stavem **Čeká na odpověď…** a uloží se jako `{me:true, text, t, req:{amt, status:'pending'}}`.
- Po ~1,2 s protějšek zareaguje voláním `pay(S, protějšek, 0, částka, 'Žádost ve Zprávách (<jméno>)')`:
  - Při úspěchu je stav **Zaplaceno ✔** a protějšek napíše „Poslal jsem ✔“.
  - Při chybě (nemá dost peněz) je stav **Odmítnuto** a protějšek napíše „Teď na to nemám.“
- Převod je skutečný: změní se zůstatky, objeví se v historii bankovní aplikace jako příchozí platba s touto poznámkou a přepočítají se všechny prvky, které ukazují zůstatek nebo historii.
- Žádost, která byla při obnovení stránky ještě nevyřízená, se po načtení vyřídí znovu.

## Důležité technické omezení
Aplikace poběží v zabezpečeném rámečku (sandbox), který blokuje odesílání formulářů.
- Nepoužívej `<form>` ani událost `submit`. Odeslání zprávy napoj ručně přes `click` na tlačítko a `keydown` na `Enter` v poli.
- V obsluze klávesy nikdy nevracej `false` (například `e=>e.key==='Enter'&&send()` vrací `false` pro každou jinou klávesu a zablokuje psaní). Piš `e=>{if(e.key==='Enter')send()}`.
- Kontejner telefonu dej `overflow:clip`, aby se jeho obsah nedal posouvat programově.

## Co aplikace nedělá
Neposílá platby od uživatele protějšku (jen žádost o platbu od protějšku), nemá skutečné protějšky ani server. Zprávy jsou jen v prohlížeči. Fotky se ukládají jako malé náhledy a soubory jen jako název s velikostí, takže po velkém množství příloh se nové zprávy po obnovení stránky nemusí uložit (komentář `shortcut:` v kódu).

## Kontrola (Playwright, chromium)
1. Kliknout na ikonu, otevřít chat s prvním kontaktem, napsat text s `<b>` a odeslat Enterem. Text se zobrazí jako text a přijde odpověď.
2. Rozbalit +, přiložit soubor (název a kB se zobrazí) a foto (v chatu je jeden `<img>`).
3. Žádost o platbu s částkou 0 se odmítne. Žádost o 300 CZK přejde z „Čeká“ na „Zaplaceno“, zůstatek v bance vzroste o 300 a v historii je řádek „Žádost ve Zprávách (…)“.
4. Žádost o částku vyšší než zůstatek protějšku skončí „Odmítnuto“.
5. Po obnovení stránky zůstanou zprávy i zůstatek.
6. Zopakovat kroky 1 a 3 uvnitř `<iframe sandbox="allow-scripts" srcdoc=...>`, aby se ověřilo, že odesílání funguje i bez povolených formulářů.
