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

from server.constants import PORT
from server.rooms import PlayerKeepAliveHandler
from server.rooms import RoomHandler
from server.rooms import RoomStateNotificationHandler
from server.rooms import DrawCardHandler


class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")


def main():
    parse_command_line()
    app = Application(
        [
            ("/", MainHandler),
            ("/room", RoomHandler),
            ("/await_state", RoomStateNotificationHandler),
            ("/keep_alive", PlayerKeepAliveHandler),
            ("/draw_card", DrawCardHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
    )
    app.listen(PORT)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
