# Co lidem vadí na mobilních bankovních aplikacích: rešerše pro UX audit, návrh a konkurenční analýzu (CZ/SK + zahraničí, stav k listopadu 2026)

Lidem v mobilním bankovnictví nejvíc vadí, když aplikace nefunguje ve chvíli, kdy ji potřebují: výpadky, odstávky, pády po aktualizaci a nucené migrace na nové aplikace, které umí méně než ty staré. Hned za tím je úzkost z podvodů a nemožnost dovolat se v kritické situaci živému člověku. Samotné ověřování SCA, na které se UX týmy často soustředí, je podle dostupných dat menší zdroj frustrace, než se obecně předpokládá.

## TL;DR

- **Spolehlivost a nepovedené přechody na nové aplikace jsou nejsilnějším a nejlépe doloženým zdrojem nespokojenosti v CZ/SK.** V letech 2025–2026 opakovaně vypadly ČSOB Smart, mBank, George ČS, KB+ i George Slovenské spořitelny. Migrace na KB+ srazila hodnocení v App Store ze 4,8 (stará aplikace) na 2,4 hvězdičky. Podle Treasury Committee britského parlamentu (6. 3. 2025) zaznamenalo devět velkých britských bank od ledna 2023 do února 2025 nejméně 158 IT selhání a nejméně 803 hodin, tedy přes 33 dní, neplánovaných výpadků.
- **Druhou osou frustrace jsou podvody a důvěra.** Podle České bankovní asociace čelili klienti českých bank v roce 2025 téměř 91 tisícům útoků (+4 % meziročně) a odčerpaný objem vzrostl o 53 % na 2,13 mld. Kč. V roce 2026 škody dál rostou. Uživatelé přitom nejvíc postrádají rychlou cestu k člověku: podle tiskové zprávy Air Bank (FeedIT.cz, 13. 5. 2025; Ipsos, n = 1 000) se téměř 40 % lidí při komunikaci s bankou cítí nekomfortně, když nemohou najít lidskou podporu místo chatbota. Složité ověřování identity při platbách frustruje jen 6 % lidí (u generace Z každého desátého).
- **Konkurenční příležitost leží v „nudných“ základech, ne v nových funkcích.** Jde o stabilitu a odolnost, postupné a vratné redesigny, podporu starších zařízení, srozumitelnost bez žargonu, eskalaci na člověka u podvodů a sporů, přístupnost podle EAA a střídmý cross-selling. Data z USA (J.D. Power 2025/2026) i z CZ ukazují, že aplikace se funkčně sbližují a rozhoduje výkon a spolehlivost.

## Key Findings

1. **Výpadky a odstávky jsou v CZ/SK nejčastěji medializovaným problémem a v nejstarším reprezentativním českém průzkumu i nejčastěji uváděnou výtkou k mobilní aplikaci.** ČBA/Ipsos v roce 2021 zjistily, že u mobilní aplikace lidem vadí hlavně „výpadky či odstávky a složité vyhledávání konkrétních plateb“.\[1\] Mladí do 26 let zmiňovali časté odstávky a výpadky ve 23 %.\[2\] *Síla důkazů: silná pro existenci a medializaci problému; střední pro aktuální četnost, protože reprezentativní data jsou starší.*
2. **Nucené migrace a redesigny jsou nejrizikovějším UX momentem.** Případ KB+ (2024–2026) je učebnicový: chybějící funkce oproti předchůdci, nutnost dál používat KB Klíč, pády při potvrzování transakcí, reklamy na půjčky na hlavní obrazovce a převedení části klientů na dražší tarif. Banka přitom veřejně tvrdila, že „neeviduje žádné nedostatky“.\[3\]\[4\]\[5\]\[6\]\[7\] *Silná (konzistentní napříč recenzemi, médii a hodnocením v obchodech).*
3. **Podvody a sociální inženýrství jsou nejzávažnějším problémem, protože škody jsou nevratné.** Nejde primárně o chybu UX, ale aplikace je místem, kde se podvod dokoná, a zároveň místem, kde lze podvodu zabránit. *Silná (ČBA, Policie ČR, finanční arbitr).*
4. **Zákaznická podpora a chatboty selhávají u složitých a stresových situací.** Podle tiskové zprávy J.D. Power (28. 5. 2026, USA) používá virtuální asistenty jen 28 % zákazníků aplikací národních bank a kreditních karet a spokojenost prudce klesá u podvodů, sporů a řešení problémů. CFPB (2023, starší kontext) dokumentoval „doom loops“ bez cesty k člověku. V CZ dává 58 % lidí přednost živému bankéři při zrušení platby nebo nahlášení podvodu (Česká spořitelna/Evropa v datech/Ipsos).\[8\] *Silná.*
5. **Ověřování SCA a biometrie jsou zdrojem frustrace spíš okrajově a souvisejí hlavně s výměnou telefonu, aktivací a migrací.** Podle Air Bank/Ipsos 2025 frustruje složité ověřování identity při platbách jen 6 % lidí, v generaci Z však každého desátého. Víc lidem vadí nefunkční terminály (25 %) a opakované zadávání platebních údajů (14 %). J.D. Power 2025: spokojenost je o 16 bodů vyšší u uživatelů, kteří používají vícefázové ověření.\[9\] *Střední.*
6. **Nároky na zařízení jsou podceňovaný problém.** V květnu 2026 se po aktualizaci aplikace George Slovenské spořitelny část klientů se staršími iPhony nemohla přihlásit (aplikace vyžaduje iOS 16.4+). Na fóru FinExpert popisují klienti ČS kolaps aplikace na starším Androidu. Postihuje to hlavně seniory a méně majetné. *Střední (anekdotická až mediální data, chybí kvantifikace).*
7. **Pro OSVČ a malé firmy chybí v CZ/SK jakákoli veřejná kvantitativní data o frustracích s mobilními aplikacemi.** To je samo o sobě zjištění a příležitost pro primární výzkum.

## Taxonomie problémů a prioritizace

Hodnocení „četnost“ a „závažnost“ je interpretace autora syntetizující níže uvedené zdroje, nikoli převzatá metrika.

