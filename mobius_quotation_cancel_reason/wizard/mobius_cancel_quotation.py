from odoo import fields, models, _


class CancelQuotation(models.TransientModel):
    _name = "cancel.quotation"
    _description = "Cancel Quotation"

    cancel_reason_id = fields.Many2one(comodel_name="crm.lost.reason", string="Cancel Reason", required=True)
    cancellation_comment = fields.Char(string="Cancellation Comment", required=True)

    def create_cancel_reason(self):
        active_sale_order = self.env.context.get('active_id')

        if active_sale_order:
            sale_order = self.env['sale.order'].browse(active_sale_order)
            sale_order.write({
                'cancel_reason_id': self.cancel_reason_id.id,
                'cancellation_comment': self.cancellation_comment,
            })
            sale_order._action_cancel()

        return {'type': 'ir.actions.act_window_close'}
