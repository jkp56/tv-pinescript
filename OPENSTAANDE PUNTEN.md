# Openstaande punten – Trade Lijnen

Regels uit het tradeplan die nog niet (of maar voorlopig) in `trade_lines.pine` (v1.10.0) en `trade_lines_strategie.pine` (v1.4.0) zitten, plus de vragen die eerst beantwoord moeten worden. Bijgewerkt: 2026-11-06.

Vaste uitgangspunten (bevestigd):

- Support/Resistance en de bijbehorende Targets worden bepaald op de **30m**.
- Een geldige trade kan ontstaan op de **30m of de 15m**, op de **eerste** candle die voorbij het level sluit.
- Bij het bepalen van een break spelen **wicks geen rol**: alleen de close telt.
- Er zijn **twee sessies**: **06:00–10:00** en **12:00–16:00**, beide in de tijdzone **Europe/Amsterdam** (nu UTC+1, in de zomer UTC+2). Het plan noemt alleen de eerste sessie; de tweede is een aanvulling van de gebruiker.
- **De indicator toont bewust alle mogelijke trades van de dag**, ook buiten de sessies. Dat laat zien hoeveel trades er optreden, genomen of niet. Of een trade binnen of buiten een sessie viel, legt de gebruiker vast in de eigen logging. Er komt dus **geen sessiefilter** in de indicator, en ook **niet in de strategie**.
- **"1 TP of 1 SL per dag" en het aantal trades per dag** worden ook in de logging bijgehouden. De scripts beperken het aantal trades per dag niet.
- **Of een trade binnen een sessie valt, bepaalt het moment van de break**: de close van de break-candle valt binnen 06:00–10:00 of 12:00–16:00. De entry mag daarna komen. Een break-candle die precies om 10:00 of 16:00 sluit, telt mee. De sessiegrenzen worden op het scherm met ongeveer ±15 minuten marge getoond; hoe strikt de grenzen worden gerespecteerd, is de beslissing van de gebruiker.
- **Een trade die eenmaal gezet is, loopt door** tot TP, SL of break-even, ook na het einde van de sessie.
- **De ranges worden doorlopend geëvalueerd**, na elke 30m-candle. Dat doet het script al. "Vóór 06:00 intekenen" betekent dus niet dat de levels voor de hele sessie vastliggen.

---

## 0. Huidige instellingen (v1.10.0)

Hieronder staat hoe het script nu beslist, per groep in het Inputs-tabblad, met de standaardwaarde tussen haakjes. Het is bedoeld als startpunt voor de punten hieronder. De volledige uitleg per instelling staat in [HANDLEIDING.md](HANDLEIDING.md), hoofdstuk 6.

Over ticks: op XAUUSD en NAS100 bij FXCM is 1 tick 0,01. Dus 50 ticks = 0,50 en 1000 ticks = 10,00, op goud in $ en op NAS100 in punten.

### Rekenfeed: op welke prijzen gerekend wordt

- **Berekeningen op andere feed** (aan) en **prefix** (`FX`): alles wordt berekend op FXCM, ook als je op een FTMO_OANDA-chart kijkt. Levels, SL, TP en lotgrootte zijn dus FXCM-prijzen.

### Support / Resistance: waar de lijnen liggen (altijd op 30m)

- **Max bars terugzoeken** (450): zo ver terug zoekt het script naar een geldige overgang.
- **Resistance** is de body-top van de laatste bullish → bearish-overgang die nog niet door een body doorbroken is. **Support** is het spiegelbeeld.
- **Target** is het eerstvolgende geldige level daarachter, minimaal **Minimale afstand Target** (300 ticks) van Resistance/Support. Ligt er een geldig level tussen dat te dichtbij ligt, dan schuift Resistance/Support daarnaartoe.
- **Fallback afstand target** (100 ticks): wordt alleen gebruikt als er geen geldig Target is. Er geldt dan nooit minder dan de minimale afstand.
- **Reversal-candle uitsluiten van eigen invalidatie** (aan): de candle die de overgang vormt, kan zijn eigen level niet ongeldig maken.
- **Body-tolerantie candle na de overgang** (uit, 50 ticks) en **body-tolerantie latere candles** (uit, 50 ticks): een body mag zoveel door een level gaan zonder het ongeldig te maken. Dit vangt kleine verschillen tussen brokers op.
- **Overgang over dagsluiting/weekend** (aan): na een gap is het level de open van de eerste candle na de gap, niet de close ervoor.

