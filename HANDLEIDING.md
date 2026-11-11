# Handleiding – Trade Lijnen (SL/S/R)

Gebruikershandleiding voor `trade_lines.pine`, versie **1.18.0**. Voor de technische wijzigingsgeschiedenis zie [CHANGELOG.md](CHANGELOG.md); voor de exacte detectielogica zie [T4G daytrade rules.md](T4G%20daytrade%20rules.md). Dit document beschrijft hoe je het script gebruikt en wat elke instelling in het Inputs-tabblad wel en niet doet.

## 1. Wat doet dit script

De indicator tekent automatisch, zonder handmatig werk:

- **Support/Resistance-lijnen** op basis van candle-patronen.
- **Target-lijnen** (verder gelegen niveaus) die bepalen hoeveel "ruimte" een trade heeft.
- **LONG/SHORT-signalen** zodra een candle met een marge voorbij een niveau sluit (de breakout-candle). Standaard is elke 15m-candle een mogelijke breakout-candle; daarnaast telt de 30m-candle.
- Een **BO-marker** bij de breakout-candle, met **(15m)** of **(30m)** erbij.
- **Stop Loss (SL)-lijnen** bij elk signaal, bepaald op de breakout-candle.
- Een **Take Profit (TP)-lijn**, of juist een **"Trade niet mogelijk"-blok** als de trade niet aan de risk/reward-eisen voldoet.
- Optionele **flip-hulplijnen** (0,12 × body terug / 0,6R door) om de flip met het oog te beoordelen.
- **Alerts** bij elk nieuw LONG/SHORT-signaal, met entry, SL, TP en of de trade mogelijk is.

De Support/Resistance- en Target-niveaus worden **altijd op de 30-minuten candles** berekend, ongeacht op welk timeframe je zelf kijkt. De breakout zelf wordt (standaard) per 15m-candle bekeken: entry, SL, R, TP, de Range-check en de max-R-check komen van de candle die de breakout geeft. Alles draait op de rekenfeed (standaard FXCM, zie §6 "Rekenfeed").

## 2. Vereisten voor gebruik

- **Alleen de 15m- en 30m-chart worden ondersteund.** Op elk ander timeframe verschijnt een rood waarschuwingslabel ("Trade Lijnen: alleen 30m en 15m worden ondersteund") en tekent het script niets.
- Op de 15m-chart zie je exact dezelfde lijnen/niveaus als op de 30m-chart, omdat alles tijd-gebaseerd (`xloc.bar_time`) getekend wordt in plaats van bar-gebaseerd.
- **Timing:** zie §4. Kort: een breakout op de **1e 15m-candle** van een 30m-candle zie je direct bij het sluiten van die 15m-candle (vroeg signaal), op de 15m-chart én (sinds v1.16.0, live) op de 30m-chart. Al het andere (ook een breakout op de 2e 15m-candle) verschijnt bij het sluiten van de 30m-candle.
- Het script is repaint-vrij voor de nog lopende candle: zolang een candle nog niet is afgesloten, blijven alle lijnen op hun laatst bevestigde waarde staan. Een signaal verschijnt pas als de breakout-candle ook op je **eigen chart** gesloten is, ook als de rekenfeed (FXCM) al verder is. Dat voorkomt te vroege signalen in Bar Replay of bij een andere chart-feed.
- De standaardwaarde van `maxRPoints` (zie hieronder) is afgestemd op **XAUUSD**: 10 punten = 100 pips. Op de Nasdaq (US100/NAS100) gebruik je 110. Gebruik je een ander symbool, controleer en herzie dan in elk geval deze instelling, net als de contractgrootte (groep Lotgrootte).

## 3. Wat zie je op de chart

