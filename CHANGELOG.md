# Changelog

Alle noemenswaardige wijzigingen aan `trade_lines.pine` worden hier bijgehouden.
Versienummering volgt [Semantic Versioning](https://semver.org/lang/nl/) (MAJOR.MINOR.PATCH).

## [1.9.4] (diagnose-build)

### Toegevoegd
- Tijdelijk geel diagnosepaneel rechtsboven in de chart (via `table.new`), dat op elke realtime update `isSupportedTF`, `timeframe.period`, `calcBarTime`, `calcResistance`, `calcSupport`, `newData`, `lastDrawnBarTime` en `bar_index` toont. Ook na de v1.9.3-fix (tuple i.p.v. Calc30-object) werden nog steeds geen lijnen getekend, zonder foutmelding - dit paneel moet aantonen of `calc*` uit `request.security()` echt gevuld wordt en of `newData` ooit `true` wordt, zodat de volgende fix op feiten i.p.v. giswerk gebaseerd kan worden. Wordt verwijderd zodra het onderliggende probleem gevonden is.

## [1.9.3]

### Opgelost
- Nog steeds geen enkele lijn/label zichtbaar, ook niet meer nadat 1.9.2 de `max_bars_back(time, 500)` had toegevoegd - en zonder foutmelding in de legenda (de losstaande debug-functionaliteit op de 30m-chart, die buiten `request.security()` om draait, werkte wél gewoon). Dit wijst erop dat het `Calc30`-object dat via `request.security()` werd opgehaald in de praktijk niet betrouwbaar gevuld werd (alle velden bleven op hun startwaarde `na` staan), ondanks dat `request.security()` in theorie objecten van een user-defined type ondersteunt.
- `f_calc30m()` en de `request.security()`-aanroep geven/ontvangen de berekende waarden nu als gewone TUPLE van 35 simpele waarden (float/int/bool/string) in plaats van als `Calc30`-object. Dit is de vorm die `request.security()` al sinds jaar en dag zonder twijfel ondersteunt. Alle `calc.veldnaam`-verwijzingen zijn hernoemd naar losse `calcVeldnaam`-variabelen; het `type Calc30` is verwijderd.

## [1.9.2]

### Opgelost
- Er werd helemaal geen enkele lijn/label meer getekend. Oorzaak: `rPivotTime`/`sPivotTime`/`trPivotTime`/`tsPivotTime` worden sinds v1.9.0 berekend via `time[rBarsBack]` (dynamische offset, tot 450 candles terug), maar alleen voor `open`/`close`/`high`/`low` was een `max_bars_back(..., 500)` gedeclareerd - niet voor `time`. Zonder die declaratie kon Pine de benodigde historische buffer voor `time` niet bepalen, bleven de pivot-tijden op `na` staan zodra de pivot verder dan de (te kleine) standaardbuffer terugligt, en crashte het script op `line.new()` met een `na` x1-coördinaat - waardoor er niets meer getekend werd. Opgelost door ook `max_bars_back(time, 500)` toe te voegen.

## [1.9.1]

### Opgelost
- Compile-error "Cannot assign a value of the 'simple na' type ... The variable is declared with the 'const bool' type" bij `rFallback`/`sFallback`/`trFallback`/`tsFallback`/`slSide`/`breakSide` in `f_calc30m()`. Oorzaak: bij `var bool x = na` legt de Pine-compiler het qualifier van `x` vast op `const`, waardoor een latere `:=` met een series/simple bool-waarde niet meer is toegestaan. Opgelost door de expliciete `bool`-type-annotatie te vervangen door de typecast-vorm (`var x = bool(na)`), zodat het qualifier vrij kan meegroeien.

## [1.9.0]

### Gewijzigd
- Alle berekeningen (Support/Resistance, Targets, LONG/SHORT-signalen, SL, TP + Range-check) draaien nu ALTIJD op het 30-minuten timeframe, ongeacht op welk timeframe de chart zelf staat. Dit gebeurt via `request.security()`, waarbij het volledige berekeningsresultaat als één user-defined type (`Calc30`) wordt opgehaald.
- De indicator ondersteunt voortaan uitsluitend de timeframes 30m en 15m; op elk ander timeframe verschijnt een waarschuwingslabel en wordt er niets getekend.
- Lijnen/labels worden getekend met tijd-gebaseerde coördinaten (`xloc.bar_time` i.p.v. `xloc.bar_index`), zodat ze exact hetzelfde prijsniveau tonen op zowel de 30m- als de 15m-chart.
- Belangrijk gevolg: de lijnen/labels worden bijgewerkt op het moment dat een 30-minuten candle sluit - ook als de 15m-chart op dat moment bekeken wordt. Ze volgen dus de 30m-klok, niet de 15m-klok.
- De debug-instelling "Debug: toon eerste Support-kandidaat + reden verwerping" blijft, zoals voorheen, alleen werkzaam op de native 30m-chart (bar_index-gebaseerd, buiten `request.security` om).

## [1.8.2]

### Gewijzigd
- Default van **"Max bars terugzoeken"** (`maxScanBars`, groep "Support / Resistance") gewijzigd van 250 naar **450**. Op XAUUSD werd anders niet ver genoeg teruggezocht naar een geldige Target Support/Resistance-pivot, waardoor die te vaak op de (te kleine) fallback-afstand terugviel - zie eerdere test met Range 3.00 - en de Range-check in "Trade Mogelijkheid" onterecht bijna altijd faalde.

## [1.8.1]

### Gewijzigd
- De break-lijn (Resistance/Support-doorbraakniveau, zwart/dashed) loopt nu onbeperkt door naar links (`extend.left`) in plaats van pas te beginnen bij de signaal-candle, zodat het niveau makkelijk te herleiden is naar de candles ervoor. De marge naar rechts (`lineLen` bars) blijft ongewijzigd - de lijn loopt dus niet oneindig door naar rechts.

## [1.8.0]

### Toegevoegd
- De break-lijn (het zwarte stippellijntje op het niveau van de doorbraak zelf) heeft nu een label met het exacte doorbroken niveau, plus of het om **Resistance** (bij LONG) of **Support** (bij SHORT) ging - bv. "Support doorbroken: 4429.10".
- Reden: het signaal wordt getoetst tegen Resistance/Support zoals die golden VOORDAT de candle sloot (`prevResistance`/`prevSupport`). Zodra de candle die lijn doorbreekt, wordt die lijn zelf ongeldig en herberekent het script Resistance/Support naar het eerstvolgende geldige (verder terugliggende) niveau - dat is de lijn die je ná het signaal op de chart ziet. Zonder label was het gebroken niveau zelf nergens meer af te lezen, waardoor het leek alsof een signaal niet bij een "echte" doorbraak van de zichtbare S/R-lijn hoorde. Met dit label is elk signaal achteraf direct te verifiëren.
- Break-labels volgen dezelfde levenscyclus als de break-lijnen zelf (signaalvenster `slSignalWindow`, max. 1 tegelijk zichtbaar per richting).

## [1.7.0]

### Toegevoegd
- Extra geldigheidsvoorwaarde bij de "Trade Mogelijkheid"-check (naast de Range-check): R (het verschil tussen de close van de signaal-candle en de SL-lijn) mag, uitgedrukt in ticks, niet groter zijn dan een instelbaar maximum (`maxRTicks`, standaard **1000 ticks**). Is R te groot, dan is de trade ook ongeldig, los van of de Range wel voldoende ruimte biedt.
- Nieuwe instelling **"Maximaal toegestane R (ticks)"** (groep "Trade Mogelijkheid", default 1000).
- Het "Trade niet mogelijk"-label toont nu per reden een eigen regel: als zowel de Range te klein is als R te groot, staan beide meldingen onder elkaar in hetzelfde label.

## [1.6.0]

### Toegevoegd
- Nieuwe sectie **"Trade Mogelijkheid"**: bij een LONG/SHORT-signaal wordt automatisch een Take Profit (TP) berekend op basis van een instelbare Risk/Reward-ratio (standaard 1.2). `R` = het verschil tussen de close van de signaal-candle en de waarde van de bijbehorende SL-lijn (Long: `low - x ticks`, Short: `high + x ticks`) - dezelfde formule als de bestaande Long/Short SL.
- Extra haalbaarheidscheck: de beschikbare Range (Resistance -> Target Resistance bij Long, Support -> Target Support bij Short) moet minimaal een instelbare R/R-ruimte (standaard 1.5 x R) kunnen bevatten. Is die ruimte er niet, dan wordt geen TP-lijn getekend maar verschijnt in plaats daarvan een **"Trade niet mogelijk"**-label, met de gemeten Range en de benodigde afstand erbij.
- Nieuwe instellingen (groep "Trade Mogelijkheid"): aan/uit-schakelaar, TP Risk/Reward-ratio, minimaal benodigde R/R-ruimte in de Range, kleur TP-lijn, kleur "Trade niet mogelijk"-label.
- TP-lijn/labels volgen hetzelfde signaalvenster (`slSignalWindow`) en dezelfde exclusiviteitslogica (max. 1 tegelijk zichtbaar, nieuw signaal verwijdert meteen het vorige) als de bestaande SL-lijnen en break-lijn.

## [1.5.0]

### Toegevoegd
- Nieuwe (uit) instelling **"Support/Resistance: reversal-candle uitsluiten van eigen invalidatie"** (groep "Support / Resistance"). Dit is de fix die eerder werd getest in het losse `trade_lines_experimental.pine`-bestand, nu ingebouwd in `trade_lines.pine` zelf als schakelbare optie - dat experimentele bestand is hiermee overbodig geworden.
- Achtergrond: in `f_autoResistance`, `f_autoSupport`, `f_autoTargetResistance` en `f_autoTargetSupport` telde de reversal-candle die een overgang bevestigt standaard ook mee in de check die bepaalt of het niveau nadien is doorbroken - waardoor die candle, bij een gap t.o.v. de pivot-candle, zijn eigen pivot kon afkeuren. Op sommige databronnen (waargenomen op Pepperstone, gaps van 35-41 ticks) zorgde dit voor onterechte FALLBACK-uitkomsten bij Support/Target Support, ook al was er een overduidelijke pivot.
- Met de instelling AAN telt de reversal-candle niet meer mee voor de geldigheid van zijn eigen pivot (wel gewoon voor het beoordelen van oudere kandidaten verderop in de terugzoek-lus). De debug-toggle (`debugSupportPivot`) houdt hier ook rekening mee.
- Standaard UIT, zodat het gedrag exact hetzelfde blijft als voorheen (o.a. voor de FXCM-feed, waar dit al goed werkte) totdat je 'm zelf aanzet.

## [1.4.1]

### Opgelost
- Tekstkleur van de debug-labels was oranje op een (semi-transparante) oranje achtergrond en dus slecht leesbaar. Tekst staat nu in zwart, en het lettertype is een maatje groter (`size.small` i.p.v. `size.tiny`).

## [1.4.0]

### Toegevoegd
- Nieuwe (uit) instelling **"Debug: toon eerste Support-kandidaat + reden verwerping"** (groep "Support / Resistance"), voor het vergelijken van Support-detectie tussen verschillende databronnen/brokers.
- Zoekt onafhankelijk van de normale Support-logica de meest recente bearish->bullish overgang op en toont een oranje label op die kandidaat-candle, met `[GELDIG]` of `[VERWORPEN]`.
- Bij een verworpen kandidaat: een tweede oranje label op de eerste latere candle die met zijn body het kandidaat-niveau doorbreekt/raakt - dat is de candle die de kandidaat ongeldig maakt.
- Bedoeld als tijdelijk diagnosemiddel: door dezelfde instellingen op twee chart-databronnen (bv. Pepperstone vs. FXCM) te vergelijken, is te zien of ze dezelfde kandidaat-candle vinden en of dezelfde candle 'm afkeurt - zo niet, dan zit het verschil in de onderliggende koersdata van die bron, niet in de scriptlogica.

## [1.3.0]

### Toegevoegd
- Het LONG/SHORT-signaallabel zelf verdwijnt nu ook weer na `slSignalWindow` candles - hetzelfde signaalvenster als de SL-lijnen en de break-lijn al gebruikten. Zolang de eerstvolgende LONG of SHORT binnen dat venster valt, wordt het label meteen vervangen zoals voorheen; anders wordt het na het verlopen venster verwijderd.

## [1.2.1]

### Opgelost
- Break-lijn was niet exclusief: als binnen elkaars signaalvenster zowel een LONG- als een SHORT-signaal optrad, stonden beide break-lijnen tegelijk op het scherm. Nu geldt, net als bij de SL-lijnen, dat een nieuw signaal de break-lijn van de andere richting meteen verwijdert - maximaal 1 break-lijn zichtbaar.

## [1.2.0]

### Toegevoegd
- Lijnstukje op het niveau van de break zelf (Resistance/Support + x ticks), zwart, 1px, dashed - even lang als de SL-lijnen (`lineLen`). Verschijnt bij een LONG- resp. SHORT-signaal op het exacte niveau waar de doorbraak plaatsvond.
- Deze break-lijn wordt verwijderd volgens hetzelfde signaalvenster (`slSignalWindow`) als de SL-lijnen.

## [1.1.0]

### Toegevoegd
- Nieuwe setting **"SL: lijn actief na signaal (aantal candles)"** (groep "Stop Loss lijnen", default 5).
- De Long/Short SL-lijn wordt nu alleen getekend/getoond als: "Toon SL lijnen" aan staat, de candle bullish/bearish is, ÉN er binnen het ingestelde aantal candles een LONG- resp. SHORT-signaal is geweest (de signaal-candle zelf telt als candle 1 van het venster).
- Als het signaalvenster verloopt terwijl er geen nieuwe bullish/bearish candle is (bv. tijdens een reeks doji's), wordt de SL-lijn alsnog verwijderd.

### Gewijzigd
- Interne codevolgorde: het Support/Resistance- en signaalblok wordt nu vóór het SL-blok berekend, omdat de SL-lijn het LONG/SHORT-signaal van dezelfde candle nodig heeft. Geen functionele wijziging voor S/R of de signalen zelf.

## [1.0.0]

### Toegevoegd
- Eerste samengevoegde versie: `sl_lines.pine` (Stop Loss lijnen) en `sr_lines.pine` (Support/Resistance, Targets en breakout-signalen) samengevoegd tot één indicator, `trade_lines.pine`.
- `max_lines_count`/`max_labels_count` opgehoogd naar 30 zodat alle lijnen/labels van beide onderdelen tegelijk kunnen bestaan.
- Functionaliteit en instellingen van beide originele scripts ongewijzigd overgenomen.
