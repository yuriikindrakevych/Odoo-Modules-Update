from odoo import api, fields, models


class StockLocation(models.Model):
    _name = "stock.location"
    _inherit = ["stock.location", "mail.thread", "mail.activity.mixin"]

    location_id = fields.Many2one(
        "stock.location", "Parent Location", index=True, ondelete="cascade", check_company=True, tracking=True,
        help="The parent location that includes this location. Example : The 'Dispatch Zone' is the 'Gate 1' parent location.")

    name = fields.Char("Location Name",  tracking=True, required=True)
