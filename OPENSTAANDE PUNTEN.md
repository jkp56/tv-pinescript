# Openstaande punten – Trade Lijnen

Regels uit het tradeplan die nog niet (of maar voorlopig) in `trade_lines.pine` (v1.10.0) en `trade_lines_strategie.pine` (v1.4.0) zitten, plus de vragen die eerst beantwoord moeten worden. Bijgewerkt: 2026-11-06.

Vaste uitgangspunten (bevestigd):

- Support/Resistance en de bijbehorende Targets worden bepaald op de **30m**.
- Een geldige trade kan ontstaan op de **30m of de 15m**, op de **eerste** candle die voorbij het level sluit.
- Bij het bepalen van een break spelen **wicks geen rol**: alleen de close telt.

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

## 4. Flip-regel in de strategie (voorlopig, v1.3.0)

**Tradeplan:** "Flip van minimaal 0,12R: de candle na de break tegengesteld aan de breakout candle. Trade overslaan als die candle 0,6R voorbij schiet." En: "Break even: op 0,8R schuif je de SL naar break even."

**Voorlopig gebouwd in `trade_lines_strategie.pine` v1.3.0:**

- Alleen de eerstvolgende 30m-candle wordt gecontroleerd. Die moet een tegengestelde body van ≥ 0,12R hebben.
- De terugval vanaf de break-close wordt gemeten op de wick. Dat is een aanname.
- Entry is een stop-order op de break-prijs, die vervalt na 4 × 30m. Ook een aanname.

**Nog open:**

- [ ] In realtime kan de flip kort of juist relatief lang duren. Is het altijd de eerstvolgende candle?
- [ ] Telt een 15m-variant mee ("de 2e 15m-candle na de 1e")?
- [ ] Wordt de terugval van 0,6R gemeten op de wick of op de close?
- [ ] Hoe lang blijft de stop-order staan?
- Wacht op een live voorbeeld en een check door de expert van de strategie.

---

## Vragen voor de expert (samengevat)

1. Wat is een "duidelijke break": alleen afstand voorbij het level, of ook een deel van de body? Klopt ongeveer 0,01–0,02% van de koers?
2. Hoe definieer je een doji, "SL op het level", "geen wick high/low" en "zwakke break-out"?
3. Is "rejection, close onder de 50%" de positie van de close binnen de range van de 15m-candle?
4. Geldt "op de 30m de 15m-candle tegen" alleen voor 30m-trades?
5. Flip: altijd de eerstvolgende candle? Telt de 15m? Meet je de terugval van 0,6R op de wick of op de close? Hoe lang blijft de entry-order staan?
