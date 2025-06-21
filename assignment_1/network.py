import networkx as nx
import matplotlib.pyplot as plt

class Network:
    def __init__(self, n):
        n_k6 = n % 6
        n_k5 = (n//6 - n%6)
        # Now n_k5*6 + n_k6*7 = n*(n//6) - 6*n%6 + 7*n%6 = n*(n//6) + n%6 = n
        # This means that every number greater than 30 can be written as 6*n1 + 7*n2. Since the number of peers in problem statement >= 50, hence this is satisfied

        k6 = [nx.relabel_nodes(nx.complete_graph(6), 
                               {0: f'U{i}', 1: f'V{i}', 2: f'W{i}', 3: f'X{i}', 4: f'Y{i}', 5: f'Z{i}'}) 
                               for i in range(n_k6)]
        k5 = [nx.relabel_nodes(nx.complete_graph(5), 
                               {0: f'A{i}', 1: f'B{i}', 2: f'C{i}', 3: f'D{i}', 4: f'E{i}',}) 
                               for i in range(n_k5)]
        
        ring = nx.cycle_graph(n_k5 + n_k6)
        ring_connectors = nx.from_edgelist([(f'U{i}', i) for i in range(n_k6)]+[(f'A{i}', i+n_k6) for i in range(n_k5)])
        self.network = nx.compose_all(k5 + k6 + [ring_connectors, ring])  
        
    def check_validity(self):
        is_connected = nx.is_connected(self.network)

        is_degree_correct = True 
        for node, d in self.network.degree:
            if d < 3 or d > 6:
                is_degree_correct = False
                print(f"Network has degree {d} at node {node}")

        return is_connected and is_degree_correct
    
    def display(self, filename = 'network.png'):
        nx.draw_random(self.network, with_labels=True)
        plt.show()
        plt.savefig(filename)
        print(f"Network visualization saved to {filename}")