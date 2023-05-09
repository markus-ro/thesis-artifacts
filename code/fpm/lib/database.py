import base64
from os.path import exists

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class LoginContainer():
    __slots__ = "domain", "username", "password", "separator", "id"

    def __init__(self, id: int, domain: str, username: str,
                 password: str) -> None:
        """Constructor for the LoginContainer class. LoginContainers
        are meant to hold all credentials for a single entry in the
        password manager.

        :param id: Unique ID of entry.
        :type id: int
        :param domain: Domain for which the credentials are.
        :type domain: str
        :param username: username for authentication.
        :type username: str
        :param password: Password for authentication.
        :type password: str
        """
        self.id = id
        self.domain = domain
        self.username = username
        self.password = password
        self.separator = "\t\t\t"

    def __str__(self) -> str:
        return str(self.id) + self.separator + self.domain + self.separator + \
            self.username + self.separator + self.password


class EncryptedDatabase():
    __slots__ = "fields", "key", "file_name", "data", "database_field",\
        "preface_template", "postface_template", "connected", "max", "changed", "selected"

    def __init__(self):
        self.connected = False
        self.data = []
        self.fields = dict()
        self.database_field = "DATABASE"
        self.preface_template = "----- BEGIN {name} DATA -----"
        self.postface_template = "----- END {name} DATA -----"
        self.max = 0
        self.changed = False
        self.selected = None

    def add_field(self, name: str, value: str):
        """Add a new field to the additional field section of database.
        Field name must be all uppercase and letters only. Can also
        be used to edit already existing field by overwriting it.
        Note, after using this function database performs a save operation.

        :param name: Name of new field.
        :type name: str
        :param value: Value of new field.
        :type value: str
        :raises Exception: Field name should only contain letters.
        :raises Exception: Field name should be all uppercase.
        :raises Exception: Field name can not be equal to default database field name.
        """
        if not name.isalpha():
            raise Exception("Field name should only contain letters.")

        if not name.isupper():
            raise Exception("Field name should be all uppercase.")

        if name == self.database_field:
            raise Exception(
                "Field name can not be equal to default database field name.")

        self.fields[name] = value
        self.save()

    def get_field(self, name: str) -> str:
        """Returns the value for the field with given name.

        :param name: Name of field, should only contain letters and be all uppercase
        :type name: str
        :return: Value of field, if field not present None is returned
        :rtype: str
        """
        if name in self.fields:
            return self.fields[name]
        return None

    def add(self, domain: str, username: str, password: str) -> None:
        """Adds a new entry to database with given data. Updated
        changed flag.

        :param domain: Domain field of new entry.
        :type domain: str
        :param username: username field of new entry.
        :type username: str
        :param password: Password field of new entry.
        :type password: str
        """
        if self.connected:
            self.max += 1
            self.data.append(LoginContainer(self.max, domain, username,
                                            password))
            self.changed = True

    def __create_field(self, name: str, content: str):
        fin = self.preface_template.format(name=name) + "\r\n"
        _content = content.replace("\\", "\\\\")
        _content = _content.replace("-", "--")
        fin += _content + "\r\n"
        return fin + self.postface_template.format(name=name) + "\r\n"

    def save(self) -> None:
        """Saves the database to disk. The database is encrypted using the
        key in the key field. Disk location is taken from the file_name field.
        """
        if self.connected:
            # Create main database content in fields dict
            self.fields[self.database_field] = "\r\n".join(
                [str(x) for x in self.data])

            # Create final file content
            fin = ""
            for (k, v) in self.fields.items():
                fin += self.__create_field(k, v)

            # Encrypt file content
            fin = Fernet(self.key).encrypt(fin.encode())

            # Write file content to disk
            with open(self.file_name, "wb") as file:
                file.write(fin)

    def open(self, file_name: str, key: str) -> bool:
        """Function to open a new database connection. Database is opened from disk
        with file_name parameter as location. Parameter key is
        used to decrypt database before loading.

        :param file_name: Location of database on disk.
        :type file_name: str
        :param key: Key to decrypt database
        :type key: str
        :return: True if database is already open with given key path pair or
        can be opened. False if not.
        :rtype: bool
        """
        if self.connected:
            if self.key == self.translate_key(key) and \
                    self.file_name == file_name:
                return True
            else:
                return False

        # Set fields
        self.file_name = file_name
        self.key = self.translate_key(key)

        # File does not yet exist, create new database
        if not exists(self.file_name):
            self.connected = True
            return True

        # File is empty, create new database
        if open(self.file_name, "r").read() == "":
            self.connected = True
            return True

        # Read file content
        content = ""
        with open(self.file_name, "rb") as file:
            content = file.read()

        # Try to decrypt file
        try:
            content = Fernet(self.key).decrypt(content).decode()
        except BaseException:
            return False

        # Extract fields
        self.__extract_fields(content)

        # Check that we have a database entry
        if self.database_field not in self.fields:
            return False

        # Get and parse database
        database_str = self.fields[self.database_field]
        del self.fields[self.database_field]

        try:
            self.__parse_database_data(database_str)
            self.connected = True
            return True
        except BaseException:
            pass

        print("Something went wrong")
        return False

    def disconnect(self):
        """Disconnect manager from database. Resets whole class back
        to state at creation.
        """
        self.fields = dict()
        self.connected = False
        self.data = []
        self.file_name = None
        self.key = None

    def translate_key(self, key):
        """Function to transform arbitrary keys to keys conforming to Fernet.
        Taken from: https://incolumitas.com/2014/10/19/using-the-python-cryptography-module-with-custom-passwords/

        :param key: Arbitrary key.
        :type key: str
        :return: Transformed key, fit for use with Fernet.
        :rtype: str
        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(key.encode())
        return base64.urlsafe_b64encode(digest.finalize())

    def __extract_fields(self, file_content: str):
        """Finds and extracts marked fields inside of the database file.
        Fields are marked with a preface and end with a postface.

        :param file_content: Read in content of file.
        :type file_content: str
        """
        cur_name = None
        content = []
        for line in file_content.split("\r\n"):
            # Check for line beginning
            if line.startswith(
                    "----- BEGIN ") and line.endswith(" DATA -----"):
                cur_name = cur_name if cur_name else line[12:-11]
                continue

            # Check for line ending
            if line == self.postface_template.format(name=cur_name):
                line_content = "\r\n".join(content)

                # Normalize content, if we are not in a DATABASE field.
                # For DATABASE field, normalization is done in the parsing
                # method.
                if cur_name != self.database_field:
                    line_content = line_content.replace("\\\\", "\\")
                    line_content = line_content.replace("--", "-")

                self.fields[cur_name] = line_content
                cur_name = None
                content = []
                continue

            # We are inside of a field, add line
            if cur_name:
                content.append(line)

    def __parse_database_data(self, content: str) -> None:
        """Parse database data from stored string. Data has to be decrypted beforehand.

        :param content: Content of database file after decryption.
        :type content: str
        """
        for line in content.split("\r\n"):
            if line.isspace() or line == "":
                continue
            # Remove transformations
            decoded_line = line.replace("\\\\", "\\")
            decoded_line = decoded_line.replace("--", "-")

            # Extract data
            entries = decoded_line.split("\t\t\t")
            entries[0] = int(entries[0])
            self.data.append(LoginContainer(entries[0], entries[1],
                                            entries[2], entries[3]))
            if entries[0] > self.max:
                self.max = entries[0]

    def __getitem__(self, _id: str) -> LoginContainer:
        """Accessor to get entry by unique id.

        :param _id: Candidate id of LoginContainer entry in database
        :type _id: str
        :return: LoginContainer with given id if found. Else None.
        :rtype: _type_
        """
        for entry in self.data:
            if entry.id == _id:
                return entry
        return None
