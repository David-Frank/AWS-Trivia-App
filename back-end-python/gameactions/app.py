"Backend for the trivia game"
2	import json
3	import os
4	import random
5	import uuid
6	
7	import boto3
8	import yaml
9	from botocore.exceptions import ClientError
10	
11	DYNAMODB = boto3.resource('dynamodb')
12	TABLE = DYNAMODB.Table(os.getenv('TABLE_NAME'))
13	MANAGEMENT = boto3.client('apigatewaymanagementapi', endpoint_url=os.getenv('APIGW_ENDPOINT'))
14	STEPFUNCTIONS = boto3.client('stepfunctions')
15	COLORS = ("AliceBlue,AntiqueWhite,Aqua,Aquamarine,Azure,Beige,Bisque,Black,BlanchedAlmond,Blue,"
16	"BlueViolet,Brown,BurlyWood,CadetBlue,Chartreuse,Chocolate,Coral,CornflowerBlue,Cornsilk,Crimson,"
17	"Cyan,DarkBlue,DarkCyan,DarkGoldenrod,DarkGray,DarkGreen,DarkKhaki,DarkMagenta,DarkOliveGreen,"
18	"DarkOrange,DarkOrchid,DarkRed,DarkSalmon,DarkSeaGreen,DarkSlateBlue,DarkSlateGray,DarkTurquoise,"
19	"DarkViolet,DeepPink,DeepSkyBlue,DimGray,DodgerBlue,FireBrick,FloralWhite,ForestGreen,Fuchsia,"
20	"Gainsboro,GhostWhite,Gold,Goldenrod,Gray,Green,GreenYellow,Honeydew,HotPink,IndianRed,Indigo,"
21	"Ivory,Khaki,Lavender,LavenderBlush,LawnGreen,LemonChiffon,LightBlue,LightCora,LightCyan,"
22	"LightGoldenrodYellow,LightGreen,LightGrey,LightPink,LightSalmon,LightSeaGreen,LightSkyBlue,"
23	"LightSlateGray,LightSteelBlu,LightYellow,Lime,LimeGreen,Linen,Magenta,Maroon,MediumAquamarine,"
24	"MediumBlue,MediumOrchid,MediumPurple,MediumSeaGreen,MediumSlateBlue,MediumSpringGreen,"
25	"MediumTurquoise,MediumVioletRed,MidnightBlue,MintCream,MistyRose,Moccasin,NavajoWhite,Navy,"
26	"OldLace,Olive,OliveDrab,Orange,OrangeRed,Orchid,PaleGoldenrod,PaleGreen,PaleTurquoise,"
27	"PaleVioletRed,PapayaWhip,PeachPuff,Peru,Pink,Plum,PowderBlue,Purple,Red,RosyBrown,RoyalBlue,"
28	"SaddleBrown,Salmon,SandyBrown,SeaGreen,Seashell,Sienna,Silver,SkyBlue,SlateBlue,SlateGray,Snow,"
29	"SpringGreen,SteelBlue,Tan,Teal,Thistle,Tomato,Turquoise,Violet,Wheat,White,WhiteSmoke,Yellow,"
30	"YellowGreen").split(",")
31	WAIT_SECONDS = 5
32	
33	SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
34	with open(os.path.join(SCRIPT_PATH, "all-questions.yaml"), 'r', encoding="utf-8") as stream:
35	    QUESTIONS = yaml.safe_load(stream)
36	
37	def get_random_player_name():
38	    "Generate a random player name"
39	    return random.choice(COLORS)
40	
41	def get_body_param(event, param):
42	    "Load JSON body content and get the value of a property"
43	    body = json.loads(event["body"])
44	    value = body[param]
45	    return value
46	
47	def get_players(game_id):
48	    "Query dynamo for a list of game players"
49	    connections = TABLE.query(
50	        KeyConditionExpression=boto3.dynamodb.conditions.Key("gameId").eq(game_id)
51	    )
52	    return [{
53	        "connectionId" : p["connectionId"],
54	        "playerName": p["playerName"],
55	        "score": int(p["score"])
56	        } for p in connections["Items"]]
57	
58	def send_broadcast(connections, data):
59	    "Post out websocket messages to a list of connection ids"
60	    for connection in connections:
61	        try:
62	            if "action" in data and data["action"] == "playerlist":
63	                # we need to insert "currentPlayer" into player list broadcasts
64	                for player in data["players"]:
65	                    player["currentPlayer"] = (connection==player["connectionId"])
66	
67	            MANAGEMENT.post_to_connection(
68	                Data=json.dumps(data),
69	                ConnectionId=connection
70	            )
71	        except ClientError as error:
72	            if error.response['Error']['Code'] == 'GoneException':
73	                print("Missing connection ", connection)
74	
75	def trivia_newgame(event, _):
76	    "Lambda function to intitate a new game"
77	    game_id = uuid.uuid4().hex
78	
79	    # write the connection and game id into the dynamo table
80	    connection_id = event["requestContext"]["connectionId"]
81	    player_name = get_random_player_name()
82	    connection = {
83	        "gameId": game_id,
84	        "connectionId": connection_id,
85	        "playerName": player_name,
86	        "score": 0
87	    }
88	    TABLE.put_item(Item=connection)
89	
90	    # send game created
91	    MANAGEMENT.post_to_connection(
92	        Data=json.dumps({"action": "gamecreated", "gameId": game_id}),
93	        ConnectionId=connection_id
94	    )
95	
96	    # send player list of single player
97	    MANAGEMENT.post_to_connection(
98	        Data=json.dumps({"action": "playerlist", "players": [
99	            {
100	                "connectionId" : connection_id,
101	                "currentPlayer" : True,
102	                "playerName": player_name,
103	                "score": 0
104	            }
105	        ]}),
106	        ConnectionId=connection_id
107	    )
108	
109	    return {
110	        "statusCode": 200,
111	        "body": 'Game created.'
112	    }
113	
114	def trivia_joingame(event, _):
115	    "Lambda function to join a game"
116	    connection_id = event["requestContext"]["connectionId"]
117	    game_id = get_body_param(event, "gameid")
118	
119	    # write the new connection into the dynamo table
120	    connection = {
121	        "gameId": game_id,
122	        "connectionId": connection_id,
123	        "playerName": get_random_player_name(),
124	        "score": 0
125	    }
126	    TABLE.put_item(Item=connection)
127	
128	    players = get_players(game_id)
129	    send_broadcast(
130	        [p["connectionId"] for p in players],
131	        {"action": "playerlist", "players": players}
132	    )
133	
134	    return {
135	        "statusCode": 200,
136	        "body": 'Joined game.'
137	    }
138	
139	
140	def trivia_startgame(event, _):
141	    "Lambda function to start a game"
142	    game_id = get_body_param(event, "gameid")
143	    state_machine = os.getenv("STATE_MACHINE")
144	
145	    questions = QUESTIONS.copy()
146	    random.shuffle(questions)
147	    questions = questions[:10]
148	
149	    machine_input = {
150	        "gameid": game_id,
151	        "questions": questions,
152	        "waitseconds": WAIT_SECONDS,
153	        "iterator": {
154	            "questionpos": 0,
155	            "IsGameOver": False
156	        }
157	    }
158	
159	    STEPFUNCTIONS.start_execution(
160	        stateMachineArn=state_machine,
161	        name=f"game-{game_id}",
162	        input=json.dumps(machine_input)
163	    )
164	
165	    players = get_players(game_id)
166	    send_broadcast([p["connectionId"] for p in players], {"action": "gamestarted"})
167	
168	    return {
169	        "statusCode": 200,
170	        "body": 'Joined game.'
171	    }
172	
173	
174	def trivia_answer(event, _):
175	    "Lambda function for a player to post an answer"
176	    game_id = get_body_param(event, "gameid")
177	    questionid = get_body_param(event, "questionid")
178	    answer = get_body_param(event, "answer")
179	    connection_id = event["requestContext"]["connectionId"]
180	
181	    TABLE.update_item(
182	        Key={"gameId": game_id, "connectionId": connection_id},
183	        AttributeUpdates={
184	            "lastQuestionId": {'Value': questionid, "Action": "PUT"},
185	            "lastAnswer": {'Value': answer, "Action": "PUT"}
186	        }
187	    )
188	
189	    return {
190	        "statusCode": 200,
191	        "body": 'Recieved answer.'
192	    }
193	
194	def trivia_question(event, _):
195	    "Send a question - called from statemachine"
196	    game_id = event["gameid"]
197	    question_pos = event["iterator"]["questionpos"]
198	    questions = event["questions"]
199	    question = event["questions"][question_pos]
200	    del question["answer"]
201	    question["question"] += f" {question_pos+1}/{len(questions)}"
202	
203	    players = get_players(game_id)
204	    send_broadcast([
205	        p["connectionId"] for p in players],
206	        {"action": "question", "question": question}
207	    )
208	
209	    return True
210	
211	def trivia_calculate_scores(event, _):
212	    "Calc scores for a game - called from statemachine"
213	    game_id = event["gameid"]
214	    question_pos = event["iterator"]["questionpos"]
215	    questions = event["questions"]
216	    question = event["questions"][question_pos]
217	
218	    connections = TABLE.query(
219	        KeyConditionExpression=boto3.dynamodb.conditions.Key("gameId").eq(game_id)
220	    )
221	
222	    # spin thru the connections and check their answers
223	    players = []
224	    for connection in connections["Items"]:
225	        connection_id = connection["connectionId"]
226	        player_name = connection["playerName"]
227	        score = int(connection["score"])
228	        last_question_id = connection["lastQuestionId"] if "lastQuestionId" in connection else ""
229	        last_answer = connection["lastAnswer"] if "lastAnswer" in connection else ""
230	
231	        if last_question_id == question["id"] and last_answer == question["answer"]:
232	            score += 10
233	            TABLE.update_item(
234	                Key={"gameId": game_id, "connectionId": connection_id},
235	                AttributeUpdates={"score": {'Value': score, "Action": "PUT"}}
236	            )
237	
238	        players.append({
239	            "connectionId" : connection_id,
240	            "playerName" : player_name,
241	            "score": score
242	        })
243	
244	    # notify everyone the scores
245	    send_broadcast(
246	        [c["connectionId"] for c in connections["Items"]],
247	        {"action": "playerlist", "players": players}
248	    )
249	
250	    question_pos += 1
251	    game_over = question_pos >= len(questions)
252	    if game_over:
253	        send_broadcast(
254	             [c["connectionId"] for c in connections["Items"]],
255	             {"action": "gameover"}
256	        )
257	
258	    return {
259	                "questionpos": question_pos,
260	                "IsGameOver": game_over
261	            }