| # | Problém | Četnost | Závažnost | Nejvíce postižené segmenty | Síla důkazů | Příklady (CZ/SK/zahraničí) |
|---|---|---|---|---|---|---|
| 1 | Výpadky, odstávky, spolehlivost | Vysoká | Vysoká | Všichni; nejvíc lidé „od výplaty k výplatě“ a OSVČ | Silná | ČSOB Smart, mBank (březen 2026), George ČS (leden 2026), KB+ (únor 2026), George SLSP (květen 2026); UK: 803 h za 2 roky |
| 2 | Nucené migrace/redesigny, ztráta funkcí | Střední (vlnovitě) | Vysoká | Dlouholetí klienti, senioři | Silná | KB+ (2,4★ vs. 4,8★), George klíč → George (ČS), falešné „aktualizace“ zneužité podvodníky |
| 3 | Podvody, phishing/vishing, falešné bezpečnostní výzvy | Vysoká | Velmi vysoká | Všichni; podle Policie ČR v 80 % ženy, průměrný věk 45 let | Silná | ČBA: 91 tis. útoků, 2,13 mld. Kč (2025); 1,9 mld. Kč za 1–7/2026 |
| 4 | Podpora, chatboty, cesta k člověku | Vysoká | Vysoká v krizi | Senioři, lidé v nouzi, oběti podvodů | Silná | Air Bank/Ipsos: téměř 40 % nekomfort; J.D. Power 2026; CFPB „doom loops“ |
| 5 | Výkon, rychlost, pády, odhlašování | Střední až vysoká | Střední | Uživatelé starších zařízení | Střední | KB+ (dlouhé načítání, samovolné odhlašování), Citi (USA) – „forced updates“ |
| 6 | Navigace a informační architektura, vyhledávání plateb | Střední | Střední | Všichni, zejm. méně zdatní | Střední (starší data) | ČBA/Ipsos 2021: složité vyhledávání plateb; KB+: „spousta věcí schovaná v prokliku“ |
| 7 | Cross-selling a reklamy v aplikaci | Střední | Střední (eroze důvěry) | Všichni | Střední/anekdotická | KB+ (reklamy na půjčky), SoFi (USA) |
| 8 | Nároky na zařízení a OS | Nízká až střední | Vysoká pro postižené | Senioři, nízkopříjmoví | Střední | George SLSP (iOS 16.4+), Wells Fargo (USA) – starší zařízení |
| 9 | Poplatky a nejasné ceny spojené s aplikací | Nízká až střední | Střední | Dlouholetí klienti | Střední | KB+: převod na tarif 39 Kč/měs. |
| 10 | Ověřování SCA, biometrie, aktivace na novém zařízení | Nízká až střední | Střední (ale blokující) | Senioři, uživatelé měnící telefon | Střední | Air Bank/Ipsos 2025: 6 % (Gen Z 10 %); KB+ nutnost KB Klíče |
| 11 | Srozumitelnost, žargon, opakované zadávání údajů | Střední | Nízká až střední | Méně zdatní, senioři | Střední | Ipsos/Air Bank 2025: 37 % žargon, 31 % opakované údaje |
| 12 | Přístupnost (zrak, motorika) | Nízká viditelnost, vysoká pro postižené | Vysoká (blokující) | Lidé s postižením, senioři | Slabá (chybí CZ testy) | ČOI: hlášení částečného neplnění EAA; Rakousko 2026: žádná ze 3 aplikací nesplnila WCAG AA |
| 13 | Komunikace změn a nečekané chování | Nízká | Střední až vysoká (panika) | Všichni | Střední | ČS: účty příbuzných viditelné v George po změně pravidel disponentů |
| 14 | Specifika OSVČ/firem | Neznámá | Pravděpodobně vysoká | OSVČ, malé firmy | Žádná kvantitativní data | SLSP: odstávky zasahují i Business24 a mToken |

## Details

### 1. Výpadky, odstávky a spolehlivost

**Co se děje.** Mediální záznamy z let 2025–2026 ukazují pravidelné výpadky u všech velkých českých bank. Server arecenze.cz (17. 3. 2026) uvádí za tři měsíce sérii: leden 2026 Česká spořitelna (George), únor 2026 Komerční banka (KB+), březen 2026 ČSOB a mBank. ČSOB Smart byl 16. 3. 2026 nedostupný asi hodinu. Podle arecenze.cz jej aktivně používá zhruba 1,58 milionu lidí.\[10\] mBank tentýž den popsala na Facebooku „výpadek velkého rozsahu“, při kterém klienti nemohli posílat ani přijímat platby. Předcházel tomu víkend plánovaných odstávek u čtyř velkých bank. ČSOB byla v sobotu nedostupná zhruba od 0:00 do 15:00, mBank v neděli od 2:30 do 9:00.\[10\] Další incident ČSOB (Peníze.cz) trval přibližně od 6:30 do 8:15 a vyřadil i Smart klíč, tedy ověřování plateb.\[11\] Při jiném výpadku ČSOB Smart mluvčí banky nejdřív uvedla, že „nikdo z banky nezaznamenal žádné problémy“, a teprve později přiznala technickou závadu (TN.cz přes arecenze.cz).\[12\] Takové chování krizovou komunikaci výrazně poškozuje.

**Slovensko.** Slovenská sporiteľňa měla v květnu 2026 výpadek aplikace George. Klienti hlásili potíže s přihlášením už dny předem a banka problém spojila s aktualizací v App Store na starších iPhonech (techbyte.sk, tvnoviny.sk, květen 2026).\[13\]\[14\]\[15\] Plánované noční odstávky SLSP v roce 2026 (březen, květen, srpen 0:00–5:00, 7. listopadu 0:00–1:00) vyřazují kromě George i Business24, mToken a notifikace.\[16\]\[17\]\[18\]\[19\]

**Zahraniční srovnání.** Podle Treasury Committee britského parlamentu (6. 3. 2025) měly Barclays, HSBC, Lloyds, Nationwide, Santander, NatWest, Danske Bank, Bank of Ireland a AIB od ledna 2023 do února 2025 nejméně 158 IT selhání a nejméně 803 hodin, tedy přes 33 dní, neplánovaných výpadků. Data nezahrnují výpadek Barclays z 31. 1. až 2. 2. 2025. Nejvíc hodin vykázaly NatWest (194 h) a HSBC (176 h), nejvíc incidentů Nationwide (18).\[20\] Banky jako nejčastější příčiny uváděly dodavatele třetích stran, změny systémů a interní softwarové chyby.\[21\] Barclays podle Computer Weekly počítala s kompenzacemi až 12,5 mil. GBP.\[20\] Předsedkyně výboru Dame Meg Hillier uvedla: „For families and individuals living paycheck to paycheck, losing access to banking services on payday can be a terrifying experience.“

**Příčiny (interpretace).** Modernizace jádrových systémů, závislost na dodavatelích, velké releasy a migrace. Mobilní aplikace je dnes jediný kanál, kterým klient vidí zůstatek i potvrzuje platby, a proto se každý výpadek projeví jako „nemám přístup k penězům“. Výpadek ověřovací aplikace (Smart klíč, mToken) navíc zablokuje i platby kartou na internetu.

**Segmenty.** Postiženi jsou všichni. Nejcitlivější jsou lidé s nízkou finanční rezervou, OSVČ s termínovanými platbami a uživatelé jediné banky. Arecenze.cz zaznamenává, že část lidí po výpadcích vybírá hotovost nebo si zakládá druhý účet.\[10\]

**Síla důkazů:** silná pro výskyt (mediální a regulatorní záznamy), střední pro četnost a vnímanou závažnost v CZ, protože aktuální reprezentativní průzkum chybí.

### 2. Nucené migrace, redesigny a ztráta funkcí

