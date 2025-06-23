class BlockchainTree():
    def __init__(self, genesis_block):
        self.genesis_block = genesis_block #Genesis block will give the initial bitcoins(say 100) to everyone
        self.tree_data = {
            genesis_block.block_ID : genesis_block,
        }
        pass
    def add_block(self, block):
        self.tree_data[block.block_ID] = block
        self.tree_data[block.prev_block_ID].has_successor = True

    def get_longest_chain(self):
        childless_block_chain_lengths = {}
        for block in self.tree_data.values():
            if not block.has_successor:
                childless_block_chain_lengths[block] = 1
                current_block_ID = block.block_ID
                while current_block_ID != self.genesis_block.block_ID:
                    current_block_ID = self.tree_data[current_block_ID].prev_block_ID
                    childless_block_chain_lengths[block]+=1
        
        return max(childless_block_chain_lengths, key=childless_block_chain_lengths.get), max(childless_block_chain_lengths.values())

    def calculate_balance(self, peer_ID, chain_end_block_ID):
        current_block_ID = chain_end_block_ID
        net_balance = 0
        while True:
            net_balance+=self.tree_data[current_block_ID].get_net_transaction(peer_ID)
            if  current_block_ID == self.genesis_block.block_ID:
                return net_balance
            current_block_ID = self.tree_data[current_block_ID].prev_block_ID

    def visualise():
        pass