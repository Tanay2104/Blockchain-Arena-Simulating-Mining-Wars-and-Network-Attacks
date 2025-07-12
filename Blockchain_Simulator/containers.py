class Event():
    def __init__(self, timestamp, type, target_peer_ID, data=None):
        self.timestamp = timestamp
        self.type = type
        self.target_peer_ID = target_peer_ID
        self.data = data
    
    def __lt__(self, other):
        return self.timestamp < other.timestamp

class Transaction():
    def __init__(self, txn_ID, sender_ID, reciever_ID, amount):
        self.txn_ID = txn_ID
        self.sender_ID = sender_ID
        self.reciever_ID = reciever_ID
        self.amount = amount
        self.transaction_size_kb = 1

class Block():
    def __init__(self, block_ID, prev_block_ID, miner_ID, timestamp, transactions=None):
        self.block_ID = block_ID
        self.prev_block_ID = prev_block_ID
        self.has_successor = False
        self.miner_ID = miner_ID
        self.timestamp = timestamp
        self.transactions = transactions
        self.size = 1+len(transactions)

    def get_net_transaction(self, peer_ID):
        balance = 0
        for transaction in self.transactions:
            if transaction.sender_ID == peer_ID:
                balance-=transaction.amount
            elif transaction.reciever_ID == peer_ID:
                balance+=transaction.amount
        
        return balance

