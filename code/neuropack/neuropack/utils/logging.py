from datetime import datetime
from os import getcwd, path
from pathlib import Path
from time import time
from typing import Optional

from ..container import EEGContainer


class AuthLogger():
    def __init__(
            self,
            log_dir: str = "log",
            file_name: Optional[str] = "main.log",
            data_dir: Optional[str] = "data"):
        """Logger instance for authentication system. Takes care of logging messages as
        well as containers/databases. Must explicitly be started before starting to write to file.

        log_dir/
        ├── <file_name>
        └── <data_dir>/


        :param log_dir: Base directory for logging, defaults to "log"
        :type log_dir: str
        :param file_name: File to write log to. Is created inside log_dir, defaults to "main.log"
        :type file_name: Optional[str], optional
        :param data_dir: Directory to store extra files in. Is created inside log_dir, defaults to "data"
        :type data_dir: Optional[str], optional
        """
        self.log_dir = log_dir
        self.file_name = file_name
        self.data_dir = data_dir
        self._logging = False
        self._file_logging = False

    def log_info(self, msg: str) -> None:
        """Add a new message of type [INFO] to log file.

        :param msg: Message to add to log file
        :type msg: str
        """
        self.__log("INFO", msg)

    def log_fail(self, msg: str) -> None:
        """Logs a fail.

        :param msg: Message to add to log file
        :type msg: str
        """
        self.__log("FAIL", msg)

    def log_database(self, database) -> None:
        """Saves TemplateDatabase instance alongside log file. Further adds a reference
        to saved instance to log file. Reference is of the form:
        <time_stamp> [DEBUG]: Saved TemplateDatabase to <file_name>
        Instance is saved to the data directory.

        :param database: Database instance to log
        :type database: TemplateDatabase
        """
        if not self._logging:
            return

        if not self._file_logging:
            return

        file_name = "database." + str(time()) + ".json"
        file_path = path.join(getcwd(), self.log_dir, self.data_dir, file_name)

        database.save(file_path)

        self.__log("DEBUG", f"Saved TemplateDatabase to \"{file_name}\"")

    def log_recording(self, container: EEGContainer) -> None:
        """Saves EEGContainer instance alongside log file. Further adds a reference
        to saved instance to log file. Reference is of the form:
        <time_stamp> [DEBUG]: Saved EEGContainer to <file_name>
        Instance is saved to the data directory.

        :param container: Recording container instance to be saved
        :type container: EEGContainer
        """
        if not self._logging:
            return

        if not self._file_logging:
            return

        file_name = "eeg_container." + str(time()) + ".csv"
        file_path = path.join(getcwd(), self.log_dir, self.data_dir, file_name)
        container.save_signals(file_path)

        self.__log("DEBUG", f"Saved EEGContainer to \"{file_name}\"")

    def start_logging(self):
        """Enables actual logging to file. Makes sure the directory exists as needed.
        """
        # Check, if logging is already enabled. If yes we are done
        if self._logging:
            return

        # Update to absolute path for compatibility
        self.log_dir = path.join(getcwd(), self.log_dir)

        # Make sure all paths exists, else create them
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(
            path.join(
                self.log_dir,
                self.data_dir)).mkdir(
            parents=True,
            exist_ok=True)

        # Set global switch and write first line to file
        self._logging = True
        self.log_info("Started logging")

    def stop_logging(self):
        """Logger no longer writes to any file.
        """
        if not self._logging:
            return
        self._logging = False

    def configure_file_logging(self, option: bool):
        """Configure option to log files alongside event logging.

        :param option: True to enable file logging, False to disable
        :type option: bool
        """
        self._file_logging = option

    def __log(self, tag: str, msg: str):
        """Internal write function for log file. Makes sure the format is consistent.
        The line format is:
        <time_stamp> [<tag>]: <msg>\r\n

        :param tag: Tag of line to write
        :type tag: str
        :param msg: Message to write to file
        :type msg: str
        """
        if not self._logging:
            return
        with open(path.join(self.log_dir, self.file_name), "a+") as f:
            f.write(f"{datetime.now()} [{tag}]: {msg}\r\n")
