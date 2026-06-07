#!/usr/bin/env python3
"""Import LCSC / EasyEDA parts into this KiCad project.

Usage (IMPORTANT: run with the Windows Python, not the msys2 one):

    py -3.14 tools/import_lcsc.py C5368700 [C12345 ...]

Each part's symbol is appended to libraries/LCSC.kicad_sym, its footprint to
libraries/LCSC.pretty/, and its 3D model to libraries/LCSC.3dshapes/. The
project sym-lib-table / fp-lib-table are created on first run so KiCad picks
up the "LCSC" library automatically.

Why this wrapper exists (lessons from the first manual import):
  * The msys2 Python at C:\\msys64 fails TLS verification against the EasyEDA
    API ("self-signed certificate in certificate chain"). The Windows Python
    (py -3.14) has a working CA bundle, so we re-exec under it if needed.
  * easyeda2kicad's --project-relative path math throws if --output is a
    relative path, so we always pass an absolute path.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# Project root = parent of this tools/ directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = PROJECT_ROOT / "libraries"
LIB_NAME = "LCSC"
SYM_OUTPUT = LIB_DIR / f"{LIB_NAME}.kicad_sym"

SYM_LIB_TABLE = PROJECT_ROOT / "sym-lib-table"
FP_LIB_TABLE = PROJECT_ROOT / "fp-lib-table"

SYM_TABLE_CONTENT = f"""(sym_lib_table
  (version 7)
  (lib (name "{LIB_NAME}")(type "KiCad")(uri "${{KIPRJMOD}}/libraries/{LIB_NAME}.kicad_sym")(options "")(descr "LCSC/EasyEDA parts imported via easyeda2kicad"))
)
"""

FP_TABLE_CONTENT = f"""(fp_lib_table
  (version 7)
  (lib (name "{LIB_NAME}")(type "KiCad")(uri "${{KIPRJMOD}}/libraries/{LIB_NAME}.pretty")(options "")(descr "LCSC/EasyEDA footprints imported via easyeda2kicad"))
)
"""


def ssl_works() -> bool:
    """Return True if this interpreter can do TLS against EasyEDA."""
    try:
        urllib.request.urlopen("https://easyeda.com", timeout=10)
    except urllib.error.HTTPError:
        # Any HTTP status means the TLS handshake succeeded.
        return True
    except Exception:
        return False
    return True


def find_good_python() -> str | None:
    """Find a Windows Python with a working CA bundle (for re-exec)."""
    for cmd in (["py", "-3.14"], ["py", "-3"], ["python"]):
        exe = shutil.which(cmd[0])
        if not exe:
            continue
        try:
            r = subprocess.run(
                [exe, *cmd[1:], "-c",
                 "import urllib.request as u\n"
                 "try:\n u.urlopen('https://easyeda.com',timeout=10)\n"
                 "except u.error.HTTPError:\n pass\n"
                 "except Exception:\n raise SystemExit(1)\n"],
                capture_output=True, timeout=30,
            )
            if r.returncode == 0:
                return " ".join([exe, *cmd[1:]])
        except Exception:
            continue
    return None


def ensure_lib_tables() -> None:
    if not SYM_LIB_TABLE.exists():
        SYM_LIB_TABLE.write_text(SYM_TABLE_CONTENT, encoding="utf-8")
        print(f"[+] Created {SYM_LIB_TABLE.name}")
    if not FP_LIB_TABLE.exists():
        FP_LIB_TABLE.write_text(FP_TABLE_CONTENT, encoding="utf-8")
        print(f"[+] Created {FP_LIB_TABLE.name}")


def import_part(lcsc_id: str) -> int:
    cmd = [
        sys.executable, "-m", "easyeda2kicad",
        "--full",
        f"--lcsc_id={lcsc_id}",
        "--output", str(SYM_OUTPUT),   # absolute path required for --project-relative
        "--project-relative",
        "--overwrite",
    ]
    print(f"[*] Importing {lcsc_id} ...")
    return subprocess.run(cmd).returncode


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    if not ssl_works():
        good = find_good_python()
        if good is None:
            print("[!] This Python cannot reach the EasyEDA API (TLS failure) and "
                  "no Windows Python was found.\n"
                  "    Re-run with:  py -3.14 tools/import_lcsc.py " + " ".join(argv))
            return 1
        print(f"[i] Current Python has TLS issues; re-executing under: {good}")
        return subprocess.run(good.split() + [str(Path(__file__).resolve()), *argv]).returncode

    LIB_DIR.mkdir(exist_ok=True)
    ensure_lib_tables()

    failed = []
    for lcsc_id in argv:
        if import_part(lcsc_id) != 0:
            failed.append(lcsc_id)

    if failed:
        print(f"[!] Failed: {', '.join(failed)}")
        return 1
    print(f"[OK] Done. Library '{LIB_NAME}' is registered in this project.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
