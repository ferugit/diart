from libraries import Benchmark
from diart import OnlineSpeakerDiarization, PipelineConfig

sample_file = "/home/azureuser/resources/audio"
sample_gt = "/home/azureuser/resources/gt"
output = "/home/azureuser/resources/output"

benchmark = Benchmark(sample_file, sample_gt, output)

config = PipelineConfig(
    tau_active=0.3,
)
# benchmark(OnlineSpeakerDiarization, config)

if __name__ == "__main__":
    benchmark(OnlineSpeakerDiarization, config)
