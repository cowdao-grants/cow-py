from abc import ABC, abstractmethod

from cow_py.common.chains import Chain

import json
import logging

import httpx


class GraphQLError(Exception):
    pass


async def gql(url, query, variables={}):
    logging.debug(f"Executing query: {query[:15]}")
    logging.debug(f"URL: {url}")
    logging.debug(f"Variables: {variables}")
    async with httpx.AsyncClient() as client:
        r = await client.post(
            url,
            json=dict(query=query, variables=variables),
        )
        logging.debug(f"Response status: {r.status_code}")
        logging.debug(f"Response body: {r.text}")
        r.raise_for_status()

    try:
        return r.json().get("data", r.json())
    except KeyError:
        print(json.dumps(r.json(), indent=2))
        raise GraphQLError


class GraphQLClient(ABC):
    def __init__(self, chain) -> None:
        self.url = self.get_url(chain)

    async def instance_query(self, query, variables=dict()):
        return await gql(self.url, query, variables=variables)

    @abstractmethod
    def get_url(self, chain) -> str:
        pass

    @classmethod
    async def query(cls, chain=Chain.MAINNET, query=None, variables=dict()):
        if not query:
            raise ValueError("query must be provided")

        client = cls(chain)
        return await client.instance_query(query, variables)
