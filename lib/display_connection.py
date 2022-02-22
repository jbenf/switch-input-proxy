"""This module handles the inter-process communication between the input_proxy and the ui_service"""

from multiprocessing.connection import Client, Listener
from time import sleep
from typing import Callable, NamedTuple, cast


class DisplayConnectionMessage(NamedTuple):
    cmd: str
    payload: str
    
class DisplayConnection:
    PORT = 6067
    ADDRESS = ('localhost', PORT)
    _AUTHKEY = b'mtSgZKBmppNM5PCuTBaXU5xc'

class DisplayConnectionServer(DisplayConnection):
    def __init__(self, handler: Callable[[DisplayConnectionMessage], None]):
        self.handler = handler

    def listen(self):
        print('Accepting Connections on ', self.ADDRESS[0], ':', self.PORT)
        listener = Listener(self.ADDRESS, authkey=self._AUTHKEY)
        while True:
            try:
                conn = listener.accept()
                print('connection accepted from', listener.last_accepted)
                while not conn.closed:
                    msg = cast(DisplayConnectionMessage, conn.recv())

                    print("Message Received: ", msg.cmd, ", ", msg.payload)
                    
                    self.handler(msg)
            except EOFError:
                print("Connection closed")
            except OSError:
                print("listening failed")
                sleep(0.05)
    
class DisplayConnectionClient(DisplayConnection):
    def send(self, cmd: str, payload: str):
        conn = Client(self.ADDRESS, authkey=self._AUTHKEY)
        conn.send(DisplayConnectionMessage(cmd, payload))
        conn.close()