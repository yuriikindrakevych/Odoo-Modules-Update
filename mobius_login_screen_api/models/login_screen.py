#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging
import requests
import json

_logger = logging.getLogger(__name__)


class LoginScreenAPI(models.Model):
    _name = "login.screen.api"

    phone = fields.Char()
    code = fields.Char()

    def _login_screen_api(self, phone, code=None):
        CodeGen = self.env["code.generation"]
        user_under_ver = False
        lead = self.env["crm.lead"].with_context({
            "with_contact": False
        }).get_by_phones(phone) if phone else None
        # _logger.info(f"_login_screen_api -> lead={lead}")
        partner_id = self.env["res.partner"].with_context({
            "with_user": True, "has_group": "base.group_portal",
        }).get_by_phones(phone) if phone else None
        # _logger.info(f"_login_screen_api -> partner_id={partner_id}")

        if lead:
            if not self.env["crm.lead"].with_context({
                "with_contact": True
            }).get_by_phones(phone):
                user_under_ver = True

        if not partner_id:
            return {
                "description": "User Under Verification",
            } if user_under_ver else {
                "description": "User Not Found",
            }

        if phone and not code:
            if partner_id:
                code_id = CodeGen.pre_create([{
                    "partner_id": partner_id.id,
                    "phone": phone,
                    }])
                message = "authorization code to Partnership360: " + code_id.code_generation
                sms = self.env["crm.lead"]._sendTurboSMS(string_phone=phone, text=message)
                if not sms:
                    return {
                        "description": "TurboSMS not working",
                    }
                return code_id
        elif phone and code:
            if CodeGen.get_code_suitable(phone, code):
                user_id_from_partner = self.env["res.users"].search([("partner_id", "=", partner_id.id)], limit=1)
                return {
                    "contact_id": partner_id.id,
                    "contact_name": partner_id.name,
                    "contact_company": partner_id.parent_id.name,
                    "contact_company_vat": partner_id.parent_id.vat,
                    "contact_phone": partner_id.phone,
                    "contact_email": partner_id.email,
                    "access_code_to_external_systems": user_id_from_partner.access_code_to_external_systems,
                    "list_of_rights_to_external_files": partner_id.right_services_ids.ids,
                    "login": user_id_from_partner.login,
                    "password": partner_id.techinal_password,
                    "saleperson": {
                        "saleperson_id": partner_id.user_id.id,
                        "saleperson_name": partner_id.user_id.name,
                        "saleperson_phone": partner_id.user_id.phone,
                        "saleperson_email": partner_id.user_id.login,
                    }
                }
            else:
                return {
                    "description": "Invalid Сode",
                }

    def _login_without_login_screen(self, login, password, url, dbname):
        if not url:
            url = "http://localhost:8069/mobius/auth"
        else:
            url = url + "/mobius/auth"
        if not dbname:
            dbname = "mydb1"

        search_user = self.env["res.users"].search([("login", "=", login)], limit=1)
        '''
        if search_user.sel_groups_1_9_10 == 9:
            if not search_user or not search_user.partner_id.techinal_password or search_user.partner_id.techinal_password != password:
                return {
                    "ERROR (Authorization)" : "Login or Password not correct",
                }
        '''
        data = {
            "params":
            {
                "db":       dbname,
                "login":    login,
                "password": password,
            },
        }
        x = requests.post(url, json=data)
        session_id = None
        if x.status_code == 200:
            data = json.loads(x.text)
            if data["result"]:
                session_id = data["result"]
            return {"session_id": session_id}
        else:
            return {
                "ERROR (Status Code)": x.status_code,
            }
