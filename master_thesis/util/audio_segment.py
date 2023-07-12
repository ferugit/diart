import subprocess
import os
from pathlib import Path

input_audio = "../resources/sample.wav"    # Path to input audio file
rttm_file = "..resources/sample.rttm"      # Path to RTTM file
output_dir = "../resources/output/"    # Path to output directory

# Segments the input audio file into separate audio files based on the RTTM file.
def seg():
    with open(rttm_file, 'r') as file:
        segment_count = {}
        for line in file:
            line_parts = line.strip().split()
            speaker_id = line_parts[7]         # Extract the speaker ID from the line
            start_time = float(line_parts[3])  # Extract the start time from the line
            duration = float(line_parts[4])    # Extract the duration from the line

            if speaker_id in segment_count:
                segment_count[speaker_id] += 1
            else:
                segment_count[speaker_id] = 1

            segment_id = segment_count[speaker_id]
            os.makedirs(f"{output_dir}/{speaker_id}", exist_ok=True)
            output_file = os.path.join(f"{output_dir}/{speaker_id}", f"segment_{speaker_id}_{segment_id:02d}.wav")
            # ffmpeg
            subprocess.run(["ffmpeg", "-i", input_audio, "-ss", str(start_time), "-t", str(duration), "-c", "copy", output_file])

    print("Segmentation completed.")

# Concatenates the audio files in each folder into a single audio file.
def concatenate():
    audios_folder = Path(output_dir)

    # iterate through each folder in the output directory
    for path in audios_folder.glob("*"):
        # if the folder has a concat.txt file, remove it
        if(os.path.exists(f"{path}/concat.txt")):
            os.remove(f"{path}/concat.txt")

        # iterate through each audio file in the folder and add it to the concat.txt file
        with open(f"{path}/concat.txt", "a") as f:
            for audio in path.glob("*.wav"):
                f.write(f"file '{audio}'\n")

        # use ffmpeg to concatenate the files in the concat.txt file
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", f"{path}/concat.txt", "-c", "copy", f"{path}/concatenated.wav"])
        
        # remove the concat.txt file
        os.remove(f"{path}/concat.txt")

if __name__ == "__main__":
    seg()     
    concatenate()
    