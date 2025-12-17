from odoo import fields, models, tools, api


class ResPartnerActivityReport(models.Model):
    _name = "res.partner.activity.report"
    _auto = False
    _description = "Contacts Activity Analysis"
    _rec_name = "id"

    date = fields.Datetime("Completion Date", readonly=True)
    subtype_id = fields.Many2one("mail.message.subtype", "Subtype", readonly=True)
    mail_activity_type_id = fields.Many2one("mail.activity.type", "Activity Type", readonly=True)
    author_id = fields.Many2one("res.partner", "Assigned To", readonly=True)
    body = fields.Html("Activity Description", readonly=True)

    partner_id = fields.Many2one("res.partner", "Customer", readonly=True)

    def _select(self):
        return """
            SELECT
                m.id,
                m.subtype_id,
                m.mail_activity_type_id,
                m.author_id,
                m.date,
                m.body,
                l.id as partner_id
        """

    def _from(self):
        return """
            FROM mail_message AS m
        """

    def _join(self):
        return """
            JOIN res_partner AS l ON m.res_id = l.id
        """

    def _where(self):
        disccusion_subtype = self.env.ref("mail.mt_comment")
        return """
            WHERE
                m.model = 'res.partner' AND (m.mail_activity_type_id IS NOT NULL OR m.subtype_id = %s)
        """ % (disccusion_subtype.id,)

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
