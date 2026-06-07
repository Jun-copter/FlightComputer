# LCSC / EasyEDA → KiCad import

Imports LCSC parts (symbol + footprint + 3D model) into this KiCad 10 project
using [`easyeda2kicad`](https://github.com/uPesy/easyeda2kicad.py).

## One-time setup

```powershell
py -3.14 -m pip install --user easyeda2kicad
```

> Use the **Windows** Python (`py -3.14`), **not** the msys2 Python at
> `C:\msys64`. The msys2 Python fails TLS verification against the EasyEDA API
> (`self-signed certificate in certificate chain`). The script auto-detects this
> and re-execs under a working Python, but installing into the right one avoids
> a round trip.

## Import a part

```powershell
py -3.14 tools/import_lcsc.py C5368700            # single part (BMI323)
py -3.14 tools/import_lcsc.py C5368700 C12345 ... # multiple at once
```

This will:
- append the symbol to `libraries/LCSC.kicad_sym`
- add the footprint to `libraries/LCSC.pretty/`
- add the 3D model to `libraries/LCSC.3dshapes/`
- create `sym-lib-table` / `fp-lib-table` (first run only) so KiCad
  auto-loads the **LCSC** library for this project

Re-running an existing part overwrites it (`--overwrite`).

## Known LCSC part numbers for this board

| Part        | LCSC      |
|-------------|-----------|
| BMI323 IMU  | C5368700  |

(Add the others — ASM330LHB, BMP388, INA226, BMM350, MAX-F10S, etc. — as you
look up their LCSC IDs.)

## Notes / gotchas baked into the script

- `easyeda2kicad --project-relative` crashes if `--output` is a *relative*
  path; the script always passes an absolute path.
- Symbols come out in KiCad-6 format (`version 20211014`); KiCad 10 reads and
  auto-upgrades them on load (verified with `kicad-cli sym upgrade`).
- The generated footprint/3D name may carry EasyEDA's generic LGA package name
  (e.g. `LGA-14_..._QMI8658A`); this is cosmetic — the pads match the BMI323.
