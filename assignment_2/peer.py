from blockchain_tree import BlockchainTree
from containers import Event, Block, Transaction
import numpy as np

class Peer():
    def __init__(self, ID, genesis_block, network, is_slow=False, is_low_CPU=False, hashing_powers=None):
        self.ID = ID
        self.is_slow=is_slow
        self.is_low_CPU = is_low_CPU
        self.hashing_power = hashing_powers[0] if is_low_CPU else hashing_powers[1]
        self.wallet_balance = 0
        self.blockchain_tree = BlockchainTree(genesis_block)
        self.pending_transactions = []
        self.network = network
        self.current_mining_parent = None
        self.known_txn_ids = set()
        self.known_block_ids = {genesis_block.block_ID}
        
    # def add_connected_neighbours(self, neighbours):
    #     self.neighbours = list(neighbours)

    def propagate_transaction(self, current_time, txn, sender_ID):
        txn_messages = []
        self.pending_transactions.append(txn)

        for neighbour in self.network.network.neighbors(self):
            if neighbour.ID != sender_ID:
            #latency = propogation_delay + length_of_message/link_speed + queing_delay
                latency_ij = self.calculate_latency(neighbour, message_size_kb=1)

                txn_message = Event(timestamp = current_time + latency_ij, type = 'RECEIVE_MESSAGE', target_peer_ID = neighbour.ID, 
                    data = {'message': txn, 'sender_id': self.ID})
                
                txn_messages.append(txn_message)

        return txn_messages
    
    def propagate_block(self, block, current_time, sender_id):

        if not self.validate_block(block):
            return [], False
                
        _, old_length = self.blockchain_tree.get_longest_chain()

        self.blockchain_tree.add_block(block)
        _, new_length = self.blockchain_tree.get_longest_chain()

        block_messages = []
        for neighbour in self.network.network.neighbors(self):
            if neighbour.ID != sender_id:
                latency_ij = self.calculate_latency(neighbour, message_size_kb=block.size)
                block_message = Event(timestamp = current_time + latency_ij, type = 'RECEIVE_MESSAGE', target_peer_ID= neighbour.ID, data = {'message': block, 'sender_id': self.ID})
                block_messages.append(block_message)
        
        return block_messages, new_length > old_length
    
    def validate_block(self, block):
        
        if block.prev_block_ID not in self.blockchain_tree.tree_data:
            return False
        
        parent_block_id = block.prev_block_ID
        temp_balances = {}
        for transaction in block.transactions:
            if transaction.amount < 0:
                return False
            sender_ID = transaction.sender_ID
            if sender_ID is None:
                continue

            if sender_ID not in temp_balances.keys():
               temp_balances[sender_ID] = self.blockchain_tree.calculate_balance(peer_ID=sender_ID, chain_end_block_ID=parent_block_id)

            temp_balances[sender_ID]-=transaction.amount
                
            if temp_balances[sender_ID] < 0:
                return False
            
            reciever_ID  = transaction.reciever_ID
            if reciever_ID not in temp_balances.keys():
               temp_balances[reciever_ID] = self.blockchain_tree.calculate_balance(peer_ID=reciever_ID, chain_end_block_ID=parent_block_id)

            temp_balances[reciever_ID]+=transaction.amount

        return True

    def generate_transaction(self, txn_id, reciever, amount, current_time, Ttx):
        txn = Transaction(txn_ID=txn_id, sender_ID=self.ID, reciever_ID=reciever, amount=amount)
        self.pending_transactions.append(txn)

        txn_messages = []

        for neighbour in self.network.network.neighbors(self):
            latency_ij = self.calculate_latency(neighbour, message_size_kb=1)

            txn_message = Event(timestamp = current_time + latency_ij, type = 'RECEIVE_MESSAGE', target_peer_ID = neighbour.ID, 
                  data = {'message': txn, 'sender_id': self.ID})
            
            txn_messages.append(txn_message)

        next_txn_time = current_time + np.random.exponential(scale=Ttx)
        next_txn = Event(timestamp = next_txn_time, type = 'GENERATE_TRANSACTION', target_peer_ID = self.ID)

        txn_messages.append(next_txn)

        

        return txn_messages
    
    def calculate_latency(self, neighbour, message_size_kb):
        #latency = propogation_delay + length_of_message/link_speed + queing_delay

        if self.is_slow or neighbour.is_slow:
            c_ij = 5
        else:
            c_ij = 100

        c_ij_bps = 1_000_000*c_ij
        d_ij = np.random.exponential(scale=96*1000/c_ij_bps)
    
        message_length = 8000*message_size_kb

        propagation_delay_ij = self.network.network[self][neighbour]['p_delay']
        
        latency_ij = propagation_delay_ij + message_length / c_ij_bps + d_ij
        return latency_ij
    
    def start_mining(self, current_time, I):
        self.current_mining_parent, _ = self.blockchain_tree.get_longest_chain()

        next_mine_time = current_time + np.random.exponential(scale = I / self.hashing_power)
        next_mining_event = Event(timestamp=next_mine_time, type='FINISH_MINING', target_peer_ID=self.ID)
        
        return next_mining_event

    def attempt_to_finalise_block(self, number_of_transactions, number_of_blocks, current_time):

        current_longest_chain_tip, _ = self.blockchain_tree.get_longest_chain()

        if current_longest_chain_tip.block_ID != self.current_mining_parent.block_ID:
            return []
        
        block_messages = []
        
        n_max_transactions = min(999, len(self.pending_transactions))
        if n_max_transactions==0:
            mining_fee_txn = Transaction(txn_ID=number_of_transactions+1, sender_ID=None, reciever_ID=self.ID, amount=50)
            new_block = Block(block_ID=number_of_blocks+1, prev_block_ID=current_longest_chain_tip.block_ID, miner_ID=self.ID, timestamp=current_time, transactions=[mining_fee_txn])
            for neighbour in self.network.network.neighbors(self):
                latency_ij = self.calculate_latency(neighbour, message_size_kb=1)
                block_message = Event(timestamp = current_time + latency_ij, type = 'RECEIVE_MESSAGE', target_peer_ID = neighbour.ID, data = {'message': new_block, 'sender_id': self.ID})
                block_messages.append(block_message)
            return block_messages
        
        n_transactions = np.random.randint(0, n_max_transactions+1)
        transactions_in_block = list(np.random.choice(a=self.pending_transactions, size=n_transactions, replace=False))

        self.pending_transactions = [txn for txn in self.pending_transactions if txn not in set(transactions_in_block)]
        
        mining_fee_txn = Transaction(txn_ID=number_of_transactions+1, sender_ID=None, reciever_ID=self.ID, amount=50)
        transactions_in_block.append(mining_fee_txn)
     
        new_block = Block(block_ID=number_of_blocks+1, prev_block_ID=current_longest_chain_tip.block_ID, miner_ID=self.ID, timestamp=current_time, transactions=transactions_in_block)

        self.blockchain_tree.add_block(new_block)

      
        for neighbour in self.network.network.neighbors(self):
            latency_ij = self.calculate_latency(neighbour, message_size_kb=new_block.size)
            block_message = Event(timestamp = current_time + latency_ij, type = 'RECEIVE_MESSAGE', target_peer_ID= neighbour.ID, data = {'message': new_block, 'sender_id': self.ID})
            block_messages.append(block_message)
        
        return block_messages