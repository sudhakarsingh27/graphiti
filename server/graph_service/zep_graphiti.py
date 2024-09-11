from typing import Annotated

from fastapi import Depends
from graphiti_core import Graphiti  # type: ignore
from graphiti_core.edges import EntityEdge  # type: ignore
from graphiti_core.llm_client import LLMClient  # type: ignore
from graphiti_core.nodes import EntityNode  # type: ignore

from graph_service.config import ZepEnvDep
from graph_service.dto import FactResult


class ZepGraphiti(Graphiti):
    def __init__(self, uri: str, user: str, password: str, llm_client: LLMClient | None = None):
        super().__init__(uri, user, password, llm_client)

    async def save_entity_node(self, name: str, uuid: str, group_id: str, summary: str = ''):
        new_node = EntityNode(
            name=name,
            uuid=uuid,
            group_id=group_id,
            summary=summary,
        )
        await new_node.generate_name_embedding(self.llm_client.get_embedder())
        await new_node.save(self.driver)
        return new_node


async def get_graphiti(settings: ZepEnvDep):
    client = ZepGraphiti(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    try:
        yield client
    finally:
        client.close()


def get_fact_result_from_edge(edge: EntityEdge):
    return FactResult(
        uuid=edge.uuid,
        name=edge.name,
        fact=edge.fact,
        valid_at=edge.valid_at,
        invalid_at=edge.invalid_at,
        created_at=edge.created_at,
        expired_at=edge.expired_at,
    )


ZepGraphitiDep = Annotated[ZepGraphiti, Depends(get_graphiti)]