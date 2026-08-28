# T4G Daytrade Rules

Dit document beschrijft alle regels waaraan het Pine Script `trade_lines.pine` ("Trade Lijnen (SL/S/R)") moet voldoen.

## Stop Loss lijnen

1. Bij het sluiten van elke candle wordt gekeken naar de **wick** (high/low) van die laatst gesloten candle — hier tellen wicks wél mee.
2. **Long SL** = `low` van de laatst gesloten candle **min** `x` ticks (instelbaar, standaard 50).
3. **Short SL** = `high` van de laatst gesloten candle **plus** `x` ticks (standaard 50).
4. Er is altijd maar **één SL-lijn tegelijk zichtbaar**: **Long SL** wordt alleen getekend/bijgewerkt als de laatst gesloten candle **bullish** is, **Short SL** alleen als die **bearish** is. Zodra de ene lijn wordt getekend, wordt de andere (indien aanwezig) verwijderd.
5. **Doji-uitzondering**: bij een doji (close == open) wordt geen van beide lijnen bijgewerkt of verwijderd — ze blijven op hun laatst geldige niveau staan. Reden: bij een doji wordt normaal geen trade genomen, dus is er ook geen aanleiding om de SL te herzien.
6. De lijn loopt een instelbaar aantal bars (`lineLen`, standaard 20) naar rechts, niet oneindig door — in dit opzicht anders dan de S/R-lijnen, die wél doorlopen naar rechts.
7. Kleur: groen voor Long SL, rood voor Short SL. Getoond met een label met de exacte prijswaarde erbij.
8. Kan volledig aan/uit gezet worden via de instelling "Toon SL lijnen".

## Resistance

1. Kijk terug vanaf de **laatst gesloten candle** (de nu lopende/vormende candle telt niet mee als startpunt van de zoektocht).
2. Zoek de **meest recente overgang** van een **bullish candle** gevolgd door een **bearish candle**.
3. Het niveau = de **bovenkant van de body** van die bullish candle (`max(open, close)`).
4. **Geldigheidscheck (alleen body)**: dit niveau is alleen geldig als geen enkele candle daarna (inclusief de nu lopende candle) met zijn **body** dat niveau raakt of doorbreekt.
5. **Wicks spelen voor Resistance geen rol** — de lijn mag gewoon door wicks van candles heen lopen, dat maakt het niveau niet ongeldig.
6. Zo niet geldig (body-doorbraak) → zoek verder terug naar de vórige bullish→bearish overgang, en herhaal de check.

## Support

Spiegelbeeld van Resistance:

1. Meest recente overgang van een **bearish candle** gevolgd door een **bullish candle**.
2. Niveau = **onderkant van de body** van die bearish candle (`min(open, close)`).
3. Geldigheidscheck (alleen body): geldig alleen als geen enkele candle daarna (incl. lopende candle) met zijn **body** dat niveau raakt/doorbreekt.
4. **Wicks spelen voor Support geen rol** — de lijn mag door wicks heen lopen.

## Target Resistance

1. **Eigen, onafhankelijke zoektocht** naar een bullish→bearish overgang — exact dezelfde soort patroondetectie als Resistance (puur op **body**, wicks spelen geen rol bij het bepalen van de overgang).
2. Het niveau = de **bovenkant van de body** (`max(open, close)`) van die pivot-candle — geen wick.
3. **Extra eis**: het niveau moet minimaal een instelbaar aantal ticks (standaard 300, `minTargetDistance`) **boven Resistance** liggen. Is de afstand kleiner, dan is de kandidaat ongeldig en wordt er verder teruggezocht naar een eerdere overgang die wél aan deze eis voldoet.
4. **Geldigheidscheck**:
   - Geen enkele latere candle mag met zijn **body** het niveau raken/doorbreken (zelfde soort check als bij Resistance zelf, geen uitzonderingen).
   - **Gratieperiode voor wicks**: direct na de pivot-candle geldt een gratieperiode zolang de candles **bearish** blijven (de "respecterende" richting voor Resistance) — in die periode telt een wick die het niveau raakt niet mee. Zodra de **eerste bullish candle** (de "aanvallende" richting) verschijnt, eindigt de gratieperiode **blijvend**: vanaf dat moment maakt élke volgende wick (ongeacht of de candle bullish of bearish is) het niveau ongeldig als hij raakt/doorbreekt. Een aanvallende (bullish) candle telt zijn eigen wick overigens altijd mee, ook tíjdens de gratieperiode.
5. Zo niet geldig → verder terugzoeken naar de vorige bullish→bearish overgang die aan alle eisen voldoet.
6. Als er geen geldige overgang gevonden wordt binnen de scanrange, valt het terug op een vaste afstand in ticks vanaf Resistance.

## Target Support

Spiegelbeeld van Target Resistance:

1. Eigen, onafhankelijke zoektocht naar een bearish→bullish overgang, puur op body.
2. Niveau = **onderkant van de body** (`min(open, close)`) van die pivot-candle.
3. Extra eis: het niveau moet minimaal `minTargetDistance` ticks **onder Support** liggen.
4. Geldigheidscheck:
   - Geen enkele latere candle mag met zijn body het niveau raken/doorbreken.
   - Gratieperiode voor wicks: zolang de candles **bullish** blijven (respecterende richting voor Support) telt een wick-aanraking niet mee. Zodra de eerste **bearish** candle (aanvallende richting) verschijnt, eindigt de gratieperiode blijvend — vanaf dan telt elke wick daarna (ongeacht kleur) mee.
5. Fallback (vaste afstand in ticks) als er geen geldige overgang gevonden wordt.

## Tekenregels (alle 4 S/R-lijnen)

- Lijn begint **exact bij de overgang-candle** (niet doorgetrokken naar links).
- Loopt door naar **rechts** (door de huidige candle heen, de toekomst in).
- Lijndikte **2px**.
- Alles wordt **opnieuw berekend en getekend bij elke candle close** (niet pas bij elke tick).
- Geen handmatig verslepen nodig — volledig automatisch.

## LONG signaal

1. Wordt alleen getest bij een **candle close**, niet tijdens de vorming van een candle.
2. Triggert wanneer de **close** van de zojuist gesloten candle voor het eerst boven `Resistance + x ticks` uitkomt — dus alleen op het moment van de eerste doorbraak, niet elke volgende candle die er nog steeds boven sluit.
3. `x` = instelbaar aantal ticks (standaard 10).
4. Bij triggeren: groen label boven de candle met tekst "LONG signaal / Close > Resistance +x ticks", plus een alert.
5. Het vorige signaallabel (long of short) wordt eerst verwijderd, zodat alleen het laatste signaal zichtbaar blijft.

## SHORT signaal

Spiegelbeeld van het LONG signaal:

1. Alleen getest bij candle close.
2. Triggert wanneer de close voor het eerst onder `Support − x ticks` zakt.
3. Zelfde instelbare `x` (ticks) als bij het LONG signaal.
4. Bij triggeren: rood label onder de candle met tekst "SHORT signaal / Close < Support -x ticks", plus alert.
5. Vervangt eveneens het vorige signaallabel.
