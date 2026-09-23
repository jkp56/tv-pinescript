# Handleiding – Trade Lijnen (SL/S/R)

Gebruikershandleiding voor `trade_lines.pine`, versie **1.9.20**. Voor de technische wijzigingsgeschiedenis zie [CHANGELOG.md](CHANGELOG.md); voor de exacte detectielogica zie [T4G daytrade rules.md](T4G%20daytrade%20rules.md). Dit document beschrijft hoe je het script gebruikt en wat elke instelling in het Inputs-tabblad wel en niet doet.

## 1. Wat doet dit script

De indicator tekent automatisch, zonder handmatig werk:

- **Support/Resistance-lijnen** op basis van candle-patronen.
- **Target-lijnen** (verder gelegen niveaus) die bepalen hoeveel "ruimte" een trade heeft.
- **LONG/SHORT-signalen** zodra de prijs een niveau met een marge doorbreekt.
- **Stop Loss (SL)-lijnen** bij elk signaal.
- Een **Take Profit (TP)-lijn**, of juist een **"Trade niet mogelijk"-label** als de trade niet aan de risk/reward-eisen voldoet.
- **Alerts** bij elk nieuw LONG/SHORT-signaal.

Alle berekeningen draaien **altijd op de 30-minuten candles**, ongeacht op welk timeframe je zelf kijkt.

## 2. Vereisten voor gebruik

- **Alleen de 15m- en 30m-chart worden ondersteund.** Op elk ander timeframe verschijnt een rood waarschuwingslabel ("Trade Lijnen: alleen 30m en 15m worden ondersteund") en tekent het script niets.
- Op de 15m-chart zie je exact dezelfde lijnen/niveaus als op de 30m-chart, omdat alles tijd-gebaseerd (`xloc.bar_time`) getekend wordt in plaats van bar-gebaseerd.
- **Belangrijk over timing:** de lijnen worden bijgewerkt op het moment dat een 30m-candle sluit — óók als je op dat moment naar de 15m-chart kijkt. Ze springen dus niet pas bij het terugschakelen naar 30m; ze volgen de 30m-klok, niet de 15m-klok. Op de 15m-chart kan het dus tot 15 minuten duren voordat een zojuist gesloten 30m-candle zichtbaar verwerkt is.
- Het script is repaint-vrij voor de nog lopende candle: zolang een 30m-candle nog niet is afgesloten, blijven alle lijnen op hun laatst bevestigde waarde staan.
- De standaardwaarde van `maxRTicks` (zie hieronder) is afgestemd op **XAUUSD** (tick-grootte 0,01). Gebruik je een ander symbool, controleer en herzie dan in elk geval deze instelling.

## 3. Wat zie je op de chart

| Element | Kleur (default) | Betekenis |
|---|---|---|
| Resistance-lijn | Rood, doorlopend | Dichtstbijzijnde geldige weerstand, loopt onbeperkt door naar rechts. Label toont hoeveel candles terug de pivot lag, of `[FALLBACK]` als er geen geldig patroon gevonden is (dan is het de hoogste high in de scanrange). |
| Support-lijn | Groen, doorlopend | Spiegelbeeld van Resistance. |
| Target Resistance-lijn | Rood, lichter/transparanter | Verder gelegen niveau boven Resistance; bepaalt de beschikbare "ruimte" voor een Long-trade. |
| Target Support-lijn | Groen, lichter/transparanter | Spiegelbeeld van Target Resistance, voor Short-trades. |
| Zwarte stippellijn + label "Resistance/Support doorbroken: …" | Zwart, gestippeld | Toont het exacte prijsniveau waarop het LONG/SHORT-signaal getriggerd is. Nodig omdat Resistance/Support na de doorbraak zelf herberekend wordt en dus kan verschuiven — deze lijn/label blijft het originele doorbroken niveau tonen. |
| Groene pijl omhoog / rode pijl omlaag | Groen/rood | LONG- resp. SHORT-signaallabel op de doorbraak-candle. Er is maximaal 1 signaallabel tegelijk zichtbaar; een nieuw signaal vervangt het vorige. |
| SL-lijn | Groen (Long) / rood (Short), gestippeld | Stop loss van het actieve signaal, inclusief prijswaarde in het label. Als de trade niet mogelijk is (zie Trade Mogelijkheid), verschijnt de reden in hetzelfde label en verandert de kleur naar de "niet mogelijk"-kleur (default oranje). |
| TP-lijn | Blauw, gestippeld | Take-profit niveau, alleen zichtbaar als de trade wél mogelijk is. |
| Rood waarschuwingslabel | Rood | Verschijnt alleen op een niet-ondersteund timeframe (zie §2). |
| Geel diagnosepaneel | Geel | Alleen zichtbaar met de debug-instelling `debugCalcPanel` aan; toont interne rekenwaarden voor troubleshooting. |

