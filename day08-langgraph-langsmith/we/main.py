from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import graph,StateGraph, START,END
from pydantic import BaseModel
import os
from typing_extensions import TypedDict
from langsmith.wrappers import wrap_openai


load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

client = wrap_openai(OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
))

# llm schema

class DetectCallResponse(BaseModel):
    is_question_ai: bool

class CodingAIResponse(BaseModel):
    answer: str 



# step-1 define state schema------------------
# The `State` class is a Python TypedDict that contains attributes for user message, AI message, and a

class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool

# step 2 - crate nodes and routin nodes------------------

# normal nodes

def detect_query(state = State):

    user_meassage = state.get('user_message')

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is related
    to coding question or not.
    Return the response in specified JSON boolean only.
    """

    res = client.beta.chat.completions.parse(
        model='gemini-1.5-flash',
        response_format=DetectCallResponse,
        messages=[
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":user_meassage}
        ]
    )

    state['is_coding_question'] = res.choices[0].message.parsed.is_question_ai
    
    return state


def solve_coding_question(state:State):
    user_meassage = state.get('user_message')

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to resolve the user query based on coding 
    problem he is facing
    """

    res = client.beta.chat.completions.parse(
        model='gemini-1.5-pro',
        response_format=CodingAIResponse,
        messages=[
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":user_meassage}
        ]
    )

    state['ai_message'] = res.choices[0].message.parsed.answer
    return state

def solve_simple_question(state:State):
    user_meassage = state.get('user_message')

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to chat with user
    """

    res = client.beta.chat.completions.parse(
        model='gemini-2.0-flash',
        response_format=CodingAIResponse,
        messages=[
            {"role":"system", "content":SYSTEM_PROMPT},
            {"role":"user", "content":user_meassage}
        ]
    )

    state['ai_message'] = res.choices[0].message.parsed.answer
    return state

# routing node

def route_edge(state:State):

    is_coding_question = state.get('is_coding_question')

    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question" 


# step 3 - create state-graph builder------------------

graph_builder = StateGraph(State)


# staep 4 - adding nodes and route nodes in graph builder------------------

graph_builder.add_node('detect_query',detect_query)
graph_builder.add_node('solve_coding_question',solve_coding_question)
graph_builder.add_node('solve_simple_question',solve_simple_question)
graph_builder.add_node('route_edge',route_edge)

# step 5 - add edges to nodes/routenodes from Start to End------------------

graph_builder.add_edge(START,'detect_query')
graph_builder.add_conditional_edges('detect_query',route_edge)

graph_builder.add_edge('solve_coding_question',END)
graph_builder.add_edge('solve_simple_question',END)

# step 6 - compiling state graph------------------

graph = graph_builder.compile()

# step 7 - run the graph ------------------

def run_graph():
    state = {
        "user_message": "what is node js",
        "ai_message": "",
        "is_coding_question": False
    }

    res = graph.invoke(state)

    print('response', res)

run_graph()

