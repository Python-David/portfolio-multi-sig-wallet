// SPDX-License-Identifier: MIT

pragma solidity ^0.8.13;

import "./MultiSigWallet.sol";

contract MultiSigFactory {
    event Deposit(address indexed sender, uint amount, uint balance);
    event SubmitTransaction(
        address indexed owner,
        uint indexed txIndex,
        address indexed to,
        uint value,
        bytes data
    );
    event ConfirmTransaction(address indexed owner, uint indexed txIndex);
    event RevokeConfirmation(address indexed owner, uint indexed txIndex);
    event ExecuteTransaction(address indexed owner, uint indexed txIndex);

    mapping(address => MultiSigWallet[]) public userToWallets;
    mapping(address => bool) public userExists;
    mapping(address => mapping(MultiSigWallet => bool)) public isOwner;
    mapping(MultiSigWallet => mapping(uint => mapping(address => bool))) public isConfirmed;

    function createMultiSig(address[] memory _owners, uint _numConfirmationsRequired) public {
        MultiSigWallet multiSigWallet = new MultiSigWallet(_owners, _numConfirmationsRequired);

        for (uint i = 0; i < _owners.length; i++) {
            if (!userExists[_owners[i]]) {
                userToWallets[_owners[i]] = [multiSigWallet];
                userExists[_owners[i]] = true;
                isOwner[_owners[i]][multiSigWallet] = true;
            }

            else if (userExists[_owners[i]]) {
                userToWallets[_owners[i]].push(multiSigWallet);
                isOwner[_owners[i]][multiSigWallet] = true;
            }
        }
        
    }

    function getOwners(address _user, uint _contract) public view returns (address[] memory) {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        return wallet_contract.getOwners();
    }

    function getTransaction(address _user, uint _contract, uint _txIndex) public view returns (address to, uint value, bytes memory data, bool executed, uint numConfirmations) {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        return wallet_contract.getTransaction(_txIndex);
    }

    function getTransactionCount(address _user, uint _contract) public view returns (uint) {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        return wallet_contract.getTransactionCount();
    }

    function submitTransaction(address _user, uint _contract, address _to, uint _value, bytes memory _data) public {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        require(isOwner[msg.sender][wallet_contract], "not owner");
        uint txIndex = getTransactionCount(_user, _contract);
        wallet_contract.submitTransaction(_to, _value, _data);
        isConfirmed[wallet_contract][txIndex][msg.sender] = true;

        emit SubmitTransaction(msg.sender, txIndex, _to, _value, _data);
        emit ConfirmTransaction(msg.sender, txIndex);
        
    }

    function confirmTransaction(address _user, uint _contract, uint _txIndex) public {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        require(isOwner[msg.sender][wallet_contract], "not owner");
        require(!isConfirmed[wallet_contract][_txIndex][msg.sender], "tx already confirmed");
        wallet_contract.confirmTransaction(_txIndex);
        isConfirmed[wallet_contract][_txIndex][msg.sender] = true;
        
        emit ConfirmTransaction(msg.sender, _txIndex);
    }

    function executeTransaction(address _user, uint _contract, uint _txIndex) public {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        require(isOwner[msg.sender][wallet_contract], "not owner");
        wallet_contract.executeTransaction(_txIndex);
        
        emit ExecuteTransaction(msg.sender, _txIndex);
    }

    function revokeConfirmation(address _user, uint _contract, uint _txIndex) public {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        require(isOwner[msg.sender][wallet_contract], "not owner");
        require(isConfirmed[wallet_contract][_txIndex][msg.sender], "tx not confirmed");
        wallet_contract.revokeConfirmation(_txIndex);
        isConfirmed[wallet_contract][_txIndex][msg.sender] = false;
        
        emit RevokeConfirmation(msg.sender, _txIndex);
    }

    function deposit(address _user, uint _contract) payable external {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        require(isOwner[msg.sender][wallet_contract], "not owner");
        (bool sent, ) = address(wallet_contract).call{value: msg.value}("");
        require(sent, "Failed to send Ether");

        emit Deposit(msg.sender, msg.value, address(this).balance);
    }

    function returnWallet(address _user, uint _contract) view public returns(address) {
        MultiSigWallet wallet_contract = userToWallets[_user][_contract];
        return address(wallet_contract);
    }

    function returnWalletCount(address _user) view public returns(uint256) {
        uint256 walletCount = userToWallets[_user].length;
        return walletCount;
    }

}

