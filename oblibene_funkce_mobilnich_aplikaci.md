# Oblíbené funkce mobilních bankovních aplikací ve světě: katalog pro hackathon (stav k listopadu 2026)

Zákazníci po celém světě nejvíc oceňují funkce, které jim šetří čas a dávají pocit kontroly a bezpečí. Jde hlavně o okamžité platby (na telefonní číslo, přes QR nebo NFC), „obálky“ a „kapsičky“ na peníze, okamžité notifikace se zamknutím karty, ochranu před podvody přímo v aplikaci (ověření volajícího a jména příjemce) a proaktivní přehledy výdajů. Zbytek se dá postavit na těchto základech. Pro český hackathon je nejzajímavější, že řada nejoblíbenějších světových funkcí v Česku už existuje (obálky, zaokrouhlování, ověření volajícího, AI asistenti). Chybí ale jejich „druhá generace“: sdílené výdaje, ověření jména příjemce u korunových plateb, pasivní stav hovoru, předpověď zůstatku a agregace účtů.

## TL;DR

- **Nejprokazatelněji oblíbené funkce:** (1) okamžité platby bez čísla účtu (UPI, Pix, Zelle, české Platby na kontakt a QR), (2) rozdělení peněz do „kapsiček“ (Monzo Pots, Starling Spaces, Nubank Caixinhas, KakaoBank), (3) okamžité notifikace a zamknutí karty, které v průzkumu Bankrate považuje za důležité nebo zásadní 83 % uživatelů, (4) ochrana před podvody v aplikaci (Monzo Call Status, CommBank NameCheck/CallerCheck) a (5) proaktivní AI asistent (Bank of America Erica: 20,6 mil. uživatelů a skoro 700 mil. interakcí za rok 2025).
- **Co lidi nejvíc štve:** pády a nestabilita aplikace, problémy s přihlášením a autentizací, odstávky, nepomocné chatboty bez cesty k člověku a netransparentní poplatky u zahraničních plateb. Nedostatek funkcí je až za nimi. Stabilita a rychlost jsou podle J.D. Power základní měřítko spokojenosti.
- **Příležitosti pro Česko:** ověření jména příjemce u korunových plateb (dnes jen u SEPA a jen u UniCredit a Fio), sdílené účtenky a skupinové výdaje (jako Monzo Tabs nebo Starling Settle Up),\[1\] předpověď zůstatku a „bezpečné k utracení“ (U.S. Bank, CommBank), pasivní „stav hovoru“ jako u Monza, agregace účtů z jiných bank (většina velkých bank ji ruší) a gamifikované spoření typu KakaoBank 26 týdnů.

## Klíčová zjištění

1. **Hodnocení aplikací se sbíhají.** J.D. Power v roce 2025 konstatuje, že bankovní aplikace v USA se „čím dál hůř odlišují“, protože mají podobné základní funkce.\[2\] Spokojenost roste hlavně díky technickým vylepšením a rychlosti.\[3\] Nejlépe hodnocenou aplikací národních bank je Bank of America (678 bodů), následuje PNC (675) a Chase (673).\[2\] Mezi regionálními bankami vede Fifth Third (667). Studie měří čtyři faktory: navigaci, rychlost, vizuální dojem a informace a obsah.\[4\]
2. **Forrester každoročně oceňuje leadery mobilního bankovnictví.** Globálně byla v letech 2024 a 2025 na prvním místě BBVA (v roce 2025 Forrester hodnotil 28 bank).\[5\]\[6\] V hodnocení za rok 2026 (22 bank, zveřejněno 24. 11. 2026) vedou CommBank (Austrálie), Intesa Sanpaolo (Evropa), IDFC FIRST Bank (Indie) a U.S. Bank (Severní Amerika). Leadery spojuje, že „proměňují finanční přehledy v akci a zjednodušují každodenní úkoly“.\[7\]
3. **Zákazníci chtějí jednu aplikaci na všechno.** Podle Forresteru (2026) očekává 82 % online dospělých v metropolitní Indii, 71 % v Austrálii, 68 % v Evropě, 67 % v USA a 65 % v Kanadě, že bankovní aplikace bude jediným místem pro správu všech financí. Banky přitom podle Forresteru zlepšují spíš jednotlivé funkce, než aby celý zážitek promyslely znovu.\[7\]
4. **Evropské aplikace jsou „OK“, ale nenadchnou.** Podle Forresteru 70 % klientů souhlasí, že mobilní funkce jejich banky pokrývají jejich potřeby. Většina evropských zákazníků ale hodnotí zážitek jen jako „OK“ a málokterá banka očekávání překoná tak, aby to zvýšilo loajalitu.\[8\]
5. **AI asistenti jsou dvousečná zbraň.** Erica od Bank of America je nejúspěšnější nasazení na světě: kumulativně přes 3,2 mld. interakcí a podle banky přes 98 % uživatelů najde, co hledá.\[9\]\[10\] J.D. Power ale v roce 2025 zaznamenal pokles využívání i spokojenosti s virtuálními asistenty napříč trhem, protože mnoho z nich má omezené konverzační schopnosti a úzký záběr.\[2\]\[3\] Podle studie J.D. Power 2026 U.S. Banking Mobile App Satisfaction Study, jak ji cituje Unblu, se při problému obrací na virtuálního asistenta jen 28 % uživatelů aplikací. CFPB (Issue Spotlight, červen 2023) přitom zjistila, že chatbota mají všechny z 10 největších komerčních bank v USA a že s bankovním chatbotem v roce 2022 komunikovalo asi 37 % obyvatel USA.
6. **Česká jednička podle uživatelů je My Air.** Podle srovnání Finparády (červen 2025, průměr z Google Play, App Store, Finparády a AI hodnocení) vede My Air od Air Bank s 95,75 %. Následuje George České spořitelny (94,50 %) a ČSOB Smart (93,33 %).\[11\]\[12\] ČSOB Smart má v českém App Store 4,8 hvězdičky ze zhruba 147 tisíc hodnocení.\[13\]

## Top 15 nejoblíbenějších funkcí napříč světem

