const contractAddress = "0xB2792b5AF0e0673A62B0467106449feB53af8189"
const contractABI = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_id",
				"type": "uint256"
			}
		],
		"name": "burnItem",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "name",
				"type": "string"
			}
		],
		"name": "ItemRegistered",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "to",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			}
		],
		"name": "registerItems",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "count",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "items",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
let provider;
let signer;
let contract;

const dappInterface = document.getElementById('dapp_interface');
const connectWalletButton = document.getElementById("connect_wallet_button")
const refreshButton = document.getElementById("refresh_button")

connectWalletButton.addEventListener("click", async function() {
    if (typeof window.ethereum == "undefined") {
        window.alert('Metamask not installed. Please install Metamask and try again')
        return
    }
    provider = new ethers.providers.Web3Provider(window.ethereum);
    try {
            const accounts = await provider.send("eth_requestAccounts", []);
            signer = provider.getSigner(); 
			window.alert("Wallet successfully connected")           
            console.log("Connected account:", accounts[0]);
            contract = new ethers.Contract(contractAddress, contractABI, signer);

            connectWalletButton.classList.add("hidden")
            dappInterface.classList.remove("hidden")

			fetchAllItems()
            

        } catch (error) {
            console.error("Error connecting to MetaMask:", error);
        }


})

refreshButton.addEventListener("click", fetchAllItems)

const registerItemButton = document.getElementById('register_item_button')
const itemNameInput = document.getElementById('item_name_input')

registerItemButton.addEventListener('click', async () => {
	const item_name = itemNameInput.value
	if (!item_name) {
		alert("Please enter an item name")
		return
	}

	try {
		const txn = await contract.registerItems(item_name);

		await txn.wait();
		alert("Item registered successfully!")
		console.log("Item with name ", item_name, " successfully registered")

		itemNameInput.value = ''
		fetchAllItems();
	}
	catch(error) {
		console.error("Error registering item: ", error)
		alert("Failed to register item, check console")
	}

})

async function fetchAllItems() {
    console.log("Fetching items list");
    document.getElementById('loading_items_msg').classList.remove('hidden');
    document.getElementById('empty_history_msg').classList.add('hidden');

    const itemList = document.getElementById('item_list');
    itemList.innerHTML = '';

    try {
        const itemEvents = await contract.queryFilter('ItemRegistered');
        
        const currentUserAddress = await signer.getAddress();

        if (itemEvents.length === 0) {
            document.getElementById('empty_history_msg').classList.remove('hidden');
        } else {
            const itemPromises = itemEvents.map(async (event) => {
                const { id, name } = event.args;
                let currentOwner = event.args.owner; 
                const transferFilter = contract.filters.OwnershipTransferred(id, null, null);
                const transferEvents = await contract.queryFilter(transferFilter);
                
                if (transferEvents.length > 0) {
                    currentOwner = transferEvents[transferEvents.length - 1].args.to;
                }

                if (currentOwner !== '0x0000000000000000000000000000000000000000') {
                    return { id, name, owner: currentOwner };
                }
                return null; 
            });

            const allItems = await Promise.all(itemPromises);

            allItems.forEach(item => {
                if (item === null) return;

                const { id, owner, name } = item;

                const isOwner = currentUserAddress.toLowerCase() === owner.toLowerCase();
                
                const controlFormHTML = isOwner ? `
                    <div class="transfer-form">
                        <input type="text" placeholder="New owner's address" class="transfer-input">
                        <button class="transfer-button">Transfer</button>
                        <button class="burn-button">Burn</button>
                    </div>
                ` : '';

                const li = document.createElement('li');
                li.innerHTML = `
                    <div>
                        <strong>ID:</strong> ${id} | <strong>Name:</strong> ${name}
                    </div>
                    <small><strong>Owner:</strong> ${owner}</small>
                    ${controlFormHTML} 
                `;

                li.addEventListener('click', (e) => {
                    if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT') {
                        showProvenance(id);
                    }
                });

                if (isOwner) {
                    li.querySelector('.transfer-button').addEventListener('click', (e) => {
                        e.stopPropagation();
                        transferItem(id, li.querySelector('.transfer-input'));
                    });
                    li.querySelector('.burn-button').addEventListener('click', (e) => {
                        e.stopPropagation();
                        burnItemOnFrontend(id);
                    });
                }
                
                itemList.appendChild(li);
            });
            
            if (itemList.children.length === 0) {
                document.getElementById('empty_history_msg').classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error("Error fetching items: ", error);
    } finally {
        document.getElementById('loading_items_msg').classList.add('hidden');
    }
}

async function transferItem(itemId, inputElement) {
    const newOwnerAddress = inputElement.value;
    
    if (!ethers.utils.isAddress(newOwnerAddress)) {
        alert("Invalid ethereum address");
        return;
    }

    try {
        const txn = await contract.transferOwnership(itemId, newOwnerAddress);
        await txn.wait();
        alert("Ownership transferred successfully!");
        fetchAllItems();
    } catch (error) {
        console.error("Error transferring ownership:", error);
        alert("Ownership transfer failed, see console");
    }
}

async function showProvenance(itemId) {
    const historySection = document.getElementById('history_section');
    const historyItemId = document.getElementById('history_item_id');
    const provenanceHistory = document.getElementById('provenance_history');
    
    historyItemId.textContent = itemId;
    provenanceHistory.innerHTML = '<li>Loading history...</li>';
    historySection.classList.remove('hidden');

    try {
        const filter = contract.filters.OwnershipTransferred(itemId, null, null);
        const transferEvents = await contract.queryFilter(filter);

        provenanceHistory.innerHTML = ''; 

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

async function burnItemOnFrontend(itemId) {
    if (!confirm(`Are you sure you want to permanently burn Item #${itemId}? This cannot be undone.`)) {
        return;
    }

    try {
        const tx = await contract.burnItem(itemId);
        await tx.wait();
        
        alert("Item burned successfully!");
        fetchAllItems();
        
    } catch (error) {
        console.error("Error burning item:", error);
        alert("Failed to burn item. See console for details.");
    }
}