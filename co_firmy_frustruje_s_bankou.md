# Co drží interakce firem s bankou zpátky – rešerše

Nov 27, 2026 · @Štěpán Pressl

## TL;DR: 10 zjištění podle závažnosti

Nejdůležitější zjištění je **o dírách v datech**: jediný český širší průzkum (Ipsos pro AMSP a ČS, 10/2025, n = 301) nepokrývá OSVČ, otevírání účtu, podporu ani kanály. Pořadí níže je **moje interpretace** podle toho, co zdroje nejvíc dokládají a jak velkou škodu popisují; není to změřená závažnost. Síla důkazů: střední = oficiální nebo průzkumový zdroj s výhradami, anekdotické = recenze a případy, hypotéza = odvozeno z mechanismu.

| # | Zjištění | ID | Síla důkazů |
| --- | --- | --- | --- |
| 1 | Účet může být odmítnut nebo zrušen bez vysvětlení a firma nemá právo na účet ani nezávislého rozhodčího | A1, A4 | střední (Forbes 2023, UK ombudsman) + anekdotické recenze |
| 2 | AML dotazy a blokace plateb zdržují provoz; FAÚ blokace obvykle trvá 2–3 dny | A3 | střední |
| 3 | Poplatky jsou největší přání firem (46 % žádá nižší a jednodušší) a změny nejsou dobře oznámeny | F2, D1 | střední (Ipsos, spoluzadavatel ČS) |
| 4 | Otevírání účtu je stále částečně online a částečně na pobočce; nevíme, jak dlouho trvá | A2 | střední (nabídka bank), délka = chybí data |
| 5 | Úvěr: 31 % firem chce volnější kritéria, OSVČ s paušální daní bývá hodnocena slabě | E1, E2 | střední / hypotéza |
| 6 | Napojení na účetnictví: formáty exportů, API za poplatek, párování plateb | C1, C2 | střední (ceníky), hypotéza (dopad) |
| 7 | Při problému není snadné se dovolat počlověka, zejména u fintechů | F1 | anekdotické |
| 8 | Výpadky a plánované odstávky (2/2026, 7/2026); dopad na firmy neměřen | F4 | střední (události), dopad chybí |
| 9 | Podvody cílené na firmy (falešný bankéř, CEO fraud); zákon se mění s PSD3/PSR | F5 | střední |
| 10 | Role, limity a schvalování plus nové povinnosti VoP a okamžitých plateb od 2027 | B1, B2 | hypotéza |

Další krok: sekce Metodika ukazuje, kde česká data chybí, a sekce Výzkumné otázky z nich dělá plán primárního výzkumu.

## Slovníček pojmů

Tyto pojmy se v dokumentu opakují a bez nich se člověk ve firemním bankovnictví ztratí; každý je vysvětlen tak, jak ho firma zažívá v praxi.

| Pojem | Co to znamená lidsky | Kde na to firmy narážejí |
| --- | --- | --- |
| KYC (Know Your Customer, „poznej svého klienta“) | Banka musí zjistit, kdo firma je, kdo ji vlastní a odkud berou peníze. | Dokládání při otevření účtu a pak opakovaně během života účtu. |
| AML (Anti-Money Laundering) | Zákon proti praní špinavých peněz; banka sleduje každou příchozí i odchozí platbu. | Dotazy na obchodní partnery, odložení nebo blokace plateb. |
| FAÚ (Finanční analytický úřad) | Státní úřad, kterému banka hlásí podezřelé obchody. | Banka o důvodu zdržení často nesmí klientovi nic říct. |
| Skutečný majitel | Fyzická osoba, která firmu nakonec ovládá, i přes holdingy a další firmy. | Banka ho musí dohledat a ověřit; u složitých struktur to trvá. |
| Statutár (jednatel) | Osoba oprávněná jednat za firmu navenek (u s.r.o. jednatel). | Banka vyžaduje jeho osobní identifikaci. |
| Disponent (oprávněná osoba) | Člověk, který smí s účtem nakládat: zadávat platby, vidět výpisy, ovládat karty. | Každá změna (nová účetní, odchod zaměstnance) znamená papíry nebo návštěvu pobočky. |
| Způsob dispozice, schvalování | Pravidlo, zda platbu smí schválit jeden člověk, nebo musí dva (tzv. dvojí podpis, „čtyři oči“). | Nastavení rolí a limitů v aplikaci bývá nepružné. |
| Hromadná platba (dávka) | Soubor mnoha plateb nahraný najednou, typicky výplaty a faktury dodavatelům. | Formáty souborů, chyby v souboru, schvalování celé dávky. |
| Trvalý příkaz, inkaso | Pravidelná platba zadaná předem (příkaz); inkaso je platba, kterou si příjemce sám vybírá s vaším souhlasem. | Správa souhlasů a limitů inkas. |
| IBAN | Mezinárodní tvar čísla účtu, nutný pro platby do zahraničí. | Překlepy, odmítnuté platby. |
| SEPA | Jednotná oblast EU pro platby v eurech za pravidla běžná pro domácí platby. | Platba v eurech mimo SEPA se řídí jinými pravidly a stojí víc. |
| SWIFT | Mezibankovní síť pro platby mimo SEPA (např. do USA nebo Číny). | Pomalejší, dražší, nejasné poplatky (volby SHA, OUR, BEN určují, kdo které poplatky platí). |
| Okamžitá platba | Převod připsaný příjemci v řádu sekund, i o víkendu. | Banky ji nenabízejí všechny stejně; u firem bývají nižší limity. |
| Ověření příjemce (Verification of Payee, VoP) | Banka před odesláním platby v eurech zkontroluje, zda jméno příjemce sedí k číslu účtu. | Nová povinnost, která mění tok zadávání plateb; u firem rozhoduje, jaký přesně název se porovnává. |
| API | Rozhraní, kterým si počítačový program (účetní software, e-shop) sám čte výpisy nebo zadává platby. | Banky ho nabízejí různě kvalitně a za různé ceny. |
| PSD2, open banking | Evropská pravidla, která nutí banky na přání klienta zpřístupnit účty aplikacím třetích stran. PSD3 a PSR jsou připravovaná nová pravidla. | Možnost sloučit účty více bank v jedné aplikaci; v praxi omezená kvalitou rozhraní. |
| SCA (silné ověření) | Potvrzení platby dvěma nezávislými prvky, např. heslo a telefon. | Zdržuje hromadné schvalování a práci účetních. |
| Párování plateb | Přiřazení příchozí platby ke konkrétní faktuře, nejčastěji podle variabilního symbolu a částky. | Hlavní pracovní zátěž účetních; chybný nebo chybějící symbol znamená ruční dohledávání. |
| Variabilní symbol | Číslo v platbě, které říká, ke které faktuře platba patří. | Zákazníci ho vyplňují špatně. |
| Formát výpisu (ABO, MT940, CAMT.053) | Strojově čitelné soubory s pohyby na účtu pro nahrání do účetního softwaru. | Banky nabízejí jiné formáty; změna banky často znamená předělat napojení. |
| Kontokorent | Povolené přečerpání běžného účtu do sjednaného limitu. | Schvalování, doložení obratů, opakované prodlužování. |
| Akceptace karet (acquirer), terminál, platební brána | Služba, která firmě umožní přijímat platby kartou: fyzický terminál v provozovně, brána na webu e-shopu. | Zvláštní smlouva, zvláštní poplatky, zvláštní portál, často mimo hlavní bankovnictví. |
| Bank iD | Způsob, jak se prokázat u jedné služby přes přihlášení do vlastní banky. | Zrychluje online otevření účtu, ale nepokrývá všechny typy firem. |
| Technický účet | Účet, na který se při zakládání s.r.o. vloží základní kapitál. | První kontakt nové firmy s bankou a první možné odmítnutí. |
| Multibanking | Správa účtů u více bank z jedné aplikace. | Firmy mívají více bank a pak kombinují několik aplikací. |

## Mapa cesty firmy s bankou

&#91;embedded content: cesta firmy s bankou · 10 fází\]

Kódy v závorkách odkazují na problémy v taxonomii. Cesta nemusí být lineární: firma se k bodům jako účetnictví nebo poplatky vrací opakovaně.

## Taxonomie problémů

Identifikoval jsem 20 opakujících se problémů; nejlépe podložené jsou ty, které plynou z regulace (AML/KYC), z cen a z technického napojení na účetnictví, zatímco česká data o četnosti téměř neexistují.

