import logging
import socket, select, threading


class SocketServer:

    def __init__(self, address=('127.0.0.1', 9000), logger=None):
        self.address = address
        self.listening = False
        self.set_logger(logger if logger else logging.getLogger())

    def _create_socket(self):
        self.logger.debug("Creating socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)

    def dlisten(self):
        t = threading.Thread(target=self.listen)
        t.start()
        return t

    def set_logger(self, logger):
        self.logger = logger

    def listen(self):
        self._create_socket()
        self.logger.debug("Listening on socket")
        self.socket.listen(100)
        connections = []

        self.listening = True
        while self.listening:
            conn, _, _ = select.select([self.socket], [], [], .1)
            for c in conn:
                connections.append(self.socket.accept())
                self.logger.debug("New connection created at {addr}".format(addr=connections[-1]))

            for connection in connections:
                try:
                    response = self.connection_handler(connection[0])
                    if response:
                        self.logger.debug("Sending message {r}".format(r=response.encode() if hasattr(response, "encode") else response))
                        connection[0].sendall(response.encode() if hasattr(response, "encode") else response)
                except socket.error as err:
                    self.logger.warning("Socket error '{err}'".format(err=err))
                    connections.remove(connection)
        self.logger.debug("Server done listening")
        self.socket.close()
        [c.close() for c in connections]

    def connection_handler(self, connection):
        data = connection.recv(4096)
        if data:
            response = self.handle_message(connection, data)
            return response
        else:
            return None

    def handle_message(self, connection, data):
        return "Hello world"

    def stop_listening(self):
        self.logger.debug("Stopping listening")
        self.listening = False

from givr.websocket import WebSocketFrame
import base64, hashlib

class WebSocketServer(SocketServer):

    WEBSOCKET_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, address=('127.0.0.1', 9000), logger=None):
        super(WebSocketServer, self).__init__(address=address, logger=logger)
        self.handshook = False

    def connection_handler(self, conn):
        data = conn.recv(4096)
        if not self.handshook:
            self.handshook = True
            return self.handle_websocket_handshake(data)
        else:
            all_frames = []
            all_frames.append(WebSocketFrame.from_bytes(data))
            while all_frames[-1].fin == 0:
                all_frames.append(WebSocketFrame.from_bytes(conn.recv(4096)))
            complete_message = "".join(f.message for f in all_frames)
            response = self.handle_message(conn, complete_message)
            return WebSocketFrame(message=response).to_bytes()

    def _get_websocket_accept(self, key):
        return base64.b64encode(hashlib.sha1((key + self.WEBSOCKET_MAGIC).encode()).digest()).decode()

    def handle_websocket_handshake(self, data):
        self.logger.debug("Starting handshake")
        split_data = data.decode().split("\r\n")
        method, path, http = split_data[0].split(" ")
        headers = {}
        for header in split_data[1:]:
            if ": " in header:
                key, value = header.split(": ")
                headers[key] = value
        accept = self._get_websocket_accept(headers.get("Sec-WebSocket-Key"))
        response = "".join(["HTTP/1.1 101 Switching Protocols\r\n",
                            "Upgrade: websocket\r\n",
                            "Connection: Upgrade\r\n",
                            "Sec-WebSocket-Accept: {accept}\r\n\r\n".format(accept=accept)])
        return response
