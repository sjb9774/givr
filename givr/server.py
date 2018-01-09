import logging
import socket, select, threading


class ConnectionPool:

    def __init__(self):
        self.cursor = 0
        self.connections = []

    def __next__(self):
        return self.next()

    def add(self, connection):
        self.connections.append(connection)

    def remove(self, connection):
        self.connections.remove(connection)

    def next(self):
        return self.connections[self.inc_cursor()]

    def get_cursor(self):
        return self.cursor

    def inc_cursor(self):
        self.cursor += 1
        self.cursor %= len(self.connections)
        return self.get_cursor()

    def dec_cursor(self):
        self.cursor -= 1
        self.cursor %= len(self.connections)
        return self.get_cursor()


class SocketConnection:

    def __init__(self, sck, address, port, logger=None):
        self.socket = sck
        self.address = address
        self.port = port
        self.handshook = False
        self.to_be_closed = False
        self.logger = logger if logger else logging.getLogger()

    def close(self):
        self.logger.debug("Closing connection at {addr}:{port}".format(addr=self.address, port=self.port))
        self.socket.close()

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
                sck, addr = self.socket.accept()
                self.logger.debug("{addr}".format(addr=addr))
                connection = SocketConnection(sck, addr[0], addr[1], logger=self.logger)
                connections.append(connection)
                self.logger.debug("New connection created at {addr}:{port}".format(addr=connections[-1].address, port=connections[-1].port))
                self.logger.debug("Total connections: {n}".format(n=len(connections)))
            new_connection_list = connections[:]
            for connection in connections:
                try:
                    avail_data, _, _ = select.select([connection.socket], [], [], .1)
                    if avail_data:
                        response = self.connection_handler(connection)
                        if response:
                            self.logger.debug("Sending message {r}".format(r=response.encode() if hasattr(response, "encode") else response))
                            connection.socket.sendall(response.encode() if hasattr(response, "encode") else response)
                        if connection.to_be_closed:
                            new_connection_list.remove(connection)
                            connection.close()
                except socket.error as err:
                    self.logger.warning("Socket error '{err}'".format(err=err))
                    new_connection_list.remove(connection)
                    connection.close()
                except KeyboardInterrupt as err:
                    self.logger.warn("Manually interrupting server")
                    self.stop_listening()
                    break
            connections = new_connection_list

        self.logger.debug("Closing {n} connections".format(n=len(connections)))
        [c.close() for c in connections]
        self.logger.debug("Closing server socket")
        self.socket.close()
        self.logger.debug("Server done listening")

    def connection_handler(self, connection):
        data = connection.socket.recv(4096)
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
        self.fragmented_messages = {}

    def connection_handler(self, conn):
        data = conn.socket.recv(4096)
        self.logger.debug("Websocket server handling data: {data}".format(data=data))
        if not conn.handshook:
            conn.handshook = True
            return self.handle_websocket_handshake(data)
        else:
            frame = WebSocketFrame.from_bytes(data)
            if not bool(frame.fin):
                self.fragmented_messages.setdefault(conn, [])
                self.fragmented_messages[conn].append(frame)
                return None
            else: # is final frame
                message_fragments = self.fragmented_messages.get(conn)
                if message_fragments:
                    complete_message = "".join(f.message for f in message_fragments)
                    complete_message += frame.message
                    self.fragmented_messages[conn] = []
                # check for special frames (PING, close, etc)
                elif frame.opcode == WebSocketFrame.OPCODE_PING:
                    self.logger.debug("Recieved PING, sending PONG")
                    return WebSocketFrame(message=frame.message, opcode=WebSocketFrame.OPCODE_PONG).to_bytes()
                elif frame.opcode == WebSocketFrame.OPCODE_PONG:
                    self.logger.debug("Recieved PONG, ignoring")
                    return None # ignore pongs
                elif frame.opcode == WebSocketFrame.OPCODE_CLOSE:
                    self.logger.debug("Recieved close frame with message: {m}".format(m=frame.message))
                    conn.to_be_closed = True
                    return WebSocketFrame(message=frame.message, opcode=WebSocketFrame.OPCODE_CLOSE).to_bytes()
                else: #normal message
                    complete_message = frame.message
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
