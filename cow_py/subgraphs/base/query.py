from abc import ABC, abstractmethod

from cow_py.common.chains import Chain
from cow_py.subgraphs.base.client import GraphQLClient


class GraphQLQuery(ABC):
    def __init__(self, chain=Chain.MAINNET, variables=dict()) -> None:
        self.chain = chain
        self.variables = variables

    @abstractmethod
    def get_query(self) -> str:
        pass

    @abstractmethod
    def get_client(self) -> GraphQLClient:
        pass

    async def execute(self):
        query = self.get_query()
        client = self.get_client()
        return await client.__class__.query(self.chain, query, self.variables)
