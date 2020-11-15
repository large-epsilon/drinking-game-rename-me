import os

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import RequestHandler
from tornado.options import parse_command_line

PORT=8080

# Poor man's in-memory database. Stores the state of one game session.
rooms_db = {}
class Room():
    def __init__(self, room_id, cards=[]):
        self.room_id = room_id
        self.cards = cards

    def set_cards(self, cards):
        self.cards = cards


def create_room(room_id):
    rooms_db[room_id] = Room(room_id)


# Loads the index page (to create a room).
class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")


class RoomHandler(RequestHandler):
    def get(self):
        room_id = self.get_argument("room_id")
        if room_id not in rooms_db:
            create_room(room_id)
        self.render("room.html", room_id=room_id)
            

def main():
    parse_command_line()
    app = Application(
        [
            ("/", MainHandler),
            ("/room.*", RoomHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
    )
    app.listen(PORT)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
