// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BlockCICD {
    mapping(bytes32 => bool) private storedHashes;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function storeHash(bytes32 hashValue) public {
        require(msg.sender == owner, "Unauthorized");
        storedHashes[hashValue] = true;
    }

    function verifyHash(bytes32 hashValue) public view returns (bool) {
        return storedHashes[hashValue];
    }
}