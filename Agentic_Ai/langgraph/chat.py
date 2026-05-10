from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START , END

class State(TypedDict):
    messages:Annotated[list,add_messages]

def chatbot(state:State):
    print("this is inside from chatbot node ,state :",state)
    return {"messages":["hi this is a messge from chatbot node"]}

def samplenode(state:State):

    print("this is inside from samplenode node ,state :",state)
    return{"messages":["these is from sample node"]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot",chatbot) #here we register chatbot function as a node, and also we named it chatbot.
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)

graph=graph_builder.compile()


#(START) -> chatbot -> samplenode -> (END) 





#state={messages: ["hey there"]}
#node runs:chatbot(state:["hi this is a message from chatbot node"])
#appending new state with prevous state
#final state will be {"messages":["hey there","hi this is a message from chatbot node"]}

