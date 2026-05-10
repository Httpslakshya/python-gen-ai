from dotenv import load_dotenv
import os
from typing_extensions import TypedDict
from openai import OpenAI
#from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START , END
from typing import Optional,Literal
load_dotenv()


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1" 
)

class State(TypedDict):
    user_query:str
    llm_output:Optional[str]
    is_good:Optional[bool]



def chatbot(state:State):
    print("ChatBot Node",state)
    response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",             
                temperature=0.2,            # lower = more reliable JSON
                messages=[
                    {"role":"system", "content":state.get("user_query") },
                ]
            )
    state["llm_output"]= response.choices[0].message.content
    return state


def evaluate_response(state: State) -> Literal["chatbot_gemini","endnode"]:
    print("evaluate Node",state)
    if True:
        return "endnode"
    return "chatbot_gemini"

def chatbot_gemini(state: State):
    print("ChatBot_gemini Node",state)
    response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",             
                temperature=0.2,            # lower = more reliable JSON
                messages=[
                    {"role":"system", "content":state.get("user_query") },
                ]
            )
    state["llm_output"]= response.choices[0].message.content
    return state

def endnode(state:State):
    print("end Node",state)
    return state


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("chatbot_gemini",chatbot_gemini)
graph_builder.add_node("endnode",endnode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot",evaluate_response)
# graph_builder.add_conditional_edges(
#     "chatbot",
#     evaluate_response,
#     {
#         "chatbot_gemini": "chatbot_gemini",
#         END: END  # ← explicitly tell LangGraph that END is a valid destination
#     }
# )
graph_builder.add_edge("chatbot_gemini","endnode")
graph_builder.add_edge("endnode",END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"user_query": "hey , What is 2+2?"}))
print(updated_state)
