// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MyContract {
    uint256 public foo;

    function calc() public {
        foo = 10 * 20;
    }
}