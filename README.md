# Logitech Sphere Controller

A macOS GUI app that controls the **pan/tilt motor** of the Logitech QuickCam Sphere (USB `046d:0994`).

## Features

- Up/Down/Left/Right pan/tilt control (D-pad buttons + keyboard arrow keys)
- Continuous movement while a button is held (native C thread, 30 ms tick)
- Adjustable step size (2°–10°)
- Reset to center (Space / R key)
- App version and build date display
- Webcam-lens style app icon

## Requirements

- macOS (IOKit-based USB control)
- Logitech QuickCam Sphere (USB VID:PID `046d:0994`)
- Python 3.12+, [uv](https://github.com/astral-sh/uv)
- Xcode Command Line Tools (`clang`)

## Install & Build

```bash
# 1. Install Python dependencies
uv sync

# 2. Build the native motor control binary
clang -framework Foundation -framework IOKit -framework AppKit -fno-objc-arc -lpthread \
  uvc-util/src/UVCController.m uvc-util/src/UVCType.m uvc-util/src/UVCValue.m \
  motor_final.m -o motor_final -I uvc-util/src

# 3. Run (development mode)
uv run python sphere_controller.py

# 4. Build a standalone .app
BUILD_DATE=$(date +%Y-%m-%d) uv run pyinstaller \
  --name "Sphere Controller" --onefile --windowed \
  --add-binary "motor_final:." --icon icon.icns \
  --noconfirm sphere_controller.py
rm -rf build "Sphere Controller.spec"
# -> dist/Sphere Controller.app
```

## Usage

### GUI buttons
| Button | Action |
|--------|--------|
| Up (green) | Tilt up |
| Down (green) | Tilt down |
| Left (blue) | Pan left |
| Right (blue) | Pan right |
| Reset (red) | Return to center |

### Keyboard
| Key | Action |
|-----|--------|
| Arrow keys | Pan/tilt (hold for continuous movement) |
| Space / R | Reset (return to center) |

### CLI (direct `motor_final`)
```bash
./motor_final right 5     # right 5 degrees
./motor_final left 10     # left 10 degrees
./motor_final up 3        # up 3 degrees
./motor_final down 3      # down 3 degrees
./motor_final reset       # center
./motor_final --daemon    # daemon mode (used by the GUI)
```

## Project structure

```
sphere_controller.py   # GUI app (PySide6)
motor_final.m          # Motor control source (Objective-C, IOKit)
motor_final            # Built motor control binary (gitignored)
uvc-util/              # UVC controller library (jtfrey/uvc-util, bundled)
icon.png               # App icon (512x512 webcam lens)
icon.icns              # macOS app icon
pyproject.toml         # Python dependencies (PySide6, PyInstaller)
dist/                  # Built .app
```

## Technical details

### UVC Extension Unit protocol

The Logitech Sphere does not expose standard UVC PTZ; instead, it uses a
vendor-specific **Extension Unit** for motor control.

| Item | Value |
|------|-------|
| GUID | `{63610682-5070-49ab-b8cc-b3855e8d2256}` |
| Unit ID | 9 |
| Selector 1 | Pan/Tilt Relative (4 bytes, signed int16 LE × 2) |
| Selector 2 | Pan/Tilt Reset (1 byte, `0x03` = both axes) |
| Selector 3 | Focus Motor (6 bytes) |
| Unit | 64 = 1 degree |

### Architecture

```
[GUI (Python/PySide6)]
    |  stdin pipe (move/stop/reset)
    v
[motor_final --daemon (Objective-C)]
    |  C pthread (30 ms tick)
    v
[IOKit USB control transfer]
    |  UVC Extension Unit (Unit 9, Selector 1)
    v
[Logitech Sphere motor]
```

- The GUI only sends `move <pan> <tilt>` / `stop` commands over a pipe.
- A pthread inside the C daemon repeats the USB command every 30 ms for smooth motion.
- No per-step process startup overhead (persistent daemon).

## License

This project is released under the [MIT License](LICENSE).

### Third-party components

| Component | License | Purpose |
|-----------|---------|---------|
| [PySide6](https://doc.qt.io/qtforpython-6/) | LGPLv3 | GUI framework |
| [Qt 6](https://www.qt.io/) | LGPLv3 | Underlying library behind PySide6 |
| [PyInstaller](https://pyinstaller.org/) | GPL-2.0 + bootloader exception | App packaging |
| [uvc-util](https://github.com/jtfrey/uvc-util) | MIT | UVC controller library (bundled) |

Full notices and license texts are available in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

> "Logitech" and "Logitech Sphere" are trademarks of Logitech International S.A.
> This project is an unofficial compatibility tool and is not affiliated with
> or endorsed by Logitech.
