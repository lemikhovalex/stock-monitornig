import asyncio
import datetime
import os
import typing as tp
from functools import wraps

import click
from binance.client import AsyncClient
from dotenv import load_dotenv

from crawler.connectors import RedisFieldConsumer
from crawler.constants import BINANCE_KLINE_FIELDS


@click.group()
def messages():
    pass


def async_cmd(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


async def _add_ts(x: tp.Coroutine[tp.Any, None, dict], dttm_fld: str = "dttm") -> dict:
    y = await x
    y[dttm_fld] = datetime.datetime.now().timestamp()
    return y


def count_criterion(count: int) -> tp.Callable[[int], bool]:
    def inner(x: int) -> bool:
        return x <= count

    return inner


def succes_criterion(**kwargs) -> tp.Callable[[int], bool]:
    def inner(x: int):
        return True

    return inner


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("count", default=1, type=int)
@click.argument("tickers", default="BTCUSDT,ETHUSDT")
@async_cmd
async def price_crawler(count: int, tickers: str):

    print(load_dotenv())
    api_secret = os.getenv("BINANCE_API_KEY")
    api_key = os.getenv("BINANCE_API_SECRET")
    symbols = tickers.split(",")

    if count == 0:
        stop_criterion = succes_criterion()
    else:
        stop_criterion = count_criterion(count)

    client = await AsyncClient.create(api_key, api_secret)
    k = 0
    while stop_criterion(k):
        tasks = [_add_ts(client.get_avg_price(symbol=s)) for s in symbols]
        prices = await asyncio.gather(*tasks)
        print(prices, k)
        k += 1
    await client.close_connection()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("count", default=1, type=int)
@click.argument("tickers", default="ETHUSDT")
@click.argument("consumer", default="redis")
@async_cmd
async def candle_crawler(count: int, tickers: str, consumer: str):

    load_dotenv()
    api_secret = os.getenv("BINANCE_API_KEY")
    api_key = os.getenv("BINANCE_API_SECRET")

    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT"))

    symbols = tickers.split(",")

    if consumer == "redis":
        cons = RedisFieldConsumer(host=redis_host, port=redis_port)
    else:
        raise KeyError

    if count == 0:
        stop_criterion = succes_criterion()
    else:
        stop_criterion = count_criterion(count)

    client = await AsyncClient.create(api_key, api_secret)
    k = 0
    while stop_criterion(k):
        tasks = [
            client.get_klines(
                symbol=s,
                interval=AsyncClient.KLINE_INTERVAL_1MINUTE,
                limit=1,
            )
            for s in symbols
        ]
        klines = await asyncio.gather(*tasks)
        klines = [
            {k: float(v) for k, v in zip(BINANCE_KLINE_FIELDS, kl[0])} for kl in klines
        ]

        data = {t: d for t, d in zip(symbols, klines)}
        await cons.consume(data)
        k += 1
    await client.close_connection()


commands = [price_crawler, candle_crawler]

for command in commands:
    messages.add_command(command)


if __name__ == "__main__":
    messages()
