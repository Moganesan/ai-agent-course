from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools=[
    {
        "type": "function",
        "name":"get_all_calandar_events",
        "description":"Get all the events from the calandar by the given date",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {"type": "string", "description": "The start time of the event in the format of YYYY-MM-DDTHH:MM:SS+05:30"},
                "end_time": {"type": "string", "description": "The end time of the event in the format of YYYY-MM-DDTHH:MM:SS+05:30"}
            },
            "required": ["start_time", "end_time"]
        },
    },
    {
        "type": "function",        # <-- FIXED HERE
        "name":"create_calandar_event",
        "description":"Create a new event in the calandar",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the event"},
                "description": {"type": "string", "description": "The description of the event"},
                "start_time": {"type": "string", "description": "The start time of the event in the format of YYYY-MM-DDTHH:MM:SS+05:30"},
                "end_time": {"type": "string", "description": "The end time of the event in the format of YYYY-MM-DDTHH:MM:SS+05:30"},
            },
            "required": ["title", "description", "start_time", "end_time"]
        },
    }
]

system_prompt = "You are a helpful ai agent that can help users to manage calandar events you can use the get_all_calandar_events with start_time and end_time to get the events before calling the get_all_calandar_events function make sure you get the required dates from the user when calling the get_all_calandar_events function make sure you pass start_time and end_time in this format YYYY-MM-DDTHH:MM:SS+05:30 then respode the users with the events. you can also use the create_calandar_event function to create a new event in the calandar make sure you pass the required details such as summary, description, start_time, end_time and make sure you pass the timing in this format YYYY-MM-DDTHH:MM:SS+05:30"

def get_all_calandar_events(start_time, end_time):
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {
        "Authorization": f"Bearer {os.getenv('GOOGLE_CALANDAR_ACCESS_TOKEN')}"
    }
    params = {
        "timeMin": f"{start_time}",
        "timeMax": f"{end_time}",
        "singleEvents": True,
    }
    try:
        response = requests.get(url, headers=headers, params=params)
    except Exception as e:
        print("Exception while calling the google calandar API:",e)
        return {"error":"request failed","details":str(e)}
    print(response.json()["items"])
    return response.json()["items"]


def create_calandar_event(title, description, start_time, end_time):
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {
        "Authorization": f"Bearer {os.getenv('GOOGLE_CALANDAR_ACCESS_TOKEN')}"
    }
    data = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": f"{start_time}"
        },
        "end": {
            "dateTime": f"{end_time}"
        },
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

input_list= [
    {
        "role":"user",
        "content":"What are the events for 2025-12-04?"
    }
]

response = client.responses.create(
    model="gpt-4o-mini",
    instructions=system_prompt,
    tools=tools,
    input=input_list
)

print(json.dumps(response.to_dict(), indent=4))

# save function call output for subsequent use
input_list += response.output

for item in response.output:
    if item.type == "function_call":
        if item.name == "get_all_calandar_events":
            arguments = json.loads(item.arguments)
            events = get_all_calandar_events(arguments["start_time"], arguments["end_time"])
            input_list.append({
                "type":"function_call_output",
                "call_id":item.call_id,
                "output":json.dumps({"events": events})
            })

response = client.responses.create(model="gpt-4o-mini", instructions=system_prompt, tools=tools, input=input_list)

print(json.dumps(response.to_dict(), indent=4))