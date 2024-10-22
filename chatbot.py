import getpass
import os
import openai
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Set up the environment variable
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPEN_API_KEY")

# Define the structure of the state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create the graph builder
graph_builder = StateGraph(State)

# Initialize OpenAI API key
openai.api_key = os.getenv("OPEN_API_KEY")

# Helper function to convert user messages into OpenAI format
def convert_messages_to_openai_format(messages):
    formatted_messages = []

    for message in messages:
        if hasattr(message, 'content'):
            # If it's a HumanMessage or similar object, we extract the content and map role
            formatted_messages.append({
                "role": "user",  # You can map the role accordingly, or derive it from the object
                "content": message.content
            })
        elif isinstance(message, tuple):
            # Handling the case where message is a tuple (role, content)
            role, content = message
            formatted_messages.append({
                "role": role,
                "content": content
            })
        elif isinstance(message, dict):
            # If message is already a dict, just pass it along
            formatted_messages.append(message)
        else:
            raise ValueError(f"Invalid message format: {message}")  # Print problematic message
    return formatted_messages

# Define the chatbot function
def chatbot(state: dict):
    # Convert the messages to OpenAI format
    formatted_messages = convert_messages_to_openai_format(state["messages"])

    # Call OpenAI API with valid model name
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Correct the model name here
        messages=formatted_messages
    )

    # Extract and return the assistant's reply
    assistant_reply = response["choices"][0]["message"]["content"]
    return {"messages": [("assistant", assistant_reply)]}

# Add the chatbot node to the graph
graph_builder.add_node("chatbot", chatbot)

# Define the graph edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# Function to stream graph updates (for conversation)
def stream_graph_updates(user_input: str):
    # Send the user's message to the graph
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            # Print the assistant's response
            print("Assistant:", value["messages"][-1][1])  # Extract content from tuple

# Main loop to handle user input and chat
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # Fallback if input() is not available (for testing environments)
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break





# import getpass
# import os


# def _set_env(var: str):
#     if not os.environ.get(var):
#         os.environ[var] = getpass.getpass(f"{var}: ")


# _set_env("OPEN_API_KEY")


# from typing import Annotated

# from typing_extensions import TypedDict

# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages


# class State(TypedDict):
#     # Messages have the type "list". The `add_messages` function
#     # in the annotation defines how this state key should be updated
#     # (in this case, it appends messages to the list, rather than overwriting them)
#     messages: Annotated[list, add_messages]


# graph_builder = StateGraph(State)

# import openai
# # Initialize OpenAI with the API key from the environment
# openai.api_key = os.getenv("OPEN_API_KEY")


# def chatbot(state: dict):
#     # Prepare the messages for OpenAI (assuming state["messages"] is a list of user and assistant messages)
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=state["messages"]
#     )

#     # Extract the assistant's reply from the response
#     return {"messages": [response["choices"][0]["message"]["content"]]}


# # The first argument is the unique node name
# # The second argument is the function or object that will be called whenever
# # the node is used.
# graph_builder.add_node("chatbot", chatbot)


# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_edge("chatbot", END)
# graph = graph_builder.compile()

# # from IPython.display import Image, display

# # try:
# #     display(Image(graph.get_graph().draw_mermaid_png()))
# # except Exception:
# #     # This requires some extra dependencies and is optional
# #     pass

# def stream_graph_updates(user_input: str):
#     for event in graph.stream({"messages": [("user", user_input)]}):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)


# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break

#         stream_graph_updates(user_input)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break
