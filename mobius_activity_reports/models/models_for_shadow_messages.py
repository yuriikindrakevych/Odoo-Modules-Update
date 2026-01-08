from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)

        messages_to_create = []
        subtype_document_create = self.env.ref('mobius_activity_reports.mt_document_created')
        activity_type_created = self.env.ref('mobius_activity_reports.activity_type_contact_created')

        for partner in partners:
            if partner.create_date and self.env.user.partner_id:
                messages_to_create.append({
                    'model': self._name,
                    'res_id': partner.id,
                    'date': partner.create_date,
                    'author_id': self.env.user.partner_id.id,
                    'body': "Contact Created",
                    'message_type': 'comment',
                    'mail_activity_type_id': activity_type_created.id,
                    'subtype_id': subtype_document_create.id,
                    'subject': "System Notification: Contact Created",
                    'notified_partner_ids': False,
                    'needaction': False,
                    'reply_to': False,
                })

        if messages_to_create:
            self.env['mail.message'].sudo().create(messages_to_create)

        return partners

class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)

        messages_to_create = []
        subtype_document_create = self.env.ref('mobius_activity_reports.mt_document_created')
        activity_type_created = self.env.ref('mobius_activity_reports.activity_type_lead_created')

        for lead in leads:
            if lead.create_date and self.env.user.partner_id:
                messages_to_create.append({
                    'model': self._name,
                    'res_id': lead.id,
                    'date': lead.create_date,
                    'author_id': self.env.user.partner_id.id,
                    'body': "Lead/Opportunity Created",
                    'message_type': 'comment',
                    'mail_activity_type_id': activity_type_created.id,
                    'subtype_id': subtype_document_create.id,
                    'subject': "System Notification: Lead/Opportunity Created",
                    'notified_partner_ids': False,
                    'needaction': False,
                    'reply_to': False,
                })

        if messages_to_create:
            self.env['mail.message'].sudo().create(messages_to_create)

        return leads


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        result = super().create(vals)

        subtype_document_create = self.env.ref('mobius_activity_reports.mt_document_created')
        activity_type_created = self.env.ref('mobius_activity_reports.activity_type_quotation_created')

        if result.create_date and self.env.user.partner_id:
            self.env['mail.message'].sudo().create({
                    'model': self._name,
                    'res_id': result.id,
                    'date': result.create_date,
                    'author_id': self.env.user.partner_id.id,
                    'body': "Sale Order Created",
                    'message_type': 'comment',
                    'mail_activity_type_id': activity_type_created.id,
                    'subtype_id': subtype_document_create.id,
                    'subject': "System Notification: Sale Order Created",
                    'notified_partner_ids': False,
                    'needaction': False,
                    'reply_to': False,
                })

        return result


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        invoices = super().create(vals_list)

        messages_to_create = []
        subtype_document_create = self.env.ref('mobius_activity_reports.mt_document_created')
        activity_type_created = self.env.ref('mobius_activity_reports.activity_type_invoice_created')

        for invoice in invoices:
            if invoice.create_date and self.env.user.partner_id:
                messages_to_create.append({
                    'model': self._name,
                    'res_id': invoice.id,
                    'date': invoice.create_date,
                    'author_id': self.env.user.partner_id.id,
                    'body': "Invoice Created",
                    'message_type': 'comment',
                    'mail_activity_type_id': activity_type_created.id,
                    'subtype_id': subtype_document_create.id,
                    'subject': "System Notification: Invoice Created",
                    'notified_partner_ids': False,
                    'needaction': False,
                    'reply_to': False,
                })

        if messages_to_create:
            self.env['mail.message'].sudo().create(messages_to_create)

        return invoices