| # | Funkce | Vzorové aplikace | Hlavní důkaz oblíbenosti |
|---|---|---|---|
| 1 | Okamžité platby bez čísla účtu (telefon, QR, alias, NFC) | UPI (Indie), Pix (Nubank), Zelle (BofA), Platby na kontakt (ČR) | UPI v prosinci 2025: 21,63 mld. transakcí za měsíc.\[14\] Zelle u BofA: 25 mil. aktivních uživatelů a 1,8 mld. transakcí v roce 2025\[10\] |
| 2 | „Kapsičky“ a obálky na peníze | Monzo Pots, Starling Spaces, Nubank Caixinhas, Revolut Pockets | Starling označuje Spaces za svou „nejoblíbenější funkci“.\[15\] Which? u Monza zmiňuje úročené pots\[16\] |
| 3 | Okamžité notifikace o každé transakci | Monzo, Starling, Revolut, BofA | BofA rozeslala 13,3 mld. upozornění, přes 38 mil. odběratelů\[17\] |
| 4 | Zamknutí a odemknutí karty, limity, virtuální karty | Revolut (jednorázové karty), všechny velké banky | 83 % uživatelů považuje zamknutí karty za zásadní nebo důležité (Bankrate)\[18\] |
| 5 | Ověření, že volá opravdu banka | Monzo Call Status, CommBank CallerCheck, české banky (push ověření) | Monzo i CommBank to uvádějí jako průmyslové prvenství. CommBank hlásí pokles ztrát klientů z podvodů o více než 70 %\[19\]\[20\] |
| 6 | Kontrola jména příjemce před platbou | CommBank NameCheck, Confirmation of Payee (UK, AU), VoP (EU) | NameCheck podle CommBank zabránil podvodům a chybným platbám za 650 mil. AUD\[21\] |
| 7 | Proaktivní AI asistent | BofA Erica, BBVA Blue, ČSOB Kate, Hey George | Erica: 20,6 mil. uživatelů a skoro 700 mil. interakcí v roce 2025.\[10\] Kate: 1,7 mil. unikátních uživatelů\[22\] |
| 8 | Automatické spoření: zaokrouhlování a pravidla | Starling Round Ups,\[15\] Monzo Salary Sorter, U.S. Bank, Česká spořitelna „Platím a spořím“ | Česká spořitelna: v pilotu průměrně 240 Kč měsíčně.\[23\] U.S. Bank je leader Forresteru 2026\[7\] |
| 9 | Výplata dřív a přečerpání bez poplatku | Monzo Get Paid Early, Chime Get Paid Early a SpotMe | Monzo: „velmi populární“ funkce.\[24\] Chime: výplata až o 2 dny dřív, SpotMe až 200 USD bez poplatku\[25\] |
| 10 | Dělení účtů a žádosti o platbu | Monzo (bill-splitting, Tabs), Starling Settle Up, KakaoBank skupinový účet | Which? u Monza mezi oceňovanými funkcemi výslovně uvádí bill-splitting\[16\] |
| 11 | Gamifikované spoření | KakaoBank 26týdenní výzva, AI Goal Savings | Přes 11 mil. účtů 26týdenního spoření.\[26\] AI spoření má 100 tis. účtů za první měsíc\[27\] |
| 12 | Poplatků prosté platby v zahraničí a multiměnové účty | Revolut, Monzo, Wise | Revolut je Euromoney World's Best Digital Bank 2025.\[28\] Which? u Monza zmiňuje poplatků prosté placení v zahraničí\[16\] |
| 13 | Rozpočty, přehledy výdajů a předpověď zůstatku | CommBank (startovní rozpočty), U.S. Bank (předpověď zůstatku), Intesa (skóre finančního zdraví) | Leadeři Forresteru 2026 a 2025\[7\]\[8\] |
| 14 | Plně digitální onboarding a produkty v aplikaci | Monzo, Nubank, KakaoBank, Revolut | Monzo (výroční zpráva FY2026): 15,2 mil. klientů, 10,4 mil. aktivních každý měsíc. Revolut: „slick and quick“\[29\] |
| 15 | Přístupnost a zjednodušený režim | BBVA (zjednodušený režim), PKO BP (hlasová navigace) | Hodnoceno ve Forresteru 2025 jako odlišující prvek leaderů\[8\] |

**Proč právě tyhle:** Funkce 1–6 řeší nejčastější každodenní úkon (zaplatit, zkontrolovat, zablokovat) nebo nejsilnější emoci (strach z podvodu). Funkce 7–13 posouvají aplikaci od výpisu k „finančnímu pomocníkovi“, což podle Forresteru odlišuje leadery od ostatních. Funkce 14–15 rozhodují o tom, kdo se do aplikace vůbec dostane.

## Podrobný katalog funkcí podle kategorií

### 1. Platby a převody

**Platba na telefonní číslo nebo alias**
- *Popis:* místo čísla účtu stačí zadat telefon, e-mail nebo jiný alias.\[30\]
- *Vzory:* UPI (Indie), Pix (Brazílie), Zelle (USA), české Platby na kontakt (od listopadu 2023, Air Bank, Česká spořitelna, ČSOB, Fio, KB, Raiffeisenbank, později další).\[31\]\[32\]
- *Důkaz:* Podle zprávy Worldline „India Digital Payments Report – Year 2025 in Review“ zpracovalo UPI v roce 2025 228,5 mld. transakcí, meziročně o 33 % víc, v hodnotě 299,74 bil. INR. V prosinci 2025 dosáhlo rekordních 21,63 mld. transakcí za měsíc. Podle pololetní Payment Systems Report RBI tvořilo UPI ve druhém pololetí 2025 85,5 % objemu digitálních transakcí v Indii. Zelle u Bank of America mělo v roce 2025 25 mil. aktivních uživatelů a 1,8 mld. transakcí za 556 mld. USD (meziroční růst o 16 %, resp. 18 %).\[10\] V Česku podle průzkumu Ipsos pro Českou bankovní asociaci plánovaly Platby na kontakt využívat téměř dvě třetiny lidí. Hlavním důvodem bylo jednodušší a rychlejší vyplnění.\[31\]
- *Proč se líbí:* žádné opisování čísla účtu, méně chyb, platba „mezi přáteli“ za pár sekund.

**QR platby**
- *Vzory:* české banky (standard SPAYD podporují všechny velké banky),\[33\] Lipa na M-PESA v Keni,\[34\] UPI QR, Pix QR.
- *Důkaz:* podle údajů citovaných ze stránky fakturaonline.cz (průzkum ČBA 2025) platí přes 61 % aktivních uživatelů mobilního bankovnictví faktury QR kódem.\[33\] Ověřte v primárním zdroji ČBA. Air Bank a Česká spořitelna umí QR načíst i ze screenshotu nebo z PDF.\[33\]
- *Proč se líbí:* odpadá přepisování symbolů a čísla účtu, takže je méně chyb.\[35\]

**Platba přiložením telefonu a platba hlasem**
- *Vzor:* Nubank „Pix por aproximação“ (květen 2025). Na Androidu stačí přiložit telefon k terminálu, platit se dá ze zůstatku nebo na splátky až ve 12 dávkách. Lze si udělat zkratku na plochu.\[36\]\[37\]
- *Doplněk:* Nubank umožňuje poslat Pix hlasovou nebo krátkou textovou zprávou zpracovanou AI. Podle Nubanku to zkracuje čas transakce až o 60 %.\[36\]
- *Proč se líbí:* rychlost na pokladně, žádné skenování.

**Offline režim**
- *Vzor:* M-PESA Super App od Safaricomu má „Offline Mode“, ve kterém jdou nejběžnější transakce provést bez Wi-Fi a mobilních dat.\[38\]
- *Proč se líbí:* aplikace funguje i při slabém signálu. Pro Českou republiku je to inspirace hlavně pro odolnost při výpadcích.

### 2. Správa výdajů, rozpočtování a přehledy

**Okamžité notifikace a kategorizace výdajů**
- *Vzory:* Monzo, Starling, Revolut, BofA.
- *Důkaz:* Trustpilot u Monza a Starlingu opakovaně uvádí okamžité notifikace o útratě mezi nejoceňovanějšími funkcemi.\[39\]\[40\]\[41\] Bank of America za rok 2025 rozeslala 13,3 mld. upozornění a počet odběratelů upozornění přesáhl 38 milionů.\[17\]
- *Proč se líbí:* klid („vidím každou korunu“) a okamžité odhalení podvodu.

