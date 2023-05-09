from threading import Thread

from kivy.clock import mainthread
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.list import (IconLeftWidget, IRightBodyTouch,
                             OneLineAvatarIconListItem, OneLineListItem)
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import Snackbar
from lib.database import EncryptedDatabase
from lib.dialogs import (BCIAuthEnrollDialog, BrowserSupportDialog,
                         ChangeKeyDialog)
from lib.language_manager import LanguageManager
from lib.settings_container import SettingsContainer
from plyer import notification


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class RightButton(IRightBodyTouch, MDFloatingActionButton):
    pass


class ListItemSettings(OneLineAvatarIconListItem):
    icon = StringProperty("android")

    def __init__(self, callback, init_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._no_ripple_effect = True
        self.callback = callback
        self.ids.checkbox.active = init_value
        self.ids.checkbox.bind(on_release=lambda x: self.__internal_callback())

    def __internal_callback(self):
        self.callback(self.id, self.ids.checkbox.active)

    def change_state(self, val):
        self.ids.checkbox.active = val


class ListItemButton(OneLineAvatarIconListItem):
    icon = StringProperty("android")

    def __init__(self, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._no_ripple_effect = True
        self.callback = callback
        self.ids.button.bind(on_release=lambda x: self.__internal_callback())

    def __internal_callback(self):
        self.callback(self.id, False)

    def change_state(self, icon, color):
        self.ids.button.icon = icon
        self.ids.button.md_bg_color = color

    @mainthread
    def interactive(self, is_interactive):
        self.ids.button.disabled = not is_interactive


class SettingsScreen(Screen):
    __slots__ = "database", "language", "connection_in_progress"

    def __init__(
            self,
            database: EncryptedDatabase,
            settings: SettingsContainer,
            language: LanguageManager,
            **kw):
        super().__init__(**kw)
        self.database = database
        self.settings_container = settings
        self.verification_system = settings.verification_system
        self.language = language
        self.connection_in_progress = False
        self.populated = False
        self.dialog = None

    def on_enter(self):
        if self.populated:
            self.__update_connection_gui()
            return
        self.populated = True

        self.build_general_category()

        self.build_bci_auth_category()

        self.build_browser_category()

    def build_general_category(self):
        self.ids.settings_scroll.add_widget(
            OneLineListItem(
                text=self.language["general_category"],
                _no_ripple_effect=True))

        self.ids.settings_scroll.add_widget(
            ListItemSettings(
                self.toggle_callback,
                self.settings_container["dark_theme"],
                text=self.language["dark_theme"],
                icon="lightbulb",
                id="dark_theme"))

        change_key = OneLineAvatarIconListItem(IconLeftWidget(
            icon="key-variant"), text=self.language["change_database_key"])
        change_key.bind(on_press=self.show_change_key_dialog)
        self.ids.settings_scroll.add_widget(change_key)

    def build_browser_category(self):
        self.ids.settings_scroll.add_widget(
            OneLineListItem(
                text=self.language["browser_category"],
                _no_ripple_effect=True))

        self.browser_support_toggle = ListItemSettings(
            self.toggle_callback,
            self.settings_container["browser_support"],
            text=self.language["browser_support"],
            icon="firefox",
            id="browser_support")
        self.ids.settings_scroll.add_widget(self.browser_support_toggle)
        self.ids.settings_scroll.add_widget(
            ListItemSettings(
                self.toggle_callback,
                self.settings_container["plugin_auth"],
                text=self.language["plugin_auth"],
                icon="lock-open-check",
                id="plugin_auth")
        )
        self.ids.settings_scroll.add_widget(
            ListItemSettings(
                self.toggle_callback,
                self.settings_container["continuous_auth"],
                text=self.language["continuous_auth"],
                icon="security",
                id="continuous_auth")
        )

    def build_bci_auth_category(self):
        self.ids.settings_scroll.add_widget(
            OneLineListItem(
                text=self.language["bci_auth_category"],
                _no_ripple_effect=True))

        self.ids.settings_scroll.add_widget(
            ListItemSettings(
                self.toggle_callback,
                self.settings_container["logging"],
                text=self.language["logging"],
                icon="receipt-text-outline",
                id="logging")
        )

        self.ids.settings_scroll.add_widget(
            ListItemSettings(
                self.toggle_callback,
                self.settings_container["file_logging"],
                text=self.language["file_logging"],
                icon="folder",
                id="file_logging")
        )

        self.connection_settings = ListItemButton(
            self.toggle_callback,
            text=self.language["device_connection"],
            icon="broadcast",
            id="device_connection")
        self.ids.settings_scroll.add_widget(self.connection_settings)
        self.__update_connection_gui()

        configure_bci = OneLineAvatarIconListItem(IconLeftWidget(
            icon="brain"), text=self.language["configure_bci_auth"])
        configure_bci.bind(on_press=self.show_bci_auth_enroll_dialog)
        self.ids.settings_scroll.add_widget(configure_bci)

    def toggle_callback(self, _id, value):
        if _id == "dark_theme":
            self.__msg(self.language["restart_snack"])
        elif _id == "browser_support":
            self.show_browser_support_diag(value)
            return
        elif _id == "device_connection":
            Thread(target=self.handle_device_connection).start()
            return
        elif _id == "logging" or _id == "file_logging":
            self.settings_container[_id] = value
            self.verification_system.configure_logging(
                self.settings_container["logging"],
                self.settings_container["file_logging"])
        self.settings_container[_id] = value

    def handle_device_connection(self):
        if not self.verification_system.device:
            return
        if self.connection_in_progress:
            return

        self.connection_in_progress = True

        device = self.verification_system.device

        self.connection_settings.interactive(False)
        if device.is_connected():
            device.disconnect()
            notification.notify(
                title="Device Connection",
                message="Disconnected BCI device")
            self.__update_connection_gui()
        else:
            notification.notify(
                title="Device Connection",
                message="Searching for BCI Device")
            res = device.connect(timeout=10, raise_exception=False)
            if res:
                self.__update_connection_gui()
                notification.notify(
                    title="Device Connection",
                    message="Connected BCI device")
            else:
                notification.notify(
                    title="Device Connection",
                    message="Could not connect device")

        self.connection_in_progress = False
        self.connection_settings.interactive(True)

    @mainthread
    def __update_connection_gui(self):
        if not self.verification_system:
            return
        device = self.verification_system.device
        if device and device.is_connected():
            self.connection_settings.change_state(
                "access-point-check", "#32681d")
        else:
            self.connection_settings.change_state(
                "access-point-off", "#b71c1c")

    def cancel_callback(self):
        self.dialog.close()
        self.dialog = None

    def show_browser_support_diag(self, new_value):
        if not new_value:
            self.settings_container["browser_support"] = False
            return

        self.browser_support_toggle.change_state(False)
        self.settings_container["browser_support"] = False
        if self.dialog:
            self.dialog.close()
        self.dialog = BrowserSupportDialog(
            self.browser_support_callback,
            self.cancel_callback,
            self.language)
        self.dialog.open()

    def browser_support_callback(self):
        self.browser_support_toggle.change_state(True)
        self.settings_container["browser_support"] = True
        self.cancel_callback()

    def show_change_key_dialog(self, *arg):
        """Function to make the change database key dialog visible.
        """
        if self.dialog:
            self.dialog.close()
        self.dialog = ChangeKeyDialog(
            self.database,
            self.cancel_callback,
            self.cancel_callback,
            self.language)
        self.dialog.open()

    def show_bci_auth_enroll_dialog(self, *arg):
        """Function to make the enrollment dialog visible.
        """
        if self.dialog:
            self.dialog.close()
        self.dialog = BCIAuthEnrollDialog(
            self.settings_container,
            self.cancel_callback,
            self.enroll_update_callback,
            self.language)
        self.dialog.open()

    def enroll_update_callback(self):
        """After any change in regards to the enrollment, make sure
        Templates possibly stored in database are updated.
        """
        json_templates = self.verification_system.database.to_json()
        self.database.add_field("TEMPLATES", json_templates)

    def __msg(self, text):
        Snackbar(
            text=text,
            size_hint_x=.4,
            snackbar_x="10dp",
            snackbar_y="10dp",
        ).open()