**KB+ (Komerční banka).** Seznam Zprávy (květen 2024) uvádějí, že stará aplikace měla v App Store 4,8 hvězdičky a KB+ jen 2,4.\[3\] Klienti popisovali černou obrazovku „Vítejte v KB+“, chyby, nezobrazený zůstatek a hlášku „něco se nepovedlo“ v okamžiku placení. Mluvčí KB tehdy uvedla: „U nové aplikace KB+ neevidujeme žádné nedostatky.“\[3\] Recenze na Google Play (KB+ 2,9★, 11,4 tis. hodnocení, nedatovaný snímek) popisují pády při potvrzování transakcí a delší načítání než u staré aplikace, „even after cca a year of being published“.\[7\] Upmedia.cz uvádí, že část uživatelů musela dál používat KB Klíč, čímž „nová aplikace de facto ztrácí svůj smysl“, a stěžovala si na samovolné odhlašování.\[4\] Peníze.cz popisují, že banka při migraci často převedla klienty z účtu zdarma na tarif za 39 Kč měsíčně a změnit to šlo jen na pobočce.\[6\] Letem světem Applem (29. 1. 2026) kritizuje reklamy na půjčky, které nešlo vypnout a zabíraly víc obrazovky než samotné služby. Podle autora je banka v další aktualizaci zrušila.\[5\] Finparáda (2024) řadila KB+ v App Store pod průměr trhu.\[22\] *Interpretace:* migrace kombinovala ztrátu funkcí, technickou nestabilitu, zdražení a obranné komunikační postoje. Proto se z ní stal reputační problém celé banky, ne jen aplikace.

**Česká spořitelna, George klíč → George.** Sloučení ověřovací aplikace do George probíhalo od září 2023 do jara 2024 (starší kontext). Podvodníci využili migraci k vlně automatizovaných hovorů a SMS s odkazy na falešnou „novou verzi“ George.\[23\]\[24\] Migrace tak otevřela bezpečnostní okno.

**Zahraničí.** Forbes Advisor (2026) u Citi uvádí stížnosti na „forced updates“ a u Wells Fargo na problémy se staršími zařízeními.\[25\]

**Segmenty:** dlouholetí klienti (ztráta naučených postupů), senioři, uživatelé starších telefonů.

**Síla důkazů:** silná.

### 3. Podvody, phishing/vishing a falešné bezpečnostní výzvy

**Rozsah (CZ).** Podle České bankovní asociace (tisková konference, HN.cz) stoupl v roce 2025 počet útoků na klienty bank meziročně o 4 % téměř na 91 tisíc. Odčerpaný objem vzrostl o 53 % na 2,13 mld. Kč a banky zachránily 12,15 mld. Kč (+53 %). Průměrná škoda vzrostla z necelých 16 tis. na 23 462 Kč (ČT24). V roce 2024 to bylo 87,4 tis. napadených a 1,39 mld. Kč.\[26\]\[27\] Za leden až červenec 2026 eviduje ČBA 62 705 útoků (+20 %), škody 1,9 mld. Kč (+79 %) a průměr 30 335 Kč (ČTK, září 2026).\[28\]\[29\] Za leden až září 2026 přesáhly škody 2,2 mld. Kč.\[30\] Policie ČR do poloviny dubna 2026 evidovala 728 případů „falešných policistů a bankéřů“ se škodou přes 322 mil. Kč, v průměru 721 546 Kč na oběť (Deník.cz).\[31\] Podle Policie ČR jsou oběťmi kyberpodvodů v 80 % ženy s průměrným věkem 45 let.\[32\]

**Regulatorní stopa.** Finanční arbitr v roce 2025 zahájil 12 050 řízení (+113 %). Naprostou většinu tvořily spotřebitelské úvěry (11 386). Druhou nejpočetnější oblastí byly platební služby s 294 řízeními, převážně kvůli neautorizovaným transakcím při phishingu a vishingu a kvůli autorizovaným platbám provedeným v omylu.\[33\]\[34\] Arbitr ve zprávě za rok 2024 uvádí, že ve většině případů zjistil porušení povinností spotřebitele chránit bezpečnostní prvky.\[35\] *Interpretace pro UX:* klient obvykle nese ztrátu sám, protože platbu „autorizoval“. Design autorizačních obrazovek, tedy co přesně klient potvrzuje, je proto otázkou ochrany spotřebitele, nejen použitelnosti.

**Bezpečnostní hygiena.** Podle Ipsos/ČBA (2025, reportováno Newstreamem) klesl podíl lidí s aktivním dvoufázovým ověřením u mobilního bankovnictví z 63 na 59 %. Senioři 65+ si naopak zlepšili hesla: silné heslo má 73 % oproti 58 % dříve. Mladší generace tak nejsou automaticky bezpečnější.\[36\]

**Dobré praxe.** Banky přesouvají ověření pravosti hovoru do aplikace: klient v aplikaci vidí, zda mu skutečně volá banka (tiscali.cz, 2026).\[37\] Česká spořitelna uvádí, že nový bezpečnostní algoritmus v George snížil škody klientů o 40 % (E15, údaj banky).\[38\] Ipsos pro ČBA (2021) zjistil, že lidé by uvítali ověření příjemce platby před odesláním.\[1\] Tato funkce je od října 2025 v eurozóně povinná jako Verification of Payee podle nařízení o okamžitých platbách. Její zavedení a UX v CZK prostředí jsem neověřoval.

**Síla důkazů:** silná.

### 4. Zákaznická podpora, chatboty a cesta k člověku

- **Tisková zpráva Air Bank (FeedIT.cz, 13. 5. 2025; Ipsos Instant Research, březen–duben 2025, n = 1 000):** „Téměř 40 % respondentů… se při komunikaci s bankou cítí nekomfortně, když nemohou najít lidskou podporu namísto chatbota.“ Výsledky komentoval Karel Horák, ředitel divize Péče o klienty Air Bank. Průzkum zadala banka a týká se komunikace s bankou obecně, ne jen aplikace.
- **Česká spořitelna/Evropa v datech/Ipsos (2025):** při zrušení platby nebo nahlášení podvodu preferuje živého bankéře 58 % lidí. „Virtuálního AI bankéře“ s možností přepojení na člověka by ocenilo 31,5 %.\[8\]
- **J.D. Power 2025 (USA):** využití virtuálních asistentů i spokojenost s nimi meziročně klesly.\[39\] **J.D. Power 2026 (tisková zpráva 28. 5. 2026):** asistenty používá jen 28 % zákazníků aplikací národních bank a kreditních karet a „satisfaction drops sharply for fraud, disputes and problem resolution“. Uživatelé asistentů jsou podle J.D. Power o 18 bodů spokojenější. **J.D. Power Canada 2026** (podle sekundárního zdroje): pokud uživatelé vnímají asistenta jako skutečně schopného, je spokojenost vyšší o 160 bodů. Při hlášení podvodu a sporech se ale uživatelé dostávají do smyček.\[40\]
- **CFPB (červen 2023, starší kontext, USA):** stížnosti na „doom loops“, tedy smyčky opakovaných odpovědí bez cesty k člověku. Podle zpráv AP jsou ohroženi hlavně starší lidé a lidé s omezenou angličtinou.\[41\]\[42\]
- **CZ příklad:** test asistenta Hey George (Peníze.cz, pilot pro 100 tis. klientů, starší) ukázal, že jednoduché úkony zvládá, ale „občas se zasekl nebo ukončil odpověď předčasně“.\[43\]
- **Neobanky:** u Revolutu se v českém internetu opakují stížnosti na blokace účtů a podporu pouze v aplikaci bez telefonní linky.\[44\]\[45\] Zdroje jsou ale převážně nízkokvalitní obsahové weby s nepodloženými „procenty výskytu“. Hodnotím je jako **anekdotické** a nepoužívám z nich žádná čísla.