**Předpověď zůstatku, „money tracker“ a nadcházející platby**
- *Vzory:* U.S. Bank (leader Forresteru 2026 pro Severní Ameriku) má money tracker a předpověď zůstatku, které ukazují příjmy, výdaje a budoucí tlak na cash flow.\[7\] Starling ukazuje nadcházející transakce pár dní dopředu. Recenzenti na Trustpilotu oceňují, že je „nic nepříjemně nepřekvapí“.\[40\]
- *Proč se líbí:* aplikace se dívá dopředu, ne jen zpětně.

**Startovní rozpočty a personalizované přehledy**
- *Vzor:* CommBank (leader Forresteru 2026 v Austrálii) nabízí startovní rozpočty podle průměrných výdajů klienta. Personalizované přehledy výdajů, investiční vzdělávání, srovnání produktů a správu portfolia má v jedné aplikaci. Díky tomu sesadila Westpac, který vedl tři roky po sobě.\[7\]
- *Proč se líbí:* rozpočet není prázdný formulář, ale hotový návrh.

**Skóre finančního zdraví a srovnání s ostatními**
- *Vzory:* Intesa Sanpaolo (komplexní skóre finančního zdraví, srovnání s podobnými klienty, automatické spoření) a BBVA (nástroje finančního zdraví, proaktivní notifikace).\[8\]
- *Důkaz:* obě banky jsou leadery Forresteru pro Evropu v roce 2025.\[8\]

**Sledování předplatných a opakovaných plateb kartou**
- *Vzory:* Erica od BofA sleduje opakované platby.\[9\] V Česku ukazují obchodníky s uloženou kartou Moneta (od června 2026 včetně blokace plateb konkrétnímu obchodníkovi), Air Bank (odebrání karty jedním klepnutím), George a mBank (mBank kartu u obchodníka smazat neumí).\[42\]\[43\]\[44\]
- *Proč se líbí:* odhalí zapomenutá předplatná a vrátí kontrolu.

### 3. Spoření a investice

**„Kapsičky“ (Pots, Spaces, Caixinhas, obálky)**
- *Popis:* pojmenované oddělené části zůstatku, často s cílem, vlastní kartou nebo úrokem.
- *Vzory:* Monzo Pots a Bills Pots, Starling Spaces (každý Space může mít virtuální kartu),\[45\] Nubank Caixinhas, Revolut Pockets a Vaults. V Česku spořicí obálky v Georgi (až 9 obálek), Air Bank (až 10 obálek na účtu) a ČSOB.\[24\]\[46\]\[47\]\[48\]\[49\]
- *Důkaz:* Starling na svém webu označuje Spaces za „naši nejoblíbenější funkci“.\[15\] Which? v roce 2025 jmenoval Monzo podruhé za sebou doporučeným poskytovatelem běžných účtů se skóre 85 %. Zákazníci zmiňovali právě úročené pots, rozpočtovací nástroje, dělení účtů a poplatků prosté placení v zahraničí.\[16\] Na Trustpilotu se pots u Monza opakují jako funkce, kvůli které lidé banku mění („pots jsou to, co mi dělá radost“).\[50\] Podle Nubanku (Suno, srpen 2023) měly Caixinhas 8,6 mil. aktivních klientů oproti 3,5 mil. v lednu 2023 a spravovaly 14,6 mld. BRL. Guilherme Espallargas z Nubanku k tomu řekl, že růst počtu klientů využívajících Caixinhas ukazuje, jak moc investory motivují konkrétní cíle. Caixinhas inspirovaly dokonce funkci „rezervy dat“ v mobilním tarifu Nubanku NuCel.
- *Proč se líbí:* mentální účetnictví bez zakládání dalších účtů. „Peníze na nájem“ se nedají omylem utratit.

**Automatické rozdělení výplaty**
- *Vzory:* Monzo Salary Sorter (rozdělí výplatu do pots v den výplaty), U.S. Bank (automatické převody podle zůstatku, nákupů kartou nebo výplaty), Intesa (automatické spoření).\[7\]\[8\]\[51\]
- *Proč se líbí:* spoření běží samo, nevyžaduje disciplínu.

**Zaokrouhlování (round-ups)**
- *Vzory:* Starling Round Ups, Monzo, Revolut. V Česku „Platím a spořím“ České spořitelny (zaokrouhlení na 10 Kč, v pilotu průměrně 240 Kč měsíčně), drobné spoření Air Bank, Raiffeisenbank Drobné spoření (pevná částka za platbu), ČSOB Drobné (rozdíl jde do fondu) a mBank mSpoření.\[23\]\[51\]\[52\]\[53\]\[54\]
- *Proč se líbí:* „nebolí to“ a výsledek je vidět.

**Gamifikované spoření**
- *Vzor:* 26týdenní spořicí výzva KakaoBank (od roku 2018). Začíná se od 1 000 wonů a částka každý týden roste.\[55\] Klient si vybere oblíbenou postavičku a cíl a průběh může sdílet na sociálních sítích.\[26\]\[56\]\[57\]
- *Důkaz:* přes 11 milionů účtů.\[58\] Produkt odstartoval celý trend „26týdenního spoření“ mezi mladými Korejci a firmy (Lotte Duty Free, Jeju Air) ho dnes využívají pro partnerské kampaně.\[26\]\[57\] Nový AI Goal Savings Account KakaoBank (listopad 2026) má za první měsíc přes 100 tisíc účtů. Dvě třetiny klientů přijaly AI navržený cíl a zhruba 70 % po AI „koučinku“ v den příjmu přidalo vklad. Nejvíc klientů poslouchalo „chladného trenéra, který říká krutou pravdu“.\[27\]
- *Proč se líbí:* malý závazek, krátký horizont, vizuální pokrok a zábava.

**Investice přímo v aplikaci**
- *Vzory:* Revolut (akcie, ETF, komodity), CommBank (vzdělávání a správa portfolia), PKO BP „Investomat“ (personalizované investiční doporučení), ČSOB Drobné.\[7\]\[8\]\[53\]\[59\]

### 4. Karty a bezpečnost

**Zamknutí a odemknutí karty, limity, PIN v aplikaci**
- *Důkaz:* podle přehledu Bankrate je zamknutí ztracené nebo ukradené karty nejcennější mobilní funkcí: 83 % uživatelů ji považuje za zásadní nebo důležitou. Druhý je mobilní vklad šeku (79 %), který je relevantní pro USA, ne pro ČR.\[18\]
- *Proč se líbí:* okamžitá kontrola bez telefonování na linku.

**Jednorázové a virtuální karty**
- *Vzor:* Revolut. Recenzenti výslovně oceňují jednorázové karty pro nákupy na neznámých webech.\[60\]

**Ověření volajícího v aplikaci**
- *Vzory:* Monzo Call Status ukazuje v aplikaci v reálném čase, jestli s vámi opravdu mluví Monzo, a odtud jde rovnou nahlásit podvod.\[61\]\[62\] Monzo to uvádělo jako průmyslové prvenství ve Velké Británii, kde se v roce 2022 ztratilo na podvodech s vydáváním se za banku 177 mil. GBP.\[19\] CommBank má CallerCheck a CustomerCheck.\[63\] V Česku umí ověření hovoru přes aplikaci Česká spořitelna (od roku 2022), ČSOB, KB, Raiffeisenbank, Moneta, Air Bank, mBank (od června 2023) a Fio (od července 2026).\[64\]\[65\]\[66\]
- *Rozdíl:* české banky typicky posílají push notifikaci na žádost klienta.\[67\] Pasivní, stále viditelný „stav hovoru“ jako u Monza jsem nenašel.

