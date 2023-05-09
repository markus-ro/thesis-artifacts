import urllib.request
from multiprocessing import Pipe, Process
from time import time

import cherrypy
import cherrypy_cors


class WebHandler(object):
    def __init__(self, pipe, timeout=5) -> None:
        self.pipe = pipe
        self.timeout = timeout

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self, msg=None):
        if not msg:
            return ""
        self.pipe.send(msg)

        start = time()
        while start + self.timeout > time():
            if self.pipe.poll(0.001):
                break

        if not self.pipe.poll(0.001):
            return "{}"

        return {"resp": self.pipe.recv()}

    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        return


class AsyncServer(Process):
    def __init__(self, port=8080, timeout=30) -> None:
        super().__init__()
        self.outside, self.inside = Pipe(True)
        self.timeout = timeout
        self.web_handler = WebHandler(self.inside, timeout)
        self.port = port

    def run(self) -> None:
        cherrypy_cors.install()
        cherrypy.config.update({"cors.expose.on": True,
                                "log.screen": False,
                                "server.socket_port": self.port})
        cherrypy.quickstart(self.web_handler)
        return super().run()

    def terminate(self) -> None:
        try:
            urllib.request.urlopen(f"http://localhost:{self.port}/shutdown").read()
        except Exception as e:
            print("[INFO\t] [BG\t\t] Webserver already stopped")
        return super().terminate()
