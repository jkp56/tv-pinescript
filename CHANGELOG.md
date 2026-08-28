# Changelog

Alle noemenswaardige wijzigingen aan `trade_lines.pine` worden hier bijgehouden.
Versienummering volgt [Semantic Versioning](https://semver.org/lang/nl/) (MAJOR.MINOR.PATCH).

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