| Element | Kleur (default) | Betekenis |
|---|---|---|
| Resistance-lijn | Rood, doorlopend | Dichtstbijzijnde geldige weerstand, loopt onbeperkt door naar rechts. Label toont hoeveel candles terug de pivot lag, of `[FALLBACK]` als er geen geldig patroon gevonden is (dan is het de hoogste high in de scanrange). |
| Support-lijn | Groen, doorlopend | Spiegelbeeld van Resistance. |
| Target Resistance-lijn | Rood, lichter/transparanter | Verder gelegen niveau boven Resistance; bepaalt de beschikbare "ruimte" voor een Long-trade. |
| Target Support-lijn | Groen, lichter/transparanter | Spiegelbeeld van Target Resistance, voor Short-trades. |
| BO-marker "BO (15m)" / "BO (30m)" | Groen (Long) / rood (Short) | Markeert de breakout-candle: de candle waarvan de close voorbij Resistance/Support de breakout bepaalt. (15m) of (30m) geeft aan of het een 15m- of 30m-breakout is; dat staat ook in de SL/TP-labels en de alert. Alleen zichtbaar als *Toon SL lijnen* aan staat (sinds v1.12.4). |
| Zwarte stippellijn + label "Resistance/Support doorbroken: …" | Zwart, gestippeld | Toont het exacte prijsniveau waarop het LONG/SHORT-signaal getriggerd is. Nodig omdat Resistance/Support na de doorbraak zelf herberekend wordt en dus kan verschuiven — deze lijn/label blijft het originele doorbroken niveau tonen. Alleen zichtbaar als *Toon SL lijnen* aan staat (sinds v1.9.29). De lijn loopt `lineLen` candles vanaf de breakout-candle; daar begint het label (sinds v1.9.33). Op de 15m-chart beginnen de lijnen bij de candle waarvan de close de breakout bepaalt (sinds v1.12.4). |
| Gestippelde lijn + label "Target Resistance/Support bij break: …" | Rood (Long) / groen (Short), gestippeld | Het Target zoals het vóór de signaal-candle op de chart stond: het target waarmee de Range-check rekent. Het Target op de chart zelf wordt na de break herberekend en kan verspringen; deze lijn blijft het oorspronkelijke target tonen. Ligt de lijn al aan de verkeerde kant van de close, dan is de Range negatief. Valt het niveau samen met een Resistance/Support/Target-label, dan wordt het samengevoegd ("= Target bij break") of boven/onder dat label gezet, zodat ze niet overlappen. Alleen zichtbaar als *Toon SL lijnen* aan staat (sinds v1.9.38). |
| SL-lijn | Groen (Long) / rood (Short), gestippeld | Stop loss van het actieve signaal, inclusief prijswaarde in het label. Bepaald op de wick van de breakout-candle (15m of 30m) plus `tickOffset`. Wordt **niet** getekend als de trade niet mogelijk is (sinds v1.9.37). |
| Tabel 15m/30m (breakout om :00/:30) | Blauw = getekende variant, groen = mogelijk, oranje = niet mogelijk | Om :00 en :30 sluiten de 15m- en de 30m-candle tegelijk. Dan toont een tabel (op de plek van het "Trade niet mogelijk"-blok) beide varianten naast elkaar: Entry, SL, R, TP, Range en Status. De entry is gelijk; SL, R, TP en de Range-check verschillen (wick van de 2e 15m-candle of van de hele 30m-candle). De kolom met "◀ lijnen" is de variant waarvan de SL/TP- en flip-lijnen getekend zijn (instelling `bkMode`). Verschijnt bij elk signaal om :00/:30, ook als beide mogelijk zijn (sinds v1.18.0). |
| "Trade niet mogelijk"-blok | Oranje | Vast blok op het scherm (default rechtsboven, instelbaar) met richting, feed en de reden(en) waarom het actieve signaal geen geldige trade is. Verdwijnt zodra het signaalvenster afloopt. De "doorbroken"-lijn blijft gewoon staan. |
| TP-lijn | Blauw, gestippeld | Take-profit niveau, alleen zichtbaar als de trade wél mogelijk is. Het label toont ook entry, R, Range en (sinds v1.9.28) de lotgrootte met het bijbehorende risico in $. |
| Flip-hulplijnen "Flip 0.12 body" en "Te ver zonder flip 0.6R" | Paars, gestippeld | Alleen als *Toon flip-hulplijnen* aan staat en de trade mogelijk is. Beginnen bij de flip-candle: de eerstvolgende candle na de breakout-candle (op hetzelfde timeframe). "Flip" ligt 0,12 × de body van de breakout-candle terug vanaf de entry (Gann box op de body: close = 0, open = 1); "Te ver zonder flip" ligt 0,6R voorbij de entry. Het flip-label wordt boven of onder het "doorbroken"-label gezet als ze anders overlappen. Puur visueel, het script beslist er niets mee (sinds v1.11.0; op de body sinds v1.13.0). |
| Rood waarschuwingslabel | Rood | Verschijnt alleen op een niet-ondersteund timeframe (zie §2). |

## 4. Wanneer wordt er bijgewerkt?

