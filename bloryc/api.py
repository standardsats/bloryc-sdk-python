from __future__ import absolute_import, division, print_function, unicode_literals
import base64
import hmac
import hashlib
import json

from future.moves.urllib.parse import urlencode
import requests

from . import exceptions

# change it to debug/demo hosts
from .exceptions import TokenError

config = {
    "BLORYC_DEMO_URL": "https://api.demo.spenxy.com",
    "BLORYC_URL": "https://api.spenxy.com",
}


class BaseRequest(object):
    @classmethod
    def send_request(cls, url, params=None, headers=None, body=None):
        if not headers:
            headers = {}
        headers["User-Agent"] = "SDK/Python"

        if not body:
            body = {}

        if params != None:
            return cls.process_result(
                requests.get(url, params=params, headers=headers, data=body)
            )
        else:
            return cls.process_result(requests.post(url, headers=headers, data=body))

    @classmethod
    def process_result(cls, result):
        if result.status_code == 400:
            raise exceptions.FormatError
        elif result.status_code == 401:
            raise exceptions.TokenError
        elif result.status_code == 403:
            raise exceptions.ScopeError
        elif result.status_code == 500:
            raise exceptions.ServerError
        elif result.status_code == 307:
            raise exceptions.FormatError
        return json.loads(result.text)


class Client(BaseRequest):
    def __init__(self, client_id, api_key, demo=False):
        if demo:
            self._url = config["BLORYC_DEMO_URL"]
        else:
            self._url = config["BLORYC_URL"]

        self.api_key = api_key
        self.client_id = client_id
        self.access_token = None

    def _send_authenticated_request(self, url, params=None, headers=None, body=None):
        if not self.access_token:
            raise TokenError
        if not headers:
            headers = {}
        headers["Authorization"] = f"Bearer {self.access_token}"
        url = self._url + url
        return self.send_request(url, params, headers, body)

    def _sign_payload(self, payload):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode("utf8"))

        h = hmac.new(self.access_token.encode("utf8"), data, hashlib.sha384)
        signature = h.hexdigest()
        return {
            "x-client-id": self.client_id,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data,
        }

    def login(self):
        full_url = self._url + "/api/v1/authentication/login/"
        # TODO add timestamps for expired logins

        login_data = self.process_result(
            requests.post(
                full_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "x-client-id": self.client_id,
                },
                data={},
            )
        )

        if not self.access_token:
            self.access_token = login_data["access_token"]
            return login_data
        else:
            print("Client already logged in")
            self.access_token = login_data["access_token"]
            return login_data

    def get_cardholders(self):
        return self._send_authenticated_request(
            "/api/v1/cardholder/get/all",
            params={},
        )

    def get_cards(self, cardholder_id):
        return self._send_authenticated_request(
            "/api/v1/cardholder/cards",
            params={"cardholder_id": cardholder_id},
        )

    def create_cardholder(self, data):
        return self._send_authenticated_request(
            "/api/v1/cardholder/create",
            body=json.dumps(data),
        )

    def get_balance(self):
        return self._send_authenticated_request("/api/v1/company/balance", params={})

    def get_bins(self):
        return self._send_authenticated_request("/api/v1/company/bins/all", params={})

    def create_card(self, card_info):
        return self._send_authenticated_request(
            "/api/v1/cards/card/create", body=json.dumps(card_info)
        )

    def update_card(self, card_id, update_info):
        # TODO: decide how to handle put requests
        # May be body + params info
        # doesn't work on 10.07.22
        full_url = self._url + "/api/v1/cards/card/update"
        return self.process_result(
            requests.put(
                full_url,
                params={"card_id": card_id},
                headers={
                    "Authorization": "Bearer {}".format(self.access_token),
                    "Content-Type": "application/json",
                },
                data=json.dumps(update_info),
            )
        )

    def card_details(self, card_id):
        return self._send_authenticated_request(
            "/api/v1/cards/card/details",
            params={"card_id": card_id},
        )

    def card_limits(self, card_id):
        return self._send_authenticated_request(
            "/api/v1/cards/card/limits",
            params={"card_id": card_id},
        )

    def card_details_secure(self, card_id):
        return self._send_authenticated_request(
            "/api/v1/cards/card/detail/sensitive",
            params={"card_id": card_id},
        )

    def card_transactions(self, card_id):
        return self._send_authenticated_request(
            "/api/v1/cards/transactions",
            params={"card_id": card_id},
        )

    def card_transactions_reversed(self, card_id):
        return self._send_authenticated_request(
            "/api/v1/cards/transactions/reversed",
            params={"card_id": card_id},
        )

    def set_tx_callback(self, url):
        # return self._send_authenticated_request(
        #    "/api/v1/cards/transactions/callback",
        #    params={"callback_url": url},
        # )
        full_url = self._url + "/api/v1/cards/transactions/callback"
        return self.process_result(
            requests.post(
                full_url,
                params={"callback_url": url},
                headers={
                    "Authorization": "Bearer {}".format(self.access_token),
                    "Content-Type": "application/json",
                },
                data={},
            )
        )

    def crypto_lnx_invoice(self, amount, external_id, card_id):
        full_url = self._url + "/api/v1/crypto/lnx/invoice"
        deposit_request = {
            "amount": str(amount),
            "external_id": external_id,
            "card_id": card_id,
        }
        return self.process_result(
            requests.post(
                full_url,
                headers={
                    "Authorization": "Bearer {}".format(self.access_token),
                    "Content-Type": "application/json",
                },
                data=json.dumps(deposit_request),
            )
        )

    def crypto_lnx_deposit(self, preimage):
        full_url = self._url + "/api/v1/crypto/lnx/deposit"
        proof_data = {
            "payment_preimage": str(preimage),
        }
        return self.process_result(
            requests.post(
                full_url,
                headers={
                    "Authorization": "Bearer {}".format(self.access_token),
                    "Content-Type": "application/json",
                },
                data=json.dumps(proof_data),
            )
        )
