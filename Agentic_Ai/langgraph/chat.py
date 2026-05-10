from dotenv import load_dotenv
import os
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START , END
from langchain_groq import ChatGroq

#from langchain.chat.models import init_chat_model
load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
llm =ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)


class State(TypedDict):
    messages:Annotated[list,add_messages]

def chatbot(state:State):
    #print("\n\n this is inside from chatbot node ,state :",state)
    response = llm.invoke(state.get("messages"))
    return {"messages":[response]}

def samplenode(state:State):

    print("\n\n this is inside from samplenode node ,state :",state)
    return{"messages":["these is from sample node"]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot",chatbot) #here we register chatbot function as a node, and also we named it chatbot.
graph_builder.add_node("samplenode",samplenode)
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)

graph=graph_builder.compile()
updated_state= graph.invoke(State({"messages":["Hi, my name is lakshya"]})) #you need to pass initial state when you invoke the graph
print("\n\n updated state :",updated_state)

#(START) -> chatbot -> samplenode -> (END) 





#state={messages: ["hey there"]}
#node runs:chatbot(state:["hi this is a message from chatbot node"])
#appending new state with prevous state
#final state will be {"messages":["hey there","hi this is a message from chatbot node"]}