- Alle lijnen/labels worden **herbouwd bij elke gesloten 30m-candle** (nooit tussentijds op een tick).
- **Uitzondering, het vroege 15m-signaal** (`signal15On`): sluit de 1e 15m-candle van een 30m-candle voorbij Resistance/Support, dan verschijnen lijnen, BO-marker en alert direct bij het sluiten van die 15m-candle. Op de 15m-chart bij de close van die candle; op de 30m-chart (sinds v1.16.0) bij de eerste tick daarna, terwijl de 30m-candle nog loopt. Dat werkt alleen live: in de geschiedenis is elke 30m-candle al gesloten. Bij de 30m-close wordt dat signaal niet nog eens gegeven: per breakout is er maar één signaal, 15m of 30m.
- Een breakout om **:00/:30** (de 2e 15m-candle en de 30m-candle sluiten tegelijk) verschijnt bij de 30m-close. Signaal, lijnen en marker horen bij de variant uit `bkMode` (standaard 15m: entry, SL en R van de 2e 15m-candle); de andere variant staat in de tabel en de alert.
- Een signaal verschijnt nooit voordat de breakout-candle op je eigen chart gesloten is (zie §2).
- **Signaalvenster en doorschuiven** (`slSignalWindow`): na een mogelijke trade telt binnen het venster geen nieuw signaal in dezelfde richting. Was het signaal "Trade niet mogelijk", dan telt een breakout van een verder liggend niveau wel direct (doorschuiven naar de volgende range, sinds v1.15.0).
- Staat **"Lijnen bevriezen zodra een geldige trade ontstaat"** (`freezeOnValidTrade`) aan, dan bevriest het script alles zodra er een geldige Long- of Short-trade ontstaat (zie §6 "Freeze") — pas daarna, op dat exacte moment, niet met terugwerkende kracht.

## 5. Alerts

Er vuurt automatisch een alert bij elk nieuw signaal (werkt met `alert()`, dus je moet zelf nog een TradingView-alert op deze indicator instellen om een notificatie te krijgen):

- **Bullish breakout**: `XAUUSD (FXCM) Bullish breakout (15m): close boven Resistance + 0.01% | Entry … · SL … · TP … | Trade mogelijk`
- **Bearish breakdown**: `XAUUSD (FXCM) Bearish breakdown (30m): close onder Support - 0.01% | Entry … · SL … · TP … | Trade niet mogelijk: Range 1.17R < 1.5R (10.23 < 13.11)`

De tekst bevat het symbool met de rekenfeed, de richting, (15m) of (30m), het ingestelde percentage, Entry, SL, TP en of de trade mogelijk is, met de reden als dat niet zo is (sinds v1.14.0). Bij een breakout om :00/:30 volgt ook de andere variant, bijv. `| 30m: SL … · TP … · niet mogelijk: Range 0.98R < 1.5R` (sinds v1.18.0). Staat `showTradeCheck` uit, dan vervallen TP en de status. De prijzen zijn die van de rekenfeed.

Elke alert vuurt **precies één keer per signaal**:
- een vroeg 15m-signaal alert op de 15m-chart direct bij het sluiten van de 1e 15m-candle, op de 30m-chart bij de eerste tick daarna (sinds v1.16.0);
- een 30m-signaal, of een breakout op de 2e 15m-candle, alert bij het sluiten van de 30m-candle **op de chart zelf** (niet eerder op een lopende 30m-waarde);
- op de 30m-chart volgt bij de 30m-close geen tweede alert voor een signaal dat al live gealert is. Was de chart tijdens die candle niet live (bijv. net geopend), dan komt het 15m-signaal bij de 30m-close binnen, met "(15m)" in de tekst.
- Staat er op een 15m- én een 30m-chart een alert, dan krijg je van elke chart een melding.

De alert wordt **niet** onderdrukt als de trade "niet mogelijk" is; dat staat in de tekst en in het "Trade niet mogelijk"-blok.

## 6. Instellingen (Inputs-tabblad)

### Groep "Info"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Versie | `1.18.0` | Puur informatief: toont de actieve scriptversie boven in de instellingen, zodat je niet in de code hoeft te kijken. | Heeft geen enkele invloed op de berekeningen of weergave; er is ook maar 1 optie beschikbaar. |