## 4. Wanneer wordt er bijgewerkt?

- Alle lijnen/labels worden **herbouwd bij elke gesloten 30m-candle** (nooit tussentijds op een tick).
- Staat **"Lijnen bevriezen zodra een geldige trade ontstaat"** (`freezeOnValidTrade`) aan, dan bevriest het script alles zodra er een geldige Long- of Short-trade ontstaat (zie §6 "Freeze") — pas daarna, op dat exacte moment, niet met terugwerkende kracht.

## 5. Alerts

Er vuurt automatisch een alert bij elk nieuw signaal (werkt met `alert()`, dus je moet zelf nog een TradingView-alert op deze indicator instellen om een notificatie te krijgen):

- **Bullish breakout**: "Bullish breakout: close boven Resistance + X ticks"
- **Bearish breakdown**: "Bearish breakdown: close onder Support - X ticks"

Elke alert vuurt **precies één keer per nieuw 30m-signaal**, ongeacht of je op de 15m- of 30m-chart kijkt (met een vertraging van maximaal één candle van je eigen chart-timeframe totdat de bijgewerkte 30m-waarde binnenkomt). De alert wordt **niet** onderdrukt als de trade achteraf "niet mogelijk" blijkt — dat wordt alleen visueel aangegeven via het label.

## 6. Instellingen (Inputs-tabblad)

### Groep "Info"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Versie | `1.9.20` | Puur informatief: toont de actieve scriptversie boven in de instellingen, zodat je niet in de code hoeft te kijken. | Heeft geen enkele invloed op de berekeningen of weergave; er is ook maar 1 optie beschikbaar. |

### Groep "Freeze"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Lijnen bevriezen zodra een geldige trade ontstaat (`freezeOnValidTrade`) | Uit | Zodra er, op de actuele (laatste) candle, een geldige Long- of Short-trade ontstaat, worden alle lijnen/labels precies op dat moment bevroren. Vanaf dan wordt er niets meer bijgewerkt — ook niet bij volgende 30m-candles — totdat je de instelling handmatig uit- en weer aanzet. | Bevriest niet met terugwerkende kracht in de geschiedenis (anders zou de allereerste geldige trade ooit alles al blokkeren) en bevriest niet meteen bij het aanzetten van de optie zelf — pas bij de eerstvolgende geldige trade daarna. Werkt alleen op de laatste candle van de chart. |

### Groep "Stop Loss lijnen"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Toon SL lijnen (`showSL`) | Aan | Schakelt de SL-lijn/label volledig in of uit. | Als je dit uitzet, verdwijnt **ook** de TP-lijn (die vereist `showSL` én `showTradeCheck` samen) — het zet dus niet alleen de SL-weergave uit. |
| SL: trailing (`trailSL`) | Uit | Als aan: de getoonde SL wordt bijgewerkt bij élke nieuwe candle van de juiste kleur binnen het signaalvenster (kan tijdens een sterke beweging "verspringen"). Als uit (default): de SL wordt eenmalig vastgezet op de signaal-candle zelf en blijft daarna ongewijzigd, net als de TP-lijn. | Heeft geen invloed op de TP-waarde of de Range-check — die blijven altijd vast op de signaal-candle, ongeacht deze instelling. |
| SL: aantal ticks van wick (`tickOffset`) | 50 | Afstand in ticks tussen de wick (low bij Long, high bij Short) van de signaal-/laatste candle en de SL-lijn. | Verandert niets aan hóe de SL bepaald wordt (nog steeds op basis van de wick), alleen de marge eromheen. |
| SL: lengte lijn (`lineLen`) | 20 | Hoeveel 30m-candles de SL-, TP- en break-lijnen naar rechts doorlopen. | Heeft **geen** effect op de Resistance/Support/Target-lijnen — die lopen altijd onbeperkt door naar rechts, ongeacht deze waarde. |
| SL: lijn actief na signaal (`slSignalWindow`) | 2 | Bepaalt het "signaalvenster": hoeveel 30m-candles (de signaal-candle zelf telt als candle 1) de SL-, TP- en "niet mogelijk"-labels zichtbaar blijven na een signaal. Wordt ook gebruikt om te voorkomen dat een kleine verschuiving van Support/Resistance een tweede, ongewenst signaal in dezelfde richting veroorzaakt terwijl het vorige venster nog loopt. | Heeft geen invloed op de Resistance/Support-lijnen zelf (die blijven gewoon doorlopend zichtbaar, los van dit venster). |
| Kleur Long SL (`longColor`) | Groen | Kleur van de SL-lijn/label bij een Long-signaal. | — |
| Kleur Short SL (`shortColor`) | Rood | Kleur van de SL-lijn/label bij een Short-signaal. | — |

