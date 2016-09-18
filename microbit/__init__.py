import json
import math
import threading
import time

import asyncio
from autobahn.asyncio.websocket import (
    WebSocketServerProtocol, WebSocketServerFactory
)

from .button import Button
from .display import Display


_start_time = time.time()
_websockets = set()


def _send_message(message_name, data):
    for websocket in _websockets:
        websocket.send(message_name, data)


button_a = Button()
button_b = Button()
display = Display()
display._send_message = _send_message


def reset():
    button_a._reset()
    button_b._reset()
    display._reset()
    _start_time = time.time()


def sleep(n):
    time.sleep(n / 1000)


def running_time():
    return math.floor((time.time() - _start_time) * 1000)


def _on_button_change(data):
    id = data.get('id')
    is_pressed = data.get('is_pressed', False)

    button = None
    if id == 'A':
        button = button_a
    elif id == 'B':
        button = button_b

    if not button:
        print('Invalid BUTTON_CHANGE id: {}'.format(id))
        return

    if is_pressed:
        button._register_down()
    else:
        button._register_up()


def _setupWebsockets(loop):
    asyncio.set_event_loop(loop)

    class MyServerProtocol(WebSocketServerProtocol):
        def onConnect(self, request):
            print('Client connecting: {}'.format(request.peer))

        def onOpen(self):
            print('WebSocket connection open.')

            _websockets.add(self)

            self.send('INITIAL_DATA', {
                'button_a': button_a._get_initial_data(),
                'button_b': button_a._get_initial_data(),
                'display': display._get_initial_data(),
            })

        def onMessage(self, raw_payload, is_binary):
            if is_binary:
                print('Ignoring received binary message ({} bytes)'.format(
                    len(raw_payload)
                ))
                return

            payload_string = raw_payload.decode('utf8')
            print('Text message received: {}'.format(payload_string))

            try:
                payload = json.loads(payload_string)
            except ValueError as error:
                print('  JSON decode error: {}'.format(error))
                return

            if type(payload) != dict:
                print('  Expected a JSON object, but got: {}'.format(
                    type(payload))
                )
                return

            message_name = payload.get('message_name')

            if message_name == 'BUTTON_CHANGE':
                _on_button_change(payload.get('data', {}))
            else:
                print('  Unrecognized message_name: {}'.format(message_name))

        def onClose(self, was_clean, code, reason):
            print('WebSocket connection closed: {}'.format({
                'was_clean': was_clean,
                'code': code,
                'reason': reason,
            }))
            _websockets.remove(self)

        def send(self, message_name, data):
            payload = {'message_name': message_name}
            payload.update(data)
            self.sendMessage(json.dumps(payload).encode('utf8'), isBinary=False)

    factory = WebSocketServerFactory('ws://localhost:8000')
    factory.protocol = MyServerProtocol

    coro = loop.create_server(factory, '0.0.0.0', 8000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()


_thread = threading.Thread(target=_setupWebsockets, args=(asyncio.get_event_loop(),))
_thread.daemon = True
_thread.start()
