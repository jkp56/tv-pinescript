# Handleiding – XAUUSD 10H Breakout (strategie)

Uitleg voor `xauusd_10h_strategie.pine`, versie **1.1.1**. Dit document beschrijft de regels van de strategie, hoe het script ze uitvoert, wat je op de chart ziet en wat elke instelling doet.

## 1. Wat doet dit script

Het script is een **TradingView-strategie** (geen indicator): het plaatst zelf orders in de Strategy Tester. Kort samengevat:

1. Om 08:59 NL-tijd ligt een **range** vast: de hoogste en laagste prijs van de afgelopen 10 uur.
2. De eerste 15m-candle die **boven de range-high of onder de range-low sluit** is de break.
3. Vanaf die breakout-candle wordt **terug in de tijd** gezocht naar de eerste tegengestelde candle: dat is de **zone**.
4. Op de zone komt een **limit-order** met vaste SL en TP.
5. Bij +1R gaat de SL naar +0,5R. Om 22:00 wordt alles gesloten.

Maximaal **één trade per dag**.

## 2. Vereisten voor gebruik

- **Alleen de 15m-chart.** Op elk ander timeframe doet het script niets en verschijnt een rood label "10H Breakout: alleen op de 15m-chart."
- Gemaakt voor **XAUUSD**. De positiegrootte gebruikt `syminfo.pointvalue` van het symbool, dus controleer bij een ander symbool of de lotgrootte klopt.
- Alle tijden zijn **NL-tijd** (`Europe/Amsterdam`, instelbaar). Zomer- en wintertijd worden automatisch verwerkt.

## 3. De regels stap voor stap

### Stap 1 – De 10H-range (23:00 t/m 08:59)

- De range bestaat uit de 15m-candles van **23:00 tot en met de 08:45-candle**, dus tot en met 08:59.
- De range loopt over middernacht: de candles van 23:00–23:45 horen bij de range van de **volgende** dag.
- Range-high = hoogste high, range-low = laagste low (inclusief wicks).
- Op maandag begint de range bij de eerste candle na de weekendsluiting.

### Stap 2 – De break (vanaf 09:00)

- Vanaf de 09:00-candle wacht het script op een 15m-candle die:
  - **boven de range-high sluit** → BUY, of
  - **onder de range-low sluit** → SELL.
- Een wick door de range telt niet, alleen de **close**.
- **Alleen de eerste break van de dag telt.** Daarna kijkt het script die dag niet meer naar nieuwe breaks, ook niet als er geen zone gevonden werd (zie stap 3).
- De laatste candle vóór 22:00 (de 21:45-candle) telt niet meer als break.

### Stap 3 – De zone: eerste tegengestelde candle terug in de tijd

Zodra de breakout-candle gesloten is, zoekt het script **terug in de tijd**, te beginnen bij de candle direct vóór de breakout-candle:

| Richting | Zone = eerste candle terug in de tijd die… |
|---|---|
| BUY | **bearish** is (close < open) |
| SELL | **bullish** is (close > open) |

- De breakout-candle zelf telt niet mee.
- Doji's (close = open) worden overgeslagen, net als candles zonder bereik (high = low).
- **Zonegrootte = high − low** van die candle, inclusief wicks.
- Er wordt maximaal *Max. candles terugzoeken naar zone* candles teruggekeken (standaard 40 = 10 uur). Het zoeken mag dus terug de range in lopen, en bij een late break ook nog verder.
- **Geen tegengestelde candle binnen die zoekdiepte = geen trade die dag.** Op de chart verschijnt dan een grijs label "Geen zone binnen X candles" bij de breakout-candle.

### Stap 4 – De entry (limit-order)

De order wordt **direct op de close van de breakout-candle** geplaatst, als limit-order:

| Instelling *Entry op zone* | BUY-entry | SELL-entry |
|---|---|---|
| **Zonerand** (standaard) | zone-high | zone-low |
| **Zone-midden** | (high + low) / 2 | (high + low) / 2 |

