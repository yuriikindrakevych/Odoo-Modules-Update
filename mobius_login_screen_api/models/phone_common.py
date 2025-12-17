# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)
try:
    import phonenumbers
except ImportError:
    _logger.error("Cannot import phonenumbers.")

delete_simbols = " +-_.(){}*:/"


class PhoneCommon(models.AbstractModel):
    _name = "phone.common"
    _description = "Common methods for phone features"

    @api.model
    def number_without_simbols(self, phone_number):
        return phone_number.translate(str.maketrans("", "", delete_simbols))

    @api.model
    def number_with_country_code(self, phone_number):
        exists_plus = (phone_number[0] == "+") or False
        phone_number = self.number_without_simbols(phone_number)
        code = phone_number[:-9]
        number = phone_number[-9:]
        country = None
        if len(code) > 0 and exists_plus:
            country = self.env.company.country_id.search([("phone_code", "=", code)], limit=1)
        else:
            country = self.env.company.country_id

        if country:
            phone_number = "+" + str(country.phone_code) + number
        return phone_number

    @api.model
    def compare_phone_numbers(self, phone1, phone2):
        if not phone1 or not phone2:
            return False
        if phone1 == phone2:
            return True
        # check phone numbers without simbols
        if self.number_without_simbols(phone1) == self.number_without_simbols(phone2):
            return True
        # check phone numbers with country code
        # if self.number_with_country_code(phone1) == self.number_with_country_code(phone2):
        #     return True

        return False
