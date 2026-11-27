Do jednostránkové bankovní aplikace (HTML + JS, stav v `localStorage`, částky v celých CZK, 4 lidé: 0 = Já, 1–3 = Plátce 1–3) přidej funkci **Skupinové rozúčtování**.

## UI (karta v aplikaci, nad Historií)
- Výběr, kdo útratu platil: 4 čipy (Já, Plátce 1, 2, 3).
- Pole „Útrata (CZK)“ a „Co to bylo“, tlačítko **Přidat útratu**.
- Seznam přidaných útrat (kdo platil, částka, popisek) a pod ním „Celkem X CZK · na osobu ≈ Y CZK“.
- Zaškrtávátko **Vlastní díly místo rovného dělení**. Po zaškrtnutí se ukážou 4 číselná pole (Já, Plátce 1–3), kolik z celkové útraty připadá na koho. Pod nimi živě „Zbývá rozdělit X CZK“ / „Díly sedí“. Text v polích je černý (`color:var(--ink)`).
- Tlačítko **Vyrovnat**.
- Stavový řádek (`role="status"`) pro hlášky.

## Logika
- Stav: `S.exp = [{who, amt, label}]`; u staršího uloženého stavu `S.exp = S.exp || []`.
- Čistá funkce `plan(exp, sh)` vrací seznam převodů `[od, komu, částka]`:
  1. `net[i]` = kolik člověk zaplatil minus jeho díl.
  2. Díl je `sh[i]`, jinak rovný: `floor(T/4) + (i < T%4 ? 1 : 0)`. Zbytek jde prvním lidem.
  3. Dlužníci (`net < 0`) a věřitelé (`net > 0`) se spárují hladově: `t = min(dluh, pohledávka)`, nulové převody se přeskočí.
- Vyrovnání přes existující funkci `pay(st, from, to, amt, note)`. Poznámka u převodů je „Rozúčtování“, převody se zapíšou do historie.
- Validace při **Přidat útratu**: částka je celé číslo ≥ 1, jinak hláška „Zadej celou částku větší než 0.“
- Validace při **Vyrovnat**:
  - Nejsou žádné útraty nebo žádný převod: „Není co vyrovnat.“
  - Ve vlastním režimu musí být díly celá čísla ≥ 0 a jejich součet přesně rovný celkové útratě, jinak „Díly dávají X, útrata je Y.“
  - Před jakýmkoli převodem se u každého dlužníka zkontroluje, že má dost peněz na součet svých plateb. Když ne, nic se nepošle a ukáže se „<Jméno> nemá dost peněz na vyrovnání.“ Nesmí vzniknout napůl hotové vyrovnání.
- Po úspěchu: `S.exp = []`, vymazat pole dílů, hláška „Vyrovnáno: N plateb.“, uložit a překreslit.
- Změna dílů nebo zaškrtávátka jen přepočítá „Zbývá rozdělit“ a viditelnost polí. Texty se uživatelům zobrazují přes `esc()`.

## Kontrola
Při načtení stránky dvě `console.assert`:
- `plan([{who:0,amt:400},{who:1,amt:200}])` vrátí 3 převody v součtu 300 CZK.
- Totéž s dílem `[600,0,0,0]` vrátí jediný převod `[0,1,200]`.

## Omezení (komentář `shortcut:` v kódu)
Jeden rozpis pro celý večer, ne pro každou útratu zvlášť. Výběr účastníků u každé útraty se nedělá.
