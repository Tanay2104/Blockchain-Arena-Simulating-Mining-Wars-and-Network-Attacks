// =============================================================================
// --- 1. SET-UP & CONFIGURATION ---
// =============================================================================

const contractAddress = "0x4689dcf146bc388492A59Af0987a1Ec760F372e5"; // Make sure this is a string
const contractABI =  [ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "uint256", "name": "id", "type": "uint256" }, { "indexed": true, "internalType": "address", "name": "owner", "type": "address" }, { "indexed": false, "internalType": "string", "name": "name", "type": "string" } ], "name": "ItemRegistered", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "uint256", "name": "id", "type": "uint256" }, { "indexed": true, "internalType": "address", "name": "from", "type": "address" }, { "indexed": true, "internalType": "address", "name": "to", "type": "address" } ], "name": "OwnershipTransferred", "type": "event" }, { "inputs": [ { "internalType": "string", "name": "_name", "type": "string" } ], "name": "registerItems", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "internalType": "uint256", "name": "id", "type": "uint256" }, { "internalType": "address", "name": "newOwner", "type": "address" } ], "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "name": "count", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "name": "items", "outputs": [ { "internalType": "uint256", "name": "id", "type": "uint256" }, { "internalType": "string", "name": "name", "type": "string" }, { "internalType": "address", "name": "owner", "type": "address" } ], "stateMutability": "view", "type": "function" } ];

let provider;
let signer;
let contract;

// Get references to all HTML elements
const dappInterface = document.getElementById('dapp_interface');
const connectWalletButton = document.getElementById('connect_wallet_button');
const registerItemButton = document.getElementById('register_item_button');
const itemNameInput = document.getElementById('item_name_input');
const refreshButton = document.getElementById('refresh_button');
const itemList = document.getElementById('item_list');
const historySection = document.getElementById('history_section');
const historyItemId = document.getElementById('history_item_id');
const provenanceHistory = document.getElementById('provenance_history');
const loadingMessage = document.getElementById('loading_items_msg');
const emptyMessage = document.getElementById('empty_history_msg');

// =============================================================================
// --- 2. CORE DAPP FUNCTIONS ---
// =============================================================================

/**
 * Fetches all 'ItemRegistered' events and displays them in the list.
 */
async function fetchAllItems() {
    loadingMessage.classList.remove('hidden');
    emptyMessage.classList.add('hidden');
    itemList.innerHTML = ''; // Clear the list before populating

    try {
        const itemEvents = await contract.queryFilter('ItemRegistered');
        
        if (itemEvents.length === 0) {
            emptyMessage.classList.remove('hidden');
        } else {
            const currentUserAddress = await signer.getAddress();
            
            for (const event of itemEvents) {
                const { id, owner, name } = event.args;

                const li = document.createElement('li');
                li.dataset.itemId = id; // Store item ID for later use

                // Check if the current user is the owner to show the transfer form
                const isOwner = currentUserAddress.toLowerCase() === owner.toLowerCase();
                const transferFormHTML = isOwner ? `
                    <div class="transfer-form">
                        <input type="text" placeholder="New owner's address" class="transfer-input">
                        <button class="transfer-button">Transfer</button>
                    </div>
                ` : '';

                li.innerHTML = `
                    <div>
                        <strong>ID:</strong> ${id} | <strong>Name:</strong> ${name}
                    </div>
                    <small><strong>Owner:</strong> ${owner}</small>
                    ${transferFormHTML}
                `;

                // Add event listener to the whole item to view its history
                li.addEventListener('click', (e) => {
                    // Prevent firing when clicking on buttons/inputs inside the item
                    if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {
                        showProvenance(id);
                    }
                });

                // If the transfer form exists, add an event listener to its button
                if (isOwner) {
                    const transferButton = li.querySelector('.transfer-button');
                    const transferInput = li.querySelector('.transfer-input');
                    transferButton.addEventListener('click', (e) => {
                        e.stopPropagation(); // Prevent the li's click event from firing
                        transferItem(id, transferInput);
                    });
                }
                
                itemList.appendChild(li);
            }
        }
    } catch (error) {
        console.error("Error fetching items:", error);
        alert("Could not fetch items. See console for details.");
    } finally {
        loadingMessage.classList.add('hidden');
    }
}

