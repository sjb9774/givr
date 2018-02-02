from givr.app import app
from givr.room import WebSocketRoom, House
from givr.user import User
from givr.logging import get_logger
from flask import request, jsonify

logger = get_logger(__name__)

@app.route("/api/room/create", methods=["POST"])
def api_room_create():
    data = request.get_json()
    room = WebSocketRoom()
    h = House.get_instance()
    h.add_room(room)
    return jsonify({"success": True, "room_id": room.room_id})

@app.route("/api/room/open", methods=["POST"])
def api_room_open():
    h = House.get_instance()
    data = request.get_json()
    room_id = data.get("room_id")
    room = h.get_room(room_id)
    room.open()
    owner_id = data.get("owner_id")

    resp = {"success": True, "address": room.address[0], "port": room.address[1]}
    if owner_id:
        room.add_owner(User.from_user_id(owner_id))
        resp["owner_id"] = owner_id
    return jsonify(resp)

@app.route("/api/room/add_user", methods=["POST"])
def api_room_add_user():
    h = House.get_instance()
    data = request.get_json()
    user_id = data.get("user_id")
    room_id = data.get("room_id")
    room = h.get_room(room_id)
    room.add_user(User.from_user_id(user_id))
    return jsonify({"room_id": room_id, "user_count": room.user_count(), "success": True})

@app.route("/api/room/remove_user", methods=["POST"])
def api_room_remove_user():
    h = House.get_instance()
    data = request.get_json()
    user_id = data.get("user_id")
    room_id = data.get("room_id")
    room = h.get_room(room_id)
    user = User.from_user_id(user_id)
    if room.has_user(u):
        room.remove_user(user)
        resp = {"success": True, "user_count": room.user_count(), "room_id": room.room_id}
    else:
        resp = {"success": True, "user_count": room.user_count(), "message": "User not in room"}
    return jsonify(resp)

@app.route("/api/room/info", methods=["GET"])
def api_room_info():
    args = request.args
    room = House.get_instance().get_room(args.get("room_id"))
    return jsonify({"room_id": room.room_id,
                    "is_open": room.is_open(),
                    "user_count": room.user_count(),
                    "owner": room.owner.user_id if room.owner else None,
                    "address": room.address[0],
                    "port": room.address[1]})
