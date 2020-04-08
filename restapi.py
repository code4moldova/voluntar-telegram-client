"""This is a mini web server that the bot uses to receive input from the backend, by means of REST calls"""

import logging
from threading import Thread
import json
import pprint

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import BadRequest, MethodNotAllowed, HTTPException

log = logging.getLogger("rest")  # pylint: disable=invalid-name


class BotRestApi:
    """The REST API that receives events and data from the backend"""

    def __init__(self, help_handler, cancel_handler, assign_handler, introspect_handler):
        """Initialize the REST API
        :param help_handler: callable, a function that will be invoked when a new request for assistance arrives
        :param cancel_handler: callable, will be invoked when a request for assistance was cancelled
        :param assign_handler: callable, will be invoked when a request for assistance was assigned to someone
        :param introspect_handler: callable, invoked when you go to the /introspect URL, it simply dumps the bot's state
                                   so you can get a clue about the current situation"""
        self.help_request_handler = help_handler
        self.cancel_request_handler = cancel_handler
        self.assign_request_handler = assign_handler
        self.introspect_handler = introspect_handler
        self.form = open("res/static/index.html", "rb").read()
        self.url_map = Map(
            [
                Rule("/", endpoint="root"),
                Rule("/help_request", endpoint="help_request"),
                Rule("/cancel_help_request", endpoint="cancel_help_request"),
                Rule("/assign_help_request", endpoint="assign_help_request"),
                Rule("/introspect", endpoint="introspect_request"),
            ]
        )

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, "on_" + endpoint)(request, **values)
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def on_root(self, request):
        """Called when the / page is opened, it provides a form where you can manually send a JSON,
        as if it came from the backend server"""
        return Response(self.form, content_type="text/html")

    def on_help_request(self, request):
        """Called when a fixer used the front-end to add a new request to the system, and the system is looking for
        a volunteer to assist the person in need"""
        if request.method == "GET":
            return MethodNotAllowed()

        if request.method == "POST":
            try:
                data = json.loads(request.get_data())
                log.debug("Got help request: `%s`", data)
            except json.decoder.JSONDecodeError as err:
                return BadRequest("Request malformed: %s" % err)

            # if we got this far, it means we're ok, so we invoke the function that does the job
            # and pass it the input parameters
            self.help_request_handler(data)
            return Response("Request handled")

    def on_cancel_help_request(self, request):
        """Called when a fixer notifies a volunteer that the request to assist has been cancelled"""
        if request.method == "GET":
            return MethodNotAllowed()

        if request.method == "POST":
            try:
                data = json.loads(request.get_data())
                log.debug("Got cancel request: `%s`", data)
            except json.decoder.JSONDecodeError as err:
                return BadRequest("Request malformed: %s" % err)

            # if we got this far, it means we're ok, so we invoke the function that does the job
            # and pass it the input parameters
            self.cancel_request_handler(data)
            return Response("Request handled")

    def on_assign_help_request(self, request):
        """Called when a fixer notifies a volunteer that the request to assist has been assigned to them"""
        if request.method == "GET":
            return MethodNotAllowed()

        if request.method == "POST":
            try:
                data = json.loads(request.get_data())
                log.debug("Got help assign request: `%s`", data)
            except json.decoder.JSONDecodeError as err:
                return BadRequest("Request malformed: %s" % err)

            # if we got this far, it means we're ok, so we invoke the function that does the job
            # and pass it the input parameters
            self.assign_request_handler(data)
            return Response("Request handled")

    def on_introspect_request(self, request):
        """Called when a developer wants to introspect the bot's state"""
        # WARNING: this is not meant to be exposed to the world, and is only intended as a development aid, accessible
        # via a localhost interface. It will leak sensitive information if exposed to the public.
        if request.method == "GET":
            result = self.introspect_handler()
            return Response(pprint.pformat(result, indent=4))


def run_background(app, interface="127.0.0.1", port=5000):
    """Run the WSGI app in a separate thread, to make integration into
    other programs (that take over the main loop) easier"""
    from werkzeug.serving import run_simple

    t = Thread(target=run_simple, args=(interface, port, app), name="rest")
    t.daemon = True  # so that it dies when the main thread dies
    t.start()
    return t


def dummy_message(chat_id, text):
    """Sample of a function that will be invoked by the REST API
    when a message is received via POST. Normally, this would call
    a function that uses Telegram to send a message to a real user"""
    log.info("You want to send %s to chat=%s", text, chat_id)


if __name__ == "__main__":
    from werkzeug.serving import run_simple

    interface = "127.0.0.1"
    port = 5000
    application = BotRestApi(dummy_message)

    run_simple(interface, port, application, use_debugger=True, use_reloader=True)
