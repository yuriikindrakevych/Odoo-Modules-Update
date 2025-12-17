#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
from odoo import _
import logging
import json
_logger = logging.getLogger(__name__)

class InvalidPhone(Exception):
    def __str__(self):
        return "1*"

class InvalidEmail(Exception):
    def __str__(self):
        return "2*"

class OnVerification(Exception):
    def __str__(self):
        return "3*"

class RegistrationInVerification(Exception):
    _name = "*4"
    def __str__(self):
        return "4*"

class Lead(models.Model):
    _inherit = "crm.lead"

    certificate_data = fields.Char(string="Certificate data")
    trade_guardian_code = fields.Char(string="Trade code")
    vat = fields.Char(string="Identification Number")
    linkedin = fields.Char(string="LinkedIn")
    linkedin_company = fields.Char(string="LinkedIn Company")

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("create create create")
        _logger.info("vals_list=%s", vals_list)
        ResPartner = self.env["res.partner"]
        context = self.env.context
        _logger.info("context=%s", context)
        need_override_record = False
        for vals in vals_list:
            if context.get("from_API"):
                create_lead = {}
                phone = vals["phone"]

                # if ResPartner.check_exist_record_mobile(phone):
                #     raise InvalidPhone

                email = vals["email_from"]

                # if ResPartner.check_exist_record_email(email):
                #     raise InvalidEmail

                if self.check_exist_record_mobile_crm(phone):
                    need_override_record = True
                    override_record = self.search([("phone", "=", phone)]).id
                    create_lead["override_record"] = override_record
                if self.check_exist_record_email_crm(email):
                    need_override_record = True
                    override_record = self.search([("email_from", "=", email)]).id
                    create_lead["override_record"] = override_record
                name = self.env["ir.sequence"].next_by_code("crm_lead_automatic_name")
                if name:
                    create_lead["name"] = name
                else:
                    create_lead["name"] = "ERROR sequence"
                create_lead["contact_name"] = vals["contact_name"]
                create_lead["partner_name"] = vals["partner_name"]
                if vals.get("vat"):
                    create_lead["vat"] = vals["vat"]
                if vals.get("street"):
                    create_lead["street"] = vals["street"]
                if vals.get("city"):
                    create_lead["city"] = vals["city"]
                if vals.get("zip"):
                    create_lead["zip"] = vals["zip"]
                source_id = self.env["utm.source"].search([("name", "=", "B2B кабінет")])
                if source_id:
                    create_lead["source_id"] = source_id.id
                create_lead["phone"] = vals["phone"]
                create_lead["email_from"] = vals["email_from"]
                create_lead["certificate_data"] = vals["certificate_data"]
                if vals.get("description"):
                    create_lead["description"] = vals["description"]

                if vals.get("trade_guardian_code"):
                    create_lead["trade_guardian_code"] = vals["trade_guardian_code"]
                    user_search = self.env["res.users"].search([("trade_guardian_code", "=", vals["trade_guardian_code"])], limit=1)
                    if user_search:
                        create_lead["user_id"] = user_search.id
                    else:
                        create_lead["user_id"] = False
                else:
                    create_lead["user_id"] = False

                if vals.get("country_code"):
                    country_search = self.env["res.country"].search([("code", "=", vals["country_code"])], limit=1)
                    if country_search:
                        create_lead["country_id"] = country_search.id


                team_search = self.env["crm.team"].search([("id", "=", 6)], limit=1)
                if team_search:
                    create_lead["team_id"] = team_search.id
                create_lead["type"] = "lead"
                list_to_create = []
                list_to_create.append(create_lead)
        if need_override_record:
            _logger.info("need_override_record")
            for need_override in list_to_create:
                override_record = self.browse(need_override["override_record"])
                need_override.pop("override_record")
                override_record.write(need_override)
            raise RegistrationInVerification
        elif context.get("from_API"):
            _logger.info("return super")
            return super(Lead, self).create(list_to_create)
            #raise OnVerification
        return super().create(vals_list)

    def _create_lead_from_api(self, contact_name, partner_name, phone, email_from,
            certificate_data, vat=None, country_code=None,
            description=None, trade_guardian_code=None, street=None, city=None, zip=None):
        ResPartner = self.env["res.partner"]
        context = self.env.context
        _logger.error("contact_name=%s, partner_name=%s, phone=%s, email_from=%s, certificate_data=%s, vat=%s, country_code=%s, description=%s, trade_guardian_code=%s, street=%s, city=%s, zip=%s", contact_name, partner_name, phone, email_from, certificate_data, vat, country_code, description, trade_guardian_code, street, city, zip)
        _logger.error("context=%s", context)
        need_override_record = False
        if True:
            create_lead = {}

            # if ResPartner.check_exist_record_mobile(phone):
            #     return {
            #         "description" : "1*",
            #     }

            email = email_from
            # if ResPartner.check_exist_record_email(email):
            #     return {
            #         "description" : "2*",
            #     }

            if self.check_exist_record_mobile_crm(phone):
                need_override_record = True
                override_record = self.search([("phone", "=", phone)]).id
                create_lead["override_record"] = override_record
            if self.check_exist_record_email_crm(email):
                need_override_record = True
                override_record = self.search([("email_from", "=", email)]).id
                create_lead["override_record"] = override_record

            name = self.env["ir.sequence"].next_by_code("crm_lead_automatic_name")
            if name:
                create_lead["name"] = name
            else:
                create_lead["name"] = "ERROR sequence"
            create_lead["contact_name"] = contact_name
            create_lead["partner_name"] = partner_name
            if vat:
                create_lead["vat"] = vat
            if street:
                create_lead["street"] = street
            if city:
                create_lead["city"] = city
            if zip:
                create_lead["zip"] = zip
            source_id = self.env["utm.source"].search([("name", "=", "B2B кабінет")])
            if source_id:
                create_lead["source_id"] = source_id.id
            create_lead["phone"] = phone
            create_lead["email_from"] = email_from
            create_lead["certificate_data"] = certificate_data
            if description:
                create_lead["description"] = description

            if trade_guardian_code:
                create_lead["trade_guardian_code"] = trade_guardian_code
                user_search = self.env["res.users"].search([("trade_guardian_code", "=", trade_guardian_code)], limit=1)
                if user_search:
                    create_lead["user_id"] = user_search.id
                else:
                    create_lead["user_id"] = False
            else:
                create_lead["user_id"] = False

            if country_code:
                country_search = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                if country_search:
                    create_lead["country_id"] = country_search.id

            team_search = self.env["crm.team"].search([("id", "=", 6)], limit=1)
            if team_search:
                create_lead["team_id"] = team_search.id
            create_lead["type"] = "lead"
            list_to_create = []
        if need_override_record:
            if vat:
                create_lead["vat"] = vat
            else:
                create_lead["vat"] = False

            if country_code:
                country_search = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                if country_search:
                    create_lead["country_id"] = country_search.id
            else:
                create_lead["country_id"] = False

            if description:
                create_lead["description"] = description
            else:
                create_lead["description"] = False

            if trade_guardian_code:
                create_lead["trade_guardian_code"] = trade_guardian_code
                user_search = self.env["res.users"].search([("trade_guardian_code", "=", trade_guardian_code)], limit=1)
                if user_search:
                    create_lead["user_id"] = user_search.id
            else:
                create_lead["trade_guardian_code"] = False

            if street:
                create_lead["street"] = street
            else:
                create_lead["street"] = False

            if city:
                create_lead["city"] = city
            else:
                create_lead["city"] = False

            if zip:
                create_lead["zip"] = zip
            else:
                create_lead["zip"] = False

            list_to_create.append(create_lead)
            for need_override in list_to_create:
                override_record = self.browse(need_override["override_record"])
                need_override.pop("override_record")
                override_record.with_context(raise_exception=False, mail_create_nolog=True, dont_notify=True, tracking_disable=True,
                    mail_notrack=True, mail_create_nosubscribe=True).write(need_override)
                return {
                    "description" : "4*",
                }
        list_to_create.append(create_lead)
        # super(Lead, self.with_context(raise_exception=False, mail_create_nolog=True, dont_notify=True, tracking_disable=True,
        #     mail_notrack=True, mail_create_nosubscribe=True)).create(list_to_create)

        ctx = dict(self.env.context)
        ctx.update({
            "raise_exception": False,
            "mail_create_nolog": True,
            "dont_notify": True,
            "tracking_disable": True,
            "mail_notrack": True,
            "mail_create_nosubscribe": True,
            "from_API": True,
        })
        self = self.with_context(ctx)
        self.create(list_to_create)

        return {
            "description" : "3*",
        }

    def send_email_crm_lead_template(self):
        self.env.ref("mobius_lead_from_api.crm_lead_reg_send_info").send_mail(self.id, force_send=True)

    def window_accept_create_user_contact_company(self):
        view = self.env.ref("mobius_lead_from_api.window_accept_create_user_contact_company_view_form").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Confirm"),
                "res_model": "crm.lead",
                "view_mode": "form",
                "res_id" : self.id,
                "views": [[view, "form"]],
                "target": "new",
        }

    def create_user_contact_company(self):
        partner_id = self._create_customer_for_api()
        self.partner_id = partner_id.id
        user = self._create_user_for_api(partner_id)
        self.send_email_crm_lead_template()
        self.convert_to_award()


    def convert_to_award(self):
        convert = self.env["crm.lead2opportunity.partner"].with_context({
            "active_model": "crm.lead",
            "active_id": self.id,
            "active_ids": self.ids,
        }).create({})
        result_opportunity = convert._action_convert()
        return result_opportunity.redirect_lead_opportunity_view()

    def _create_customer_for_api(self):
        Partner = self.env["res.partner"]
        contact_name = self.contact_name
        partner_company = False
        if not contact_name:
            contact_name = Partner._parse_partner_name(self.email_from)[0] if self.email_from else False

        if self.vat:
            search_domain = [
                    '&', ("company_type", "!=", "person"),
                    ("vat", "=", self.vat),
                ]
            search_company_by_vat = self.env["res.partner"].search(search_domain, limit=1)
            if search_company_by_vat:
                partner_company = search_company_by_vat
        if self.partner_name and not partner_company:
            search_domain = [
                    '&', ("company_type", "!=", "person"),
                    ("vat", "=", self.partner_name),
                ]
            search_company_by_name = self.env["res.partner"].search(search_domain, limit=1)
            if search_company_by_name:
                partner_company = search_company_by_name

        if not partner_company:
            if self.partner_name:
                partner_company = Partner.create(self._prepare_customer_values_for_api(self.partner_name, is_company=True,
                    certificate_data=self.certificate_data if self.certificate_data else False,
                    trade_guardian_code=self.trade_guardian_code if self.trade_guardian_code else False,
                    vat=self.vat if self.vat else False))
            elif self.partner_id:
                partner_company = self.partner_id
            else:
                partner_company = None

        if contact_name:
            return Partner.create(self._prepare_customer_values_for_api(contact_name, is_company=False, parent_id=partner_company.id if partner_company else False,
                certificate_data=self.certificate_data if self.certificate_data else False,
                trade_guardian_code=self.trade_guardian_code if self.trade_guardian_code else False,
                vat=self.vat if self.vat else False))

        if partner_company:
            return partner_company
        return Partner.create(self._prepare_customer_values_for_api(self.name, is_company=False, certificate_data=self.certificate_data if self.certificate_data else False,
                trade_guardian_code=self.trade_guardian_code if self.trade_guardian_code else False, vat=self.vat if self.vat else False))

    def _prepare_customer_values_for_api(self, partner_name, is_company=False, parent_id=False, certificate_data=False, trade_guardian_code=False, vat=False):
        email_split = tools.email_split(self.email_from)
        #currency_id = self.env['ir.config_parameter'].sudo().get_param('account.currency_id')
        pln = self.env["res.currency"].search([("name", "=", "PLN")], limit=1)
        pricelist = False
        if pln:
            pricelist = self.env["product.pricelist"].search([("currency_id", "=", pln.id)], limit=1)
            if not pricelist:
                pricelist = False
            else:
                pricelist = pricelist.id
        res = {
            "name": partner_name,
            "user_id": self.env.context.get("default_user_id") or self.user_id.id,
            "comment": self.description,
            "team_id": self.team_id.id,
            "parent_id": parent_id,
            "phone": self.phone,
            "mobile": self.mobile,
            "email": email_split[0] if email_split else False,
            "title": self.title.id,
            "function": self.function,
            "street": self.street,
            "street2": self.street2,
            "zip": self.zip,
            "city": self.city,
            "country_id": self.country_id.id,
            "state_id": self.state_id.id,
            "website": self.website,
            "linkedin": self.linkedin,
            "linkedin_company": self.linkedin_company,
            "is_company": is_company,
            "type": "contact",
            "certificate_data" : certificate_data,
            "trade_guardian_code" : trade_guardian_code,
            "vat" : vat,
            "property_product_pricelist": pricelist,
        }
        if self.lang_id:
            res['lang'] = self.lang_id.code
        return res


    def _create_user_for_api(self, partner_id):
        code_ok = True
        new_code = None
        while code_ok:
            new_code = self.env["code.generation"]._create_code()
            search_code = self.env["res.users"].search([("access_code_to_external_systems", "=", new_code)])
            if search_code:
                continue
            else:
                break
        techinal_password = self.env["code.generation"]._create_random_string_upper_and_lower()
        partner_id.write({
            "techinal_password": techinal_password,
            })
        #currency_id = self.env['ir.config_parameter'].sudo().get_param('account.currency_id')
        pln = self.env["res.currency"].search([("name", "=", "PLN")], limit=1)
        pricelist = False
        if pln:
            pricelist = self.env["product.pricelist"].search([("currency_id", "=", pln.id)], limit=1)
            if not pricelist:
                pricelist = False
            else:
                pricelist = pricelist.id

        user = self.env["res.users"].sudo().with_context(no_reset_password=True).create({
            "name": partner_id.name,
            "login": partner_id.email,
            "partner_id": partner_id.id,
            "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            #"sel_groups_1_9_10": "9",
            "access_code_to_external_systems" : new_code,
            "property_product_pricelist": pricelist,
        })
        user.sudo().write({
            "password": techinal_password,
            })
        return user


    def check_exist_record_mobile_crm(self, phone):
        search_record = self.search_count([("phone", "=", phone)])
        if search_record > 0:
            return True
        return False

    def check_exist_record_email_crm(self, email_from):
        search_record = self.search_count([("email_from", "=", email_from)])
        if search_record > 0:
            return True
        return False


    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super()._prepare_customer_values(partner_name=partner_name, is_company=is_company, parent_id=parent_id)
        pln = self.env["res.currency"].search([("name", "=", "PLN")], limit=1)
        pricelist = False
        if pln:
            pricelist = self.env["product.pricelist"].search([("currency_id", "=", pln.id)], limit=1)
            if not pricelist:
                pricelist = False
            else:
                pricelist = pricelist.id
        res["certificate_data"] = self.certificate_data
        res["trade_guardian_code"] = self.trade_guardian_code
        res["vat"] = self.vat
        res["property_product_pricelist"] = pricelist
        res["linkedin"] = self.linkedin
        res["linkedin_company"] = self.linkedin_company
        return res
