import numpy as np
import heapq
from network import Network
from containers import Event, Block, Transaction

class Simulator():
    def __init__(self, n, z_0, z_1, Ttx, inter_arrival_time = 600, intitial_wallet_balance = 100):
        self.event_queue = []
        heapq.heapify(self.event_queue)

        self.current_time = 0
        self.number_of_transactions = 0
        self.number_of_blocks = 0
        self.Ttx = Ttx
        self.I = inter_arrival_time

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
            txn_event = Event(timestamp=random_txn_time, type='GENERATE_TRANSACTION', target_peer_id=peer.ID)

            mining_time = np.random.exponential(scale=(self.I/peer.hashing_power))
            mining_event = Event(timestamp=mining_time, type='FINISH_MINING', target_peer_ID=peer.ID)

            heapq.heappush(self.event_queue, txn_event)
            heapq.heappush(self.event_queue, mining_event)

    def run(self, runtime):
        while self.event_queue and self.current_time < runtime:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.timestamp

            peer = self.network.get_peer(event.peer_id)

            if event.type == 'GENERATE_TRANSACTION':
                self.handle_generate_transaction(peer)

            elif event.type == 'FINISH_MINING':
                self.handle_finish_mining(peer)

            elif event.type == 'RECEIVE_MESSAGE':
                # The event's data contains the message (block or txn)
                message = event.data['message']
                sender_id = event.data['sender_id']
                self.handle_receive_message(peer, message, sender_id)