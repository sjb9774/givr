import unittest
import json
from givr.app import app
from givr.endpoints import *

class EndpointsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_endpoint_room_create(self):
        response = self.app.post("/api/room/create")
        json_resp = json.loads(response.data.decode())
        self.assertTrue(json_resp.get("success"))
        self.assertIsNotNone(json_resp.get("room_id"))
