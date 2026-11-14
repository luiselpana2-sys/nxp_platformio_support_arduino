# NXP MCX PlatformIO v0.4 (experimental)

Supports FRDM-MCXA153, FRDM-MCXA156, FRDM-MCXN947, FRDM-MCXN236, and FRDM-MCXC444. This installation includes all five variant source trees from mcx-arduino-core 0.10.0.

## Install Variants

If restoring the platform from a clean copy, install variants from an mcx-arduino-core 0.10.0 checkout. The installer accepts the repository root and its Arduino hardware layout. In PowerShell:

```powershell
git clone https://github.com/teddokano/mcx-arduino-core.git
python scripts/install_variants.py "C:/path/to/mcx-arduino-core"
```

Or use the directory containing `variants/` from your Arduino installation. This script copies only variants; it does not alter your original checkout.

## Use

```ini
[env:frdm_mcxa153]
platform = C:/path/to/nxpmcx-platform-v0.4
board = frdm_mcxa153
framework = arduino
upload_protocol = linkserver
```

Replace board with `frdm_mcxa156`, `frdm_mcxn947`, `frdm_mcxn236`, or `frdm_mcxc444`. `upload.py` selects the LinkServer target from board JSON. Set LINKSERVER_EXE if auto-discovery fails.

## Important

The Blink smoke test builds for all five board definitions. Hardware uploads have not been verified. The adapter omits unused `<iostream>` and `<iomanip>` includes from `r01lib.h`; linking those stream headers pulls in a C++ runtime too large for the A153 and C444 flash sizes. The core's original `platform.txt` and `boards.txt` remain the reference for board flags and memory limits.
