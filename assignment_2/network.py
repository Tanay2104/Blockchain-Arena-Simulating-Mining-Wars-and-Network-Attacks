import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from peer import Peer

class Network:
    def __init__(self, n, z_0_slow, z_1_low_CPU, genesis_block):
        self.all_peers = set()
        #z1*n*low_hashing + (1-z1)*10*n*low_hashing = 1
        #low_hashing(nz1 + 10(1-z1)n) = 1
        #low_hashing(10n -9z1n) = 1
        #low_hashing = 1/(n*(10-9z1))
        low_hashing_power = 1/(n*(10-9*z_1_low_CPU))
        high_hashing_power = 1/(n)
        for i in range(n):
            peer = Peer(ID=i,genesis_block=genesis_block, is_slow=(np.random.random() < z_0_slow), 
                        is_low_CPU=(np.random.random() < z_1_low_CPU), hashing_powers=(low_hashing_power, high_hashing_power))
            self.all_peers.add(peer)

        self.network = nx.Graph()

        self.network.add_nodes_from(self.all_peers)

    def build_connections(self):
        all_peers = list(self.all_peers)
        for peer in all_peers:
            k = np.random.randint(3, 7)
            while self.network.degree(peer) < k:
                peer2 = np.random.choice(all_peers)
                if (peer2 != peer) and (not self.network.has_edge(peer, peer2)) and (self.network.degree(peer2) < 6):
                    self.network.add_edge(peer, peer2)
                    #print(f"Added edge between {peer} and {peer2}")

    def check_validity(self):
        is_connected = nx.is_connected(self.network)

        is_degree_correct = True 
        for node, d in self.network.degree:
            if d < 3 or d > 6:
                is_degree_correct = False
                print(f"Network has degree {d} at node {node}")

        return is_connected and is_degree_correct
    
    def display(self, filename = 'network.png'):
        nx.draw_random(self.network, with_labels=False)
        plt.show()
        plt.savefig(filename)
        print(f"Network visualisation saved to {filename}")

    def build_network(self):
        while True:
            self.network.remove_edges_from(list(self.network.edges()))
            self.build_connections()
            is_valid = self.check_validity()
            if is_valid:
                print("Network is valid")
                break
        
        return self.network
    
# network = Network(50, 0.05, 0.2)
# network.build_network()
# network.display()