import numpy as np
import heapq
from network import Network
from containers import Event, Block, Transaction

class Simulator():
    def __init__(self, n, z_0, z_1, Ttx, inter_arrival_time = 600, intitial_wallet_balance = 100, max_coins_per_transaction=200):
        self.event_queue = []
        heapq.heapify(self.event_queue)

        self.current_time = 0
        self.number_of_transactions = 0
        self.number_of_blocks = 0
        self.Ttx = Ttx
        self.I = inter_arrival_time
        self.max_coins_per_transaction=max_coins_per_transaction
       

        # Initialising the Genesis block to give initial wallet balance to everyone
        genesis_transactions = []
        for i in range(n):
            transaction = Transaction(txn_ID=i, sender_ID=None, reciever_ID=i, amount = intitial_wallet_balance)
            genesis_transactions.append(transaction)
        self.number_of_transactions += n

        genesis_block = Block(block_ID=0, prev_block_ID=None, miner_ID=None, timestamp=0, transactions=genesis_transactions)
        self.number_of_blocks+=1

        self.network = Network(n=n, z_0_slow=z_0, z_1_low_CPU=z_1, genesis_block=genesis_block)
        self.network.build_network()
        
        #Initialising the first transactions so that the loop later can run
        for peer in self.network.network.nodes():
            random_txn_time = np.random.exponential(scale=self.Ttx)
            txn_event = Event(timestamp=random_txn_time, type='GENERATE_TRANSACTION', target_peer_ID=peer.ID)
            
            mining_event = peer.start_mining(self.current_time, self.I)
            
            heapq.heappush(self.event_queue, txn_event)
            heapq.heappush(self.event_queue, mining_event)

    def run(self, runtime):
        while self.event_queue and self.current_time < runtime:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.timestamp

            peer = self.network.get_peer(event.target_peer_ID)

            if event.type == 'GENERATE_TRANSACTION':
                self.handle_generate_transaction(peer)

            elif event.type == 'FINISH_MINING':
                self.handle_finish_mining(peer)

            elif event.type == 'RECEIVE_MESSAGE':
                # The event's data contains the message (block or txn)
                message = event.data['message']
                sender_id = event.data['sender_id']
                self.handle_receive_message(reciever=peer, message=message, sender_id=sender_id)

    def handle_generate_transaction(self, peer):
        number_of_coins = np.random.randint(1, self.max_coins_per_transaction)
        transaction_reciever_ID = np.random.choice(list(self.network.all_peers.keys()))
        longest_chain_end_block, longest_length = peer.blockchain_tree.get_longest_chain()
        txn_id = self.number_of_transactions+1
        self.number_of_transactions+=1
        current_balance = peer.blockchain_tree.calculate_balance(peer.ID, longest_chain_end_block.block_ID)
        if transaction_reciever_ID != peer.ID and current_balance >= number_of_coins:
            txn_messages = peer.generate_transaction(txn_id=txn_id, reciever = transaction_reciever_ID, amount=number_of_coins, current_time=self.current_time, Ttx = self.Ttx)
            for message in txn_messages:
                heapq.heappush(self.event_queue, message)
        
        else:
            next_txn_time = self.current_time + np.random.exponential(scale=self.Ttx)
            next_txn_event = Event(timestamp=next_txn_time, type='GENERATE_TRANSACTION', target_peer_ID=peer.ID)
            heapq.heappush(self.event_queue, next_txn_event)

    def handle_finish_mining(self, peer):
        block_messages = peer.attempt_to_finalise_block(number_of_transactions=self.number_of_transactions, 
                                        current_time=self.current_time, number_of_blocks = self.number_of_blocks)
        for message in block_messages:
            heapq.heappush(self.event_queue, message)

        if block_messages:
            self.number_of_blocks+=1
            self.number_of_transactions+=1

        next_mining_event = peer.start_mining(self.current_time, self.I)
        heapq.heappush(self.event_queue, next_mining_event)

    def handle_receive_message(self, reciever, message, sender_id):
        if isinstance(message, Transaction):
            if message.txn_ID in reciever.known_txn_ids:
                return
            else:
                reciever.known_txn_ids.add(message.txn_ID)
                txn_messages = reciever.propagate_transaction(current_time=self.current_time, txn=message, sender_id=sender_id)
                for gossip in txn_messages:
                    heapq.heappush(self.event_queue, gossip)

        elif isinstance(message, Block):
            if message.block_ID in reciever.known_block_ids:
                return
            else:
                reciever.known_block_ids.add(message.block_ID)
                block_messages, new_mining = reciever.propagate_block(block=message, current_time=self.current_time, sender_id=sender_id)
                if block_messages:
                    for gossip in block_messages:
                        heapq.heappush(self.event_queue, gossip)

                if new_mining:
                    next_mining_event = reciever.start_mining(self.current_time, self.I)
                    heapq.heappush(self.event_queue, next_mining_event)
                    

        
