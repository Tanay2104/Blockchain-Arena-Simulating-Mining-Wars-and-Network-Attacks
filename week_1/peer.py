class Peers:
    def __init__(self):
        self.all_peers = set()
    
    def add_peer(self, peer):
        self.all_peers.add(peer.ID)

class Peer:
    def __init__(self, ID):
        self.ID = ID

    def get(self):
        return self
    