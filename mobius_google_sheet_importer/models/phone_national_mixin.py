try:
    import phonenumbers
except ImportError:
    phonenumbers = None

from odoo import models, fields, api
from ..tools import phone_parser


class PhoneNationalMixin(models.AbstractModel):
    """
    Abstract model (mixin) to add fields for searchable national phone numbers.
    Any model inheriting this mixin will get searchable phone/mobile fields,
    assuming it already has 'phone', 'mobile', and 'country_id' fields.
    """
    _name = "mobius.phone.national.mixin"
    _description = 'Mixin for National Significant Phone Number'

    phone_national_significant = fields.Char(
        string="Searchable Phone Number",
        compute="_compute_national_significant_numbers",
        store=True, index=True, readonly=True
    )

    mobile_national_significant = fields.Char(
        string="Searchable Mobile Number",
        compute="_compute_national_significant_numbers",
        store=True, index=True, readonly=True
    )

    @api.depends("phone", "mobile", "country_id")
    def _compute_national_significant_numbers(self):
        """
        Computes the "significant" part of the number (without the country code) for the phone and mobile fields.
        If the number cannot be parsed, it stores the original value instead.
        """
        for record in self:
            record.phone_national_significant = phone_parser.get_national_significant(
                record.phone, country=record.country_id, company=record.company_id
            )

            record.mobile_national_significant = phone_parser.get_national_significant(
                record.mobile, country=record.country_id, company=record.company_id
            )
