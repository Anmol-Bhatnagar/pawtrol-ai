import logging
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)


def get_checkpointer() -> BaseCheckpointSaver:
    """
    Creates and returns a checkpoint saver for LangGraph memory.
    Defaults to an in-memory saver for stateless container instances.

    For production environments, swap this with:
    - SqliteSaver (from langgraph.checkpoint.sqlite)
    - PostgresSaver (from langgraph.checkpoint.postgres)
    """
    logger.info(
        "Initializing memory checkpointer: using default in-memory MemorySaver."
    )
    return MemorySaver()
