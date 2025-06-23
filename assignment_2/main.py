# main.py
from simulator import Simulator
from visualise import visualize_blockchain_tree # Import your new function

if __name__ == '__main__':
    # ... your simulator parameters ...
    sim = Simulator(n=200, z_0=0.2, z_1=0.01, Ttx=5, inter_arrival_time = 100)
    sim.run(runtime=10000)

    # After the simulation is done, get the final tree from any peer
    # (they should all have a similar view of the history, but the one
    # with the longest chain is a good representative).
    final_tree = sim.network.get_peer(0).blockchain_tree
    for peer in sim.network.all_peers.values():
         if len(peer.blockchain_tree.tree_data) > len(final_tree.tree_data):
              final_tree = peer.blockchain_tree

    visualize_blockchain_tree(final_tree)
    # ... call your other visualization functions for balances, etc. ...