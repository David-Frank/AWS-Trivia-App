import os
2	from unittest import TestCase
3	
4	import boto3
5	import requests
6	import asyncio
7	import websockets
8	import json
9	
10	"""
11	Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test.
12	"""
13	
14	
15	class TestApiGateway(TestCase):
16	    api_endpoint: str
17	
18	    @classmethod
19	    def get_stack_name(cls) -> str:
20	        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
21	        if not stack_name:
22	            raise Exception(
23	                "Cannot find env var AWS_SAM_STACK_NAME. \n"
24	                "Please setup this environment variable with the stack name where we are running integration tests."
25	            )
26	
27	        return stack_name
28	
29	    def setUp(self) -> None:
30	        """
31	        Based on the provided env variable AWS_SAM_STACK_NAME,
32	        here we use cloudformation API to find out what the TriviaWebSocketApi URL is
33	        """
34	        stack_name = TestApiGateway.get_stack_name()
35	
36	        client = boto3.client("cloudformation")
37	
38	        try:
39	            response = client.describe_stacks(StackName=stack_name)
40	        except Exception as e:
41	            raise Exception(
42	                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
43	            ) from e
44	
45	        stacks = response["Stacks"]
46	
47	        stack_outputs = stacks[0]["Outputs"]
48	        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "TriviaWebSocketApi"]
49	        self.assertTrue(api_outputs, f"Cannot find output TriviaWebSocketApi in stack {stack_name}")
50	
51	        self.api_endpoint = api_outputs[0]["OutputValue"]
52	
53	    def test_api_gateway(self):
54	        asyncio.get_event_loop().run_until_complete(self.simulate_game(self.api_endpoint))
55	
56	    async def simulate_game(self, uri):
57	        async with websockets.connect(uri, compression=None) as websocket:
58	            # intitial new game
59	            print(f"sending websocket to {uri}")
60	            await websocket.send(json.dumps({"action":"newgame"}))
61	            game_created_message = json.loads(await websocket.recv())
62	            print(game_created_message)
63	
64	            # start the game
65	            game_id = game_created_message['gameId']
66	            await websocket.send(json.dumps({"action":"startgame", "gameid": game_id}))
67	
68	            # player list
69	            player_list_message = json.loads(await websocket.recv())
70	            print(player_list_message)
71	            # game started
72	            game_start_message= json.loads(await websocket.recv())
73	            print(game_start_message)
74	
75	            # questions
76	            for i in range(10):
77	                # question
78	                question_message = json.loads(await websocket.recv())
79	                print(question_message)
80	                options = question_message['question']['options']
81	                question_id = question_message['question']['id']
82	
83	                # send an answer
84	                await websocket.send(json.dumps({
85	                "action": "answer",
86	                "gameid": game_id,
87	                "questionid": question_id,
88	                "answer": options[0]
89	                }))
90	
91	                # get the list / scores update
92	                player_list_message = json.loads(await websocket.recv())
93	                print(player_list_message)
