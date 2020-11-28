import asyncio
import os
import time

from tornado.escape import json_decode
from tornado.ioloop import IOLoop
from tornado.locks import Condition
from tornado.web import Application
from tornado.web import RequestHandler
from tornado.web import HTTPError
from tornado.options import parse_command_line

# Poor man's in-memory database. Stores the state of all game sessions.
rooms_db = {}

class Room:
    def __init__(self, room_id, cards=[]):
        self.cond = Condition()
        self.room_id = room_id
        # TODO: initial state?
        self.frontend_state = {"version": 1, "message": "AAAAA"}
        # starting at 1 instead of 0 so clients will pull the first update
        self.state_version_counter = 1
        self.players = {}

    def add_player(self, username):
        if username in self.players:
            raise KeyError
        self.players[username] = Player(username)
        self.update_frontend_state()
        

    def update_frontend_state(self, state=None):
        if state:
            self.frontend_state = state
        self.state_version_counter += 1
        self.frontend_state["version"] = self.state_version_counter
        self.frontend_state["players"] = [key for key in self.players.keys()]
        self.cond.notify_all()

    def get_last_update_id(self):
        return self.state_version_counter

    def get_frontend_state(self):
        return self.frontend_state


# TODO: somehow check if the player is still connected
class Player():
    def __init__(self, username):
        self.username = username


class RoomHandler(RequestHandler):
    def get(self):
        room_id = self.get_argument("room_id")
        player = self.get_argument("username")
        if room_id not in rooms_db:
            rooms_db[room_id] = Room(room_id)
        room = rooms_db[room_id]
        try:
            room.add_player(player)
        except KeyError:
            raise HTTPError(400)
        self.render("room.html", room_id=room_id, username=player)


class UpdateRoomStateHandler(RequestHandler):
    def post(self):
        self.args = json_decode(self.request.body)
        room_id = str(self.args["room_id"])
        new_state = self.args["new_state"]
        if room_id not in rooms_db:
            raise HTTPError(400)
        rooms_db[room_id].update_frontend_state(state=new_state)


class RoomStateNotificationHandler(RequestHandler):
    """Longpoll handler for pushing new room state to clients."""

    async def post(self):
        room_id = self.get_argument("room_id")
        last_seen_update = self.get_argument("last_update")
        if room_id not in rooms_db:
            raise HTTPError(400)
        room = rooms_db[room_id]
        while room.get_last_update_id() <= int(last_seen_update):
            self.wait_future = room.cond.wait()
            try:
                await self.wait_future
            except asyncio.CancelledError:
                return
        if self.request.connection.stream.closed():
            return
        self.write(room.get_frontend_state())

    def on_connection_close(self):
        self.wait_future.cancel()
