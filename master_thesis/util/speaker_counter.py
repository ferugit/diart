import csv

hyperparameter = 'delta_new'  # Replace with your desired hyperparameter

filename = f"E:\\Code\\master_thesis\\5.22\\{hyperparameter}\\sample.rttm"  # Update the path to your file

# Read the file content
with open(filename, 'r') as file:
    file_content = file.read()

# Split the file content based on 'tau_active'
sections = file_content.split(hyperparameter)

# Initialize a dictionary to store the number of speakers for each tau_active
speaker_counts = {}

# Process each section
for section in sections[1:]:  # Skip the first empty section
    lines = section.strip().split('\n')
    tau_active_line = lines[0].strip(':')
    tau_active = float(tau_active_line.split('=')[1].strip().replace(':', ''))
    speakers = set()
    
    for line in lines[1:]:
        speaker = line.split()[-3]
        speakers.add(speaker)
    
    num_speakers = len(speakers)
    speaker_counts[tau_active] = num_speakers

# Find the maximum speaker number and add 1 to get the total number of speakers
max_speaker_num = max(map(int, [speaker.split('speaker')[1] for speaker in speakers])) + 1

data = [[hyperparameter, 'speakers']]
for tau_active, num_speakers in speaker_counts.items():
    data.append([tau_active, num_speakers])

# Write the data to a CSV file
output_filename = f'E:\\Code\\master_thesis\\5.22\\{hyperparameter}\\speaker_number.csv'  # Replace with your desired output file path
with open(output_filename, 'w+', newline='') as output_file:
    writer = csv.writer(output_file)
    writer.writerows(data)
