from odoo import fields, models, tools, api


class ActivityReport(models.Model):
    _inherit = "crm.activity.report"

    def _select(self):
        return """
            SELECT
                m.id,
                l.create_date AS lead_create_date,
                l.date_conversion,
                l.date_deadline,
                l.date_closed,
                m.subtype_id,
                m.mail_activity_type_id,
                m.author_id,
                m.date,
                m.body,
                m.customer_id,
                l.id as lead_id,
                l.user_id,
                l.team_id,
                l.country_id,
                l.company_id,
                l.stage_id,
                l.partner_id,
                l.type as lead_type,
                l.active
        """