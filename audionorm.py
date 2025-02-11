import os
import glob
import subprocess
import json

# -------------------
# Configuration
# -------------------
SOURCE_DIR = r"C:\Path\to\your\files"  # folder with .mp4 files
TARGET_LOUDNESS = -16.0
TARGET_LRA = 11.0
TARGET_TP = -1.5

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

    # --------------------------------------------------
    # PASS 1: Loudness analysis (no output file produced)
    # --------------------------------------------------
    analysis_filter = (
        f"loudnorm=I={TARGET_LOUDNESS}:LRA={TARGET_LRA}:TP={TARGET_TP}:print_format=json"
    )
    cmd_analysis = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-af", analysis_filter,
        "-f", "null",
        "-"  # sends processed output to null
    ]

    print(f"\nAnalyzing loudness for: {filename}")
    result = subprocess.run(cmd_analysis, capture_output=True, text=True)
    stderr_output = result.stderr

    # Look for the JSON block from loudnorm in stderr output
    json_start = stderr_output.find("{")
    json_end = stderr_output.rfind("}") + 1
    if json_start == -1 or json_end == 0:
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

    print(f"  Measured I={measured_I}, LRA={measured_LRA}, TP={measured_tp}, OFFSET={offset}")

    # --------------------------------------------------
    # PASS 2: Use measured values to normalize the audio
    # --------------------------------------------------
    # This is where we add the -map directives and specify -c:v copy, -c:a aac
    loudnorm_filter_pass2 = (
        f"loudnorm=I={TARGET_LOUDNESS}:LRA={TARGET_LRA}:TP={TARGET_TP}"
        f":measured_I={measured_I}:measured_LRA={measured_LRA}:measured_tp={measured_tp}"
        f":measured_thresh={measured_thresh}:offset={offset}"
        f":linear=true:print_format=summary"
    )

    output_path = os.path.join(OUTPUT_DIR, f"{name}_normalized{ext}")
    cmd_normalize = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        #
        # Here's where the main updates are:
        # * Explicitly map the first video track (-map 0:v:0)
        # * Explicitly map the first audio track (-map 0:a:0)
        # * Copy video as-is (-c:v copy)
        # * Re-encode audio to AAC (-c:a aac)
        #
        "-map", "0:v:0",
        "-map", "0:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-af", loudnorm_filter_pass2,
        output_path
    ]

    print(f"Normalizing: {filename} -> {os.path.basename(output_path)}")
    subprocess.run(cmd_normalize)

def main():
    mp4_files = glob.glob(os.path.join(SOURCE_DIR, "*.mp4"))
    if not mp4_files:
        print(f"No .mp4 files found in {SOURCE_DIR}")
        return

    for mp4_file in mp4_files:
        normalize_file(mp4_file)

if __name__ == "__main__":
    main()