**Kontrola jména příjemce**
- *Vzory:* CommBank NameCheck (od března 2023) porovná zadané jméno a číslo účtu s platebními daty a upozorní na nesoulad, a to i když jméno sedí, ale transakce vykazuje rizikové znaky. Podle CommBank zabránil podvodům a chybným platbám za 650 mil. AUD (červenec 2023 – prosinec 2024).\[21\]\[68\]\[69\] Banka zároveň hlásí pokles ztrát klientů z podvodů o více než 70 %.\[20\]
- *Česko:* nařízení EU o okamžitých platbách zavádí ověření příjemce (VoP) pro platby v eurech. V Česku ho jako první nabídla UniCredit (od 9. 10. 2025), druhá byla Fio.\[70\]\[71\] Pro korunové platby obecně chybí.\[72\] KB+ zobrazí jméno majitele účtu jen u účtu, kam už klient dříve platil.\[73\]

**Biometrie a vícefaktorové ověření**
- *Důkaz:* podle J.D. Power je u uživatelů aplikací národních bank celková spokojenost o 16 bodů vyšší, když používají vícefaktorové ověření už před přihlášením.\[4\]
- *Pozor:* přílišné tření při autentizaci je zároveň nejčastější stížnost (viz pain pointy).

**„Režim ulice“ a chytré limity**
- *Vzor:* Nubank „modo rua“ s nastavitelnými limity pro platby mimo domov a upozorněními na podezřelé transakce v reálném čase.\[74\]

### 5. Personalizace a AI asistenti

- *Bank of America Erica:* hlasem nebo textem vyhledá transakce, zamkne kartu, pošle Zelle nebo sleduje opakované platby. V roce 2025 ji použilo 20,6 mil. lidí téměř 700 milionkrát. Od roku 2018 má přes 3,2 mld. interakcí a podle banky přes 98 % uživatelů najde potřebnou informaci. Velká část interakcí jsou proaktivní tipy, které Erica nabídne sama.\[9\]\[10\]
- *BBVA:* konverzační asistent soustřeďuje transakce, podporu i personalizované finanční přehledy (Forrester 2025, evropská jednička).\[8\]
- *PKO Bank Polski:* konverzační AI asistent spojený s hlasovou navigací.\[8\]
- *IDFC FIRST Bank:* AI nástroj odpovídá na dotazy, vyhledává informace a dokončuje bankovní úkony (Forrester 2026, jednička v Indii).\[7\]
- *Česko:* ČSOB Kate má podle výroční zprávy skupiny ke konci roku 2025 1,7 mil. unikátních uživatelů.\[22\] V roce 2026 přešla na velké jazykové modely a podle ČSOB klienti oceňují lepší porozumění.\[75\]\[76\]\[77\] Česká spořitelna má Hey George (radí i s osobními financemi), Air Bank Anetu (podle e15 řeší dvě třetiny klientských dotazů), KB Ruby a Moneta Toma.\[78\]\[79\]\[80\]
- *Proč se líbí:* odpověď kdykoli bez čekání a hlavně „udělej to za mě“ (zablokuj, pošli, najdi). Podle J.D. Power ale spokojenost klesá, když asistent jen odkazuje na FAQ.\[2\]

### 6. Onboarding a produkty v aplikaci

- *Vzory:* Monzo (recenzenti mluví o „nejlepším onboardingu“), Nubank, KakaoBank (minimalizovaný proces registrace), Revolut. Euromoney u Revolutu oceňuje „slick and quick“ nákup finančních produktů v aplikaci.\[29\]\[51\]\[81\]
- *Důkaz:* Podle výroční zprávy Monzo za FY2026 (rok do 31. 3. 2026) přibyly 3 mil. klientů na celkových 15,2 mil. Počet měsíčně aktivních uživatelů vzrostl o 26 % na 10,4 mil. a 49 % z nich používá Monzo jako hlavní banku.
- *Česko:* Bankovní identita umožňuje založit účet bez návštěvy pobočky.

### 7. Notifikace a proaktivní upozornění

- *Vzory:* BBVA (proaktivní notifikace), PKO BP (spořicí „nudge“ v reálném čase), Intesa (upozornění na možnou duplicitní platbu a na rozhodnutí, která by vedla k poplatkům), ČSOB Kate (upozorní na nezaplacené pojistné a rovnou připraví příkaz).\[7\]\[8\]\[82\]
- *Proč se líbí:* banka „hlídá za mě“ a pomáhá předcházet chybám.

### 8. Gamifikace a věrnost

- *Vzory:* KakaoBank (postavičky, 26týdenní výzva), Revolut RevPoints (celoevropský věrnostní program pro platby debetní kartou), ČSOB Kate Coin (body za využívání aplikace, podle ČSOB skoro 700 tisíc aktivních uživatelů),\[83\] Monzo placené plány s partnerskými benefity (podle výroční zprávy FY2026 přes 1,6 mil. předplatitelů).

### 9. Sdílení plateb, dělení účtů a skupinové účty

- *Vzory:* Starling Settle Up (žádost o peníze odkazem, zaplatit může i klient jiné banky),\[1\] Monzo (bill-splitting a sdílené Tabs), KakaoBank skupinový účet (mezi dvacátníky a třicátníky oblíbený na sdílení výdajů na rande), Air Bank „Zaplať mi“ (rozdělí částku mezi více lidí přes QR).\[26\]\[51\]\[84\]
- *Důkaz:* bill-splitting je mezi funkcemi, které zákazníci Monza výslovně zmiňovali v hodnocení Which?.\[16\]

### 10. Podpora a chat

- *Vzory:* Monzo (lidský chat 24/7 v aplikaci, recenzenti chválí rychlost), Nubank (filozofie „Customer Love“, NPS jako hlavní metrika při uvádění nových produktů).\[85\]\[86\]
- *Negativní vzor:* Wells Fargo podle analýzy recenzí Unstar.app nemá pro osobní bankovnictví chat v aplikaci. Revolut podle recenzí frustruje u složitějších problémů silnou závislostí na AI chatu.\[87\]

### 11. Přístupnost a inkluze

- *Vzory:* BBVA má zjednodušený režim, PKO BP hlasovou navigaci a podporu čtečky obrazovky.\[8\]
- *Kontext:* podle Forresteru se přístupnost mezi evropskými bankami výrazně liší a hlasová navigace ani zjednodušené režimy zatím nejsou standard.\[8\] J.D. Power navíc v prosinci 2025 zjistil, že spokojenost s národními bankami v USA vzrostla u klientů do 64 let o 12 bodů, ale u lidí nad 65 let zůstala beze změny.\[88\]

### 12. Open banking a agregace účtů

- *Vzory:* IDFC FIRST Bank (leader Forresteru 2026 v Indii) umožní přidat účty a úvěry z jiných institucí a sledovat čisté jmění, cash flow, spořicí cíle a investice na jednom místě.\[7\] Monzo nabízí v placeném plánu přehled jiných bank a kreditních karet.\[24\]
- *Česko:* trend je opačný (viz níže).