**Síla důkazů:** silná (zahraničí), střední (CZ).

### 5. Výkon, rychlost a stabilita

Rychlost je jedním ze čtyř faktorů metodiky J.D. Power 2025 (navigace, rychlost, vizuální stránka, informace).\[9\] V roce 2026 J.D. Power metodiku přepracoval na informace, nástroje, výkon systému a design.\[9\]\[46\] Jon Sundberg (J.D. Power) v roce 2025 přisoudil růst spokojenosti „technical enhancements and speed“.\[9\] V CZ jsou doklady kvalitativní: KB+ (dlouhé načítání, samovolné odhlašování, uzamčení aplikace při každém pohybu telefonu).\[4\]\[7\] *Síla důkazů:* střední.

### 6. Navigace, informační architektura a vyhledávání

Nejstarší reprezentativní CZ data (ČBA/Ipsos 2021) uvádějí „složité vyhledávání konkrétních plateb“ jako druhou nejčastější výtku k mobilní aplikaci.\[1\] Dlouhodobý výpis transakcí je důležitý pro více než dvě třetiny klientů.\[2\] Lidé tehdy dělali složitější úkony (trvalé příkazy, limity karet) raději v internetovém bankovnictví.\[1\] Analýza Finparády (starší) ukázala, že i nejlépe hodnocená aplikace My Air (Air Bank) byla pod průměrem v počtu kliknutí a čase k nalezení základních funkcí.\[47\] **Vysoké hodnocení v obchodech tedy nezaručuje efektivní navigaci.** Na Slovensku hlasovalo v anketě Smart Banka 2025 72 628 lidí a vyhrál George SLSP.\[48\]\[49\] Anketa však měří preferenci, ne použitelnost. *Síla důkazů:* střední; aktuální CZ data chybí.

### 7. Cross-selling a reklamy v aplikaci

KB+ (2026): vyskakovací nabídky půjček bez možnosti vypnutí, později podle autora článku zrušené.\[5\] U neobank je model monetizace přes upsell běžný. Forbes Advisor (2026) u SoFi uvádí kritiku „overwhelming ads and in-app upselling“.\[25\] Ipsos/Air Bank 2025: více než čtvrtina lidí vnímá jako problém nesoulad mezi reklamou a realitou a téměř 22 % kvůli tomu ztrácí důvěru.\[50\] *Síla důkazů:* střední/anekdotická.

### 8. Ověřování SCA, biometrie a aktivace

Ověřování je v datech méně palčivé, než se předpokládá. Podle Air Bank/Ipsos 2025 (airbank.cz) „celkově jen 6 % lidí tvrdí, že je frustruje složité ověřování identifikace při platbách, nicméně v rámci Generace Z takový postup vadí každému desátému“. Víc vadí nefunkční terminály (25 %) a opakované zadávání platebních údajů (14 %). J.D. Power 2025 ukazuje vyšší spokojenost u uživatelů vícefázového ověření (+16 bodů).\[9\] V CZ ale přetrvávají bolestivé okamžiky: aktivace na novém telefonu, závislost na druhé aplikaci (KB Klíč) a výpadky ověřovacích aplikací (Smart klíč ČSOB, mToken SLSP). V roce 2021 (ČBA/Ipsos) vadilo složité přihlašování do internetového bankovnictví 18 % žen a zhruba 25 % lidí do 35 let.\[2\] Tato data jsou ale starší a týkají se webu. *Interpretace:* problém není SCA jako takové, ale hraniční stavy (výměna zařízení, výpadek, migrace). *Síla důkazů:* střední.

### 9. Nároky na zařízení

Slovenská sporiteľňa v květnu 2026 uvedla, že aktualizovaný George funguje na novějších modelech, „za podmienky, že si klient aktualizuje operačný systém“. Oficiální minimum je iOS 16.4. Klienti se staršími iPhony zůstali bez přístupu, dokud banka nepřipravila opravu.\[13\]\[14\] Na fóru FinExpert klient ČS popisuje, že jej při sloučení aplikací nikdo nevaroval, že starší Android „ze dne na den“ přestane fungovat.\[51\] *Segmenty:* senioři a nízkopříjmoví. *Síla důkazů:* střední/anekdotická. Kvantifikace podílu postižených klientů není veřejně dostupná.

### 10. Komunikace změn

Echo24 popisuje, že po změně pravidel disponentských práv se v George části klientů zobrazily účty příbuzných nebo bývalých partnerů. Banka podle mluvčího obeslala asi půl milionu klientů, ti ale namítali, že obecné oznámení o změně obchodních podmínek nestačí.\[52\] Rok změny se z dostupného úryvku nepodařilo ověřit. *Interpretace:* změny viditelnosti dat potřebují v aplikaci explicitní a kontextové oznámení, ne jen e-mail.

### 11. Přístupnost (EAA)

Od 28. 6. 2025 platí v ČR evropský akt o přístupnosti (EAA) prostřednictvím zákona č. 424/2023 Sb. Vztahuje se na spotřebitelské bankovní služby včetně mobilních aplikací.\[53\] Technickým základem je norma EN 301 549, která odkazuje na WCAG 2.1 AA.\[54\]\[55\]\[56\]\[57\] Echo24 (25. 7. 2025) uvádí, že ČOI „registruje oznámení od subjektů finančního sektoru o částečném nenaplňování požadavků na přístupnost“, zatím preferuje nápravu a pokuty se pohybují od 1 do 10 mil. Kč. Raiffeisenbank podle téhož zdroje provedla externí WCAG audit. Expert upozorňuje na naskenované PDF ceníky, které odečítač obrazovky nepřečte.\[53\] **Nezávislé české testy přístupnosti bankovních aplikací po nabytí účinnosti EAA (SONS, Blind Friendly Web apod.) jsem nenašel.** Nejbližší srovnání je rakouské: bluesource (OTS, 19. 5. 2026) v heuristické revizi aplikací bank99, Revolut a Trade Republic zjistil, že „keine der drei Apps erfüllt die WCAG-AA-Anforderungen vollständig“.\[58\] Rada seniorů ČR upozorňuje na motorické bariéry, například artrózu prstů znesnadňující ovládání dotykového displeje.\[59\] *Síla důkazů:* slabá pro CZ.

### 12. Specifika OSVČ a firemního bankovnictví

