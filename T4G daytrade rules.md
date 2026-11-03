# T4G Daytrade Rules

Dit document beschrijft alle regels waaraan het Pine Script `trade_lines.pine` ("Trade Lijnen (SL/S/R)") moet voldoen. Bijgewerkt tot en met versie **1.9.37**. Bij twijfel is de code leidend; dit document beschrijft wat de code doet.

## Algemeen

1. **Timeframe**: alle berekeningen draaien op **30m-candles**, ook als de chart op 15m staat. Alleen de 30m- en 15m-chart worden ondersteund; op elk ander timeframe verschijnt een rood waarschuwingslabel en wordt er niets getekend en geen alert verstuurd.
2. **Alleen gesloten candles**: alles wordt berekend bij het sluiten van een 30m-candle. Een nog lopende 30m-candle telt nergens mee; zolang die loopt, blijven alle waarden op de laatst bevestigde stand staan.
3. **Rekenfeed** (instelling, standaard aan): de berekeningen draaien op hetzelfde symbool bij een andere broker-feed dan de chart, standaard FXCM (prefix `FX`), bijv. `FX:XAUUSD` op een `FTMO_OANDA:XAUUSD`-chart. Alle niveaus, SL, TP en de lotgrootte zijn dan FXCM-prijzen; de labels tonen "(FXCM)". Bij prefix `FX` worden afwijkende OANDA-tickernamen vertaald (bijv. `NAS100USD` → `NAS100`). Is de prefix gelijk aan die van de chart of leeg, dan rekent het script op de chart-feed.
4. **Tijd-coördinaten**: lijnen en labels staan op tijd (`xloc.bar_time`), zodat ze op de 30m- en 15m-chart op dezelfde plek staan.

## Stop Loss lijnen

1. Op de **signaal-candle** (zie LONG/SHORT signaal) wordt de SL gezet op basis van de **wick** van die candle — hier tellen wicks wél mee:
   - **Long SL** = `low` van de signaal-candle **min** `x` ticks (instelbaar, standaard 50).
   - **Short SL** = `high` van de signaal-candle **plus** `x` ticks (standaard 50).
2. Op de signaal-candle wordt de SL altijd gezet, ongeacht de kleur van die candle (na een gap kan een break-candle boven Resistance toch bearish zijn).
3. **Trailing** (instelling, standaard uit): staat trailing uit, dan blijft de SL vanaf de signaal-candle vast staan, net als de TP. Staat trailing aan, dan werkt binnen het signaalvenster elke volgende gesloten **bullish** candle de Long SL bij (`low` − x ticks) en elke **bearish** candle de Short SL (`high` + x ticks).
4. **Doji-uitzondering** (alleen bij trailing): een doji (close == open) werkt geen van beide lijnen bij.
5. **Signaalvenster** (`slSignalWindow`, standaard 2): de SL-lijn is alleen zichtbaar zolang het bijbehorende signaal actief is, dus binnen dit aantal 30m-candles na het signaal (de signaal-candle telt als candle 1).
6. Er is altijd maar **één SL-lijn tegelijk zichtbaar**: die van het laatste signaal.
7. De lijn begint bij de signaal-candle en loopt `lineLen` 30m-candles (standaard 5) naar rechts; daar begint het label met de exacte prijs. De lijn loopt niet oneindig door, anders dan de S/R-lijnen.
8. Kleur: instelbaar, standaard groen voor Long SL en rood voor Short SL. Is de trade niet mogelijk (zie Trade Mogelijkheid), dan wordt de SL-lijn niet getekend.
9. Kan volledig aan/uit gezet worden via "Toon SL lijnen". Uit betekent ook: geen TP-lijn en geen break-lijn.

## Resistance

