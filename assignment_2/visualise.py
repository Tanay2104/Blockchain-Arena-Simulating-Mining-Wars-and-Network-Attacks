# visualize.py
import graphviz

def visualize_blockchain_tree(blockchain_tree, filename='blockchain_tree'):
    """
    Generates a visualization of the blockchain tree using Graphviz.
    
    Args:
        blockchain_tree (BlockchainTree): The tree object to visualize.
        filename (str): The base name for the output file (e.g., 'blockchain_tree').
    """
    dot = graphviz.Digraph(comment='Blockchain Tree',format='png')

    # Get the longest chain to color nodes
    longest_chain_tip, _ = blockchain_tree.get_longest_chain()
    longest_chain_ids = set()
    current_block = longest_chain_tip
    while current_block is not None:
        longest_chain_ids.add(current_block.block_ID)
        if current_block.prev_block_ID is None:
            break
        current_block = blockchain_tree.tree_data.get(current_block.prev_block_ID)

    # Add all nodes and edges to the graph
    for block_id, block in blockchain_tree.tree_data.items():
        label = f"ID: {block.block_ID}\nMiner: {block.miner_ID}\nTime: {block.timestamp:.2f}"
        
        # Set node properties based on its type
        if block_id == blockchain_tree.genesis_block.block_ID:
            dot.node(str(block_id), label, shape='doubleoctagon', style='filled', fillcolor='purple', fontcolor='white')
        elif block_id in longest_chain_ids:
            dot.node(str(block_id), label, shape='box', style='filled', fillcolor='green')
        else: # Stale block
            dot.node(str(block_id), label, shape='box', style='filled', fillcolor='red')

        # Add an edge from the parent to the current block
        if block.prev_block_ID is not None:
            dot.edge(str(block.prev_block_ID), str(block.block_ID))
            
    # Render the graph to a file
    try:
        dot.render(filename, view=False, cleanup=True)
        print(f"Blockchain tree visualization saved to {filename}.png")
    except graphviz.backend.execute.ExecutableNotFound:
        print("Graphviz executable not found. Please install Graphviz and ensure it's in your system's PATH.")