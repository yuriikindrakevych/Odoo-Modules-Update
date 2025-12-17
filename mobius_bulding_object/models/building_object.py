#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from datetime import datetime
import time

import inspect
import traceback
# Subset of partner fields: sync all or none to avoid mixed addresses
PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]

class Attachment(models.Model):
    _inherit = 'ir.attachment'

    attach_rel = fields.Many2many('building.object', 'attachment', 'attachment_id', 'document_id', string="Attachment")


class BuildingObject(models.Model):
    _name = "building.object"

    @api.model
    def _default_country_id(self):
        country = self.env["res.country"].search([("code", "=", "PL")])
        if country:
            return country
        return False

    name = fields.Char(string="Name Object")

    state = fields.Selection([
        ('new', 'New'),
        ('executed', 'Executed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=False, store=True, copy=False, index=True, default='new', compute="_compute_state", inverse="_set_state")

    date = fields.Date(readonly=False, copy=False,
                       default=lambda self: fields.Date.today())
    seq_number = fields.Char(readonly=False, string="No.")

    crm_lead_id = fields.Many2one('crm.lead', 'Opportunity', domain="[('type', '=', 'opportunity')]",
        index=True, ondelete='set null', store=True)
    crm_lead_id_show = fields.Integer("Technical", compute="_compute_crm_lead_id_show")

    building_object_line = fields.One2many('building.object.line', 'building_object_id', string='Building Lines',  copy=True, auto_join=True)

    order_line_building = fields.One2many('sale.order.line', 'order_building_id', string='Order Lines', copy=True, auto_join=True)

    sale_order_ids = fields.One2many('sale.order', 'building_object', string='Sale Order', copy=True, auto_join=True)

    company_id = fields.Many2one(
        'res.company', string='Company', index=True,
        compute='_compute_company_id', readonly=False, store=True)

    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True,
        compute="_compute_partner_id", inverse="_set_partner_id", store=True)
    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Pricelist', related="partner_id.property_product_pricelist")

    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user,
        compute="_compute_user_id", inverse="_set_user_id",
        domain=lambda self: "[('groups_id', '=', {}), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ), check_company=True, store=True)

    team_id = fields.Many2one(
        'crm.team', string='Sales Team', check_company=True, compute="_compute_team_id", inverse="_set_team_id", store=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", ondelete="set null", readonly=False)

    analytical_account = fields.Char("Analytical Account")

    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', inverse="_set_address", readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', inverse="_set_address", readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', inverse="_set_address", readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', inverse="_set_address", readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_address_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_address_values', default=_default_country_id, readonly=False, store=True)

    show_button_cancel = fields.Boolean(compute="_compute_button_cancel")

    sale_order_count = fields.Integer("Sale Order count", compute="_compute_sale_order_count")
    crm_lead_count = fields.Integer("Sale Order count", compute="_compute_crm_lead_count")

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")

    start_date_time = fields.Datetime("Start Date", compute="_compute_start_date_time")
    end_date_time = fields.Datetime("End Date", compute="_compute_end_date_time")

    total_power = fields.Float("Total power")
    investor_id = fields.Many2one("res.partner", string="Investor")
    designer_id = fields.Many2one("res.partner", string="Designer")
    general_executor_id = fields.Many2one("res.partner", string="General Executor")
    installer_id = fields.Many2one("res.partner", string="Installer")

    attachment = fields.Many2many("ir.attachment", "attach_rel", "doc_id", "attach_id", string="Attachment",
                                  help="You can upload your document", copy=False)

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    _sql_constraints = [
        ('seq_number_unique',
         'unique(seq_number)',
         'The value of sequence number (No.) must be unique!')
    ]

    def _compute_start_date_time(self):
        mytime = datetime.strptime('0000','%H%M').time()
        for obj in self:
            if obj.start_date:
                obj.start_date_time = datetime.combine(obj.start_date, mytime)
            else:
                obj.start_date_time = False

    def _compute_end_date_time(self):
        mytime = datetime.strptime('0000','%H%M').time()
        for obj in self:
            if obj.end_date:
                obj.end_date_time = datetime.combine(obj.end_date, mytime)
            else:
                obj.end_date_time = False


    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'building.object'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense._origin.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'building.object'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'building.object', 'default_res_id': self.id}
        return res

    def _compute_sale_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)

    def _compute_crm_lead_count(self):
        for rec in self:
            crm_lead_ids = self.env['crm.lead'].search([("building_object_id", "=", rec.id)])
            rec.crm_lead_count = len(crm_lead_ids)

    def open_sale_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id("mobius_bulding_object.act_building_object")
        action["domain"] = [("id", "in", self.sale_order_ids.ids)]
        return action

    def open_crm_lead(self):
        action = self.env['ir.actions.act_window']._for_xml_id("mobius_bulding_object.crm_lead_building_object")
        crm_lead_ids = self.env['crm.lead'].search([("building_object_id", "=", self.id)])
        action["domain"] = [("id", "in", crm_lead_ids.ids)]
        return action

    def method_traceback(self):
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        _logger.error(''.join(stack_trace))

    @api.depends("building_object_line.reserved", "building_object_line.demand")
    def _compute_state(self):
        for rec in self:
            state_was_changed = False
            if len(rec.building_object_line.mapped("id")) > 0:
                a = sum(rec.building_object_line.mapped("demand"))
                b = sum(rec.building_object_line.mapped("reserved"))
                if a == b and a != 0:
                    rec.state = "done"
                    state_was_changed = True
                if sum(rec.building_object_line.mapped("reserved")) > 0 and not state_was_changed:
                    rec.state = "executed"
                    state_was_changed = True
            if rec.state == "сancel" and not state_was_changed:
                rec.state = rec.state
                state_was_changed = True
            if not state_was_changed:
                rec.state = "new"

    def _set_state(self):
        pass

    def _compute_button_cancel(self):
        for rec in self:
            if len(rec.building_object_line.mapped("id")) > 0:
                # _logger.debug("len(rec.building_object_line.mapped('id'))=%s", len(rec.building_object_line.mapped("id")))
                rec.show_button_cancel = True
            else:
                # _logger.debug("len(rec.building_object_line.mapped('id'))=%s", len(rec.building_object_line.mapped("id")))
                rec.show_button_cancel = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("seq_number"):
                vals["seq_number"] = self._generate_next_seq_number()
            if vals.get('partner_id'):
                partner_id = self.env["res.partner"].browse(vals.get('partner_id'))
                vals["property_product_pricelist"] = partner_id.property_product_pricelist
                vals["show_button_cancel"] = False
        return super().create(vals_list)

    def copy(self, default = {}):
        default["seq_number"] = self._generate_next_seq_number()
        rtn = super(BuildingObject, self).copy(default=default)
        return rtn

    @api.model
    def _generate_next_seq_number(self):
        return str(datetime.today().year) + self.env["ir.sequence"].next_by_code("building.object")

    def create_offer(self):
        view = self.env.ref("mobius_bulding_object.view_building_object_form_confirm_order").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Confirm Order"),
                "res_model": "building.object",
                "view_mode": "form",
                "res_id" : self.id,
                "views": [[view, "form"]],
                "target": "new",
        }

    def button_cancel(self):
        self.write({
            "state": "cancel",
            })

    def button_renew(self):
        self.write({
            "state": "new",
            })

    def create_analytic_account(self):
        account = self.env["account.analytic.account"].create({
            "name": self.name,
            })
        return account

    def confirm_offer(self):
        account = self.create_analytic_account()
        sale_order = self.env['sale.order'].create({
            "user_id": self.user_id.id,
            "partner_id": self.partner_id.id,
            "team_id": self.team_id.id,
            "analytic_account_id": account.id,
            "building_object": self.id,
            "pricelist_id": self.property_product_pricelist.id,
        })
        for rec in self.building_object_line:
            if rec.order == 0:
                continue
            order_line = self.env["sale.order.line"].create({
                "product_id": rec.product_id.id,
                "order_id": sale_order.id,
                "order_building_id": self.id,
                "order_building_line_id": rec.id,
                "product_uom_qty": rec.order,
                "price_unit": rec.price_unit,
                })
            rec.order = 0
        view = self.env.ref("sale.view_order_form").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Sale Order"),
                "res_model": "sale.order",
                "view_mode": "form",
                "res_id" : sale_order.id,
                "views": [[view, "form"]],
                "target": "form",
        }
    def fill_all_confirm_offer(self):
        for rec in self.building_object_line:
            if rec.full_reserved:
                continue
            num = rec.demand - rec.reserved
            rec.write({
                "order": num,
                })
        view = self.env.ref("mobius_bulding_object.view_building_object_form_confirm_order").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Confirm Order"),
                "res_model": "building.object",
                "view_mode": "form",
                "res_id" : self.id,
                "views": [[view, "form"]],
                "target": "new",
        }

    def clear_all_confirm_offer(self):
        for rec in self.building_object_line:
            if rec.full_reserved:
                continue
            rec.write({
                "order": 0,
                })
        view = self.env.ref("mobius_bulding_object.view_building_object_form_confirm_order").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Confirm Order"),
                "res_model": "building.object",
                "view_mode": "form",
                "res_id" : self.id,
                "views": [[view, "form"]],
                "target": "new",
        }
    #
    # def write(self, vals):
    #     #self.method_traceback()
    #     # _logger.error("self=%s, vals=%s", self, vals)
    #     return super().write(vals)


    @api.depends('crm_lead_id')
    def _compute_crm_lead_id_show(self):
        for building in self:
            building.crm_lead_id_show = building.crm_lead_id.id

    @api.depends('name')
    def _compute_analytical_account(self):
        for building in self:
            building.analytical_account = "{0} - {1}".format(building.id, building.name)

    def _set_address(self):
        pass

    @api.depends('partner_id')
    def _compute_partner_address_values(self):
        """ Sync all or none of address fields """
        for building in self:
            building.update(building._prepare_address_values_from_partner(building.partner_id))

    def _prepare_address_values_from_partner(self, partner):
        # Sync all address fields from partner, or none, to avoid mixing them.
        if any(partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values

    @api.depends("crm_lead_id.team_id")
    def _compute_team_id(self):
        for building in self:
            building.team_id = building.crm_lead_id.team_id.id

    def _set_team_id(self):
        pass

    @api.depends("crm_lead_id.partner_id")
    def _compute_partner_id(self):
        for building in self:
            building.partner_id = building.crm_lead_id.partner_id.id

    def _set_partner_id(self):
        pass

    @api.depends("crm_lead_id.user_id")
    def _compute_user_id(self):
        for building in self:
            building.user_id = building.crm_lead_id.user_id.id

    def _set_user_id(self):
        pass



    @api.depends('user_id', 'team_id', 'partner_id')
    def _compute_company_id(self):
        """ Compute company_id coherency. """
        for lead in self:
            proposal = lead.company_id

            # invalidate wrong configuration
            if proposal:
                # company not in responsible companies
                if lead.user_id and proposal not in lead.user_id.company_ids:
                    proposal = False
                # inconsistent
                if lead.team_id.company_id and proposal != lead.team_id.company_id:
                    proposal = False
                # void company on team and no assignee
                if lead.team_id and not lead.team_id.company_id and not lead.user_id:
                    proposal = False
                # no user and no team -> void company and let assignment do its job
                # unless customer has a company
                if not lead.team_id and not lead.user_id and \
                   (not lead.partner_id or lead.partner_id.company_id != proposal):
                    proposal = False

            # propose a new company based on team > user (respecting context) > partner
            if not proposal:
                if lead.team_id.company_id:
                    proposal = lead.team_id.company_id
                elif lead.user_id:
                    if self.env.company in lead.user_id.company_ids:
                        proposal = self.env.company
                    else:
                        proposal = lead.user_id.company_id & self.env.companies
                elif lead.partner_id:
                    proposal = lead.partner_id.company_id
                else:
                    proposal = False

            # set a new company
            if lead.company_id != proposal:
                lead.company_id = proposal

    def action_show_crm_lead(self):
        # _logger.debug("crm_lead_id=%s", self.crm_lead_id.id)
        view = self.env.ref("crm.crm_lead_view_form").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Lead"),
                "res_model": "crm.lead",
                "view_mode": "form",
                "res_id" : self.crm_lead_id.id,
                "views": [[view, "form"]],
                "target": "form",
        }