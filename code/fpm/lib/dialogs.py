import string
from abc import ABC
from random import choices

from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from lib.language_manager import LanguageManager
from lib.settings_container import SettingsContainer
from plyer import notification


def msg(text):
    """ Shows a snackbar with the given text

    :param text: The text to show
    """
    Snackbar(
        text=text,
        size_hint_x=0.35,
        snackbar_x="10dp",
        snackbar_y="10dp",
    ).open()


class DetailDialogContent(BoxLayout):
    def __init__(self, chip_callback, pw_button_callback, **kwargs):
        super().__init__(**kwargs)
        self.chip_callback = chip_callback
        self.pw_button_callback = pw_button_callback

    def on_release_chip(self, chip):
        self.chip_callback(chip)

    def on_generate_password(self):
        self.pw_button_callback()


class ChangeDatabaseKeyContent(BoxLayout):
    pass


class InstallationDialogContent(BoxLayout):
    pass


class BCIAuthEnrollContent(BoxLayout):
    pass


class AbstractBaseDialog(ABC):
    def __init__(self, confirmation_callback, cancel_callback) -> None:
        super().__init__()
        self.confirmation_callback = confirmation_callback
        self.cancel_callback = cancel_callback
        self.dialog = None

    def open(self):
        if self.dialog:
            self.dialog.open()

    def close(self):
        self.dialog.dismiss(force=True)


class DeletionConformationDialog(AbstractBaseDialog):
    def __init__(
            self,
            confirmation_callback,
            cancel_callback,
            language: LanguageManager,
            title: str,
            _id: str) -> None:
        super().__init__(confirmation_callback, cancel_callback)
        self.dialog = MDDialog(
            title=title,
            text=language["delete_text_diag"],
            buttons=[
                MDRaisedButton(
                    text=language["delete_btn"],
                    on_release=lambda x: self.confirmation_callback(_id)
                ),
                MDFlatButton(
                    text=language["cancel_btn"],
                    on_release=lambda x: self.cancel_callback()
                ),
            ]
        )


class DetailDialog(AbstractBaseDialog):
    def __init__(
            self,
            confirmation_callback,
            cancel_callback,
            language: LanguageManager,
            _id: str,
            domain: str = "",
            username: str = "",
            password: str = "") -> None:
        super().__init__(confirmation_callback, cancel_callback)
        self.dialog = MDDialog(
            title=language["edit_entry_diag"] if _id else language["new_entry_diag"],
            type="custom",
            content_cls=DetailDialogContent(
                self.on_release_chip,
                self.on_generate_password),
            buttons=[
                MDRaisedButton(
                    text=language["save_btn"] if id else language["save_btn"],
                    on_release=lambda x: self.__internal_callback()),
                MDFlatButton(
                    text=language["cancel_btn"],
                    on_release=lambda x: self.cancel_callback())],
        )
        self._id = _id
        self.dialog.content_cls.ids.dialog_domain.text = domain
        self.dialog.content_cls.ids.dialog_username.text = username
        self.dialog.content_cls.ids.dialog_password.text = password
        self.dialog.content_cls.ids.dialog_domain.disabled = \
            True if _id else False
        self.upper_case = False
        self.numbers = False
        self.special_chars = False

    def on_release_chip(self, chip):
        if chip == "upper_case_chip":
            self.upper_case = not self.upper_case
        elif chip == "numbers_chip":
            self.numbers = not self.numbers
        elif chip == "special_chip":
            self.special_chars = not self.special_chars

    def on_generate_password(self):
        character_pool = string.ascii_lowercase

        if self.upper_case:
            character_pool += string.ascii_uppercase
        if self.numbers:
            character_pool += "0123456789"
        if self.special_chars:
            character_pool += string.punctuation

        pw = "".join(choices(character_pool, k=64))
        self.dialog.content_cls.ids.dialog_password.text = pw

    def __internal_callback(self):
        domain = self.dialog.content_cls.ids.dialog_domain.text.strip()
        username = self.dialog.content_cls.ids.dialog_username.text.strip()
        password = self.dialog.content_cls.ids.dialog_password.text.strip()
        if not domain or domain.isspace():
            msg("Please enter a domain")
            return
        self.confirmation_callback(self._id, domain, username, password)


