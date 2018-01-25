from givr.app import app
from givr.room import WebSocketRoom
from givr.user import User
from flask import request, jsonify

@app.route("/api/room/open", methods=["POST"])
def api_room_open():
    data = request.get_json()
    owner = User.from_user_id(data.get("owner"))
    room = WebSocketRoom()
    room.open()
    room.add_owner(owner)
    return jsonify({"room_id": room.room_id, "owner_id": owner.user_id})