### Signaal: wanneer er een break is

- **Break-tolerantie** (0,01% van het level): de **30m-close** moet minimaal zoveel voorbij Resistance/Support sluiten, en de close daarvoor nog niet. Wicks tellen niet. Op XAUUSD (~4000) is dat ongeveer 0,40, op NAS100 (~27000) ongeveer 2,7 punt.
- Alleen de **eerste** close voorbij het level telt. Binnen het signaalvenster (zie SL) telt een nieuwe break in dezelfde richting niet als nieuw signaal.
- Er zijn nog **geen 15m-signalen** (zie punt 2).

### Stop Loss: waar de SL ligt

- **SL: aantal ticks van wick** (50): Long SL = low van de break-candle − 50 ticks, Short SL = high + 50 ticks. Hier tellen wicks dus wél.
- **SL: trailing** (uit): de SL blijft staan op de waarde van de break-candle.
- **SL: lijn actief na signaal** (2 candles van 30m): zo lang blijven SL, TP en de break-lijn zichtbaar. Dit is ook het venster tegen dubbele signalen.
- **Toon SL lijnen** (aan): uit zet ook de TP-lijn en de break-lijnen uit.

### Trade Mogelijkheid: of de trade geldig is

- **Entry** = close van de break-candle. **R** = afstand van de entry tot de SL.
- **TP: Risk/Reward** (1,2): TP = entry ± 1,2 × R.
- **Minimaal benodigde R/R-ruimte in de Range** (1,0): tussen de entry en het Target zoals dat vóór de break stond, moet minimaal 1,0 × R ruimte zijn.
- **Maximaal toegestane R** (1000 ticks): is R groter, dan is de trade niet mogelijk.
- **Rejection candle 15m** (uit, 50 ticks): sluit de tweede 15m-candle van de break-candle met minimaal 50 ticks body tegen de richting in, dan is de trade niet mogelijk.
- Is een voorwaarde niet gehaald, dan verschijnt het oranje blok "Trade niet mogelijk" met de reden. De alert gaat wel af.

### Lotgrootte: hoe groot de positie is

- **Account** ($10.000), **risico** (1%), **contractgrootte** (100, voor XAUUSD) en **commissie** ($6 per lot): lot = account × risico% / (R × contractgrootte + commissie), naar beneden afgerond op 0,01.

### Weergave (geen invloed op de beslissing)

- Info/versie, Freeze (lijnen bevriezen bij een geldige trade, uit), lijnlengte (5 candles), kleuren en de positie van het "Trade niet mogelijk"-blok.

### Let op: instellingen in ticks schalen niet mee

De break-tolerantie is een percentage, maar de andere afstanden staan nog in ticks. Die zijn afgestemd op XAUUSD. Op NAS100 is 1000 ticks maar 10 punt en 300 ticks maar 3 punt. Dat is erg klein voor een index rond 27000.

- [ ] Instellingen in ticks per instrument controleren, of ook omzetten naar een percentage: Minimale afstand Target, Fallback afstand, Maximaal toegestane R, SL-offset, de body-toleranties en Rejection.
- [ ] Contractgrootte per instrument controleren: 100 geldt voor XAUUSD, NAS100 is anders.

---

## 1. Duidelijke break (deels afgerond in v1.10.0)

**Tradeplan:** "een duidelijke break op zowel de 15m als de 30m", zonder te zeggen wat "duidelijk" is.

**Gedaan (v1.10.0):** de break-tolerantie is nu een percentage van het level (`breakPct`, standaard **0,01%**). Die vervangt de oude 10 ticks, die op XAUUSD en NAS100 vrijwel nul waren.

- Referentie voor een duidelijke break: XAUUSD, close 0,93 voorbij Support, ongeveer 0,02% (93 ticks). De helft daarvan is ook acceptabel.
- Aanleiding: NAS100 op 2026-11-06. De 30m-close van 12:30 lag maar 0,32 punt (0,0012%) boven Resistance 27094.22 en gaf toch een signaal.

**Nog open:**

- [ ] Is 0,01% de goede standaard, of liever 0,015–0,02%? Even testen op XAUUSD en NAS100.
- [ ] Is afstand (percentage) genoeg, of moet ook een minimaal deel van de body voorbij de lijn liggen (bijv. 25%)? Zie "Zwakke break-out" in punt 3.

## 2. Signalen op de 15m (nog niet gebouwd)

Het script zoekt nu alleen breaks op de 30m. Op een 15m-chart toont het de 30m-lijnen, maar er komen geen 15m-signalen.