1. Kijk terug vanaf de **laatst gesloten 30m-candle**, maximaal `maxScanBars` candles (standaard 450).
2. Zoek de **meest recente overgang** van een **bullish candle** (pivot-candle) gevolgd door een **bearish candle** (reversal-candle). Een doji is geen van beide en vormt dus geen overgang.
3. Het niveau = de **bovenkant van de body** van de pivot-candle (`max(open, close)`). **Uitzondering (dagsluiting/weekend)**: ligt er tussen pivot-candle en reversal-candle een tijdsgat van meer dan één 30m-candle, dan is het niveau de **open van de reversal-candle** (eerste prijs na de gap), bij gap up én gap down (instelling, standaard aan).
4. **Geldigheidscheck (alleen body)**: het niveau is alleen geldig als geen enkele latere gesloten candle met zijn **body boven** het niveau komt. Een body die precies op het niveau eindigt, maakt het niet ongeldig.
5. **Reversal-candle uitsluiten** (instelling, standaard aan): de reversal-candle zelf telt niet mee in de check van zijn eigen niveau. Alleen candles daarna kunnen het ongeldig maken.
6. **Body-tolerantie voor de candle na de overgang** (instelling, standaard uit): de candle **direct na** de reversal-candle mag met zijn body maximaal een instelbaar aantal ticks (standaard 50) boven het niveau komen, **mits die candle bearish is** (de respecterende richting). Een bullish candle op die plek blijft strikt.
7. **Body-tolerantie voor alle latere candles** (instelling, standaard uit): **elke** latere candle, ongeacht kleur, mag met zijn body maximaal een instelbaar aantal ticks (standaard 50) boven het niveau komen. Voor de candle direct na de reversal-candle geldt dan de grootste van de twee toleranties (mits bearish). Let op: is deze tolerantie groter dan `x` (signaal), dan kan een close tussen die twee grenzen een signaal geven terwijl het niveau blijft staan.
8. **Wicks spelen voor Resistance geen rol** — de lijn mag door wicks heen lopen.
9. Niet geldig → zoek verder terug naar de vórige bullish→bearish overgang en herhaal de check.
10. **Fallback**: geen geldige overgang binnen `maxScanBars` → Resistance = de hoogste high in die range, label `[FALLBACK]`.
11. **Verschuiving**: na de Target-zoektocht kan Resistance nog verschuiven naar een tussenliggend niveau (zie Target Resistance, punt 6).

## Support

Spiegelbeeld van Resistance:

1. Meest recente overgang van een **bearish candle** (pivot) gevolgd door een **bullish candle** (reversal).
2. Niveau = **onderkant van de body** van de pivot-candle (`min(open, close)`). Zelfde uitzondering bij een tijdsgat: dan de **open van de reversal-candle**.
3. Geldigheidscheck (alleen body): geldig alleen als geen enkele latere gesloten candle met zijn **body onder** het niveau komt. Precies op het niveau is toegestaan.
4. Reversal-candle uitsluiten en beide body-toleranties werken gespiegeld: de tolerantie voor de candle direct na de overgang geldt alleen als die candle **bullish** is; de tolerantie voor latere candles geldt ongeacht kleur, onder het niveau.
5. **Wicks spelen voor Support geen rol.**
6. **Fallback**: de laagste low in de scanrange, label `[FALLBACK]`.
7. **Verschuiving**: zie Target Support.

## Target Resistance

1. **Eigen zoektocht** vanaf de laatst gesloten candle naar bullish→bearish overgangen, met dezelfde patroondetectie, hetzelfde niveau (incl. gap-uitzondering) en dezelfde body-check als Resistance (incl. reversal-candle uitsluiten en beide body-toleranties).
2. **Afstandseis**: het niveau moet minimaal `minTargetDistance` ticks (standaard 300) **boven Resistance** liggen. Resistance is hier de waarde vóór een eventuele verschuiving (punt 6).
3. **Wick-check** (alleen voor het Target zelf):
   - De reversal-candle hoort bij de overgang en wordt niet op zijn wick gecontroleerd.
   - De **eerste candle ná de overgang** mag het niveau met een wick raken, maar alleen als die candle **bearish** is. Een bullish candle of doji op die plek krijgt geen gratie.
   - Élke candle daarna (ongeacht kleur) maakt het niveau ongeldig zodra zijn high het niveau raakt of doorbreekt.
4. Het **eerste** niveau dat body-geldig is, ver genoeg ligt én de wick-check doorstaat, wordt Target Resistance. Daar stopt de zoektocht.
5. Body-geldige niveaus die onderweg afvallen (te dichtbij, of al met een wick geraakt) worden onthouden; het **laatst gevondene** daarvan (het verst terug, vlak vóór het Target) is het tussenliggende niveau.
6. **Verschuiving van Resistance**: is er een Target gevonden én een tussenliggend niveau, dan wordt Resistance dat tussenliggende niveau. Anders blijven Resistance en Target zoals ze zijn. Het tussenliggende niveau hoeft de wick-check niet te doorstaan.
7. **Fallback**: geen geldig Target binnen de scanrange → Target = Resistance plus het grootste van `autoTargetTicks` (standaard 100) en `minTargetDistance` ticks, label `[FALLBACK]`. Resistance verschuift dan niet.

