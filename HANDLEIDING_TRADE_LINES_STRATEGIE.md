# Handleiding – Trade Lijnen strategie (backtest)

Script: `trade_lines_strategie.pine` (versie 1.3.0)
Gebaseerd op: `trade_lines.pine` (indicator, versie 1.9.38)

## 1. Wat doet dit script

Een strategie-versie van de indicator *Trade Lijnen (SL/S/R)*. De signalen worden precies zo berekend als in de indicator. Waar de indicator alleen lijnen tekent, opent de strategie echte posities. Je kunt de regels dus backtesten in de Strategy Tester van TradingView.

**De rekenlogica is ongewijzigd.** Deze onderdelen zijn letterlijk overgenomen uit de indicator:

- Resistance en Support, Target Resistance en Target Support (inclusief het verschuiven van levels)
- breakout-signaal (close voorbij S/R + X ticks) en het signaalvenster
- SL-formule, TP (R/R) en de Trade Mogelijkheid-check (Range, max. R, rejection candle)
- rekenfeed (FXCM) en het 30m-rekentimeframe

Zie `T4G daytrade rules.md` en `HANDLEIDING.md` voor de detectielogica zelf.

## 2. Vereisten

- Chart op **30m** of **15m**. Andere timeframes geven een waarschuwing en er wordt niet gehandeld.
- Op 15m valt de entry op de close van de tweede 15m-candle van de signaal-candle. Dat is dezelfde prijs als de 30m-close.

## 3. Wanneer wordt een trade geopend

Er wordt alleen een trade geopend als **al deze voorwaarden** gelden:

1. Er is een nieuw breakout-signaal (Long of Short).
2. De trade is **mogelijk**. Dat is dezelfde voorwaarde waarbij de indicator een TP-lijn tekent:
   - de Range tot het Target bij de break is minimaal *Minimaal benodigde R/R-ruimte* × R
   - R is niet groter dan *Maximaal toegestane R (ticks)*
   - er is geen rejection candle (alleen als die check aan staat)
3. De richting staat aan (*Richting*).
4. Het signaal valt binnen de backtest-periode.
5. Er is nog geen positie open (zolang *Nieuwe signalen negeren zolang er een positie open is* aan staat).
6. Het is niet de sluit-candle van het vaste sluituur (zolang die optie aan staat).
7. **Flip** (tradeplan, standaard aan): de eerste 30m-candle **na** de breakout-candle is aan **beide** eisen voldaan:
   - hij is tegengesteld aan de breakout-candle (bearish bij Long, bullish bij Short), met een body (open − close) van minimaal **0,12R**
   - hij valt niet meer dan **0,6R** terug vanaf de close van de breakout-candle (standaard gemeten op de wick: low bij Long, high bij Short)

   R is hier de R van de breakout-candle. Haalt de flip-candle één van beide niet, dan geldt de trade als niet mogelijk.

**Niet-mogelijke trades worden volledig genegeerd:** geen trade, geen lijnen, geen label. In de berekening tellen ze nog wel mee: net als in de indicator start zo'n signaal een signaalvenster. Een nieuwe break in dezelfde richting binnen dat venster telt dan niet als nieuw signaal.

## 4. De trade

| Onderdeel | Regel |
|---|---|
| **Entry met flip** (standaard) | Na een geldige flip komt er een **stop-order op de break-prijs** (close van de breakout-candle). Hij wordt gevuld zodra de prijs daar terugkomt. R, SL en TP blijven precies die van de breakout-candle. De order vervalt na *x* 30m-candles (standaard 4). Hij wordt ook geannuleerd als de prijs eerst de SL raakt, op het sluituur of bij een nieuw signaal. Optioneel: market op de close van de flip-candle (SL en TP op dezelfde prijzen, positiegrootte op de werkelijke afstand tot de SL). |
| **Entry zonder flip** | Market op de close van de signaal-candle (`process_orders_on_close`) |
| **SL** | Long: low van de signaal-candle − *SL: aantal ticks van wick*. Short: high + ticks. |
| **R** | Afstand entry → SL (berekend op de close van de rekenfeed) |
| **TP** | Entry ± *TP: Risk/Reward ratio* × R |
| **Trailing SL** (optioneel) | Binnen het signaalvenster werkt elke bullish (Long) resp. bearish (Short) candle de SL bij. Dit gebeurt **alleen als de SL daardoor dichter bij de prijs komt.** |
| **Break-even** (tradeplan, standaard aan) | Raakt de high (Long) of de low (Short) **+0,8R** vanaf de fill-prijs, dan gaat de SL naar de **entry** (fill-prijs). Eenmalig per trade, pas vanaf de candle na de entry-candle. De SL wordt verplaatst op de close van de candle die de trigger raakt. Een strakkere trailing SL blijft staan. |
| **Sluiten** | Op SL of TP. Optioneel ook na x 30m-candles, op een vast uur of aan het einde van de backtest-periode. |

