import polib


class LanguageManager():
    def __init__(self, lang_file: str):
        """Language manager for FoundationPM. Takes care of loading and parsing language files. Language files are in the .po format. Language files are parsed on initialization. Language files are parsed using the polib library.

        :param lang_file: Path to language file.
        :type lang_file: str
        """
        self.lang_file = lang_file
        self.__parse_file()

    def update_language_file(self, lang_file: str):
        """Update language file. Language file is parsed on initialization. Language files are parsed using the polib library.

        :param lang_file: Path to language file.
        :type lang_file: str
        """
        self.lang_file = lang_file
        self.__parse_file()

    def __parse_file(self):
        """Parse language file. Language files are parsed using the polib library. If parsing fails, the language dictionary is cleared. If the language file is not a .po file, the language dictionary is cleared. If the language file is a .po file, the language dictionary is updated.
        """
        self.lang_dict = dict()
        if not self.lang_file.endswith(".po"):
            return

        try:
            po_file = polib.pofile(self.lang_file)
        except BaseException:
            return

        for entry in po_file:
            self.lang_dict[entry.msgid] = entry.msgstr

    def __getitem__(self, key):
        if key not in self.lang_dict:
            return f"!{key}!"
        return self.lang_dict[key]
