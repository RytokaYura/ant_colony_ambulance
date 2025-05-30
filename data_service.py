import pandas as pd
import numpy as np

class DataService:
    def __init__(self, data_source):
        self.data_source = data_source

    def fetch_data(self, query):
        df = pd.read_excel(query)
        df = df.fillna(np.inf)
        print(df.head(17))
        return df
    
    @staticmethod
    def get_node_indices(data):
        nodes = data.iloc[:, 0].to_list()
        print(f"Nodes: {nodes}")
        return {name: idx for idx, name in enumerate(nodes)}
    
    @staticmethod
    def get_distance(data, node_indices, traffic_settings):
        distance_matrix = data.iloc[:, 3:].to_numpy()
        traffic_factors = np.ones_like(distance_matrix)

        for asal, tujuan, faktor in traffic_settings:
            if asal in node_indices and tujuan in node_indices:
                i = node_indices[asal]
                j = node_indices[tujuan]
                traffic_factors[i][j] = faktor
                traffic_factors[j][i] = faktor

        return distance_matrix * traffic_factors