/**
 * Registers a new item on the blockchain.
 */
async function registerNewItem() {
    const itemName = itemNameInput.value;
    if (!itemName) {
        alert("Please enter an item name.");
        return;
    }

    try {
        // Your contract function is named 'registerItems'
        const tx = await contract.registerItems(itemName);
        alert("Registering item... please wait for the transaction to be confirmed.");
        await tx.wait(); // Wait for the transaction to be mined
        alert("Item registered successfully!");
        itemNameInput.value = ''; // Clear input field
        fetchAllItems(); // Refresh the list
    } catch (error) {
        console.error("Error registering item:", error);
        alert("Item registration failed. See console for details.");
    }
}

/**
 * Fetches and displays the ownership history for a specific item.
 * @param {number} itemId - The ID of the item to track.
 */
async function showProvenance(itemId) {
    historyItemId.textContent = itemId;
    provenanceHistory.innerHTML = '<li>Loading history...</li>';
    historySection.classList.remove('hidden');

    try {
        const filter = contract.filters.OwnershipTransferred(itemId, null, null);
        const transferEvents = await contract.queryFilter(filter);

        provenanceHistory.innerHTML = ''; // Clear loading message

        if (transferEvents.length === 0) {
            provenanceHistory.innerHTML = '<li>No ownership transfers recorded for this item.</li>';
        } else {
            transferEvents.forEach(event => {
                const { from, to } = event.args;
                const li = document.createElement('li');
                li.innerHTML = `<strong>From:</strong> ${from} <br> <strong>To:</strong> ${to}`;
                provenanceHistory.appendChild(li);
            });
        }
    } catch (error) {
        console.error("Error fetching provenance:", error);
        provenanceHistory.innerHTML = '<li>Could not fetch history.</li>';
    }
}

/**
 * Transfers an item to a new owner.
 * @param {number} itemId - The ID of the item to transfer.
 * @param {HTMLElement} inputElement - The input field containing the new owner's address.
 */
async function transferItem(itemId, inputElement) {
    const newOwnerAddress = inputElement.value;
    if (!ethers.utils.isAddress(newOwnerAddress)) {
        alert("Invalid Ethereum address.");
        return;
    }

    try {
        const tx = await contract.transferOwnership(itemId, newOwnerAddress);
        alert("Transferring ownership... please wait for confirmation.");
        await tx.wait();
        alert("Ownership transferred successfully!");
        fetchAllItems(); // Refresh list to show new owner and remove transfer form
    } catch (error) {
        console.error("Error transferring ownership:", error);
        alert("Ownership transfer failed. See console for details.");
    }
}

/**
 * Initializes the DApp, connects to MetaMask, and sets up listeners.
 */
async function connectAndInitialize() {
    if (typeof window.ethereum === "undefined") {
        return alert('Metamask not installed. Please install Metamask and try again');
    }
    
    try {
        provider = new ethers.providers.Web3Provider(window.ethereum);
        await provider.send("eth_requestAccounts", []);
        signer = provider.getSigner();            
        contract = new ethers.Contract(contractAddress, contractABI, signer);

        // --- UI Updates and Initial Data Fetch ---
        connectWalletButton.classList.add("hidden");
        dappInterface.classList.remove("hidden");
        
        console.log("Wallet connected! Fetching items...");
        fetchAllItems();

        // --- Set up real-time event listeners ---
        contract.on('ItemRegistered', (id, owner, name) => {
            console.log(`New Item Registered: ID ${id}, Owner ${owner}`);
            // Simple refresh to show the new item
            fetchAllItems();
        });
        
        contract.on('OwnershipTransferred', (id, from, to) => {
            console.log(`Ownership Transfer: ID ${id} from ${from} to ${to}`);
            // Refresh if the currently viewed history is for the transferred item
            if (!historySection.classList.contains('hidden') && historyItemId.textContent == id) {
                showProvenance(id);
            }
            fetchAllItems();
        });

    } catch (error) {
        console.error("Error connecting to MetaMask:", error);
    }
}

// =============================================================================
// --- 3. EVENT LISTENERS ---
// =============================================================================
connectWalletButton.addEventListener("click", connectAndInitialize);
registerItemButton.addEventListener("click", registerNewItem);
refreshButton.addEventListener("click", fetchAllItems);