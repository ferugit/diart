def count_speaker_turns(rttm_file):
    with open(rttm_file, 'r') as file:
        lines = file.readlines()

    speaker_turns = 0
    previous_speaker = None

    for line in lines:
        if line.startswith('SPEAKER'):
            parts = line.split()
            speaker = parts[7]

            if previous_speaker and speaker != previous_speaker:
                speaker_turns += 1

            previous_speaker = speaker

    return speaker_turns

rttm_file = "../resources/sample.rttm"
turns = count_speaker_turns(rttm_file)
print("Number of speaker turns:", turns)
