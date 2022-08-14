from gameactions import app
2	from botocore.exceptions import ClientError
3	
4	import uuid
5	import json
6	from unittest import mock
7	
8	NEW_GAME_EVENT = {
9	        "requestContext": {
10	            "connectionId" : "connection-123"
11	        }
12	    }
13	
14	JOIN_GAME_EVENT = {
15	        "requestContext": {
16	            "connectionId" : "connection-joining-123"
17	        },
18	        "body" : json.dumps({"gameid" : "01234567012301230123012345678901"})
19	    }
20	
21	START_GAME_EVENT = {
22	    "body" : json.dumps({"gameid" : "01234567012301230123012345678901"})
23	}
24	
25	ANSWER_EVENT = {
26	        "requestContext": {
27	            "connectionId" : "connection-answer-123"
28	        },
29	        "body" : json.dumps({
30	            "gameid" : "01234567012301230123012345678901",
31	            "questionid" : "q-1234",
32	            "answer" : "Answer"
33	            })
34	    }
35	
36	QUESTION_EVENT = {
37	        "gameid" : "01234567012301230123012345678901",
38	        "questions" : [{ "id" : "q-1234", "question" : "Question?", "answer" : "Answer"}],
39	        "iterator" : { "questionpos" : 0 }
40	}
41	
42	SCORES_EVENT = {
43	        "gameid" : "01234567012301230123012345678901",
44	        "questions" : [
45	            { "id" : "q-1111", "question" : "Good question?", "answer" : "Yes"},
46	        ],
47	        "iterator" : { "questionpos" : 0 }
48	}
49	
50	SCORES_EVENT_TWO = {
51	        "gameid" : "01234567012301230123012345678901",
52	        "questions" : [
53	            { "id" : "q-1111", "question" : "Good question?", "answer" : "Yes"},
54	            { "id" : "q-1112", "question" : "Second question?", "answer" : "Yes"},
55	        ],
56	        "iterator" : { "questionpos" : 0 }
57	}
58	
59	
60	def test_trivia_newgame(mocker):
61	    # create mocks
62	    mocker.patch.object(app, 'TABLE')
63	    mocker.patch.object(app, 'MANAGEMENT')
64	    mocker.patch('uuid.uuid4', return_value=uuid.UUID('01234567-0123-0123-0123-012345678901'))
65	    mocker.patch('random.choice', side_effect=lambda seq: seq[0])
66	
67	
68	    # call the lambda entry point
69	    app.trivia_newgame(NEW_GAME_EVENT, None)
70	
71	    # assert we call dynamo with a row for the game
72	    app.TABLE.put_item.assert_called_with(
73	        Item={
74	            "gameId":"01234567012301230123012345678901",
75	            "connectionId": "connection-123",
76	            'playerName': 'AliceBlue',
77	            "score": 0
78	            })
79	
80	    # assert the post_to_connection calls to the connection that created the game
81	    app.MANAGEMENT.post_to_connection.assert_has_calls([
82	        mock.call(Data='{"action": "gamecreated", "gameId": "01234567012301230123012345678901"}', ConnectionId='connection-123'),
83	        mock.call(Data='{"action": "playerlist", "players": [{"connectionId": "connection-123", "currentPlayer": true, "playerName": "AliceBlue", "score": 0}]}',
84	          ConnectionId='connection-123')
85	        ])
86	
87	def test_trivia_joingame(mocker):
88	    # create mocks
89	    mocker.patch.object(app, 'TABLE')
90	    mocker.patch.object(app, 'MANAGEMENT')
91	    mocker.patch('random.choice', side_effect=lambda seq: seq[0])
92	
93	    # mock the response from the game table
94	    app.TABLE.query.return_value = {'Items':[{'connectionId': "connection-1", "playerName" : "AliceBlue", "score" : "10"}]}
95	
96	    # call the lambda entry point
97	    app.trivia_joingame(JOIN_GAME_EVENT, None)
98	
99	    # assert we insert the joined player
100	    app.TABLE.put_item.assert_called_with(
101	        Item={
102	            'gameId': '01234567012301230123012345678901',
103	            'connectionId': 'connection-joining-123',
104	            'playerName': 'AliceBlue',
105	            'score': 0
106	            })
107	    # assert the post_to_connection sends a new player list
108	    app.MANAGEMENT.post_to_connection.assert_called_with(
109	        Data='{"action": "playerlist", "players": [{"connectionId": "connection-1", "playerName": "AliceBlue", "score": 10, "currentPlayer": true}]}', ConnectionId='connection-1'
110	    )
111	
112	def test_trivia_startgame(mocker):
113	    # create mocks
114	    mocker.patch.object(app, 'TABLE')
115	    mocker.patch.object(app, 'MANAGEMENT')
116	    mocker.patch.object(app, 'STEPFUNCTIONS')
117	
118	    # mock the response from the game table
119	    app.TABLE.query.return_value = {'Items':[{'connectionId': "connection-1", "playerName" : "AliceBlue", "score" : "10"}]}
120	
121	    # call the lambda entry point
122	    app.trivia_startgame(START_GAME_EVENT, None)
123	
124	    # assert call to stepfunctions
125	    assert app.STEPFUNCTIONS.start_execution.call_count == 1
126	
127	    # assert the gamestarted is sent
128	    app.MANAGEMENT.post_to_connection.assert_called_with(
129	        Data='{"action": "gamestarted"}', ConnectionId='connection-1'
130	    )
131	
132	def test_trivia_answer(mocker):
133	    # create mocks
134	    mocker.patch.object(app, 'TABLE')
135	
136	    # call the lambda entry point
137	    app.trivia_answer(ANSWER_EVENT, None)
138	
139	    # assert we updated the game item
140	    app.TABLE.update_item.assert_called_with(
141	        Key={'gameId': '01234567012301230123012345678901', 'connectionId': 'connection-answer-123'},
142	        AttributeUpdates={'lastQuestionId': {'Value': 'q-1234', 'Action': 'PUT'}, 'lastAnswer': {'Value': 'Answer', 'Action': 'PUT'}}
143	    )
144	
145	def test_trivia_question(mocker):
146	    # create mocks
147	    mocker.patch.object(app, 'TABLE')
148	    mocker.patch.object(app, 'MANAGEMENT')
149	
150	    # mock the response from the game table
151	    app.TABLE.query.return_value = {'Items':[{'connectionId': "connection-1", "playerName" : "AliceBlue", "score" : "10"}]}
152	
153	    # call the lambda entry point
154	    app.trivia_question(QUESTION_EVENT, None)
155	
156	    app.MANAGEMENT.post_to_connection.assert_called_with(
157	        Data='{"action": "question", "question": {"id": "q-1234", "question": "Question? 1/1"}}',
158	        ConnectionId='connection-1'
159	    )
160	
161	
162	
163	def test_trivia_calculate_scores_correct(mocker):
164	    mocker.patch.object(app, 'TABLE')
165	    mocker.patch.object(app, 'MANAGEMENT')
166	
167	    # mock a correct response from the game table
168	    app.TABLE.query.return_value = {'Items':[
169	        {
170	            "connectionId": "connection-1",
171	            "gameId": "01234567012301230123012345678901",
172	            "playerName" : "AliceBlue",
173	            "lastAnswer": "Yes",
174	            "lastQuestionId": "q-1111",
175	            "score": 0
176	        }
177	    ]}
178	
179	    app.trivia_calculate_scores(SCORES_EVENT, None)
180	
181	    # assert we updated the game item, score is incremented
182	    app.TABLE.update_item.assert_called_with(
183	        Key={'gameId': '01234567012301230123012345678901', 'connectionId': 'connection-1'},
184	        AttributeUpdates={'score': {'Value': 10, 'Action': 'PUT'}}
185	    )
186	
187	    app.MANAGEMENT.post_to_connection.assert_has_calls([
188	        mock.call(Data='{"action": "playerlist", "players": [{"connectionId": "connection-1", "playerName": "AliceBlue", "score": 10, "currentPlayer": true}]}', ConnectionId='connection-1'),
189	        mock.call(Data='{"action": "gameover"}', ConnectionId='connection-1')
190	        ])
191	
192	
193	def test_trivia_calculate_scores_wrong(mocker):
194	    mocker.patch.object(app, 'TABLE')
195	    mocker.patch.object(app, 'MANAGEMENT')
196	
197	    # mock a correct response from the game table
198	    app.TABLE.query.return_value = {'Items':[
199	        {
200	            "connectionId": "connection-1",
201	            "gameId": "01234567012301230123012345678901",
202	            "playerName" : "AliceBlue",
203	            "lastAnswer": "No",
204	            "lastQuestionId": "q-1111",
205	            "score": 0
206	        }
207	    ]}
208	
209	    app.trivia_calculate_scores(SCORES_EVENT_TWO, None)
210	
211	    # score not incremented
212	    app.MANAGEMENT.post_to_connection.assert_called_with(
213	        Data='{"action": "playerlist", "players": [{"connectionId": "connection-1", "playerName": "AliceBlue", "score": 0, "currentPlayer": true}]}',
214	        ConnectionId='connection-1'
215	    )
216	
217	
218	def test_broadcast_connection_gone(mocker):
219	    # create mocks
220	    mocker.patch.object(app, 'TABLE')
221	    mocker.patch.object(app, 'MANAGEMENT')
222	
223	    # mock the response from the game table
224	    app.TABLE.query.return_value = {'Items':[{'connectionId': "connection-1", "playerName" : "AliceBlue", "score" : "10"}]}
225	
226	    app.MANAGEMENT.post_to_connection.side_effect = ClientError(
227	        {
228	            'Error': {'Code': 'GoneException'}
229	        },
230	        'PostToConnection'
231	    )
232	
233	    app.send_broadcast("01234567012301230123012345678901", {})
234	
235	
236	def test_broadcast_other_error(mocker):
237	    # create mocks
238	    mocker.patch.object(app, 'TABLE')
239	    mocker.patch.object(app, 'MANAGEMENT')
240	
241	    # mock the response from the game table
242	    app.TABLE.query.return_value = {'Items':[{'connectionId': "connection-1", "playerName" : "AliceBlue", "score" : "10"}]}
243	
244	    app.MANAGEMENT.post_to_connection.side_effect = ClientError(
245	        {
246	            'Error': {'Code': 'Anything'}
247	        },
248	        'PostToConnection'
249	    )
250	    app.send_broadcast("01234567012301230123012345678901", {})