## 5. Positiegrootte

Zelfde formule als de lotgrootte in de indicator:

```
units = (saldo × risico%) / (R × puntwaarde × koers-naar-USD + commissie per unit)
```

Het resultaat wordt naar beneden afgerond op *Afronding positiegrootte*, met minimaal 1 stap. Bij XAUUSD is 1 unit 1 oz, 100 units 1 lot en stap 1 dus 0,01 lot.

| Modus | Saldo in de formule |
|---|---|
| Risico % van equity (standaard) | Equity van de Strategy Tester. Posities groeien mee na winst en krimpen na verlies. |
| Risico % van vast saldo | *Vast saldo ($)*. Rekent zoals de indicator. |
| Vaste lotgrootte | Altijd *Vaste lotgrootte* × *Contractgrootte* |

## 6. Wezenlijke verschillen met de indicator

1. **Een trade loopt door tot SL of TP.** De indicator kent geen afloop: lijnen verdwijnen na het signaalvenster. In de strategie kan een positie uren tot dagen open blijven, ook over de nacht en het weekend. Wil je dat beperken, gebruik dan *Sluiten na x 30m-candles* of *Alles sluiten op vast uur*.
2. **Signalen tijdens een open positie worden overgeslagen** (standaard). Zet je dat uit, dan keert een tegengesteld signaal de positie om. Een signaal in dezelfde richting doet niets, want pyramiding staat op 0.
3. **De entry vult op de chart-feed, SL en TP komen van de rekenfeed.** Staat *Berekeningen op andere feed dan de chart* aan, dan komen signaal, SL en TP van FXCM. De fill komt dan op de chart-prijs, bijvoorbeeld FTMO_OANDA. De werkelijke R en R/R in de backtest wijken daardoor iets af van wat de indicator toont. Dat is realistisch voor hoe je handelt. Voor een test op één feed zet je de optie uit.
4. **De trailing SL beweegt alleen in je voordeel.** In de indicator kan hij ook verder van de prijs komen.
5. **De positiegrootte groeit mee met de equity** (standaard), in plaats van een vaste accountgrootte.
6. **Flip en break-even uit het tradeplan.** De indicator kent geen flip: hij toont de trade direct bij de break. De strategie wacht standaard op de flip-candle en zet dan pas een stop-order op de break-prijs. Een deel van de trades die de indicator toont, valt daardoor af of wordt nooit gevuld.
   **Break-even:** De indicator heeft geen break-even. De strategie verplaatst de SL naar de entry zodra de prijs +0,8R haalt. Een trade die daarna terugvalt, sluit op ongeveer 0R. Je verliest dan alleen de commissie (en in de praktijk de spread).
7. **Wat er op de chart staat is anders:**
   - lijnen per trade blijven in de historie staan
   - de "doorbroken"-lijn, de "Target bij break"-lijn, het "Trade niet mogelijk"-blok, de Freeze-optie en de alerts zijn weggelaten

## 7. Instellingen die bij de strategie horen

De groepen *Rekenfeed*, *Stop Loss*, *Support / Resistance*, *Signaal instellingen* en *Trade Mogelijkheid* werken precies zoals in de indicator.

### Groep "Flip"

| Instelling | Standaard | Betekenis |
|---|---|---|
| Flip vereist | aan | Entry-criterium uit het tradeplan |
| Flip: minimale body (R) | 0,12 | Minimale tegengestelde body van de flip-candle |
| Overslaan als de flip-candle meer dan x R terugvalt | 0,6 | Gemeten vanaf de close van de breakout-candle |
| Terugval meten op | Wick | Wick = low (Long) / high (Short). Close = close van de flip-candle. |
| Entry na de flip | Op break-prijs (stop-order) | Of: market op de close van de flip-candle |
| Stop-order vervalt na x 30m-candles | 4 | Gerekend vanaf de close van de flip-candle |

