# Za hranicemi bankovní aplikace: realizovatelné směry pro Českou spořitelnu (stav k 27. 11. 2026)

Nejsilnější směr pro hackathon České spořitelny není další obrazovka. Je to **Hey George, který věci rovnou připraví a hlídá klienta**. Vede od proaktivní ochrany před podvody přes správu předplatných až k vyhledávání nároků. Platí přitom pravidlo, že AI dělá přípravu, ale peníze se pohnou až po potvrzení klientem v Georgovi. Tento model lze postavit na dnešní regulaci (PSD2/SCA, GDPR, AI Act) i na infrastruktuře ČS. Plně autonomní agenti a open finance bez PSD2 zatím realizovatelní nejsou.

## TL;DR

- **Doporučené Top 3 koncepty:** (1) „Zeptej se George, než zaplatíš“, tedy multimodální ochrana před podvody, (2) „Hey George Akce“, agent pro předplatná a platby s potvrzením v Georgovi, (3) „Nárokomat“, proaktivní vyhledávání státních dávek a úspor napojené na Bankovní identitu. Všechny tři mají reálné precedenty: Starling Scam Intelligence, Air Bank správa uložených karet a Commonwealth Bank Benefits finder.
- **Regulace k listopadu 2026:** platí PSD2/SCA, GDPR, DORA a části AI Actu, včetně transparentnosti chatbotů. PSD3/PSR jsou politicky dohodnuté, ale nejsou v Úředním věstníku a začnou se uplatňovat realisticky až v roce 2028.\[1\] FiDA Komise 4. 11. 2026 zařadila mezi návrhy určené ke stažení.\[2\] Povinnosti pro vysoce rizikové AI (např. credit scoring) se posunuly na 2. 12. 2027.\[3\] Koncepty závislé na PSD3, FiDA nebo EUDI Wallet proto nedoporučujeme.
- **Hackathon:** ČS nabízí přes Erste Developer Portal sandbox s mock daty (až 10 testovacích účtů, testovací klient „Jiří Spokojený“), PSD2 Accounts/Payments API, Corporate API a veřejná API (transparentní účty, kurzy, pobočky).\[4\]\[5\] Funkční a pro porotu uvěřitelný prototyp za 24–48 hodin tak vznikne kombinací sandboxu, komerčního LLM (Hey George sám běží na GPT-4o v Azure) a české řeči.\[6\]

## Executive summary

Česká spořitelna má na českém trhu nejširší digitální základnu. Ke konci roku 2025 měla 4 548 757 klientů, k polovině roku 2026 uvádí 4,6 milionu klientů a 322 poboček.\[7\] George podle tiskové zprávy banky z 19. 5. 2026 používají více než 3 miliony uživatelů\[8\] a v soutěži Zlatá koruna 2026 vyhrál kategorii Bankovní aplikace roku.\[9\] Banka má navíc tři strategická aktiva, která konkurence v této kombinaci nemá:

1. **Hey George** je LLM asistent vyvíjený centrálně pro celou Erste Group (centrální tým sídlí v Praze), postavený na modelech OpenAI. ČS k němu podle Michala Krause „buduje znalostní bázi pro AI, upravuje lokální API a tvoří proaktivní scénáře“.\[10\]
2. **Protipodvodní AI v Georgovi.** Červená varovná obrazovka a zpomalení podezřelé platby podle banky snížily škody klientů o 40 % (o více než 21 milionů Kč).\[11\]
3. **Bankovní identita.** Bank iD používá 5,3 milionu lidí a je napojeno na 550+ firem a 600+ státních služeb. ČS je zakládající banka a akcionář.\[12\]\[13\]

Chybí ale **akce**. Hey George dnes hlavně radí, vysvětluje a naviguje. Sám o sobě výslovně říká, že „není finanční poradce“.\[14\] Hlasový kanál v roce 2025 banka „nevyhodnotila jako prioritní“.\[15\] Konkurence se mezitím posouvá k jednání: ČSOB s Mastercardem v květnu 2026 provedla první platbu kartou iniciovanou AI agentem v Česku\[16\] a Air Bank 12. 10. 2026 spustila hlasovou i textovou „Rychlou navigaci“, která podle Jiřího Suchého, ředitele divize Produkty a inovace Air Bank, „pracuje přibližně se dvěma stovkami cílových míst v aplikaci“.

Největší naléhavost má **bezpečnost**. Podle České bankovní asociace dosáhly škody klientů bank v roce 2025 2,13 mld. Kč při 90 936 útocích. Jen za leden až červenec 2026 to bylo 1,9 mld. Kč, tedy +79 % meziročně, a průměrná škoda vzrostla na 30 335 Kč.\[17\]\[18\]\[19\] Každá nová forma interakce (hlas, agent, messenger) proto musí zlepšovat bezpečnost, ne ji oslabovat.

**Doporučení:** stavět na vzorci *„AI připraví, klient potvrdí v Georgovi“*, který odpovídá dnešní SCA. Na hackathonu ukázat tři scénáře, kde je přínos měřitelný: zachráněné peníze při podvodu, zrušená zbytečná předplatná a vyčerpané nároky. Jako vizi, nikoli doporučení, zmínit agentní platby (Mastercard Agent Pay) a EUDI Wallet.

## Profil České spořitelny

### Kanály a produkty (ověřeno z veřejných zdrojů)

| Oblast | Co funguje dnes | Poznámka / mezera |
|---|---|---|
| George (web + mobil) | Více než 3 mil. uživatelů (ČS, 5/2026). Podle sekundárního zdroje Finemia aktivně v mobilu zhruba 2,4 mil. klientů, v mobilu nebo na webu přes 2,6 mil.\[7\] Vítěz Zlatá koruna 2026.\[9\] | Silná základna. Interakce je stále převážně obrazovková a formulářová. |
| George Store / investice | Investice v Georgovi: k dubnu 2026 přes 780 tis. investujících klientů a přes 520 mld. Kč ve správě.\[8\] Od 18. 5. 2026 zrušen minimální poplatek (nově 0,35 % z objemu).\[20\] | Cíl ČS: do roku 2030 investuje každý čtvrtý občan ČR.\[21\] Detailní obsah George Store jsme veřejně neověřovali. |
| Hey George | LLM asistent (GPT-4/4o, Azure). Pilot v únoru 2025 pro zhruba 100 tis. klientů.\[6\]\[10\]\[15\]\[22\] Podle UX Design Awards 2025 milion uživatelů v beta rolloutu, podle LinkedIn příspěvků manažerů ČS „přes 2 000 000 klientům“.\[23\]\[24\] Na webu ČS je uveden jako standardní funkce George („odpoví na otázky o financích 24/7“).\[25\] | Oficiální tisková zpráva o plném nasazení ani data o počtu konverzací, deflexi či spokojenosti **nebyla veřejně nalezena**. Neumí hlas. Nejpoužívanější je analýza výdajů (Erste, UX Awards).\[24\] |
| Future Lab | Nonstop experimentální pobočka v Praze (Národní/Na Perštýně) od 11/2025 s AI avatary Adam a Eva (ChatGPT, PromethistAI).\[26\] | Šéf distribuce ČS: „Do roku a půl chceme, aby AI avataři zvládli 80 procent operací.“\[26\] To je ambice, ne výsledek. |
| Bezpečnost | AI detekce podvodů v reálném čase, červená varovná obrazovka, −40 % škod.\[11\] | Zaměřeno na transakci, ne na moment manipulace (hovor, inzerát). |
| Bankovní identita | Klienti George ji získali automaticky. Bank iD: 5,3 mil. uživatelů, 118 mil. přihlášení za 5 let.\[27\]\[28\] | ČS ruší Bank iD po 14 měsících nečinnosti, takže část klientů ji ztrácí.\[29\] |
| Věrnostní program | Level Up od 1. 10. 2026: k sazbě 3,8 % na spořicím účtu je potřeba aspoň 10 bodů.\[30\] | Hotový mechanismus pro behaviorální „nudges“. |
| Firmy/OSVČ | George pro malé podnikatele. Erste zmiňuje „working capital simulation“ pro firmy (výroční zpráva 2025).\[31\] | Detailní data o firemních digitálních službách ČS jsme nedohledali. |
| Karty/wallety | Neověřovali jsme nad rámec obecně známého. | **Veřejné informace jsme v rámci výzkumu neověřili**, proto neodhadujeme. |

### API, developer portál a sandbox

