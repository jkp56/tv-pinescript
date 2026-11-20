# Handleiding – sr_levels.py

`sr_levels.py` berekent Support, Resistance en de twee Target-lijnen op dezelfde manier als `trade_lines.pine` en `trade_lines_nasdaq.pine` (versie 1.23.0). Vindt het op 30m geen Target, dan zoekt het net als Pine verder op 1h, 4h en Daily, mits je die candles meegeeft (zie §5a). Het script berekent geen signalen, SL, TP of lotgrootte.

## 1. Wat moet er draaien?

| Onderdeel | Nodig? | Toelichting |
|---|---|---|
| Python 3 | Ja | Getest met Python 3.14, die al op deze pc staat. Controleer met `python --version`. |
| Extra Python-pakketten | Nee | Het script gebruikt alleen de standaardbibliotheek. Je hoeft niets te installeren. |
| Claude Code met de TradingView-koppeling | Ja, om candles op te halen | Het script kan TradingView niet zelf benaderen. Claude haalt de candles op via de TradingView MCP en bewaart ze in een JSON-bestand. |
| TradingView-account | Ja | De koppeling gebruikt jouw account en data-abonnement. |
| TradingView-app of geopende chart | Nee | De candles komen rechtstreeks van de server. |
| Achtergrondproces of server | Nee | Het script rekent één keer en stopt. Voor nieuwe niveaus haal je nieuwe candles op en start je het opnieuw. |

## 2. Snel aan de slag

De makkelijkste manier is Claude Code in deze map te vragen:

> Haal 500 candles van 30m op voor FTMO_OANDA:US100.CASH, bewaar ze als nasdaq.json en draai sr_levels.py.

Voor goud:

> Haal 500 candles van 30m op voor FX:XAUUSD, bewaar ze als xauusd.json en draai sr_levels.py.

Wil je ook de Target-fallback op 1h, 4h en Daily (nodig als een Target op `FALLBACK` staat):

> Haal voor FX:XAUUSD ook 1h-, 4h- en 1D-candles op met format="columns" (1h: 8000, 4h: 3000, 1D: 1000), bewaar ze als xauusd_1h.json, xauusd_4h.json en xauusd_1d.json en draai sr_levels.py met --h1, --h4 en --d1.

Heb je het JSON-bestand al, dan start je het script zelf in PowerShell vanuit deze map:

```powershell
python sr_levels.py nasdaq.json
```

## 3. Welke data gebruik je?

| Instrument | Symbool | Mintick |
|---|---|---|
| Nasdaq | `FTMO_OANDA:US100.CASH` | 0.01 |
| XAUUSD | `FX:XAUUSD` (FXCM) | 0.01 |

Het JSON-bestand is de ongewijzigde uitvoer van de MCP-tool `get_ohlcv`:

```text
get_ohlcv(symbol="FTMO_OANDA:US100.CASH", interval="30m", count=500, format="columns")
```

- **Interval:** alleen 30m-candles worden geaccepteerd.
- **Aantal:** vraag minstens 500 candles op. Het script scant net als Pine 450 gesloten candles terug.
- **Nasdaq:** `FX:NAS100` wordt geweigerd, omdat de Nasdaq niet op FXCM wordt berekend.
- **1h, 4h en Daily (optioneel):** zelfde symbool als de 30m-candles, bij voorkeur met `format="columns"`. Hoe verder terug, hoe beter: Pine zoekt over alle historie die TradingView laadt. Eén aanroep geeft maximaal 8000 candles in kolomvorm (1h ≈ 13 maanden, 4h ≈ 6 jaar). Wil je verder terug, haal dan meer pagina's op met `date_to` en voeg ze samen; dubbele candles worden overgeslagen.

## 4. De uitvoer lezen

```text
FTMO_OANDA:US100.CASH, laatste gesloten 30m-candle: 18-11-2026 12:00

Target Resistance    27368.23   Range    40.40   pivot 21 candles terug (18-11-2026 01:30)
Resistance           27327.83   Range   266.50   pivot 3 candles terug (18-11-2026 10:30)
Support              27061.33   Range   266.50   pivot 19 candles terug (18-11-2026 02:30)
Target Support       26804.83   Range   256.50   pivot 29 candles terug (17-11-2026 20:30)
```

