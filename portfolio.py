import os
import requests
import time
import platform

def make_nft_request(collection_slug: str) -> dict:
    r = requests.get(f"https://api.opensea.io/api/v1/collection/{collection_slug}/stats/")
    time.sleep(1)
    try:
        return r.json()['stats']['floor_price']
    except Exception as e:
        print(e)
        return 0

def make_request(currency: str):
    nfts = [nft.replace('NFT_', '') for nft in portfolio if nft.startswith('NFT_')]
    nft_floors = { 'NFT_' + nft: make_nft_request(nft) for nft in nfts }

    r = requests.get('https://api.coingecko.com/api/v3/simple/price', params={'ids': ','.join([cur for cur in portfolio if not cur.startswith('NFT_')]), 'vs_currencies': currency, 'include_24hr_change': 'true'})
    if r.status_code == 200:
        response = r.json()
    else:
        print(f'Request failed. Code: {r.status_code}')
        print(r.content)
        exit(0)

    total = 0

    for nft in nft_floors:
        response[nft] = {currency: round(nft_floors[nft] * response['ethereum'][currency], 2)}

    print(f"{'Coin':<15}{f'Price ({currency})':>10}{'Stack':>20}{f'Holdings ({currency})':>20}")

    for key in response:
        print(f"{key[:14]:<15}{response[key][currency]:>10}{portfolio[key]:>20}{response[key][currency] * portfolio[key]:>20}")
        total += response[key][currency] * portfolio[key]

    print(f'\nTotal ({currency}): {round(total, 2)}')

if __name__ == "__main__":
    with open('portfolio.txt', 'r') as f:
        portfolio = {}
        currency = 'usd'
        refetch = 180
        for line in filter(lambda l: not l.startswith(('#', '\n')), f.readlines()):
            key, value = line.split(':')
            if key not in ('currency', 'refetch'):
                value = float(value)
                portfolio[key] = value
            elif key == 'currency':
                currency = value.strip()
            else:
                refetch = int(value)

    clear = 'cls' if 'Win' in platform.system() else 'clear'
    while True:
        make_request(currency)
        time.sleep(refetch)
        os.system(clear)