**Let op:** de flip en de *Rejection candle*-check (groep Trade Mogelijkheid) zijn tegengestelde regels. De rejection-check keurt een tegengestelde tweede 15m-candle **binnen** de breakout-candle af. De flip vraagt juist om een tegengestelde candle **na** de breakout-candle. De rejection-check staat standaard uit.

### Groep "Break-even"

| Instelling | Standaard | Betekenis |
|---|---|---|
| Break-even aan | aan | Regel uit het tradeplan |
| SL verplaatsen zodra prijs (R) haalt | 0,8 | Winst in R vanaf de fill-prijs waarbij de SL schuift |
| SL verplaatsen naar (R t.o.v. entry) | 0,0 | 0 = break-even. Positief zet winst vast, negatief mag ook. |

Op de chart verschijnt bij het verplaatsen een oranje lijn "SL -> 0R" (als *Toon entry/SL/TP-lijnen per trade* aan staat).

### Groep "Strategie"

| Instelling | Standaard | Betekenis |
|---|---|---|
| Richting | Long en Short | Of alleen Long / alleen Short |
| Nieuwe signalen negeren zolang er een positie open is | aan | Uit: een tegengesteld signaal keert de positie om |
| Sluiten na x 30m-candles | 0 (uit) | Telt vanaf de signaal-candle |
| Alles sluiten op vast uur / Sluituur / Tijdzone | uit / 22 / Europe/Amsterdam | Sluit op de close van de laatste candle vóór het sluituur |
| Backtest vanaf / tot | 2024-01-01 / 2099-12-31 | Alleen signalen binnen deze periode worden getraded |

### Groep "Positiegrootte"

| Instelling | Standaard |
|---|---|
| Positiegrootte | Risico % van equity |
| Risico per trade (%) | 1,0 |
| Vast saldo ($) | 10000 |
| Vaste lotgrootte (lots) | 0,10 |
| Contractgrootte (units per lot) | 100 (XAUUSD) |
| Commissie per lot round-trip ($, voor de sizing) | 6 |
| Afronding positiegrootte (units) | 1 (= 0,01 lot) |

### Groep "Weergave"

| Instelling | Standaard | Betekenis |
|---|---|---|
| Toon actuele Resistance/Support/Target-lijnen | aan | Alleen de huidige stand, met naamlabels |
| Toon entry/SL/TP-lijnen per trade | aan | Gestippelde lijnen vanaf de signaal-candle |
| Toon labels bij entry/SL/TP-lijnen | **uit** | Prijs, lotgrootte en R |
| Toon label bij geldig signaal dat niet getraded is | **uit** | Oranje label met reden: positie al open, richting uit of sluituur |
| Lengte trade-lijnen | 5 | Aantal 30m-candles |

## 8. Properties-tabblad (Strategy Tester)

Deze waarden staan in de code als standaard, maar je past ze aan in het Properties-tabblad:

| Eigenschap | Standaard | Opmerking |
|---|---|---|
| Initial capital | 10000 USD | |
| Commission | $0,03 per contract (= per unit, per kant) | $6 per lot round-trip. Betaal je $6 per kant, zet dan 0,06. |
| Margin long/short | 5% (1:20) | Bij 100% weigert TradingView gold-orders door te weinig margin |
| Pyramiding | 0 | Maximaal 1 positie tegelijk |
| Orders verwerken op close | aan | Entry op de close van de signaal-candle |

## 9. Goed om te weten

- **Een fill tegen de close is optimistisch.** In de praktijk zie je het signaal pas na de close en vul je een fractie later, met spread. Houd daar rekening mee bij het lezen van de resultaten.
- **Raken SL en TP dezelfde candle,** dan bepaalt de standaard bar-simulatie van TradingView welke eerst gaat. Zet *Bar Magnifier* aan voor een nauwkeurigere volgorde.
- **De historie is beperkt.** De S/R-berekening kijkt maximaal 450 30m-candles terug. De eerste candles van de chart geven daarom nog geen betrouwbare levels.
