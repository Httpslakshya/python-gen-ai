from dotenv import load_dotenv
import os
from langgraph.checkpoint.mongodb import MongoDBSaver
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START , END
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

model = init_chat_model(
    "llama-3.3-70b-versatile",
    model_provider="groq"
)


class State(TypedDict):
    messages:Annotated[list,add_messages]

def chatbot(state:State):
   
    response = model.invoke(state.get("messages"))
    return {"messages":[response]}



graph_builder = StateGraph(State)
graph_builder.add_node("chatbot",chatbot) 

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot",END)


graph=graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)
    
   
        
MONGODB_URI = "mongodb://admin:admin@localhost:27017"
with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)

    config = {
        "configurable": {
            "thread_id": "lakshya"
        }
    }

    for chunk in  graph_with_checkpointer.stream(
        State({"messages":["what am i learning"]}),
        config,
        stream_mode="values"
        ):
            chunk["messages"][-1].pretty_print()

    

#on checkpointer(lakshya)= Hi, my name is lakshya will be save