# Blockchain-Arena-Simulating-Mining-Wars-and-Network-Attacks

This repository contains the completed projects for the "Blockchain Arena: Simulating Mining Wars and Network Attacks" SoC project. It includes a discrete-event simulator for a P2P network and a full-stack decentralized application (DApp) for provenance tracking.

---

## Part 1: Simulation of a P2P Cryptocurrency Network

### Overview

This project is a discrete-event simulator built in Python to model a Proof-of-Work (PoW) based P2P cryptocurrency network. The simulation is designed to be a digital laboratory for studying the emergent properties of decentralized networks. It models key aspects such as:
- **Peer Heterogeneity:** Nodes can be configured with different network speeds (fast/slow) and computational power (high/low CPU).
- **Network Topology:** A random, connected graph where each peer has between 3 and 6 neighbors.
- **Transaction & Block Propagation:** Simulates message latency based on link speed, propagation delay, and queuing delay.
- **Proof-of-Work Mining:** Block mining times are modeled using an exponential distribution based on a peer's share of the total network hashing power.
- **Fork Resolution:** Each peer maintains its own blockchain tree and always mines on the tip of the longest chain it has seen, naturally simulating fork creation and resolution.

### Code Structure

The simulator is organized into several modular Python files:

-   `main.py`: The entry point for the simulation. It sets the global parameters (number of peers, peer types, etc.), initializes the simulator, and runs it for a specified duration. It also triggers the final visualizations.
-   `simulator.py`: The core engine of the simulation. It manages the priority event queue (using `heapq`) and processes events chronologically. It handles the global state, such as time and total transaction/block counts.
-   `network.py`: Defines the `Network` class, which uses the `networkx` library to create and manage the P2P network graph, ensuring it is connected and adheres to the specified degree constraints.
-   `peer.py`: Defines the `Peer` class, which encapsulates the logic and state for a single node in the network. This includes generating transactions, validating and propagating messages (blocks and transactions), and handling the mining process.
-   `blockchain_tree.py`: Implements the `BlockchainTree` class, a data structure used by each peer to store its local view of the blockchain. It includes methods for adding blocks and finding the longest chain.
-   `containers.py`: Contains simple data classes (`Event`, `Transaction`, `Block`) to structure the data passed around in the simulation.
-   `visualise.py`: A utility file that uses `graphviz` and `matplotlib` to generate visualizations from the final simulation state, such as the blockchain tree, wealth distribution, and miner efficiency.
-   `Project 1 Report.pdf`: A detailed report covering the theoretical justifications, experimental analysis, and findings from the simulation.

### How to Run

1.  **Prerequisites:**
    -   Python 3.x
    -   The following Python libraries: `numpy`, `matplotlib`, `networkx`, `graphviz`. You can install them via pip:
        ```bash
        pip install numpy matplotlib networkx graphviz
        ```
    -   **Important:** `graphviz` is a Python wrapper for the Graphviz software. You must also install the Graphviz command-line tools on your system. You can find instructions at [https://graphviz.org/download/](https://graphviz.org/download/).

2.  **Execution:**
    -   Navigate to the project directory in your terminal.
    -   Run the `main.py` script:
        ```bash
        python main.py
        ```
    -   The simulation will run, and upon completion, it will save several PNG images (`blockchain_tree.png`, `wealth_distribution.png`, etc.) in the same directory.

---

## Part 2: Verifiable On-Chain Provenance Tracker (DApp)

### Overview

This project is a full-stack decentralized application (DApp) that provides a verifiable, tamper-proof system for registering unique items and tracking their ownership history on the Ethereum blockchain. It functions as a basic Non-Fungible Token (NFT) system. 

Note: Building DApps was a new  and very challenging experience. It took a lot of time to understand the concepts, especially `ethers.js` . I decided to take generative AI's help for the css styling of the web app since the deadline for SoC submission was approaching, and styling web pages wouldnt add much to my skillset. The main javascript, html and solidity files were written be me.

The DApp has two main components:
1.  **Smart Contract (`tracker.sol`):** The backend logic, written in Solidity. It is deployed on an Ethereum test network (Sepolia) and is responsible for storing item data, managing ownership, and enforcing the rules of interaction.
2.  **Frontend (HTML/CSS/JS):** A user-friendly web interface that allows users to interact with the deployed smart contract through their browser-based wallets (e.g., MetaMask).

### Code Structure

-   `Tracker.sol`: The Solidity smart contract. It defines the `Item` struct, state variables for storing items and their count, and the core functions (`registerItem`, `transferOwnership`, `burnItem`). It also emits events (`ItemRegistered`, `OwnershipTransferred`) that the frontend listens to for updates.
-   `index.html`: The main HTML file that defines the structure and layout of the user interface, including the connection button, registration form, and lists for items and provenance.
-   `styles.css`: The stylesheet that provides the visual design and layout for the DApp, making it responsive and user-friendly.
-   `script.js`: The heart of the frontend logic. It uses the `ethers.js` library to:
    -   Connect to the user's MetaMask wallet.
    -   Instantiate a contract object using the ABI and deployed address.
    -   Handle user actions by calling the smart contract's functions (e.g., `registerItem`).
    -   Query the blockchain for past events (`ItemRegistered`, `OwnershipTransferred`) to dynamically build and update the item list and provenance history.

### How to Run

1.  **Prerequisites:**
    -   A web browser with the [MetaMask](https://metamask.io/) extension installed.
    -   In MetaMask, connect to the **Sepolia Test Network**.
    -   Obtain some free Sepolia ETH from a faucet (e.g., [https://sepoliafaucet.com/](https://sepoliafaucet.com/)) to pay for transaction gas fees.

2.  **Execution:**
    -   To run the DApp frontend, you need to serve the files from a local web server.
    -   Navigate to the DApp's project directory in your terminal.
    -   If you have Python installed, you can start a simple server with one of the following commands:
        ```bash
        # For Python 3
        python -m http.server
        ```
    -   Open your web browser and go to `http://localhost:8000`. The DApp interface should load.
    -   Click "Connect Wallet" and follow the prompts in MetaMask to interact with the application.

### Deployed Contract Information

**Note:** You must fill in the details below with your actual deployed contract address.

*   **Network:** Sepolia Test Network
*   **Deployed Contract Address:** `0xB2792b5AF0e0673A62B0467106449feB53af8189`