### 13. Mikroúvěry a přečerpání bez stresu

- *Vzory:* Chime SpotMe (přečerpání až 200 USD bez poplatku) a MyPay (přístup k části výplaty předem).\[89\]\[90\] M-PESA Fuliza (přečerpání přímo při platbě) aktivně používá 9,1 mil. Keňanů podle pololetních výsledků Safaricomu z listopadu 2025.\[91\]
- *Proč se líbí:* platba „neselže u pokladny“. Pozor ale na riziko zadlužování, tohle je citlivá oblast.

## Co zákazníky nejvíc štve (pain pointy z recenzí)

1. **Pády, zamrzání a pomalost.** Analýza 6 790 recenzí 35 největších bankovních aplikací (AppImp, červen 2026) řadí „aplikace padá, zamrzá nebo se nenačte“ na první místo s 24 % stížností.\[92\]
2. **Přihlášení a autentizace.** Stejný podíl, 24 %.\[92\] Studie Amirkhaliliho a Wonga z University of Waterloo „Banking on Feedback“ (arXiv, březen 2025) analyzovala recenze aplikací pěti kanadských bank (CIBC, TD, RBC, Scotiabank, BMO) z iOS i Google Play. V negativních recenzích opakovaně našla potíže s přihlášením, chyby a nespokojenost s aktualizacemi. Typické jsou stížnosti na SMS kódy v zahraničí, vynucená odhlášení, nefunkční biometrii a nefunkční push notifikace k potvrzení přihlášení.\[93\]\[94\]
3. **Aktualizace, které něco rozbijí nebo změní design.** Častý zdroj jednohvězdičkových recenzí. Patří sem i ukončení podpory starších verzí OS.\[92\]\[95\]
4. **Nedostupná nebo nepomocná podpora a smyčky chatbotů.** 14 % stížností podle AppImp.\[92\] Analýza Unstar.app (2026), která vychází z recenzí aplikací Chase, Wells Fargo, Bank of America a Capital One s 1–3 hvězdičkami, připisuje 9 % stížností přesměrování podpory do smyčky s chatbotem. J.D. Power potvrzuje, že asistenti často nesplňují očekávání.\[2\]
5. **Chybějící nebo nefunkční základní funkce.** 14 % stížností.\[92\] Patří sem nespolehlivé notifikace u přečerpání a nového přihlášení.\[96\]
6. **Odstávky a výpadky.** Recenze ČSOB Smart v App Store si stěžuje na údržbová okna dlouhá „až 10+ hodin“.\[13\] Nubank měl v roce 2025 opakované výpadky, mimo jiné nedostupné Caixinhas v červnu 2025.\[97\]
7. **Zahraniční platby.** Podle Forresteru (2025) zůstávají těžkopádné, s malou transparentností poplatků a nekonzistentní podporou převodu měn v reálném čase.\[8\]
8. **Nedostatečná ochrana před podvody.** Podle Forresteru chybí proaktivní upozornění na podvody a provedení klienta nahlášením.\[8\]
9. **Nekonzistence napříč kanály.** Web a aplikace se liší, přihlášení se vyžaduje opakovaně mezi produkty (Chase) a klient musí věci vysvětlovat znovu.\[96\]\[98\]
10. **Přehnaná ochrana proti podvodům.** Blokace transakcí a účtů bez vysvětlení. Na Trustpilotu se objevuje i u jinak velmi chválených bank, jako je Starling.\[99\]\[100\]

**Ponaučení pro hackathon:** stabilita, rychlé a bezbolestné přihlášení a dobře řešená cesta „když se něco pokazí“ mají větší váhu než další nová funkce.

## Co v českých bankovních aplikacích zatím chybí nebo je slabé (příležitosti)

Ověřeno pro George, ČSOB Smart, KB+, My Air, Raiffeisenbank, Moneta, Fio a mBank ze zdrojů z let 2023–2026. Nepřítomnost funkce je odvozena z toho, že se nenašla, nikoli z oficiálního potvrzení.

| Funkce | Stav v ČR | Světový vzor | Příležitost |
|---|---|---|---|
| Ověření jména příjemce u korunových plateb | Chybí. VoP jen pro SEPA a jen u UniCredit a Fio. Povinnost pro české banky u eur až od 9. 7. 2027\[71\]\[101\] | CommBank NameCheck, UK Confirmation of Payee | Vysoká: prevence podvodů i překlepů |
| Pasivní „stav hovoru“ v aplikaci | Banky mají ověření hovoru na vyžádání (push), stále viditelný stav ne | Monzo Call Status | Střední až vysoká: snadno uchopitelné na hackathonu |
| Sdílené výdaje a skupinové účty | Jen QR žádosti o platbu (Air Bank „Zaplať mi“ umí rozdělit částku)\[84\] | Monzo Tabs, Starling Settle Up, KakaoBank skupinový účet | Vysoká: sociální a virální funkce |
| Agregace účtů jiných bank | Ustupuje. ČSOB zrušila v roce 2023, Raiffeisenbank končí 20. 2. 2026, KB+ ani George ji nemají. Zůstává Air Bank, Moneta a Partners\[102\] | IDFC FIRST, Monzo | Střední: banky uvádějí nízký zájem, takže je potřeba lepší hodnota (čisté jmění, cash flow)\[102\] |
| Předpověď zůstatku a „bezpečné k utracení“ | Nenalezeno jako standard | U.S. Bank, Starling (nadcházející platby), CommBank | Vysoká: odpovídá trendu Forresteru |
| Zrušení předplatného u obchodníka | Banky umí jen přehled a blokaci karty (Moneta, Air Bank, George, mBank)\[42\]\[43\] | Erica (sledování opakovaných plateb) | Střední |
| Gamifikované spoření s výzvou | Obálky a zaokrouhlování existují, výzvy typu „26 týdnů“ jsem nenašel | KakaoBank | Střední až vysoká: levné na prototyp |
| Zjednodušený režim a hlasová navigace | Nenalezeno jako standard | BBVA, PKO BP | Střední: senioři (viz J.D. Power) |
| Pravidla automatického spoření podle výplaty | Částečně (trvalé příkazy, zaokrouhlování) | Monzo Salary Sorter, U.S. Bank | Střední |

**Co v Česku už funguje dobře a nemá smysl to „vymýšlet“:** platby QR kódem (SPAYD), Platby na kontakt (limit 5 000 Kč),\[33\]\[103\] spořicí obálky (George, Air Bank, ČSOB), zaokrouhlování (Česká spořitelna, Air Bank, Raiffeisenbank, ČSOB, mBank), ověření bankéře přes aplikaci (téměř všechny velké banky) a AI asistenti (Kate, Hey George, Aneta, Ruby, Tom).\[32\]\[46\]\[48\]\[53\]\[66\]\[80\]\[104\]

## Doporučení pro zadání hackathonu