| Onderdeel | Betekenis |
|---|---|
| Laatste gesloten 30m-candle | De candle waarop de niveaus zijn berekend. Een lopende candle telt niet mee. De tijd is de lokale tijd van je pc. |
| Range bij Resistance en Support | Afstand tussen Resistance en Support, in punten. |
| Range bij Target Resistance | Afstand van Resistance tot Target Resistance, in punten. |
| Range bij Target Support | Afstand van Support tot Target Support, in punten. |
| Pivot | Aantal candles terug en het tijdstip van de pivot-candle. |
| `FALLBACK` | Er is geen geldig patroon gevonden. Support en Resistance worden dan de laagste low en hoogste high van de scanrange. Een Target komt dan op een vaste afstand te liggen, als ook 1h, 4h en Daily niets opleveren of niet zijn meegegeven. |
| `1h pivot`, `4h pivot`, `D pivot` | Het Target is gevonden op een hoger timeframe (zie §5a), met de tijd van de pivot-candle op dat timeframe. |

## 5. Opties

| Optie | Wat het doet | Voorbeeld |
|---|---|---|
| `--history N` | Toont de niveaus van de laatste N gesloten candles. Met 500 opgehaalde candles kan dat tot ongeveer 50. | `python sr_levels.py nasdaq.json --history 10` |
| `--json` | Geeft de uitvoer als JSON. `bar_time` en `pivot_time` staan in Unix-seconden (UTC). | `python sr_levels.py nasdaq.json --json` |
| `--now` | Rekent alsof het dit moment is (Unix-seconden of ISO-datum). Gebruik dit bij een ouder bestand, met het moment waarop de candles zijn opgehaald. | `python sr_levels.py nasdaq.json --now 2026-11-18T12:35:00+01:00` |
| `--profile` | Kiest handmatig `nasdaq` of `xauusd`. Standaard volgt het profiel uit het symbool. | `python sr_levels.py data.json --profile nasdaq --tick 0.01` |
| `--symbol` | Geeft het symbool op als dat niet in het bestand staat. | `python sr_levels.py data.json --symbol FTMO_OANDA:US100.CASH` |
| `--tick` | Mintick van de feed. Verplicht bij een andere Nasdaq-feed dan FTMO_OANDA. | `python sr_levels.py data.json --tick 0.1` |
| `-` als bestandsnaam | Leest de JSON uit de invoer van een ander commando. | `Get-Content nasdaq.json \| python sr_levels.py -` |
| `--h1`, `--h4`, `--d1` | Bestanden met 1h-, 4h- en Daily-candles voor de Target-fallback (§5a). Je mag er ook één of twee meegeven. | `python sr_levels.py xauusd.json --h1 xauusd_1h.json --d1 xauusd_1d.json` |
| `--no-htf` | Geen Target-fallback, ook niet als de bestanden zijn opgegeven (zoals de Pine-instelling uit). | `python sr_levels.py xauusd.json --h1 xauusd_1h.json --no-htf` |

## 5a. Target-fallback op 1h, 4h en Daily

Vindt het script binnen de 450 candles van 30m geen geldig Target, dan zoekt het, net als Pine sinds 1.23.0, achtereenvolgens in de 1h-, 4h- en Daily-candles die je hebt meegegeven:

- Dezelfde regels als op 30m: overgang op body-niveau (na een sessie-gap de open van de reversal-candle), level ongeldig zodra een latere body erdoorheen sluit, wick niet geraakt (behalve de respecterende candle direct na de reversal-candle) en minimaal de minimale Target-afstand voorbij Resistance/Support.
- Alleen gesloten candles van dat timeframe tellen mee, en een level dat sinds het begin van de lopende candle van dat timeframe door een 30m-wick is geraakt, valt af.
- Het dichtstbijzijnde geldige level wordt het Target. Pas als ook Daily niets oplevert, geldt de vaste fallback-afstand.

