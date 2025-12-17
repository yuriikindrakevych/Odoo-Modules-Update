from odoo import api, fields, models, exceptions, _
from odoo.addons.base.models import res_partner, res_country
from odoo.exceptions import ValidationError
from requests.auth import HTTPBasicAuth

import datetime
import json
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests


_logger = logging.getLogger(__name__)


class LeadByVatModel(models.TransientModel):
    _name = "lead_by_vat.wizard"
    _description = "Creating of Lead by the VAT code"

    vat_code = fields.Char(string="Enter the VAT code")

    @api.constrains("vat_code")
    def _check_vat_code(self):
        partner = self.env["res.partner"].search([("vat", "=", self.vat_code)])
        if partner:
            raise ValidationError(_("This VAT code already exists in the system. \nContact name: %s \nManager name: %s") % (partner[0].name, partner[0].user_id.name if partner[0].user_id.name else ""))
        if not self.vat_code:
            raise exceptions.ValidationError(_("The VAT code value can't be empty!"))
        if not self.vat_code.isdigit():
            raise exceptions.ValidationError(_("The VAT code value have to be a digit!"))

    def _request_information(self):
        response_dist = {}
        url_for_request = f"https://wl-api.mf.gov.pl/api/search/nip/{self.vat_code}?date={datetime.date.today()}"
        with requests.get(url_for_request) as response:
            if not response:
                raise exceptions.ValidationError(_("Sorry, nothing was found with the code you provided"))

            if response.status_code == requests.codes.ok:
                response_dist = json.loads(response.text)
        return response_dist

    def _request_elfasoft(self):
        URL_ELFASOFT = "https://elfasoft.ddns.net/whitelist/hs/vatnumberverification/check"
        
        postdata = {
            "VATNumber": "{}".format(self.vat_code),
        }
        json_data = {}
        try:
            r = requests.post(URL_ELFASOFT, json=postdata, auth=HTTPBasicAuth("aklima", "aklim@12345!"), verify=False)

            if r.status_code == requests.codes.ok:
                json_data = json.loads(r.text)
            return json_data
        except requests.exceptions.RequestException as e:
            raise ValidationError(_("RequestException,{}".format(e)))

    def get_adress(self, data):
        if not data or data is None:
            return ""
        return f"{data.get('Street')}, {data.get('HouseNumber')}, {data.get('ApartmentNumber')}"

    def button_vat_code(self):
        json_data = self._request_information()
        json_elfasoft = self._request_elfasoft()
        try:
            result = json_data["result"]["subject"]  # result = dict(response.json()["result"]["subject"])

            country_obj = self.env["res.country"]
            partner_obj = self.env["res.partner"]
            lead_obj = self.env["crm.lead"]

            state = self.env["res.country.state"].search([("code", "=", json_elfasoft.get("ProvinceCode")), ("country_id.name", "=", "Poland")], limit=1)
            city = self.env["mobius_catalogue_koatuu.settlement"].search([("name", "=", json_elfasoft.get("LocalityDescription"))], limit=1)
            adress = self.get_adress(json_elfasoft)

            partner = partner_obj.search([("vat", "=", self.vat_code)], limit=1)
            if not partner:
                partner = partner_obj.create({
                    "name": json_elfasoft.get("OfficialName"),
                    "krs": result.get("krs"),
                    "zip": json_elfasoft.get("PostCode"),
                    "state_id": state.id if state else False,
                    "city_ua": city.id if city else False,
                    "street": adress,
                    "regon": json_elfasoft.get("Regon"),
                    "country_id": country_obj.search([("code", "=", "PL")])[0].id,  # default value!
                    "is_company": True,  # default value!
                    "company_type": "company",  # default value!
                    })

            new = partner
            pl_lang_id = self.env["res.lang"].search([("code", "=", "pl_PL")], limit=1)[0].id
            lead = lead_obj.create({
                "name": "LEAD {0}".format(new.name),
                "partner_id": new.id,
                "country_id": new.country_id.id,
                "lang_id": pl_lang_id,
                "vat": self.vat_code,
                "street": new.street,
                "zip": json_elfasoft.get("PostCode"),
                "city": city.id if city else False,
                })
            return {
                "type": "ir.actions.act_window",
                "res_model": "crm.lead",
                "view_mode": "form",
                "view_type": "form",
                "target": "form",
                "res_id": lead.id,
                "context": {},
            }
        except Exception as ex:
            _logger.error("Exception (ContactByVatModel -> requests by VAT): ", ex)
            return {}