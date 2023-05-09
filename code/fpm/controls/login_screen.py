import os
import sys
from typing import List

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.uix.snackbar import Snackbar
from lib.database import EncryptedDatabase
from lib.language_manager import LanguageManager
from lib.settings_container import SettingsContainer
from neuropack import TemplateDatabase
from plyer import filechooser

sys.path.append("./code/Library")


class LoginScreen(Screen):
    __slots__ = "database", "settings", "verification_system", "language"

    def __init__(
            self,
            database: EncryptedDatabase,
            settings: SettingsContainer,
            language: LanguageManager,
            **kw):
        super().__init__(**kw)
        self.database = database
        self.settings = settings
        self.verification_system = self.settings.verification_system
        self.language = language
        Window.bind(on_key_down=self._on_keyboard_down)
        self.installation_dialog = None

    def overview_button(self):
        """Checks credentials and switches to the overview screen. If the credentials are wrong, a snack bar is shown. If the credentials are correct, the database is unlocked and the overview screen is shown.
        """
        # Check that database file exists
        path = self.ids.path_to_database.text.strip()
        if not path or path.isspace():
            self.__snack(self.language["no_database_path_snack"])
            return

        if not path.endswith(".fpw"):
            self.__snack(self.language["no_fpw_file_snack"])
            return

        key = self.ids.secret_key.text.strip()
        if not key or key.isspace():
            self.__snack(self.language["enter_key_snack"])
            return

        if not self.database.open(path, key):
            self.__snack(self.language["wrong_data_snack"])
            return

        # Check if there are stored templates inside the database
        field_val = self.database.get_field("TEMPLATES")
        if field_val:
            self.verification_system.database = TemplateDatabase.construct_from_json(
                field_val)

        # If we load a new database, we need to reset the verification system. Else continous authentication allows for
        # login into the database.
        if not self.ids.path_to_database.readonly:
            self.settings.verification_system.reset()

        basename = os.path.basename(self.ids.path_to_database.text.strip())
        App.get_running_app(
        ).title = f"{basename} - Foundation Password Manager"
        self.ids.secret_key.text = ""
        self.manager.transition.direction = "up"
        self.manager.current = "application_view"

    def on_discover_btn(self):
        """Opens a file chooser dialog to select a database file. If the user selects a file, the path to the file is set as the text of the path text input. If the user cancels the dialog, nothing happens.
        """
        filechooser.open_file(
            on_selection=self.handle_selection,
            multiple=False,
            title=self.language["open_btn"],
            filters=["*fpw"])

    def handle_selection(self, selection: List):
        """Handles the selection of a file in the file chooser dialog. If the user selects a file, the path to the file is set as the text of the path text input. If the user cancels the dialog, nothing happens.

        :param selection: The selected file path or an None if the user cancels the dialog.
        :type selection: List
        """
        if selection:
            self.ids.path_to_database.text = selection[0]

    def on_enter(self):
        """Event called when Login Screen is entered. Updates the UI elements to reflect the current state of the database and the device.
        """
        self.ids.database_lock_indicator.opacity = 1 if self.database.connected else 0
        self.ids.path_to_database.readonly = self.database.connected
        self.ids.discover_btn.disabled = self.database.connected

        dev = self.settings.verification_system.device
        self.ids.device_connection_indicator.opacity = 1 if dev.is_connected() else 0

    def set_file_path(self, file_path: str):
        """Sets the path to the database file. If the database is connected, a snack bar is shown. If the file is not a .fpw file, a snack bar is shown. If the file is a .fpw file, the path is set as the text of the path text input.

        :param file_path: The path to the database file.
        :type file_path: str
        """
        if self.database.connected:
            self.__snack(self.language["file_connected_state_snack"])
            return
        if not file_path.endswith(".fpw"):
            self.__snack(self.language["no_fpw_file_snack"])
            return
        self.ids.path_to_database.text = file_path

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        """Event called when a key is pressed. If the key is the enter key and the secret key text input is focused, the overview button is pressed. Suggested function by Emiram Kablo.
        """
        if keycode != 40 and keycode != 88:
            return
        if self.ids.secret_key.focus:
            self.ids.secret_key.focus = False
            self.overview_button()

    def __snack(self, text: str):
        Snackbar(
            text=text,
            size_hint_x=.4,
            snackbar_x="10dp",
            snackbar_y="10dp",
        ).open()
