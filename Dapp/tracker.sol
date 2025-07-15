pragma solidity  ^0.8.20;

contract SimpleStorage {
    struct Item {
        uint256 id;
        string name;
        address owner;
    }
    mapping (uint256 => Item) public items;
    uint public count = 0;

    event ItemRegistered(uint256 indexed id, address indexed owner, string name);
    event OwnershipTransferred(uint256 indexed id, address indexed from, address indexed to);

    function registerItems(string memory _name) public {
        Item memory newItem = Item(count, _name, msg.sender);
        items[count] = newItem;
        emit ItemRegistered(newItem.id, newItem.owner, newItem.name);
        count ++;
    }
    function transferOwnership(uint256 id, address newOwner) public {
        address orig_owner = items[id].owner;
        require(msg.sender == orig_owner, "Only the owner can call this function");
        items[id].owner = newOwner;
        emit OwnershipTransferred(id, orig_owner, newOwner);
    }
    function burnItem(uint256 _id) public {
    require(msg.sender == items[_id].owner, "Only the current owner can burn this item.");
    address originalOwner = items[_id].owner;
    items[_id].owner = address(0);
    emit OwnershipTransferred(_id, originalOwner, address(0));
}
}