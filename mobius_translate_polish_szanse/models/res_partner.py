# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from lxml import etree


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        # call super to get the original view
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form":
            doc = etree.XML(result["arch"])
            for field in doc.xpath("//field"):
                if field.get("name") == "city_ua":
                    field.set("placeholder", _("City"))
                if field.get("name") == "state_id":
                    field.set("placeholder", _("Stan"))

            # update the view arch with the modified XML
            result["arch"] = etree.tostring(doc)
        return result
