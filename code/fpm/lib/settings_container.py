import json
import threading
from os import path


class SettingsContainer():
    def __init__(
            self,
            filename: str,
            verification_system=None):
        """Container for settings. Settings are stored in a json file. If file is not present on initialization, a new file is created with default settings.

        :param filename: Path to settings file.
        :type filename: str
        :param verification_system: Verification system to use for authentication.
        :type verification_system: _type_, optional
        """

        self.format_description = {
            "dark_theme": (bool, False),
            "plugin_auth": (bool, True),
            "continuous_auth": (bool, True),
            "browser_support": (bool, True),
            "language_file": (str, "code/fpm/lang/english.po"),
            "id": (str, "my_id"),
            "logging": (bool, True),
            "file_logging": (bool, False)
        }
        self.container = dict()
        self.lock = threading.Lock()
        self.filename = filename
        self.verification_system = verification_system
        self.__read_in()

    def __read_in(self):
        """Try to read in settings file. If file not present
        create it with default settings.
        """
        if path.exists(self.filename):
            try:
                self.container = json.load(open(self.filename, "r"))
                self.__check_dict()
                self.__save()
            except ValueError:
                self.__initilize()
        else:
            self.__initilize()

    def __check_dict(self):
        """Check loaded settings dictionary against format definition.
        """
        for key in self.format_description:
            if key in self.container and isinstance(
                    self.container[key], self.format_description[key][0]):
                continue
            self.container[key] = self.format_description[key][1]

    def __initilize(self):
        """Initialize new settings container using default settings.
        """
        self.container = {}
        for key in self.format_description:
            self.container[key] = self.format_description[key][1]
        self.__save()

    def __save(self):
        """Save settings configuration into new file
        """
        with open(self.filename, "w") as settings_file:
            json.dump(self.container, settings_file)

    def __setitem__(self, key: str, value: bool):
        """Thread safe assignment of new value.

        :param key: Key to set value of.
        :type key: str
        :param value: New value.
        :type value: bool
        """
        self.lock.acquire()
        self.container[key] = value
        self.__save()
        self.lock.release()

    def __getitem__(self, key: str):
        """Returns value for given key

        :param key: Key to look for.
        :type key: str
        :return: Value behind key. If key is not found in container,
        returns None.
        :rtype: obj
        """
        self.lock.acquire()
        if key in self.container:
            item = self.container[key]
            self.lock.release()
            return item
        self.lock.release()
        return None
