## About
ratehttp is fork from octopus-api based on aiohttp, and ratehttp provides ssl-verify setting feature

ratehttp is simple; it combines the [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://docs.aiohttp.org/en/stable/) and [octopus-api](https://github.com/FilipByren/octopus-api) library's functionality and makes sure the requests follows the constraints set by the contract.

## Installation
`pip install ratehttp`

## PyPi
https://pypi.org/project/ratehttp/


## Get started
To start RateHttp, you first initiate the client, setting your constraints. 
```python
client = RateHttp(rate=100, connections=10, retries=5, sll=False)
client = RateHttp(connections=10, retries=3, sll=True)
```
After that, you will specify what you want to perform on the endpoint response. This is done within a user-defined function.
```python
async def patch_data(session: RateSession, request: Dict):
    async with session.patch(url=request["url"], data=requests["data"], params=request["params"]) as response:
        body = await response.json()
        return body["id"]
```

As RateHttp `RateSession` uses [aiohttp](https://docs.aiohttp.org/en/stable/) under the hood, the resulting  way to write 
**POST**, **GET**, **PUT** and **PATCH** for aiohttp will be the same for RateHttp. The only difference is the added functionality of 
retries and optional rate limit.

Finally, you finish everything up with the `execute` call for the RateHttp client, where you provide the list of requests dicts and the user function.
The execute call will then return a list of the return values defined in user function. As the requests list is a bounded stream we return the result in order.


```python
result: List = client.execute(requests_list=[
    {
        "url": "http://localhost:3000",
        "data": {"id": "a", "first_name": "filip"},
        "params": {"id": "a"}
    },
    {
        "url": "http://localhost:3000",
        "data": {"id": "b", "first_name": "morris"},
        "params": {"id": "b"} 
    }
    ] , func=patch_data)
```


### Examples

Optimize the request based on max connections constraints:
```python
from ratehttp import RateSession, RateHttp
from typing import Dict, List

if __name__ == '__main__':
    async def fetch_data(session: RateSession, request: Dict):
        async with session.get(url=request["url"], params=request["params"]) as response:
            body = await response.text()
            return body


    client = RateHttp(connections=100)
    result: List = client.execute(requests_list=[{
        "url": "http://google.com",
        "params": {}}] * 100, func=fetch_data)
    print(result)

```

Optimize the request based on rate limit and connections limit:
```python
from ratehttp import RateSession, RateHttp
from typing import Dict, List

if __name__ == '__main__':
    async def fetch_data(session: RateSession, request: Dict):
        async with session.get(url=request["url"], params=request["params"]) as response:
            body = await response.json()
            return body

    client = RateHttp(rate=50, resolution="sec", connections=6)
    result: List = client.execute(requests_list=[{
        "url": "https://api.pro.coinbase.com/products/ETH-EUR/candles?granularity=900&start=2021-12-04T00:00:00Z&end=2021-12-04T00:00:00Z",
        "params": {}}] * 1000, func=fetch_data)
    print(result)
```