**Te bouwen:**

- [ ] De eerste 15m-candle die voorbij het 30m-S/R-level sluit (met de break-tolerantie), is een signaal. De SL, R, Range-check en TP komen dan van die 15m-candle.
- [ ] Om :15 en :45 kan alleen een 15m-signaal ontstaan. Om :00 en :30 sluiten de 15m en de 30m tegelijk, en dan beslist de voorkeursregel (punt 3).
- [ ] In het label staat of het een 15m- of een 30m-trade is.

## 3. Regels uit het tradeplan (nog niet gebouwd)

### Niet spelen, ook al ziet het er valid uit

| # | Regel | In het script? |
|---|---|---|
| 1 | Doji break-out candle | Nee |
| 2 | Kleine SL die óp het level staat | Nee. Er is alleen een maximum voor R (`maxRTicks`) |
| 3 | Op de 15m een rejection candle (close onder de 50%) | Nee. De bestaande rejection-check kijkt naar de kleur en grootte van de body, niet naar de positie van de close in de range |
| 4 | Op de 30m de 15m-candle tegen | Gedeeltelijk: `rejectionOn` (standaard uit) keurt af bij een tweede 15m-body van ≥ 50 ticks tegen de richting |

### 15m en 30m sluiten tegelijk

Standaard pak je de 15m. Geldt één van deze vier, dan pak je de 30m:

- 15m SL op het level
- Doji break-out candle
- Geen wick high/low
- Zwakke break-out

### Vragen (eerst beantwoorden, daarna bouwen)

Voorstel voor de standaardwaarde tussen haakjes. Alles komt als instelling in het script, zodat het later bij te stellen is.

- [ ] **Doji:** body kleiner dan X% van de range van de candle? (10%)
- [ ] **SL op het level:** ligt de SL (low − offset bij Long) binnen X van het level, of aan de verkeerde kant ervan? Dan biedt het level geen buffer.
- [ ] **Rejection, close onder de 50%:** de close ligt in de onderste helft van de range van de 15m-candle bij Long, en in de bovenste helft bij Short?
- [ ] **Geen wick high/low:** bij Long geen onderwick (dan ligt de SL direct op de low), of geen bovenwick?
- [ ] **Zwakke break-out:** valt de close onder de break-tolerantie, of ligt minder dan Y% van de body voorbij de lijn?
- [ ] **Regel 4** ("op de 30m de 15m-candle tegen"): geldt die alleen voor een 30m-trade? En telt elke tegengestelde 15m-candle, of alleen vanaf een minimale body?

## 4. Flip-regel (geparkeerd)

**Status (2026-11-06):** de flip is volledig verwijderd uit `trade_lines_strategie.pine` (v1.5.0). De indicator had geen flip. Zodra de flip weer een rol speelt, wordt de regel hier eerst goed vastgelegd en pas daarna gebouwd.

**Tradeplan:** "Flip van minimaal 0,12R: de candle na de break tegengesteld aan de breakout candle. Trade overslaan als die candle 0,6R voorbij schiet." En: "De flip is alleen ongeldig als de prijs voorbij 0,6R schiet zónder flip."

**Wat de gebruiker er al over gezegd heeft:**

- De flip is een korte retracement tegen de richting van de breakout-candle. Die candle kan een 15m- of een 30m-candle zijn.
- Alleen de candle direct na de breakout-candle telt als flip-candle.
- De flip is een extra bevestiging van de trade. De candle na de flip-candle "doet wat hij moet doen" en wordt niet apart gecontroleerd.
- De 0,12R is alleen een check of de flip genoeg kracht had.

**Schets van de gebruiker (2026-11-06), voorbeeld Long:** de breakout-candle sluit bullish boven het level. De candle daarna opent, zakt eerst terug richting het level (hij is dan even bearish) en draait daarna om: hij stijgt en sluit bullish, ver boven de open. Dat omslaan van bearish naar bullish **binnen** de volgende candle is de flip. Hij helpt om een fakeout-trade te vermijden. Bij Short is het het spiegelbeeld.

