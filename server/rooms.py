import asyncio
import os
import time

from tornado.escape import json_decode
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.locks import Condition
from tornado.web import Application
from tornado.web import RequestHandler
from tornado.web import HTTPError
from tornado.options import parse_command_line

from server.constants import FE_STATE_PLAYERS
from server.constants import FE_STATE_VERSION
from server.constants import FE_STATE_DRAWN_CARDS
from server.constants import FE_STATE_CARD_SUIT
from server.constants import FE_STATE_CARD_VALUE
from server.constants import FE_STATE_CARD_OWNER
from server.constants import ROOM_PLAYER_CONN_UPDATE_MS
from server.deck import Deck

# Poor man's in-memory database. Stores the state of all game sessions.
rooms_db = {}


class PlayerExistsInRoomException(Exception):
    pass


class Room:
    def __init__(self, room_id, cards=[]):
        self.cond = Condition()
        self.room_id = room_id
        self.frontend_state = {FE_STATE_VERSION: 1, FE_STATE_DRAWN_CARDS: []}
        # starting at 1 instead of 0 so clients will pull the first update
        self.state_version_counter = 1
        self.players = {}
        self.deck = Deck()
        self.periodic_callback = PeriodicCallback(
            lambda: self.maybe_update_player_statuses(), ROOM_PLAYER_CONN_UPDATE_MS
        )
        self.periodic_callback.start()

    def add_player(self, username):
        if username in self.players and self.players[username].is_online():
            raise PlayerExistsInRoomException()
        self.players[username] = Player(username)
        self.update_frontend_state()

    def draw_card(self, player):
        card = self.deck.draw_card()
        self.frontend_state[FE_STATE_DRAWN_CARDS].append(
            {
                FE_STATE_CARD_SUIT: card.suit,
                FE_STATE_CARD_VALUE: card.value,
                FE_STATE_CARD_OWNER: player,
            }
        )
        self.update_frontend_state()

    def get_player_statuses(self):
        return {u: p.is_online() for u, p in self.players.items()}

    def maybe_update_player_statuses(self):
        statuses = self.get_player_statuses()
        for username, status in self.frontend_state[FE_STATE_PLAYERS].items():
            if username not in statuses or statuses[username] != status:
                self.update_frontend_state()
                return

    def update_frontend_state(self, state=None):
        if state:
            self.frontend_state = state
        self.state_version_counter += 1
        self.frontend_state[FE_STATE_VERSION] = self.state_version_counter
        self.frontend_state[FE_STATE_PLAYERS] = self.get_player_statuses()
        self.cond.notify_all()

    def get_last_update_id(self):
        return self.state_version_counter

    def get_frontend_state(self):
        return self.frontend_state


class Player:
    def __init__(self, username):
        self.username = username
        self.last_seen = time.time()

    def is_online(self):
        return time.time() - self.last_seen < 1


class RoomHandler(RequestHandler):
    def get(self):
        room_id = self.get_argument("room_id")
        player = self.get_argument("username")
        if room_id not in rooms_db:
            rooms_db[room_id] = Room(room_id)
        room = rooms_db[room_id]
        try:
            room.add_player(player)
        except PlayerExistsInRoomException:
            raise HTTPError(403)
        self.render("room.html", room_id=room_id, username=player)


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


class PlayerKeepAliveHandler(RequestHandler):
    def post(self):
        room_id = self.get_argument("room_id")
        player = self.get_argument("username")
        if room_id not in rooms_db:
            raise HTTPError(400)
        if player not in rooms_db[room_id].players:
            raise HTTPError(400)
        rooms_db[room_id].players[player].last_seen = time.time()


class DrawCardHandler(RequestHandler):
    def post(self):
        room_id = self.get_argument("room_id")
        player = self.get_argument("username")
        if room_id not in rooms_db:
            raise HTTPError(400)
        if player not in rooms_db[room_id].players:
            raise HTTPError(400)
        rooms_db[room_id].draw_card(player)
