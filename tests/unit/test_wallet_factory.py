from brownie import accounts, network, exceptions
from helpful_scripts import get_account
from scripts.deploy_factory import deploy, TESTNETS
import pytest
from web3 import Web3


def test_create_wallet():
    if network.show_active() in TESTNETS:
        pytest.skip()
    else:
        account = get_account()
        factory = deploy()

        # Create two new wallets with different sets of owners, making sure owner 1 (account) stays the same
        create_tx_1 = factory.createMultiSig(
            [account, accounts[1], accounts[2]], 2, {"from": account}
        )
        create_tx_1.wait(1)
        create_tx_2 = factory.createMultiSig(
            [account, accounts[3], accounts[4]], 2, {"from": account}
        )
        create_tx_2.wait(1)

        # Get both wallets
        wallet_1 = factory.returnWallet(account, 0)
        wallet_2 = factory.returnWallet(account, 1)

        # Assert

        assert factory.getOwners(account, 0) == [account, accounts[1], accounts[2]]
        assert factory.getOwners(account, 1) == [account, accounts[3], accounts[4]]

        assert factory.userToWallets(account, 0) == wallet_1
        assert factory.userToWallets(account, 1) == wallet_2
        assert factory.isOwner(account, wallet_1) == True
        assert factory.isOwner(accounts[3], wallet_2) == True

        with pytest.raises(exceptions.VirtualMachineError):
            factory.userToWallets(
                accounts[1], 1
            )  # account[1] has only one wallet so this will fail
            factory.isOwner(
                accounts[1], wallet_2
            )  # account[1] is not an owner of the second wallet

    return (factory, wallet_1, wallet_2)


def test_submit_transaction():
    account = get_account()
    (factory, wallet_1, wallet_2) = test_create_wallet()

    # Confirm transaction count on both wallets before submitting a transaction

    assert factory.getTransactionCount(account, 0) == 0
    assert factory.getTransactionCount(account, 1) == 0

    # Check that onlyOwner can submit a transaction

    with pytest.raises(exceptions.VirtualMachineError):
        factory.submitTransaction(
            account,
            0,
            accounts[5],
            Web3.toWei(1, "ether"),
            "0x00",
            {"from": accounts[4]},
        )

    # Now submit a transaction on both wallets

    submit_tx_1 = factory.submitTransaction(
        account, 0, accounts[5], Web3.toWei(1, "ether"), "0x00", {"from": account}
    )
    submit_tx_1.wait(1)
    submit_tx_2 = factory.submitTransaction(
        account, 1, accounts[6], Web3.toWei(1, "ether"), "0x00", {"from": account}
    )
    submit_tx_2.wait(1)

    # Check that transaction count has increased for both wallets upon submitting transaction

    assert factory.getTransactionCount(account, 0) == 1
    assert factory.getTransactionCount(account, 1) == 1

    # Check that sender (account) has confirmed the transaction as a result of submitting it. And also that other owners have not yet confirmed

    assert factory.isConfirmed(wallet_1, 0, account) == True
    assert factory.isConfirmed(wallet_1, 0, accounts[1]) == False
    assert factory.isConfirmed(wallet_1, 0, accounts[2]) == False
    assert factory.getTransaction(account, 0, 0) == [
        accounts[5],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        1,
    ]

    assert factory.isConfirmed(wallet_2, 0, account) == True
    assert factory.isConfirmed(wallet_2, 0, accounts[3]) == False
    assert factory.isConfirmed(wallet_2, 0, accounts[4]) == False
    assert factory.getTransaction(account, 1, 0) == [
        accounts[6],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        1,
    ]

    return (factory, wallet_1, wallet_2)


def test_confirm_transaction():
    account = get_account()
    (factory, wallet_1, wallet_2) = test_submit_transaction()

    # Confirm transaction for second user

    confirm_tx_1 = factory.confirmTransaction(accounts[1], 0, 0, {"from": accounts[1]})
    confirm_tx_1.wait(1)
    confirm_tx_2 = factory.confirmTransaction(account, 1, 0, {"from": accounts[3]})
    confirm_tx_2.wait(1)

    # Check that confirmation has happened

    assert factory.isConfirmed(wallet_1, 0, accounts[1]) == True
    assert factory.getTransaction(account, 0, 0) == [
        accounts[5],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        2,
    ]

    assert factory.isConfirmed(wallet_2, 0, accounts[3]) == True
    assert factory.getTransaction(account, 1, 0) == [
        accounts[6],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        2,
    ]

    # Finally check that a non-owner cannot confirm a transaction on a wallet

    with pytest.raises(exceptions.VirtualMachineError):
        factory.confirmTransaction(account, 0, 0, {"from": accounts[4]})
        factory.confirmTransaction(account, 1, 0, {"from": accounts[1]})

    return (factory, wallet_1, wallet_2)