Gevolgen van deze lezing:
- De flip wordt beoordeeld op de **body terwijl de candle zich vormt**, niet op de wick: de candle is eerst rood (bij Long) en wordt daarna groen. De flip-candle **sluit dus in de richting van de break**. De versie in v1.3.0 eiste het omgekeerde (tegengestelde close) en was dus fout.
- Let op bij het bouwen: zodra de candle gesloten is, is het rode deel uit de vormingsfase niet meer als body te zien. Het is dan de onderwick (Long) of bovenwick (Short). Een script dat achteraf op de 30m-candle kijkt, kan de flip dus alleen herkennen via de wick, of via een kleiner timeframe.
- Waarschijnlijk: de 0,12R is de diepte van die retracement en de 0,6R betekent dat de candle 0,6R in de trade-richting doorschiet zonder eerst terug te zakken. Dan heb je de flip gemist en sla je de trade over. Dit moet nog bevestigd worden.
- Voor een backtest is de 30m-candle alleen niet genoeg: uit open/high/low/close blijkt niet of de dip vóór of ná de stijging kwam. Dat moet dan op een lager timeframe (15m of kleiner) worden bekeken.

**Nog vast te leggen als de flip terugkomt:** hoe de 0,12R gemeten wordt (body of terugval), hoe de 0,6R gemeten wordt (wick of close), en waar en hoe lang de entry-order staat.

---

## 5. Tradingplan vergeleken met het script

Bron: `20261005_plan_nl_theme_3.pdf` ("Tradingplan Goud (XAUUSD) — ranges & break-outs"), 2 pagina's. Het plan is geschreven voor goud, maar geldt volgens de gebruiker ook voor NAS100.

Legenda: ✅ zit erin en klopt · ⚠️ zit erin, maar wijkt af of is anders uitgelegd · ❌ zit er niet in · ❓ plan onduidelijk

### De basis

| Plan | Script nu | Status |
|---|---|---|
| Zones op de 30m-chart | S/R en Targets op 30m (FXCM) | ✅ |
| Entry op 15m of 30m | Alleen 30m (zie punt 2) | ❌ |
| Sessie 06:00–10:00, plus de tweede sessie 12:00–16:00 (aanvulling gebruiker), Europe/Amsterdam | Geen sessiefilter: de indicator toont alle trades van de dag. Dat is zo bedoeld, want de sessie wordt in de logging vastgelegd. Ook de strategie filtert niet (het vaste sluituur staat standaard uit) | ✅ bewuste keuze, in indicator en strategie |
| Ranges intekenen vóór 06:00 | Het script berekent S/R na elke 30m-candle opnieuw, ook tijdens de sessie. Bevestigd: dat is de bedoeling | ✅ |

### Stap 1 en 2: ranges en validatie

| Plan | Script nu | Status |
|---|---|---|
| Elke range is een nieuwe support of resistance. Target = het volgende level van hetzelfde type | Target = het eerstvolgende geldige level van hetzelfde type, maar minimaal 300 ticks van S/R (`minTargetDistance`). Een geldig level dat dichterbij ligt, wordt overgeslagen en S/R schuift ernaartoe | ⚠️ De minimale afstand en de verschuiving staan niet in het plan |
| Check 1: er past een nette **1,5R** in, met een conservatieve SL. Gemeten bij de break-out | Range-check meet vanaf de entry tot het Target bij de break, met `minRangeRR` = **1,0** (was 1,5 tot v1.9.23) | ⚠️ |
| Check 2: het Target is nog vrij, er heeft geen wick aan gezeten. De candles direct na de vorming van het level tellen niet mee | Wick-check op het Target. Alleen de **eerste** candle na de overgang krijgt gratie, en alleen als hij in de respecterende richting sluit | ⚠️ Het plan zegt "de candles" (meervoud) en stelt geen eis aan de kleur |
| Is het Target geraakt? Pak de range erboven of eronder | Het script zoekt verder terug naar een vrij Target en verschuift S/R naar een tussenliggend level | ⚠️ Lijkt op het plan, maar moet gecontroleerd worden |
| De eerste range die valid is, is jouw range. Geen valid range, geen trade | Er is altijd één S/R-paar. Is er geen geldig Target, dan wordt een fallback-Target getekend en kan er alsnog een trade getoond worden | ⚠️ |

### Entry criteria

| Plan | Script nu | Status |
|---|---|---|
| Duidelijke break-out candle op je range, 15m of 30m | 30m-close ≥ 0,01% voorbij S/R (v1.10.0), geen 15m | ⚠️ Zie punt 1 en 2 |
| 1,5RR vanuit een conservatieve stop loss | Zie check 1 | ⚠️ |
| Flip van 0,12 | Niet gebouwd (geparkeerd) | ⏸️ Zie punt 4 |
| De flip is alleen ongeldig als de prijs voorbij 0,6R schiet zonder flip. Dan sla je hem over | Niet gebouwd (geparkeerd) | ⏸️ Zie punt 4 |
| Doorschuiven: kun je niet instappen, of pakt de break-out candle je Target al? Ga naar de volgende range erboven of eronder en check opnieuw | Ligt de close al voorbij het Target, dan is de Range negatief en is de trade "niet mogelijk". Er wordt niet doorgeschoven naar de volgende range | ❌ |

