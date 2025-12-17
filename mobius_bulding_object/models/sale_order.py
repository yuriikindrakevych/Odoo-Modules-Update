from odoo import fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    building_object = fields.Many2one("building.object", string="Building Object")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_building_id = fields.Many2one("building.object", "Building Object")
    order_building_line_id = fields.Many2one("building.object.line", "Building Object Line")