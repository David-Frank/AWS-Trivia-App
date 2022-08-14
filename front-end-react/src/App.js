import React, { useState } from 'react';
2	import { Row, Col, Card, Button, Container, Form, ListGroup, Badge, Spinner, Jumbotron} from 'react-bootstrap';
3	import { CountdownCircleTimer } from 'react-countdown-circle-timer'
4	import { WebsocketEndpoint } from './config'
5	
6	var TRIVIA_STEP = {
7	  STEP_GETSTARTED : {value: 0},
8	  STEP_JOINGAME: {value: 1},
9	  STEP_WAITING : {value: 2},
10	  STEP_QUESTIONS : {value: 3},
11	  STEP_GAMEOVER : {value: 4},
12	};
13	
14	function GetStarted(props) {
15	  if (props.currentStep !== TRIVIA_STEP.STEP_GETSTARTED) {
16	    return null
17	  }
18	
19	  return (<Card>
20	    <Card.Body>
21	      <Card.Title>Get Started</Card.Title>
22	      <Card.Text>
23	        Click the button below to start a new game.
24	      </Card.Text>
25	      <Button variant="primary" onClick={props.onNewGame}>Create a New Game</Button>
26	    </Card.Body>
27	  </Card>);
28	}
29	
30	function JoinGame(props) {
31	  if (props.currentStep !== TRIVIA_STEP.STEP_JOINGAME) {
32	    return null
33	  }
34	  return (
35	    <Card>
36	      <Card.Body>
37	        <Card.Title>Join Game</Card.Title>
38	        <Card.Text>
39	          You've been invited to join a game!
40	        </Card.Text>
41	        <Button variant="primary" onClick={props.onJoinGame}>Join</Button>
42	      </Card.Body>
43	    </Card>
44	  );
45	}
46	
47	function Waiting(props) {
48	  if (props.currentStep !== TRIVIA_STEP.STEP_WAITING) {
49	    return null
50	  }
51	  const invitelink = new URL(`#newgame/${props.gameId}`, document.baseURI).href;
52	  const inviteBody = (props.gameId) ? (
53	    <Card.Text>
54	      Share the link below with players joining the game
55	      <Form.Control type="text" value={invitelink} readOnly />
56	      <Button variant="primary" onClick={props.onStartGame}>Start Game</Button>
57	    </Card.Text>
58	    ) : (
59	      <Spinner animation="grow" variant="secondary" />
60	  );
61	
62	  return (
63	    <Card>
64	      <Card.Body>
65	        <Card.Title>Waiting for players</Card.Title>
66	        {inviteBody}
67	      </Card.Body>
68	    </Card>
69	  );
70	}
71	
72	function Questions(props) {
73	  const [activeButton, setActiveButton] = useState(null);
74	
75	  const answerClick = (key, id, option) => {
76	    props.onAnswer(id, option);
77	    setActiveButton(key);
78	  }
79	
80	  if (props.currentStep !== TRIVIA_STEP.STEP_QUESTIONS) {
81	    return null
82	  }
83	
84	  var questionBody = !props.question ? (
85	    <Spinner animation="grow" variant="secondary" />
86	  ) : (
87	    <Col lg="8">
88	      <b>{props.question.question}</b>
89	      <div className="d-grid gap-2">
90	      {props.question.options.map((option, i) => {
91	        const myKey = props.question.id + "-" + i;
92	        return (
93	          <Button
94	           key={myKey}
95	           variant={activeButton===myKey ? "success" : "secondary"}
96	           onClick={() => answerClick(myKey, props.question.id, option)}
97	           size="lg" block>
98	            {option}
99	          </Button>
100	        )
101	      })}
102	      </div>
103	    </Col>
104	  );
105	
106	  return (
107	    <Card>
108	      <Card.Body>
109	        <Card.Title>Let's Play!</Card.Title>
110	          {questionBody}
111	      </Card.Body>
112	    </Card>
113	  );
114	}
115	
116	function Players(props) {
117	  if (!props.playerList) {
118	    return null;
119	  }
120	  return (
121	    <Card>
122	      <Card.Body>
123	        <Card.Title>Players</Card.Title>
124	
125	        <ListGroup>
126	        {props.playerList && props.playerList.filter((player)=>player.currentPlayer).map((player, i) => {
127	            return (<ListGroup.Item key={player.connectionId} variant="primary" className="d-flex justify-content-between align-items-center">
128	              <span style={{color:player.playerName}}>&#11044; <span className="small" style={{color:"Black"}}>{player.playerName}</span></span>
129	              <Badge pill variant="dark">{player.score}</Badge>
130	            </ListGroup.Item>)
131	         })}
132	         </ListGroup>
133	         <p></p>
134	         <ListGroup>
135	        {props.playerList ? props.playerList.filter((player)=>!player.currentPlayer).map((player, i) => {
136	            return (<ListGroup.Item key={player.connectionId} className="d-flex justify-content-between align-items-center">
137	              <span style={{color:player.playerName}}>&#11044; <span className="small" style={{color:"Black"}}>{player.playerName}</span></span>
138	              <Badge pill variant="dark">{player.score}</Badge>
139	            </ListGroup.Item>)
140	         }) : <div>no players</div>}
141	
142	        </ListGroup>
143	      </Card.Body>
144	    </Card>
145	  );
146	}
147	
148	function GameOver(props) {
149	  if (props.currentStep !== TRIVIA_STEP.STEP_GAMEOVER) {
150	    return null
151	  }
152	  const restart = () => {
153	    document.location = document.baseURI;
154	  };
155	
156	  return (
157	    <Jumbotron>
158	    <h1>Game Completed!</h1>
159	    <p>
160	    </p>
161	    <p>
162	      <Button variant="primary" onClick={()=>restart()}>Restart</Button>
163	    </p>
164	  </Jumbotron>
165	  );
166	}
167	
168	class App extends React.Component {
169	  ws = new WebSocket(WebsocketEndpoint);
170	
171	  constructor(props) {
172	    super(props);
173	    this.state = {
174	      currentStep: document.location.hash.startsWith('#newgame') ? TRIVIA_STEP.STEP_JOINGAME : TRIVIA_STEP.STEP_GETSTARTED,
175	      connected: false,
176	      playerList: null,
177	      gameId: document.location.hash.startsWith('#newgame') ? document.location.hash.replace('#newgame/', '') :  null,
178	      question: null
179	    };
180	  }
181	
182	  newGame() {
183	    var message = JSON.stringify({"action":"newgame"});
184	    this.ws.send(message);
185	    this.setState({currentStep: TRIVIA_STEP.STEP_WAITING});
186	  }
187	
188	  joinGame() {
189	    var message = JSON.stringify({"action":"joingame", "gameid": this.state.gameId});
190	    this.ws.send(message);
191	    this.setState({currentStep: TRIVIA_STEP.STEP_QUESTIONS});
192	  }
193	
194	  startGame() {
195	    var message = JSON.stringify({"action":"startgame", "gameid": this.state.gameId});
196	    this.ws.send(message);
197	    this.setState({currentStep: TRIVIA_STEP.STEP_QUESTIONS});
198	  }
199	
200	  answer(questionId, answer) {
201	    var message = JSON.stringify({
202	      "action":"answer",
203	      "gameid": this.state.gameId,
204	      "questionid": questionId,
205	      "answer": answer
206	    });
207	    this.ws.send(message);
208	  }
209	
210	  componentDidMount() {
211	      this.ws.onopen = () => {
212	        this.setState({connected: true});
213	      }
214	
215	      this.ws.onmessage = evt => {
216	        const message = JSON.parse(evt.data)
217	
218	        switch(message.action) {
219	          case "gamecreated":
220	            this.setState({gameId: message.gameId});
221	            break;
222	          case "playerlist":
223	            this.setState({playerList: message.players.splice(0)});
224	            break;
225	          case "question":
226	            this.setState({question: message.question})
227	            break;
228	          case "gameover":
229	            this.setState({currentStep: TRIVIA_STEP.STEP_GAMEOVER});
230	            break;
231	          default:
232	            break;
233	        }
234	      }
235	
236	      this.ws.onclose = () => {
237	        this.setState({connected: false});
238	      }
239	
240	  }
241	
242	
243	  render() {
244	    return (
245	      <Container className="p-3">
246	      <Row>
247	      <Col>
248	        <GetStarted currentStep={this.state.currentStep} onNewGame={() => this.newGame()} />
249	        <JoinGame currentStep={this.state.currentStep} onJoinGame={() => this.joinGame()} gameId={this.state.gameId} />
250	        <Waiting currentStep={this.state.currentStep} onStartGame={() => this.startGame()} gameId={this.state.gameId} />
251	        <Questions currentStep={this.state.currentStep} onAnswer={(questionId, answer) => this.answer(questionId, answer)} question={this.state.question}  />
252	        <GameOver currentStep={this.state.currentStep} />
253	        {this.state.connected ? <small>&#129001; connected</small> :  <small>&#128997; disconnected</small>}
254	      </Col>
255	      <Col xs={3}>
256	        <Players playerList={this.state.playerList}/>
257	        <br/>
258	        <div className="d-flex justify-content-center">
259	        {this.state.question && <CountdownCircleTimer
260	          key={this.state.question.id}
261	          size={120}
262	          isPlaying
263	          duration={5}
264	          colors={[["#007bff"]]}
265	        >
266	          {({ remainingTime }) => remainingTime}
267	        </CountdownCircleTimer>}
268	        </div>
269	      </Col>
270	
271	      </Row>
272	      </Container>
273	    );
274	  }
275	}
276	
277	export default App;