1. **Postavte výzvy na ověřených vzorech, ne na nápadech od nuly.** Doporučuji 4–5 tracků: (a) „Anti-scam“ (NameCheck pro korunové platby, pasivní Call Status, provedení klienta nahlášením podvodu), (b) „Social money“ (sdílené výdaje à la Settle Up a Tabs), (c) „Pohled dopředu“ (předpověď zůstatku a „bezpečné k utracení“), (d) „Spoření jako hra“ (výzva à la KakaoBank s volbou tónu AI kouče) a (e) „Když se něco pokazí“ (UX výpadků, přihlášení a předání z chatbota na člověka).
2. **Měřte to, co měří J.D. Power a Forrester:** rychlost, navigaci, vizuální dojem, kvalitu informací a dokončení úkolu ve scénáři. Týmy ať ukazují počet kroků a čas na úkol.
3. **Přidejte povinné kritérium přístupnosti** (zjednodušený režim, čtečka obrazovky), protože senioři v datech J.D. Power zaostávají.
4. **U AI asistentů hodnoťte schopnost úkol dokončit,** ne jen odpovědět. Na tom stojí úspěch Eriky i Forresterových leaderů a právě to chybí asistentům, se kterými jsou lidé nespokojení.

## Upozornění

- **Hodnocení v obchodech s aplikacemi jsou zkreslená.** Banky aktivně vyzývají k hodnocení, takže ratingy kolem 4,8 jsou běžné a málo odlišují. Spolehlivější jsou nezávislé studie (J.D. Power, Forrester, Which?) a analýzy textu recenzí.
- **Některé údaje pocházejí od samotných bank** (Erica 98 %, NameCheck 650 mil. AUD, Monzo 85 % u Which?, Revolut 4,7 na Trustpilotu) a nebyly nezávisle ověřeny. Statistiky stížností (AppImp, analýza recenzí US bank) pocházejí z komerčních nástrojů s menšími vzorky.
- **Plné reporty Forresteru jsou placené.** Vycházím z veřejných tiskových zpráv a blogů.
- **Číslo o QR platbách v ČR (61 %)** pochází ze sekundárního zdroje. Doporučuji ho ověřit přímo u ČBA.
- **České „mezery“ vycházejí z rešerše veřejných zdrojů.** Některé banky (KB, Moneta, Fio) nemusely mít všechny funkce zdokumentované. Před finálním zadáním je dobré rychle ověřit aktuální verze aplikací.
- **Funkce typu přečerpání a výplata předem (Fuliza, SpotMe, MyPay) jsou populární, ale regulatorně i eticky citlivé.** Na hackathonu je vhodné je rámovat odpovědně.

## Sources

