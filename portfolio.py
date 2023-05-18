import os
import requests
import time
import platform


def make_nft_request(collection_slug: str) -> dict:
    r = requests.get(
        f"https://api.opensea.io/api/v1/collection/{collection_slug}/stats/"
    )
    time.sleep(1)
    try:
        return r.json()["stats"]["floor_price"] or 0
    except Exception as e:
        print(e)
        return 0


def make_request(
    portfolio: dict,
    currency: str,
    refetch: int,
    show_btc: bool,
    show_eth: bool,
    clear: str,
):
    nfts = [nft.replace("NFT_", "") for nft in portfolio if nft.startswith("NFT_")]
    nft_floors = {"NFT_" + nft: make_nft_request(nft) for nft in nfts}

    if (
        show_btc or show_eth
    ):  # fetch btc or eth values if the user wants to but doesn't have any.
        if "bitcoin" not in portfolio:
            portfolio["bitcoin"] = 0
        if "ethereum" not in portfolio:
            portfolio["ethereum"] = 0

    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": ",".join([cur for cur in portfolio if not cur.startswith("NFT_")]),
            "vs_currencies": currency,
            "include_24hr_change": "true",
        },
    )
    if r.status_code == 200:
        response = r.json()
    else:
        print(f"Request failed. Code: {r.status_code}")
        print(r.content)
        return

    for nft in nft_floors:
        response[nft] = {
            currency: round(nft_floors[nft] * response["ethereum"][currency], 2)
        }

    os.system(clear)
    print(
        f"{'Coin':<15}{f'Price ({currency})':>10}{'Stack':>20}{f'Holdings ({currency})':>20}"
    )

    total = 0

    for key in response:
        print(
            f"{key[:14]:<15}{response[key][currency]:>10}{portfolio[key]:>20}{round(response[key][currency] * portfolio[key], 2):>20}"
        )
        total += response[key][currency] * portfolio[key]

    btc_total = total / response["bitcoin"][currency]
    eth_total = total / response["ethereum"][currency]

    print(f"\nTotal ({currency}): {round(total, 2)}")
    if show_btc:
        print(f"\nTotal (btc): {round(btc_total, 2)}")
    if show_eth:
        print(f"\nTotal (eth): {round(eth_total, 2)}")


if __name__ == "__main__":
    with open("portfolio.txt", "r") as f:
        portfolio = {}
        options = ("currency", "refetch", "show-btc-value", "show-eth-value")
        currency = "usd"
        refetch = 180
        show_btc = False
        show_eth = False
        lines = filter(lambda l: not l.startswith(("#", "\n")), f.readlines())
        keys_values = [tuple(line.split(":")) for line in lines]

        for k, v in filter(lambda tup: tup[0] not in options, keys_values):
            portfolio[k] = float(v)

        for k, v in filter(lambda tup: tup[0] in options, keys_values):
            if k == "currency":
                currency = v.strip()
            elif k == "refetch":
                refetch = int(v)
            elif k == "show-btc-value" and v.strip().lower() == "true":
                show_btc = True
            elif k == "show-eth-value" and v.strip().lower() == "true":
                show_eth = True

    clear = "cls" if "Win" in platform.system() else "clear"
    while True:
        make_request(portfolio, currency, refetch, show_btc, show_eth, clear)
        time.sleep(refetch)
