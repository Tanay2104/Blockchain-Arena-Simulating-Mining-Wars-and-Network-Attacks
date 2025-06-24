from network import Network
import random
i = random.randint(50, 100)
network = Network(20)
network.display()
print(f"Checking network with {i} nodes...")
print(f"Network validity: {network.check_validity()}")
print("----")