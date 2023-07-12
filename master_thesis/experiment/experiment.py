sample_file = "/home/azureuser/resources/audio"
sample_gt = "/home/azureuser/resources/gt"
output = "/home/azureuser/resources/output"

from optimizer import Optimizer

optimizer = Optimizer(sample_file, sample_gt, output, output)
optimizer(num_iter=100)