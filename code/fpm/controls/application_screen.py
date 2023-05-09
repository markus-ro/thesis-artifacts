import sys

from controls.app_controls.overview_screen import OverviewScreen
from controls.app_controls.settings_screen import SettingsScreen
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.snackbar import Snackbar
from lib.database import EncryptedDatabase
from lib.language_manager import LanguageManager
from lib.settings_container import SettingsContainer
from neuropack import TemplateDatabase

sys.path.append("./code/Library")


class ApplicationScreen(Screen):
    __slots__ = "database", "overview_items", "populated", "language", "overview", "settings", "verification"

    def __init__(
            self,
            database: EncryptedDatabase,
            settings: SettingsContainer,
            language: LanguageManager,
            **kw):
        """The application screen is the main screen of the application. It contains the overview screen and the settings screen. The application screen is the first screen that is shown after the login screen.

        :param database: The database that is used by the application.
        :type database: EncryptedDatabase
        :param settings: The settings that are used by the application.
        :type settings: SettingsContainer
        :param language: The language manager that is used by the application.
        :type language: LanguageManager
        """
        super().__init__(**kw)
        self.database = database
        self.settings = settings
        self.verification = settings.verification_system
        self.language = language
        self.populated = False
        self.overview = None

    def on_enter(self):
        """Called when the screen is entered. The overview screen is populated with the database entries.
        """
        if self.overview:
            self.overview.on_enter()
        if self.populated:
            return
        self.populated = True
        self.overview = OverviewScreen(
            self.database, self.language, name="overview_screen")
        self.ids.screen_manager.add_widget(self.overview)
        self.settings = SettingsScreen(
            self.database,
            self.settings,
            self.language,
            name="settings_screen")
        self.ids.screen_manager.add_widget(self.settings)

    def on_action(self, button):
        """Handles the action button clicks. The action button is located in the lower right corner of the screen. It can be used to lock the database, disconnect the database, or add a new entry to the database.

        :param button: The button that was clicked.
        :type button: kivymd.uix.button.MDFloatingActionButton
        """
        if button.icon == "account-lock":
            self.on_lock()
        elif button.icon == "lan-disconnect":
            self.on_disconnect()
        elif button.icon == "plus":
            self.overview.show_detail_dialog(None)
        self.ids.action_button.close_stack()

    def on_overview_screen(self):
        """Switches to the overview screen.
        """
        self.on_enter()
        self.ids.screen_manager.current = "overview_screen"

    def on_settings_screen(self):
        """Switches to the settings screen.
        """
        self.on_enter()
        self.ids.screen_manager.current = "settings_screen"

    def on_lock(self):
        """Switches to the login screen, thereby locking the database.
        """
        self.manager.transition.direction = "down"
        self.manager.current = "login_view"

    def on_disconnect(self):
        """Disconnects the database and switches to the login screen. The database is also resetted.
        """
        self.database.disconnect()
        self.verification.database = TemplateDatabase()
        self.overview.clean_up_view()
        self.on_lock()
        self.ids.screen_manager.current = "overview_screen"
        App.get_running_app().title = "Foundation Password Manager"
