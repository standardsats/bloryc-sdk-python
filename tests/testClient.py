from __future__ import absolute_import, division, print_function, unicode_literals
from future.builtins import *
import unittest

from bloryc.api import Client
from os import getenv


class ClientTestSuite(unittest.TestCase):
    def setUp(self):
        super(ClientTestSuite, self).setUp()
        client_id = getenv("CLIENT_ID", default=None)
        api_key = getenv("API_SECRET", default=None)
        self.api = Client(client_id, api_key, demo=True)
        # to avoid test order problems
        response = self.api.login()
        self.assertIn("access_token", response)
        # Look into test vectors next time
        self.cid = "cc9ecf18-c417-4a2f-a386-186ef9df7097"
        self.card = "895fb62b-bd7a-490e-8424-59feba68a626"
        self.callback = "https://dexpa.online/standardsats"

        self.update_info = {
            "status": "ACTIVE",
            "active_from": None,
            "active_to": "2023-05-31T15:21:45.423Z",
            "allowed_transaction_count": "multiple",
            "allowed_currencies": None,
            "limits": [
                {"interval": "per transaction", "amount": 1},
                {"interval": "daily", "amount": 1},
            ],
        }

        self.new_card = {
            "cardholder_id": self.cid,
            "settings": {
                "active_from": None,
                "active_to": "2023-05-31T15:21:45.423Z",
                "allowed_transaction_count": "multiple",
                "allowed_currencies": None,
                "limits": [
                    {"interval": "per transaction", "amount": 5},
                    {"interval": "weekly", "amount": 500},
                ],
            },
        }

    def assert_auth_header_present(self):
        pass

    def testGetCardholders(self):
        response = self.api.get_cardholders()
        # {'cardholder_id': 'cc9ecf18-c417-4a2f-a386-186ef9df7097', 'user': {'email': 'user777@example.com', 'id': 15, 'account': {'first_name': 'Alex', 'middle_name': 'V', 'last_name': 'K', 'date_of_birth': '1975-03-03', 'phone': '1111111111', 'type': 'cardholder', 'id': 8, 'user_id': 15, 'company': {'name': 'standart', 'registration_number': 'TU1111111119', 'phone': '1111111119', 'primary_contact_email': 'teststandart@client.test', 'id': 9}}}, 'cards': [{'cardholder_id': 'cc9ecf18-c417-4a2f-a386-186ef9df7097', 'form_factor': 'virtual', 'card_id': '895fb62b-bd7a-490e-8424-59feba68a626', 'created_at': '2022-07-10T12:04:35.514030Z', 'mask_number': '************5682', 'nick_name': None, 'status': 'ACTIVE', 'brand': 'VISA', 'settings': {'active_from': '2022-07-10T12:04:35.513896Z', 'active_to': '2023-05-31T15:21:45.423Z', 'allowed_currencies': [''], 'allowed_transaction_count': 'multiple', 'limits': [{'interval': 'per transaction', 'amount': 5}, {'interval': 'weekly', 'amount': 500}, {'interval': 'all time', 'amount': 1000}]}, 'bin': {'scheme': 'Visa', 'code': '47259300', 'id': 1}, 'balance': {'card_id': '32', 'limit': 1000.0, 'available': 1000.0, 'used': 0.0}}]}
        self.assertTrue(len(response) > 0)
        self.assertIn("cardholder_id", response[0])
        self.assertIn("user", response[0])
        self.assertIn("cards", response[0])

    def testGetCards(self):
        response = self.api.get_cards(self.cid)
        self.assertTrue(len(response) > 0)
        self.assertIn("cardholder_id", response[0])
        self.assertIn("form_factor", response[0])
        self.assertIn("card_id", response[0])

    def testGetBalance(self):
        response = self.api.get_balance()
        self.assertIn("currency", response)
        self.assertIn("total_amount", response)
        self.assertIn("available_amount", response)

    def testGetBins(self):
        response = self.api.get_bins()
        self.assertTrue(response == [])

    def testGetCardLimits(self):
        response = self.api.card_limits(self.card)
        self.assertIn("currency", response)
        self.assertIn("limits", response)

    def testGetCardDetails(self):
        response = self.api.card_details(self.card)
        self.assertIn("cardholder_id", response)
        self.assertIn("form_factor", response)
        self.assertIn("card_id", response)

    def testGetCardDetailsSecure(self):
        response = self.api.card_details_secure(self.card)
        self.assertIn("card_number", response)
        self.assertIn("cvv", response)
        self.assertIn("expiry_month", response)

    def testGetCardTransactions(self):
        response = self.api.card_transactions(self.card)
        self.assertTrue(len(response) > 0)
        self.assertIn("status", response[0])
        self.assertIn("failure_reason", response[0])
        self.assertIn("merchant_name", response[0])

    def testGetCardTransactionsReversed(self):
        response = self.api.card_transactions_reversed(self.card)
        self.assertTrue(len(response) > 0)
        self.assertIn("status", response[0])
        self.assertTrue(response[0]["status"] == "REVERSED")
        self.assertIn("failure_reason", response[0])
        self.assertIn("merchant_name", response[0])

    def testCreateCard(self):
        response = self.api.create_card(self.new_card)
        self.assertIn("cardholder_id", response)
        self.assertIn("form_factor", response)
        self.assertIn("settings", response)

    def testUpdateCard(self):
        response = self.api.update_card(self.card, self.update_info)
        self.assertIn("cardholder_id", response)
        self.assertIn("form_factor", response)
        self.assertIn("settings", response)

    def testSetCallback(self):
        response = self.api.set_tx_callback(self.callback)
        self.assertIn("msg", response)
