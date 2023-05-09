import json
import time
from threading import Thread

from lib.database import EncryptedDatabase
from lib.settings_container import SettingsContainer

from .async_server import AsyncServer

# The BrowserWorker class is responsible for communication with the browser extension.
# It supports two different messages from the addon:
#
# Check: Is the domain present in database?
# Format: {"type": "check", "domain": "<domain>"}
# Returns: {"type": "check", "is_present": <bool>}
#
# Authenticate: Request authentication data to fill in
# Format: {"type": "auth", "domain": "<domain>"}
# Returns: {"type": "auth", "username": "<username>", "password": "<password>"}
# if authentication is successful, else:
# Returns: {"type": "auth_fail"}
#
# Empty Type: Send when nothing happens
# Format: {"type":"empty"}


class BrowserWorker(Thread):
    def __init__(
            self,
            database: EncryptedDatabase,
            settings: SettingsContainer,):
        super().__init__()
        self.database = database
        self.settings = settings
        self.verification_system = self.settings.verification_system
        self.running = False
        self.setDaemon(True)
        self.async_server = AsyncServer()

    def start(self):
        """Starts the browser worker. Starts the async server and then starts the thread.
        """
        self.running = True
        self.async_server.start()
        return super().start()

    def run(self):
        """ Main loop of the browser worker. Checks if there is a message from the browser extension. If so, processes it. If not, waits for 0.01 seconds and checks again.
        """
        while self.running:
            if not self.async_server.outside.poll(0.001):
                time.sleep(0.01)
                continue

            msg = self.async_server.outside.recv()
            msg = json.loads(msg)
            self.process_msg(msg)

    def process_msg(self, msg: dict) -> None:
        """Processes received message from browser extension. If browser support is turned off, sends an empty message. If message is not a dictionary, sends an empty message. If message does not contain a type, sends an empty message. If message type is check, calls process_check. If message type is auth, calls process_auth. If message type is not check or auth, sends an empty message.

        :param msg: Received message from browser extension.
        :type msg: dict
        """
        # Check if browser support is turned on
        if not self.settings["browser_support"] or not self.database.connected:
            time.sleep(0.01)
            self.async_server.outside.send({"type": "auth_fail"})
            return

        # Check if received message is a dictionary
        if not isinstance(msg, dict):
            self.__send_empty()
            return

        # Check if message contains a type
        if "type" not in msg:
            self.__send_empty()
            return

        if msg["type"] == "check":
            self.process_check(msg)
        elif msg["type"] == "auth":
            self.process_auth(msg)
        else:
            self.__send_empty()

    def stop(self):
        """Stops the browser worker.
        """
        self.async_server.terminate()
        self.running = False

    def process_check(self, msg: dict):
        """Function to process message of check type. Checks if domain is present in database. If so, sends a message to browser extension. If not, sends an empty message. If database is not connected, sends an empty message. If message does not contain a domain, sends an empty message. If domain contains www prefix, removes it. If message is not a dictionary, sends an empty message.

        :param msg: Received message from browser extension containing domain to check for.
        :type msg: dict
        """
        if "domain" not in msg:
            self.__send_empty()
            return

        if msg["domain"].startswith("www."):
            msg["domain"] = msg["domain"][4:]

        if not self.database.connected:
            self.__send_empty()
            return

        domain = msg["domain"]

        answer = dict()
        answer["type"] = "check"
        answer["is_present"] = False
        for entry in self.database.data:
            if entry.domain.endswith(domain):
                answer["is_present"] = True
                break

        self.async_server.outside.send(answer)

    def __del__(self):
        self.stop()

    def process_auth(self, msg: dict):
        """Function to process message of auth type. If domain is in database, process to perform authentication procedure if FPM is configured to do so. If authentication is successful, send login credentials to browser extension. If authentication is not successful, send an empty message. If database is not connected, send an empty message. If message does not contain a domain, send an empty message. If domain contains www prefix, remove it. If message is not a dictionary, send an empty message.

        :param msg: Received message from browser extension containing domain to authenticate for.
        :type msg: dict
        """
        # Check, that message contains domain
        if "domain" not in msg:
            self.__send_empty()
            return

        # Some domains contain www prefix. Remove it.
        if msg["domain"].startswith("www."):
            msg["domain"] = msg["domain"][4:]

        # Check, that we are actually inside a database
        if not self.database.connected:
            self.__send_empty()
            return

        auth = True
        if self.settings["plugin_auth"] and self.verification_system:
            auth = self.verification_system.authenticate(
                self.settings["id"], self.settings["continuous_auth"])

        answer = dict()
        if auth:
            domain = msg["domain"]
            answer["type"] = "auth"
            for entry in self.database.data:
                if entry.domain.endswith(domain):
                    answer["username"] = entry.username
                    answer["password"] = entry.password
                    break
        else:
            answer["type"] = "auth_fail"

        self.async_server.outside.send(answer)

    def check_fields(self, _dict, *args) -> bool:
        """Checks fields of a dictionary.

            Args:
                _dict   (dict)  -   Dictionary to check for.
                *args   (tupel) -   Tupels containing   (<field_name>, <data_type>)

            Returns:
                (bool)  -   Everything as expected?
        """
        for k in args:
            if k[0] not in _dict:
                return False
            if not isinstance(_dict[k[0]], k[1]):
                return False
        return True

    def __send_empty(self):
        self.async_server.outside.send({"type": "empty"})
