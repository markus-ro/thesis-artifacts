import unittest

import numpy as np

from neuropack import TemplateDatabase


class TemplateDatabaseTests(unittest.TestCase):
    def test_creation_from_dict(self):
        """Check, that database can be created from dictionary
        """
        # arrange
        database_dict = {"ps1": [np.array([1, 2, 3, 4, 5]), np.array(
            [0.4, 0.5, 6, 6])], "ps2": [np.array([5, 6, 7, 8, 9])]}

        # action
        database = TemplateDatabase.construct_from_dict(database_dict)

        # check
        for k in database_dict:
            self.assertTrue(
                database.get_templates(k)[0],
                f"Could not find template(s) with id \"{k}\" in database")
            self.assertListEqual(
                database.get_templates(k)[1],
                database_dict[k],
                f"Template(s) found for id \"{k}\" did not match with the ones added prior.")

    def test_creation(self):
        """Check, that database can be created using subsequent add commands.
        """
        # arrange
        database_dict = {"ps1": [np.array([1, 2, 3, 4, 5]), np.array(
            [0.4, 0.5, 6, 6])], "ps2": [np.array([5, 6, 7, 8, 9])]}

        # action
        database = TemplateDatabase()
        for k in database_dict:
            for t in database_dict[k]:
                database.add_template(k, t)

        # check
        for k in database_dict:
            self.assertTrue(
                database.get_templates(k)[0],
                f"Could not find template(s) with id \"{k}\" in database")
            self.assertListEqual(
                database.get_templates(k)[1],
                database_dict[k],
                f"Template(s) found for id \"{k}\" did not match with the ones added prior.")

    def test_identity_removal(self):
        """Check, that a identity can be removed from the database.
        """
        # arrange
        database_dict = {"ps1": [np.array([1, 2, 3, 4, 5]), np.array(
            [0.4, 0.5, 6, 6])], "ps2": [np.array([5, 6, 7, 8, 9])]}
        database = TemplateDatabase.construct_from_dict(database_dict)

        # action
        database.remove_identity("ps1")

        # check
        self.assertFalse(
            database.get_templates("ps1")[0],
            "Id \"ps1\" was found in database. This was not expected.")
        self.assertIsNone(
            database.get_templates("ps1")[1],
            "Database returned templates when it was not intended.")
        self.assertTrue(
            database.get_templates("ps2")[0],
            "Expected template(s) with id \"ps2\" to be presented.")
        self.assertListEqual(
            database.get_templates("ps2")[1],
            database_dict["ps2"],
            f"Template(s) found for id \"ps2\" did not match with the ones added prior.")

    def test_json_load_save(self):
        """Check, that database can be saved and loaded as json string.
        """
        # arrange
        database_dict = {"ps1": [np.array([1, 2, 3, 4, 5]), np.array(
            [0.4, 0.5, 6, 6])], "ps2": [np.array([5, 6, 7, 8, 9])]}
        database = TemplateDatabase.construct_from_dict(database_dict)

        # action
        json_str = database.to_json()
        database2 = TemplateDatabase.construct_from_json(json_str)

        # check
        self.assertEqual(
            database,
            database2,
            "Database constructed from saved json is not equal to original one.")
