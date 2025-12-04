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
    response = requests.get(url, headers=headers, params=params)
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

response = client.responses.create(
    model="gpt-4o-mini",
    instructions="You are a helpful ai agent that can help users to manage calandar events you can use the get_all_calandar_events with start_time and end_time to get the events before calling the get_all_calandar_events function make sure you get the required dates from the user when calling the get_all_calandar_events function make sure you pass start_time and end_time in this format YYYY-MM-DDTHH:MM:SS+05:30 then respode the users with the events. you can also use the create_calandar_event function to create a new event in the calandar make sure you pass the required details such as summary, description, start_time, end_time and make sure you pass the timing in this format YYYY-MM-DDTHH:MM:SS+05:30",
    tools=tools,
    input="What are the events for the next 7 days?"
)

print(json.dumps(response.to_dict(), indent=4))