### Groep "Support / Resistance"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Max bars terugzoeken (`maxScanBars`) | 450 (min 10, max 500) | Hoeveel 30m-candles terug het script maximaal zoekt naar een geldig Resistance/Support/Target-patroon, én de basis voor de fallback (hoogste/laagste punt in die range) als er geen patroon gevonden wordt. | Verhogen kost meer rekentijd; het script zoekt nooit verder terug dan deze grens, ook niet als er dieper een "beter" niveau zou liggen. |
| Fallback afstand target lijnen (ticks) (`autoTargetTicks`) | 100 | Vaste afstand (in ticks) die gebruikt wordt voor de Target-lijn **als** er binnen `maxScanBars` geen geldige overgang gevonden wordt. | Wordt genegeerd zodra er wél een geldig patroon gevonden wordt — dan telt alleen dat niveau. De werkelijk gebruikte fallback is bovendien nooit kleiner dan `minTargetDistance` (het hoogste van de twee wordt gebruikt). |
| Minimale afstand Target t.o.v. Resistance/Support (ticks) (`minTargetDistance`) | 300 | Minimaal vereiste afstand tussen een Target-kandidaat en Resistance/Support. Een kandidaat die dichterbij ligt, wordt afgekeurd; het script zoekt dan verder terug én onthoudt dat afgekeurde niveau als mogelijk "tussenliggend" niveau waar Resistance/Support zelf naar kan verschuiven. | Verandert niets aan hóe Resistance/Support zelf in eerste instantie gevonden wordt — alleen aan de Target-zoektocht en de eventuele verschuiving van Resistance/Support die daaruit volgt. |
| Labelkleur (tekst) (`labelTextColor`) | Zwart | Tekstkleur van de Resistance/Support/Target-labels en de "doorbroken"-labels. | Heeft geen invloed op de kleur van de SL/TP-labels (die hebben hun eigen kleurinstellingen) of op de lijnkleuren zelf. |
| Support/Resistance: reversal-candle uitsluiten van eigen invalidatie (`excludeReversalCandle`) | Aan | Bepaalt of de candle die een bullish/bearish-overgang zelf afrondt, meetelt in de check die dat niveau weer ongeldig kan maken. Standaard (aan) telt die candle niet mee voor zijn eigen invalidatie, wat voorkomt dat een fractie van een tick verschil tussen broker-datafeeds een niveau onterecht laat overslaan. | Latere candles (ná de overgang) kunnen het niveau nog steeds normaal ongeldig maken — deze instelling geldt alleen voor de candle die de overgang zelf vormt. |
| Debug: toon eerste Support-kandidaat + reden verwerping (`debugSupportPivot`) | Uit | Alleen bedoeld voor troubleshooting/vergelijking tussen databronnen. Toont een label op de allereerste Support-kandidaat en, indien afgekeurd, waar deze precies "breekt". | Werkt **uitsluitend op de native 30m-chart** (niet op 15m) en heeft geen invloed op de daadwerkelijk getekende Support-lijn — puur ter controle. |
| Debug: toon diagnosepaneel (`debugCalcPanel`) | Uit | Toont een geel paneel rechtsboven met interne rekenwaarden (o.a. of `calc*`-waarden gevuld worden en of er nieuwe data binnenkomt). Bedoeld om te controleren of het script correct doorrekent. | Heeft geen invloed op de berekeningen zelf, alleen op de weergave van een diagnosepaneel. Laat dit voor normaal gebruik uit. |

### Groep "Signaal instellingen"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| X: aantal ticks voorbij S/R voor signaal (`xTicks`) | 10 | Marge (in ticks) die de close voorbij Resistance (Long) of onder Support (Short) moet sluiten voordat een LONG/SHORT-signaal (en dus ook de SL/TP-berekening) getriggerd wordt. | Heeft geen invloed op waar Resistance/Support zelf getekend wordt — alleen op de drempel voor het signaal. |

