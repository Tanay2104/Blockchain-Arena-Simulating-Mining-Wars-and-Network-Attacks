# main.py
from simulator import Simulator
from visualise import *

if __name__ == '__main__':
    number_of_peers = 20
    low_speed_fraction = 0.6
    low_cpu_fraction = 0.1
    transaction_frequency = 1
    interarrival_time = 20
    runtime = 500
    sim = Simulator(n=number_of_peers, z_0=low_speed_fraction, z_1=low_cpu_fraction, 
                    Ttx=transaction_frequency, inter_arrival_time = interarrival_time)
    sim.run(runtime=runtime)


    final_tree = sim.network.get_peer(0).blockchain_tree
    for peer in sim.network.all_peers.values():
         if len(peer.blockchain_tree.tree_data) > len(final_tree.tree_data):
              final_tree = peer.blockchain_tree

    plot_title = f'n={number_of_peers}, z₀={low_speed_fraction}, z₁={low_cpu_fraction}, Ttx={transaction_frequency}, I={interarrival_time}'

    visualise_blockchain_tree(final_tree, 
                              filename=f'blockchain_tree', 
                              title=plot_title)

    visualise_wealth_distribution(final_tree, 
                                  sim.network.all_peers, 
                                  filename='wealth_distribution', 
                                  title=plot_title)

    visualise_miner_efficiency(final_tree, 
                               sim.network.all_peers, 
                               filename='miner_efficiency', 
                               title=plot_title)
