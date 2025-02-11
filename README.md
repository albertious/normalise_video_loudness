# Loudness Normalizer (Two-Pass EBU R128)

This Python script normalizes the loudness of `.mp4` videos using FFmpeg’s [loudnorm](https://ffmpeg.org/ffmpeg-all.html#loudnorm) filter. It implements a **two-pass** workflow:

1. **Analyze** each file’s loudness (pass 1)  
2. **Apply** the loudness normalization (pass 2)  

The resulting files have more consistent perceived volume and adhere to EBU R128 recommendations.

---

## Features

- **Two-Pass Normalization**  
  Accurately measures audio loudness, then applies precise gain adjustments for best results.

- **Video Stream Copy**  
  The video is not re-encoded (`-c:v copy`), so there’s no loss of video quality.

- **Batch Processing**  
  Automatically processes all `.mp4` files in the specified source directory.

- **Configurable Targets**  
  Adjust `TARGET_LOUDNESS` (integrated LUFS), `TARGET_LRA` (loudness range), and `TARGET_TP` (true peak) to suit your requirements.

---

## Requirements

1. **Python 3.6+**  
   - You can check your version with `python --version` (Windows) or `python3 --version` (macOS/Linux).
2. **FFmpeg** (in your system PATH)  
   - Verify with `ffmpeg -version`.
3. **A folder with `.mp4` files** that you want to normalize.

---

## Installation

1. **Clone or download** this repository.  
2. **Install FFmpeg** if not already installed:
   - [Download FFmpeg](https://ffmpeg.org/download.html) or use a package manager like [Homebrew](https://brew.sh/) (macOS) or [Chocolatey](https://chocolatey.org/) (Windows).
3. *(Optional)* Create and activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html) for your Python project.

---

# Configuration

# -------------------
# Configuration
# -------------------
- SOURCE_DIR = r"C:\Path\to\your\files"
- TARGET_LOUDNESS = -16.0
- TARGET_LRA = 11.0
- TARGET_TP = -1.5
- **`SOURCE_DIR`**: Path to your folder of `.mp4` files.  
- **`TARGET_LOUDNESS (I)`**: Integrated loudness target in LUFS (commonly between -23 and -14).  
- **`TARGET_LRA`**: Loudness Range limit in LU.  
- **`TARGET_TP`**: True peak limit in dBFS.

The script also creates a subdirectory called `normalized` inside `SOURCE_DIR` to store normalized outputs.  
If you want to overwrite the source files or use a different path, change `OUTPUT_DIR` accordingly.

## Usage

1. **Place** all `.mp4` files to be normalized in the specified `SOURCE_DIR`.  
2. **Run** the script:
   ```bash
   python normalize_loudness.py
3. Check the `normalized` subfolder for your new, loudness-normalized `.mp4` files. Each file’s name will have `_normalized` appended before the extension.

## How It Works

1. **First Pass (Analysis)**  
   The script calls FFmpeg with `loudnorm=...:print_format=json -f null -` to measure the file’s loudness, loudness range, true peak, and offset.

2. **Extract JSON**  
   The script extracts the loudnorm analysis from FFmpeg’s stderr in JSON format.

3. **Second Pass (Apply)**  
   The script feeds the measured values back into the `loudnorm` filter for accurate gain adjustment, copying the video stream (`-c:v copy`) to avoid re-encoding.

# Troubleshooting

- **Could not find JSON in FFmpeg output**  
  - Ensure FFmpeg is up to date.
  - Check that the file is a valid `.mp4` with an audio track.

- **No `.mp4` files found**  
  - Verify the `SOURCE_DIR` path is correct and that `.mp4` files exist.

- **Permission Errors**  
  - Run the script with proper permissions.
  - Check read/write access to `SOURCE_DIR`.
