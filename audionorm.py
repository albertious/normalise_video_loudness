import os
import glob
import subprocess
import json

# -------------------
# Configuration
# -------------------
SOURCE_DIR = r"C:\Working Files\ALAN PRODUCTION\2025\Production of Space Twitch Stream Finder\vids"  # Change this to where your .mp4 files live
TARGET_LOUDNESS = -16.0
TARGET_LRA = 11.0
TARGET_TP = -1.5

# Where to place normalized files
# (You can set it to SOURCE_DIR if you want them in the same folder, but be aware of overwriting)
OUTPUT_DIR = os.path.join(SOURCE_DIR, "normalized")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def normalize_file(input_path):
    """
    Perform two-pass loudnorm on a single .mp4 file:
     1) Analyze loudness (first pass)
     2) Use measured values to normalize audio (second pass)
    """

    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)

    # 1) Loudness analysis (pass 1)
    #    We use `-f null -` to avoid writing an output; the stats are printed in stderr as JSON.
    analysis_filter = f"loudnorm=I={TARGET_LOUDNESS}:LRA={TARGET_LRA}:TP={TARGET_TP}:print_format=json"
    cmd_analysis = [
        "ffmpeg",
        "-y",               # overwrite output
        "-i", input_path,
        "-af", analysis_filter,
        "-f", "null",
        "-"                 # Send output to null
    ]

    print(f"Analyzing loudness for: {filename}")
    result = subprocess.run(cmd_analysis, capture_output=True, text=True)
    stderr_output = result.stderr

    # Extract the JSON block from FFmpeg's stderr (the loudnorm stats appear at the very end).
    # They typically appear in the form:
    # {
    #     "input_i" : "-19.5",
    #     "input_tp" : "-4.2",
    #     ...
    # }
    json_start = stderr_output.find("{")
    json_end = stderr_output.rfind("}") + 1
    if json_start == -1 or json_end == -1:
        print(f"Could not find JSON in FFmpeg output for file: {filename}")
        return

    json_str = stderr_output[json_start:json_end]
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        print(f"Error parsing JSON loudnorm data for file: {filename}")
        return

    measured_I = data["input_i"]
    measured_LRA = data["input_lra"]
    measured_tp = data["input_tp"]
    measured_thresh = data["input_thresh"]
    offset = data["target_offset"]

    print(f"  Measured values: I={measured_I}, LRA={measured_LRA}, TP={measured_tp}, OFFSET={offset}")

    # 2) Normalize using the measured values (pass 2)
    #    We provide them back to loudnorm for a more accurate second pass.
    #    linear=true ensures a linear gain across the entire file (rather than dynamic).
    loudnorm_filter_pass2 = (
        f"loudnorm=I={TARGET_LOUDNESS}:LRA={TARGET_LRA}:TP={TARGET_TP}"
        f":measured_I={measured_I}:measured_LRA={measured_LRA}:measured_tp={measured_tp}"
        f":measured_thresh={measured_thresh}:offset={offset}"
        f":linear=true:print_format=summary"
    )

    # Construct output path
    output_path = os.path.join(OUTPUT_DIR, f"{name}_normalized{ext}")
    cmd_normalize = [
        "ffmpeg",
        "-y",                 # overwrite if file exists
        "-i", input_path,
        "-c:v", "copy",       # copy video without re-encoding
        "-af", loudnorm_filter_pass2,
        output_path
    ]

    print(f"Normalizing: {filename} -> {os.path.basename(output_path)}")
    subprocess.run(cmd_normalize)

def main():
    # Find all MP4 files in SOURCE_DIR
    mp4_files = glob.glob(os.path.join(SOURCE_DIR, "*.mp4"))
    if not mp4_files:
        print(f"No .mp4 files found in {SOURCE_DIR}")
        return

    for mp4_file in mp4_files:
        normalize_file(mp4_file)

if __name__ == "__main__":
    main()