### Groep "Rekenfeed"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Berekeningen op andere feed dan de chart (`useSourceFeed`) | Aan | Alle berekeningen (Resistance/Support, Targets, signalen, SL/TP, Range-/R-check, lotgrootte) draaien op de rekenfeed in plaats van op de chart-feed. Op een FTMO_OANDA-chart zie je dan de beslissing van FXCM. In de labels staat de feed erbij, bijv. `Long SL (FXCM): …`. | Rekent de prijzen niet om naar de chart-feed: SL, TP en levels zijn de FXCM-prijzen en kunnen een paar tienden afwijken van de OANDA-candles. |
| Exchange-prefix van de rekenfeed (`sourceExchange`) | `FX` | De exchange die voor de ticker van de chart wordt gezet. TradingView gebruikt voor FXCM de prefix `FX`, dus `FX` → `FX:XAUUSD` (in de labels staat dan "FXCM"). `FXCM` werkt niet: dat geeft "Invalid symbol". | Is de prefix gelijk aan die van de chart, of leeg, dan rekent het script gewoon op de chart-feed. Het symbool moet op die exchange onder dezelfde naam bestaan; bij `FX` worden afwijkende OANDA-namen vertaald (bijv. `NAS100USD` → `NAS100`, `US30USD` → `US30`). Bij FTMO-namen met `.cash` valt dat achtervoegsel weg (bijv. `US100.cash` → `NAS100`, `US500.cash` → `SPX500`, `GER40.cash` → `GER30`; sinds v1.15.1). |

### Groep "Freeze"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Lijnen bevriezen zodra een geldige trade ontstaat (`freezeOnValidTrade`) | Uit | Zodra er, op de actuele (laatste) candle, een geldige Long- of Short-trade ontstaat, worden alle lijnen/labels precies op dat moment bevroren. Vanaf dan wordt er niets meer bijgewerkt — ook niet bij volgende 30m-candles — totdat je de instelling handmatig uit- en weer aanzet. | Bevriest niet met terugwerkende kracht in de geschiedenis (anders zou de allereerste geldige trade ooit alles al blokkeren) en bevriest niet meteen bij het aanzetten van de optie zelf — pas bij de eerstvolgende geldige trade daarna. Werkt alleen op de laatste candle van de chart. |

