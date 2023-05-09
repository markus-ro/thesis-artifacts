import sys

from lib.language_manager import LanguageManager

sys.path.append("./code/neuropack")

if __name__ == "__main__":
    import os
    from os import getcwd, path
    from threading import Thread

    from controls.application_screen import ApplicationScreen
    from controls.login_screen import LoginScreen
    from kivy.config import Config
    from kivy.core.window import Window
    from kivy.lang import Builder
    from kivy.uix.screenmanager import ScreenManager
    from kivymd.app import MDApp
    from lib.auth_factory import build_verification
    from lib.browser_communication.browser_worker import BrowserWorker
    from lib.database import EncryptedDatabase
    from lib.settings_container import SettingsContainer

    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Builder.load_file("views/login_view.kv")
    Builder.load_file("views/application_view.kv")
    Builder.load_file("views/dialogs.kv")
    Builder.load_file("views/app_views/overview_view.kv")
    Builder.load_file("views/app_views/settings_view.kv")

    class FoundationPM(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.title = "Foundation Password Manager"
            self.database = EncryptedDatabase()
            self.settings = SettingsContainer(
                path.join(getcwd(), "settings.json"),
                build_verification())
            self.settings.verification_system.configure_logging(
                self.settings["logging"], self.settings["file_logging"])

            t = Thread(target=self.start_server)
            t.start()

            self.theme_cls.material_style = "M3"
            self.theme_cls.theme_style = "Dark" if self.settings["dark_theme"] else "Light"

            self.language = LanguageManager(self.settings["language_file"])

            if os.name == 'nt':
                from ctypes import c_int64, windll
                windll.user32.SetProcessDpiAwarenessContext(c_int64(-4))

        def build(self):
            """Function to stitch everything together.

            :return: Kivy Builder.
            :rtype: Builder
            """
            Window.bind(on_drop_file=self._on_drop_file)
            self.screen_manager = ScreenManager()
            self.login_screen = LoginScreen(
                self.database, self.settings, self.language, name="login_view")
            self.application_screen = ApplicationScreen(
                self.database, self.settings, self.language, name="application_view")
            self.screen_manager.add_widget(self.login_screen)
            self.screen_manager.add_widget(self.application_screen)
            return self.screen_manager

        def start_server(self):
            """Start web server in separate thread for faster start up time.
            """
            self.browser_worker = BrowserWorker(self.database, self.settings)
            self.browser_worker.start()

        def _on_drop_file(self, window, file_path: str, x, y) -> None:
            """Event handler to handle file drop in window. Files can only be
            dropped if current view is the "login_view".

            :param window: Window object.
            :type window: Window
            :param file_path: Path of file dropped into window.
            :type file_path: str
            """
            if self.screen_manager.current == "login_view" and not self.database.connected:
                self.login_screen.set_file_path(file_path.decode("utf-8"))

        def on_stop(self):
            """Event handler to handle application stop. This function is called when the application is closed. It will stop the web server and disconnect the verification device. It will also hide the window to prevent the user from seeing the window close.
            """
            Window.hide()
            t = None
            if self.settings.verification_system:
                device = self.settings.verification_system.device
                if device and device.is_connected():
                    t = Thread(target=device.disconnect)
                    t.start()
            if self.browser_worker.running:
                self.browser_worker.stop()
            if t:
                t.join()
            return super().on_stop()


if __name__ == "__main__":
    FoundationPM().run()
