from brownie import accounts, network, config, MultiSigWallet
from helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, FORKED_ENV

owners = [
    "0xC7e8810b45c8fA9e2797dCC5ae94fE2380210cAE",
    "0xF2C610eB50ba2D5467D7CCFd484f5f560052F923",
]

TESTNETS = ["goerli"]


def deploy():
    account = get_account()

    if network.show_active() == "development":
        multi_sig_wallet = MultiSigWallet.deploy(
            [account, accounts[1], accounts[2]],
            2,
            {"from": account},
            publish_source=config["networks"][network.show_active()]["verify"],
        )
    elif network.show_active() in TESTNETS:
        multi_sig_wallet = MultiSigWallet.deploy(
            [account, owners[0], owners[1]],
            2,
            {"from": account},
            publish_source=config["networks"][network.show_active()]["verify"],
        )

    print(account)

    return multi_sig_wallet


def main():
    deploy()
