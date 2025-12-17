from odoo import fields, models, tools, api


class GeneralActivityReport(models.Model):
    _name = "general.activity.report"
    _auto = False
    _description = "General Activity Analysis"
    _rec_name = "id"

    date = fields.Datetime("Completion Date", readonly=True)
    subtype_id = fields.Many2one("mail.message.subtype", "Subtype", readonly=True)
    mail_activity_type_id = fields.Many2one("mail.activity.type", "Activity Type", readonly=True)
    author_id = fields.Many2one("res.partner", "Assigned To", readonly=True)
    body = fields.Html("Activity Description", readonly=True)

    sale_order_id = fields.Many2one("sale.order", "Sale Order", readonly=True)
    partner_id = fields.Many2one("res.partner", "Customer", readonly=True)
    purchase_order_id = fields.Many2one("purchase.order", "Purchase Order", readonly=True)
    lead_id = fields.Many2one("crm.lead", "Opportunity", readonly=True)

    def _select(self):
        return """
            SELECT
                m.id,
                m.subtype_id,
                m.mail_activity_type_id,
                m.author_id,
                m.date,
                m.body,
                CASE WHEN m.model = 'sale.order' THEN m.res_id ELSE NULL END as sale_order_id,
                CASE WHEN m.model = 'res.partner' THEN m.res_id ELSE NULL END as partner_id,
                CASE WHEN m.model = 'purchase.order' THEN m.res_id ELSE NULL END as purchase_order_id,
                CASE WHEN m.model = 'crm.lead' THEN m.res_id ELSE NULL END as lead_id
        """

    def _from(self):
        return """
            FROM mail_message AS m
        """

    def _join(self):
        return """"""

    def _where(self):
        disccusion_subtype = self.env.ref("mail.mt_comment")
        # subtype_created_id = self.env.ref('mobius_activity_reports.mt_document_created').id
        return """
            WHERE
                (m.model = 'sale.order' AND (m.mail_activity_type_id IS NOT NULL OR m.subtype_id = {subtype}))
                OR
                (m.model = 'res.partner' AND (m.mail_activity_type_id IS NOT NULL OR m.subtype_id = {subtype}))
                OR
                (m.model = 'purchase.order' AND (m.mail_activity_type_id IS NOT NULL OR m.subtype_id = {subtype}))
                OR
                (m.model = 'crm.lead' AND (m.mail_activity_type_id IS NOT NULL OR m.subtype_id = {subtype}))
                OR m.subtype_id IN (SELECT res_id FROM ir_model_data WHERE module = 'mobius_activity_reports' AND name = 'mt_document_created')
        """.format(subtype=disccusion_subtype.id) # , subtype_created_id=subtype_created_id

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where())
        )
