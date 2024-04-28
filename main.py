import json
import requests

import re

config = json.load(open("config.json"))

MIN_SPREAD = config['minSpread']
MAX_SPREAD = config['maxSpread']
ALLOWED_QUOTES = config['allowedQuotes']
MIN_TRADING_VOLUME = config['minTradingVolume']
MAX_TRADING_VOLUME = config['maxTradingVolume']
START_RANK_POSITION = config['startRankPosition']




def getData(links) -> list:
    data = list()

    for link in links:
      try:
        coin = re.split('https://cryptorank\.io/price/|/arbitrage', link)[1]
        response = requests.get(f'https://api.cryptorank.io/v0/coins/{coin}/tickers?includeQuote=false').json()

        allowedData = []
        exchanges = list()
        
        for i in range(len(response['data'])):
                if len(response['data']) > 1 and response['data'][i]['to'] in ALLOWED_QUOTES:
                 if "usdVolume" in response['data'][i] and response['data'][i]["usdVolume"] > MIN_TRADING_VOLUME:
                    if "usdLast" in response['data'][i]:
                        allowedData.append(response['data'][i])
                        exchanges.append({
                            'exchange_name': response['data'][i]['exchangeName'],
                            "volume": response['data'][i]['usdVolume'],
                            "usd_last": response['data'][i]['usdLast'],
                        })
      except Exception as e:
            print(coin)
        
      pairs = list()
      for i in range(len(allowedData)):
            for j in range(len(allowedData)):
                if i == j:
                    continue

                firstExchange = allowedData[i]
                secondExchange = allowedData[j]

                spread = 100 * (float(firstExchange['usdLast']) - float(secondExchange['usdLast'])) / float(
                    firstExchange['usdLast'])
                if MIN_SPREAD <= spread <= MAX_SPREAD:
                    coinName = allowedData[0]['coinName']
                    pairs.append({
                        secondExchange['exchangeName']: secondExchange['url'],
                        firstExchange['exchangeName']: firstExchange['url'],
                        "scheme": f"{secondExchange['exchangeName']} [BUY] -> {firstExchange['exchangeName']} [SELL]",
                        "spread": spread
                    })

      if len(exchanges) > 0 and len(pairs) > 0:
            scheme = {
                "name": coin,
                "url": f'https://cryptorank.io/price/{coin}',
                "exchanges": list(exchanges),
                "pairs": list(pairs)
            }
            data.append(scheme)

    return data



with open("tokens.json", "r") as file:
    data = json.load(file)

links = [("https://cryptorank.io/price/"+datum['key']+"/arbitrage") for datum in data]

data = getData(links)

with open('data.json', 'w', encoding='utf-8') as f:
    print(f"Output Data: {len(data)}")
    json_data = {"data": data}
    json.dump(json_data, f, ensure_ascii=False, indent=4)
