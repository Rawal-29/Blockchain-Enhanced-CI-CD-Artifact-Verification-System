// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BlockCICD {
    mapping(string => bool) private storedHashes;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function storeHash(string memory hashValue) public {
        require(msg.sender == owner, "Unauthorized");
        storedHashes[hashValue] = true;
    }

    function verifyHash(string memory hashValue) public view returns (bool) {
        return storedHashes[hashValue];
    }
}
