import ReconnectingWebSocket from 'reconnecting-websocket';


const WEBSOCKET_URL = 'wss://localhost:8000/ws';

const socket = new ReconnectingWebSocket(WEBSOCKET_URL);

export default socket;