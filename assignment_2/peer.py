from blockchain_tree import BlockchainTree

class Peer():
    def __init__(self, ID, genesis_block, is_slow=False, is_low_CPU=False, initial_extra_balance=0, hashing_powers=None):
        self.ID = ID
        self.is_slow=is_slow
        self.is_low_CPU = is_low_CPU
        self.hashing_power = hashing_powers[0] if is_low_CPU else hashing_powers[1]
        self.wallet_balance = initial_extra_balance
        self.blockchain_tree = BlockchainTree(genesis_block)
        pending_transactions = None
        known_messages = None
        current_mining_event = None
        