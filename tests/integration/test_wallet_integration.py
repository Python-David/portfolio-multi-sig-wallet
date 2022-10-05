from brownie import accounts, network, config, MultiSigWallet, exceptions
from helpful_scripts import get_account
from scripts.deploy import TESTNETS, deploy, owners
import pytest
from web3 import Web3


def test_owners():
    if network.show_active() not in TESTNETS:
        pytest.skip()
    else:
        account = get_account()
        multi_sig_wallet = MultiSigWallet[-1]

        assert multi_sig_wallet.owners(0) == account
        assert multi_sig_wallet.owners(1) == owners[0]
        assert multi_sig_wallet.owners(2) == owners[1]
        assert len(multi_sig_wallet.getOwners()) == 3
        assert multi_sig_wallet.getOwners() == (account, owners[0], owners[1])

        return multi_sig_wallet


# def test_submit_transaction():
#     """
#     Tests if a transaction is submitted successfully. Tests if a transaction is
#     confirmed by the owner, upon successful submission. Tests if only owner can submit transaction.
#     """
#     account = get_account()
#     multi_sig_wallet = test_owners()

#     # First send money to the contract
#     multi_sig_wallet.deposit({"from": account, "value": Web3.toWei(2, "ether")})

#     #
#     multi_sig_wallet.submitTransaction(
#         accounts[3], 1000000000000000000, "0x00", {"from": account}
#     )

#     assert multi_sig_wallet.getTransactionCount() == 1
#     assert multi_sig_wallet.getTransaction(0)[4] == 1
#     assert multi_sig_wallet.isConfirmed(0, account) == True

#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet.submitTransaction(
#             accounts[3], (Web3.toWei(1, "ether")), "0x00", {"from": accounts[4]}
#         )

#     return multi_sig_wallet


# def test_confirm_transaction():
#     """
#     Tests if transaction is confirmed upon submission.
#     Tests if only the owner can confirm a transaction.
#     Tests that transaction exists

#     """
#     account = get_account()
#     multi_sig_wallet = test_submit_transaction()

#     num_of_confirmations = multi_sig_wallet.getTransaction(0, {"from": account})[4]
#     owner_confirmed = multi_sig_wallet.isConfirmed(0, account)

#     assert num_of_confirmations == 1
#     assert owner_confirmed == True

#     # Try and confirm the transaction from a non-owner (onlyOwner)
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet.confirmTransaction(0, {"from": accounts[4]})

#     # Try to confirm a transaction that does not exist from an owner account (txExists)
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet.confirmTransaction(1, {"from": accounts[1]})

#     # Test that transaction has already been confirmed by account[0] (the one who submitted the transaction) (notConfirmed)
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet.confirmTransaction(0, {"from": account})

#     # Test that transaction is not confirmed by second account (notConfirmed)
#     assert multi_sig_wallet.isConfirmed(0, accounts[1], {"from": accounts[1]}) == False

#     # Now confirm with the right owner (second account)
#     multi_sig_wallet.confirmTransaction(0, {"from": accounts[1]})

#     # Test that transaction is now confirmed (notConfirmed)
#     assert multi_sig_wallet.isConfirmed(0, accounts[1], {"from": accounts[1]}) == True

#     assert multi_sig_wallet.getTransaction(0, {"from": accounts[8]})[4] == 2
#     assert multi_sig_wallet.isConfirmed(0, accounts[1]) == True

#     return multi_sig_wallet


# def test_execute_transaction():
#     account = get_account()
#     multi_sig_wallet_confirmed_complete = test_confirm_transaction()
#     multi_sig_wallet_confirmed_incomplete = test_submit_transaction()

#     # Test that only an owner can call this function
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet_confirmed_complete.executeTransaction(0, {"from": accounts[4]})

#     # Test that transaction exists
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet_confirmed_complete.confirmTransaction(1, {"from": account})

#     # Test that transaction has not been executed
#     assert (
#         multi_sig_wallet_confirmed_complete.getTransaction(0, {"from": account})[3]
#         == False
#     )

#     # Test the levels of confirmations for both transactions (complete and incomplete above)
#     assert multi_sig_wallet_confirmed_complete.getTransaction(0)[4] == 2
#     assert multi_sig_wallet_confirmed_incomplete.getTransaction(0)[4] == 1
#     assert (
#         multi_sig_wallet_confirmed_complete.getTransaction(0)[4]
#         >= multi_sig_wallet_confirmed_complete.numConfirmationsRequired()
#     )
#     assert (
#         multi_sig_wallet_confirmed_incomplete.getTransaction(0)[4]
#         < multi_sig_wallet_confirmed_incomplete.numConfirmationsRequired()
#     )

#     # Test execution status for transaction
#     assert multi_sig_wallet_confirmed_complete.getTransaction(0)[3] == False

#     # Now execute transaction
#     # Test execute a transaction that has not been completely confirmed
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet_confirmed_incomplete.executeTransaction(0, {"from": account})

#     # Test execute a transaction that has been completely confirmed
#     multi_sig_wallet_confirmed_complete.executeTransaction(0, {"from": account})

#     assert multi_sig_wallet_confirmed_complete.getTransaction(0)[3] == True

#     return multi_sig_wallet_confirmed_complete


# def test_revoke_confirmation():
#     account = get_account()
#     multi_sig_wallet_executed = test_execute_transaction()
#     multi_sig_wallet_not_executed = test_confirm_transaction()

#     # Test revoking confirmation for a transaction that has already been executed
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet_executed.revokeConfirmation(0, {"from": account})

#     # Test revoking confirmation for a transaction from a non-owner
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet_executed.revokeConfirmation(0, {"from": accounts[4]})

#     # Test revoking confirmation for a transaction that does not exist
#     with pytest.raises(exceptions.VirtualMachineError):
#         multi_sig_wallet_executed.revokeConfirmation(1, {"from": account})
