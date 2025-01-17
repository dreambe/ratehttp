import asyncio
import time
from typing import Any, Dict, List

import aiohttp
from tqdm import tqdm


# class TentacleSession(aiohttp.ClientSession(TCPConnector(ssl=False))):
class RateSession(aiohttp.ClientSession):
    """RatesSession is a wrapper around the aiohttp.ClientSession, where it introduces the retry and rate functionality
    missing in the default aiohttp.ClientSession.

       Args:
           sleep (float): The time the client will sleep after each request.
           retries (int): The number of retries for a successful request.
           retry_sleep (float): The time service sleeps between nonsuccessful request calls. Defaults to 1.0.

       Return:
           RateSession(aiohttp.ClientSession)
    """

    retries: int
    retry_sleep: float = 1.0

    def __init__(self, retries=3, retry_sleep=1.0, **kwargs):
        self.retries = retries
        self.retry_sleep = retry_sleep
        super().__init__(raise_for_status=True, **kwargs)

    def __retry__(self, func, **kwargs) -> Any:
        attempts = 0
        error = Exception()
        while attempts < self.retries:
            try:
                return func(**kwargs)
            except Exception as error:
                attempts += 1
                error = error
                time.sleep(self.retry_sleep)

        raise error

    def get(self, **kwargs) -> Any:
        return self.__retry__(func=super().get, **kwargs)

    def patch(self, **kwargs) -> Any:
        return self.__retry__(func=super().patch, **kwargs)

    def post(self, **kwargs) -> Any:
        return self.__retry__(func=super().post, **kwargs)

    def put(self, **kwargs) -> Any:
        return self.__retry__(func=super().put, **kwargs)

    def request(self, **kwargs) -> Any:
        return self.__retry__(func=super().request, **kwargs)


class RateHttp:
    """Initiates the Rate client.
    Args:
        rate (Optional[float]): The rate per second limits of the endpoint; default to no limit.
        connections (Optional[int]): Maximum connections on the given endpoint, defaults to 5.
        ssl (Optional[bool]): Enable SSL for the requests, defaults to True.

    Returns:
        RateHttp
    """

    def __init__(
        self,
        rate: float = None,
        connections: int = 5,
        retries: int = 3,
        ssl: bool = True,
    ):

        self.rate = rate
        self.connections = connections
        self.retries = retries
        self.ssl = ssl

    def get_coroutine(self, req_list: List[Dict[str, Any]], func: callable):

        async def __limit__(
            rate: float,
            retries: int,
            connections: int,
            req_list: List[Dict[str, Any]],
            func: callable,
        ) -> List[Any]:

            resp_list: Dict = {}
            progress_bar = tqdm(total=len(req_list))
            sleep = 1 / rate if rate else 0

            async def func_mod(session: RateSession, request: Dict, itr: int):
                resp = await func(session, request)
                resp_list[itr] = resp
                progress_bar.update()

            conn = aiohttp.TCPConnector(limit_per_host=connections, ssl=self.ssl)
            async with RateSession(
                retries=retries,
                retry_sleep=sleep * self.connections * 2.0 if rate else 1.0,
                connector=conn,
            ) as session:

                tasks = set()
                itr = 0
                for req in req_list:
                    if len(tasks) >= self.connections:
                        _done, tasks = await asyncio.wait(
                            tasks, return_when=asyncio.FIRST_COMPLETED
                        )
                    tasks.add(asyncio.create_task(func_mod(session, req, itr)))
                    await asyncio.sleep(sleep)
                    itr += 1
                await asyncio.wait(tasks)
                return [value for (key, value) in sorted(resp_list.items())]

        return __limit__(self.rate, self.retries, self.connections, req_list, func)

    def execute(self, req_list: List[Dict[str, Any]], func: callable) -> List[Any]:
        """Execute the requests given the functions instruction.

        Empower asyncio libraries for performing parallel executions of the user-defined function.
        Given a list of requests, the result is ordered list of what the user-defined function returns.

        Args:
            requests_list (List[Dict[str, Any]): The list of requests in a dictionary format, e.g.
            [{"url": "http://example.com", "params": {...}, "body": {...}}..]
            func (callable): The user-defined function to execute, this function takes in the following arguments.
                Args:
                    session (RateSession): The RateLimit wrapper around the aiohttp.ClientSession.
                    request (Dict): The request within the req_list above.

        Returns:
            List(func->return)
        """

        result = asyncio.run(self.get_coroutine(req_list, func))
        if result:
            return result
        return []
