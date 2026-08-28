# Changelog

Alle noemenswaardige wijzigingen aan `trade_lines.pine` worden hier bijgehouden.
Versienummering volgt [Semantic Versioning](https://semver.org/lang/nl/) (MAJOR.MINOR.PATCH).

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
