import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from numpy import genfromtxt


class GCNLayer(nn.Module):
    def __init__(self, in_channels, out_channels, dropout=0.5):
        super(GCNLayer, self).__init__()
        self.conv = GCNConv(in_channels, out_channels)
        self.dropout = dropout

    def forward(self, x, edge_index):
        x = self.conv(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        return x


class GCN_LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, time_steps=9, gcn_dropout=0.5, lstm_dropout=0.5):
        super(GCN_LSTM, self).__init__()
        self.time_steps = time_steps

        self.gcn = GCNLayer(input_dim, hidden_dim, dropout=gcn_dropout)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True, dropout=lstm_dropout)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.final_dropout = nn.Dropout(lstm_dropout)

    def forward(self, x_seq, edge_index):
        embeddings = []
        for t in range(self.time_steps):
            x_t = x_seq[t]  # [num_nodes, input_dim]
            emb_t = self.gcn(x_t, edge_index)  # [num_nodes, hidden_dim]
            embeddings.append(emb_t.unsqueeze(1))  # Add time dimension -> [num_nodes, 1, hidden_dim]

        emb_seq = torch.cat(embeddings, dim=1)
        lstm_out, _ = self.lstm(emb_seq)  # lstm_out: [num_nodes, time_steps, hidden_dim]
        lstm_out = self.final_dropout(lstm_out)

        predictions = self.fc(lstm_out)
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

    edge_index = genfromtxt('edge_index.csv', delimiter=',')
    edge_index = torch.tensor(edge_index, dtype=torch.int)

    features = torch.load('Original_Features.pth')

    model.eval()
    with torch.no_grad():
        test_predictions = model(features, edge_index)

