import json
import random
import os
import uuid

import tornado.escape
import tornado.ioloop
import tornado.web

from tornado import gen
from tornado.locks import Lock
from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, type=bool, help="run in debug mode")
define("prettify", default=False, type=bool, help="prettify json file")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")
NAME_LIST = ['Кафе', 'Отель', 'WC', 'Парковка', 'Памятник']


def file_not_found_404_decorator(func):
    def func_wrapper(self, *args, **kwargs):
        if not os.path.isfile(DATA_PATH):
            self.send_error(404)
            return
        func(self, *args, **kwargs)

    return func_wrapper


class AppWithStorage(tornado.web.Application):
    def __init__(self, **settings):
        super().__init__(**settings)
        self.lock = Lock()
        self.storage_state = self.__load_state_from_storage()

    def __load_state_from_storage(self):
        if not os.path.isfile(DATA_PATH):
            return {}
        else:
            with open(DATA_PATH, 'r+') as f:
                return json.load(f)

    def __save_state_to_storage(self):
        with open(DATA_PATH, 'w+') as f:
            if options.prettify:
                indent = 4
            else:
                indent = None
            json.dump(self.storage_state, f, indent=indent)

    def get_all(self):
        return self.storage_state

    def get(self, id_):
        return self.storage_state[id_]

    def insert(self, data):
        with (yield self.lock.acquire()):
            self.storage_state.update(data)
            self.__save_state_to_storage()

    def delete(self, id_):
        with (yield self.lock.acquire()):
            del self.storage_state[id_]
            self.__save_state_to_storage()

    def patch(self, id_, new_content):
        with (yield self.lock.acquire()):
            self.storage_state[id_].update(new_content)
            self.__save_state_to_storage()
        return self.storage_state[id_]


class PointsHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        data = {str(uuid.uuid4()): {
            "name": data.get('name', random.choice(NAME_LIST)),
            "x": data["x"],
            "y": data["y"],
        }}
        yield from self.application.insert(data)
        self.set_status(201)
        self.write(data)

    @gen.coroutine
    def get(self):
        self.write(self.application.get_all())


class SinglePointHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self, p_id):
        try:
            data = self.application.get(p_id)
            self.write(data)
        except KeyError:
            self.send_error(404)
            return

    @gen.coroutine
    def delete(self, p_id):
        try:
            yield from self.application.delete(p_id)
        except KeyError:
            self.send_error(404)
        self.set_status(204)

    @gen.coroutine
    def patch(self, p_id):
        data = tornado.escape.json_decode(self.request.body)
        try:
            data = yield from self.application.patch(p_id, data)
            return data
        except KeyError:
            self.send_error(404)


def main():
    parse_command_line()
    app = AppWithStorage(
        handlers=[
            (r"/", tornado.web.RedirectHandler, {'url': 'static/index.html'}),
            (r"/api/point/([^/]+)", SinglePointHandler),
            (r"/api/point", PointsHandler),
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
    )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