class ChangeKeyDialog(AbstractBaseDialog):
    def __init__(self, database_manager, confirmation_callback,
                 cancel_callback, language: LanguageManager) -> None:
        super().__init__(confirmation_callback, cancel_callback)
        self.database_manager = database_manager
        self.language = language
        self.dialog = MDDialog(
            title=language["change_key_diag"],
            type="custom",
            content_cls=ChangeDatabaseKeyContent(),
            buttons=[
                MDRaisedButton(
                    text=language["save_btn"],
                    on_release=lambda x: self.__internal_callback()
                ),
                MDFlatButton(
                    text=language["cancel_btn"],
                    on_release=lambda x: self.cancel_callback()
                )],
        )

    def __internal_callback(self):
        if not self.database_manager.connected:
            msg(self.language["no_database_connected_snack"])
            return
        old = self.database_manager.\
            translate_key(self.dialog.content_cls.ids.
                          dialog_old_key.text.strip())
        new = self.dialog.content_cls.ids.dialog_key.text.strip()
        new_r = self.dialog.content_cls.ids.dialog_repeat_key.text.strip()

        if old != self.database_manager.key:
            msg(self.language["incorrect_key_snack"])
            return

        if not new or new.isspace():
            msg(self.language["fill_in_fields_snack"])
            return

        if new != new_r:
            msg(self.language["keys_no_match_snack"])
            return

        self.database_manager.key = self.database_manager.translate_key(new)
        self.database_manager.save()
        self.confirmation_callback()


class BrowserSupportDialog(AbstractBaseDialog):
    def __init__(
            self,
            confirmation_callback,
            cancel_callback,
            language: LanguageManager) -> None:
        super().__init__(confirmation_callback, cancel_callback)
        self.dialog = MDDialog(
            title=language["browser_support_diag"],
            text=language["browser_support_warning"],
            buttons=[
                MDRaisedButton(
                    text=language["continue_btn"],
                    on_release=lambda x: self.confirmation_callback()
                ),
                MDFlatButton(
                    text=language["cancel_btn"],
                    on_release=lambda x: self.cancel_callback()
                ),
            ]
        )


class BCIAuthEnrollDialog(AbstractBaseDialog):
    def __init__(
            self,
            settings: SettingsContainer,
            cancel_callback,
            update_callback,
            language: LanguageManager) -> None:
        super().__init__(None, cancel_callback)
        self.settings_container = settings
        self.language = language
        self.update_callback = update_callback

        verification_system = self.settings_container.verification_system
        has_auth = True if verification_system else False
        is_connected = verification_system.device.is_connected()
        is_enrolled = settings["id"] in verification_system.database.get_all_idents(
        )

        self.enroll_btn = MDRaisedButton(
            text=language["enroll_btn"],
            on_release=lambda x: self.perform_enrollment()
        )

        self.enroll_btn.disabled = not (
            has_auth and is_connected and not is_enrolled)

        self.reset_btn = MDRaisedButton(
            text=language["reset_btn"],
            on_release=lambda x: self.reset_database()
        )

        self.reset_btn.md_bg_color = "#b71c1c"
        self.reset_btn.disabled = not (
            has_auth and is_connected and is_enrolled)

        self.dialog = MDDialog(
            title="KeyWave",
            type="custom",
            content_cls=BCIAuthEnrollContent(),
            buttons=[
                self.enroll_btn,
                self.reset_btn,
                MDFlatButton(
                    text=language["cancel_btn"],
                    on_release=lambda x: self.cancel_callback()
                )],
        )
        self.dialog.content_cls.ids["info_text"].visible = not (
            has_auth and is_connected)

        task = verification_system.task
        self.dialog.content_cls.ids["assigned_image"].source = task.target_image

    def perform_enrollment(self):
        verification_system = self.settings_container.verification_system
        res = verification_system.enroll(self.settings_container["id"])
        if res:
            self.update_callback()
            self.cancel_callback()
        else:
            notification.notify("Enrollment",
                                "Something went wrong. Please try again.")

    def reset_database(self):
        self.settings_container.verification_system.database.remove_identity(
            self.settings_container["id"])
        self.update_callback()
        self.cancel_callback()
