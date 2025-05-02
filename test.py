import requests
import json

url = "https://kpi.knowlarity.com/Basic/v1/account/calllog"
params = {
    "start_time": "2025-04-24 15:55:00+05:30",
    "end_time": "2025-04-25 18:30:00+05:30"
}

headers = {
    'channel': "Basic",
    'x-api-key': "2hlpb3ODYOagdYTw2DKz65p1XBVguQJP74t362XY",
    'authorization': "d5f28fd0-0e75-45eb-91e5-fd05ac9104de",
    'content-type': "application/json",
    'cache-control': "no-cache",
}

response = requests.get(url, headers=headers, params=params)

# Check if the request was successful
if response.status_code == 200:
    try:
        # Attempt to parse the response to JSON
        data = response.json()  # Convert the response to JSON
        
        # Assuming the response is a list of call log entries
        if isinstance(data, list):  # Check if the response is a list
            filtered_data = [entry for entry in data if entry.get("agent_number") == "Call Missed"]
            
            # Printing the filtered data where agent_number is "Call Missed"
            print("Filtered Data: ")
            print(json.dumps(filtered_data, indent=4))  # Pretty-print the filtered data
            
        else:
            print("The response is not in the expected format.")
            print(data)  # Print the raw response if it's not a list or dictionary
    except json.JSONDecodeError:
        print("Error: Unable to parse the response as JSON")
        print(response.text)  # Print the raw response text for debugging
else:
    print(f"Error: {response.status_code}")
    print(response.text)  # Print the error message if the response is not successful
