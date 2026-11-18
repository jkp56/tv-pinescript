#!/usr/bin/env python3
"""Support, Resistance en Targets berekenen zoals trade_lines.pine (v1.22.0).

Invoer is de JSON-uitvoer van de TradingView MCP-tool get_ohlcv, op 30m-candles.
Gebruik voor XAUUSD de rekenfeed FXCM (FX:XAUUSD) en voor de Nasdaq FTMO_OANDA
(FTMO_OANDA:US100.CASH). Vraag minstens 500 candles op, zodat de volledige
scanrange van 450 gesloten candles beschikbaar is:

    get_ohlcv(symbol="FX:XAUUSD", interval="30m", count=500, format="columns")
    get_ohlcv(symbol="FTMO_OANDA:US100.CASH", interval="30m", count=500, format="columns")

Gebruik:

    python sr_levels.py bars.json
    python sr_levels.py bars.json --history 10
    python sr_levels.py bars.json --json
    type bars.json | python sr_levels.py -

Gebruik je voor de Nasdaq een andere feed dan FTMO_OANDA, geef dan de mintick van
die feed op met --tick, want de afstanden in het profiel staan in ticks.

Alleen de Python-standaardbibliotheek is nodig.
"""

from __future__ import annotations

import argparse
import json
import sys
import time as time_module
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Iterator, NamedTuple, Optional

BAR_SECONDS = 1800


class Bar(NamedTuple):
    t: int
    o: float
    h: float
    l: float
    c: float
    valid: bool


@dataclass(frozen=True)
class Settings:
    """Standaardwaarden van de groep Support / Resistance in het Pine-script."""

    auto_target_ticks: int
    min_target_distance: int
    body_tol_ticks: int
    later_tol_ticks: int
    tick: float = 0.01
    max_scan: int = 450
    exclude_reversal: bool = True
    body_tol_enabled: bool = False
    later_tol_enabled: bool = False
    session_gap_open: bool = True


PROFILES = {
    "xauusd": Settings(auto_target_ticks=100, min_target_distance=300, body_tol_ticks=50, later_tol_ticks=50),
    "nasdaq": Settings(auto_target_ticks=700, min_target_distance=2100, body_tol_ticks=350, later_tol_ticks=350),
}


@dataclass(frozen=True)
class Line:
    price: float
    bars_back: int
    pivot_time: Optional[int]
    fallback: bool


@dataclass(frozen=True)
class Levels:
    bar_time: int
    resistance: Line
    support: Line
    target_resistance: Line
    target_support: Line


def _mirror(bar: Bar) -> Bar:
    """Spiegelt een candle, zodat Support met de Resistance-logica rekent."""
    return Bar(bar.t, -bar.o, -bar.l, -bar.h, -bar.c, bar.valid)


class _Side:
    """Zoekt het niveau en Target aan één kant; index i = aantal candles terug."""

    def __init__(self, bars: list[Bar], end: int, settings: Settings) -> None:
        self.bars = bars
        self.end = end
        self.s = settings
        self.body_tol = settings.body_tol_ticks * settings.tick
        self.later_tol = settings.later_tol_ticks * settings.tick if settings.later_tol_enabled else 0.0

    def at(self, i: int) -> Optional[Bar]:
        index = self.end - i
        return self.bars[index] if 0 <= index <= self.end else None

    def time_at(self, i: int) -> Optional[int]:
        bar = self.at(i)
        return bar.t if bar else None

    def _body_valid(self, i: int, bar: Bar, candidate: float, max1: Optional[float], max2: Optional[float]) -> bool:
        top = max(bar.o, bar.c)
        exclude = self.s.exclude_reversal
        full = max1 if exclude else (top if max1 is None else max(max1, top))
        if full is None or full <= candidate + self.later_tol:
            return True
        if not self.s.body_tol_enabled or i < 1:
            return False
        rest = max2 if exclude else (top if max2 is None else max(max2, top))
        next_bar = self.at(i - 1)
        return (
            next_bar is not None
            and next_bar.valid
            and next_bar.c < next_bar.o
            and max(next_bar.o, next_bar.c) <= candidate + max(self.body_tol, self.later_tol)
            and (rest is None or rest <= candidate + self.later_tol)
        )

    def pivots(self) -> Iterator[tuple[int, float]]:
        """Geeft elke body-geldige overgang, van recent naar oud."""
        max1: Optional[float] = None
        max2: Optional[float] = None
        for i in range(self.s.max_scan - 1):
            bar = self.at(i)
            pivot = self.at(i + 1)
            if bar and pivot and bar.valid and pivot.valid and pivot.c > pivot.o and bar.c < bar.o:
                gap = self.s.session_gap_open and bar.t - pivot.t > BAR_SECONDS
                candidate = bar.o if gap else max(pivot.o, pivot.c)
                if self._body_valid(i, bar, candidate, max1, max2):
                    yield i, candidate
            max2 = max1
            if bar and bar.valid:
                top = max(bar.o, bar.c)
                max1 = top if max1 is None else max(max1, top)

    def _wick_valid(self, pivot_offset: int, level: float) -> bool:
        for k in range(pivot_offset - 2, -1, -1):
            bar = self.at(k)
            if bar and bar.valid:
                graced = k == pivot_offset - 2 and bar.c < bar.o
                if not graced and bar.h >= level:
                    return False
        return True

    def _highest(self) -> float:
        highs = [bar.h for i in range(self.s.max_scan) if (bar := self.at(i)) and bar.valid]
        if not highs:
            raise ValueError("Geen geldige candles in de scanrange.")
        return max(highs)

    def calculate(self) -> tuple[Line, Line]:
        s = self.s
        first = next(self.pivots(), None)
        fallback = first is None
        level = self._highest() if first is None else first[1]
        back = s.max_scan if first is None else first[0] + 1

        target: Optional[float] = None
        target_back = s.max_scan
        shift: Optional[float] = None
        shift_back = 0
        for i, candidate in self.pivots():
            if candidate - level >= s.min_target_distance * s.tick and self._wick_valid(i + 1, candidate):
                target = candidate
                target_back = i + 1
                break
            shift = candidate
            shift_back = i + 1

        if target is not None and shift is not None:
            level = shift
            back = shift_back

        target_fallback = target is None
        if target is None:
            target = level + max(s.auto_target_ticks, s.min_target_distance) * s.tick

        return (
            Line(level, back, self.time_at(back), fallback),
            Line(target, target_back, self.time_at(target_back), target_fallback),
        )