**Pro CZ/SK jsem nenašel žádná veřejná kvantitativní data o tom, co OSVČ a malým firmám vadí na mobilních aplikacích.** Dostupné jsou jen nepřímé indicie: plánované odstávky SLSP zasahují i Business24 a mToken a výpadky plateb (mBank, březen 2026) mají pro podnikatele s termínovanými úhradami přímé finanční dopady.\[17\]\[18\] Hypotézy k ověření primárním výzkumem jsou interpretace: oddělení soukromých a firemních účtů v jedné aplikaci, hromadné a dávkové platby, exporty a napojení na účetnictví, více disponentů a schvalování.

## Srovnání: CZ/SK vs. zahraničí, tradiční banky vs. neobanky

- **Celková spokojenost je vysoká všude a rozdíly se zmenšují.** V USA vzrostla spokojenost s aplikacemi národních bank v roce 2025 na 669 bodů (+18). Sean Gelles z J.D. Power mluví o „plateau“, protože banky konvergují k osvědčeným praktikám.\[39\] V roce 2026 (nová metodika, nesrovnatelná s rokem 2025) dosáhl průměr 723 bodů, nejlépe skončila Chase (730) a mezi regionálními bankami Huntington (719).\[46\] V CZ mají hlavní aplikace v obchodech přes 90 %: My Air 96 % na Google Play a 98 % v App Store, George 96/96 %, ČSOB Smart 94–96/96 % (Finparáda 2025). Výjimkou je KB+ a slabší je Creditas (84/80 %).\[60\]\[61\]\[62\]
- **CZ/SK mají vyšší medializovanou frekvenci výpadků velkých bank, ale ne nutně horší spolehlivost.** Kvantitativní srovnání s UK chybí, protože v CZ neexistuje obdoba šetření Treasury Committee. *Toto je jasná datová mezera.*
- **Neobanky** sbírají pochvaly za rychlost a design. Opakující se výtky (anekdotické, CZ i zahraničí) míří na blokace účtů při AML kontrolách, podporu pouze přes chat a upselling. Tradiční banky naopak dostávají výtky za migrace, výpadky a zastaralé procesy, které končí na pobočce (KB: „požiadavky na fyzickú cestu do pobočky“ v recenzích App Store).\[63\]
- **Podvody:** rostoucí škody v CZ odpovídají evropskému trendu. Čísla o podvodech přímo pro neobanky v CZ jsem nenašel.

## Analýza podle segmentů

- **Mladí (18–29/Gen Z):** nejintenzivnější uživatelé. Mobilní bankovnictví pravidelně používá 84,6 % lidí ve věku 18–29 let (ČS/Ipsos) a denně 50 % generace Z (NMS pro Raiffeisenbank, říjen 2025).\[8\]\[64\]\[65\] Nejvíc vnímají výpadky (23 % mladých do 26 let v roce 2021).\[2\] Mají horší bezpečnostní návyky, než se čeká.\[36\]
- **Senioři:** nižší frekvence. Denně aplikaci používá 31 % Baby Boomers a 25 % ji používá několikrát měsíčně nebo méně (NMS, vzorek však končí na 64 letech).\[64\]\[65\] Hlavní bariéry jsou tlak na „pouze aplikaci“ (Rada seniorů: „čím dál častější problém“), motorika, nároky na zařízení a preference člověka.\[59\] 45 % seniorů připouští, že je některé hrozby mohou zaskočit (Neviditelní/Ipsos, únor 2025).\[66\]\[67\] J.D. Power 2025 (USA, národní banky) uvádí, že spokojenost lidí 65+ stagnovala, zatímco u mladších vzrostla o 12 bodů.\[68\]
- **OSVČ/malé firmy:** data chybí (viz výše). Vysoká citlivost na výpadky a odstávky ověřování.
- **Lidé s postižením:** EAA vytváří právní nárok. Nezávislá CZ data chybí a zahraniční vzorek naznačuje plošné nedostatky.
- **Méně technicky zdatní:** 37 % je nekomfortně u odborných výrazů ve formulářích a 31 % vadí opakované zadávání stejných údajů (Ipsos/Air Bank 2025).\[50\] Nejvíc je zasahují migrace a změny navigace.

## Co uživatele těší a dobré praxe (benchmarky)

- **Spolehlivý základ a rychlost.** Lídři J.D. Power 2025/2026 vyhrávají na výkonu a designu: Chase uvádí „Design and System Performance“ a kanadské vyhodnocení zdůrazňuje fundamenty jako načítání, jasné informace a spolehlivé převody.\[40\]\[69\]
- **Air Bank My Air** je dlouhodobě nejlépe hodnocenou českou aplikací (Finparáda 2025: průměr 95,75–96 %).\[61\]\[62\] Je to benchmark pro konzistenci, i když starší analýza ukazuje rezervy v počtu kliknutí.
- **George ČS:** reklamace karetních plateb přímo v aplikaci s vyřízením do 48 hodin, robot vyřídí až pětinu reklamací automaticky (údaj banky).\[70\] Dále okamžitá virtuální karta a bezpečnostní algoritmus snižující škody (údaj banky: −40 %).
- **Ověření hovoru v aplikaci** jako ochrana proti spoofingu.\[37\]
- **Vícefázové ověření** zvyšuje spokojenost (+16 bodů, J.D. Power 2025), pokud je hladké.\[9\]\[71\]

## Recommendations

### Rychlé výhry (0–3 měsíce)
1. **Stavová stránka a in-app banner o výpadku nebo odstávce** s odhadem obnovy a alternativou (bankomat, karta, web). Nikdy nepopírat incident, který uživatelé vidí (poučení z ČSOB).
2. **Viditelné tlačítko „Mám podezření na podvod / zablokovat vše“** na úvodní obrazovce, s okamžitou eskalací na člověka. Chatbot u podvodů a sporů vždy předává konverzaci.
3. **Přepsat autorizační obrazovky:** co přesně, komu a kolik potvrzuji, plus varování v kontextu („Banka vás nikdy nežádá o převod na bezpečný účet“).
4. **Odstranit žargon a opakované zadávání údajů** v nejčastějších formulářích (37 % a 31 % frustrovaných).
5. **Omezit cross-selling na hlavní obrazovce:** frekvenční strop, možnost vypnutí, žádné nabídky úvěrů v kontextu bezpečnostních nebo platebních toků.
6. **Lepší vyhledávání a filtrování transakcí** (částka, protistrana, VS, období) jako dlouhodobě nejčastější „tichá“ výtka.

