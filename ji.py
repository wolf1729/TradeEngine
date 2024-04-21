import torch

cuda_available = torch.cuda.is_available()
if cuda_available:
    cuda_version = torch.version.cuda
    print("CUDA Version:", cuda_version)
else:
    print("CUDA is not available.")