### Groep "Stop Loss lijnen"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Toon SL lijnen (`showSL`) | Aan | Schakelt de SL-lijn/label volledig in of uit. | Als je dit uitzet, verdwijnen **ook** de TP-lijn (die vereist `showSL` én `showTradeCheck` samen) en de zwarte "Resistance/Support doorbroken"-lijn met label (sinds v1.9.29) en de target-lijn bij de break (sinds v1.9.38) — het zet dus niet alleen de SL-weergave uit. |
| SL: trailing (`trailSL`) | Uit | Als aan: de getoonde SL wordt bijgewerkt bij élke nieuwe candle van de juiste kleur binnen het signaalvenster (kan tijdens een sterke beweging "verspringen"). Als uit (default): de SL wordt eenmalig vastgezet op de signaal-candle zelf en blijft daarna ongewijzigd, net als de TP-lijn. | Heeft geen invloed op de TP-waarde of de Range-check — die blijven altijd vast op de signaal-candle, ongeacht deze instelling. |
| SL: aantal ticks van wick (`tickOffset`) | 50 | Afstand in ticks tussen de wick (low bij Long, high bij Short) van de signaal-/laatste candle en de SL-lijn. | Verandert niets aan hóe de SL bepaald wordt (nog steeds op basis van de wick), alleen de marge eromheen. |
| SL/TP/doorbroken: lengte lijn tot label (`lineLen`) | 5 | Hoeveel 30m-candles de SL-, TP- en break-lijnen vanaf de breakout-candle naar rechts lopen. Waar de lijn eindigt, begint het label (sinds v1.9.33; daarvoor default 20 en stond het label aan het eind van een lange lijn). | Heeft **geen** effect op de Resistance/Support/Target-lijnen — die lopen altijd onbeperkt door naar rechts, ongeacht deze waarde. |
| SL: lijn actief na signaal (`slSignalWindow`) | 2 | Bepaalt het "signaalvenster": hoeveel 30m-candles (de signaal-candle zelf telt als candle 1) de SL-, TP- en break-lijnen met hun labels (incl. de "niet mogelijk"-reden) zichtbaar blijven na een signaal. Wordt ook gebruikt om te voorkomen dat een kleine verschuiving van Support/Resistance een tweede, ongewenst signaal in dezelfde richting veroorzaakt terwijl het vorige venster nog loopt. Die blokkade geldt alleen na een **mogelijke** trade: was het vorige signaal "Trade niet mogelijk", dan telt een breakout van een verder liggend niveau (hogere Resistance bij Long, lagere Support bij Short) direct als nieuw signaal (doorschuiven, vanaf 1.15.0). | Heeft geen invloed op de Resistance/Support-lijnen zelf (die blijven gewoon doorlopend zichtbaar, los van dit venster). |
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
| Body-tolerantie voor candle na de overgang (`bodyTolEnabled`) + Body-tolerantie (ticks) (`bodyTolTicks`) | Uit / 50 | Staat deze aan, dan mag de candle **direct na** de reversal-candle met zijn body maximaal `bodyTolTicks` door het level gaan zonder het ongeldig te maken, mits die candle in de respecterende richting sluit (bullish bij Support/Target Support, bearish bij Resistance/Target Resistance). Voorkomt dat een paar tienden verschil tussen broker-feeds (bijv. FTMO_OANDA vs FXCM) een level laat vervallen. Op XAUUSD (tick 0.01) is 50 ticks = 0.50. | Geldt niet voor latere candles en niet voor een candle in de aanvallende richting: die blijven strikt. Verandert niets aan de wick-check van de Target-lijnen. |
| Body-tolerantie voor alle latere candles (`laterTolEnabled`) + Body-tolerantie latere candles (ticks) (`laterTolTicks`) | Uit / 50 | Staat deze aan, dan mag **elke** candle na de overgang, ongeacht kleur, met zijn body maximaal `laterTolTicks` door het level gaan zonder het ongeldig te maken. Voorkomt dat bijv. een break-candle die op de ene feed net onder en op de andere net boven het level sluit, het level op één broker laat vervallen. Op XAUUSD (tick 0.01) is 50 ticks = 0.50. | Een body die verder dan de tolerantie doorgaat maakt het level nog steeds ongeldig. Verandert niets aan de wick-check van de Target-lijnen. Is de tolerantie groter dan de break-tolerantie (`breakPct`), dan kan een close tussen die twee grenzen een breakout-signaal geven terwijl het level blijft staan. |
| Overgang over dagsluiting/weekend: level = open van de reversal-candle (`sessionGapOpen`) | Aan | Ligt er tussen de pivot-candle en de reversal-candle een tijdsgat (dagsluiting of weekend), dan wordt het level de **open van de reversal-candle**, de eerste prijs na de gap, in plaats van de close van de pivot-candle. Geldt bij gap up én gap down, voor Support, Resistance en beide Target-lijnen. De close vlak voor de dagsluiting is door dunne handel en brede spread per broker onbetrouwbaar (bijv. FTMO_OANDA vs FXCM). | Verandert niets aan overgangen zonder tijdsgat. Het label blijft het aantal candles tot de pivot-candle tonen en de lijn begint daar ook. |

### Groep "Signaal instellingen"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Break-tolerantie: close voorbij S/R (% van het level) (`breakPct`) | 0,01% | Hoe ver de close van de breakout-candle (15m of 30m) voorbij Resistance (Long) of onder Support (Short) moet sluiten, als percentage van het level, voordat een LONG/SHORT-signaal (en dus ook de SL/TP-berekening) getriggerd wordt. Alleen de close telt, wicks spelen geen rol. 0,01% = ca. 0,40 op XAUUSD (~4000) en ca. 2,7 punt op NAS100 (~27000). Na te meten met de price range tool van TradingView (de "%"-waarde). | Heeft geen invloed op waar Resistance/Support zelf getekend wordt — alleen op de drempel voor het signaal. |
| Breakout om :00/:30 (15m en 30m sluiten tegelijk): SL/TP-lijnen van (`bkMode`) | 15m | Tradeplan: bij een gelijktijdige close speel je standaard de 15m, en de 30m bij een doji, een 15m-SL op het level, geen wick of een zwakke break-out. **15m:** signaal, SL, TP, Range-/max-R-check en flip-lijnen van de 2e 15m-candle. **30m:** van de hele 30m-candle (met de rejection-check als die aanstaat). Kies je na afweging de 30m, zet de instelling om: de lijnen springen naar de 30m-waarden. De andere variant staat altijd in de tabel en de alert. Tot v1.17.0 heette dit "Breakout-candle" met de opties "Elke 15m-candle" (= 15m) en "30m-candle + 1e 15m" (= 30m). | Een breakout om :15/:45 is altijd 15m. Verandert niets aan hoe S/R en Targets berekend worden (altijd op 30m). Bepaalt ook welke variant meetelt voor het signaalvenster en doorschuiven. |
| Ook breakout op de 1e 15m-candle van de 30m (vroeg signaal) (`signal15On`) | Aan | Sluit de 1e 15m-candle al voorbij S/R, dan is dat het signaal, met entry, SL en R van die 15m-candle. Je ziet het direct bij het sluiten van die 15m-candle, op de 15m-chart én live op de 30m-chart (sinds v1.16.0). | Per breakout is er maar één signaal: 15m of 30m. Uit = de 1e 15m-candle telt niet apart. |

