# import asyncio
# import httpx
# from rest_framework.views import APIView
# from rest_framework.response import Response
# import datetime
# import pytz
# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()

# X_API_KEY = os.getenv("X_API_KEY")
# AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")

# class AsyncUnattendedMissedCallsView(APIView):

#     async def fetch_page(self, client, url, headers, params):
#         try:
#             response = await client.get(url, headers=headers, params=params)
#             response.raise_for_status()
#             return response.json()
#         except httpx.HTTPError as e:
#             print(f"Error fetching page: {e}")
#             return None

#     async def get_all_call_logs(self, url, headers, start_time, end_time, limit=500):
#         async with httpx.AsyncClient() as client:
#             # First call to get total count
#             params = {
#                 'start_time': start_time,
#                 'end_time': end_time,
#                 'limit': limit,
#                 'offset': 0
#             }
#             first_response = await self.fetch_page(client, url, headers, params)
#             if not first_response:
#                 return []

#             total_count = first_response.get('meta', {}).get('total_count', 0)
#             tasks = [self.fetch_page(client, url, headers, {
#                 'start_time': start_time,
#                 'end_time': end_time,
#                 'limit': limit,
#                 'offset': offset
#             }) for offset in range(0, total_count, limit)]

#             results = await asyncio.gather(*tasks)
#             all_calls = []
#             for res in results:
#                 if res and 'objects' in res:
#                     all_calls.extend(res['objects'])
#             return all_calls

#     def get(self, request):
#         try:
#             india_timezone = pytz.timezone('Asia/Kolkata')
#             now_india = datetime.datetime.now(india_timezone)
#             start_time = (now_india - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
#             end_time = now_india.strftime("%Y-%m-%dT%H:%M:%S")

#             url = 'https://kpi.knowlarity.com/Basic/v1/account/calllog'
#             headers = {
#                 'x-api-key': X_API_KEY,
#                 'authorization': AUTHORIZATION_TOKEN,
#                 'content-type': "application/json",
#             }

#             all_calls = asyncio.run(self.get_all_call_logs(url, headers, start_time, end_time))


#             # Debug: Print the full API response data
#             print("=== All Calls Fetched ===")
#             for call in all_calls:
#                 print(json.dumps(all_calls[:100], indent=4))





#             if not all_calls:
#                 return Response({"message": "No calls in last 24 hours."}, status=200)

#             all_calls.sort(key=lambda x: x.get('start_time', ''))  # Oldest to newest

#             attended_calls = {}
#             unattended_missed_calls = []

#             # First collect latest attended calls
#             for call in all_calls:
#                 agent = call.get('agent_number', '')
#                 customer = call.get('customer_number', '')
#                 call_time = call.get('start_time', '')

#                 if not customer:
#                     continue

#                 if agent != 'Call Missed':
#                     attended_calls[customer] = max(call_time, attended_calls.get(customer, ''))

#             # Then find missed calls which are not followed by attended ones
#             for call in all_calls:
#                 agent = call.get('agent_number', '')
#                 customer = call.get('customer_number', '')
#                 call_time = call.get('start_time', '')

#                 if not customer or agent != 'Call Missed':
#                     continue

#                 if call_time > attended_calls.get(customer, ''):
#                     unattended_missed_calls.append({
#                         "customer_number": customer,
#                         "missed_time": call_time
#                     })


#                     # Debug: Print the final result before returning
#                     # print("=== Unattended Missed Calls ===")
#                     # print(unattended_missed_calls)

#             return Response({"unattended_missed_calls": unattended_missed_calls}, status=200)

#         except Exception as e:
#             return Response({"error": str(e)}, status=500)






import asyncio
import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime
import pytz
from dotenv import load_dotenv
import os

load_dotenv()

X_API_KEY = os.getenv("X_API_KEY")
AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")


class AsyncUnattendedMissedCallsView(APIView):

    async def fetch_page(self, client, url, headers, params):
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"[ERROR] Fetching page failed: {e}")
            return None

    async def get_all_call_logs(self, url, headers, start_time, end_time, limit=500):
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Initial request to get total count
            params = {
                'start_time': start_time,
                'end_time': end_time,
                'limit': limit,
                'offset': 0
            }
            initial_data = await self.fetch_page(client, url, headers, params)
            if not initial_data:
                return []

            total_count = initial_data.get('meta', {}).get('total_count', 0)
            tasks = [
                self.fetch_page(client, url, headers, {
                    'start_time': start_time,
                    'end_time': end_time,
                    'limit': limit,
                    'offset': offset
                }) for offset in range(0, total_count, limit)
            ]
            results = await asyncio.gather(*tasks)
            all_calls = [call for result in results if result for call in result.get('objects', [])]
            return all_calls

    def get(self, request):
        try:
            india_tz = pytz.timezone('Asia/Kolkata')
            now = datetime.datetime.now(india_tz)
            start_time = (now - datetime.timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
            end_time = now.strftime("%Y-%m-%dT%H:%M:%S")

            url = 'https://kpi.knowlarity.com/Basic/v1/account/calllog'
            headers = {
                'x-api-key': X_API_KEY,
                'authorization': AUTHORIZATION_TOKEN,
                'content-type': "application/json",
            }

            all_calls = asyncio.run(self.get_all_call_logs(url, headers, start_time, end_time))
            if not all_calls:
                return Response({"message": "No call logs found in the last 24 hours."}, status=200)

            # Sort all calls chronologically
            all_calls.sort(key=lambda x: x.get('start_time', ''))

            attended_calls = {}
            unattended_missed_calls = []

            # Track last attended call per customer
            for call in all_calls:
                agent = call.get('agent_number', '')
                customer = call.get('customer_number', '')
                call_time = call.get('start_time', '')

                if customer and agent not in ['Call Missed', 'NA', '', None]:
                    attended_calls[customer] = max(call_time, attended_calls.get(customer, ''))

            # Identify missed calls that are not followed by attended calls
            for call in all_calls:
                agent = call.get('agent_number', '')
                customer = call.get('customer_number', '')
                call_time = call.get('start_time', '')

                if customer and agent in ['Call Missed', 'NA']:
                    if call_time > attended_calls.get(customer, ''):
                        unattended_missed_calls.append({
                            "customer_number": customer,
                            "missed_time": call_time
                        })

            return Response({"unattended_missed_calls": unattended_missed_calls}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