def calculate(bars: list[Bar], end: int, settings: Settings) -> Levels:
    """Berekent de niveaus bij het sluiten van de candle op index end."""
    resistance, target_resistance = _Side(bars, end, settings).calculate()
    mirrored, mirrored_target = _Side([_mirror(bar) for bar in bars], end, settings).calculate()
    support = Line(-mirrored.price, mirrored.bars_back, mirrored.pivot_time, mirrored.fallback)
    target_support = Line(
        -mirrored_target.price, mirrored_target.bars_back, mirrored_target.pivot_time, mirrored_target.fallback
    )
    return Levels(bars[end].t, resistance, support, target_resistance, target_support)


def parse_bars(payload: object) -> tuple[list[Bar], Optional[str]]:
    """Leest de get_ohlcv-uitvoer in rij- of kolomvorm."""
    symbol = None
    if isinstance(payload, dict) and isinstance(payload.get("content"), list):
        text = next((item.get("text") for item in payload["content"] if item.get("type") == "text"), None)
        if text is None:
            raise ValueError("Geen tekstinhoud gevonden in de MCP-respons.")
        payload = json.loads(text)
    if isinstance(payload, dict):
        symbol = payload.get("symbol")
        payload = payload.get("bars")

    if isinstance(payload, dict):
        columns = [payload[key] for key in ("t", "o", "h", "l", "c")]
        rows = list(zip(*columns))
    elif isinstance(payload, list):
        rows = [(row["t"], row["o"], row["h"], row["l"], row["c"]) for row in payload]
    else:
        raise ValueError("Geen candles gevonden. Verwacht de JSON-uitvoer van get_ohlcv.")

    bars = [
        Bar(int(t), float(o), float(h), float(l), float(c), o > 0 and h > 0 and l > 0 and c > 0)
        for t, o, h, l, c in sorted(rows, key=lambda row: row[0])
    ]
    if len(bars) < 2:
        raise ValueError("Te weinig candles in de invoer.")
    if min(b.t - a.t for a, b in zip(bars, bars[1:])) != BAR_SECONDS:
        raise ValueError("De invoer moet uit 30m-candles bestaan (interval=\"30m\").")
    return bars, symbol


def detect_profile(symbol: Optional[str]) -> Optional[str]:
    name = (symbol or "").upper()
    if "XAU" in name or "GOLD" in name:
        return "xauusd"
    if "NAS100" in name or "US100" in name:
        return "nasdaq"
    return None


def parse_now(value: Optional[str]) -> int:
    if value is None:
        return int(time_module.time())
    if value.isdigit():
        return int(value)
    return int(datetime.fromisoformat(value).timestamp())


def format_time(timestamp: Optional[int]) -> str:
    if timestamp is None:
        return "buiten de data"
    return datetime.fromtimestamp(timestamp).astimezone().strftime("%d-%m-%Y %H:%M")


