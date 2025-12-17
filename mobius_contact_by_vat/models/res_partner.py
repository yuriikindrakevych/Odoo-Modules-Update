#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _
import requests
import json
import datetime
from requests.auth import HTTPBasicAuth
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    regon = fields.Char("REGON")
    krs = fields.Char("KRS")
    country_code = fields.Char(related="country_id.code")

    def request_elfasoft(self, vat):
        URL_ELFASOFT = "https://elfasoft.ddns.net/whitelist/hs/vatnumberverification/check"

        postdata = {
            "VATNumber": "{}".format(vat),
        }
        json_data = {}
        try:
            with requests.post(URL_ELFASOFT, json=postdata,
                               auth=HTTPBasicAuth("aklima", "aklim@12345!"), verify=False) as response:
                if not response:
                    raise ValidationError(_("Sorry, nothing was found with the code you provided"))

                if response.status_code == requests.codes.ok:
                    json_data = json.loads(response.text)
            return json_data
        except requests.exceptions.RequestException as e:
            raise ValidationError(_("RequestException,{}".format(e)))

    def request_mf_gov_pl(self, vat):
        date = datetime.date.today().strftime("%Y-%m-%d")
        URL_MFGOVPL = "https://wl-api.mf.gov.pl/api/search/nip/{}?date={}".format(vat, date)
        json_data_result = {}
        try:
            with requests.get(URL_MFGOVPL) as response:
                if not response:
                    raise ValidationError(_("Sorry, nothing was found with the code you provided"))

                if response.status_code == requests.codes.ok:
                    json_data = json.loads(response.text)
                    json_data_result = json_data["result"]["subject"]
                    if not json_data_result:
                        raise ValidationError(_("Sorry, nothing was found with the code you provided"))
            return json_data_result
        except requests.exceptions.RequestException as e:
            raise ValidationError(_("RequestException,{}".format(e)))

    def get_adress_from_dict(self, data):
        if not data or data is None:
            return ""
        return f"{data.get('Street')}, {data.get('HouseNumber')}, {data.get('ApartmentNumber')}"

    def get_vals_from_api(self, vat):
        # отримання частини даних з elfasoft
        json_elfasoft = self.request_elfasoft(vat)
        # отримання частини даних з gov.pl
        json_data = self.request_mf_gov_pl(vat)

        vals = {
            "name": json_elfasoft.get("OfficialName"),
            "vat": vat,
            "krs": json_data.get("krs"),
            "zip": json_elfasoft.get("PostCode"),
            "regon": json_elfasoft.get("Regon"),
            "street": self.get_adress_from_dict(json_elfasoft),
        }

        if json_elfasoft.get("ProvinceCode"):
            domain = [("code", "=", json_elfasoft.get("ProvinceCode")), ("country_id.name", "=", "Poland")]
            state = self.env["res.country.state"].search(domain, limit=1)
            if state:
                vals["state_id"] = state.id
            else:
                vals["state_id"] = None

        if json_elfasoft.get("LocalityDescription"):
            vals["street2"] = json_elfasoft.get("LocalityDescription")
            domain = [("name", "=", json_elfasoft.get("LocalityDescription"))]
            city = self.env["mobius_catalogue_koatuu.settlement"].search(domain, limit=1)
            if city:
                vals["city_ua"] = city.id
            else:
                vals["city_ua"] = None

        return vals

    def button_download_info_by_vat(self):
        if not self.vat:
            raise ValidationError(_("Enter your VAT/Tax ID"))
        #vat = re.sub("[^0-9]", "", self.vat)
        vals = self.get_vals_from_api(self.vat)
        self.write(vals)