Síla důkazů: **silná** = změřené nebo dané zákonem, ceníkem či oficiálním dokumentem; **střední** = jeden kvalitní zdroj nebo zdroj se zkreslením (zadavatelem je banka, zahraničí, neznámý vzorek); **anekdotická** = recenze, diskuze, jednotlivé případy. „Měřeno“ = číslo z uvedeného zdroje; „Odhad“ = můj úsudek bez čísla. Zdroje jsou v buňkách, plnou citaci najdete na konci.

### A. Otevření účtu a prověřování

| ID | Problém lidsky | Četnost a závažnost | Koho postiženo | Příčina | Příklady | Důkazy |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Banka účet neotevře nebo ho zruší a důvod neřekne. | Měřeno: české počty odmítnutí nikdo nezveřejňuje. UK: osm velkých bank zavřelo 142 tis. účtů malých firem za rok ([City AM](https://cityam.com/?p=2168907)). Závažnost vysoká, bez účtu firma nemůže podnikat. | Nové firmy, firmy s cizinci mezi vlastníky, krypto, spolky, firmy po přestávce; majitel, jednatel. | Regulatorní (AML) a obchodní: banka si klienty vybírá a právní osoba nemá na účet nárok ([Forbes](https://forbes.cz/maji-firmy-pravo-na-bankovni-ucet-krypto-byznys-ma-jasno-vlada-vaha/), 2023). | CZ: spolek odmítnut po odmítnutí sdělit počet členů ([banky.cz](https://www.banky.cz/poradna/banka-odmitla-zridit-ucet-19980/), 2022); UK: [FCA o obranných MSP](https://www.fca.org.uk/publications/multi-firm-reviews/defence-smes-access-banking-services), proces je zbytečně dlouhý. | střední |
| A2 | Otevření trvá a u složitějších firem vyžaduje návštěvu pobočky. | Měřeno: KB otevírá účet obvykle druhý pracovní den po kompletních dokladech kvůli AML ([KB](https://www.kb.cz/cs/podpora/ucty-a-platby/jak-si-zalozit-podnikatelsky-ucet)); online jen firma s jedním jednatelem ([KB](https://www.kb.cz/cs/podnikatele-a-firmy/sjednejte-si-podnikatelsky-ucet)). České průměrné doby nemám. | S.r.o. s více jednateli, nové firmy, členové spáru; majitel, jednatel. | Procesní: banka ověřuje osobně a online postup zatím pokrývá jen nejjednodušší struktury. | [Moneta](https://www.banky.cz/clanky/moneta-umoznuje-vybranym-sro-zalozit-firemni-ucet-kompletne-online/) (9/2026) online jen pro s.r.o., kde jedná každý sam; [Air Bank](https://www.mesec.cz/n/podnikatelske-ucty/) rozšířila od 23. 1. 2026 na s.r.o. s více jednateli; SK: [Tatra banka](https://www.tatrabanka.sk/sk/blog/tlacove-spravy/tatra-banka-zjednodusila-proces-otvarania-uctov-podnikatelov) od 2/2025. UK starší: 2,6 týdne ([Tide](https://ffnews.com/newsarticle/inaccessible-high-street-banks-could-cost-uk-smes-245-million-a-year), 2017, dodavatel fintechu). | střední |
| A3 | Banka se během provozu ptá na obchodní partnery a původ peněz, platbu zdrží nebo zablokuje. | Měřeno: banka sleduje každou platbu; když klient informace nedodá, musí platbu odmítnout nebo účet vypovědět; blokace FAÚ trvá obvykle 2–3 dny ([arecenze](https://www.arecenze.cz/clanky/banky-cechum-hlidaji-kazdou-platbu-2026-o-hlaseni-uradu-mlci-trestnim-oznamenim-konci-zhruba-kazde-desate/), 31. 10. 2026; FAÚ 2025: 7 497 oznámení, z toho 5 656 od bank). Odhad: závažné u obchodů s hotovostí a cizinou. | Nové firmy, importy/exporty, hotovost, spolky; majitel nebo FD odpovídá, účetní dokládá. | Regulatorní: AML zákon; banka nesmí klientovi říct, že podala hlášení ([FAÚ](https://fau.gov.cz/files/instituty-omezeni-vlastnickeho-prava-na-zaklade-zakona-o-aml.pdf)). | [Klientka mBank čekala 12 dnů po doložení](https://www.banky.cz/poradna/aml-banka-zablokovala-ucet-22246/); [dotaz na obchodní know-how](https://www.banky.cz/poradna/aml-a-blokace-platby-11756/); analytik Banky.cz učí o 1–2 týdnech ([banky.cz](https://www.banky.cz/poradna/banka-mi-zablokovala-ucet-aml-22241/)). | střední (zákon), anekdotická (délka) |
| A4 | Když banka účet zablokuje nebo zruší, firma nemá srozumitelný a nezávislý způsob, jak se bránit. | Měřeno: český finanční arbitr řeší spotřebitelské spory ([gov.cz](https://portal.gov.cz/sluzby-vs/reseni-spotrebitelskych-sporu-u-financniho-arbitra-S12252)); u účtů používaných k podnikání ho podle [arecenze](https://www.arecenze.cz/clanky/banky-cechum-hlidaji-kazdou-platbu-2026-o-hlaseni-uradu-mlci-trestnim-oznamenim-konci-zhruba-kazde-desate/) nelze využít (ověřit u arbitra). Závažnost vysoká. | Všechny firmy, nejvíc fintech klienti a malé firmy; majitel. | Právní a obchodní: ochrana je psaná pro spotřebitele, firma jde k soudu. | CZ: [rušení účtu občasně po nepřevzatém dopisu](https://www.banky.cz/poradna/banka-mi-zrusila-ucet-27552/) (2/2026, jeden případ). UK: ombudsman u Revolutu bere uzavření jako obchodní rozhodnutí banky ([FOS](https://www.financial-ombudsman.org.uk/decision/DRN-6091789.pdf)); Revolut: [€36 tis. zmražených pět měsíců](https://www.trustpilot.com/review/business.revolut.com) (recenze 2026); Wise: [uzavření bez vysvětlení a bez odvolání](https://au.trustpilot.com/review/wise.com?page=10). | střední (právní rámec), anekdotická (případy) |

### B. Každodenní provoz: role, schvalování, nové povinnosti

| ID | Problém lidsky | Četnost a závažnost | Koho postiženo | Příčina | Příklady | Důkazy |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | Role, oprávněné osoby a schvalování plateb více lidmi se sdělují těže, než by firma čekala (hypotéza). | Měřeno: žádný zdroj. Odhad: každá změna (nová účetní, odchod zaměstnance, karta pro další osobu) znamená úpravu práv u banky; závažnost střední, četná. | Firmy se dvěma a více lidmi, externí účetní, zaměstnanec s kartou. | Procesní a technická: práva jsou vzána na smlouvě, ne na jednoduchém nastavení. | Z druhé strany: KB nabízí [hromadné potvrzování plateb v mobilu](https://www.kb.cz/cs/podpora/ucty-a-platby/hromadna-autorizace-plateb-v-mobilni-banka-business), fintech Vivid [pravidla schvalování](https://vivid.money/cs-cz/enterprise/approval-rules/). Potřebuje ověřit rozhovory. | hypotéza |
| B2 | Nové evropské povinnosti mění zadávání plateb (ověření příjemce, okamžité platby). | Měřeno: ověření jména příjemce u europlateb platí v eurozóně od 9. 10. 2025; české banky mají zákonnou povinnost od 2027, UniCredit ji nabízí od 10/2025 a u hromadných plateb ji umí při importu XML ([UniCredit](https://www.unicreditbank.cz/content/dam/cee2020-pws-cz/cz-dokumenty/cash-management/novinky-v-oblasti-sepa-plateb-2025.pdf)). Okamžité platby tvořily v červeni 2025 40 % úhrad ([banky.cz](https://www.banky.cz/clanky/okamzite-platby-umi-uz-8-bank-a-dalsi-pribydou-v-nejblizsich-tydnech/)). Odhad: neshoda obchodního a zapsaného názvu firmy zdrží platby. | Firmy s eurovými a hromadnými platbami, účetní. | Regulatorní. | SK: banky porovnávají u firem různé údaje, některé jen název, jiné i právní formu ([podnikajte.sk](https://www.podnikajte.sk/technologie/sluzba-overenie-prijemcu-platby-od-oktobra-2025)). | silná (pravidla), hypotéza (dopad) |

### C. Účetnictví, fakturace a daňové povinnosti

| ID | Problém lidsky | Četnost a závažnost | Koho postiženo | Příčina | Příklady | Důkazy |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | Každá banka dává data účetnímu jinak; napojení je křehké a někdy placené. | Měřeno: účetní program vyžaduje formát podle banky (ABO, Multicash, Gemini, u Fia API) ([Money S3](https://money.cz/navod/import-vypisu-a-export-platebniho-prikazu/)); KB od 30. 6. 2026 ukončí dosavadní API a pokračování je jen s extra službou API Business (Basic zdarma, Plus 100 Kč, Pro 500 Kč měsíčně) ([KB ceník](https://www.kb.cz/getmedia/2a3093db-9b2e-49c4-b530-993d221ebde9/cenik-produktu-a-sluzeb-pro-fyzicke-osoby-podnikatele-a-pravnicke-osoby-zmeny.pdf)). Odhad: hodiny účetního měsíčně neznámé. | Účetní (externí i interní), e-shopy, mikrofirmy. | Technická a obchodní: API je produkt, ne standard. | Fakturoid [neumí párovat mBank a Partners banku](https://www.fakturoid.cz/podpora/automatizace/parovani-plateb-s-bankou) kvůli formátu oznámení; KB od 1. 11. 2026 [nový poplatek za denní výpis camt.052](https://www.kb.cz/getmedia/c1eaaab5-6a89-406c-96dc-4470f64a651d/Zmeny-v-Sazebniku-KB-platne-od-1-11-2026.pdf). | střední až silná (fakta), neznámá (rozsah dopadu) |
| C2 | Platba bez správného variabilního symbolu znamená ruční dohledávání faktury. | Měřeno: nic nezávislého; dodavatel [Pohoda](https://portal.pohoda.cz/?p=40771) říká, že ruční kontrola výpisu patří k nejčastějším žroutm času (tvrzení dodavatele). Závažnost nízká za kus, vysoká v souhrnu. | Účetní, e-shopy, firmy s mnoha malými platbami. | Procesní: zákazník platí špatně a banka předá jen to, co dostala. | UK: u Revolutu se platby od obchodníků připisovaly úhrnně a firma je musí párovat ručně ([FOS](https://www.financial-ombudsman.org.uk/decision/DRN-5568416.pdf)). | anekdotická |

### D. Příjem plateb, hotovost, cizina

| ID | Problém lidsky | Četnost a závažnost | Koho postiženo | Příčina | Příklady | Důkazy |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | Hotovost je dražší a hůře dostupná, banky ji tlačí k bankomatům. | Měřeno: KB od 1. 11. 2026 nový poplatek 0,5 % (min. 1 000, max. 5 000 Kč) za neuskutečněný oznámený výběr hotovosti a 5 % (min. 150 Kč) u vkladů s více než 50 mincí ([KB](https://www.kb.cz/getmedia/c1eaaab5-6a89-406c-96dc-4470f64a651d/Zmeny-v-Sazebniku-KB-platne-od-1-11-2026.pdf)). Závažnost pro hotovostní obory odhadem vysoká. | Gastro, maloobchod, služby s denní tržbou; majitel, provozní. | Obchodní model: banka přenáší hotovost na samoobslužné kanály. | Moneta [ruší pokladny v některých městech](https://tn.nova.cz/zpravodajstvi/clanek/636822-znama-banka-rusi-pokladny-nektere-budou-fungovat-jen-dvakrat-v-tydnu); naopak [sdílené vkladové bankomaty](https://www.kb.cz/cs/o-bance/tiskove-zpravy/ke-sdilenym-vkladovym-bankomatum-se-pripojuje-unicredit-bank-klienti-komercni-banky-nove-vlozi) (1,8 mil. vkladů od 8/2024). | silná (ceníky), neznámá (dopad) |
| D2 | Přijímání karet je mimo hlavní bankovnictví a od 2027 ho změní EET 2.0. | Měřeno: zákon vyhlášen 7. 10. 2026, od 1. 1. 2027 se evidují hotovostní a kontaktní (kartové) platby, platba přes e-shop bránu ne; živnostník v prvním pásmu paušální daně se může evidenci vyhnout za 1 400 Kč měsíčně navíc ([Forvis Mazars](https://www.forvismazars.com/cz/cs/prehledy/forvis-mazars-v-mediich/archiv-2026/navrat-eet-se-blizi), [Seznam Zprávy](https://www.seznamzpravy.cz/clanek/315961)). Dopad na banky odhad. | Obchodníci s hotovostí a terminály, gastro; majitel, účetní. | Regulatorní. | Fio zlevňuje terminály pro obchodníky v 2. pololetí 2026 ([e15](https://www.e15.cz/finexpert/banky-a-ucty/fio-banka-ma-novinky-zlevnuje-platebni-terminaly-pridava-letistni-salonky-i-fast-track-1434022)). | silná (pravidla), hypotéza (dopad na banky) |
| D3 | U zahraničních plateb a výměny měn není na první pohled vidět, kolik přesně stojí. | Měřeno: nákup v zahraničí s kartou má u ČSOB a Fia přírážku v rozmezí asi 2,4–3,1 % ([Levnocestování](https://levnocestovani.cz/blog/post/ktere-banky-maji-nejlepsi-kurzy-pri-platbe-v-zahranici), 9/2025, spotřebitelský kontext); Wise ([dodavatel konkurence](https://wise.com/cz/blog/platba-v-usd)) uvádí rozdíl 2–4 %. | E-shopy, dovozci a vyvozci, IT služby; FD, účetní. | Obchodní model (marže na kurzu) a technická (řetěz bank u SWIFT). | HK ČR: při exportním financování se 72,7 % firem obracelo na svou stávající banku, překážkou je administrativa ([HK ČR](https://www.businessinfo.cz/clanky/pruzkum-hk-cr-firmy-maji-zajem-o-exportni-financovani-a-pojisteni-potykaji-se-ale-s-prekazkami-pri-jejich-vyuzivani/), rok neověřen). | anekdotická až střední |
| D4 | Firmy s cizinci mezi vlastníky nebo expanze do zahraničí narazí na obtížné otevírání účtů. | Měřeno: nic. České firmy účty v EU shledávají obtížně a ČNB do rozhodování bank nevstupuje ([Forbes](https://forbes.cz/ucet-v-zahranici-mate-smulu-slysi-ceske-firmy-od-bank/)). | Start-upy, firmy s cizinci, exportní firmy; majitel. | Regulatorní (AML a skutečný majitel). | Zahraniční investoři v ČR ([epravo](https://www.epravo.cz/top/aktualne/zahranicni-investori-to-v-cr-nemaji-snadne-od-zacatku-113024.html?pdf=1)); analytik Banky.cz radil ukrajinskému majiteli s.r.o. obrátit se na největší banky ([banky.cz](https://www.banky.cz/stitky/firemni-ucet/), 2023). | anekdotická |

### E. Financování

| ID | Problém lidsky | Četnost a závažnost | Koho postiženo | Příčina | Příklady | Důkazy |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | Úvěr trvá týdny, vyžaduje mnoho podkladů a začínající firmy často neuspějí. | Měřeno: v průzkumu Ipsos pro AMSP a ČS (10/2025, n = 301 MSP) 31 % firem žádá uvolnění úvěrových kritérií a 30 % větší flexibilitu financování ([Ipsos](https://www.amsp.cz/media/amsp/15913/ipsos-pro-amspvysledky-pruzkumu-2025-financni-zdravi-a-inovace-v-bankovnictvi.pdf)). UK: dvě třetiny firem hledajících financování má potíže ([RFI Global](https://rfi.global/?p=48252), 2025). | Začínající firmy, sezónní obory, OSVČ; majitel, FD. | Procesní a rizikové modely banky. | Vyřízení může trvat několik týdnů a vyžaduje daňová přiznání, potvrzení o bezdlužnosti, výpisy a často plán ([businessinfo](https://www.businessinfo.cz/clanky/zacinajici-podnikatele-na-uver-od-banky-casto-nedosahnou-co-s-tim/), rok neuveden); starší průzkum HK ČR: dvě třetiny firem si stěžovaly na nevstřícnost bank ([ČT24](https://ct24.ceskatelevize.cz/clanek/ekonomika/male-podniky-maji-problem-ziskat-pujcku-banky-jim-neveri-313791), cca 2020–21, datum nepotvrzeno). | střední |
| E2 | OSVČ s nízkým vykazovaným základem daně vypadají pro banku slabé i při dobrém obratu. | Měřeno: nic. Příběh čtenaře s obratem 350 tis. Kč měsíčně, kterému úvěr nedali ([Energozrůti](https://energozrouti.cz/clanek/pausalni-dan-uver-banka), 3/2026). | OSVČ na paušální dani, živnostníci; majitel. | Procesní: banky hodnotí příjem z daňového přiznání. | Každá banka účtuje bonitu OSVČ jinak ([Energozrůti](https://energozrouti.cz/clanek/banka-hypoteka-podnikani-osvc-pujcka)); starší průzkum: úvěr přes rodné číslo je jednodušší než přes IČO ([businessinfo](https://www.businessinfo.cz/clanky/podnikatele-preferuji-resit-vse-s-jednou-bankou-zjistil-pruzkum/)). | anekdotická |

### F. Podpora, poplatky, změna banky, výpadky, bezpečnost

| ID | Problém lidsky | Četnost a závažnost | Koho postiženo | Příčina | Příklady | Důkazy |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | V krizi (zablokovaná platba, zmražený účet) se firma těžko dostane k člověku, který rozhodne. | Měřeno: v UK 50 % MSP (n = 2 250, 6/2025) není spokojeno s proaktivní radou hlavní banky ([RFI Global](https://rfi.global/?p=48252)); k dostupnosti podpory jsou jen recenze. CZ: žádná data. | Klienti fintechů v krizi, malé firmy bez bankéře; majitel. | Obchodní model: levný automatizovaný servis, eskalace až na konci. | Revolut: [desítky agentů, žádná finální odpověď](https://www.trustpilot.com/review/business.revolut.com) (recenze 2026); Qonto: [bez telefonu a bez reakce v chatu](https://www.trustpilot.com/review/qonto.com?page=10) (1/2026). Obě služby mají tisíce velmi pozitivních recenzí. | anekdotická (fintech), střední (UK rada) |
| F2 | Ceny a podmínky se mění často a „zdarma“ neznamená bez poplatků. | Měřeno: největší požadavek firem na banky je nižší poplatky a jednodušší ceník, uvádí ho 46 % ([Ipsos](https://www.amsp.cz/media/amsp/15913/ipsos-pro-amspvysledky-pruzkumu-2025-financni-zdravi-a-inovace-v-bankovnictvi.pdf), 10/2025; spoluzadavatel ČS). | Všechny segmenty, nejvíc mikrofirmy; majitel. | Obchodní model: transakční poplatky kryjí náklady, výhody se ruší. | Air Bank ukončila k 30. 6. 2026 1 % zpět z karet bez výrazného upozornění; UniCredit od 1/2027 zdraží a ruší výběry zdarma u starších účtů ([Měšec](https://www.mesec.cz/n/bezne-ucty/)); „zdarma“ běžně znamená bez poplatku za vedení ([banky.cz](https://www.banky.cz/clanky/podnikatelsky-ucet-zdarma-kdy-za-nej-opravdu-nebudete-platit/)). | silná |
| F3 | Změna banky znamená nové číslo účtu a práci s fakturačními i dalšími systémy (hypotéza). | Měřeno: změna účtu nepřenáší číslo účtu a převod příkazů trvá až 13 pracovních dnů ([Air Bank](https://www.airbank.cz/file-download/2624-postup-pri-zmene-platebniho-uctu.pdf), [ČBA rádce](https://www.citfin.cz/wp-content/uploads/2018/08/20170221-R%C3%A1dce-p%C5%99i-zm%C4%9Bn%C4%9B-platebn%C3%ADho-%C3%BA%C4%8Dtu.pdf), 2017); zda tento postup platí i pro firmy, jsem neověřil. UK: 73 % MSP by změnu zvažovalo ([Censuswide pro CASS](https://www.startupdonut.co.uk/news/big-switch-uk-business-owners-rethink-their-banking), n = 1 000, 5/2025, zadavatel služba změny účtu). | E-shopy, firmy s API a automatizací, účetní; majitel. | Procesní: přechod je práce na straně firmy. | SK: během přechodu chodí platby stále na starý účet a nový účet je třeba ověřit ve všech nástrojích ([podnikajte.sk](https://www.podnikajte.sk/financny-manazment/prenos-podnikatelskeho-uctu-ako-prebieha)). | hypotéza, střední (pravidla) |
| F4 | Výpadky a odstávky blokují platby ve chvíli, kdy firma potřebuje platit nebo vybírat. | Měřeno: 9. 2. 2026 se do KB+ nemohly přihlásit statisíce klientů ([Blesk](https://www.blesk.cz/clanek/832811)); v červenci 2026 byly plánované víkendové odstávky u ČS, ČSOB, RB a mBank, pak výpadek ČSOB zasáhl 1,58 mil. klientů ([arecenze](https://www.arecenze.cz/clanky/vypadek-csob-zasahl-158-milionu-klientu-problemy-hlasi-i-mbank-zkoumali-jsme-jak-casto-se-to-deje/)). Dopad na firmy nikdo neměří. | Všechny firmy; výplatní dny, e-shopy, provozní. | Technická (nasazení nových aplikací, plánované odstávky, kyberútěky). | ČSOB CEB má plánovanou neprůchodnou noc 0:00–7:00 ([iPrima](https://cnn.iprima.cz/banky-v-cesku-hlasi-odstavky-co-nebude-fungovat-a-koho-se-to-dotkne-523439)). | silná (existence), neznámá (dopad) |
| F5 | Podvodníci volí jako „bankéř“ nebo „šéf“ a firmy přes zaměstnance s oprávněním posílají peníze. | Měřeno: KB varuje před falešnými bankéři a CEO fraudem miřícím na firmy ([KB](https://www.kb.cz/cs/o-bance/novinky/bezpecnost/falesne-telefonaty-a-utoky-podvodniku-cili-nejen-na-firmy-a-podnikatele), 5. 11. 2026); počet útoků na klienty všech bank v 1. čtvrtletí 2026 vzrostl o 4 % na téměř 24 tis. ([e15](https://www.e15.cz/finexpert/banky-a-ucty/komercni-banka-hlasi-narust-podvodu-s-kartami-a-platbami-o-41-procent-utocnici-meni-taktiky-1434777), data ČBA, ne jen firmy). | Účetní, zaměstnanec s oprávněním, FD. | Lidská (sociální inženýrství); od PSR se mění odpovědnost bank. | Představovaní obchodního partnera se změnou účtu na faktuře s razítky ([Seznam Zprávy](https://www.seznamzpravy.cz/clanek/ekonomika-firmy-a-penize-jsou-pryc-ceskem-bezi-novy-bankovni-podvod-262540)). | střední |
| F6 | Neziskovky a spolky dostanou „normalní“ firemní produkt s poplatky, který jim nesedí. | Měřeno: nic aktuálního. | Spolky, SVJ, charity; členové výboru bez bankovních zkušeností. | Obchodní: malý výnos, malé přizpůsobení. | Analytik Banky.cz uvádí, že Fio nabízí spolkům vedení zdarma ([banky.cz](https://www.banky.cz/poradna/bezny-ucet/?pl=26)); starší článek: neziskovka dostala jen standardní podnikatelský účet s vysokými poplatky ([businessinfo](https://www.businessinfo.cz/clanky/bankovni-poplatky-nejhur-jsou-na-tom-male-firmy-a-charita/), starší). | anekdotická, starší |
| F7 | SK: platební transakce podléhají transakční dani, kterou některé banky aspoň částečně kompenzují. | Měřeno: zákon platí od 1. 1. 2025, první zdaněné období byl duben 2025 ([VÚB](https://www.vub.sk/document/documents/VUB/transakcna-dan/ebook_transakcna_dan_mastercard.pdf)); Tatra banka živnostníkům uhradí daň za rok 2025 ([Tatra banka](https://www.tatrabanka.sk/sk/blog/tlacove-spravy/tatra-banka-zjednodusila-proces-otvarania-uctov-podnikatelov)). | SK živnostníci a malé firmy; majitel. | Regulatorní (daň). | Dopad na chování firem (hotovost, účty) jsem nenalezl. | silná (existence), neznámá (dopad) |

## Skryté problémy

To, co by člověk bez zkušenosti s firmou nikdy nehledal, se týká hlavně práva, odpovědnosti a administrativy, ne vzhledu aplikace; polovina položek nižše je přitom dána zákonem nebo ceníkem, tedy pevně.

| # | Skrytý problém | Proč ho člověk bez firmy nečeká | ID | Důkazy |
| --- | --- | --- | --- | --- |
| 1 | Firma nemá právní nárok na účet; právo na základní platební účet mají jen spotřebitelé ([Forbes](https://forbes.cz/maji-firmy-pravo-na-bankovni-ucet-krypto-byznys-ma-jasno-vlada-vaha/)). | U osobního účtu je odmítnutí nezvyklé, u firmy často ne. | A1 | silná |
| 2 | Bez účtu se firma nemůže dostat k DPH; číslo účtu se hlásí úřadům, a s.r.o. musí mít účet, jakmile vklady přesahnou 20 000 Kč ([Forbes](https://forbes.cz/maji-firmy-pravo-na-bankovni-ucet-krypto-byznys-ma-jasno-vlada-vaha/), [banky.cz](https://www.banky.cz/clanky/podnikatelsky-ucet-zdarma-kdy-za-nej-opravdu-nebudete-platit/)). | Odmítnutí banky tak zablokuje celý start, ne jen jednu službu. | A1 | silná |
| 3 | Firma s více jednateli, kteří jednají společně, často nemůže založit účet online a musí na pobočku nebo do firemního centra ([KB](https://www.kb.cz/cs/podnikatele-a-firmy/sjednejte-si-podnikatelsky-ucet), [Moneta](https://www.banky.cz/clanky/moneta-umoznuje-vybranym-sro-zalozit-firemni-ucet-kompletne-online/)). | „Online za pár minut“ platí jen pro nejjednodušší strukturu. | A2 | silná |
| 4 | Prověřování nikdy nekončí: dotazník v aplikaci, hlášení změn příjmů, doklady o původu peněz; bez nich banka platbu odmítne nebo účet ukončí ([arecenze](https://www.arecenze.cz/clanky/banky-cechum-hlidaji-kazdou-platbu-2026-o-hlaseni-uradu-mlci-trestnim-oznamenim-konci-zhruba-kazde-desate/)). | Člověk čeká jednorázové ověření při založení. | A3 | střední |
| 5 | Banka vám nesmí říct, že platbu nahlásila úřadu; peníze lze zdržet 24 hodin a pak až další dva tři pracovní dny ([FAÚ](https://fau.gov.cz/files/instituty-omezeni-vlastnickeho-prava-na-zaklade-zakona-o-aml.pdf)). | Banka mlkí zákonně, takže podpora nemůže ukázat, „co je špatně“. | A3 | silná |
| 6 | Spor s bankou řeší soud, ne arbitr; arbitr je určen spotřebitelům ([gov.cz](https://portal.gov.cz/sluzby-vs/reseni-spotrebitelskych-sporu-u-financniho-arbitra-S12252)). | Spotřebitel má levnou cestu, firma ne. | A4 | střední (ověřit u arbitra) |
| 7 | Banka může z formy ukončit smlouvu, např. po nepřevzatém dopisu, a účet je hned nedostupný ([banky.cz](https://www.banky.cz/poradna/banka-mi-zrusila-ucet-27552/), 2/2026). | Člověk čeká výstrahu a lhůtu. | A4 | anekdotická |
| 8 | Změna opravňující osoby (nová účetní, odchod zaměstnance) je administrativa u banky a běžně se bez ní neobejde. | Hypotéza: nenalezl jsem přímý zdroj, přesto je to první věc k ověření v rozhovorech. | B1 | hypotéza |
| 9 | Účetní potřebuje data ve formátu pro svůj program; každá banka dodává jiný a API může být placené ([Money S3](https://money.cz/navod/import-vypisu-a-export-platebniho-prikazu/), [KB ceník](https://www.kb.cz/getmedia/2a3093db-9b2e-49c4-b530-993d221ebde9/cenik-produktu-a-sluzeb-pro-fyzicke-osoby-podnikatele-a-pravnicke-osoby-zmeny.pdf)). | Pro člověka bez firmy je výpis jen PDF. | C1 | střední |
| 10 | Název firmy v bance musí sedět s tím, co zadá plátce, jinak ověření příjemce ukáže neshodu; banky se liší v tom, co přesně porovnávají ([podnikajte.sk](https://www.podnikajte.sk/technologie/sluzba-overenie-prijemcu-platby-od-oktobra-2025)). | Fyzická osoba má jedno jméno, firma název, zkratku a právní formu. | B2 | střední |
| 11 | „Zdarma“ běžně znamená bez měsíčního poplatku za vedení; hotovost, výpisy, API a zahraniční platby se účtují zvlášť ([banky.cz](https://www.banky.cz/clanky/podnikatelsky-ucet-zdarma-kdy-za-nej-opravdu-nebudete-platit/), [KB změny](https://www.kb.cz/getmedia/c1eaaab5-6a89-406c-96dc-4470f64a651d/Zmeny-v-Sazebniku-KB-platne-od-1-11-2026.pdf)). | Spotřebitelé mají mnoho služeb v balení zdarma. | F2 | silná |
| 12 | Banka hodnotí daňové přiznání, ne obrat; OSVČ na paušální dani má nízký vykazovaný základ ([Energozrůti](https://energozrouti.cz/clanek/pausalni-dan-uver-banka)). | Člověk čeká, že obrat stačí. | E2 | anekdotická |
| 13 | Změna banky znamená nové číslo účtu, které firma musí změnit v e-shopu, na fakturách, ve smlouvách a v API ([Air Bank](https://www.airbank.cz/file-download/2624-postup-pri-zmene-platebniho-uctu.pdf), [podnikajte.sk](https://www.podnikajte.sk/financny-manazment/prenos-podnikatelskeho-uctu-ako-prebieha)). | U mobilního čísla je přenos běžný. | F3 | střední |
| 14 | Změna čísla účtu u obchodního partnera přijde na faktuře s razítky a je to podvod ([Seznam Zprávy](https://www.seznamzpravy.cz/clanek/ekonomika-firmy-a-penize-jsou-pryc-ceskem-bezi-novy-bankovni-podvod-262540)). | U soukromých plateb se čísla účtu nemění. | F5 | střední |
| 15 | Od 1. 1. 2027 se vrací EET 2.0 pro hotovostní a kartové platby v provozovnách ([Forvis Mazars](https://www.forvismazars.com/cz/cs/prehledy/forvis-mazars-v-mediich/archiv-2026/navrat-eet-se-blizi)). | Není to bankovní téma, a přesto mění chování zákazníků vůči bance a terminálům. | D2 | silná |

## Co firmy od banky chtejí a co je nadchlo

Nejsilnější změřený signal z ČR je, že firmy chtejí nižší a srozumitelnější poplatky (46 %) a že banka zaostává hlavně v proaktivní podpoře: největší mezera mezi tím, co firmy považují za důležité, a tím, co jim vlastní banka dává, je u pomoci s včasnou úhradou závazků (77 % vs. 46 %).

**Co firmy po bankách žádají** (Ipsos pro AMSP a ČS, 10/2025, n = 301 MSP se 4–250 zaměstnanci, firmy mohly uvést více odpovědí; ČS byla spoluzadavatel, takže zkreslení je možné; [zpráva](https://www.amsp.cz/media/amsp/15913/ipsos-pro-amspvysledky-pruzkumu-2025-financni-zdravi-a-inovace-v-bankovnictvi.pdf)):

| Požadavek | Podíl firem |
| --- | --- |
| Nižší poplatky a jednodušší ceník | 46 % |
| Rychlejší a efektivnější bankovní procesy | 32 % |
| Uvolnění úvěrových kritérií | 31 % |
| Větší flexibilita financování | 30 % |
| Další digitální nástroje | 22 % |
| Vzdělávací a konzultační programy pro MSP | 13 % |

**Kde je mezera mezi důležitostí a nabídkou** (stejný průzkum; „poskytuje“ je vnímání respondenta u jeho banky; mezera = můj výpočet rozdílu):

| Služba | Důležité | Poskytuje banka | Mezera (procentní body) |
| --- | --- | --- | --- |
| Podpora při včasném placení závazků | 77 % | 46 % | 31 |
| Podpora investic do rozvoje | 81 % | 54 % | 27 |
| Upozornění na situace ovlivňující finance | 83 % | 58 % | 25 |
| Služby za výhodných podmínek | 85 % | 70 % | 15 |
| Výhodné platební podmínky | 86 % | 72 % | 14 |
| Úvěrové produkty za výhodných podmínek | 78 % | 65 % | 13 |

Jediná položka, kde nabídka dosahuje očekávání, je přehled příjmů a výdařů v internetovém a mobilním bankovnictví (76 % důležité, 77 % poskytuje).

**Co firmy nadílilo** (vše z dostupných zdrojů, často z tiskových zpráv bank, tedy jako popis nabídky, ne změřená spokojenost):

- **Online účet za minuty.** ČSOB nabízí firmám oficiálně online otevírání od roku 2022 ([ČSOB](https://www.pruvodcepodnikanim.cz/clanek/pruzkum-csob-optimismus-firem-v-cesku-stoupl-na-trilety-vrchol-trumpova-cla-se-zatim-neprojevila/)), Moneta přes Bank iD ([banky.cz](https://www.banky.cz/clanky/moneta-umoznuje-vybranym-sro-zalozit-firemni-ucet-kompletne-online/)); u fintechů recenze opérálně chválí snadné otevírání ([Qonto na Trustpilotu](https://www.trustpilot.com/review/qonto.com?page=9)).
- **Vestavěné nástroje místo dalších aplikací.** Moneta nabízí bezplatný export karet do účetnictví přes API a online fakturaci; Air Bank umožňuje fakturaci z mobilu ([Měšec](https://www.mesec.cz/n/podnikatelske-ucty/)).
- **Schvalování v mobilu.** KB nabízí [hromadnou autorizaci plateb](https://www.kb.cz/cs/podpora/ucty-a-platby/hromadna-autorizace-plateb-v-mobilni-banka-business) v aplikaci.
- **Hotovost mimo pobočku.** Sdílené vkladové bankomaty zvládly od srpna 2024 přes 1,8 mil. vkladů ([KB](https://www.kb.cz/cs/o-bance/tiskove-zpravy/ke-sdilenym-vkladovym-bankomatum-se-pripojuje-unicredit-bank-klienti-komercni-banky-nove-vlozi), 2/2026).
- **Fintech jako inspirace.** Uživatelé chválí intuitivní aplikaci a sledování transakcí v reálném čase ([Financer o Revolut Business](https://www.financer.com/review/revolut-business)); UK průzkum řadí odměny, zákaznický servis a digitální schopnosti mezi hlavní faktory spokojenosti ([RFI Global](https://rfi.global/press-release-fintechs-gain-ground-as-uk-smes-rethink-banking-relationships/)).

**Benchmarky** (vždy s územím; zahraniční čísla nepřenáším na ČR):

| Ukazatel | Hodnota | Území, rok, vzorek |
| --- | --- | --- |
| Spokojenost s hlavní bankou | 70 % | UK, 6/2025, n = 2 250 ([RFI Global](https://rfi.global/?p=48252)) |
| MSP využívající fintech pro firemní bankovnictví | 50 % (před pěti lety zhruba třetina) | UK, 6/2025, n = 2 250 |
| Týdenní používání mobilní aplikace banky | více než 50 % (2019: třetina) | UK, 6/2025, n = 2 250 |
| Vnímaná dostupnost bankovních služeb | 79 % dobrá, 3 % špatná | CZ, 10/2025, n = 301 ([Ipsos](https://www.amsp.cz/media/amsp/15913/ipsos-pro-amspvysledky-pruzkumu-2025-financni-zdravi-a-inovace-v-bankovnictvi.pdf)) |
| Okamžité platby jako podíl všech úhrad | 40 % | CZ, 6/2025 ([banky.cz](https://www.banky.cz/clanky/okamzite-platby-umi-uz-8-bank-a-dalsi-pribydou-v-nejblizsich-tydnech/)) |
| Hrdost na banku jako partnera | 29 % (Fio) až 44 % (ČSOB) | CZ, 10/2025, n = 301 |

## Srovnání: tradiční banky vs. fintech, ČR/SK vs. zahraničí, kanály

Srovnání je tu záměrně opatrné: jediná zmapovaná čísla o firmách jsou z Velké Británie a z Česka a jsou z různých průzkumů, takže se nedají přímo srovnávat. Kde chybí česká data, je to řečeno výslovně.

### Tradiční banky vs. fintech

| Téma | Tradiční banky (ČR/SK) | Fintech (Revolut Business, Wise, Qonto aj.) | Důkazy |
| --- | --- | --- | --- |
| Otevření účtu | Postupně online (KB jen pro s.r.o. s jedním jednatelem, Moneta pro vybrané s.r.o., Air Bank i pro více jednatelů od 23. 1. 2026); jinak často pobočka | Recenze opakovaně chválí snadné otevření, ale i jejich pozdější bloky | střední (tiskové zprávy bank; anekdotické recenze na [Trustpilotu](https://www.trustpilot.com/review/qonto.com?page=9)) |
| Podpora | Pobočka a telefon; stížnosti míří spíš na pomalé procesy | Opakovaná stížnost: žádný telefon, těžko dostupný člověk při zablokování | anekdotické ([Financer](https://www.financer.com/review/revolut-business)) |
| Blokace a uzavření účtu | Důvody se firmě často nesdělují; FAÚ blokace obvykle 2–3 dny | Uzavření bez vysvětlení a zmrazené prostředky na měsíce jsou nejčastější popsaná křivda | anekdotické; ve Velké Británii ombudsman bere uzavření jako obchodní rozhodnutí banky |
| Nástroje a rozhraní | Aplikace i API (např. KB API Business, Moneta export karet), často za poplatek | Chváleny intuitivní aplikace a sledování transakcí v reálném čase | střední |
| Zahraniční platby | Dražší a pomalejší, hlavní bolest exportérů a importérů | Hlavní konkurenční výhoda fintechů, ale bez českého úvěru a poboček | hypotéza, nepodloženo českým měřením |
| Úvěr a poradenství | Plný produktový rozsah; firmy chtějí volnější kritéria (31 %) | Úvěr je užší nabídka | střední (CZ Ipsos 2025) |

**Co z toho plyne.** Fintech vyhrává u prvního dojmu a nástrojů, tradiční banka u úvěru, hotovosti a lidského kontaktu. Oba typy sdílejí totéž slabé místo: když se něco zablokuje, firma nemá jasný postup ani nezávislého rozhodčího. Finanční arbitr řeší jen spory spotřebitelů ([gov.cz](https://www.financnyarbitr.cz/)), podnikatelské spory vedou k soudu.

### ČR a SK vs. zahraničí

| Ukazatel | ČR / SK | Zahraničí | Poznámka |
| --- | --- | --- | --- |
| Spokojenost s hlavní bankou | Dostupnost služeb hodnotí dobře 79 % (jiná otázka než spokojenost) | UK 70 % spokojených, 50 % nespokojených s proaktivní radou | Nesrovnatelné otázky, **chybí česká přímá spokojenost** |
| Ochota přejít | Česká data nejsou | UK 29 % ([RFI Global](https://rfi.global/press-release-fintechs-gain-ground-as-uk-smes-rethink-banking-relationships/)); 73 % by zvážilo změnu v průzkumu sponzorovaném službou pro přechod | Druhé číslo je pravděpodobně nadsazené sponzorem |
| Okamžité platby | 40 % všech českých úhrad (6/2025); povinné SEPA Instant v eurech od 7/2027 | Nepřeneseno | Česko je v tomto bodě vpředu |
| Ověření příjemce (VoP) | Povinné pro české banky u eurových plateb SEPA od 2027 | EU legislativa | Nový zdroj tření i ochrany |
| Odpovědnost za podvody | PSD3/PSR: podvody typu impersonation přesouvají odpovědnost na poskytovatele, texty finalizovány 23. 4. 2026, vyhlášení očekáváno do konce 2026 (zdroje se liší) | EU | Dopad na firmy zatím nejasný |
| Daň z transakcí (SK) | Od 1. 1. 2025 dotýká i firem | Neplatí jinde v EU | Slovenská specifika |

### Mobil vs. web vs. pobočka

Tohle srovnání není podložené českým měřením. Dostupné jsou jen tyto stopy:

- Ve Velké Británii používá mobilní banku týdně více než polovina firem, před šesti lety třetina (RFI Global, 6/2025).
- Česká data o podílu firem v mobilu, webu a na pobočce, o dokončování úkolů v jednotlivých kanálech ani o chybovosti nenašla ani jedna z použitých rešerší.
- Funkční rozdíly jsou doložené jen z nabídky bank: hromadná autorizace v mobilu (KB), fakturace z mobilu (Air Bank), hotovost na pobočce nebo ve sdílených vkladomatech.

| Kanál | Kdy se podle dostupných zdrojů používá | Co chybí |
| --- | --- | --- |
| Mobil | Schvalování plateb, drobné úkony, upozornění | Česká měření, rozdíl mezi rolemi (majitel vs. účetní) |
| Web / internetové bankovnictví | Dávky plateb, export pro účetnictví, správa rolí | Česká měření dokončování úkolů |
| Pobočka | Otevření účtu u složitějších firem, hotovost, řešení blokace | Podíl firem, které pobočku skutečně potřebují |

## Rozdíly podle segmentu a role

Česká data podle segmentu a role prakticky neexistují: Ipsos pro AMSP a ČS (10/2025) pokrývá firmy se 4–250 zaměstnanci a neříká nic o OSVČ ani o jednotlivých rolích. Níže proto jsou **hypotézy** odvozené z mechanismu problémů (ID odkazují do taxonomie) a z popísaných případů, ne změřené rozdíly. Pro ověření slouží výzkumné otázky v další sekci.

### Segmenty

| Segment | Co je pro ně pravděpodobně nejvíc tíživé | Související ID | Síla důkazů |
| --- | --- | --- | --- |
| OSVČ (fyzická osoba podnikající na vlastní jméno) | Směšování osobního a podnikatelského účtu, slabší posouzení příjmů při paušální dani, EET 2.0 od 1. 1. 2027 | E2, D2 | hypotéza, střední u právní změny |
| Mikrofirmy | Ceník a poplatky (46 % žádá nižší), pomalé procesy | F2 | střední (užší vzorek 4–250 zaměstnanců) |
| Střední firmy | Role, limity a schvalování, integrace do účetnictví | B1, C1 | hypotéza |
| E-shopy | Přijímání plateb, párování podle variabilního symbolu, výpisy v účetním softwaru | C2, D2 | střední (UK ombudsman: vypořádání obchodníka nebylo vidět v účetnictví) |
| Startupy | Odmítnutí nebo zavření účtu bez vysvětlení, zahraniční spoluzakladatelé | A1, D4 | anekdotické |
| Import / export | Zahraniční platby, kurzy, pomalost | D3 | hypotéza |
| Hotovostní obory | Poplatek za neuskutečněný oznámený výběr u KB (0,5 %, min. 1 000, max. 5 000 Kč); AML otázky | D1, A3 | střední u ceníku |
| Nezisk. organizace | Členové výboru bez bankovních zkušeností, poplatky | F6 | slabé (starší zdroj) |
| Firmy v prvním roce | Účet otálí on-boarding a AML dotazy v době, kdy je firma nejzranitelnější | A2, A3 | hypotéza |

### Role

| Role | Co potřebuje a co ho zdržuje | ID | Síla důkazů |
| --- | --- | --- | --- |
| Majitel | Rychlé rozhodnutí, pochopitelné poplatky, strach z blokace účtu | A1, F2, F4 | hypotéza |
| Finanční ředitel (CFO) | Přehled a predikce, limity a schvalování, zahraniční platby | B1, D3 | hypotéza |
| Účetní | Formáty exportů (ABO, MT940, camt), párování plateb, nové poplatky za camt.052 od 1. 11. 2026 u KB | C1, C2 | střední (ceník) |
| Omezený zaměstnanec (např. pokladní, řidič) | Karta s limitem, jednoduché schválení, řešení sporů bez přístupu k účtu | B1 | hypotéza |

**Co je vidět.** Banka má jednoho „účtového zákazníka“, ale firmu tvoří role s opačnými potřebami: majitel chce klid, účetní přesná data, CFO kontrolu a zaměstnanec rychlost. Z českých zdrojů nevíme, která z těchto rolí na bankách ztrácí nejvíc času.

## Příležitosti

Všechno níže je **interpretace** postavená na zdrojích v této rešerši, ne ověřená potřeba. Rychlé výhry jsou změny, které nevyžadují nové produkty ani integrace; strategické vyžadují větší investici.

### Rychlé výhry

| Nápad | Jaký problém řeší | ID | Opora |
| --- | --- | --- | --- |
| Změny ceníku oznámit člověku, který ho zaplatí (e-mail, upozornění v aplikaci, shrnutí „co se vám změní v Kč“) | Ukončení cashbacku u Air Bank bez zřetelného upozornění; změny UniCredit od 1/2027 | F2 | střední |
| Průvodce „před otevřením účtu“: jaké doklady, kdo musí přijít, jak dlouho to trvá | Nejasné požadavky při otevírání, rozdíly podle počtu jednatelů | A2 | střední (podmínky se liší podle banky) |
| Vysvětlit AML dotazy a blokace jednou větou, co se děje a kdy to končí | FAÚ blokace obvykle 2–3 dny, firma neví proč | A3 | střední |
| Označit hotovostní poplatky před výběrem, ne až po něm | Poplatek za neuskutečněný oznámený výběr | D1 | střední |
| Vyjádřit, co se změní s VoP a okamžitými platbami | Nové povinnosti 2027 | B2 | hypotéza |
| Jedno místo se stavem výpadků a plánovaných odstávek | Výpadky ČSOB, KB+, víkendové odstávky 7/2026 | F4 | střední |

### Strategické příležitosti

| Nápad | Jaký problém řeší | ID | Opora |
| --- | --- | --- | --- |
| Proaktivní upozornění na situace ovlivňující finance a připomínky úhrad | Mezera 25 a 31 procentních bodů mezi důležitostí a nabídkou | viz Co firmy chtejí | střední (Ipsos) |
| Srozumitelný postup pro spor s bankou (lhůty, stav, co dělat) i bez nezávislého rozhodčího | Nezávislý rozhodčí pro firmy neexistuje | A4 | střední |
| Role, limity a schvalování s šablonami podle typu firmy | Správa rolí u menších týmů | B1 | hypotéza |
| Plynulý přechod mezi bankami (převod trvalých příkazů, výpisů) | Přechod je pracný, firmy zůstávají | F3 | hypotéza |
| Úvěr posuzovaný i z dat o účtu, rychlejší rozhodnutí | 31 % chce volnější kritéria, 32 % rychlejší procesy | E1, E2 | střední |
| Zahraniční platby s předem známou cenou a časem | Cena a trvání plateb do zahraničí | D3 | hypotéza |

### Nenaplněné potřeby (interpretace, bez českého měření)

- **Vidět, co se s žádostí děje.** Opakující se motiv v taxonomii (otevírání účtu, AML dotazy, blokace, spor) je nejistota, v jakém stavu věc je a kdy skončí. Nikdo ale v ČR neměří, kolik firm tato nejistota stojí.
- **Ochrana před podvody šítá na firmy.** Banky varují před falešnými bankéři a CEO fraudem (podvodný příkaz „zá šéfa“), ale z našich zdrojů není známo, zda firmy dostávají specifický nástroj, například druhého schvalovatele neobvyklých plateb.
- **Veřejné srovnání firemních bank.** Nenašli jsme žádný nezávislý český index; Ipsos měří jen hrdost na banku.

## Výzkumné otázky pro primární výzkum

Otázky vyplývají z mezer v datech (viz Metodika). U každé je uvedeno, co řeší, a metoda, kterou ji nejlépe zjistit.

| # | Otázka | Co řeší (ID) | Metoda |
| --- | --- | --- | --- |
| 1 | Jak dlouho trvá od první žádosti po funkční účet a kolikrát musí firma poslat doklad znovu? | A2 | Kvantitativní průzkum, deník |
| 2 | Kdo ve firmě prakticky účet otevírá (majitel, účetní, externí pomoc) a co mu brání dát to online? | A2 | Rozhovory |
| 3 | Jak firmy čtou a co říkají o dotazích AML (původ prostředků, doklady k platbám)? | A3 | Rozhovory, test srozumitelnosti |
| 4 | Kolik firem za poslední 2 roky zažilo blokaci, odmítnutí nebo zrušení účtu a co udělaly? | A1, A3, A4 | Kvantitativní průzkum |
| 5 | Kdo ve firmě opravdu schvaluje platby a kde na výchozí role a limity nestačí? | B1 | Rozhovory, pozorování |
| 6 | Co se změní pro firmy s VoP a okamžitými platbami a vidí to, nebo se to dozvídají až při první chybě? | B2 | Rozhovory, test prototypu |
| 7 | Jak účetní dává dohromady výpisy a platby a kolik času jí to měsíčně zabere? | C1, C2 | Pozorování při práci, deník |
| 8 | Kolik firem plácí za API nebo export (např. KB API Business) a vídí to předem? | C1 | Průzkum mezi účtovými |
| 9 | Kde se e-shopu rozchází platba, objednávka a výpis? | C2, D2 | Rozhovory s e-shopy |
| 10 | Které poplatky firmy nechtejí, které nezná a které je překvapily? | F2, D1 | Test ceníku, rozhovory |
| 11 | Které platby do zahraničí se zdržely, zdražily nebo selhaly a jak je firma řešila? | D3 | Průzkum exportérů |
| 12 | Jak firmy dostanou úvěr a kde se zasekne (dokumenty, čas, OSVČ s paušální daní)? | E1, E2 | Rozhovory, průzkum |
| 13 | Co firma zkouší, když narazí na problém, a kolik kontaktů s bankou potřebuje k vyřešení? | F1 | Deník, analýza případů |
| 14 | Co firmy způsobily výpadky a plánované odstávky a mají na ty chvíle náhradní řešení (druhá banka, karta)? | F4 | Průzkum, rozhovory |
| 15 | Setkali se s podvodem (falešný bankéř, CEO fraud) a co by jim pomohlo? | F5 | Průzkum, rozhovory |
| 16 | Proč firmy zůstávají u jedné banky a co by je přimělo přidat druhou nebo přejít? | F3 | Průzkum, rozhovory |
| 17 | Jak se liší zkušenost OSVČ, mikrofirmy a střední firmy? | Segmenty | Kvantitativní průzkum s kvotami |
| 18 | Co potřebují nezisk. organizace s dobrovolnickým výborem? | F6 | Rozhovory |
| 19 | Jak firmy poznají změnu ceníku a co s ní udělají? | F2 | Test e-mailů, rozhovory |
| 20 | Pro co firmy různých velikostí používají mobil, web a pobočku a kde jim který kanál nestačí? | Kanály | Průzkum, pozorování |

## Metodické poznámky

**Jak rešerše vznikla.** Data jsem sbíral z veřejně dostupných zdrojů k 27. 11. 2026: průzkum Ipsos pro AMSP a ČS, tiskové zprávy a ceníky bank, zpravodajství (banky.cz, Forbes), regulatorní texty, UK průzkumy (RFI Global, Censuswide) a recenze fintechů (Trustpilot, Financer, rozhodnutí britštího Financial Ombudsman Service). Hlavní česká číselná data jsou z Ipsosu, zbytek je kvalitativní.

**Co je měřené a co ne.** Měřená je jen menší část čísel (Ipsos, RFI Global, ceníky bank). Ostatní jsou příklady, tiskové zprávy nebo můj odhad; v taxonomii a ve slovníku je to u každého označeno.

### Zkreslení

- **Zadavatel.** Průzkum Ipsos zadaly AMSP a ČS; ČS je banka, takže otázky a výběr témat mohou být posunuty k tomu, co banka umí nabídnout. Podobně průzkum Censuswide (73 % by zvážilo změnu) pro CASS zadala služba pro přechod mezi bankami.
- **Tiskové zprávy bank.** Informace o online otevírání, hromadné autorizaci nebo vkladových bankomatech jsou nároky banky, ne měřená zkušenost.
- **Recenze a fóra.** Recenze na Trustpilotu a podobných webech psávají převážně lidé s výrazně špatnou nebo výrazně dobrou zkušeností; běžný průběh se v nich ztrácí. Jsou označeny jako anekdotické a žádná procenta z nich nepočítám.
- **Časové údaje.** Průzkumy jsou z let 2025–2026, některé starší zdroje jsou označeny: Tide (2017), průzkum HK ČR o úvěru (cca 2020–21, bez data), průzkum businessinfo o „jedné bance“ (bez data) a článek o poplatcích neziskových organizací (starší).

### Kde chybí česká a slovenská data

| Oblast | Stav |
| --- | --- |
| OSVČ a on-boarding | Ipsos nepokrývá OSVČ ani otevírání účtu; nenašel jsem žádné měření jeho trvání |
| Podpora a reklamace | Žádná česká data o čase odpovědi ani vyřízení |
| Úvěr | Chybí česká data o době posuzování i podílu zamítnutých žádostí; jen dotaz Ipsos (31 % žádá volnější kritéria) |
| Výpadky | Známy jednotlivé výpadky, ale ne dopad na firmy |
| Role a kanály | Není průzkum podle role (majitel, účetní) ani kanálu |
| Slovensko | Na Slovensku jsem našel hlavně zpravodajství (Tatra banka, daň z transakcí); dvě stránky s průzkumy (businessinfo o úvěru UCB, Tatra) se nepodařilo načíst, proto z nich mám jen údaje z výsledků vyhledávání |
| Obecné zahraniční studie | Eurostat, EBA a UX studie typu Nielsen Norman Group: nic konkrétního o firemním bankovnictví jsem nenašel |

### Co jsem nepoužil

- Recenze firemních aplikací v App Store a Google Play.
- Reddit a skupiny na Facebooku a LinkedInu.
- Žádné rozhovory ani vlastní měření; vše je ze sekundárních zdrojů.

Tyto zdroje by rozšířily anekdotickou stříšku názorů, ale nenahradí primární výzkum z předchozí sekce.

**Známé nejistoty.** Prahy u hotovostních poplatků se v zdrojích liší (0,5 mil. vs. 2 mil. Kč), proto je v tabulce uvádím jen u KB a se zdrojem. Termín vyhlášení PSD3/PSR v Oficiálním věstníku se v zdrojích liší. Tvrzení, že finanční arbitr není použitelný pro účty používané k podnikání, jsem neověřil u druhého zdroje.

## Zdroje

Odkazy jsou uvedeny u tvrzení v textu; zde je jejich přehled. Stav k 27. 11. 2026.

**Odkazy uvedené v textu**

- Ipsos pro AMSP a ČS, 10/2025: [Finanční zdraví a inovace v bankovnictví](https://www.amsp.cz/media/amsp/15913/ipsos-pro-amspvysledky-pruzkumu-2025-financni-zdravi-a-inovace-v-bankovnictvi.pdf)
- RFI Global, 6/2025: [Fintechs gain ground as UK SMEs rethink banking](https://rfi.global/press-release-fintechs-gain-ground-as-uk-smes-rethink-banking-relationships/)
- banky.cz: [okamžité platby, 6/2025](https://www.banky.cz/clanky/okamzite-platby-umi-uz-8-bank-a-dalsi-pribydou-v-nejblizsich-tydnech/); [Moneta, online účet pro s.r.o.](https://www.banky.cz/clanky/moneta-umoznuje-vybranym-sro-zalozit-firemni-ucet-kompletne-online/)
- KB: [hromadná autorizace plateb](https://www.kb.cz/cs/podpora/ucty-a-platby/hromadna-autorizace-plateb-v-mobilni-banka-business); [sdílené vkladové bankomaty, 2/2026](https://www.kb.cz/cs/o-bance/tiskove-zpravy/ke-sdilenym-vkladovym-bankomatum-se-pripojuje-unicredit-bank-klienti-komercni-banky-nove-vlozi)
- [Průvodce podnikáním: ČSOB, průzkum](https://www.pruvodcepodnikanim.cz/clanek/pruzkum-csob-optimismus-firem-v-cesku-stoupl-na-trilety-vrchol-trumpova-cla-se-zatim-neprojevila/); [Měšec: podnikatelské účty](https://www.mesec.cz/n/podnikatelske-ucty/)
- Fintech recenze (anekdotické): [Qonto na Trustpilotu](https://www.trustpilot.com/review/qonto.com?page=9); [Financer: Revolut Business](https://www.financer.com/review/revolut-business)
- [Finanční arbitr](https://www.financnyarbitr.cz/)

**Zdroje použité v analýze, jejichž přesný odkaz tento přehled nenese** (je třeba je dohledat před citací): Forbes 2023 o právu na účet pro právnické osoby; arecenze 31. 10. 2026 (výroční zpráva FAÚ 2025); Censuswide pro CASS, 5/2025; UniCredit (VoP, změna ceníku 1/2027); zprávy o EET 2.0 (zákon vyhlášen 7. 10. 2026); PSD3/PSR; zprávy o výpadcích ČSOB a KB+; varování KB z 5. 11. 2026; ČBA za 1. čtvrtletí 2026; rozhodnutí FOS (DRN-5568416); Tide 2017; HK ČR o úvěru (cca 2020–21); businessinfo (jedna banka, nezisk. organizace).
