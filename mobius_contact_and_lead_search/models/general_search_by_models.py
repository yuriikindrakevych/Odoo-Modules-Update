from odoo import models, fields, api, _
from odoo.exceptions import UserError


class GeneralSearchByModels(models.Model):
    _name = "general.search.by.models"
    _description = "General search by models"

    name = fields.Char(
        compute="_compute_name",
        store=True, )
    phone = fields.Char()
    phone_for_search = fields.Char(
        compute="_compute_phone_for_search",
        store=True, )
    vat = fields.Char(
        string="VAT", )
    email = fields.Char()
    title = fields.Char()

    contact_ids = fields.Many2many(
        comodel_name="res.partner", )
    opportunity_ids = fields.Many2many(
        comodel_name="crm.lead",
        relation="general_search_model_opportunity_rel", )
    lead_ids = fields.Many2many(
        comodel_name="crm.lead",
        relation="general_search_model_lead_rel", )
    contact_count = fields.Integer(
        compute="_compute_contact_count", )
    opportunity_count = fields.Integer(
        compute="_compute_opportunity_count", )
    lead_count = fields.Integer(
        compute="_compute_lead_count", )

    @api.depends("create_date", "create_uid")
    def _compute_name(self):
        for obj in self:
            if obj.create_date and obj.create_uid:
                obj.name = _("{} at {}").format(
                    obj.create_uid.name,
                    obj.create_date.strftime("%d.%m.%Y %H:%M:%S"))
            else:
                obj.name = _("Search #")

    @api.depends("phone")
    def _compute_phone_for_search(self):
        for obj in self:
            if obj.phone:
                phone_for_search = obj.phone
                for symbols in ["+", "(", ")", "-", " "]:
                    phone_for_search = phone_for_search.replace(symbols, "")
                obj.phone_for_search = phone_for_search
            else:
                obj.phone_for_search = False

    @api.depends("contact_ids")
    def _compute_contact_count(self):
        for obj in self:
            obj.contact_count = len(obj.contact_ids)

    @api.depends("lead_ids")
    def _compute_lead_count(self):
        for obj in self:
            obj.lead_count = len(obj.lead_ids)

    @api.depends("opportunity_ids")
    def _compute_opportunity_count(self):
        for obj in self:
            obj.opportunity_count = len(obj.opportunity_ids)

    def action_view_contacts(self):
        self.ensure_one()
        
        # Use standard Odoo action for partners
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_partner_form')
        action['domain'] = [('id', 'in', self.contact_ids.ids)]
        action['context'] = dict(self.env.context)
        
        if self.contact_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.contact_ids.ids[0]
        
        return action

    def action_view_opportunities(self):
        self.ensure_one()
        
        # Use standard Odoo action for opportunities
        try:
            action = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_opportunities')
        except:
            action = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_action_pipeline')
        
        action['domain'] = [('id', 'in', self.opportunity_ids.ids), ('type', '=', 'opportunity')]
        action['context'] = dict(self.env.context, default_type='opportunity')
        
        if self.opportunity_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.opportunity_ids.ids[0]
        
        return action

    def action_view_leads(self):
        self.ensure_one()
        
        # Use standard Odoo action for leads
        try:
            action = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_all_leads')
        except:
            action = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_action_pipeline')
        
        action['domain'] = [('id', 'in', self.lead_ids.ids), ('type', '=', 'lead')]
        action['context'] = dict(self.env.context, default_type='lead')
        
        if self.lead_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.lead_ids.ids[0]
        
        return action

    def action_general_search(self):
        self._check_parameters_for_search()
        self._general_search_for_contact()
        self._general_search_for_opportunity()
        self._general_search_for_lead()

        if not self.contact_ids and not self.opportunity_ids and not self.lead_ids:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "warning",
                    "title": _("Search completed"),
                    "message": _("No contacts, opportunities or leads were found for such parameters."),
                    "next": {
                        "type": "ir.actions.act_window_close"
                    },
                }
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "title": _("Search completed"),
                    "message":
                        _("Found {} contacts, {} opportunities and {} leads for the specified parameters.").format(
                            self.contact_count, self.opportunity_count, self.lead_count),
                    "next": {
                        "type": "ir.actions.act_window_close"
                    },
                }
            }

    def _check_parameters_for_search(self):
        if not self.phone and not self.vat and not self.email and not self.title:
            raise UserError(_("All parameters for search is empty. Please fill in at least one parameter."))

    def _general_search_for_contact(self):
        domain = []
        if self.phone:
            domain.append(("phone_for_search", "like", self.phone_for_search))
        if self.vat:
            domain.append(("vat", "like", self.vat))
        if self.email:
            domain.append(("email", "like", self.email))
        if self.title:
            domain.append(("name", "like", self.title))
        contact_ids = self.env["res.partner"].search(domain)

        if contact_ids:
            self.contact_ids = contact_ids
        else:
            self.contact_ids = False

    def _general_search_for_opportunity(self):
        domain = [("type", "=", "opportunity")]
        if self.phone:
            domain.append(("phone_for_search", "like", self.phone_for_search))
        if self.vat:
            domain.append(("vat", "like", self.vat))
        if self.email:
            domain.append(("email_from", "like", self.email))
        if self.title:
            domain.append(("name", "like", self.title))
        opportunity_ids = self.env["crm.lead"].search(domain)

        if opportunity_ids:
            self.opportunity_ids = opportunity_ids
        else:
            self.opportunity_ids = False

    def _general_search_for_lead(self):
        domain = [("type", "=", "lead")]
        if self.phone:
            domain.append(("phone_for_search", "like", self.phone_for_search))
        if self.vat:
            domain.append(("vat", "like", self.vat))
        if self.email:
            domain.append(("email_from", "like", self.email))
        if self.title:
            domain.append(("name", "like", self.title))
        lead_ids = self.env["crm.lead"].search(domain)

        if lead_ids:
            self.lead_ids = lead_ids
        else:
            self.lead_ids = False