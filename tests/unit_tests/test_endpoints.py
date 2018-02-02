import unittest
from unittest.mock import Mock
import json
from givr.app import app
from givr.endpoints import *
import givr.room

class EndpointsTestCase(unittest.TestCase):

    def setUp(self):
        givr.room.WebSocketServer = Mock()
        givr.room.SocketServer = Mock()
        self.app = app.test_client()

        self.house = givr.room.House.get_instance()
        self.room = givr.room.WebSocketRoom()
        self.room.address = ("127.0.0.1", 9000) # manually set since we mocked out the WebSocketServer
        self.house.add_room(self.room)

    def tearDown(self):
        for room in self.house.rooms[:]:
            self.house.remove_room(room)

    def json_response(self, path=None, method=None, params={}):
        kwargs = {}
        if method.upper() == "GET":
            kwargs["query_string"] = params
        else:
            kwargs["data"] = json.dumps(params)
            kwargs["content_type"] = "application/json"
        kwargs["method"] = method.upper()
        response = self.app.open(path, **kwargs)
        return json.loads(response.get_data().decode())

    def test_endpoint_room_create(self):
        json_resp = self.json_response(path="/api/room/create", method="POST")
        self.assertTrue(json_resp.get("success"))
        self.assertIsNotNone(json_resp.get("room_id"))

    def test_endpoint_room_open(self):
        json_resp = self.json_response(path="/api/room/open", method="POST", params={"room_id": self.room.room_id, "owner_id": "TEST USER"})
        self.assertTrue(json_resp["success"])
        self.assertTrue(self.room.is_open())
        self.assertEqual(json_resp["owner_id"], "TEST USER")
        self.assertEqual(self.room.owner.user_id, "TEST USER")

    def test_endpoint_room_info(self):
        json_resp = self.json_response(path="/api/room/info", method="GET", params={"room_id": self.room.room_id})
        self.assertIsNone(json_resp["owner"])
        self.assertEqual(json_resp["user_count"], 0)
        self.assertEqual(json_resp["room_id"], self.room.room_id)
        self.assertFalse(json_resp["is_open"])
        self.assertEqual(json_resp["address"], "127.0.0.1")
        self.assertEqual(json_resp["port"], 9000)
