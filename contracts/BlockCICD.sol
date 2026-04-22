// SPDX-License-Identifier: MIT
// M4: pinned to 0.8.20+ to avoid silent behavioral changes across OZ major versions
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract BlockCICD is ERC20, Ownable {
    mapping(bytes32 => uint256) public verifiedHashes;

    event PlanVerified(bytes32 indexed planHash, address indexed auditor, uint256 timestamp);

    // M4: OZ 5.x requires explicit Ownable(msg.sender) in constructor
    constructor() ERC20("DevOps Trust Token", "DTT") Ownable(msg.sender) {}

    function storeHash(bytes32 hashValue) public onlyOwner {
        require(verifiedHashes[hashValue] == 0, "Hash already registered");
        verifiedHashes[hashValue] = block.timestamp;

        _mint(msg.sender, 10 * 10 ** decimals());
        emit PlanVerified(hashValue, msg.sender, block.timestamp);
    }

    function verifyHash(bytes32 hashValue) public view returns (bool) {
        return verifiedHashes[hashValue] > 0;
    }
}