### Niet spelen en 15m/30m tegelijk

Zie punt 3. Geen van de vier "niet spelen"-regels en geen van de vier 30m-voorkeursregels zit er volledig in.

### Risicobeheer

| Plan | Script nu | Status |
|---|---|---|
| Take profit **1RR**, inclusief 5 pips extra ruimte bij je SL | `tpRR` = **1,2**. De SL ligt 50 ticks voorbij de wick: op goud is dat 0,50 = 5 pips, en die ruimte zit al in R | ⚠️ Het plan zegt 1R, het script 1,2R |
| Break-even: op 0,8R schuif je de SL naar break-even | Strategie: aan, trigger 0,8R. Indicator: niet zichtbaar | ✅ in de strategie |
| Per dag 1 TP of 1 SL. Na een break-even mag je er nog één | Niet aanwezig. Bewuste keuze: dit wordt in de logging bijgehouden. De strategie negeert alleen nieuwe signalen zolang er een positie open is | ✅ bewuste keuze (logging) |
| Stop loss max 100 pips, strak op de candle high/low | `maxRTicks` = 1000 ticks: op goud 10,00 = 100 pips. De SL ligt op de wick ± 50 ticks | ✅ voor goud, ❓ voor NAS100 |
| Het risicopercentage bepaal je zelf | `riskPct` instelbaar (1%) | ✅ |

### Onduidelijkheden in het plan

- [x] **Sessies en tijdzone:** 06:00–10:00 en 12:00–16:00, Europe/Amsterdam. Beide gelden ook voor NAS100. De opening van de Nasdaq-cash-sessie (15:30) valt in de tweede sessie.
- [x] **Sessiefilter in de indicator:** nee. Alle mogelijke trades blijven zichtbaar, en binnen of buiten de sessie wordt in de logging vastgelegd.
- [x] **Strategie (backtest):** geen sessiefilter. Binnen of buiten de sessie wordt in de logging bijgehouden.
- [x] **"1 TP of 1 SL per dag":** wordt in de logging bijgehouden, net als het aantal trades per dag. Geen limiet in de scripts.
- [x] **"Ranges intekenen vóór 06:00":** de ranges worden doorlopend geëvalueerd, zoals het script nu al doet.
- [x] **Open trades aan het einde van de sessie:** die lopen door tot TP, SL of break-even.
- [ ] **"Elke range is een nieuwe support of resistance":** is een range één level, of het gebied tussen een support en een resistance?
- [ ] **"Conservatieve SL" bij check 1 tegenover "strak op de candle high/low" bij Stop loss:** is de conservatieve SL dezelfde als de echte SL (wick + 5 pips)? Of reken je bij check 1 met een ruimere SL, bijv. aan de andere kant van de range?
- [ ] **1,5R in de range tegenover TP 1R:** de 1,5R is dus ruimte en niet het doel. Klopt het dat `minRangeRR` terug moet naar 1,5 en `tpRR` naar 1,0? De gebruiker heeft eerder bewust 1,0 en 1,2 gekozen (v1.9.23: 1,5 bleek te streng).
- [ ] **Waar meet je de 1,5R vanaf:** vanaf de entry (close van de break-candle, zoals nu) of vanaf het level?
- [ ] **"De candles direct na de vorming tellen niet mee":** hoeveel candles? En maakt de kleur uit? Het script geeft nu gratie aan één candle, mits die in de respecterende richting sluit.
- [ ] **Minimale afstand Target (300 ticks):** staat niet in het plan. Moet die weg, of volgt hij uit de 1,5R-check?
- [ ] **Doorschuiven, "kun je niet instappen":** wanneer is dat het geval? Bijv. als de SL groter is dan 100 pips, als er geen 1,5R past, of als de flip niet komt?
- [ ] **Flip van 0,12:** is de flip een tegengestelde candle met een body van ≥ 0,12R, of een terugval van de prijs van ≥ 0,12R richting het level? En moet hij op 15m of op 30m beoordeeld worden?
- [ ] **"Voorbij 0,6R schiet zonder flip":** 0,6R in de trade-richting gemeten vanaf de entry/break-close, op wick of op close?
- [ ] **TP 1RR "inclusief 5 pips extra ruimte bij je SL":** betekent dit dat R al inclusief de 5 pips is (zoals het script nu rekent)?
- [ ] **Pips op NAS100:** het plan rekent in pips voor goud (1 pip = 0,10). Wat is een pip op NAS100: 1 punt? Dan zijn 5 pips = 5 punt (500 ticks) en max 100 pips = 100 punt (10.000 ticks). Nu staat er 50 en 1000 ticks, dus 0,50 en 10 punt.