Bij *Zonerand* ligt de entry op de rand die prijs bij een retest als eerste raakt.

Omdat de zone vóór de break ligt, staat de entry meestal **onder de prijs (BUY) of erboven (SELL)**: de order wacht dan op een terugval naar de zone. Ligt de entry toch aan de verkeerde kant van de prijs (bijv. een BUY-entry boven de close van de breakout-candle), dan vult TradingView de order op de **open van de volgende candle**, tegen die prijs of beter.

### Stap 5 – SL en TP

- **1R = SL-multiplier × zonegrootte** (standaard 2,5 × zonegrootte).
- **SL** = entry − 1R (BUY) of entry + 1R (SELL).
- **TP** = entry + 4R (BUY) of entry − 4R (SELL), met de standaard *TP (R/R)* = 4.
- SL en TP worden berekend vanaf de **geplande entry**, niet vanaf een eventueel betere fill.

### Stap 6 – Trade-beheer

- **SL naar +0,5R:** raakt prijs (high bij BUY, low bij SELL) **+1R** vanaf de geplande entry, dan schuift de SL naar **entry + 0,5R** (BUY) of **entry − 0,5R** (SELL). Dit gebeurt één keer per trade.
- **22:00 – alles sluiten:** op de laatste candle vóór 22:00 annuleert het script een niet-gevulde order en sluit het een open trade. Die sluit-order vult op de open van de 22:00-candle (comment "22:00").
- **Vangnet:** buiten het venster 09:00–22:00 staan er nooit orders of posities open. Ontbreekt de candle vóór 22:00, dan sluit het script de positie alsnog bij de eerste candle buiten het venster (comment "Buiten venster").

### Positiegrootte

```
units = equity × risico% ÷ (1R × pointvalue)
```

Daarna wordt naar beneden afgerond op *Afronding positiegrootte (stap)*. Komt dat op 0 uit, dan wordt er geen order geplaatst.

## 4. Rekenvoorbeeld (BUY)

| | Waarde |
|---|---|
| Range-high / range-low | 2650,00 / 2630,00 |
| Break: 10:15-candle sluit op | 2652,40 → **BUY** |
| Terugzoeken: 10:00-candle | bullish → overslaan |
| Terugzoeken: 09:45-candle | **bearish**, high 2648,20, low 2645,80 → **zone** |
| Zonegrootte | 2648,20 − 2645,80 = 2,40 |
| Entry (Zonerand) | 2648,20 |
| 1R = 2,5 × 2,40 | 6,00 |
| SL | 2648,20 − 6,00 = **2642,20** |
| TP (4R) | 2648,20 + 24,00 = **2672,20** |
| SL-verplaatsing bij +1R | prijs raakt 2654,20 → SL naar **2651,20** (+0,5R) |
| Positiegrootte (equity 10.000, 1 %, pointvalue 1) | 100 ÷ 6,00 = 16,666 → **16,66 units** |

De BUY-limit op 2648,20 ligt onder de close van 2652,40. De order vult dus pas als prijs terugvalt naar de zone vóór 22:00. Gebeurt dat niet, dan wordt de order om 22:00 geannuleerd.

## 5. Wat zie je op de chart

### 5.1 Lijnen en vlakken

| Element | Kleur (default) | Betekenis |
|---|---|---|
| Range-lijnen | Grijs, doorlopend | Range-high en -low, van de eerste range-candle (23:00) tot 22:00. |
| Zone-rechthoek | Blauw, transparant | Van de zone-candle (de gevonden tegengestelde candle) tot 22:00, van zone-high tot zone-low. |
| Entry-lijn | Blauw, doorlopend | Limit-prijs; begint bij de breakout-candle. |
| SL-lijn | Rood, gestippeld | Oorspronkelijke stop loss. |
| TP-lijn | Groen, gestippeld | Take profit. |
| Verplaatste SL-lijn | Oranje, gestippeld | Nieuwe SL na het halen van +1R; begint bij de candle die +1R raakte. |

