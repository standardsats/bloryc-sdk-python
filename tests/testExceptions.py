from __future__ import absolute_import, division, print_function, unicode_literals

from os import getenv
import unittest
from bloryc import exceptions
from bloryc.api import Client


class ExceptionsTestSuite(unittest.TestCase):
    def setUp(self):
        client_id = getenv("CLIENT_ID", default=None)
        api_key = getenv("API_SECRET", default=None)
        # self.api = Client(client_id, api_key)
        self.api = Client("test", "test")

    def testTokenError(self):
        # Not finished. Not working as for 19.07.2022
        self.assertRaises(exceptions.FormatError, self.api.login())