- **Erste Group Developer Portal** (developers.erstegroup.com) je centrální vstup pro API všech bank skupiny. Aplikaci lze registrovat jako FAC (přístup k vlastním účtům) nebo TPP (licencovaný poskytovatel). Sandbox „poskytuje mockovaná data“.\[32\]
- **API České spořitelny** podle katalogu a sekundárních zdrojů: PSD2 Account Information API (v1/v4), Accounts Balance API v2, Payment Initiation API v4, Corporate API (sandbox i produkce), Transparent Accounts API v2, Exchange rates, Places (pobočky/ATM), Hypoteční kalkulačka (HypoCalc v2) a podle OpenBankingTracker také „Know your customer API“.\[33\]\[34\]\[35\]\[36\]\[37\]
- **Sandbox bez licence:** podle příručky ČS stačí registrace na EDP, vytvoření aplikace a vygenerování testovacího API klíče. Sandbox podporuje „až 10 testovacích účtů“ a k dispozici je testovací klient „Jiří Spokojený“.\[4\]\[5\] Produkční přístup k účtovým datům třetích osob vyžaduje TPP licenci.\[32\] Veřejná data (transparentní účty, kurzy, místa) potřebují jen API klíč.
- **Bank iD** má samostatný developer portál (developer.bankid.cz).\[38\] Na Erste portálu ČS „identity API“ nenabízí.

### Strategické priority (ČS a Erste)