Alle tekeningen staan aan of uit met *Teken range, zone en trade-lijnen*. De orders zelf worden altijd geplaatst.

### 5.2 De teksten rechts (bij 22:00) en wat je ermee doet

De prijzen in de tabel zijn voorbeelden. Alle labels van een dag staan rechts, aan het eind van de lijnen (22:00). Liggen twee prijzen dicht bij elkaar (bijv. de entry vlak bij de 10H high), dan schuift het script het hogere label iets omhoog zodat de teksten niet over elkaar vallen. Een label staat dan niet precies op zijn lijn, maar de prijs in de tekst is altijd de echte prijs. De volgorde van onder naar boven blijft gelijk aan de volgorde van de prijzen. De afstand is instelbaar met *Min. afstand labels* (§6).

| Tekst | Wat het voorstelt | Wat je ermee doet |
|---|---|---|
| **10H high 4029.10** (grijs) | Hoogste prijs van de range 23:00–08:59. Verschijnt om 09:00. | Een 15m-**close** hierboven = BUY-break. Vanaf 09:00 in de gaten houden; een wick erdoor is nog geen break. |
| **10H low 4001.30** (grijs) | Laagste prijs van de range. Verschijnt om 09:00. | Een 15m-**close** hieronder = SELL-break. |
| **BUY limit 4028.80 · 5.46 units** (blauw) | Er was een break, de zone is gevonden en de strategie heeft een limit-order geplaatst. Prijs = entry (zone-high bij BUY, zone-low bij SELL); *units* = positiegrootte die de strategie in de backtest gebruikt. | Dit is het signaal om de order live te plaatsen: **limit-order op deze prijs**, met de SL en TP van de labels hieronder. De *units* zijn berekend op de equity van de Strategy Tester (standaard 10.000, 1 % risico), niet op je eigen account: bepaal je eigen lotgrootte zelf. |
| **SELL limit …** (blauw) | Idem, voor een SELL-break. | Idem: sell-limit op deze prijs. |
| **SL 4007.52** (rood) | Stop loss = entry ∓ 1R (1R = 2,5 × zonegrootte). | Als SL van je order instellen. |
| **TP 4113.90 (4R)** (groen) | Take profit = entry ± 4R. | Als TP van je order instellen. |
| **SL -> 0.5R 4039.44** (oranje) | Prijs heeft +1R vanaf de entry geraakt; de strategie heeft de SL verplaatst naar entry + 0,5R (BUY) of entry − 0,5R (SELL). | Je SL live naar deze prijs verplaatsen. De trade staat dan op minimaal +0,5R winst. |

**Geen blauw/rood/groen label na een break?** Dan is er die dag geen trade: geen zone gevonden (zie hieronder) of de positiegrootte kwam op 0 uit.

**Om 22:00:** staat de order nog open of loopt de trade nog, dan annuleert/sluit de strategie alles. Live doe je hetzelfde: niet-gevulde order verwijderen, open trade sluiten. Na 22:00 die dag niets nieuws meer.

### 5.3 Overige teksten

| Tekst | Waar | Wat het voorstelt | Wat je ermee doet |
|---|---|---|---|
| **Geen zone binnen 40 candles** (grijs label) | Bij de breakout-candle | Break gevonden, maar binnen de zoekdiepte geen tegengestelde candle. | Niets: geen trade die dag, ook niet bij een latere break. |
| **10H Breakout: alleen op de 15m-chart.** (rood label) | Laatste candle | Het script draait op een ander timeframe en doet niets. | Chart op 15m zetten. |
| **Long +5.4** / **Short -5.4** (pijl + tekst onder/boven een candle) | Candle waar de order gevuld werd | Marker van de Strategy Tester: de limit-order is **gevuld**, met de positiegrootte (+ = long, − = short). | Vanaf hier loopt de trade; let op de SL-verplaatsing bij +1R. |
| **Long exit** / **Short exit** (marker) | Candle van de exit | Trade gesloten op SL, verplaatste SL of TP. | Controleren of je live trade ook gesloten is. |
| **22:00** (marker) | 22:00-candle | Trade gesloten door de 22:00-regel. | Live trade ook sluiten. |
| **Buiten venster** (marker) | Eerste candle na 22:00 | Vangnet: positie gesloten omdat de candle vóór 22:00 ontbrak. | Zelfde als bij 22:00. |

