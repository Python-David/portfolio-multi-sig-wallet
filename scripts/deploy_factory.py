from brownie import accounts, network, config, MultiSigFactory
from helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, FORKED_ENV

owners = [
    "0xC7e8810b45c8fA9e2797dCC5ae94fE2380210cAE",
    "0xF2C610eB50ba2D5467D7CCFd484f5f560052F923",
    "0xACBD67FbFD7130A95126CAe4fB42F08CD58106E7",
    "0xB398D90f912D18FdeE08F853bE34848D6D2E1C4A",
    "0x2Cbd70C84b205e4AF35E5238Acd4a27A53eDb4e9",
]

TESTNETS = ["goerli"]


def deploy():
    account = get_account()
    print(account)
    if network.show_active() == "deployment":
        multi_sig_factory = MultiSigFactory.deploy(
            {"from": account},
            publish_source=config["networks"][network.show_active()]["verify"],
        )
    else:
        multi_sig_factory = MultiSigFactory.deploy(
            {"from": account},
            publish_source=config["networks"][network.show_active()]["verify"],
        )

    return multi_sig_factory


def main():
    deploy()
