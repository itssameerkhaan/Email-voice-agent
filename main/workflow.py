import os
import time

from langgraph.graph import StateGraph, START, END
# from typing import TypedDict

from node import content,create_query,varify_query,log_emil,line_varify,route_varify_query,fetching,deleteBackups
from node import state

# class state(TypedDict):
#     content : str
#     query : str
#     query_varification : bool

graph = StateGraph(state)

#-----NODE
graph.add_node('content',content)
graph.add_node('create_query',create_query)
graph.add_node('varify_query', varify_query)
graph.add_node('login_to_email',log_emil)
graph.add_node('fetching',fetching)
graph.add_node('deleteBackups',deleteBackups)


#-----EDGES
graph.add_edge(START,'content')
graph.add_conditional_edges('content',line_varify,{True:'create_query',False:'content'})
graph.add_edge('create_query', 'varify_query')
graph.add_conditional_edges('varify_query', route_varify_query, {
    'yes': 'login_to_email',
    'no': 'create_query'
})
graph.add_conditional_edges('login_to_email',line_varify,{True:'fetching',False:'content'})
graph.add_conditional_edges('fetching',line_varify,{True:'deleteBackups',False:'content'})
graph.add_edge('deleteBackups',END)
# graph.add_edge('login_to_email',END)



initial_state = {
    "content": "",
    "query": "",
    "query_verification": False,
    "update_query":""
}

def run():
    workflow = graph.compile()
    WATCH_FOLDER = r"D:\langGraph\email_agent\audio"
    while True:
        
            mp3_file = [f for f in os.listdir(WATCH_FOLDER) if f.lower().endswith(".mp3")]
            if mp3_file:
                print(f"Found WAV files: {mp3_file}")
                final_state = workflow.invoke(initial_state)
                print("FINAL STATE IS :-",final_state)
            time.sleep(2)

run()