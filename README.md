# Custom Flight Controller

An open-source ArduPilot-compatible flight controller for quadcopters, built around the STM32H743VIT6 with an integrated 2.4 GHz ExpressLRS receiver.

> **Status: in development.** Schematic capture is underway. The board has not yet been fabricated or flown. See [Roadmap](#roadmap).

---

## Overview

Most hobby flight controllers bolt an RC receiver and GPS module onto the outside of the board. This design integrates the ExpressLRS receiver directly onto the PCB, and moves the GNSS receiver and magnetometer onto a separate mast-mounted board where they belong, away from high-current traces and clear of 2.4 GHz desense.

The result is a two-board system: a main flight controller carrying the MCU, sensors, power tree and radio, and a small NavBoard carrying GNSS and the compass.

## Key specifications

| | |
|---|---|
| **MCU** | STM32H743VIT6 (Cortex-M7, 480 MHz, LQFP100) |
| **Firmware** | ArduPilot (custom hwdef) |
| **IMUs** | BMI270 + ASM330LHBTR (dual, redundant, SPI) |
| **Barometer** | BMP388 |
| **Power monitoring** | INA226 (I²C) |
| **RC link** | On-board 2.4 GHz ExpressLRS — ESP8285 + SX1280 |
| **GNSS** | u-blox MAX-F10S (L1/L5 dual-band, on NavBoard) |
| **Magnetometer** | BMM350 (on NavBoard) |
| **Logging** | microSD via 4-bit SDMMC |
| **Motor outputs** | 4× DShot on TIM1, with ESC telemetry return |
| **Input voltage** | 6S LiPo (25.2 V nominal max) |
| **EDA** | KiCad |

## Architecture

### Flight controller board

**Power tree.** A TPS54360 (60 V input) steps the 6S pack down to 5 V. A TPS2116 power mux OR-s that against USB VBUS so the two supplies never contend, with the buck holding priority. Three independent 3.3 V rails branch from there:

- **AP2114H** — MCU, microSD, INA226 (digital, noisy)
- **TPS7A2033** — IMUs and barometer (low-noise, high PSRR)
- **AMS1117-3.3** — ESP8285 + SX1280 (isolates WiFi current transients)

Separating the rails keeps SD-card write spikes and WiFi bursts off the gyro supply, since IMU noise propagates directly into the PID loop and EKF.

**Radio.** The ExpressLRS section replicates the pin mapping of the official [ExpressLRS RX_20x20 reference design](https://github.com/ExpressLRS/ExpressLRS-Hardware), so it flashes with a stock `DIY_2400_RX_ESP8285_SX1280` target rather than a custom hardware definition. RF routes 50 Ω controlled-impedance to a U.FL connector; a separate PCB trace antenna serves the ESP's WiFi for OTA updates.

**Connectivity.** All ports follow the Pixhawk connector standard (JST-GH 1.25 mm) so off-the-shelf peripherals are capable of being used: telemetry, RC, spare UARTs, I²C, and analog battery input.


## Repository structure

```
├── FlightComputer.kicad_pro     # KiCad project
├── FlightComputer.kicad_sch     # Top-level schematic
├── FlightComputer.kicad_pcb     # KiCad pcb layout
├── mcu.kicad_sch                # MCU, debug
├── power.kicad_sch              # Power tree
├── IO.kicad_sch                 # USB, connectors, power mux
├── sensing_interface.kicad_sch  # Sensors
├── COMMS.kicad_sch              # ExpressLRS connections
├── libraries/                   # LCSC-sourced symbols and footprints
└── tools/
    └── import_lcsc.py           # Pulls LCSC parts into the project library
```

## Design notes


**Sensor selection was validated against ArduPilot driver support before commit.** An earlier revision specified the BMI323, which has no mainline ArduPilot driver — flying it would have meant writing and maintaining one, or running on a single working IMU. It was replaced with a supported part.

**The GNSS receiver is not on the flight controller.** Doing the bare-module RF design on the main board would have put a GNSS front end next to switching regulators and a 2.4 GHz transmitter. Moving it to a mast board solves the antenna placement, the compass's magnetic interference, and the desense problem at once.

## Roadmap

- [x] Component selection and ArduPilot driver validation
- [x] MCU, power tree, and I/O schematic capture
- [ ] ExpressLRS receiver integration
- [ ] PCB layout and impedance-controlled routing
- [ ] Fabrication and assembly
- [ ] ArduPilot hwdef authoring
- [ ] Bring-up and bench validation
- [ ] Flight testing

## Building

Manufacturing files target JLCPCB assembly; parts are sourced from LCSC where possible. The `tools/import_lcsc.py` helper pulls symbols, footprints, and 3D models into the project library by LCSC part number:

```bash
python tools/import_lcsc.py C88373
```

## Acknowledgements

- [ArduPilot](https://ardupilot.org/) — flight control firmware
- [ExpressLRS](https://www.expresslrs.org/) — RC link firmware and open reference hardware


---

*Built by Mounib Jamous. Questions and issues welcome.*