### Groep "Trade Mogelijkheid"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Toon TP-lijn en Trade-mogelijkheid check (`showTradeCheck`) | Aan | Schakelt de TP-lijn en de Range/R-controle (en dus het "Trade niet mogelijk"-blok) in of uit. | Uitzetten onderdrukt **niet** de LONG/SHORT-alert, de break-lijn of de SL-lijn zelf — alleen de TP-gerelateerde weergave verdwijnt. Vereist bovendien dat `showSL` ook aanstaat, anders verschijnt er sowieso geen TP-lijn. |
| TP: Risk/Reward ratio (`tpRR`) | 1.2 | Bepaalt de TP-afstand als veelvoud van R (het risico): `TP = entry ± tpRR × R`. | Heeft geen invloed op of de trade "mogelijk" is — dat wordt apart bepaald door `minRangeRR` en `maxRTicks`. |
| Minimaal benodigde R/R-ruimte in de Range (`minRangeRR`) | 1.5 | De beschikbare ruimte tussen de entry en de bijbehorende Target-lijn (Target Resistance bij Long, Target Support bij Short), zoals die lijn op de chart stond op het moment van de break, moet minimaal `minRangeRR × R` zijn, anders is de trade "niet mogelijk" (geen TP- en SL-lijn, wel het "Trade niet mogelijk"-blok met de reden). De gemeten Range staat altijd in R in het label: bij een mogelijke trade achter de TP-waarde, samen met entry en R ("TP (1.2 R/R): 4279.86 · Entry 4284.16 · R 3.58 · Range 1.62R"), bij een niet-mogelijke trade in de reden (bijv. "Range 1.17R < 1.5R (10.23 < 13.11)": de ruimte is 10.23, nodig is 1,5 × R = 13.11). Volgens het tradeplan is 1,5R ruimte nodig voor een trade met een TP van 1,2R (default weer 1.5 sinds v1.13.0; v1.9.23 t/m 1.12 was het 1.0). | Entry en R komen van de breakout-candle (15m of 30m). Omdat R en de S/R-niveaus per feed iets verschillen, kan een grensgeval op de ene broker net wel en op de andere net niet slagen — beoordeel dat zelf aan de hand van de getoonde R-waarde. Is onafhankelijk van de `maxRTicks`-check hieronder; beide voorwaarden kunnen los van elkaar (of tegelijk) een trade blokkeren. |
| Maximaal toegestane R (punten) (`maxRPoints`) | 10 | Als het risico R (entry tot SL, in punten = prijseenheden) van de breakout-candle groter is dan deze waarde, is de trade sowieso "niet mogelijk", ongeacht de Range-check. Reden in het blok bijv. "R 46.50 > max 10 punten". Punten zijn wat de price range tool als prijsverschil toont. Richtwaarden (tooltip): **XAUUSD 10** (= 100 pips, $10 SL), **Nasdaq 110** (110 indexpunten, waarde van de coach). Tot v1.16.0 stond deze instelling in ticks (`maxRTicks`, 1000). | Wordt niet automatisch per symbool bepaald: stel hem per chart in. Pas op met "pips": bij goud is 1 pip 0,10, bij indices meestal 1 punt. |
| Rejection candle (15m) maakt trade ongeldig, alleen bij 30m-signaal (`rejectionOn`) | Uit | Geldt alleen voor een 30m-signaal. Kijkt naar de twee 15m-candles van de breakout-30m-candle, op de rekenfeed. Sluit de **tweede** 15m-candle tegen de trade-richting in (bearish bij Long, bullish bij Short) met een body van minimaal `rejectionTicks`, dan is de trade "niet mogelijk". Het "Trade niet mogelijk"-blok toont dan bijv. "Rejection candle 15m (85 ticks >= 50)". | Een doji of een kleinere tegengestelde body telt niet als rejection. Latere candles in het signaalvenster worden niet gecontroleerd. De LONG/SHORT-alert gaat gewoon af. Komt uit de NASDAQ-strategie, daarom standaard uit; zet hem per chart aan. |
| Rejection candle: minimale tegengestelde body (`rejectionTicks`) | 50 | Minimale body (in ticks, verschil tussen open en close) van de tegengestelde tweede 15m-candle om als rejection te tellen. | **Let op:** ticks zijn per symbool anders. Op XAUUSD is 50 ticks $0,50; controleer de tick-grootte van je NASDAQ-symbool en stel de waarde daarop af. |
| Kleur TP-lijn (`tpColor`) | Blauw | Kleur van de TP-lijn/label wanneer de trade mogelijk is. | — |
| Kleur 'Trade niet mogelijk'-blok (`noTradeColor`) | Oranje | Achtergrondkleur van het "Trade niet mogelijk"-blok. | — |
| Positie 'Trade niet mogelijk'-blok (`noTradePosStr`) | Rechtsboven | Waar het blok op het scherm staat: rechts-, midden- of linksboven/-midden/-onder. Het blok staat vast op die schermpositie, los van prijs en tijd. | Verschijnt ook als `showSL` uitstaat (sinds v1.9.37); alleen `showTradeCheck` uit zet het blok uit. |

