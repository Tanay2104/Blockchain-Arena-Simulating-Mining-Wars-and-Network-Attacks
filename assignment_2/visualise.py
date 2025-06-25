import graphviz
import matplotlib.pyplot as plt
import numpy as np

def visualise_blockchain_tree(blockchain_tree, filename='blockchain_tree', title=None):
    dot = graphviz.Digraph(comment='Blockchain Tree',format='png')

    longest_chain_tip, _ = blockchain_tree.get_longest_chain()
    longest_chain_ids = set()
    current_block = longest_chain_tip
    while current_block is not None:
        longest_chain_ids.add(current_block.block_ID)
        if current_block.prev_block_ID is None:
            break
        current_block = blockchain_tree.tree_data.get(current_block.prev_block_ID)

    for block_id, block in blockchain_tree.tree_data.items():
        label = f"ID: {block.block_ID}\nMiner: {block.miner_ID}\nTime: {block.timestamp:.2f}"
        
        if block_id == blockchain_tree.genesis_block.block_ID:
            dot.node(str(block_id), label, shape='doubleoctagon', style='filled', fillcolor='purple', fontcolor='white')
        elif block_id in longest_chain_ids:
            dot.node(str(block_id), label, shape="box", style='filled', fillcolor='green')
        else:
            dot.node(str(block_id), label, shape='box', style='filled', fillcolor='red')

        if block.prev_block_ID is not None:
            dot.edge(str(block.prev_block_ID), str(block.block_ID))
            
    try:
        dot.graph_attr['label'] = f'{title}\n'
        dot.render(filename, view=False, cleanup=True)
        print(f"Blockchain tree visualization saved to {filename}.png")
    except graphviz.backend.execute.ExecutableNotFound:
        print("Graphviz executable not found. Please install Graphviz and ensure it's in your system's PATH.")


def visualise_wealth_distribution(final_tree, all_peers, filename='wealth_distribution.png', title=''):
    print("Generating wealth distribution plot...")
    
    peer_ids = []
    balances = []

    longest_chain_tip, _ = final_tree.get_longest_chain()
    
    sorted_peers = sorted(all_peers.values(), key=lambda p: p.ID)

    for peer in sorted_peers:
        balance = final_tree.calculate_balance(peer.ID, longest_chain_tip.block_ID)
        if peer.is_slow:
            speed='slow_net'
        else:
            speed='fast_net'
        if peer.is_low_CPU:
            power = 'low_power'
        else:
            power = 'high_power'

        peer_ids.append(f'{peer.ID}, {speed}, {power}')
        balances.append(balance)

    plt.figure(figsize=(12, 7))
    plt.bar(peer_ids, balances, color='gold', edgecolor='black')
    
    plt.xlabel("Peer ID")
    plt.ylabel("Final Coin Balance")
    plt.title(f"Final Wealth Distribution\n{title}")
    plt.xticks(peer_ids, rotation=45, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    plt.savefig(filename)
    plt.close()
    print(f"Wealth distribution visualization saved as {filename}")


def visualise_miner_efficiency(final_tree, all_peers, filename='miner_efficiency.png', title=''):
    print("Generating miner efficiency plot...")

    longest_chain_tip, _ = final_tree.get_longest_chain()
    longest_chain_ids = set()
    current_block = longest_chain_tip
    while current_block is not None:
        longest_chain_ids.add(current_block.block_ID)
        if current_block.prev_block_ID is None:
            break
        current_block = final_tree.tree_data.get(current_block.prev_block_ID)

    miner_stats = {}
    for peer_id, peer in all_peers.items():
        miner_stats[peer_id] = {
            'total_mined': 0,
            'on_chain': 0,
            'efficiency': 0.0,
            'is_low_cpu': peer.is_low_CPU,
            'is_slow': peer.is_slow
        }
    
    for block in final_tree.tree_data.values():
        if block.miner_ID is not None:
            miner_stats[block.miner_ID]['total_mined'] += 1
            if block.block_ID in longest_chain_ids:
                miner_stats[block.miner_ID]['on_chain'] += 1

    categories = {
        'High CPU / Fast Link': {'ids': [], 'on_chain': [], 'total': []},
        'High CPU / Slow Link': {'ids': [], 'on_chain': [], 'total': []},
        'Low CPU / Fast Link': {'ids': [], 'on_chain': [], 'total': []},
        'Low CPU / Slow Link': {'ids': [], 'on_chain': [], 'total': []}
    }

    for peer_id, stats in miner_stats.items():
        if stats['total_mined'] > 0:
            stats['efficiency'] = stats['on_chain'] / stats['total_mined']
        
        if not stats['is_low_cpu'] and not stats['is_slow']:
            cat = 'High CPU / Fast Link'
        elif not stats['is_low_cpu'] and stats['is_slow']:
            cat = 'High CPU / Slow Link'
        elif stats['is_low_cpu'] and not stats['is_slow']:
            cat = 'Low CPU / Fast Link'
        else:
            cat = 'Low CPU / Slow Link'

        categories[cat]['ids'].append(peer_id)
        categories[cat]['on_chain'].append(stats['on_chain'])
        categories[cat]['total'].append(stats['total_mined'])

    plt.figure(figsize=(14, 8))
    
    n_categories = len(categories)
    bar_width = 0.35
    index = np.arange(len(all_peers))

    peer_id_map = {peer_id: i for i, peer_id in enumerate(sorted(all_peers.keys()))}
    
    colors = {'on_chain': 'limegreen', 'stale': 'tomato'}
    plotted_total = set()

    for category, data in categories.items():
        if not data['ids']: continue
        
        cat_indices = [peer_id_map[pid] for pid in data['ids']]
        
        stale_blocks = [total - on_chain for total, on_chain in zip(data['total'], data['on_chain'])]

        plt.bar(cat_indices, stale_blocks, bar_width, color=colors['stale'], label='Stale Blocks' if 'stale' not in plotted_total else "")
        plt.bar(cat_indices, data['on_chain'], bar_width, bottom=stale_blocks, color=colors['on_chain'], label='On-Chain Blocks' if 'on_chain' not in plotted_total else "")
        plotted_total.add('stale')
        plotted_total.add('on_chain')

    plt.xlabel('Peer ID')
    plt.ylabel('Number of Blocks Mined')
    plt.title(f'Miner Success and Efficiency by Peer Type\n{title}')
    plt.xticks(index, sorted(all_peers.keys()), rotation=90)
    plt.legend()
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()
    print(f"Miner efficiency visualization saved to {filename}")