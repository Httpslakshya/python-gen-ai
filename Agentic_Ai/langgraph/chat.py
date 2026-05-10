from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph

class State(TypedDict):
    messages:Annotated[list,add_messages]

def samplenode(state:State):

    return{"messages":["these is from sample node"]}

def chatbot(state:State):

    return {"messages":["hi this is a messge from chatbot node"]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot",chatbot)#here we register chatbot function as a node, and also we named it chatbot.

#here chatbot is a node that append ["hi this is a..."]with the initial message given by user, after graph envoke.
#final state will be {"messages":["hey there","hi this is a message from chatbot node"]}