## Target Support

Spiegelbeeld van Target Resistance:

1. Eigen zoektocht naar bearish→bullish overgangen, met dezelfde niveaubepaling en body-check als Support.
2. Afstandseis: minimaal `minTargetDistance` ticks **onder Support** (vóór verschuiving).
3. Wick-check: de reversal-candle wordt niet gecontroleerd; de eerste candle ná de overgang mag het niveau met een wick raken als die candle **bullish** is; élke candle daarna maakt het niveau ongeldig zodra zijn low het raakt of doorbreekt.
4. Eerste niveau dat aan alle eisen voldoet = Target Support; het laatst afgevallen body-geldige niveau ervoor is het tussenliggende niveau waar Support naartoe verschuift.
5. Fallback: Support min het grootste van `autoTargetTicks` en `minTargetDistance` ticks. Support verschuift dan niet.

## Tekenregels (alle 4 S/R-lijnen)

- De lijn begint bij de **pivot-candle** van de overgang (bij een fallback aan het begin van de scanrange).
- Loopt door naar **rechts** (door de huidige candle heen, de toekomst in).
- Lijndikte **2px**. Resistance rood, Support groen; de Target-lijnen in dezelfde kleur, lichter.
- Label bij de laatst gesloten 30m-candle met de naam, de feed (bijv. "(FXCM)") en `[pivot N candles terug]` of `[FALLBACK]`. Tekstkleur instelbaar.
- Alles wordt **opnieuw berekend en getekend bij elke gesloten 30m-candle**, ook op de 15m-chart. Uitzondering: zie Freeze.
- Geen handmatig verslepen nodig — volledig automatisch.

## LONG signaal

1. Wordt alleen getest bij het sluiten van een 30m-candle.
2. Triggert wanneer de **close** van die candle boven `Resistance + x ticks` sluit terwijl de vorige close daar nog op of onder lag — alleen bij de eerste doorbraak, niet bij elke volgende candle die er nog boven sluit.
3. `x` = instelbaar aantal ticks (standaard 10).
4. **Getoetst tegen de Resistance van vóór deze candle**: de Resistance zoals die na de vorige candle op de chart stond (inclusief een eventuele verschuiving). Zodra de candle die lijn doorbreekt, wordt ze ongeldig en berekent het script Resistance opnieuw.
5. **Geen dubbel signaal**: loopt er nog een LONG-signaalvenster (`slSignalWindow`), dan telt een nieuwe doorbraak niet als nieuw signaal. Resistance kan na een sterke beweging verspringen; zonder deze regel zou dat een tweede signaal met een andere R geven.
6. Bij triggeren:
   - een **alert** ("Bullish breakout: close boven Resistance + x ticks"), één keer per signaal, ook als de trade niet mogelijk is;
   - de **break-lijn**: zwarte stippellijn op het doorbraakniveau (`Resistance + x ticks`), doorlopend naar links tot `lineLen` candles na de signaal-candle, met het label "Resistance doorbroken: [prijs]". Zo is het doorbroken niveau achteraf te controleren. Alleen zichtbaar als "Toon SL lijnen" aan staat;
   - SL, TP en Trade Mogelijkheid (zie daar).
7. Er is geen apart signaallabel of signaalpijl.
8. Er is maximaal één signaal tegelijk actief: het laatste signaal (LONG of SHORT) bepaalt welke lijnen getoond worden.

## SHORT signaal

Spiegelbeeld van het LONG signaal:

1. Alleen getest bij het sluiten van een 30m-candle.
2. Triggert wanneer de close onder `Support − x ticks` sluit terwijl de vorige close daar nog op of boven lag.
3. Zelfde `x` als bij LONG.
4. Getoetst tegen de Support van vóór deze candle.
5. Geen dubbel signaal zolang er een SHORT-signaalvenster loopt.
6. Bij triggeren: alert ("Bearish breakdown: close onder Support - x ticks"), break-lijn met label "Support doorbroken: [prijs]", SL, TP en Trade Mogelijkheid.

## Trade Mogelijkheid (TP & Range-check)

1. Wordt eenmalig bepaald op de signaal-candle zelf en blijft ongewijzigd zolang het signaalvenster loopt.
2. **Entry** = close van de signaal-candle.
3. **R** = afstand van entry tot de SL, met dezelfde formule als de Stop Loss-lijnen:
   - Long: `SL = low van de signaal-candle − x ticks` → `R = entry − SL`.
   - Short: `SL = high van de signaal-candle + x ticks` → `R = SL − entry`.
