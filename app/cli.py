"""Click-powered command-line interface – the ‘controller/view’ layer."""
import sys
from typing import Optional

import click
from tabulate import tabulate  # pretty table output

from .db import init_db, log_conversion
from .models import ConversionRequest
from .services import convert

# ------------------------------------------------------------- #
# Ensure DB tables exist before any command executes
init_db()


@click.group()
def convert_cli() -> None:  # root command
    """Convert length, temperature or weight between common units."""
    pass


def _run_conversion(category: str, value: float, src: str, dst: str,
                    verbose: bool) -> None:
    """Shared runner used by all sub-commands."""
    try:
        req = ConversionRequest(
            category=category, value=value, from_unit=src, to_unit=dst
        )
        resp = convert(req)
        log_conversion(category, value, src, dst, resp.result)
        if verbose:
            click.echo(tabulate([[resp.details, resp.result]], headers=["Details", "Result"]))
        else:
            click.echo(resp.result)
    except Exception as exc:  # noqa: BLE001 – show user-friendly msg
        click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(1)


# -------- LENGTH -------- #
@convert_cli.command()
@click.argument("value", type=float)
@click.option("--from", "src", required=True, help="Source unit (m, cm, ft, mi …)")
@click.option("--to", "dst", required=True, help="Target unit")
@click.option("-v", "--verbose", is_flag=True, help="Pretty output table")
def length(value: float, src: str, dst: str, verbose: bool) -> None:
    """Convert **length** units."""
    _run_conversion("length", value, src, dst, verbose)


# -------- TEMPERATURE -------- #
@convert_cli.command()
@click.argument("value", type=float)
@click.option("--from", "src", required=True, help="Source unit (C, F, K)")
@click.option("--to", "dst", required=True, help="Target unit")
@click.option("-v", "--verbose", is_flag=True)
def temperature(value: float, src: str, dst: str, verbose: bool) -> None:
    """Convert **temperature** units."""
    _run_conversion("temperature", value, src, dst, verbose)


# -------- WEIGHT -------- #
@convert_cli.command()
@click.argument("value", type=float)
@click.option("--from", "src", required=True, help="Source unit (kg, g, lb …)")
@click.option("--to", "dst", required=True, help="Target unit")
@click.option("-v", "--verbose", is_flag=True)
def weight(value: float, src: str, dst: str, verbose: bool) -> None:
    """Convert **weight** units."""
    _run_conversion("weight", value, src, dst, verbose)


if __name__ == "__main__":  # allows `python -m app.cli …`
    convert_cli()


