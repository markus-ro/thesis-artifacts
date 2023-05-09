import pyperclip
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomsheet import MDGridBottomSheet
from kivymd.uix.list import OneLineListItem
from kivymd.uix.snackbar import Snackbar
from lib.database import EncryptedDatabase, LoginContainer
from lib.dialogs import DeletionConformationDialog, DetailDialog
from lib.language_manager import LanguageManager


class OverviewScreen(Screen):
    __slots__ = "database", "overview_items", "populated", "dialog", "language"

    def __init__(
            self,
            database: EncryptedDatabase,
            language: LanguageManager,
            **kw):
        super().__init__(**kw)
        self.database_manager = database
        self.language = language
        self.overview_items = []
        self.populated = False
        self.dialog = None

    def on_cancel(self):
        """Dialog cancel callback. Closes dialogs and resets property.
        """
        if self.dialog:
            self.dialog.close()
            self.dialog = None

    def on_detail_dialog_callback(self, _id, domain, username, password):
        """Dialog conformation callback. If field _id is set, updates entry
        in database. Else creates a new entry.

        :param _id: None if new entry else id of entry to change
        :type _id: int
        :param domain: Text of domain input in dialog. Is ignored when entry is updated.
        :type domain: str
        :param username: Text of username input in dialog
        :type username: str
        :param password: _description_
        :type password: _type_
        """
        if _id:
            self.database_manager[int(_id)].username = username
            self.database_manager[int(_id)].password = password
        else:
            self.database_manager.add(domain, username, password)
            entry = self.database_manager.data[-1]
            self.add_item_to_list(entry)

        self.database_manager.save()
        self.dialog.close()

    def on_enter(self):
        if self.populated and self.database_manager.changed:
            # Something has changed since the last time we displayed this screen
            # Update view to accommodate changes
            for entry in self.overview_items:
                self.ids.overview_list.remove_widget(entry)
            self.database_manager.changed = False
        elif self.populated:
            return
        self.update_view()

    def __set_clipboard(self, content: str, ident: str):
        if not content or content == "":
            self.__msg(self.language["copy_empty_snack"])
            return
        pyperclip.copy(content)
        self.__msg(self.language["copy_clipboard_snack"])

    def remove_item(self, id: str):
        if self.dialog:
            self.dialog.close()
            self.dialog = None

        overview_item = [x for x in self.overview_items if x.id == id][0]
        self.ids.overview_list.remove_widget(overview_item)
        self.overview_items.remove(overview_item)
        self.database_manager.data.remove(self.database_manager[int(id)])
        self.database_manager.save()

    def show_bottom_sheet(self, instance):
        bottom_sheet_menu = MDGridBottomSheet()
        data = self.database_manager[int(instance.id)]
        bottom_sheet_menu.add_item(
            self.language["copy_username_sheet"],
            lambda x: self.__set_clipboard(
                data.username,
                "Username"),
            "account")
        bottom_sheet_menu.add_item(
            self.language["copy_password_sheet"],
            lambda x: self.__set_clipboard(
                data.password,
                "Password"),
            "account-key")
        bottom_sheet_menu.add_item(
            self.language["edit_entry_sheet"],
            lambda x: self.show_detail_dialog(
                instance.id),
            "lead-pencil")
        bottom_sheet_menu.add_item(
            self.language["delete_entry_sheet"],
            lambda x: self.show_confirmation_dialog(
                instance.id),
            "delete")

        bottom_sheet_menu.open()

    def show_confirmation_dialog(self, id: str):
        if self.dialog:
            self.dialog.close()
        self.dialog = DeletionConformationDialog(
            self.remove_item, self.on_cancel, self.language, self.database_manager[int(id)].domain, id)
        self.dialog.open()

    def show_detail_dialog(self, id: str):
        if self.dialog:
            self.dialog.close()
        if id:
            entry = self.database_manager[int(id)]
            self.dialog = DetailDialog(
                self.on_detail_dialog_callback,
                self.on_cancel,
                self.language,
                id,
                entry.domain,
                entry.username,
                entry.password)
        else:
            self.dialog = DetailDialog(
                self.on_detail_dialog_callback,
                self.on_cancel,
                self.language,
                id)
        self.dialog.open()

    def clean_up_view(self):
        for entry in self.overview_items:
            self.ids.overview_list.remove_widget(entry)
        self.overview_items = []
        self.populated = False

    def update_view(self):
        self.clean_up_view()
        for entry in self.database_manager.data:
            self.add_item_to_list(entry)
        self.populated = len(self.overview_items) > 0

    def add_item_to_list(self, entry: LoginContainer):
        list_item = OneLineListItem(text=entry.domain)
        list_item.id = str(entry.id)
        list_item.bind(on_press=self.show_bottom_sheet)
        self.ids.overview_list.add_widget(list_item)
        self.overview_items.append(list_item)

    def __msg(self, text):
        Snackbar(
            text=text,
            size_hint_x=.4,
            snackbar_x="10dp",
            snackbar_y="10dp",
        ).open()
