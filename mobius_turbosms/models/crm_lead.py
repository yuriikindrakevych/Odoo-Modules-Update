#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
import logging
import json
import requests

_logger = logging.getLogger(__name__)

class TokenNotExistInOdoo(Exception):
    def __str__(self):
        return "Token not found in odoo"

class Lead(models.Model):
    _inherit = "crm.lead"

    def _sendTurboSMS(self, string_phone, text=False):
        token = self.env["ir.config_parameter"].sudo().get_param("token_for_turbosms")
        if not token:
            raise TokenNotExistInOdoo

        string_phone = string_phone.strip()
        url = "https://api.turbosms.ua/message/send.json"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if not text:
            text = "TurboSMS"
        data = {
            "recipients": [
                f"{string_phone}"
            ],
           "sms": {
              "sender": "ACLIMA",
              "text": f"{text}"
           }
        }
        r = requests.post(url, json=data, headers=headers)
        req_json = r.json()
        r.close()
        if r.status_code == 200:
            return {
                "status_code" : "200",
                "description" : "Message sent"
            }
        else:
            return {
                "status_code" : r.status_code,
                "description" : "Message not sent"
            }

    def _sendTurboSMS_call_odoo(self, res_id, string_phone, text=False):
        if not text:
            return {
                "res_id": res_id,
                "state": "server_error",
                "credit": 0,
            }
        token = self.env["ir.config_parameter"].sudo().get_param("token_for_turbosms")
        if not token:
            return {
                "res_id": res_id,
                "state": "server_error",
                "credit": 0,
            }

        string_phone = string_phone.strip()
        url = "https://api.turbosms.ua/message/send.json"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if not text:
            text = "TurboSMS"
        data = {
            "recipients": [
                f"{string_phone}"
            ],
           "sms": {
              "sender": "ACLIMA",
              "text": f"{text}"
           }
        }
        r = requests.post(url, json=data, headers=headers)
        r.close()
        return {
                "res_id": res_id,
                "state": "success",
                "credit": 0,
            }

    def _sendTurboSMS_integration_odoo(self, messages):
        list_of_dict = []
        for item in messages:
            res_id = item["res_id"]
            number = item["number"]
            content = item["content"]
            list_of_dict.append(self._sendTurboSMS_call_odoo(res_id=res_id, string_phone=number, text=content))
        return list_of_dict