4. **TP** = entry **plus** (Long) of **min** (Short) `tpRR` × R (standaard **1.2**).
5. **Range-check**: de vrije ruimte van entry tot het Target moet minimaal `minRangeRR` × R (standaard **1.0**) zijn:
   - Long: Range = **Target Resistance − entry**.
   - Short: Range = **entry − Target Support**.
   - Het Target is de waarde zoals die **vóór de signaal-candle** op de chart stond, net als de doorbroken Resistance/Support zelf — niet de waarde die op de signaal-candle opnieuw berekend wordt.
   - Bewust niet gemeten vanaf (verschoven) Resistance/Support: dat niveau kan vlak bij het Target liggen, waardoor de Range kunstmatig klein wordt terwijl de trade vrij baan heeft.
6. **Max R-check**: R in ticks mag niet groter zijn dan `maxRTicks` (standaard **1000**). Deze standaard hoort bij **XAUUSD** (tick 0.01): 1000 ticks = 100 pips / $10. Op een ander symbool moet `maxRTicks` opnieuw bepaald worden.
7. **Rejection candle** (optioneel, standaard uit): de signaal-30m-candle bestaat uit twee 15m-candles (op de rekenfeed). Sluit de **tweede** tegen de trade-richting in (Long: bearish, Short: bullish) met een body van minimaal `rejectionTicks` (standaard **50**), dan is de trade niet mogelijk. Een doji of kleinere tegengestelde body telt niet. Bestaat de 30m-candle niet uit precies twee 15m-candles, dan wordt deze check overgeslagen. Komt uit de NASDAQ-strategie.
8. **Trade mogelijk** = R > 0 **én** Range ≥ `minRangeRR` × R **én** R ≤ `maxRTicks` **én** geen rejection. Dan verschijnt een blauwe stippellijn op de TP met label "TP (1.2 R/R): ... · Entry ... · R ... · Range x.xxR", plus (instelbaar) de lotgrootte (zie Lotgrootte). De Range in R is naar beneden afgerond op 2 decimalen.
9. **Trade niet mogelijk**: geen TP-lijn en geen SL-lijn. De reden staat in een vast **"Trade niet mogelijk"-blok** op het scherm (positie instelbaar, standaard rechtsboven; kleur standaard oranje), met per overtreden voorwaarde een eigen regel, bijv. "Range 0.92R < 1R (3.50 < 3.80)", "R 1250 ticks > max 1000 ticks" of "Rejection candle 15m (85 ticks >= 50)". De alert wordt **niet** onderdrukt.
10. TP-lijn en reden volgen het signaalvenster (`slSignalWindow`) en verdwijnen zodra dat verloopt; een nieuw signaal vervangt ze direct. De TP-lijn loopt, net als de SL-lijn, `lineLen` candles vanaf de signaal-candle.
11. Aan/uit via "Toon TP-lijn en Trade-mogelijkheid check"; de TP-lijn vereist daarnaast "Toon SL lijnen".

## Lotgrootte

1. Bij een mogelijke trade toont het TP-label (instelbaar, standaard aan) de lotgrootte en het werkelijke risico, bijv. `Lot 0.27 · risico $98.76 (0.99%)`.
2. Formule: `lot = account × risico% / (R × contractgrootte × koers-naar-USD + commissie per lot)`, naar beneden afgerond op 0.01 lot, minimaal 0.01. Accountvaluta is USD; niet-USD-symbolen worden omgerekend.
3. Valt de berekening onder 0.01 lot, dan toont het label 0.01 lot met "min. lot, boven je risico!".
4. R is de vaste R van de signaal-candle op de rekenfeed. Spread en swap zijn niet meegerekend.

## Freeze

1. Instelling "Lijnen bevriezen zodra een geldige trade ontstaat" (standaard uit).
2. Staat die aan en is er bij een nieuwe 30m-candle **op de laatste candle van de chart** een mogelijke trade actief, dan blijven alle lijnen en labels staan zoals ze op dat moment getekend zijn; daarna wordt niets meer bijgewerkt.
3. Bevriest niet met terugwerkende kracht in de geschiedenis.
4. Opheffen: de instelling uit- en weer aanzetten.
5. Alerts blijven werken tijdens een freeze.
