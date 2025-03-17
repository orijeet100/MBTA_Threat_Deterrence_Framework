import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import numpy as np


class GCNLayer(nn.Module):
    def __init__(self, in_channels, out_channels, dropout=0.5):
        super(GCNLayer, self).__init__()
        self.conv = GCNConv(in_channels, out_channels)
        self.dropout = dropout

    def forward(self, x, edge_index):
        edge_index = edge_index.t().contiguous() if edge_index.shape[0] != 2 else edge_index  # Ensure correct shape
        x = self.conv(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        return x


class GCN_LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, time_steps=9, gcn_dropout=0.5, lstm_dropout=0):
        super(GCN_LSTM, self).__init__()
        self.time_steps = time_steps

        self.gcn = GCNLayer(input_dim, hidden_dim, dropout=gcn_dropout)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True, dropout=lstm_dropout, num_layers=1)  # Fix dropout warning
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.final_dropout = nn.Dropout(lstm_dropout)

    def forward(self, x_seq, edge_index):
        embeddings = []
        for t in range(self.time_steps):
            x_t = x_seq[t]  # [num_nodes, input_dim]
            if len(x_t.shape) == 1:  # Fix shape if it's 1D
                x_t = x_t.unsqueeze(0)

            emb_t = self.gcn(x_t, edge_index)  # [num_nodes, hidden_dim]
            embeddings.append(emb_t.unsqueeze(1))  # Add time dimension -> [num_nodes, 1, hidden_dim]

        emb_seq = torch.cat(embeddings, dim=1)  # [num_nodes, time_steps, hidden_dim]
        lstm_out, _ = self.lstm(emb_seq)  # lstm_out: [num_nodes, time_steps, hidden_dim]
        lstm_out = self.final_dropout(lstm_out)

        predictions = self.fc(lstm_out)  # [num_nodes, time_steps, output_dim]
        return predictions


if __name__ == "__main__":
    input_dim = 12
    hidden_dim = 64
    output_dim = 1
    time_steps = 9
    gcn_dropout = 0.5
    lstm_dropout = 0.5

    model = GCN_LSTM(input_dim, hidden_dim, output_dim, time_steps, gcn_dropout, lstm_dropout)
    model.load_state_dict(torch.load('GCN_LSTM_weights.pth'))

    edge_index = np.genfromtxt('edge_index.csv', delimiter=',', dtype=int)
    edge_index = torch.tensor(edge_index.T, dtype=torch.long)  # Ensure correct shape

    features = torch.load('Original_Features.pth')

    model.eval()
    with torch.no_grad():
        test_predictions = model(features, edge_index)

    print("GCN-LSTM Predictions Shape:", test_predictions.shape)
