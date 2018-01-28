from givr.app import app
from givr.room import WebSocketRoom, House
from givr.user import User
from flask import request, jsonify

@app.route("/api/room/create", methods=["POST"])
def api_room_create():
    data = request.get_json()
    room = WebSocketRoom()
    h = House.get_instance()
    h.add_room(room)
    return jsonify({"room_id": room.room_id})

@app.route("/api/room/open", methods=["POST"])
def api_room_open():
    h = House.get_instance()
    data = request.get_json()
    user_id = data.get("user_id")
    room_id = data.get("room_id")
    room_instance = h.get_room(room_id)
    room_instance.open()
    room_instance.add_owner(User.from_user_id(user_id))
    return jsonify({"success": True})

@app.route("/api/room/status", methods=["GET"])
def api_room_get():
    args = request.args
    room = House.get_instance().get_room(args.get("room_id"))
    return jsonify({"room_id": room.room_id,
                    "is_open": room.is_open(),
                    "user_count": len(room.users),
                    "owner": room.owner.user_id})

    return str(args)
