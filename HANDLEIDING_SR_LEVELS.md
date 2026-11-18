# Handleiding – sr_levels.py

`sr_levels.py` berekent Support, Resistance en de twee Target-lijnen op dezelfde manier als `trade_lines.pine` en `trade_lines_nasdaq.pine` (versie 1.22.0). Het script berekent geen signalen, SL, TP of lotgrootte.

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
| `FALLBACK` | Er is geen geldig patroon gevonden. Support en Resistance worden dan de laagste low en hoogste high van de scanrange. Een Target komt dan op een vaste afstand te liggen. |

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

**Let op bij oudere bestanden:** de laatste candle in het bestand was tijdens het ophalen vaak nog niet gesloten. Draai je het script later zonder `--now`, dan telt die onvolledige candle als gesloten en kloppen de niveaus niet. Haal bij twijfel nieuwe candles op.

## 6. Instellingen

De instellingen staan vast in het script en zijn gelijk aan de standaardwaarden van de Pine-scripts:

| Instelling | XAUUSD | Nasdaq |
|---|---|---|
| Fallback afstand target lijnen (ticks) | 100 | 700 |
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
| `FX:NAS100 is de FXCM-feed` | Gebruik `FTMO_OANDA:US100.CASH`. |
| `Geef bij een andere Nasdaq-feed dan FTMO_OANDA de mintick op` | Voeg `--tick` toe met de mintick van die feed. |
| `Geen profiel bekend voor ...` | Het symbool is niet herkend. Voeg `--profile xauusd` of `--profile nasdaq` toe. |
| `Geen candles gevonden` | Het bestand is geen `get_ohlcv`-uitvoer. Haal de candles opnieuw op. |
| `Te weinig candles in de invoer` of `Te weinig gesloten candles voor --history` | Haal meer candles op of kies een kleinere N. |
| `Let op: ... gesloten candles beschikbaar` | Dit is een waarschuwing: de scanrange is niet compleet. Haal meer candles op, zeker als een niveau op `FALLBACK` staat. |
| `No such file or directory` | Het bestand staat niet in deze map. Controleer de naam en het pad. |