1. [What is Settle Up? - Starling Help](https://help.starlingbank.com/joint/topics/uk-payments/what-is-settle-up/)
2. [Bank and Credit Card Apps and Websites Struggle to Stand Out, J.D. Power Finds](https://finance.yahoo.com/news/bank-credit-card-apps-websites-110000226.html)
3. [2025 U.S. Banking and Credit Card Mobile App Satisfaction Studies - JD Power](https://www.jdpower.com/business/press-releases/2025-us-banking-and-credit-card-mobile-app-satisfaction-studies)
4. [www.businesswire.com](https://www.businesswire.com/news/home/20250529002789/en)
5. [Best Practice Report](https://www.forrester.com/report/the-forrester-digital-experience-review-tm-global-mobile-banking-apps-2025/RES189398)
6. [Best Practice Report](https://www.forrester.com/report/the-forrester-digital-experience-review-tm-global-mobile-banking-apps-q4/RES181794)
7. [Forrester: More Than Two-Thirds Of Consumers Expect Their Banking App To Manage All Financial Tasks](https://www.forrester.com/press-newsroom/forrester-more-than-two-thirds-of-consumers-expect-their-banking-app-to-manage-all-financial-tasks/)
8. [Adaptive Mobile Banking: Forrester’s 2025 European Insights](https://www.forrester.com/blogs/the-age-of-adaptive-banking-insights-from-forresters-2025-european-mobile-banking-app-review/)
9. [What Made Bank of America’s Erica So Successful in Customer Support](https://cosupport.ai/articles/bank-of-america-erica-customer-support-success)
10. [bofa ai and digital innovations fuel 30 billion client interactions](https://www.barchart.com/story/news/665679/bofa-ai-and-digital-innovations-fuel-30-billion-client-interactions)
11. [Která bankovní aplikace je nejpřívětivější? Sami uživatelé hodnotí - Finparáda](https://www.finparada.cz/8869-Mobilni-aplikace-hodnoceni.aspx)
12. [Která bankovní aplikace je nejpřívětivější? Sami uživatelé hodnotí - Finparada.cz](https://m.finparada.cz/www.m.finparada.cz/8869-Mobilni-aplikace-hodnoceni.aspx)
13. [Aplikace ČSOB Smart - App Store - Apple](https://apps.apple.com/cz/app/%C4%8Dsob-smart/id1528483245?l=cs)
14. [UPI just had its biggest month ever](https://galific.com/reports/upi-biggest-month-december-2025/)
15. [Starling banking app features](https://www.starlingbank.com/features/)
16. [Monzo Races Past 14 Million Customers Amid Record Growth and Standout Engagement](https://financialit.net/news/banking/monzo-races-past-14-million-customers-amid-record-growth-and-standout-engagement)
17. [Bank of America’s digital prowess keeps growing](https://www.emarketer.com/content/bank-of-america-digital-erica-2025)
18. [Digital Banking Trends In 2025](https://www.bankrate.com/banking/digital-banking-trends-and-statistics/)
19. [Monzo launches industry-first ‘call status’ tool to stall impersonation scams](https://www.lbc.co.uk/article/a054028b0b8a4d9096a68b9163729dcc-DWzfY8_2/)
20. [CommBank strengthens online security as customer scam losses drop by more than 70 percent](https://www.finextra.com/pressarticle/104581/commbank-strengthens-online-security-as-customer-scam-losses-drop-by-more-than-70-percent)
21. [Strengthening scam protection: Introducing Confirmation of Payee](https://www.commbank.com.au/articles/newsroom/2025/07/scam-protection-confirmation-of-payee.html)
22. [V Praze dne 12. února 2026 Strana 1/5 Michaela Průchová Mluvčí skupiny ČSOB](https://www.csob.cz/documents/10710/31521696/tz260212.pdf)
23. [Spořka nabízí spoření přes zaokrouhlování plateb kartou. V pilotu šlo na spořák průměrně 240 Kč měsíčně - Měšec.cz](https://www.mesec.cz/aktuality/sporka-spousti-sporeni-pres-zaokrouhlovani-plateb-kartou-v-pilotnim-rezimu-slo-na-sporak-prumere-240-kc-mesicne/)
24. [Monzo review: Is it the best banking app for travellers?](https://www.finder.com/uk/monzo-review)
25. [Early Direct Deposit Banks: Get Paid 2 Days Sooner](https://www.chime.com/blog/early-direct-deposit-banks/)
26. [KakaoBank tops the Asian Digital Banking race](https://www.weeklyolio.com/p/kakaobank-tops-the-asian-digital-banking-race)
27. [KakaoBank's AI Savings Account Tops 100,000 in First Month - Seoul Economic Daily](https://en.sedaily.com/finance/2026/11/17/kakaobanks-ai-savings-account-tops-100000-in-first-month)
28. [Revolut Wins Euromoney's Best Digital Bank 2025 - First Neobank](https://neobanque.ch/blog/revolut-first-neobank-wins-euromoney-best-digital-bank-2025/)
29. [The world’s best digital bank 2025: Revolut - Euromoney](https://www.euromoney.com/article/183kpq5dv2yo40s4840s0co4o/awards/awards-for-excellence/the-worlds-best-digital-bank-2025-revolut/)
30. [e15.cz - Trendy v placení: Kryptoměna, digitální peněženka nebo platba obličejem. Čím vším se dá zaplatit?](https://www.e15.cz/finexpert/banky-a-ucty/trendy-v-placeni-kryptomena-digitalni-penezenka-nebo-platba-oblicejem-cim-vsim-se-da-zaplatit-1422436)
31. [e15.cz - Platby na kontakt: Prvních šest bank spouští novou službu. K zaplacení stačí telefonní číslo](https://www.e15.cz/platby-na-kontakt)
32. [První banka v Česku umí ověřit, komu posíláte peníze](https://www.penize.cz/osobni-ucty/479304-prvni-banka-v-cesku-umi-overit-komu-posilate-penize)
33. [QR platba na faktuře: jak funguje a jak ji nastavit](https://www.fakturaonline.cz/podnikateluv-pruvodce/technologie-a-inovace/online-fakturace/jak-platit-pomoci-qr-kodu-na-fakture)
34. [Safaricom - M-PESA Journey](https://www.safaricom.co.ke/main-mpesa/about-m-pesa/m-pesa-journey)
35. [e15.cz - Na bankovní trh se blíží nový způsob platby. Bude okamžitá a pomocí telefonu](https://www.e15.cz/byznys/technologie-a-media/na-bankovni-trh-se-blizi-novy-zpusob-platby-bude-okamzita-a-pomoci-telefonu-1399650)
36. [Nubank lança Pix por aproximação pelo aplicativo](https://nu.com/en/newsroom/consumers/nubank-launches-tap-to-pay-pix-through-its-app)
37. [Pix por aproximação começa a ser disponibilizado](https://international.nubank.com.br/pt-br/consumidores/nubank-lanca-pix-por-aproximacao-pelo-aplicativo/)
38. [M-PESA APP MANUAL C2 - Safaricom Internal New App for Consumers Highlights:](https://www.safaricom.co.ke/images/Downloads/M-PESA_App_Manual.pdf)
39. [Starling Reviews](https://ie.trustpilot.com/review/starlingbank.com?page=9)
40. [Starling Reviews](https://www.trustpilot.com/review/starlingbank.com?page=8)
41. [Monzo Reviews](https://au.trustpilot.com/review/www.monzo.com?page=8)
42. [MONETA nově ukáže vaše předplatná a umí zablokovat platby obchodníkovi. Kde je háček](https://www.bankovnipoplatky.cz/moneta-nove-ukaze-vase-predplatna-a-umi-zablokovat-platby-obchodnikovi-kde-je-hacek/)
43. [Které banky ukážou, kde máte kartu uloženou, jaká na ní jsou předplatná a které umožní platby snadno zrušit? - Měšec.cz](https://www.mesec.cz/clanky/ktere-banky-ukazou-kde-mate-kartu-ulozenou-jaka-na-ni-jsou-predplatna-a-ktere-umozni-platby-snadno-zrusit/)
44. [Kdo všechno si strhává peníze z vaší karty? Další banka ukáže přehled](https://www.penize.cz/osobni-ucty/489151-kdo-vsechno-si-strhava-penize-z-vasi-karty-dalsi-banka-ukaze-prehled)
45. [Starling Bank - eutony.net](https://eutony.net/2025/01/10/starling-bank/)
46. [Airbank](https://ib.airbank.cz/static-html/main/IB_MENU_SIDE_SAV_ACC_OVERVIEW/help.html)
47. [Srovnali jsme mobilní aplikace čtyř českých bank. V čem jsou dobré a co můžou ještě zlepšit?](https://www.bellhurry.com/blog/jak-jsou-na-tom-bankovni-aplikace-srovnali-jsme-ctyri-ceske-banky)
48. [Co jsou a jak fungují spořicí obálky?](https://www.csas.cz/cs/caste-dotazy/co-jsou-a-jak-funguji-sporici-obalky)
49. [Revolut Review 2025: Travel Banking Pros, Cons & Hidden Fees](https://askapp.top/apps/revolut)
50. [Monzo Reviews](https://www.trustpilot.com/review/www.monzo.com?page=7)
51. [Monzo Review UK 2026: Is It Worth It? An Honest Opinion](https://coolcuration.com/monzo-review-uk)
52. [Z každé platby kartou pár korun stranou. Spořicí automat spouští další banka - Měšec.cz](https://www.mesec.cz/aktuality/z-kazde-platby-kartou-par-korun-stranou-sporici-automat-spousti-dalsi-banka/)
53. [Spořicí automat už nabízí i Raiffeisenbank. Vylepšila aplikaci](https://www.penize.cz/sporici-ucty/461814-sporici-automat-uz-nabizi-i-raiffeisenbank-vylepsila-aplikaci)
54. [Revolut Review 2026](https://digitalnomads.world/tips/revolut-review/)
55. [카카오뱅크 - APK Download for Android](https://com-kakaobank-channel.en.aptoide.com/app)
56. [KakaoBank](https://spark.mwm.ai/us/apps/kakaobaengkeu/1258016944)
57. [Lotte Duty Free partners with KakaoBank and Jeju Air to roll out 26-week instalment savings programme : Moodie Davitt Report](https://moodiedavittreport.com/lotte-duty-free-partners-with-kakaobank-and-jeju-air-to-roll-out-26-week-instalment-savings-programme/)
58. [www.statista.com](https://www.statista.com/statistics/1250719)
59. [How to Build a Digital Bank like Revolut in 2026?](https://sdk.finance/blog/how-to-build-a-revolut-like-digital-bank/)
60. [Revolut Reviews 2026: What 391K Users Really Think - Revolut](https://checkthat.ai/brands/revolut/reviews)
61. [Android Developers Blog: Battling Impersonation Scams: Monzo’s Innovative Approach](https://android-developers.googleblog.com/2024/03/battling-impersonation-scams-monzo-innovative-approach.html)
62. [How do I know if it's really Monzo calling me?](https://monzo.com/learn/money-safety/is-monzo-calling-me)
63. [CBA urges SME to avoid "too good to be true" investment scams](https://dynamicbusiness.com/topics/news/cba-urges-sme-to-avoid-too-good-to-be-true-investment-scams.html)
64. [Volá vám skutečně pracovník Fio banky? Nově si ho ověříte v mobilní aplikaci - Měšec.cz](https://www.mesec.cz/aktuality/vola-vam-skutecne-pracovnik-fio-banky-nove-si-ho-overite-v-mobilni-aplikaci/)
65. [Volá vám skutečný bankéř z mBank? Můžete si ho rovnou ověřit v aplikaci - Měšec.cz](https://www.mesec.cz/aktuality/vola-vam-skutecny-banker-z-mbank-muzete-si-ho-rovnou-overit-v-aplikaci/)
66. [Opravdu volá bankéř? Snadné ověření nabízí i Fio banka](https://www.penize.cz/osobni-ucty/493380-opravdu-vola-banker-snadne-overeni-nabizi-i-fio-banka)
67. [Opravdu volá vaše banka? Podvod odhalíte snadněji](https://www.penize.cz/osobni-ucty/439429-opravdu-vola-vase-banka-podvod-odhalite-snadneji)
68. [CommBank launches Australian banking first to help prevent payment scams](https://www.commbank.com.au/business/brighter-perspectives/commbank-launches-tech-to-prevent-scams.html)
69. [Scam Protection Boost: Confirmation Of Payee Launches](https://www.miragenews.com/scam-protection-boost-confirmation-of-payee-1488919/)
70. [UniCredit Bank je na ověřování příjemců připravena už dva roky předem - Investujeme.cz - odborný server společnosti Swiss Life Select a.s.](https://www.investujeme.cz/tiskove-zpravy/unicredit-bank-je-na-overovani-prijemcu-pripravena-uz-dva-roky-predem/)
71. [Komu posíláte peníze? Ověřit jméno příjemce umí druhá banka](https://www.penize.cz/osobni-ucty/479608-komu-posilate-penize-overit-jmeno-prijemce-umi-druha-banka)
72. [Okamžité platby začínají fungovat i v eurech. Banky ověří příjemce](https://www.penize.cz/osobni-ucty/493489-okamzite-platby-zacinaji-fungovat-i-v-eurech-banky-overi-prijemce)
73. [Komu posíláte peníze? Banky budou muset ověřit číslo účtu a jméno příjemce](https://www.penize.cz/osobni-ucty/473992-banky-budou-muset-overit-cislo-uctu-a-jmeno-prijemce)
74. [Conta Nubank](https://nubank.com.br/nu/conta)
75. [Skupina ČSOB za 9 měsíců 2026: Silná úvěrová i investiční aktivita klientů pokračuje](https://zpravy.kurzy.cz/881634-skupina-csob-za-9-mesicu-2026-silna-uverova-i-investicni-aktivita-klientu-pokracuje/)
76. [Bankovní virtuální asistenti v nové éře: Jak umělá inteligence mění Kate, George a Anetu - Finparáda](https://www.finparada.cz/9230-Asistenti-ceskych-bank.aspx)
77. [ČSOB spouští novou generaci asistentky Kate. Využívá technologii jako ChatGPT](https://www.e15.cz/finexpert/banky-a-ucty/csob-spousti-novou-generaci-asistentky-kate-vyuziva-technologii-jako-chatgpt-1433235)
78. [Co plánují banky v Česku? Air Bank a Česká spořitelna sází na AI](https://www.e15.cz/finexpert/banky-a-ucty/air-bank-a-ceska-sporitelna-pracuji-na-virtualnim-asistentovi-moneta-chysta-novy-uver-na-bydleni-co-planuji-banky-v-cesku-1421611)
79. [Nový asistent v bance: Jak umělá inteligence zrychluje schvalování hypoték - Finparáda](https://www.finparada.cz/8944-AI-zrychluje-hypoteky.aspx)
80. [Česká spořitelna překopává vizi poboček. Umělá inteligence poradí s vašimi penězi, tepem i tlakem](https://www.e15.cz/byznys/finance-a-bankovnictvi/ceska-sporitelna-prekopava-vizi-pobocek-umela-inteligence-poradi-s-vasimi-penezi-tepem-i-tlakem-1428715)
81. [\[GLOBAL FINANCE AWARDS\] KakaoBank CEO embraces digital wave, innovates financial services - The Korea Herald](https://www.koreaherald.com/article/2735775)
82. [ČSOB Smart s jedinečnou virtuální asistentkou Kate](https://www.zlatakoruna.info/financni-produkty/on-line-aplikace/csob-smart-s-jedinecnou-virtualni-asistentkou-kate-ceskoslovenska-obchodni-banka)
83. [ČSOB rozšiřuje věrnostní program Kate Coin. Chystá další vylepšení](https://www.penize.cz/osobni-ucty/495601-csob-rozsiruje-vernostni-program-kate-coin-chysta-dalsi-vylepseni)
84. [Jak vytvořit QR kód s platebními údaji / Zaplať mi](https://www.airbank.cz/co-vas-nejvic-zajima/jak-vytvorit-qr-kod-s-platebnimi-udaji-zaplat-mi/)
85. [Inside NuCel: The strategy for launching a new vertical in Nubank's app - Building Nubank](https://building.nubank.com/inside-nucel/)
86. [What is Customer Demographics and Target Market of Nubank Company?](https://businessmodelcanvastemplate.com/blogs/target-market/nubank-target-market)
87. [Revolut Review 2026: Fees, Features, Pros & Cons](https://financer.com/review/revolut/)
88. [www.businesswire.com](https://www.businesswire.com/news/home/20251211608475/en)
89. [Chime Review 2026: Checking & Savings](https://bankbonus.com/reviews/chime-bank/)
90. [How MyPay Works on Chime & Cash Advance Alternatives](https://joingerald.com/blog/how-does-mypay-work-on-chime)
91. [A Guide To Using Safaricom’s Fuliza Through Multiple Options](https://thekenyatimes.com/business/how-to-access-fuliza-services-using-different-ways-december/)
92. [Banking apps: what users complain about · App Imp](https://appimp.app/c/banking-apps)
93. [How to Deliver the Best Banking App User Experience on the Market](https://www.europeanbusinessreview.com/how-to-deliver-the-best-banking-app-user-experience-on-the-market/)
94. [Chase Mobile®: Bank & Invest Review Analysis Report](https://insightly.top/shared-app-report/ae026bb358be595934ce73e96155a5f7)
95. [Banking on Feedback: Text Analysis of Mobile Banking iOS and Google App Reviews](https://arxiv.org/pdf/2503.11861)
96. [Chase, Wells Fargo, BofA: 4 Bank Apps Ranked (2026)](https://unstar.app/blog/chase-wells-fargo-bofa-capital-one-banking-apps-ranked-2026)
97. [Instabilidade no app do Nubank deixa clientes sem acesso a valores das caixinhas](https://www.mixvale.com.br/2025/06/21/instabilidade-no-app-do-nubank-deixa-clientes-sem-acesso-a-valores-das-caixinhas/)
98. [Digital Banking Experience Disconnect: Banking UX Problems • UXDA](https://theuxda.com/blog/banking-customers-arent-stupid-your-app-just-confusing)
99. [Starling Reviews](https://ca.trustpilot.com/review/starlingbank.com)
100. [Common Mobile Banking App Complaints & How You Can Fix Them](https://blog.flexcutech.com/blog/complaints-mobile-banking-apps)
101. [Okamžitá platba: jak funguje, limity a ověření příjemce - Aedu.cz](https://aedu.cz/okamzite-platby/)
102. [Účet odjinud už si nepřidáte. Multibanking zruší další banky](https://www.penize.cz/osobni-ucty/477641-ucet-odjinud-uz-si-nepridate-multibanking-zrusi-dalsi-banky)
103. [Jak funguje Platba na kontakt. V Česku už pohodlně pošlete peníze na telefonní číslo](https://mobilmania.zive.cz/clanky/platby-na-kontakt-navod/sc-3-a-1358881/default.aspx)
104. [Bez AI už ani krok. Umělá inteligence bankéřům práci nebere, naopak jí zefektivňuje](https://www.newstream.cz/money/co-vsechno-dela-v-bankach-umela-inteligence)
