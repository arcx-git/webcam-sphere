# Third-Party Licenses

This project bundles or depends on the following third-party components.
All licenses listed below permit free redistribution under the stated conditions.

---

## 1. PySide6 (Qt for Python)

- **Upstream**: https://doc.qt.io/qtforpython-6/
- **License**: GNU Lesser General Public License v3.0 (LGPLv3) / Commercial (dual-licensed)
- **Usage**: Runtime dependency (GUI framework)

PySide6 and the underlying Qt libraries are used under the terms of the LGPLv3.
Redistribution is permitted provided that:

1. This notice and a copy of the LGPLv3 license text are included with any
   distribution.
2. End users retain the ability to replace the Qt/PySide6 libraries with a
   modified version (satisfied by shipping them as separate dynamic libraries,
   or by providing re-linking instructions for frozen bundles).
3. Any modifications made to PySide6 or Qt itself are released under LGPLv3.

Full license text: https://www.gnu.org/licenses/lgpl-3.0.txt

---

## 2. Qt 6 (underlying C++ framework)

- **Upstream**: https://www.qt.io/
- **License**: GNU Lesser General Public License v3.0 (LGPLv3) / Commercial
- **Usage**: Transitive dependency via PySide6

Same conditions as PySide6 above. Qt is The Qt Company Ltd.'s trademark.

---

## 3. PyInstaller

- **Upstream**: https://pyinstaller.org/
- **License**: GNU General Public License v2.0 **with a bootloader exception**
- **Usage**: Build-time tool (packaging only; not linked into the app logic)

The PyInstaller bootloader exception explicitly permits the distribution of
applications frozen with PyInstaller under **any license**, including
proprietary or closed-source licenses, without triggering GPL obligations on
the user's own application code.

Full license and exception text:
https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt

---

## 4. uvc-util

- **Upstream**: https://github.com/jtfrey/uvc-util
- **License**: MIT License
- **Usage**: Bundled source code (see `uvc-util/`), used to build `motor_final`
  which interacts with the Logitech Sphere UVC controls.

```
The MIT License (MIT)

Copyright (c) 2016 Jeffrey Frey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Trademarks

- "Logitech" and "Logitech Sphere" are trademarks of Logitech International S.A.
  This project is not affiliated with or endorsed by Logitech. References to
  the device are nominative use for compatibility description only.
- "Qt" is a trademark of The Qt Company Ltd.

---

## Summary

| Component    | License                         | Redistribution |
|--------------|---------------------------------|----------------|
| PySide6      | LGPLv3                          | Allowed w/ notice & re-link ability |
| Qt 6         | LGPLv3                          | Allowed w/ notice & re-link ability |
| PyInstaller  | GPL-2.0 + bootloader exception  | Allowed under any license |
| uvc-util     | MIT                             | Allowed w/ copyright notice |
