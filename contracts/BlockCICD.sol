
contract BlockCICD {
    mapping(bytes32 => bool) private storedHashes; // CHANGED from string to bytes32
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function storeHash(bytes32 hashValue) public { // CHANGED from string to bytes32
        require(msg.sender == owner, "Unauthorized");
        storedHashes[hashValue] = true;
    }

    function verifyHash(bytes32 hashValue) public view returns (bool) { // CHANGED from string to bytes32
        return storedHashes[hashValue];
    }
}