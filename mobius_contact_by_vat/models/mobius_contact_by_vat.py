from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError
import urllib3
import logging
_logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ContactByVatModel(models.TransientModel):
    _name = "contact_by_vat.wizard"
    _description = "Creating of Contact by the VAT code"

    vat_code = fields.Char(string="Enter the VAT code")

    @api.constrains("vat_code")
    def _check_vat_code(self):
        # перевірка введеного VAT коду
        partner = self.env["res.partner"].search([("vat", "=", self.vat_code)])
        if partner:
            raise ValidationError(_("This VAT code already exists in the system. \n Contact name: %s \n Manager name: %s" % (partner[0].name, partner[0].user_id.name if partner[0].user_id.name else '') ))
        if not self.vat_code:
            raise ValidationError(_("The VAT code value can't be empty!"))
        if not self.vat_code.isdigit():
            raise ValidationError(_("The VAT code value have to be a digit!"))

    def button_vat_code(self):
        contact_obj = self.env["res.partner"]
        vals = contact_obj.get_vals_from_api(self.vat_code)

        # default values
        vals["country_id"] = self.env["res.country"].search([("code", "=", "PL")])[0].id
        vals["is_company"] = True
        vals["company_type"] = "company"

        # створення контакту з отриманими даними
        new = contact_obj.create(vals)

        # перейти на створений контакт
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "res_id": new.id,
            "context": {},
        }