### Strategické změny (6–24 měsíců)
1. **Odolnost jako funkce produktu:** oddělit ověřovací službu od hlavní aplikace, aby výpadek jedné nevyřadil platby. Režim jen pro čtení s posledním známým zůstatkem během odstávky. Plánované odstávky co nejkratší a mimo citlivá okna.
2. **Migrace a redesigny jako řízený program:** paritu funkcí se starou aplikací zajistit před povinným přechodem, souběh a možnost návratu, postupný rollout s kill-switchem, sledovat hodnocení v obchodech jako KPI, neměnit tarif automaticky a připravit protiphishingovou kampaň před zahájením migrace.
3. **Politika podpory zařízení:** zveřejněné minimum OS s ročním předstihem, testování na starších zařízeních a webová alternativa pro nepodporované telefony.
4. **Přístupnost podle EAA:** nezávislý audit WCAG 2.1 AA (příprava na WCAG 2.2) s reálnými uživateli odečítačů. Řešit časové limity SCA, biometrii bez alternativy a nepřístupná PDF. Vydat prohlášení o přístupnosti.
5. **Hybridní podpora:** AI asistent pro jednoduché úkony, garantovaný přenos na člověka u podvodů, sporů a blokací, callback z aplikace a měření „false negative“ eskalací.
6. **Primární výzkum pro OSVČ a seniory 65+,** kde chybí data (viz Caveats).

### Konkurenční příležitosti
- Komunikovat **spolehlivost a lidskou dostupnost** jako značku. Banky soupeří funkcemi, ale lidi štve hlavně nedostupnost.
- Bezpečí jako UX: ověření hovoru, ověření příjemce a „cool-off“ u neobvyklých převodů.
- Segment „starší telefon + senior + OSVČ“ je trhem zanedbaný.

## Caveats a metodické poznámky

- **Zkreslení recenzí:** hodnocení v obchodech jsou ovlivněna výzvami k hodnocení v aplikaci. Velké americké aplikace mají všechny přes 4,7★ (Appcircle 2025) a recenze odrážejí spíš extrémy a období migrací.\[72\] Procenta Finparády jsou převody hvězdiček a jedna z jejích metod použila i hodnocení generované AI, které nepovažuji za validní měření.\[61\]
- **Stáří dat:** jediný reprezentativní český průzkum se seznamem výtek k mobilní aplikaci (ČBA/Ipsos, srpen 2021, n=1 000) je **starší** než požadované okno 24 měsíců.\[1\] Používám jej jen pro kontext. Aktuální průzkumy (Air Bank/Ipsos 2025, ČS/Ipsos 2025, NMS 2025) jsou buď objednané bankami, nebo měří používání, ne frustrace.
- **Zadavatelský bias:** údaje bank o vlastních úspěších (−40 % škod, reklamace do 48 h) jsou neověřená tvrzení zadavatelů.
- **Média a agregátory:** část CZ/SK zpráv o výpadcích pochází ze serverů, které přebírají obsah (arecenze.cz, kryptomagazin.sk). U Revolutu jsem odmítl obsahové farmy s nepodloženými čísly.
- **Nesrovnatelnost:** J.D. Power 2026 přepracoval metodiku, takže skóre 723 nelze srovnávat s 669 z roku 2025. Kanadský údaj „+160 bodů“ pochází ze sekundárního zdroje.
- **Chybějící data pro CZ/SK:** frustrace OSVČ a firem, nezávislé testy přístupnosti po EAA, oficiální statistika výpadků (obdoba UK Treasury Committee), data o seniorech 65+ (NMS končí na 64 letech) a SK reprezentativní průzkum frustrací.
- **Rozpory:** KB tvrdila, že u KB+ „neeviduje žádné nedostatky“, zatímco hodnocení a recenze ukazovaly opak.\[3\] ČSOB nejdřív výpadek popírala a pak jej přiznala.\[12\] Na Slovensku se údaj „40–45 % webů a aplikací prošlo kontrolou“ pravděpodobně týká veřejného sektoru, ne bank.\[73\]

## Sources