Op stderr meldt het script vanaf welke datum de bestanden lopen, bijvoorbeeld `Target-fallback met: 1h vanaf 03-10-2025 00:00, D vanaf 18-08-2025 00:00`. Ligt het level dat Pine vindt verder terug dan je bestand, dan vindt het script het niet en kan het uitkomen op een verder liggend level of op een hoger timeframe. Haal dan meer historie op.

**Controle:** XAUUSD (FX:XAUUSD), candle van 20-11-2026 05:30 met alleen Daily: Target Support 3365.50 (D pivot 25-08-2025), Target Resistance 3877.19, gelijk aan Pine. Met 1h-historie tot september 2025 geeft Pine 3481.99 (1h pivot 02-09-2025 14:00).

**Let op bij oudere bestanden:** de laatste candle in het bestand was tijdens het ophalen vaak nog niet gesloten. Draai je het script later zonder `--now`, dan telt die onvolledige candle als gesloten en kloppen de niveaus niet. Haal bij twijfel nieuwe candles op.

## 6. Instellingen

De instellingen staan vast in het script en zijn gelijk aan de standaardwaarden van de Pine-scripts:

| Instelling | XAUUSD | Nasdaq |
|---|---|---|
| Fallback afstand target lijnen (ticks) | 1000 | 700 |
| Target zoeken op 1h, 4h en Daily | Aan (als de bestanden zijn meegegeven) | Aan (als de bestanden zijn meegegeven) |
| Minimale afstand Target t.o.v. Resistance/Support (ticks) | 300 | 2100 |
| Max bars terugzoeken | 450 | 450 |
| Reversal-candle uitsluiten van eigen invalidatie | Aan | Aan |
| Body-tolerantie (candle na de overgang en latere candles) | Uit | Uit |
| Overgang over dagsluiting/weekend: level = open van de reversal-candle | Aan | Aan |

Het script leest je TradingView-instellingen niet uit. Wijzig je deze waarden op je chart, dan moet je ze ook aanpassen in `PROFILES` en `Settings` in `sr_levels.py`, anders wijken de niveaus af.

## 7. Hoe betrouwbaar is de uitkomst?

- **Nasdaq (FTMO_OANDA):** op 110 gesloten candles waren alle 440 waarden gelijk aan een Pine-kopie van de S/R- en targetfuncties.
- **XAUUSD (FXCM):** op dezelfde candles als Pine waren alle 236 vergeleken waarden gelijk. De candles van `get_ohlcv` wijken op deze feed soms iets af van wat Pine ziet (19 van de 129 vergeleken candles). Daardoor verschilden 3 van de 236 waarden, dus een klein verschil met je chart is mogelijk.

## 8. Foutmeldingen

| Melding | Oorzaak en oplossing |
|---|---|
| `De invoer moet uit 30m-candles bestaan` | Het bestand bevat een ander interval. Haal de candles op met `interval="30m"`. |
| `Het 1h-bestand bevat geen 1h-candles` (of 4h/D) | Het bestand bij `--h1`, `--h4` of `--d1` heeft een ander interval. Haal het op met `interval="1h"`, `"4h"` of `"1D"`. |
| `Het 1h-bestand is van …, de 30m-candles van …` | De bestanden horen bij verschillende symbolen of feeds. Gebruik voor alles hetzelfde symbool (XAUUSD: `FX:XAUUSD`). |
| `FX:NAS100 is de FXCM-feed` | Gebruik `FTMO_OANDA:US100.CASH`. |
| `Geef bij een andere Nasdaq-feed dan FTMO_OANDA de mintick op` | Voeg `--tick` toe met de mintick van die feed. |
| `Geen profiel bekend voor ...` | Het symbool is niet herkend. Voeg `--profile xauusd` of `--profile nasdaq` toe. |
| `Geen candles gevonden` | Het bestand is geen `get_ohlcv`-uitvoer. Haal de candles opnieuw op. |
| `Te weinig candles in de invoer` of `Te weinig gesloten candles voor --history` | Haal meer candles op of kies een kleinere N. |
| `Let op: ... gesloten candles beschikbaar` | Dit is een waarschuwing: de scanrange is niet compleet. Haal meer candles op, zeker als een niveau op `FALLBACK` staat. |
| `No such file or directory` | Het bestand staat niet in deze map. Controleer de naam en het pad. |