- **AI-podporované digitální poradenství.** Peter Bosek (CEO Erste) pro Euromoney (CEE's best bank 2026): George chce posunout „na další úroveň“ přidáním AI poradenství, které umožní „proaktivnější a hlubší finanční poradenství pro všechny retailové klienty – včetně těch, kteří nechtějí jednat s osobním poradcem“.\[39\]
- **Finanční zdraví** je podle zprávy dozorčí rady Erste za rok 2025 „klíčovou prioritou“. Erste zároveň „průběžně monitoruje skupinové zavádění AI“.\[31\]
- **AI v rozhodování o cenách a limitech.** Erste nasadila optimalizaci FICO pro pricing a limity úvěrů s nárůstem zisku o 22 % (FICO, duben 2026).\[40\] Pro klientské rozhraní je to méně relevantní, ale ukazuje datovou vyspělost skupiny.
- **Investice** jsou růstový motor (cíl: každý čtvrtý Čech investuje).\[21\]

### Konkurence na českém trhu (2025–2026)

| Hráč | Novinka | Význam pro ČS |
|---|---|---|
| ČSOB | Nová generace Kate na LLM (od dubna, „téměř půl milionu klientů“).\[41\]\[42\] Kate komunikuje hlasem i textem. Pro firmy 12 000+ aktivních uživatelů.\[43\] **První agentní platba kartou v ČR** (Mastercard Agent Pay, Priceless.com, PayOS, passkeys; květen 2026).\[16\]\[44\] | ČSOB vede v hlasu a agentních platbách. ČS vede v rozsahu Hey George a v protipodvodní AI. |
| Air Bank | Rychlá navigace (spuštěna 12. 10. 2026, hlas i text; podle Jiřího Suchého z Air Bank „přibližně dvě stovky cílových míst v aplikaci“). Přehled obchodníků s uloženou kartou a smazání jedním klikem. Aneta „odbaví dvě třetiny všech klientských dotazů“ textem i hlasem.\[45\] | Přímý precedent pro správu předplatných. |
| Komerční banka | Asistentka Ruby, vlastní jazykový model,\[46\] „KB na dálku“ (video). Vishing tvořil v Q1 2026 37 % objemu podvodů u KB.\[45\]\[46\]\[47\] | Video a lidský kontakt jako doplněk. |
| Moneta | Videobankéř (pilot), přechod do cloudu.\[45\]\[46\] | Hybrid člověk + digitál. |
| Revolut, fintechy | V rámci tohoto výzkumu jsme aktuální stav AI funkcí Revolutu v ČR **neověřili**. | Neodhadujeme. |

### Pain pointy klientů ČS – co víme a co ne

- **Systematická veřejná data o pain pointech klientů ČS (NPS, analýza recenzí) jsme nenašli.** Recenze v Google Play obsahují jednotlivé stížnosti, např. na složité první zprovoznění aplikace („to get to work was a nightmare“).\[48\] Jde o anekdotu, ne o reprezentativní data.
- Nepřímé, dobře doložené signály:
  - **Podvody:** viz výše. Vishing a „falešný bankéř“ jsou dominantní scénář. Podle Policie ČR jsou typickou obětí falešného bankéře ženy kolem 45 let, ne senioři, a průměrná škoda u tohoto typu útoku přesahuje 700 tis. Kč.\[47\]\[49\]
  - **Orientace v aplikaci:** samotný vznik Hey George a Rychlé navigace Air Bank ukazuje, že klienti v rozsáhlých aplikacích nenacházejí funkce. Nejčastěji hledají IBAN, QR kód, smlouvy, šablony a PIN.\[50\]
  - **„Spící“ platby:** podle online průzkumu Ipsos pro Air Bank (duben 2026, reprezentativní vzorek 1 018 respondentů) zažilo 41 % Čechů strhnutí platby za předplatné nebo službu, kterou nechtěli, nejčastěji mladí do 26 let (58 %). Alespoň jedno předplatné platí 83 % Čechů.
  - **Teenageři:** v Kybertestu ČBA měli skupina 12–17 let nejhorší výsledek (68 %) oproti 80 % u lidí ve věku 26–55 let.\[17\]
  - **Ztráta identity:** automatické rušení Bank iD po 14 měsících nečinnosti může vylučovat méně aktivní klienty.\[29\]

## Limity současných rozhraní

1. **Reaktivita.** Klient musí vědět, co hledat. I Hey George reaguje převážně na dotaz. Proaktivita existuje hlavně u podvodů (červená obrazovka), ale až v momentě platby, ne v momentě manipulace (telefonát, inzerát, falešná SMS).
2. **Rozdíl mezi radou a akcí.** Asistent poradí, „kde to najdete“, ale nastavení trvalého příkazu, zrušení karty u obchodníka nebo podání žádosti musí klient proklikat sám. Proto má mnoho konverzací nulový efekt.
3. **Kognitivní zátěž a nízká finanční gramotnost.** Hey George vysvětluje pojmy jako RPSN nebo inflaci, což ukazuje, že poptávka existuje.\[14\] Jenže vysvětlení bez kontextu klientových dat zůstává obecné.
4. **Vyloučení.** Hlas chybí u Hey George, takže nevidomí, lidé s motorickým omezením a digitálně méně zdatní klienti mají horší přístup. Pobočky ubývají (z 329 na 322 mezi koncem 2025 a polovinou 2026).\[7\]
5. **Důvěra.** Každý nový kanál (hlas, messenger) je zároveň nový útokový vektor. Podvodníci umí podvrhnout číslo infolinky banky (spoofing) a podle Deníku stále častěji využívají AI a deepfake videa.\[49\]\[51\]

## Nové interakční přístupy, které fungují už dnes

### 1. Agentní AI (jednání jménem klienta)
- **Jak funguje:** LLM agent převede záměr („zruš mi Netflix, už ho nechci“) na posloupnost akcí přes API. V bankovním kontextu je dnes realistický režim *human-in-the-loop*: agent připraví, klient potvrdí.
- **Kde je nasazen:** ČSOB + Mastercard Agent Pay jako pilot (jedna transakce, květen 2026; tokenizovaná karta, passkeys, výslovný souhlas).\[16\]\[44\] Starling Assistant (UK) podle Starlingu vytváří rozpočty, nastavuje spořicí plány, otevírá „Spaces“ a vypisuje inkasa na základě přirozeného jazyka.\[52\] Air Bank nabízí správu uložených karet u obchodníků (bez AI, ale jde o „akční“ precedent).\[53\]
- **Výsledky:** u agentních plateb zatím žádná veřejná data o objemu. Jde o **pilot**.
- **Omezení:** SCA podle PSD2 vyžaduje dva ze tří faktorů. Odpovědnost za chybu agenta není v PSD2 výslovně upravena. Rušení předplatného u obchodníka nemusí jít přes banku (smazání karty platbu technicky zablokuje, smlouvu ale neukončí).
- **ČS:** rozšířit Hey George o „akční karty“ (předvyplněný příkaz nebo blokace), které klient potvrdí standardní autorizací v Georgovi.

### 2. Konverzační a hlasové rozhraní
- **Precedenty:** Bank of America Erica: 24,2 mil. aktivních uživatelů ve 3. čtvrtletí 2026, kumulativně 3,8 mld. interakcí, v roce 2025 téměř 700 mil. interakcí.\[54\]\[55\]\[56\]\[57\] Podle tiskové zprávy Bank of America z 13. 7. 2023 „personalizované a proaktivní insighty nyní tvoří více než 60 % zapojení“ (údaj z roku 2023). Starling Spending Intelligence (Gemini, opt-in, dotazy typu „kolik jsem utratil za jídlo minulý týden“).\[58\]\[59\] Kate (ČSOB) a Aneta (Air Bank) v češtině hlasem i textem.\[43\]\[45\]\[46\]
- **Výsledky:** Starling uvádí, že nasazení Gemini v help centru snížilo předávání na zákaznický servis o 50 %.\[60\] U Kate a Anety jsou dostupná jen provozní čísla (Aneta odbaví dvě třetiny dotazů).\[45\]
- **Omezení:** halucinace, hranice investičního poradenství (Hey George ani Starling neposkytují investiční doporučení) a hlasová autentizace je zranitelná deepfaky.
- **ČS:** hlas jako *vstup* do Hey George (speech-to-text v češtině) je dnes technicky triviální. Citlivé akce ale potvrzovat vždy biometrií v Georgovi, ne hlasem.

### 3. Proaktivní a kontextové bankovnictví
- **Precedenty:** Commonwealth Bank Benefits finder (vyvinutý s Harvard STAR Lab). Do února 2023 klienti nárokovali přes 1 mld. AUD a do konce roku 2022 zahájili 2,2 mil. žádostí. Původní očekávání bylo zhruba 150 mil. AUD ročně.\[61\]\[62\]\[63\] Erica podle BofA aktivně upozorňuje na duplicitní platby a zdražení předplatného.\[64\]
- **Omezení:** únava z notifikací, vnímání jako „prodejní tlak“ a GDPR (účel zpracování, profilování podle čl. 22).
- **ČS:** Hey George už má „proaktivní scénáře“ v plánu, takže infrastruktura existuje.\[10\]

### 4. Embedded finance
- **Dnes v ČR:** Bank iD v e-shopech (ověření věku u 240 tis. nakupujících na 500+ e-shopech v roce 2025), na katastru (630+ tis. lidí v H1 2026), v bezobslužných prodejnách 24/7 (200+). Vodafone má Bank iD nasadit v e-shopu v H2 2026.\[28\]\[38\]
- **Messengery (WhatsApp apod.):** jako kanál pro transakce silně nedoporučujeme kvůli podvodům a SCA. Nanejvýš pro upozornění bez citlivých dat. Ani precedenty v ČR jsme nenašli.
- **ČS:** nejsilnější dnešní „embedded“ aktivum je Bank iD. Embedded není nutně „banka v messengeru“, ale „banka jako důvěryhodná identita a souhlas všude“.

### 5. Nositelná elektronika a zařízení
- Platby hodinkami a telefonem jsou běžné, ale málo inovativní. Konkrétní data o wearables u ČS jsme **neověřili**. Jako hackathonové téma má nízký „wow“ a nízký dopad. Jedinou rozumnou nadstavbou jsou haptická nebo hodinková upozornění na podezřelou platbu.

### 6. Behaviorální a emoční design
- **ČS:** spolupracuje s behaviorálními experty (Daniela Pešková, členka představenstva)\[65\] a má program Level Up s body jako hotový mechanismus odměn. Hey George používá tón „partnera“.
- **Precedenty:** Starling Scam Intelligence (Gemini vyhodnotí inzerát z marketplace) podle případové studie Google Cloud „už zvýšil míru, s jakou zákazníci ruší platby na marketplace, o 300 %“. CIO Starlingu Harriet Rees na Money20/20 USA uvedla, že nástroj „dokáže identifikovat 90 % znaků podvodu na libovolném obrázku“. Klíčový princip je „frikce ve správný moment“, tedy zpomalit platbu, ne ji zakázat.

### 7. Další přístupy
- **AI avatary na pobočce** (ČS Future Lab) jsou pilot,\[26\] mají vysokou vizuální hodnotu, ale omezený dopad na digitální interakci.
- **Asistovaná digitalizace** (Air Bank CAir: asistent s tabletem provede klienta jeho vlastní aplikací) je ověřený přístup pro digitálně méně zdatné klienty.\[66\]\[67\]
- **Delegovaný přístup pro blízké osoby** (např. „strážce“ seniora s právem jen vidět a být upozorněn) je silná potřeba. Konkrétní české precedenty jsme v tomto výzkumu nedoložili, proto ho řadíme jako koncept s nutností ověření.

## Mapa příležitostí

Škála 1–5 (5 = nejlepší, u regulatorního rizika uvádíme slovní hodnocení).

| # | Koncept | Cílový klient a problém | Inov. | Realiz. dnes v ČS (zdůvodnění) | Hackathon | Dopad | Regulatorní riziko | Precedenty | Proč by v ČS nemusel fungovat |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **„Zeptej se George, než zaplatíš“** – klient nahraje screenshot inzerátu, SMS nebo přepis hovoru a AI vyhodnotí znaky podvodu, propojené s červenou obrazovkou | Všichni, zejména 36–55 let a teenageři; vishing, falešné inzeráty | 4 | 5 – navazuje na existující fraud engine a Hey George, nevyžaduje platební API | 5 | 5 | Nízké (GDPR: citlivý obsah screenshotů) | Starling Scam Intelligence; ČS červená obrazovka | Podvodník klienta instruuje, aby nic nekontroloval. Falešně negativní výsledek může vytvořit falešný pocit bezpečí. |
| 2 | **Hey George Akce** – z konverzace vznikne předvyplněný příkaz, trvalý příkaz, blokace nebo smazání uložené karty; potvrzení v Georgovi | Retail; mezera mezi radou a akcí | 4 | 4 – Hey George už využívá lokální API; nutná integrace na platební služby\[10\] | 4 | 4 | Střední (SCA zůstává v Georgovi; chyba AI v návrhu) | Starling Assistant; Air Bank uložené karty; ČSOB Kate („řekněte, ona to udělá“)\[43\] | Riziko chybného příjemce či částky; klienti nemusí AI svěřit peníze. |
| 3 | **Hlídač předplatných** – detekce opakovaných plateb, zdražení a „spících“ služeb; jedním krokem zablokovat kartu u obchodníka | Retail, mladí; 41 % Čechů zažilo nechtěné stržení, u mladých do 26 let 58 % (Ipsos pro Air Bank, 4/2026) | 3 | 4 – transakční data má ČS; blokace u obchodníka závisí na karetních schématech | 5 | 4 | Nízké | Air Bank; BofA Erica | Zablokování karty neukončí smlouvu; dluh u obchodníka zůstává. |
| 4 | **Nárokomat** – proaktivní hledání státních dávek a příspěvků (např. Superdávka, příspěvek na bydlení) a podání přes Bank iD | Rodiny, senioři, lidé ve finanční tísni; nevyčerpané nároky | 4 | 3 – odhad nároku z transakcí je citlivý (GDPR, profilování); podání přes Bank iD existuje (Superdávka 37 % online žádostí)\[28\] | 4 | 5 | Střední (GDPR čl. 22, nutný opt-in) | CBA Benefits finder (1 mld. AUD) | Česká pravidla dávek jsou složitá; chybný odhad poškodí důvěru; nutná spolupráce s MPSV/ÚP. |
| 5 | **Cashflow radar pro OSVČ** – predikce zůstatku, upozornění na DPH, zálohy na pojištění a splatnost faktur | OSVČ a mikrofirmy | 3 | 4 – transakční data + Corporate API; Erste má „working capital simulation“\[31\] | 4 | 4 | Nízké | Erste working capital simulation; ČSOB Kate pro firmy (12 000+ uživatelů)\[43\] | Data z účetního softwaru banka nemá (FiDA neprojde); přesnost predikce. |
| 6 | **Hlasový Hey George (read-only + navigace)** – mluvené dotazy v češtině, odpovědi hlasem, bez transakcí | Senioři, zrakově postižení, řidiči | 3 | 4 – české STT/TTS je komerčně dostupné; ČSOB i Air Bank hlas mají | 5 | 3 | Nízké až střední (AI Act: označení chatbota) | Kate, Aneta, Air Bank Rychlá navigace | ČS hlas v roce 2025 neměla jako prioritu;\[15\] malé „wow“ bez akcí. |
| 7 | **Rodinný strážce** – delegovaný přístup typu „vidět a být upozorněn“ pro důvěryhodnou osobu seniora | Senioři a jejich děti | 4 | 3 – vyžaduje produktové a právní řešení plné moci a GDPR | 3 | 4 | Střední (zmocnění, ochrana dat) | Mezinárodní precedenty jsme v tomto výzkumu nedoložili | Riziko zneužití uvnitř rodiny; senioři podle dat nejsou hlavní obětí vishingu. |
| 8 | **Včasné varování ve finanční tísni** – detekce rizika (opakovaný debet, propad příjmů) a nabídka splátkového kalendáře | Klienti ve finanční tísni | 3 | 3 – data má ČS; citlivé z hlediska profilování a pozdějších AI Act povinností pro úvěry | 3 | 5 | Střední až vysoké (od 12/2027 high-risk, pokud jde o hodnocení úvěruschopnosti) | Erste: optimalizace v oblasti vymáhání (FICO)\[68\] | Stigmatizace a pocit sledování; nutná spolupráce s dluhovým poradenstvím. |
| 9 | **Teen money coach** – gamifikovaný kouč (Level Up body), kybertesty, simulace podvodů | Teenageři 12–17 | 3 | 4 – Level Up existuje | 5 | 3 | Nízké (souhlas zákonných zástupců) | ČBA Kybertest | Teenageři nemusí bankovní aplikaci otevírat; nutná atraktivita obsahu. |
| 10 | **Life-event balíčky** (stěhování, dítě, první práce) – AI rozpozná událost a nabídne kontrolní seznam včetně Bank iD podání | Retail | 3 | 3 – rozpoznání události z dat je citlivé | 4 | 3 | Střední (GDPR) | CBA Customer Engagement Engine | Vnímání jako „big brother“ nebo prodejní tlak. |
| 11 | **Agentní platba kartou** (Mastercard Agent Pay / Visa Intelligent Commerce) | Digitálně zdatní | 5 | 2 – pilot u konkurence, závislý na schématech a obchodnících | 2 | 2 | Střední až vysoké (odpovědnost, SCA) | ČSOB + Mastercard (1 transakce, 5/2026)\[16\] | Nízká akceptace obchodníky; nejasná odpovědnost. **Nedoporučujeme do Top 3.** |
| 12 | **George v messengeru** (WhatsApp/Messenger) | Mladí | 3 | 1 – bezpečnost, SCA, spoofing | 3 | 2 | Vysoké | Nenalezen relevantní český precedent | Nový podvodný vektor; **nedoporučujeme.** |
| 13 | **Open finance agregátor nad rámec plateb (penze, pojištění)** | Afluentní klienti | 3 | 1 – FiDA je určená ke stažení; jen bilaterální dohody\[2\] | 2 | 3 | Vysoké (právní základ chybí) | – | **Vyřazeno: závisí na neúčinné nebo stahované regulaci.** |
| 14 | **Onboarding přes EUDI Wallet** | Všichni noví klienti | 4 | 1 – česká peněženka zatím není hotová; povinnost akceptace bankami od konce 2027 | 2 | 3 | Vysoké (regulace ještě není účinná v praxi) | – | **Vyřazeno z doporučení.** |

## Top 3 koncepty pro hackathon ČS

### 1. „Zeptej se George, než zaplatíš“ (Scam Second Opinion)

**User story:** Jako klientka, které právě volá „bezpečnostní oddělení banky“, chci jedním tlačítkem v Georgovi (nebo hlasem „Georgi, je tohle podvod?“) zjistit, jestli jde o podvod, abych nepřišla o úspory.

**„Wow“ moment pro porotu:** Live demo. Někdo z týmu „volá“ jako falešný bankéř. Klientka během hovoru přepne do Hey George, nadiktuje, co jí volající říká, a George během několika sekund odpoví klidným hlasem: *„Tohle je typický podvod ‚bezpečný účet‘. Česká spořitelna vás nikdy nepožádá o převod na jiný účet. Zavěste. Chcete, abych vám zablokoval odchozí platby na 24 hodin?“* Druhý scénář: screenshot inzerátu z marketplace, který George vyhodnotí jako rizikový. Pro kontext v pitchi: Starling u podobného nástroje uvádí +300 % ve zrušených rizikových platbách.\[69\]

**Napojení na ČS:** vstup přes Hey George (chat + nový hlasový vstup). Výstup napojený na existující červenou obrazovku a fraud engine (signál „klient je v aktivní manipulaci“ zvýší riziko další platby). Volitelně akce „dočasná pojistka“ (zablokování odchozích plateb nebo snížení limitu), potvrzená biometrií v Georgovi.

**Technický stack:** Azure OpenAI (GPT-4o nebo novější, stejná rodina jako Hey George) s multimodálním vstupem (obrázek, text). Česká STT/TTS (např. Azure Speech). RAG nad veřejnými varováními ČBA, Policie ČR a ČS. Sandbox ČS (PSD2 Accounts) pro zobrazení účtu a simulaci pojistky. Frontend v React Native nebo webu stylizovaný jako George.

**Rozsah MVP (48 h):** 3 typy vstupu (hlasový popis hovoru, screenshot SMS, screenshot inzerátu). Klasifikace do 8–10 známých scénářů (falešný bankéř, bezpečný účet, investiční podvod, falešný kupující, „kamarád v nouzi“ atd.). Doporučený krok a tlačítko „pojistka“.

**Cesta k pilotu (6–12 měsíců):** (1) interní test s fraud týmem nad historickými případy, (2) zapojení do Hey George jako nového intentu, (3) A/B pilot u 5–10 % klientů s metrikami zachráněná částka, false positive rate a CSAT, (4) napojení signálu na fraud engine. Regulace: nejde o vysoce rizikovou AI podle Annexu III (detekce podvodů je z credit scoringu výslovně vyňata).\[70\] Platí transparentnost chatbota a GDPR (DPIA kvůli obsahu screenshotů).

**Rizika a odpovědi:**
- *Falešně negativní výsledek („George řekl, že je to OK“)* → George nikdy neříká „bezpečné“, jen „nenašel jsem známé znaky, přesto…“. Pro pochybné případy nabídne vždy přepojení na lidský fraud tým.
- *Podvodník klienta navede, aby George nepoužíval* → kombinovat s pasivní detekcí (červená obrazovka) a s kampaní „Než zaplatíš, zeptej se George“.
- *Deepfake hlas banky* → George sám nikdy nevolá; klient vždy iniciuje kontakt v aplikaci.

### 2. Hey George Akce: „Řekni a já připravím“ (subscription & payment agent)

**User story:** Jako zaneprázdněný klient chci napsat nebo říct „ukaž mi, co mi pravidelně strhávají, a zruš to, co nepoužívám“ a dostat hotový návrh, který jen potvrdím.

**„Wow“ moment:** George odpoví: *„Platíte 7 opakovaných služeb za 1 284 Kč měsíčně. Dvě z nich jste 4 měsíce nepoužil a jedna zdražila o 30 %. Chcete u nich zablokovat uloženou kartu?“* Klient řekne „ano, ty dvě“ a otevře se standardní potvrzení v Georgovi (Face ID). Druhý příklad: „pošli mámě 2000 jako minulý měsíc“ vytvoří předvyplněný příkaz z historie, ale k odeslání vyžaduje autorizaci.

**Napojení na ČS:** Hey George (konverzace), transakční historie z Georgova backendu, platební příkazy přes existující interní API (v prototypu PSD2 Payment Initiation API v sandboxu) a správa karet. Body Level Up za „finanční úklid“.

**Technický stack:** LLM s function calling a tool-use. Pravidlová detekce opakovaných plateb (merchant, perioda, částka) doplněná o LLM vysvětlení. Erste sandbox: Accounts + Payment Initiation (mock data, 10 testovacích účtů).\[4\] Syntetická transakční data pro demo. Potvrzovací obrazovka napodobující George.

**Rozsah MVP:** detekce předplatných, 3 nástroje (vytvořit příkaz, trvalý příkaz, blokovat kartu u obchodníka), povinné potvrzení a audit log „co AI navrhla a co klient potvrdil“.

**Cesta k pilotu:** začít jen u nízkorizikových akcí (zobrazení, blokace karty u obchodníka), pak předvyplněné příkazy k vlastním a známým příjemcům a teprve potom ostatní. Plná SCA zůstává v Georgovi, takže z pohledu PSD2 nejde o novou autentizaci. Precedent pro „akci“ existuje na trhu (Air Bank uložené karty, ČSOB Kate „ona to za vás udělá“).\[43\]

**Rizika a odpovědi:**
- *Chyba LLM v příjemci nebo částce* → LLM nikdy nevyplňuje IBAN volně, jen z historie nebo ze šablon. Před potvrzením se zobrazí rozdíly oproti minulé platbě.
- *Smazání karty neukončí smlouvu* → George vygeneruje i text výpovědi nebo odkaz na zrušení u obchodníka.
- *Prompt injection přes texty transakcí* → oddělit data od instrukcí a nástroje mít s whitelistovanými parametry.

### 3. Nárokomat: proaktivní hledání nároků a úspor

**User story:** Jako rodič na rodičovské nebo jako senior s nízkým důchodem chci, aby mi banka sama řekla, na jaké příspěvky mohu mít nárok, a pomohla mi o ně požádat. Nechci se v tom sám vyznat.

**„Wow“ moment:** George (s opt-inem) zjistí z příchozích plateb změnu životní situace, například narození dítěte nebo pokles příjmu. Položí čtyři jednoduché otázky (jako Benefits finder) a ukáže: *„Můžete mít nárok na tyto podpory. Odhadem až X Kč měsíčně.“* Na konci je tlačítko „Požádat přes Bankovní identitu“. Pro pitch: CBA Benefits finder pomohl klientům nárokovat přes 1 mld. AUD a původně počítal se 150 mil. AUD ročně.\[61\]\[63\]

**Napojení na ČS:** Hey George (konverzace), Bank iD (přihlášení na státní portály: Superdávka už 37 % online žádostí přes Bank iD, 600+ státních služeb),\[12\]\[28\] cíle finančního zdraví ČS a Level Up.

**Technický stack:** pravidlový engine se zjednodušenými podmínkami 5–8 dávek (zdroj: veřejná pravidla MPSV), LLM pro vysvětlení v jednoduché češtině, sandbox ČS pro transakční signály a Bank iD sandbox (developer.bankid.cz) pro demo přihlášení.

**Rozsah MVP:** 5 dávek nebo úspor (např. příspěvek na bydlení, Superdávka, přídavek na dítě, případně levnější tarif energie podle výdajů), dotazník o 4 otázkách, odhad v pásmech („pravděpodobně / možná / ne“) a deeplink na podání.

**Cesta k pilotu:** začít jako *dotazník iniciovaný klientem* (bez profilování), poté opt-in proaktivní upozornění. Validace pravidel s MPSV/ÚP nebo neziskovým partnerem (např. dluhové poradny). Metriky: zahájené žádosti a odhad vyplacených částek.

**Rizika a odpovědi:**
- *Chybný odhad nároku* → komunikovat jako „možný nárok“, ne „máte nárok“, a vždy odkázat na oficiální kalkulačku nebo úřad.
- *GDPR a profilování* → výslovný opt-in, DPIA a žádné rozhodnutí s právním účinkem (jen informace).
- *Změny pravidel dávek* → pravidla ve verzovaném konfiguračním souboru, ne v promptu.
- *Proč nemusí fungovat:* česká dávková agenda je fragmentovaná a průběžně reformovaná. Bez partnera na straně státu zůstane u informací bez napojení na podání.

## Specifické skupiny klientů ČS

- **Senioři:** potřebují hlas, jednoduchost a ochranu. Data ale ukazují, že typickou obětí vishingu je žena kolem 45 let, ne senior. Ochrana by tedy neměla být „jen pro seniory“. Vhodné koncepty: #1, #6, #7.
- **Děti a teenageři:** nejhorší skóre v Kybertestu (68 %). Vhodné koncepty: #9 a #1 (gamifikované simulace podvodů).
- **Lidé se zdravotním postižením:** hlasový vstup a výstup v češtině (#6) a jednoduchý jazyk. Specifická data o přístupnosti George jsme **nenašli**, doporučujeme audit.
- **Digitálně méně zdatní:** asistovaná digitalizace (Air Bank CAir), Future Lab avatary a hlas. Pozor na rušení Bank iD po nečinnosti.
- **OSVČ a malé firmy:** #5 Cashflow radar. ČSOB má s Kate pro firmy 12 000+ aktivních uživatelů, takže poptávka existuje.\[43\]
- **Klienti ve finanční tísni:** #4 Nárokomat a #8 Včasné varování. Citlivé, nutný opt-in a spolupráce s dluhovým poradenstvím.

## Regulace, bezpečnost a důvěra (stav k listopadu 2026)

| Předpis | Stav k 27. 11. 2026 | Dopad na koncepty |
|---|---|---|
| **PSD2 + RTS SCA** | Účinné | Každá platba vyžaduje SCA (2 ze 3 faktorů). Model „AI připraví, klient potvrdí v Georgovi“ je plně v souladu. |
| **PSD3 / PSR** | Politická dohoda 27. 11. 2025, finální kompromisní texty 23. 4. 2026, postoj Rady v prvním čtení 29. 10. 2026. V Úředním věstníku zatím nevyšly. Aplikace 21 měsíců po vstupu v platnost (ověření příjemce 27 měsíců), realisticky v roce 2028.\[1\]\[71\] | Pravidla o vracení peněz obětem podvodů typu impersonace, rozšíření kontroly jméno–IBAN a dashboardy oprávnění **nejsou účinné**.\[72\] Nelze na nich stavět, jen se na ně připravovat. |
| **FiDA (open finance)** | Pracovní program Komise na rok 2027 (4. 11. 2026) uvádí FiDA mezi 18 návrhy, které Komise „zamýšlí stáhnout do šesti měsíců“.\[2\] | Koncepty s penzijními, pojistnými a investičními daty třetích stran jsou vyřazeny. Zbývají GDPR přenositelnost a bilaterální dohody.\[2\] |
| **AI Act** | Zakázané praktiky a AI gramotnost od 2/2025, GPAI od 8/2025. Digital Omnibus (nařízení (EU) 2026/1744) je účinný od 27. 7. 2026 a posunul high-risk povinnosti pro Annex III (vč. hodnocení úvěruschopnosti) na 2. 12. 2027 a pro Annex I na 2. 8. 2028. Transparentnost chatbotů a deepfaků Omnibus neposunul.\[3\] | Hey George musí být označen jako AI (ČSOB to dělá uvítací obrazovkou).\[42\] Koncept #8 se dostane do režimu high-risk, pokud bude hodnotit úvěruschopnost. Detekce podvodů je z credit scoringu výslovně vyňata.\[70\] |
| **GDPR** | Účinné | Proaktivní scénáře (#4, #8, #10) vyžadují jasný právní základ, opt-in a DPIA. Čl. 22 brání plně automatizovaným rozhodnutím s právním účinkem. |
| **eIDAS 2.0 / EUDI Wallet** | Státy mají peněženku nabídnout do konce roku 2026 (zdroje uvádějí různá data v listopadu a prosinci 2026). Banky ji musí akceptovat od konce roku 2027.\[73\]\[74\]\[75\] Česká peněženka podle médií včas nebude, tendr na klientskou část v roce 2026 probíhal. eDoklady mají 1 000 088 uživatelů.\[73\]\[76\] | Na hackathonu jen jako vize. Bank iD je dnešní realita. |
| **DORA** | Účinné od 17. 1. 2025 | Externí LLM (OpenAI/Azure) je ICT služba třetí strany: registr smluv, exit strategie a testování odolnosti. |
| **ČNB** | Specifické metodiky ČNB k GenAI asistentům jsme v rámci výzkumu **nenašli**. | Doporučujeme konzultaci s compliance ČS. Neodhadujeme. |

### Autentizace a souhlas bez obrazovky nebo při jednání agenta
1. **Oddělit záměr od autorizace:** hlas nebo chat slouží jen pro záměr, autorizace probíhá vždy v Georgovi (biometrie zařízení). To je dnes nejbezpečnější a regulatorně čistá cesta.
2. **Mandáty s limity:** trvalé příkazy a limity jsou již dnes „předautorizované“ akce. Agent v jejich rámci smí jednat jen tam, kde to umožňuje existující výjimka nebo mandát.
3. **Tokenizace a passkeys pro agentní platby:** model Mastercard Agent Pay (token, výslovný souhlas, biometrie přes passkeys). V ČR je zatím pilot.\[44\]
4. **Hlasová biometrie** jako jediný faktor se **nedoporučuje** kvůli deepfakům.

### Rizika a zmírnění
- **Podvody a deepfaky:** banka nikdy sama nevolá s výzvou k akci. Kontakt iniciuje klient v aplikaci. Červená obrazovka a „pojistky“ (dočasné limity) pomáhají.
- **Chyby AI:** strukturované nástroje místo volného textu, whitelisty, audit logy, lidská eskalace a měření kvality řešení, ne jen „containment“ (poučení z Klarny).
- **Odpovědnost:** PSD2 neřeší AI agenta. Dokud klient potvrzuje každou platbu, zůstává odpovědnostní rámec beze změny.

## Technická proveditelnost pro hackathon (24–48 h)

**Zdroje dat a API:**
- Erste Developer Portal: registrace, aplikace a testovací API klíč. ČS sandbox (PSD2 Accounts/Balance, Payment Initiation v4, Corporate API) s až 10 testovacími účty a testovacím klientem „Jiří Spokojený“ přes sandbox-idp.\[4\]\[5\]
- Veřejná API ČS: Transparent Accounts (reálná data transparentních účtů, vhodná pro dema), Exchange rates, Places (pobočky a bankomaty pro geolokační scénáře), HypoCalc.\[34\]\[35\]\[77\]
- Bank iD: samostatný developer portál pro demo přihlášení a ověření identity.\[38\]
- Syntetická transakční data: vygenerovat 6–12 měsíců realistických transakcí (předplatná, nájem, výplata, dávky) a kategorie popsat v češtině.

**AI vrstva:**
- LLM: Azure OpenAI (konzistentní s Hey George, který běží na GPT-4o v Azure),\[6\] případně Google Gemini (Starling).
- Řeč: komerční česká STT/TTS (např. Azure Speech).
- Orchestrace: function calling se 3–5 nástroji a jednoduchý RAG nad veřejnými texty ČS, ČBA a Policie.

**Jak být uvěřitelní pro porotu:**
- Napodobit vizuální jazyk George (modrá paleta, karty, tón „partnera“) podle veřejně dostupných screenshotů. Existenci veřejného design systému George jsme **neověřili**.
- Prototyp zobrazit jako **nový intent v Hey George**, ne jako samostatnou aplikaci. Porota uvidí, že jde o rozšíření, ne o paralelní produkt.
- Vždy ukázat potvrzovací krok (SCA) a audit log, protože porota z banky bude řešit bezpečnost.
- Prezentovat metriky pilotu (zachráněné Kč, zrušená předplatná, zahájené žádosti) a cestu přes existující týmy (Hey George tým v Praze, fraud tým, Bank iD).

## Případové studie

1. **Bank of America – Erica (USA, ověřeno v praxi):** 24,2 mil. aktivních uživatelů ve 3. čtvrtletí 2026, 3,8 mld. interakcí od roku 2018, téměř 700 mil. interakcí v roce 2025.\[54\]\[55\]\[56\]\[57\] BofA uvádí, že přes 98 % klientů najde, co hledá.\[78\] Podle tiskové zprávy BofA z 13. 7. 2023 tvořily personalizované a proaktivní insighty (duplicitní platby, zdražení předplatného) „více než 60 % zapojení“. Poučení: proaktivita a dlouhodobé iterace, ne jednorázový launch.
2. **Starling Bank – Spending Intelligence, Scam Intelligence, Starling Assistant (UK, ověřeno a pilot):** Gemini na Google Cloud, opt-in a bez finančního poradenství.\[59\]\[79\] Scam Intelligence vznikl za 4 týdny a podle Google Cloud zvýšil rušení plateb na marketplace o 300 %. Podle CIO Harriet Rees identifikuje 90 % znaků podvodu na obrázku. AI v help centru snížila předávání na zákaznický servis o 50 %. Poučení: rychlé iterace a jasné regulatorní hranice. Pozor: podle Financial Times (převzal PYMNTS 3. 7. 2026) Starlingu za fiskální rok končící březnem 2026 klesly výnosy o 6 % na 887 mil. GBP a zisk před zdaněním o 3 % na 217 mil. GBP. Banka zároveň ruší zhruba 130 míst (asi 3 % z více než 4 000 zaměstnanců), takže AI není automaticky obchodní úspěch.
3. **Commonwealth Bank – Benefits finder (Austrálie, ověřeno):** vyvinuto s Harvard STAR Lab, přes 1 mld. AUD nárokovaných benefitů do února 2023, 2,2 mil. zahájených žádostí a přes 320 benefitů včetně firemních.\[61\]\[62\]\[63\]\[80\] Poučení: proaktivita, která klientovi přináší peníze, ne produkt.
4. **ČSOB + Mastercard – Agent Pay (ČR, pilot):** první platba kartou iniciovaná AI agentem v ČR (květen 2026). Tokenizovaná karta, passkeys a výslovný souhlas.\[16\]\[44\] Poučení: technologie existuje, ale jde o jednu demonstrační transakci, ne o produkt.
5. **Air Bank – Rychlá navigace a správa uložených karet (ČR, ověřeno):** hlasová i textová AI navigace (spuštěna 12. 10. 2026), která podle Jiřího Suchého z Air Bank „pracuje přibližně se dvěma stovkami cílových míst v aplikaci“. Přehled obchodníků s uloženou kartou a smazání jedním klikem. Poučení: malé, praktické AI funkce s jasným úkolem.
6. **Česká spořitelna – červená varovná obrazovka (ČR, ověřeno):** AI detekce a zpomalení platby snížily škody o 40 % (o více než 21 mil. Kč).\[11\] Poučení: správně načasovaná frikce funguje.

## Anti-patterny: co selhalo a proč

1. **Klarna, „AI místo lidí“:** Klarna v roce 2024 tvrdila, že AI asistent dělá práci 700 agentů. V květnu 2025 CEO Sebastian Siemiatkowski pro Bloomberg připustil „nižší kvalitu“ a firma začala znovu nabírat lidi.\[81\]\[82\] Klarna to sama označuje za rebalancování, ne obrat, ale poučení platí: měřit vyřešení problému, ne „containment“, a vždy nabídnout člověka.\[83\]\[84\]
2. **Asistent, který umí recepty lépe než bankovnictví:** penize.cz při testu raného Hey George (2025) zjistil, že „s receptem poradí výborně“, ale „s praktickým využitím v bankovnictví je to někdy horší“.\[15\] Poučení: zúžit doménu a dát asistentovi akce, ne konverzaci o všem.
3. **Asistent jako prodejní kanál:** ČSOB při uvedení Kate deklarovala cíl zvýšit pravděpodobnost přijetí nabídek až na 30 % a sama připustila, že ji klienti mohou vnímat jako vnucování produktů.\[85\] Poučení: proaktivita musí přinášet hodnotu klientovi (ochrana, úspory, nároky), jinak ztrácí důvěru.
4. **Nové kanály jako nové útokové vektory:** spoofing čísel bank a deepfaky ukazují, že každý hlasový nebo messengerový kanál, kterým banka *sama oslovuje* klienta, lze napodobit. Poučení: kontakt iniciuje klient, banka sama nevolá s výzvou k akci.
5. **Stavění na neúčinné regulaci:** FiDA, s níž počítala řada open finance strategií, Komise navrhla stáhnout.\[2\] Poučení: realizovatelnost dnes je jen to, co stojí na PSD2, GDPR a bilaterálních dohodách.

## Caveats

- Řada čísel o Hey George (1 mil., resp. 2 mil. uživatelů) pochází z UX Design Awards a LinkedIn příspěvků manažerů ČS, ne z oficiální tiskové zprávy.\[23\]\[24\] Data o počtu konverzací, deflexi a spokojenosti **nejsou veřejná**.
- Údaj o aktivních uživatelích George v mobilu (zhruba 2,4 mil.) pochází ze sekundárního zdroje (Finemia).\[7\]
- Konkrétní data o kartách a walletech ČS, o přístupnosti George a o metodikách ČNB k GenAI jsme v tomto výzkumu nedohledali, proto je neodhadujeme.
- Data vydání EUDI Wallet se ve zdrojích liší (21. 11., 24. 12. či 31. 12. 2026). Shodují se, že česká peněženka zpožděná.\[73\]\[74\]\[75\]
- Výsledek Starling Scam Intelligence (+300 %) pochází z případové studie Google Cloud, tedy z dodavatelského zdroje.
- Hodnocení v mapě příležitostí je expertní úsudek autora na základě citovaných faktů, nikoli měření.

## Sources

1. [PSD3 guide: When it applies and what changes for EU payments](https://paymentexpert.com/2026/11/10/psd3-guide-eu-payment-services/)
2. [Brussels Shelved Open Finance. Europe's Fintechs Will Have to Build It Without a Law. — FinTech Weekly](https://www.fintechweekly.com/magazine/articles/fida-withdrawal-open-finance-europe-2026)
3. [Digital Omnibus on AI: the amended EU AI Act timetable](https://bratby.law/digital-omnibus-ai-high-risk-delay/)
4. [www.csas.cz/en Page 1/8 Česká spořitelna: API handbook Table of contents](https://cdn0.erstegroup.com/content/dam/cz/csas/www_csas_cz/dokumenty/obecne/how-to-connect-to-api-of-cs.pdf)
5. [User authentication / authorization](https://developers.erstegroup.com/docs/tutorial/csas-how-to-call-api)
6. [Jmenuje se Hey George. Nový virtuální poradce České spořitelny](https://feedit.cz/2024/12/02/jmenuje-se-hey-george-novy-virtualni-poradce-ceske-sporitelny/)
7. [Česká spořitelna: kdo ji vlastní a proč není největší bankou v Česku - Finemia.cz](https://www.finemia.cz/ceska-sporitelna/)
8. [Investování přes George: recenze, ETF a poplatky Spořitelny](https://www.investnews.cz/ceska-sporitelna-george-investovani-recenze/)
9. [Michal Kraus - AI that truly creates value, not dizzying costs.](https://www.linkedin.com/in/michal-kraus-digitalandfintech/)
10. [Hey, George! Spořitelna spouští chatbota v mobilní aplikaci](https://www.penize.cz/osobni-ucty/459970-hey-george!-sporitelna-spousti-chatbota-v-mobilni-aplikaci)
11. [e15.cz - George České spořitelny má nový bezpečnostní algoritmus. Snížil škody klientů o 40 procent](https://www.e15.cz/finexpert/banky-a-ucty/george-ceske-sporitelny-ma-novy-bezpecnostni-algoritmus-snizil-skody-klientu-o-40-procent-1431664)
12. [O firmě za Bank iD](https://bankid.cz/o-nas/)
13. [Bankovní identita](https://cs.wikipedia.org/wiki/Bankovn%C3%AD_identita)
14. [Naše další oblíbená AI? Česká spořitelna spustila asistenta, který běží na GPT-4 od OpenAI - HEY FOMO](https://heyfomo.cz/hey-george-od-ceske-sporitelny)
15. [Spořitelna vylepšila George. Vyzkoušeli jsme, co umí virtuální poradce](https://www.penize.cz/osobni-ucty/439357-sporitelna-vylepsila-george-vyzkouseli-jsme-co-umi-virtualni-poradce)
16. [Nákup přes AI? Člověk určí cíl, rozpočet i hranice, říká ředitelka Mastercard](https://denik.cz/ekonomika/nakup-pres-ai-clovek-urci-cil-rozpocet-i-hranice-rika-reditelka-mastercard/?amp=&amp=&amp=)
17. [Bezpečnost bankovního účtu: ochrana účtu před podvody](https://bonusito.cz/ucty-a-karty/bezpecnost-bankovniho-uctu/)
18. [Škoda klientů bank z kyberpodvodů stoupla o 79 % na 1,9 miliardy](https://www.ceskenoviny.cz/zpravy/skoda-klientu-bank-z-kyberpodvodu-stoupla-o-79-na-19-miliardy/2872651)
19. [Kyberšmejdi v Česku spáchají v průměru 58 trestných činů denně - Měšec.cz](https://www.mesec.cz/aktuality/kybersmejdi-v-cesku-spachaji-v-prumeru-58-trestnych-cinu-denne/)
20. [e15.cz - Levnější investice v Georgi. Česká spořitelna ruší fixní poplatek za nákup akcií](https://www.e15.cz/finexpert/banky-a-ucty/levnejsi-investice-v-georgi-ceska-sporitelna-rusi-fixni-poplatek-za-nakup-akcii-1432883)
21. [Česká spořitelna má přes 750 tisíc investorů. Zájem Čechů roste](https://www.e15.cz/finexpert/banky-a-ucty/zajem-cechu-o-zhodnoceni-penez-roste-ceska-sporitelna-ma-pres-750-tisic-investoru-1429611)
22. [Česká spořitelna přidává AI asistenta do aplikace. Hey, George poradí s financemi](https://www.e15.cz/byznys/finance-a-bankovnictvi/ceska-sporitelna-pridava-ai-asistenta-do-aplikace-hey-george-poradi-s-financemi-1422356)
23. [Karel Svrček - IT Domain lead, AI domain](https://www.linkedin.com/in/karel-svrcek-33a10a9/)
24. [Hey George](https://ux-design-awards.com/winners/2025-2-hey-george)
25. [Založte si účet zdarma v Georgi](https://www.csas.cz/cs/osobni-finance/stante-se-klientem)
26. [Česká spořitelna má první nonstop pobočku. Je v ní AI avatar, kterého pohání ChatGPT a karta za statisíce](https://cc.cz/ceska-sporitelna-ma-prvni-nonstop-pobocku-je-v-ni-ai-avatar-ktereho-pohani-chatgpt-a-karta-za-statisice/)
27. [Bankovní identita](https://www.csas.cz/cs/financni-slovnik/bankovni-identita)
28. <https://bankid.cz/files/Bank-iD_Souhrn-za-rok-2025_Factsheet.pdf>
29. [Česká spořitelna mění podmínky. Jaké novinky chystá?](https://www.penize.cz/osobni-ucty/460966-ceska-sporitelna-meni-podminky-jake-novinky-chysta)
30. [Spořitelna spouští nové odměny. Láká i na vyšší úrok nebo vstupenky do kina](https://www.penize.cz/osobni-ucty/497497-sporitelna-spousti-nove-odmeny-laka-i-na-vyssi-urok-nebo-vstupenky-do-kina)
31. [Report supervisory board](https://www.erstegroup.com/en/investors/annualreport2025/report_supervisory_board)
32. [Welcome](https://developers.erstegroup.com/docs/tutorial/welcome)
33. [Production Corporate Accounts V1 · Apiary](https://jsapi.apiary.io/apis/eahcorporatev1prod/reference/passive-transactions/list-of-users-bank-accounts.html)
34. [Production Mortgage calculator V2 · Apiary](https://jsapi.apiary.io/apis/eahcalculatorsv2prod/reference/loans/mortgage-loans.html)
35. [CSAS Transparent Accounts REST API v2.0](https://www.programmableweb.com/api/csas-transparent-accounts-rest-api-v20)
36. [Erste Developer Portal](https://developers.csas.cz/docs/exchange-rates)
37. [Česká spořitelna API Documentation, Developer Portal & SDKs](https://www.openbankingtracker.com/provider/ceska-sporitelna/apis)
38. [Skokanem prvního pololetí je katastr nemovitostí | Bank iD](https://bankid.cz/skokanem-je-katastr/)
39. [CEE’s best bank 2026: Erste Group - Euromoney](https://www.euromoney.com/article/78slla2659gkkc4k0gkscoksg/cees-best-bank-2026-erste-group/)
40. [Erste Group Offers Tailored Financing Solutions Across Countries Using FICO AI](https://www.cityam.com/erste-group-offers-tailored-financing-solutions-across-countries-using-fico-ai/)
41. [ČSOB spouští novou generaci asistentky Kate. Využívá technologii jako ChatGPT](https://www.e15.cz/finexpert/banky-a-ucty/csob-spousti-novou-generaci-asistentky-kate-vyuziva-technologii-jako-chatgpt-1433235)
42. [ČSOB představuje novou generaci digitální asistentky Kate založenou na velkých jazykových modelech](https://zpravy.kurzy.cz/859962-csob-predstavuje-novou-generaci-digitalni-asistentky-kate-zalozenou-na-velkych-jazykovych-modelech/)
43. [Virtuální asistentka Kate od ČSOB mění svět firemního bankovnictví](https://www.pruvodcepodnikanim.cz/clanek/virtualni-asistentka-kate-od-csob/)
44. [Mastercard a ČSOB uskutečnily první platbu v Česku provedenou AI agentem - Měšec.cz](https://www.mesec.cz/aktuality/mastercard-a-csob-uskutecnily-prvni-platbu-v-cesku-provedenou-ai-agentem/)
45. [Co plánují banky v Česku? Air Bank a Česká spořitelna sází na AI](https://www.e15.cz/finexpert/banky-a-ucty/air-bank-a-ceska-sporitelna-pracuji-na-virtualnim-asistentovi-moneta-chysta-novy-uver-na-bydleni-co-planuji-banky-v-cesku-1421611)
46. [Bez AI už ani krok. Umělá inteligence bankéřům práci nebere, naopak jí zefektivňuje](https://www.newstream.cz/money/co-vsechno-dela-v-bankach-umela-inteligence)
47. [Pět lidí denně přijde o 700 tisíc korun kvůli jednomu telefonátu. Hlavní oběti paradoxně nejsou senioři](https://www.tiscali.cz/pet-lidi-denne-prijde-o-700-tisic-korun-kvuli-jednomu-telefonatu-hlavni-obeti-paradoxne-nejsou-seniori-773099)
48. [George Česko - Apps on Google Play](https://play.google.com/store/apps/details?id=cz.csas.georgego&hl=en_CA&gl=US)
49. [Aktuální telefonní podvody v Česku](https://provericislo.cz/pruvodce/aktualni-telefonni-podvody)
50. [Air Bank nabízí ve své aplikaci rychlou navigaci: Řeknete AI, co hledáte a ona vás rovnou nasměruje - Měšec.cz](https://www.mesec.cz/aktuality/air-bank-nabizi-ve-sve-aplikaci-rychlou-navigaci-reknete-ai-co-hledate-a-ona-vas-rovnou-nasmeruje/)
51. [Kyberšmejdi v ČR zdokonalují útoky, pomáhá jim AI. Škody rychle rostou](https://www.denik.cz/krimi/digitalni-podvody-cesko-vyuziti-al-na-co-si-maji-dat-cesi-pozor/?amp=&amp=&amp=)
52. ['We’ve removed the biggest barrier to customer AI adoption: writer’s block' — Starling Bank AI boss on why agentic AI could be the key to help customers manage their money better](https://www.techradar.com/pro/weve-removed-the-biggest-barrier-to-customer-ai-adoption-writers-block-starling-bank-ai-boss-on-why-agentic-ai-could-be-the-key-to-help-customers-manage-their-money-better)
53. [e15.cz - Air Bank má novinku v aplikaci. Ukáže, kam vám mizí peníze](https://www.e15.cz/finexpert/banky-a-ucty/air-bank-ma-novinku-v-aplikaci-ukaze-kam-vam-mizi-penize-1432505)
54. [Erica: Bank of America's AI Virtual Assistant, 2018 to 2026](https://www.bankingnewsai.com/banks/bank-of-america/virtual-assistant)
55. [Bank of America AI Strategy (2026): Erica, EricaAssist](https://www.bankingnewsai.com/banks/bank-of-america)
56. [Bank of America's AI Playbook: What CX Leaders Can Learn From Erica's Long Game](https://www.cmswire.com/digital-experience/bank-of-americas-ai-playbook-what-cx-leaders-can-learn-from-ericas-long-game/)
57. [How Bank of America Uses AI: Erica and EricaAssist](https://imagine.ai/research/bank-of-america)
58. [UK's Digital Bank Starling Introduces AI Banking Tool](https://www.crowdfundinsider.com/2025/06/241756-uks-digital-bank-starling-introduces-ai-banking-tool/)
59. [Starling Bank Launches AI Tool for Personal Spending Insights - Fintech Schweiz Digital Finance News - FintechNewsCH](https://fintechnews.ch/london/starling-bank-spending-intelligence-ai-feature/76917/)
60. [Starling case study](https://cloud.google.com/customers/starling)
61. [CommBank's Benefits finder records new customer milestone](https://www.commbank.com.au/articles/newsroom/2021/04/benefits-finder-saves-customers.html)
62. [CBA customers find \$1 billion in benefits - Finance - Strategy](https://www.itnews.com.au/news/cba-customers-find-1-billion-in-benefits-590814)
63. [Transcript of Andrew McMullan radio grabs: Benefits finder \$1 billion](https://www.commbank.com.au/content/dam/caas/newsroom/audio/230213_Andrew_McMullan_Benefits_finder_transcript.pdf)
64. [What Made Bank of America’s Erica So Successful in Customer Support](https://cosupport.ai/articles/bank-of-america-erica-customer-support-success)
65. [Jen v České spořitelně je digitální asistent muž](https://www.nejlepsi.cx/ceska-sporitelna)
66. [Zákazníky Air Bank nově přivítá asistent s tabletem. Na pobočky ale chodí stále méně lidí](https://cc.cz/bankovni-asistent-s-tabletem-airbank/)
67. [Air Bank mění způsob obsluhy na pobočkách, ukáže aplikaci](https://www.penize.cz/osobni-ucty/454092-air-bank-meni-zpusob-obsluhy-na-pobockach-ukaze-aplikaci)
68. [Erste Group Offers Tailored Financing Solutions Across Countries Using FICO AI](https://investors.fico.com/news-releases/news-release-details/erste-group-offers-tailored-financing-solutions-across-countries/)
69. [Starling cuts marketplace fraud exposure with…](https://aiforbanking.org/case-studies/starling-cuts-marketplace-fraud-exposure-with-gemini-powered-scam-intelligence-tool)
70. [Europe Moved Its AI Deadline for Credit Scoring. The Lesson for Lenders Is Not the Extra Time](https://credisense.com/news/eu-ai-act-credit-scoring-deadline-moved/)
71. [PSD3 & PSR re-authorisation for PIs and EMIs](https://compliance-support.nl/english/knowledge/psd3-psr/)
72. [Europe Agreed on Its New Payment Rules Ten Months Ago. Not One of Them Applies Yet. — FinTech Weekly](https://www.fintechweekly.com/magazine/articles/psd3-fida-clarity-ai-act-fintech-regulation-waiting-room-2026)
73. [Česko si postavilo vlastní aplikaci na doklady, jenže v EU s ní nepochodíte. Náhrada má přijít do konce roku](https://www.geeklife.cz/evropska-digitalni-penezenka/)
74. [EUDI Wallet: Proč potřebujeme evropskou peněženku digitální identity, když už máme Identitu občana a eDoklady? - Principal engineering s.r.o.](https://www.principal.tech/cz/blog/aktuality/eudi-wallet-proc-potrebujeme-evropskou-penezenku-digitalni-identity-kdyz-uz-mame-identitu-obcana-a-edoklady)
75. [Česko před klíčovou výzvou: Digitální identita občana musí být realitou do konce roku 2026 - VIP Noviny](https://www.vipnoviny.cz/cesko-pred-klicovou-vyzvou-digitalni-identita-obcana-musi-byt-realitou-do-konce-roku-2026/)
76. [eDoklady končí, milion Čechů si bude muset stáhnout novou aplikaci. Stát ještě neví jakou, může za to Brusel](https://www.tiscali.cz/edoklady-konci-milion-cechu-si-bude-muset-stahnout-novou-aplikaci-stat-jeste-nevi-jakou-muze-za-to-brusel-732224)
77. [Erste Group - API, Developer Portal & Open Banking](https://www.openbankingtracker.com/provider/erste-group)
78. [Bank of America Erica AI Surpasses 3 Billion Interactions Deflecting Calls](https://www.aiintelreport.com/enterprise-ai/bank-of-america-erica-ai-enterprise-win)
79. [UK’s Starling Bank rolls out Gen AI powered chatbot](https://www.retailbankerinternational.com/news/starling-bank-gen-ai-chatbot/)
80. [More than 1.5m claims commenced to uncover government benefits and rebates](https://www.commbank.com.au/articles/newsroom/2021/08/Benefits-finder-milestone.html)
81. [Klarna Replaced Its Support Team With AI, Then Started Hiring Humans Again](https://jobiora.com/blog/klarna-replaced-its-support-team-with-ai-then-started-hiring-humans-again)
82. [Klarna cut 700 support jobs for AI, then hired humans back](https://imceleste.com/news/2026-07-12-klarna-ai-customer-service-reversal)
83. [Two Years After Klarna’s AI Reversal: The Measurement Problem Nobody Talked About](https://www.mavenagi.com/resources/klarna-reversal-two-years-later)
84. [Klarna AI Customer Service: Replacing 700 Agents — A 2026 Case Study](https://getperspective.ai/blog/klarna-ai-customer-service-replacing-700-agents-conversational-ai-case-study)
85. [V ČSOB chystají převratnou novinku. Jmenuje se Kate, je to digitální asistentka a hodně na ni sázíme, říká Lhotková - CzechCrunch](https://cc.cz/v-csob-chystaji-prevratnou-novinku-jmenuje-se-kate-je-to-digitalni-asistentka-a-hodne-na-ni-sazime-rika-lhotkova/)