1. [Roste využívání mobilního bankovnictví i zájem o bankovní identitu](https://www.ipsos.com/cs-cz/roste-vyuzivani-mobilniho-bankovnictvi-i-zajem-o-bankovni-identitu)
2. [Jak ovládáte účet a proč? Češi řekli, co chtějí od digitálního bankovnictví](https://www.penize.cz/osobni-ucty/429971-jak-ovladate-ucet-a-proc-cesi-rekli-co-chteji-od-digitalniho-bankovnictvi)
3. [Z KB+ je spíš KB–. Část klientů si stěžuje na aplikaci Komerční banky - Seznam Zprávy](https://www.seznamzpravy.cz/clanek/ekonomika-firmy-z-kb-je-spis-kb-klienti-si-stezuji-na-aplikaci-komercni-banky-252110?noredirect=1)
4. [Komerční banka mění mobilní aplikaci, nespokojenost je velká](https://pres.upmedia.cz/zpravy/komercni-banka-meni-mobilni-aplikaci-nespokojenost-je-velka)
5. [How the new KB+ app made me disgusted with the entire bank](https://www.letemsvetemapplem.eu/en/2026/01/29/jak-mi-nova-aplikace-kb-znechutila-celou-banku/)
6. [Za účty zdarma máte platit tisícovku ročně. Pozor při přechodu na KB+](https://www.penize.cz/osobni-ucty/466711-za-ucty-zdarma-mate-platit-tisicovku-rocne-pozor-pri-prechodu-na-kb)
7. [KB+ - Apps on Google Play](https://play.google.com/store/apps/details?id=cz.kb.ndb&amp%3Bhl=ar)
8. [O čem sní klienti bank? Hlavně nechtějí čekat, ukázal průzkum](https://www.penize.cz/osobni-ucty/480068-o-cem-sni-klienti-bank-hlavne-nechteji-cekat-ukazal-pruzkum)
9. [2025 U.S. Banking and Credit Card Mobile App Satisfaction Studies - JD Power](https://www.jdpower.com/business/press-releases/2025-us-banking-and-credit-card-mobile-app-satisfaction-studies)
10. [Obří výpadek zasáhl miliony klientů 2 českých bank. Někteří Češi v obavách vybírají hotovost a mění účty](https://www.arecenze.cz/clanky/vypadek-csob-zasahl-158-milionu-klientu-problemy-hlasi-i-mbank-zkoumali-jsme-jak-casto-se-to-deje/)
11. [ČSOB má problémy s online službami. Nefunguje aplikace ani internetové bankovnictví](https://www.penize.cz/bezne-ucty/491286-csob-ma-problemy-s-online-sluzbami-nefunguje-aplikace-ani-internetove-bankovnictvi)
12. [Klienti velké banky se ráno nedostali do aplikace. „O ničem nevíme,“ hlásila banka. Pak přiznali pravdu](https://www.arecenze.cz/clanky/klienti-csob-se-rano-nedostali-do-aplikace-o-nicem-nevime-hlasila-banka-pak-priznala-zavadu/)
13. [Slovenská sporiteľňa hlási problémy s aplikáciou](https://tvnoviny.sk/ekonomika/clanok/1030126-jedna-z-najvaecsich-bank-na-slovensku-hlasi-problemy-s-aplikaciou-klienti-sa-do-nej-mozno-nedostanu)
14. [Slovenská sporiteľňa má problém s Georgeom. Ak nemáte novší iPhone, pripravte sa na výpadky](https://www.techbyte.sk/2026/05/slovenska-sporitelna-problem-george-starsi-iphone-vypadky/)
15. [Slovenská sporiteľňa má výpadok. Nefunguje George, oprava je na ceste](https://www.techbyte.sk/2026/05/slovenska-sporitelna-vypadok-nefunguje-george/)
16. [Slovenská sporiteľňa odstaví služby: Výpadok zasiahne Georgea aj bankomaty](https://kryptomagazin.sk/slovenska-sporitelna-odstavi-sluzby-vypadok-zasiahne-georgea-aj-bankomaty/)
17. [Slovenská sporiteľňa vypne kľúčové služby: Výpadok zasiahne bankomaty aj Georgea](https://kryptomagazin.sk/slovenska-sporitelna-vypne-klucove-sluzby-vypadok-zasiahne-bankomaty-aj-georgea/)
18. [Najväčšia slovenská banka varuje, že sa k peniazom nemusíte dostať tak, ako doteraz (odstávka 11 služieb)](https://www.techbyte.sk/2026/11/najvacsia-slovenska-banka-varuje-peniazom-dostat-doteraz/)
19. [Slovenská sporiteľňa obmedzí služby: Výpadok sa dotkne bankomatov aj platieb](https://kryptomagazin.sk/slovenska-sporitelna-obmedzi-sluzby-vypadok-sa-dotkne-bankomatov-aj-platieb/)
20. [Big bank systems crashed for over 800 hours in last two years due to IT outages](https://www.computerweekly.com/news/366620352/Big-bank-systems-down-for-over-800-hours-in-last-two-years-due-to-IT-outages)
21. [Treasury Committee publishes UK banking outage data](https://paymentexpert.com/2025/03/06/treasury-committee-banking-outages/)
22. [Která bankovní mobilní aplikace je podle uživatelů nejlepší? - Finparáda](https://www.finparada.cz/8622-Jak-hodnoti-mobilni-aplikace-bank-primo-jejich-uzivatele.aspx)
23. [Pozor na falešnou aplikaci George, vyčistí vám účet](https://www.bezpecnapribram.cz/blog/clanek/pozor-na-falesnou-aplikaci-george-vycisti-vam-ucet)
24. [Největší česká banka chystá velké změny. Radši si o nich přečtěte](https://udalosti247.cz/spotrebitel/nejvetsi-ceska-banka-chysta-velke-zmeny-radsi-si-o-nich-prectete/)
25. [Analysis: Best Mobile Banking Apps of 2026](https://www.forbes.com/advisor/banking/best-mobile-banking-apps/)
26. [Podvodných telefonátů přibývá. Falešní bankéři způsobili meziročně o 41 % vyšší škody, operátoři blokují miliony pokusů o zneužití čísel - Tojesenzace.cz](https://tojesenzace.cz/2025/07/29/podvodnych-telefonatu-pribyva-falesni-bankeri-zpusobili-mezirocne-o-41-vyssi-skody-operatori-blokuji-miliony-pokusu-o-zneuziti-cisel/)
27. [Baby Boomers online: Digitální sebevědomí a kyberhrozby](https://zpravy.kurzy.cz/805845-baby-boomers-online-digitalni-sebevedomi-a-kyberhrozby/)
28. [Podvodný telefonát z banky: kdy zavěsit a co dělat](https://chybelomalo.cz/podvody/falesny-banker-po-telefonu-kdy-zavesit/)
29. [Finanční správa varuje před novým podvodem. Lidem chodí falešné zprávy o vrácení téměř 10 tisíc korun na daních - EnergoZrouti.cz](https://energozrouti.cz/clanek/financni-sprava-varuje-pred-novym-podvodem-lidem-chodi-falesne-zpravy-o-vraceni-dane)
30. [Klienti bank přišli za devět měsíců o 2,2 miliardy korun. Co jim poradce může doporučit](https://www.poradenstvifinance.cz/klienti-bank-prisli-za-devet-mesicu-o-22-miliardy-korun-co-jim-poradce-muze-doporucit/)
31. [Kyberšmejdi udeřili naplno, obětí mohl být každý: Za 3 měsíce škoda 800 milionů](https://www.denik.cz/krimi/cesko-krimi-kybersmejdi-falesni-policiste-a-bankeri-utoci-v-cesku-rekordni-skody/)
32. [Aktuální telefonní podvody v Česku](https://provericislo.cz/pruvodce/aktualni-telefonni-podvody)
33. [Zájem o finančního arbitra prudce roste. Dominují spory ze spotřebitelských úvěrů](https://nezadluzimse.cz/2026/08/03/zajem-o-financniho-arbitra-prudce-roste-dominuji-spory-ze-spotrebitelskych-uveru/)
34. [Zájem o finančního arbitra prudce roste. Dominují spory ze spotřebitelských úvěrů](https://www.sos-msk.cz/zajem-o-financniho-arbitra-prudce-roste-dominuji-spory-ze-spotrebitelskych-uveru/)
35. [VÝROČNÍ ZPRÁVA O ČINNOSTI FINANČNÍHO ARBITRA ZA ROK 2024 (předkládaná podle §](https://finarbitr.gov.cz/galerie/tinymce/V%C3%BDro%C4%8Dn%C3%AD%20zpr%C3%A1va%20o%20%C4%8Dinnosti%20finan%C4%8Dn%C3%ADho%20arbitra%20za%20rok%202024_1.pdf)
36. [Digitální generace pohořela. Kyberšmejdům se lépe ubránili senioři](https://www.newstream.cz/money/digitalni-generace-pohorela-kybersmejdum-se-lepe-ubranili-seniori)
37. [91 000 brutálních útoků na české účty! Banky ukázaly neprůstřelný způsob, jak během pár vteřin odhalit falešného bankéře](https://www.tiscali.cz/91-000-brutalnich-utoku-na-ceske-ucty-banky-ukazaly-neprustrelny-zpusob-jak-behem-par-vterin-odhalit-falesneho-bankere-680389)
38. [e15.cz - Česká spořitelna má výpadek. Internetové bankovnictví i aplikace George jsou několik hodin nedostupné](https://www.e15.cz/finexpert/banky-a-ucty/ceska-sporitelna-ma-vypadek-internetove-bankovnictvi-i-aplikace-george-jsou-nekolik-hodin-nedostupne-1431908)
39. [www.businesswire.com](https://www.businesswire.com/news/home/20250529002789/en)
40. [J.D. Power's 2026 Verdict on Canadian Banking Apps](https://yourtechreport.com/2026/06/23/j-d-powers-2026-verdict-on-canadian-banking-apps/)
41. [Chatbots in consumer finance](https://www.consumerfinance.gov/data-research/research-reports/chatbots-in-consumer-finance/chatbots-in-consumer-finance/)
42. [CFPB report: customers stuck in finance chatbot loops](https://vibegraveyard.ai/story/cfpb-report-financial-chatbots-customer-loops/)
43. [Spořitelna vylepšila George. Vyzkoušeli jsme, co umí virtuální poradce](https://www.penize.cz/osobni-ucty/439357-sporitelna-vylepsila-george-vyzkouseli-jsme-co-umi-virtualni-poradce)
44. [Revolut: Nejčastější potíže klientů a jak je skutečně vyřešit \< nuspring.cz](https://nuspring.cz/revolut-nejcastejsi-potize-klientu-a-jak-je-skutecne-vyresit/)
45. [Revolut problémy hýbou Českem: Co se děje? \< ZooHoo](https://zoohoo.cz/revolut-problemy-hybou-ceskem-co-se-deje/)
46. [2026 U.S. Digital Banking and Credit Card Mobile App Satisfaction Studies - JD Power](https://www.jdpower.com/business/press-releases/2026-us-digital-banking-and-credit-card-mobile-app-satisfaction-studies/)
47. [Žebříček mobilního bankovnictví. Jak dopadla aplikace vaší banky? - Finparáda](https://www.finparada.cz/6897-Analyza-mobilniho-bankovnictvi.aspx)
48. [Rekordných 73-tisíc ľudí rozhodlo. Toto je najlepšia banková aplikácia](https://kryptomagazin.sk/rekordnych-73-tisic-ludi-rozhodlo-toto-je-najlepsia-bankova-aplikacia/)
49. [Smart Banka 2025: Viac ako 72 000 Slovákov rozhodlo. Toto sú najlepšie bankové aplikácie! - MojAndroid.sk](https://www.mojandroid.sk/smart-banka-2025-vysledky/)
50. [Chatbota nechci! 40 % Čechů raději mluví s živým operátorem. Co dalšího ukázal průzkum banky?](https://www.kupi.cz/magazin/clanek/35724-pruzkum-ukazal-co-stve-klienty-bank)
51. [Česká spořitelna - FinExpert.cz](https://forum.finexpert.e15.cz/viewtopic.php?f=316&p=13677110)
52. [„Máma vidí v Georgi můj účet.“ Nová pravidla České spořitelny vyvolala vlnu paniky - Echo24.cz](https://www.echo24.cz/a/HxcyY/zpravy-domov-mama-george-muj-ucet-pravidla-ceska-sporitelna-vlna-panika)
53. [Weby bank a e-shopů musí plnit nové standardy pro lidi s postižením. ČOI varuje před porušováním - Echo24.cz](https://www.echo24.cz/a/H4six/zpravy-ekonomika-banky-e-shopy-pravidla-pro-pristupnost-pro-nevidome)
54. [Přístupnost digitálních služeb: Co od června 2025 čeká české firmy](https://www.beey.io/cs/pristupnost-digitalnich-sluzeb-co-od-cervna-2025-ceka-ceske-firmy-a-jak-s-tim-pomuze-beey-53614/)
55. [European Accessibility Act for Banking & Finance](https://askem.com/financial-services/)
56. [How the EAA Applies to Banking and Financial Services](https://accessible.org/eaa-banking-financial-services/)
57. [Proč u mobilních aplikací nestačí myslet jen na nevidomé uživatele - JanBalak.name](https://www.janbalak.name/clanky/co-rika-zakon-a-proc-nestaci-myslet-jen-na-nevidome.html)
58. [Kaum eine Banking-App erfüllt Barrierefreiheitsstandards vollständig](https://www.ots.at/presseaussendung/OTS_20260519_OTS0100/kaum-eine-banking-app-erfuellt-barrierefreiheitsstandards-vollstaendig)
59. [Česká banka na spořicím účtu nabízí vyšší úroky. Část zákazníků tím ale naštvala](https://tn.nova.cz/zpravodajstvi/clanek/658182-ceska-banka-na-sporicim-uctu-nabizi-vyssi-uroky-cast-zakazniku-tim-ale-nastvala)
60. [Platební trendy roku 2025. Jak hodnotíte svou bankovní mobilní aplikaci? - Finparada.cz](https://m.finparada.cz/www.m.finparada.cz/8767-Platebni-trendy-na-rok-2025.aspx)
61. [Která bankovní aplikace je nejpřívětivější? Sami uživatelé hodnotí - Finparada.cz](https://m.finparada.cz/8869-Mobilni-aplikace-hodnoceni.aspx)
62. [Bankovnictví Creditas One: změny pro uživatele i nové funkce - Finparada.cz](https://m.finparada.cz/9030-Banka-Creditas-aplikace-One.aspx)
63. [KB+ - Ratings & Reviews - App Store - Apple](https://apps.apple.com/sk/app/kb/id1585485232?see-all=reviews&platform=watch)
64. [53 % mileniálů používá mobilní bankovnictví alespoň jednou denně. U Baby Boomers je to 31 %](https://zpravy.kurzy.cz/877607-53--milenialu-pouziva-mobilni-bankovnictvi-alespon-jednou-denne-u-baby-boomers-je-to-31/)
65. [53 % mileniálů používá mobilní bankovnictví alespoň jednou denně. U Baby Boomers je to 31 %](https://feedit.cz/2026/10/08/53-milenialu-pouziva-mobilni-bankovnictvi-alespon-jednou-denne-u-baby-boomers-je-to-31/)
66. [Baby Boomers online: Digitální sebevědomí a kyberhrozby](https://feedit.cz/2025/03/12/baby-boomers-online-digitalni-sebevedomi-a-kyberhrozby/)
67. [Baby Boomers online: Digitální sebevědomí a kyberhrozby - průzkum](https://zpravy.kurzy.cz/805903-baby-boomers-online-digitalni-sebevedomi-a-kyberhrozby-pruzkum/)
68. [www.businesswire.com](https://www.businesswire.com/news/home/20251211608475/en)
69. [Chase Ranks #1 in the JD Power 2026 U.S. Mobile Banking App Satisfaction Study](https://media.chase.com/news/chase-ranks-1-in-the-jd-power-2026-us-mobile-banking-app-satisfaction-study)
70. [Spořitelna spustila online reklamaci plateb v mobilní aplikaci George. Díky využití robota vyřídí reklamaci do 48 hodin - Investujeme.cz - odborný server společnosti Swiss Life Select a.s.](https://www.investujeme.cz/tiskove-zpravy/sporitelna-spustila-online-reklamaci-plateb-v-mobilni-aplikaci-george-diky-vyuziti-robota-vyridi-reklamaci-do-48-hodin/)
71. [Bank and Credit Card Apps and Websites Struggle to Stand Out J.D. Power Finds](https://www.businesswire.com/news/home/20250529002789/en/Bank-and-Credit-Card-Apps-and-Websites-Struggle-to-Stand-Out-J.D.-Power-Finds)
72. [Most Popular Banking Apps in the US: 2025 Data Analysis - Appcircle Blog](https://appcircle.io/blog/most-popular-banking-apps-in-the-us-2025-data-analysis)
73. [Konec „chaosu“ na webech. Banky se připravují na nová pravidla - Seznam Zprávy](https://www.seznamzpravy.cz/clanek/domaci-zivot-v-cesku-banky-se-pripravuji-na-nova-pravidla-269873?noredirect=1)
