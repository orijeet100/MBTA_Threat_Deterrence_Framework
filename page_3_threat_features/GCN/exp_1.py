import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from numpy import genfromtxt

# Load and inspect edge_index.csv
edge_index = genfromtxt('edge_index.csv', delimiter=',')
edge_index = torch.tensor(edge_index, dtype=torch.int)


print("Edge Index Shape:", edge_index.shape)
print("Edge Index Sample:\n", edge_index[:5])  # Print first 5 rows

# Load and inspect GCN_LSTM_weights.pth
weights_path = "GCN_LSTM_weights.pth"
model_weights = torch.load(weights_path, map_location=torch.device('cpu'))
print("\nGCN-LSTM Model Weights Keys:", model_weights.keys())

# Load and inspect Original_Features.pth
features_path = "Original_Features.pth"
features = torch.load(features_path, map_location=torch.device('cpu'))
print("\nOriginal Features Shape:", features.shape if isinstance(features, torch.Tensor) else type(features))
if isinstance(features, torch.Tensor):
    print("Original Features Sample:\n", features[:5])  # Print first 5 rows if it's a tensor
