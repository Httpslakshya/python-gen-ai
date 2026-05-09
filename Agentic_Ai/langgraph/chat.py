from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph

class State(TypedDict):
    messages:Annotated[list,add_messages]

graph_builder = StateGraph(State)