## 6. Instellingen (Inputs-tabblad)

### Groep "Info"

| Instelling | Default | Wat het doet |
|---|---|---|
| Versie | 1.1.1 | Alleen ter informatie. |

### Groep "Tijd"

| Instelling | Default | Wat het doet |
|---|---|---|
| Tijdzone | Europe/Amsterdam | Tijdzone voor alle tijden hieronder. |
| Range sluit om (uur) | 9 | De range loopt tot dit uur (9 = t/m 08:59); vanaf dit uur wordt naar een break gezocht. |
| Range-lengte (uren) | 10 | Hoeveel uur vóór de sluittijd de range begint (10 → vanaf 23:00). |
| Alles sluiten om (uur) | 22 | Open trade sluiten en pending order annuleren. Na dit uur geen nieuwe setups. |

### Groep "Trade"

| Instelling | Default | Wat het doet |
|---|---|---|
| Entry op zone | Zonerand | *Zonerand*: BUY op zone-high, SELL op zone-low. *Zone-midden*: midden van de zone. |
| SL = x keer zonegrootte | 2,5 | Grootte van 1R als veelvoud van de zonegrootte. |
| TP (R/R) | 4,0 | TP-afstand in R. |
| SL verplaatsen zodra prijs (R) haalt | 1,0 | Bij deze winst (in R, vanaf de geplande entry) schuift de SL. |
| SL verplaatsen naar (R) | 0,5 | Nieuwe SL in R ten opzichte van de entry (0 = break-even, negatief mag). |
| Risico per trade (% van equity) | 1,0 | Risico per trade voor de positiegrootte. |
| Max. candles terugzoeken naar zone | 40 | Hoe ver vanaf de breakout-candle terug in de tijd naar de tegengestelde candle gezocht wordt. 40 = 10 uur. |
| Afronding positiegrootte (stap) | 0,01 | De positiegrootte wordt naar beneden afgerond op deze stap. |

### Groep "Weergave"

| Instelling | Default | Wat het doet |
|---|---|---|
| Teken range, zone en trade-lijnen | aan | Alle tekeningen aan/uit. Heeft geen invloed op de orders. |
| Kleur range-lijnen | Grijs | Kleur van de range-lijnen en -labels. |
| Kleur zone | Blauw (80 % transparant) | Kleur van de zone-rechthoek. |
| Min. afstand labels (% van dag-span) | 5,0 | Labels rechts die dichter bij elkaar liggen dan dit percentage van de afstand tussen het hoogste en laagste label van die dag, worden uit elkaar geschoven. Overlappen teksten nog: verhogen. Staan ze te ver van hun lijn: verlagen. 0 = uit. |

## 7. Goed om te weten

- **Eén kans per dag:** de eerste break bepaalt de dag. Wordt er geen zone gevonden, komt de order niet tot een fill vóór 22:00, of is de positiegrootte 0, dan is er die dag geen trade.
- **Backtest-fills:** TradingView vult limit-orders in de backtest op basis van OHLC-data. Raakt een candle zowel de entry als de SL of TP, dan bepaalt de Strategy Tester de volgorde aan de hand van de candle-vorm. Dat kan afwijken van wat er live binnen die candle gebeurde.
- **SL-verplaatsing:** de +1R-check gebeurt op gesloten candles. De nieuwe SL geldt dus vanaf de candle ná de candle die +1R raakte.
