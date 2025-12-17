from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.state == "done" \
                and picking.picking_type_id.sequence_code.startswith("OUT") \
                    and picking.sale_id:
                picking.sale_id.commitment_date = picking.date_done

        return res