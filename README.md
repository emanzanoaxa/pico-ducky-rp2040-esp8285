# pico-ducky-rp2040-esp8285 🚀

An adaptation of [pico-ducky](https://github.com/dbisu/pico-ducky) tailored to work on Chinese Pi Pico W clones that use an ESP8285 WiFi module connected over UART.

This fork keeps the same features of the original project (local payload execution using DuckyScript + a webserver to upload/edit/run scripts), but it is modified specifically to operate with RP2040 boards that rely on the included ESP module (esp8285) rather than a native Pico W wireless stack.

---

## ⚠️ Important Compatibility Note

- This project only works for **Chinese Pi Pico W clones that use an `esp8285` WiFi module** (connected via UART TX/RX). It does not target the official Raspberry Pi Pico W (with the Infineon/CYW43439 WiFi chip).
- The code expects the Adafruit CircuitPython runtime and uses `adafruit_espatcontrol` to communicate with the esp8285 via UART.

---

## ✅ What this fork includes

- Web UI to view/edit and run DuckyScript-style payloads (found under: `src/espatwebapp.py`) at `http://192.168.4.1`
- `payload.dd` sample payloads (`payload.dd`, `payload1.dd`) and a simple editor in the web UI
- Support for selecting payloads using switches on GP4/GP5/GP10/GP11 (GPIO pins) or running a payload via the web/API
- A `boot.py` that toggles onboard USB storage visibility based on a jumper to GP15 (explained below)
- Default AP credentials and settings saved to `src/secrets.py`

---

## Hardware & Pinout 🔧

- Bar the RP2040 microcontroller, this adaptation expects the WiFi module to be an esp8285 connected over UART. The default UART pins are:
	- UART_TX = `GP0`
	- UART_RX = `GP1`
- Web server uses AT-style commands via UART and `adafruit_espatcontrol`

Programming / USB storage jumper:
- `GP15` determines whether the USB storage is visible to the host
	- By default, the storage is disabled (not visible) for safety (the code sets USB storage to disabled if GP15 is not grounded)
	- To enable USB storage (so you can copy files onto the board), ground `GP15` while connecting the board to your PC

---

## Software prerequisites

- Adafruit CircuitPython for Raspberry Pi Pico (UF2): A file is included in the repository: `adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.1.uf2`
- The library files in the `src/lib/` directory are provided to work with this CircuitPython build. Copy them to the board instead of installing them separately.

---

## Quick Start — Flash + Install 🔄

1. Download the UF2:
	 - The included `adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.1.uf2` file in the project root can be used. If you want to use another version of CircuitPython: validate that the `lib` subfolder files match the CircuitPython version you flash.

2. Put the board into bootloader mode and flash the UF2 file (drag & drop the `.uf2` file to the board's USB mass storage device). If unsure: double-press the board's BOOT/RESET button to mount the drive.

3. Copy all the files inside the `src` directory to the root of the board's USB storage (the CircuitPython drive). The files you should copy include:
	 - `code.py`, `boot.py`, `duckyinpython.py`, `espatwebapp.py`, `espatwebapp_html.py`, `espatwifi.py`, `secrets.py`, `payload.dd`, and the `lib/` folder.

4. Eject the board and plug it in (or reset). CircuitPython will automatically run `code.py` on boot.

5. Connect to the board's WiFi AP: default credentials are in `src/secrets.py`. Defaults are:
	 - SSID: `TestAP`
	 - Password: `passw123`
	 - Visit: http://192.168.4.1

---

## Configuration ⚙️

- `src/secrets.py`: Change the AP name and password in `secrets = { 'ssid' : 'MySSID', 'password' : 'MyPass' }`
- `src/espatwifi.py`: change UART pin constants, BAUD_RATE, or WiFi AP channel/encryption if necessary (defaults in the file are `GP0`, `GP1`, 115200)

---

## Using the Web UI

Visit: http://192.168.4.1

Main features:
- Browse and edit payload files (`.dd`) via the web UI
- Upload and create new payload files
- Run a payload from the UI (click “Run”). The web server uses the ESP8285 AT commands and may be slow/unreliable depending on your board – see the troubleshooting section.

Available endpoints (examples):
- GET `/ducky` — Main payload list
- GET `/edit/<filename>` — Edit a payload
- POST `/write/<filename>` — Save contents to a payload
- GET `/run/<filename>` — Run a payload immediately
- GET `/api/run/<1|2|3|4>` — Run payload 1–4 (map to `payload.dd`, `payload2.dd`...)

---

## Payload & Run Behavior 📝

- The project uses a DuckyScript parser (`duckyinpython.py`) and will run the selected payload on boot, unless programming mode is detected via `GP15` (if grounded, programming mode). The `getProgrammingStatus()` checks `GP15` and causes the board to not auto-run payloads.
- `selectPayload()` checks GP4/GP5/GP10/GP11; if no switch is pulled to ground, it defaults to `payload.dd`.
- Example payload provided: `payload.dd` prints `Hello World!` into Notepad on Windows.

---

## Troubleshooting 🛠️

- The web server is slow and can be unreliable: this is a limitation of the esp8285 over UART and the AT command approach. If requests time out, try again, or restart the esp module using the device USB reset.
- If the web UI doesn’t load:
	- Make sure the esp module is properly wired to the UART pins (`GP0`/`GP1` by default)
	- Make sure `secrets.py` has valid values and the module gets configured to AP mode
- To make storage visible to the host for copying files: bridge `GP15` to `GND` while inserting the board into USB.
- If the board doesn’t run payloads, verify `code.py` and `ducky` script are present and not failing—connect to the serial REPL or use prints in the code for diagnostics.

---

## Security & Ethics ⚖️

This tool can execute keyboard macros and could be misused. Use it only with devices you own or have explicit permission to test. Abide by local laws and organization policies when using or testing this code.

---

## Contributing & Credits ❤️

- This project is a fork/adaptation of [dbisu/pico-ducky](https://github.com/dbisu/pico-ducky). Big thanks to Dave Bailey (@dbisu) for the original work.
- PRs, issues, and enhancements that improve reliability for ESP8285 usage are welcome.

---

## License

This project uses MIT License (see the original license in the code headers). Check `LICENSE` in this repository for details.

---