def line_rows(levels: Levels) -> list[tuple[str, Line, float]]:
    sr_range = levels.resistance.price - levels.support.price
    return [
        ("Target Resistance", levels.target_resistance, levels.target_resistance.price - levels.resistance.price),
        ("Resistance", levels.resistance, sr_range),
        ("Support", levels.support, sr_range),
        ("Target Support", levels.target_support, levels.support.price - levels.target_support.price),
    ]


def describe(line: Line) -> str:
    if line.fallback:
        return "FALLBACK"
    return f"pivot {line.bars_back} candles terug ({format_time(line.pivot_time)})"


def print_levels(levels: Levels, symbol: str) -> None:
    print(f"{symbol}, laatste gesloten 30m-candle: {format_time(levels.bar_time)}")
    print()
    for name, line, size in line_rows(levels):
        print(f"{name:<18} {line.price:>10.2f}   Range {size:>8.2f}   {describe(line)}")


def print_history(history: list[Levels], symbol: str) -> None:
    print(f"{symbol}, niveaus per gesloten 30m-candle")
    print()
    print(f"{'Candle':<17} {'Target R':>10} {'Resistance':>11} {'Support':>10} {'Target S':>10}")
    for levels in history:
        print(
            f"{format_time(levels.bar_time):<17} {levels.target_resistance.price:>10.2f} "
            f"{levels.resistance.price:>11.2f} {levels.support.price:>10.2f} {levels.target_support.price:>10.2f}"
        )


def to_json(levels: Levels) -> dict:
    keys = ["target_resistance", "resistance", "support", "target_support"]
    return {
        "bar_time": levels.bar_time,
        **{
            key: {
                "price": round(line.price, 10),
                "range": round(size, 10),
                "bars_back": line.bars_back,
                "pivot_time": line.pivot_time,
                "fallback": line.fallback,
            }
            for key, (_, line, size) in zip(keys, line_rows(levels))
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Berekent S/R en Targets zoals trade_lines.pine.")
    parser.add_argument("input", help="JSON-bestand met de get_ohlcv-uitvoer, of - voor stdin")
    parser.add_argument("--profile", choices=sorted(PROFILES), help="standaard: afgeleid van het symbool")
    parser.add_argument("--symbol", help="symbool, als dat niet in de invoer staat")
    parser.add_argument("--tick", type=float, help="mintick van de feed (verplicht bij een andere Nasdaq-feed dan FTMO_OANDA)")
    parser.add_argument("--history", type=int, default=1, metavar="N", help="toon de laatste N gesloten candles")
    parser.add_argument("--now", help="rekenmoment (epoch of ISO), bepaalt of de laatste candle gesloten is")
    parser.add_argument("--json", action="store_true", help="uitvoer als JSON")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        if args.history < 1:
            raise ValueError("--history moet minimaal 1 zijn.")
        if args.input == "-":
            payload = json.load(sys.stdin)
        else:
            with open(args.input, encoding="utf-8") as handle:
                payload = json.load(handle)
        bars, input_symbol = parse_bars(payload)
        symbol = args.symbol or input_symbol or "onbekend symbool"
        profile = args.profile or detect_profile(symbol)
        if profile is None:
            raise ValueError(f"Geen profiel bekend voor {symbol}. Geef --profile xauusd of --profile nasdaq op.")
        if profile == "nasdaq":
            if symbol.upper().startswith("FX:"):
                raise ValueError(f"{symbol} is de FXCM-feed. Gebruik voor de Nasdaq FTMO_OANDA:US100.CASH.")
            if args.tick is None and not symbol.upper().startswith("FTMO_OANDA:"):
                raise ValueError("Geef bij een andere Nasdaq-feed dan FTMO_OANDA de mintick op met --tick.")
        if args.tick is not None and args.tick <= 0:
            raise ValueError("--tick moet groter zijn dan 0.")
        settings = PROFILES[profile] if args.tick is None else replace(PROFILES[profile], tick=args.tick)

        # Net als in Pine telt een lopende candle niet mee.
        last = len(bars) - 1
        if bars[last].t + BAR_SECONDS > parse_now(args.now):
            last -= 1
        first = last - args.history + 1
        if first < 0:
            raise ValueError("Te weinig gesloten candles voor --history.")
        if first + 1 < settings.max_scan:
            print(
                f"Let op: {first + 1} gesloten candles beschikbaar, het Pine-script scant er "
                f"{settings.max_scan}. Vraag meer candles op als een niveau op FALLBACK staat.",
                file=sys.stderr,
            )
        history = [calculate(bars, end, settings) for end in range(first, last + 1)]
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Fout: {error}", file=sys.stderr)
        return 2

    if args.json:
        result = [to_json(levels) for levels in history]
        print(json.dumps({"symbol": symbol, "levels": result if args.history > 1 else result[0]}, indent=2))
    elif args.history > 1:
        print_history(history, symbol)
    else:
        print_levels(history[0], symbol)
    return 0


if __name__ == "__main__":
    sys.exit(main())
