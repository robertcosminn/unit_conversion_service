import subprocess
import sys
from pathlib import Path


def _run(args):
    """Helper to run CLI in a subprocess and capture stdout."""
    cmd = [sys.executable, "-m", "app.cli", *args]
    return subprocess.check_output(cmd, text=True).strip()


def test_length_to_ft(tmp_path: Path):  # noqa: D103
    out = _run(["length", "1", "--from", "m", "--to", "ft"])
    assert abs(float(out) - 3.28084) < 1e-4