### Groep "Flip-hulplijnen"

Hulpmiddel om de flip live met het oog te beoordelen. De flip-candle is de eerstvolgende candle na de breakout-candle, op hetzelfde timeframe (na een 15m-breakout dus de volgende 15m-candle). Tijdens zijn vorming moet die eerst minimaal 0,12 × de body van de breakout-candle tegen de break in komen (een wick-raak telt) en daarna weer de kleur van de breakout krijgen. Tradeplan: komt de prijs eerst 0,6R in de trade-richting zonder flip, dan is het "te ver"; gaat de prijs voorbij de wick van de breakout-candle, dan is het "te diep". Geen flip, geen trade. De lijnen beslissen niets; ze vervangen alleen het meten met een Gann box of de price range tool.

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Toon flip-hulplijnen (`showFlipLines`) | Uit | Tekent bij een mogelijke trade de twee flip-lijnen, van de flip-candle tot het labelpunt (`lineLen`). | Geen lijnen als de trade niet mogelijk is. Geen alert, geen invloed op "Trade mogelijk". |
| Flip: diepte terug vanaf de entry, deel van de body (`flipMinRR`) | 0.12 | Lijn op `entry − 0,12 × body` (Long) of `entry + 0,12 × body` (Short), met body = close − open van de breakout-candle (Gann box: close = 0, open = 1). Label "Flip 0.12 body". Zo ver moet de flip-candle tegen de break in komen; raken telt. | Controleert niet of de flip echt gebeurt. Was tot v1.13.0 0,12 × R. |
| Te ver zonder flip, in R (`flipMaxRR`) | 0.6 | Lijn op `entry + 0,6R` (Long) of `entry − 0,6R` (Short): komt de prijs daar zonder flip, dan is de flip gemist (tradeplan). | — |
| Kleur flip-hulplijnen (`flipColor`) | Paars | Kleur van beide lijnen en labels. | — |

Entry, R en body zijn die van de breakout-candle op de rekenfeed (bijv. FXCM), net als bij de TP-lijn. De entry is de close van de breakout-candle; in de praktijk stap je in zodra de prijs na de flip weer over het level gaat, zonder op de close van de flip-candle te wachten.

### Groep "Lotgrootte"

| Instelling | Default | Wat het doet | Wat het niet doet |
|---|---|---|---|
| Toon lotgrootte in TP-label (`showLots`) | Aan | Voegt bij een geldige trade een regel toe aan het TP-label: `Lot 0.27 · risico $98.76 (0.99%)`. Berekening: `account × risico% / (R × contractgrootte × koers-naar-USD + commissie per lot)`, naar beneden afgerond op 0.01 lot. | Verschijnt niet bij een "niet mogelijke" trade (daar is geen TP-label). Spread en swap zijn niet meegerekend. |
| Accountgrootte ($) (`accountSize`) | 10000 | Basis voor het risicobedrag. Accountvaluta is USD. | Leest je werkelijke accountsaldo niet uit; pas dit zelf aan. |
| Risico per trade (%) (`riskPct`) | 1.0 | Percentage van de accountgrootte dat je per trade riskeert. | — |
| Contractgrootte (`contractSize`) | 100 | Aantal eenheden per lot (XAUUSD = 100 oz). | Wordt niet automatisch per symbool bepaald; controleer dit bij een ander instrument. |
| Commissie per lot ($) (`commPerLot`) | 6 | Wordt per lot bij het risico opgeteld, zodat SL-verlies + commissie samen binnen je risico blijven. | — |

