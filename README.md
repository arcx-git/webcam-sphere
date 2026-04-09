# Logitech Sphere Controller

macOS에서 Logitech QuickCam Sphere (046d:0994)의 **팬/틸트 모터**를 제어하는 GUI 앱.

## 기능

- 상/하/좌/우 팬/틸트 제어 (D-pad 버튼 + 키보드 방향키)
- 버튼 누르고 있으면 연속 이동 (C 네이티브 스레드, 30ms 간격)
- 스텝 크기 조절 (2°~10°)
- Reset으로 중앙 복귀 (Space / R 키)
- 앱 버전 및 빌드 날짜 표시
- 웹캠 렌즈 스타일 앱 아이콘

## 요구사항

- macOS (IOKit 기반 USB 제어)
- Logitech QuickCam Sphere (USB VID:PID 046d:0994)
- Python 3.12+, uv
- Xcode Command Line Tools (`clang`)

## 설치 및 빌드

```bash
# 1. 의존성 설치
uv sync

# 2. 모터 제어 바이너리 빌드
clang -framework Foundation -framework IOKit -framework AppKit -fno-objc-arc -lpthread \
  uvc-util/src/UVCController.m uvc-util/src/UVCType.m uvc-util/src/UVCValue.m \
  motor_final.m -o motor_final -I uvc-util/src

# 3. 실행 (개발 모드)
uv run python sphere_controller.py

# 4. 독립 실행 앱 빌드 (.app)
BUILD_DATE=$(date +%Y-%m-%d) uv run pyinstaller \
  --name "Sphere Controller" --onefile --windowed \
  --add-binary "motor_final:." --icon icon.icns \
  --noconfirm sphere_controller.py
rm -rf build "Sphere Controller.spec"
# -> dist/Sphere Controller.app 생성
```

## 사용법

### GUI 버튼
| 버튼 | 동작 |
|------|------|
| Up (초록) | 틸트 위 |
| Down (초록) | 틸트 아래 |
| Left (파랑) | 팬 왼쪽 |
| Right (파랑) | 팬 오른쪽 |
| Reset (빨강) | 중앙 복귀 |

### 키보드
| 키 | 동작 |
|----|------|
| 방향키 | 팬/틸트 (누르고 있으면 연속 이동) |
| Space / R | Reset (중앙 복귀) |

### CLI (motor_final 직접 사용)
```bash
./motor_final right 5     # 오른쪽 5도
./motor_final left 10     # 왼쪽 10도
./motor_final up 3        # 위 3도
./motor_final down 3      # 아래 3도
./motor_final reset       # 중앙 복귀
./motor_final --daemon    # 데몬 모드 (GUI에서 사용)
```

## 프로젝트 구조

```
sphere_controller.py   # GUI 앱 (PySide6)
motor_final.m          # 모터 제어 소스 (Objective-C, IOKit)
motor_final            # 빌드된 모터 제어 바이너리
uvc-util/              # UVC 컨트롤러 라이브러리 (jtfrey/uvc-util)
icon.png               # 앱 아이콘 (512x512 웹캠 렌즈)
icon.icns              # macOS용 앱 아이콘
pyproject.toml         # Python 의존성 (PySide6, PyInstaller)
dist/                  # 빌드된 .app
```

## 기술 상세

### UVC Extension Unit 프로토콜

Logitech Sphere는 표준 UVC PTZ가 아닌 **벤더 전용 Extension Unit**으로 모터를 제어한다.

| 항목 | 값 |
|------|-----|
| GUID | `{63610682-5070-49ab-b8cc-b3855e8d2256}` |
| Unit ID | 9 |
| Selector 1 | Pan/Tilt Relative (4바이트, signed int16 LE x2) |
| Selector 2 | Pan/Tilt Reset (1바이트, 0x03=양쪽 리셋) |
| Selector 3 | Focus Motor (6바이트) |
| 단위 | 64 = 1도 |

### 아키텍처

```
[GUI (Python/PySide6)]
    |  stdin pipe (move/stop/reset)
    v
[motor_final --daemon (Objective-C)]
    |  C pthread (30ms tick)
    v
[IOKit USB Control Transfer]
    |  UVC Extension Unit (Unit 9, Selector 1)
    v
[Logitech Sphere Motor]
```

- GUI는 `move <pan> <tilt>` / `stop` 명령만 파이프로 전송
- C 데몬 내부 스레드가 30ms 간격으로 USB 명령을 반복 전송하여 부드러운 이동 구현
- 프로세스 재시작 오버헤드 없음 (상주 데몬)

## 라이선스

본 프로젝트는 [MIT License](LICENSE)로 배포된다.

### 서드파티 컴포넌트

| 컴포넌트 | 라이선스 | 용도 |
|---------|---------|------|
| [PySide6](https://doc.qt.io/qtforpython-6/) | LGPLv3 | GUI 프레임워크 |
| [Qt 6](https://www.qt.io/) | LGPLv3 | PySide6 기반 라이브러리 |
| [PyInstaller](https://pyinstaller.org/) | GPL-2.0 + bootloader exception | 앱 패키징 |
| [uvc-util](https://github.com/jtfrey/uvc-util) | MIT | UVC 컨트롤러 라이브러리 (번들) |

전체 고지 및 원문은 [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) 참조.

> "Logitech" 및 "Logitech Sphere"는 Logitech International S.A.의 상표이며,
> 본 프로젝트는 Logitech과 무관한 비공식 호환 도구이다.
