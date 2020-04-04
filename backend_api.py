import logging
import json

import requests

log = logging.getLogger("back")


class Backender(object):
    def __init__(self, url, username, password):
        """Initialize the backend REST API client"""
        self.base_url = url
        self.username = username
        self.password = password

    def _get(self, url=''):
        """Function for internal use, that sends GET requests to the server
        :param url: str, this will be added to the base_url to which the request is sent"""
        res = requests.get(self.base_url+url, auth=(self.username, self.password))
        import pdb; pdb.set_trace()
        print(res)

    # TODO
    def _post(self, url='', payload):
        """Function for internal use, it sends POST requests to the server
        :param url: str, this will be added to the base_url to which the request is sent
        :param payload: what needs to be sent within the POST request"""
        requests.get(self.base_url+url, auth=(self.username, self.password))

    # TODO
    def link_chatid_to_volunteer(self, volunteer_id, chat_id):
        """Tell the backend that a specific volunteer is associated with the given Telegram chat_id"""
        pass

    # TODO
    def upload_shopping_receipt(self, data, request_id):
        """Upload a receipt to the server, to document expenses handled by the volunteer on behalf of the
        beneficiary. Note that it is possible that a volunteer will send several photos that are linked to the same
        request in the system.
        :param data: bytearray, raw data corresponding to the image
        :param request_id: str, identifier of request"""
        pass

    # TODO
    def upload_shopping_receipt(self, data, request_id):
        """Upload a receipt to the server, to document expenses handled by the volunteer on behalf of the
        beneficiary. Note that it is possible that a volunteer will send several photos that are linked to the same
        request in the system.
        :param data: bytearray, raw data corresponding to the image
        :param request_id: str, identifier of request"""
        pass

    # TODO
    def relay_offer(self, request_id, volunteer_id, offer):
        """Notify the server that an offer to handle a request was provided by a volunteer. Note that this function
        will be invoked multiple times for the same request, as soon as each volunteer will send their response.
        :param request_id: str, identifier of request
        :param volunteer_id: str, volunteer identifier
        :param offer: TODO the offer indicates when the volunteer will be able to reach the beneficiary"""
        pass

    # TODO
    def update_request_status(self, request_id, status):
        """Change the status of a request, e.g., when a volunteer is on their way, or when the request was fulfilled.
        :param request_id: str, identifier of request
        :param status: TODO indicate what state it is in {new, assigned, in progress, done, something else...}"""
        pass


if __name__ == "__main__":
    # Here you can play around with the backend without involving any of the Telegram-related logic

    url = 'http://127.0.0.1:5000/api/'
    username = 'testuser'
    password = "changethis"

    b = Backender(url, username, password)
    b._get('beneficiary')
