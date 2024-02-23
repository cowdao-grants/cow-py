from cow_py.subgraphs.base.query import GraphQLQuery
from cow_py.subgraphs.base.client import GraphQLClient
from cow_py.subgraphs.deployments import build_subgraph_url, SubgraphEnvironment


class CoWSubgraph(GraphQLClient):
    def get_url(self, chain):
        # TODO: add a nice way to change the environment
        return build_subgraph_url(chain, SubgraphEnvironment.PRODUCTION)


class CoWSubgraphQuery(GraphQLQuery):
    def get_client(self):
        return CoWSubgraph(self.chain)
