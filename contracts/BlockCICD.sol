// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BlockCICD {
    // Mapping to store verified artifact hashes (bytes32 => true)
    mapping(bytes32 => bool) private storedHashes;
    address public owner;

    constructor() {
        // Set the contract deployer as the owner.
        owner = msg.sender;
    }

    function storeHash(bytes32 hashValue) public {
        // Security check: Only the owner (CI pipeline) can register hashes.
        require(msg.sender == owner, "Unauthorized");
        storedHashes[hashValue] = true;
    }

    function verifyHash(bytes32 hashValue) public view returns (bool) {
        // Checks if the hash exists in the immutable record.
        return storedHashes[hashValue];
    }
}