from diart import PipelineConfig, OnlineSpeakerDiarization
from diart.sources import FileAudioSource
from diart.inference import RealTimeInference
from diart.sinks import RTTMWriter

import subprocess
subprocess.run(["arecord", "-d", "90", "-Dac108", "-f", "S32_LE", "-r", "16000", "-c", "1", "test.wav"])

config = PipelineConfig(step=1, tau_active=0.717, rho_update=0.466, delta_new=0.875)
pipeline = OnlineSpeakerDiarization(config)
file = FileAudioSource("/home/pi/test.wav", 16000)
inference = RealTimeInference(pipeline, file, batch_size=1, do_plot=False)
inference.attach_observers(RTTMWriter("sample", "/home/pi/code/resources/rttm/sample_presentation.rttm"))

import time
start = time.time()
# --------------------------------
prediction = inference()
# --------------------------------
stop = time.time()
print("Time: ", stop - start)

import util.audio_segment as asg
asg.seg()
asg.concatenate()
