from brownie import accounts, network, exceptions
from helpful_scripts import get_account
from scripts.deploy_factory import deploy, TESTNETS, owners
import pytest
from web3 import Web3


def test_create_wallet():
    if network.show_active() in TESTNETS:
        account = get_account()
        factory = deploy()

        # Create two new wallets with different sets of owners, making sure owner 1 (account) stays the same
        create_tx_1 = factory.createMultiSig(
            [account, owners[0], owners[1]], 2, {"from": account}
        )
        create_tx_1.wait(1)
        create_tx_2 = factory.createMultiSig(
            [account, owners[2], owners[3]], 2, {"from": account}
        )
        create_tx_2.wait(1)

        # Get both wallets
        wallet_1 = factory.returnWallet(account, 0, {"from": account})
        wallet_2 = factory.returnWallet(account, 1, {"from": account})

        # Assert

        assert factory.getOwners(account, 0, {"from": account}) == [
            account,
            owners[0],
            owners[1],
        ]
        assert factory.getOwners(account, 1, {"from": account}) == [
            account,
            owners[2],
            owners[3],
        ]

        with pytest.raises(exceptions.VirtualMachineError):
            factory.getOwners(account, 0, {"from": owners[4]})

        assert factory.userToWallets(account, 0, {"from": account}) == wallet_1
        assert factory.userToWallets(account, 1, {"from": account}) == wallet_2
        assert factory.isOwner(account, wallet_1, {"from": account}) == True
        assert factory.isOwner(owners[3], wallet_2, {"from": account}) == True
        assert (
            factory.isOwner(owners[1], wallet_2, {"from": account}) == False
        )  # owner[1] is not an owner of the second wallet

    else:
        pytest.skip()

    return (factory, wallet_1, wallet_2)