---

## 6. Instrumentprofiel (idee 11-11-2026, eerst live observeren)

Doel: bij het toevoegen van de indicator automatisch de juiste waarden per instrument. Pine Script kan standaardwaarden van inputs niet per symbool laten verschillen; "Opslaan als standaard" in TradingView bewaart één set voor alle symbolen.

Voorstel:
- Nieuwe instelling **"Instrumentprofiel": Automatisch (standaard) / Handmatig.**
- **Automatisch:** het script herkent het symbool en gebruikt de waarden uit HANDLEIDING.md (groep Lotgrootte, "Instellingen per instrument"):
  - ticker bevat XAU (XAUUSD, GOLD) → goud: SL-buffer 50, fallback target 100, min. afstand Target 300, body-toleranties 50/50, max R 10 punten, rejection 50, contractgrootte 100, commissie 6;
  - NAS100, US100, NAS100USD → Nasdaq: 200, 700, 2100, 350/350, 110, 350, 1, 0;
  - iets anders → de handmatige instellingen.
- **Handmatig:** zoals nu, de waarden uit het Inputs-tabblad.
- Het actieve profiel zichtbaar op de chart (bijv. "Profiel: Nasdaq (auto)").

Nadelen:
- Bij Automatisch tonen het Inputs-tabblad en de alertnaam de handmatige waarden, niet de profielwaarden; controleren via de alertnaam kan dan niet meer.
- Een profielwaarde aanpassen = nieuwe versie van het script.

Alternatief (minder voorkeur): tick-instellingen in % van de koers, zoals de break-tolerantie. Verandert de betekenis van instellingen die nu goed werken; max R van de coach blijft per instrument verschillen.

Nog te beslissen voordat het gebouwd wordt:
1. Alleen goud en Nasdaq, of ook andere instrumenten (US30, DAX, …)? Daarvoor zijn nog geen waarden vastgesteld.
2. Accountgrootte en risico % buiten het profiel laten (horen bij het account, niet bij het instrument)?
3. Waar het profiel tonen: in het TP-label, als regel in de tabel, of als klein label linksboven?

---

## Vragen voor de expert (samengevat)

1. Wat is een "duidelijke break": alleen afstand voorbij het level, of ook een deel van de body? Klopt ongeveer 0,01–0,02% van de koers?
2. Hoe definieer je een doji, "SL op het level", "geen wick high/low" en "zwakke break-out"?
3. Is "rejection, close onder de 50%" de positie van de close binnen de range van de 15m-candle?
4. Geldt "op de 30m de 15m-candle tegen" alleen voor 30m-trades?
5. Flip: is het een tegengestelde candle (body ≥ 0,12R) of een terugval van 0,12R? Hoe lang mag je erop wachten? Meet je de 0,6R op de wick of op de close? Op de 15m of op de 30m? Hoe lang blijft de entry-order staan?
6. Sessies 06:00–10:00 en 12:00–16:00 (Amsterdam): het moment van de break bepaalt of een trade binnen de sessie valt (beantwoord door de gebruiker). Geen vraag meer voor de expert, tenzij die er anders over denkt.
7. Is de "conservatieve SL" van de 1,5R-check dezelfde als de echte SL (high/low + 5 pips)?
8. Hoeveel candles na de vorming van een level mogen het Target met een wick raken?
9. Is er een minimale afstand tussen level en Target, los van de 1,5R?
10. Wanneer schuif je door naar de volgende range ("kun je niet instappen")?
11. Wat is een pip op NAS100 (voor de 5 pips SL-ruimte en de max 100 pips)? *(Deels beantwoord 11-11-2026: coach noemt max 110 "pips" voor de Nasdaq; aangenomen = 110 indexpunten, ingesteld als max R 110 punten. Nog bevestigen met een voorbeeld: is een SL van 46,5 punten 46,5 of 465 pips?)*