def test_revoke_confirmation():
    account = get_account()
    (factory, wallet_1, wallet_2) = test_confirm_transaction()

    # Revoke transaction for first user on both wallets

    with pytest.raises(exceptions.VirtualMachineError):
        factory.revokeConfirmation(account, 0, 0, {"from": accounts[3]})
        factory.revokeConfirmation(account, 1, 0, {"from": accounts[1]})

    revoke_tx_1 = factory.revokeConfirmation(account, 0, 0, {"from": account})
    revoke_tx_1.wait(1)
    revoke_tx_2 = factory.revokeConfirmation(account, 1, 0, {"from": account})
    revoke_tx_2.wait(1)

    # Check that transaction has been revoked for user 1 (account)

    assert factory.isConfirmed(wallet_1, 0, account) == False
    assert factory.getTransaction(account, 0, 0) == [
        accounts[5],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        1,
    ]

    assert factory.isConfirmed(wallet_2, 0, account) == False
    assert factory.getTransaction(account, 1, 0) == [
        accounts[6],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        1,
    ]

    assert factory.isConfirmed(wallet_1, 0, accounts[1]) == True

    # Revoke transaction for second user on both wallets

    with pytest.raises(exceptions.VirtualMachineError):
        factory.revokeConfirmation(account, 0, 0, {"from": accounts[3]})
        factory.revokeConfirmation(account, 1, 0, {"from": accounts[1]})

    revoke_tx_1_2 = factory.revokeConfirmation(account, 0, 0, {"from": accounts[1]})
    revoke_tx_1_2.wait(1)
    revoke_tx_2_2 = factory.revokeConfirmation(account, 1, 0, {"from": accounts[3]})
    revoke_tx_2_2.wait(1)

    # Check that transaction has been revoked for user 2 on both wallets

    assert factory.isConfirmed(wallet_1, 0, accounts[1]) == False
    assert factory.getTransaction(account, 0, 0) == [
        accounts[5],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        0,
    ]

    assert factory.isConfirmed(wallet_2, 0, accounts[3]) == False
    assert factory.getTransaction(account, 1, 0) == [
        accounts[6],
        Web3.toWei(1, "ether"),
        "0x00",
        False,
        0,
    ]


def test_deposit():
    account = get_account()
    (factory, wallet_1, wallet_2) = test_confirm_transaction()

    # Deposit 1 ether to both wallets, confirm that only owner can deposit from factory to wallets

    with pytest.raises(exceptions.VirtualMachineError):
        factory.deposit(
            account, 0, {"from": accounts[3], "value": Web3.toWei(1, "ether")}
        )
        factory.deposit(
            account, 1, {"from": accounts[1], "value": Web3.toWei(1, "ether")}
        )

    deposit_tx_1 = factory.deposit(
        account, 0, {"from": account, "value": Web3.toWei(1, "ether")}
    )
    deposit_tx_1.wait(1)
    deposit_tx_2 = factory.deposit(
        account, 1, {"from": account, "value": Web3.toWei(1, "ether")}
    )
    deposit_tx_2.wait(1)

    return (factory, wallet_1, wallet_2)


def test_execute_transaction():
    account = get_account()
    (factory, wallet_1, wallet_2) = test_deposit()

    # Execute transaction for both wallets

    with pytest.raises(exceptions.VirtualMachineError):
        factory.executeTransaction(account, 0, 0, {"from": accounts[3]})
        factory.executeTransaction(account, 1, 0, {"from": accounts[1]})

    execute_tx_1 = factory.executeTransaction(account, 0, 0, {"from": account})
    execute_tx_1.wait(1)

    execute_tx_2 = factory.executeTransaction(account, 1, 0, {"from": accounts[3]})
    execute_tx_2.wait(1)

    assert factory.getTransaction(account, 0, 0) == [
        accounts[5],
        Web3.toWei(1, "ether"),
        "0x00",
        True,
        2,
    ]

    assert factory.getTransaction(account, 1, 0) == [
        accounts[6],
        Web3.toWei(1, "ether"),
        "0x00",
        True,
        2,
    ]