De lotgrootte wordt berekend met de R van de rekenfeed (standaard FXCM, zie groep "Rekenfeed"). Staat de rekenfeed uit, dan kan de lotgrootte op FXCM en FTMO_OANDA iets verschillen.

## 7. Veelgestelde vragen

**Waarom zie ik geen TP-lijn, terwijl er wel een LONG/SHORT-signaal is?**
Twee mogelijke oorzaken: (1) `showSL` of `showTradeCheck` staat uit — beide moeten aan staan; (2) de trade is "niet mogelijk" volgens de Range- of R-check — kijk dan naar de reden in het "Trade niet mogelijk"-blok (default rechtsboven).

**Waarom verschuift Resistance/Support ineens naar een ander niveau?**
Er zijn twee oorzaken. (1) Zodra de huidige lijn door een candle-body doorbroken wordt, is ze ongeldig geworden en berekent het script automatisch het eerstvolgende geldige (verder terugliggende) niveau. (2) Bij het zoeken naar het Target-niveau kan het script een geldig tussenliggend niveau vinden dat te dicht bij Resistance/Support ligt om Target te zijn (`minTargetDistance`) of al met een wick geraakt is. Is er een Target gevonden, dan verschuift Resistance/Support naar het laatste (verst terugliggende) zo'n tussenliggend niveau. Zie "T4G daytrade rules.md", Target Resistance punt 5 en 6. Dit kan er tegelijk voor zorgen dat de drempel voor een nieuw signaal (`Resistance/Support ± breakPct %`) verschuift — het script voorkomt hierbij expliciet dat zo'n verschuiving een tweede, ongewenst signaal in dezelfde richting veroorzaakt zolang het vorige signaalvenster nog loopt. Uitzondering (vanaf 1.15.0): was het vorige signaal "Trade niet mogelijk" en breekt de koers daarna een verder liggend niveau, dan telt dat wel als nieuw signaal (doorschuiven).

**Waarom loopt de SL/TP-lijn niet even ver door als de Resistance/Support-lijn?**
Dat is bewust: `lineLen` bepaalt alleen de lengte van SL/TP/break-lijnen. Resistance/Support/Target lopen altijd onbeperkt door naar rechts.

**Ik zie het rode waarschuwingslabel "alleen 30m en 15m worden ondersteund" — wat nu?**
Schakel de chart naar het 30m- of 15m-timeframe; op elk ander timeframe tekent het script bewust niets.

**Moet ik zelf nog iets instellen voor de alerts?**
Ja — de indicator roept `alert()` aan, maar je moet in TradingView zelf nog een alert aanmaken op deze indicator (Conditie: "Trade Lijnen (SL/S/R)") om een notificatie te ontvangen.

**Waarom geeft mijn 15m-chart een ander signaal dan mijn 30m-chart (of een andere broker)?**
Mogelijke oorzaken: (1) de rekenfeed staat op de ene chart aan en op de andere uit, of de feeds verschillen (FXCM vs FTMO_OANDA); (2) een verschillende `slSignalWindow`; (3) timing: een breakout op de 2e 15m-candle verschijnt op beide charts pas bij de 30m-close; tot v1.15.1 verscheen ook het vroege 15m-signaal op de 30m-chart pas bij de 30m-close. Vergelijk daarom ook de instellingen van beide charts.

**Er kwam "Trade niet mogelijk" en daarna toch een nieuw signaal in dezelfde richting. Klopt dat?**
Ja, sinds v1.15.0 (doorschuiven). Was de trade niet mogelijk, dan blokkeert het signaalvenster niet: breekt de koers daarna een verder liggend niveau (hogere Resistance bij Long, lagere Support bij Short), dan is dat een nieuw signaal met een eigen Range-check. Na een mogelijke trade blijft de blokkade binnen het venster wel gelden.
