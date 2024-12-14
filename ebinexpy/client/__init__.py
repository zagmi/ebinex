import re
import json
import threading
import websocket
from typing import (
    Any,
    List,
    Dict,
    Union,
    overload,
    Callable,
    Optional,
)

from .frame import Frame
from .constants import (
    HDR_ID,
    CMD_ACK,
    VERSION,
    CMD_SEND,
    CMD_NACK,
    HEARTBEAT,
    CMD_CONNECT,
    HDR_HEARTBEAT,
    CMD_SUBSCRIBE,
    HDR_MESSAGE_ID,
    CMD_DISCONNECT,
    CMD_UNSUBSCRIBE,
    HDR_DESTINATION,
    HDR_SUBSCRIPTION,
    HDR_ACCEPT_VERSION,
)

from varname import nameof
from ebinexpy.iykyk import DEFAULT_FUNC


class StompClient:
    '''
    If you're mentally retarded enough to not Google what Stomp is and want to know what this is, it's a custom
    implementation of the [Stomp Client](https://docs.spring.io/spring-framework/reference/web/websocket/stomp.html), anyway.

    Thanks to the [base project](https://github.com/GlassyWing/stomp_ws_py) for this wonderful piece of code.

    In case you're reading this to help the project, please go ahead ;) otherwise, go away.
    '''

    def __init__(
        self,
        url: str,
        on_open: Optional[Callable[['StompClient'], None]] = None,
        on_close: Optional[Callable[['StompClient', int], None]] = None,
        on_error: Optional[Callable[['StompClient', str], None]] = None,
        on_message: Optional[Callable[['StompClient', str], None]] = None,
        **kwargs,
    ):
        '''
        :param url: The URL to connect to.
        :param on_open: Callback function called when the connection opens.
        :param on_close: Callback function called when the connection closes.
        :param on_error: Callback function called when an error occurs.
        :param on_message: Callback function called when a message is received.
        :param kwargs: Other optional arguments.
        '''
        self.url = url
        self.on_open = on_open
        self.on_close = on_close
        self.on_error = on_error
        self.on_message = on_message
        
        self.on_connected: Callable[[StompClient]] = kwargs.get('on_connected', DEFAULT_FUNC)

        self.connected = threading.Event()
        self.subscriptions: Dict[str, Callable] = {}

        def _on_open(client: websocket.WebSocketApp):
            self.on_open(self)

        def _on_close(client: websocket.WebSocketApp, code: int, message: str):
            self.connected.clear()
            self.on_close(self, code)

        def _on_error(client: websocket.WebSocketApp, error: str):
            self.on_error(self, error)

        def _on_message(client: websocket.WebSocketApp, message: str):
            self.connected.set()
            frame = Frame.unmarshall(message)

            if 'CONNECTED' in frame.command:
                self.on_connected(self)

            elif 'MESSAGE' in frame.command:
                self.on_message(self, self.jsonify(frame.body))

            elif 'RECEIPT' in frame.command:
                pass

        self.ws = websocket.WebSocketApp(
            self.url,
            header=kwargs.get('header'),
            on_message=_on_message,
            on_error=_on_error,
            on_close=_on_close,
            on_open=_on_open,
        )

        threading.Thread(
            daemon=True,
            name=nameof(StompClient),
            target=self.ws.run_forever,
            kwargs={'suppress_origin': True},
        ).start()

    def connect(self, headers: Dict = {}):
        self.connected.wait()

        headers[HDR_ACCEPT_VERSION] = VERSION
        headers[HDR_HEARTBEAT] = HEARTBEAT

        self._transmit(CMD_CONNECT, headers)

    def disconnect(self, headers: Dict = {}):
        self._transmit(CMD_DISCONNECT, headers)
        self.ws.close()

    def send(self, destination: str, **kwargs):
        body = kwargs.get('body', '')
        headers = kwargs.get('headers', {})
        headers[HDR_DESTINATION] = destination
        return self._transmit(CMD_SEND, headers, body)

    def subscribe(self, destination, callback: Callable = DEFAULT_FUNC, **kwargs) -> str:
        headers: Dict[str, Any] = kwargs.get('headers', {})
        sub_id = headers.get(HDR_ID, None)

        if sub_id is None:
            sub_id = f'sub-{len(self.subscriptions)+1}'

        headers[HDR_ID] = sub_id
        headers[HDR_DESTINATION] = destination
        self.subscriptions[sub_id] = callback
        self._transmit(CMD_SUBSCRIBE, headers)

        return sub_id

    def unsubscribe(self, id: str):
        del self.subscriptions[id]
        return self._transmit(CMD_UNSUBSCRIBE, {HDR_ID: id})

    def ack(self, message_id, subscription, **kwargs):
        headers = kwargs.get('headers', {})
        headers[HDR_MESSAGE_ID] = message_id
        headers[HDR_SUBSCRIPTION] = subscription
        return self._transmit(CMD_ACK, headers)

    def nack(self, message_id, subscription, **kwargs):
        headers = kwargs.get('headers', {})
        headers[HDR_MESSAGE_ID] = message_id
        headers[HDR_SUBSCRIPTION] = subscription
        return self._transmit(CMD_NACK, headers)

    @overload
    def jsonify(self, data: str) -> Dict:
        ...

    @overload
    def jsonify(self, data: str) -> List:
        ...

    def jsonify(self, data: str) -> Union[Dict, List]:
        data = data.strip()
        data = data[:1] + data[2:-1]
        data = data.replace('\\', '')

        jp = r'\{.*\}'
        matches = re.findall(jp, data, re.DOTALL)

        chunks = []
        for match in matches:
            try:
                chunk = json.loads(match)
                chunks.append(chunk)
            except json.JSONDecodeError:
                continue

        return chunks[0] if len(chunks) == 1 else chunks

    def dumpy(self, data: Dict):
        return json.dumps(data).replace(' ', '').replace('"', r'\"').strip()

    def _transmit(self, command, headers, body=None):
        self.ws.send(f'["{Frame.marshall(command, headers, body)}"]')
