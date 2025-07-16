# Basler Camera Preview

A lightweight Python utility I put together for previewing live camera feeds from Basler IP cameras using OpenCV and the Pylon SDK. Automatically discovers all GigE Vision cameras on your network and provides a simple interface to switch between multiple camera feeds.

## Prerequisites

- Python 3.7+
- Basler Pylon SDK
- Python packages: `opencv-python`, `pypylon`

## Installation

1. Install Basler Pylon SDK from [Basler's website](https://www.baslerweb.com/en/software/pylon/)
2. Install Python dependencies:
   ```bash
   pip install opencv-python pypylon
   ```

## Usage

Run the script:
```bash
python basler_preview.py
```

**Controls:**
- **LEFT/RIGHT arrows**: Switch between cameras
- **ESC**: Exit

## Configuration

Modify these constants at the top of the script:
- `TIMEOUT_MS`: Grab timeout (default: 1000ms)
- `WANTED_PF`: Pixel format (default: "BayerRG8")
- `SCALE_FACTOR`: Display scaling (default: 1/3)
- `FPS`: Frame rate (default: 5fps)
