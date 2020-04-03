import logging
from threading import Thread

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import BadRequest, MethodNotAllowed, HTTPException

log = logging.getLogger("rest")


class BotRestApi(object):
    def __init__(self, messageFun):
        """Initialize the REST API
        :param messageFun: callable, a function that will be invoked when a message was sent via the web-ui"""
        self.messageFun = messageFun
        self.form = open("res/static/index.html", "rb").read()
        self.url_map = Map([
            Rule("/", endpoint="root"),
            Rule("/help_request", endpoint="help_request"),
        ])

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
        """Called when /help_request is invoked, this happens when a fixer used the front-end to add a new
        request to the system, and the system is looking for a volunteer to assist the person in need"""
        if request.method == "GET":
            return MethodNotAllowed()

        # we only allow POST requests, we'll check if both
        # parameters we need are present, and if so, invoke the
        # actual messaging function
        if request.method == "POST":
            log.debug("Got request: `%s`", request.form)
            if False:
                # TODO verify if the payload has all the required data
                # TODO define parameters in the data
                # do some processing, if there are any issues, return an error
                return BadRequest("Request malformed")

            # if we got this far, it means we're ok, so we invoke the function that does the job
            # and pass it the input parameters
            self.messageFun(request.form)
            return Response("Request handled")


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