### Groep "Trade Mogelijkheid"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Toon TP-lijn en Trade-mogelijkheid check (`showTradeCheck`) | Aan | Schakelt de TP-lijn en de Range/R-controle (en dus het "Trade niet mogelijk"-label) in of uit. | Uitzetten onderdrukt **niet** de LONG/SHORT-alert of de signaallabels/SL-lijn zelf — alleen de TP-gerelateerde weergave verdwijnt. Vereist bovendien dat `showSL` ook aanstaat, anders verschijnt er sowieso geen TP-lijn. |
| TP: Risk/Reward ratio (`tpRR`) | 1.2 | Bepaalt de TP-afstand als veelvoud van R (het risico): `TP = entry ± tpRR × R`. | Heeft geen invloed op of de trade "mogelijk" is — dat wordt apart bepaald door `minRangeRR` en `maxRTicks`. |
| Minimaal benodigde R/R-ruimte in de Range (`minRangeRR`) | 1.0 | De beschikbare ruimte tussen Resistance/Support en de bijbehorende Target-lijn moet minimaal `minRangeRR × R` zijn, anders is de trade "niet mogelijk" (geen TP-lijn, wel een label met de reden). De gemeten Range staat altijd in R in het label: bij een mogelijke trade achter de TP-waarde ("· Range 1.62R"), bij een niet-mogelijke trade in de reden (bijv. "Range 0.92R < 1R (3.50 < 3.80)"). | Tot v1.9.23 was de default 1.5R; dat bleek te streng voor trades met een TP rond 1.2R en gaf bij grensgevallen verschillen tussen broker-feeds (bijv. 1.46R op FTMO_OANDA vs 1.50R op FXCM). Omdat R en de S/R-niveaus per feed iets verschillen, kan een grensgeval op de ene broker net wel en op de andere net niet slagen — beoordeel dat zelf aan de hand van de getoonde R-waarde. Is onafhankelijk van de `maxRTicks`-check hieronder; beide voorwaarden kunnen los van elkaar (of tegelijk) een trade blokkeren. |
| Maximaal toegestane R (ticks) (`maxRTicks`) | 1000 | Als het risico R (in ticks) groter is dan deze waarde, is de trade sowieso "niet mogelijk", ongeacht de Range-check. | **Let op:** deze default (1000 ticks = 100 pips / $10 SL) is specifiek afgestemd op **XAUUSD** (tick-grootte 0,01). Op een ander symbool of een andere tick-grootte moet je deze waarde zelf opnieuw bepalen — het script doet dat niet automatisch. |
| Kleur TP-lijn (`tpColor`) | Blauw | Kleur van de TP-lijn/label wanneer de trade mogelijk is. | — |
| Kleur 'Trade niet mogelijk'-label (`noTradeColor`) | Oranje | Kleur van de SL-lijn/label wanneer de trade **niet** mogelijk is (de reden wordt dan in het SL-label getoond). | Er is geen apart losstaand "niet mogelijk"-label meer (sinds v1.9.18) — de reden staat in het SL-label zelf, dus zonder `showSL` zie je deze melding niet. |

## 7. Veelgestelde vragen

**Waarom zie ik geen TP-lijn, terwijl er wel een LONG/SHORT-signaal is?**
Twee mogelijke oorzaken: (1) `showSL` of `showTradeCheck` staat uit — beide moeten aan staan; (2) de trade is "niet mogelijk" volgens de Range- of R-check — kijk dan naar de reden in het SL-label.

**Waarom verschuift Resistance/Support ineens naar een ander niveau?**
Zodra de huidige lijn door een candle-body doorbroken wordt, is ze ongeldig geworden en berekent het script automatisch het eerstvolgende geldige (verder terugliggende) niveau. Dit kan er tegelijk voor zorgen dat de drempel voor een nieuw signaal (`Resistance/Support ± xTicks`) verschuift — het script voorkomt hierbij expliciet dat zo'n verschuiving een tweede, ongewenst signaal in dezelfde richting veroorzaakt zolang het vorige signaalvenster nog loopt.

**Waarom loopt de SL/TP-lijn niet even ver door als de Resistance/Support-lijn?**
Dat is bewust: `lineLen` bepaalt alleen de lengte van SL/TP/break-lijnen. Resistance/Support/Target lopen altijd onbeperkt door naar rechts.

**Ik zie het rode waarschuwingslabel "alleen 30m en 15m worden ondersteund" — wat nu?**
Schakel de chart naar het 30m- of 15m-timeframe; op elk ander timeframe tekent het script bewust niets.

**Moet ik zelf nog iets instellen voor de alerts?**
Ja — de indicator roept `alert()` aan, maar je moet in TradingView zelf nog een alert aanmaken op deze indicator (Conditie: "Trade Lijnen (SL/S/R)") om een notificatie te ontvangen.
