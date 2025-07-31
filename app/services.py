"""Business logic layer: pure functions + optional caching."""
from functools import lru_cache
from typing import Callable, Dict, Tuple

from .models import ConversionRequest, ConversionResponse

# ------------------------ LENGTH ------------------------ #
# base unit = metre
_LENGTH_FACTORS: Dict[str, float] = {
    "m": 1.0,
    "cm": 0.01,
    "mm": 0.001,
    "km": 1000.0,
    "ft": 0.3048,
    "in": 0.0254,
    "mi": 1609.34,
}

# ------------------------ WEIGHT ------------------------ #
# base unit = kilogram
_WEIGHT_FACTORS: Dict[str, float] = {
    "kg": 1.0,
    "g": 0.001,
    "lb": 0.453592,
    "oz": 0.0283495,
}

# ------------------------ TEMPERATURE ------------------------ #
# Use callable mapping because °C↔K↔F require formulas
def _c_to_f(c: float) -> float:  # noqa: D401
    """Celsius → Fahrenheit."""
    return c * 9 / 5 + 32


def _f_to_c(f: float) -> float:
    return (f - 32) * 5 / 9


def _c_to_k(c: float) -> float:
    return c + 273.15


def _k_to_c(k: float) -> float:
    return k - 273.15


_TEMPERATURE_FUNCS: Dict[Tuple[str, str], Callable[[float], float]] = {
    ("c", "f"): _c_to_f,
    ("f", "c"): _f_to_c,
    ("c", "k"): _c_to_k,
    ("k", "c"): _k_to_c,
    ("f", "k"): lambda f: _c_to_k(_f_to_c(f)),
    ("k", "f"): lambda k: _c_to_f(_k_to_c(k)),
}


# ------------------------ PUBLIC FACADE ------------------------ #
@lru_cache(maxsize=128)  # simple in-memory cache
def convert(req: ConversionRequest) -> ConversionResponse:
    """Main entry: dispatch per category, cache identical calls."""
    if req.category == "length":
        res = _convert_by_factor(req.value, req.from_unit, req.to_unit, _LENGTH_FACTORS)
    elif req.category == "weight":
        res = _convert_by_factor(req.value, req.from_unit, req.to_unit, _WEIGHT_FACTORS)
    elif req.category == "temperature":
        res = _convert_temp(req.value, req.from_unit, req.to_unit)
    else:  # pragma: no cover
        raise ValueError(f"Unsupported category {req.category}")

    details = f"{req.value} {req.from_unit} → {res} {req.to_unit}"
    return ConversionResponse(result=res, details=details)


# ------------------------ helpers ------------------------ #
def _convert_by_factor(value: float, src: str, dst: str,
                       table: Dict[str, float]) -> float:
    """Generic helper for units convertible via multiplicative factor."""
    try:
        base = value * table[src]  # go to base unit
        return round(base / table[dst], 6)  # 6 decimals is enough
    except KeyError as exc:
        raise ValueError(f"Unknown unit: {exc.args[0]}") from exc


def _convert_temp(value: float, src: str, dst: str) -> float:
    key = (src, dst)
    if key not in _TEMPERATURE_FUNCS:
        raise ValueError(f"Unsupported temperature conversion {src}->{dst}")
    return round(_TEMPERATURE_FUNCS[key](value), 2)
