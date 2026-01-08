#!/usr/bin/python3
# -*- coding: utf-8 -*-

import binascii


from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
from odoo.fields import Command
from odoo.http import request
from collections import OrderedDict
from odoo.tools import float_compare, float_is_zero, single_email_re
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers import main
from odoo.addons.website_sale.controllers.main import WebsiteSale


def _message_post_helper(res_model, res_id, message, attachments=None, **kwargs):
    """Compatibility helper for Odoo 18 - replaces removed _message_post_helper"""
    record = request.env[res_model].browse(res_id).sudo()
    attachment_ids = []
    if attachments:
        for name, content in attachments:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': name,
                'datas': base64.b64encode(content),
                'res_model': res_model,
                'res_id': res_id,
            })
            attachment_ids.append(attachment.id)
    return record.message_post(body=message, attachment_ids=attachment_ids)
from datetime import datetime
from odoo.tests import Form
import base64


import logging
_logger = logging.getLogger(__name__)


class Hospital(http.Controller):

    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name"]

    _items_per_page = 80

    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id

        return {
            'sales_user': sales_user,
            'page_name': 'home',
        }


    def details_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        partner = request.env.user.partner_id
        if data.get("vat") and partner and partner.vat != data.get("vat"):
            if partner.can_edit_vat():
                if hasattr(partner, "check_vat"):
                    if data.get("country_id"):
                        data["vat"] = request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")), data.get("vat"))
                    partner_dummy = partner.new({
                        'vat': data['vat'],
                        'country_id': (int(data['country_id'])
                                       if data.get('country_id') else False),
                    })
                    try:
                        partner_dummy.check_vat()
                    except ValidationError:
                        error["vat"] = 'error'
            else:
                error_message.append(_('Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data if k not in self.MANDATORY_BILLING_FIELDS + self.OPTIONAL_BILLING_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message


    @http.route("/create_building_object_webform", type="http", auth="user", website=True)
    def patient_webform(self, redirect=None, **kw):
        _logger.error("kw=%s", kw)
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': [],
        })
        partner = request.env.user.partner_id
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        
        if kw and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(kw)
            values.update({'error': error, 'error_message': error_message})
            values.update(kw)
            if not error:
                values = {key: kw[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: kw[key] for key in self.OPTIONAL_BILLING_FIELDS if key in kw})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
        })
        _logger.error("values=%s", values)
        response = request.render("mobius_portal_aklima.create_building_object_form", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
        #return request.render("mobius_portal_aklima.create_building_object_form", values)


    @http.route("/create/webbuildingobject", type="http", auth="user", website=True)
    def create_webpatient(self, **kw):
        _logger.error("kw=%s", kw)
        date_start = None
        date_end = None
        if kw.get("my_datetimepicker"):
            parts = str(kw.get("my_datetimepicker")).rsplit(' ', 2)
            date_start = datetime.strptime(parts[0], '%m/%d/%Y').date()
        if kw.get("my_datetimepickertwo"):
            parts_two = str(kw.get("my_datetimepickertwo")).rsplit(' ', 2)
            date_end = datetime.strptime(parts_two[0], '%m/%d/%Y').date()
        _logger.error("request.env.context.get('uid')=%s", request.env.context.get("uid"))
        _logger.error("env.user.partner_id=%s", request.env.user.partner_id)

        building_object = request.env["building.object"].sudo().create({
            "name": kw.get("name_buil_object"),
            "country_id": kw.get("country_id"),
            "state_id": kw.get("state_id"),
            "city": kw.get("name_city"),
            "street": kw.get("name_street"),
            "zip": kw.get("name_zip"),
            "total_power": kw.get("name_total_power"),
            "partner_id": request.env.user.partner_id.id,
            "start_date": date_start if date_start else False,
            "end_date": date_end if date_end else False,
            })
        # ATTACH FILE
        files = request.httprequest.files.getlist("attachment")
        _logger.error("files=%s", files)
        for file in files:
            file_content = file.read()
            if file_content:
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': file.filename,
                    'datas': base64.b64encode(file_content),
                    'res_model': 'building.object',
                    'res_id': building_object.id,
                    'type': 'binary',
                })
        return request.redirect("/my/building_objects")


class WebsiteSale(main.WebsiteSale):


    @http.route(["/shop/checkout"], type="http", auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        _logger.info("777=%s", post.get("building_object_id"))
        _logger.error("kw=%s", post)
        if order:
            if post.get("building_object_id") and post.get("building_object_id") != False:
                order.sudo().write({
                        "building_object": post.get("building_object_id"),
                    })
        res = super().checkout(**post)
        return res

    @http.route(["/shop/create_quotation"], type="http", auth="public", website=True, sitemap=False)
    def create_quotation(self, **post):
        print(http.request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('web.base.url')) # BASE URL
        base_url = http.request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('web.base.url') + '/my/home'
        print(http.request.httprequest)

        print(http.request.httprequest.full_path)
        #return
        print(base_url)
        # return {
        #     'type': 'ir.actions.act_url',
        #     'target': 'new',
        #     'url': base_url,
        # }
        order = request.website.sale_get_order()
        if order:
            _logger.error("order.name=%s", order.name)
            order.sudo().write({
                    "building_object": post.get("building_object_id") if post.get("building_object_id") else False,
                    "website_id": 1,
                    "reference": order.name,
                })
            order.action_quotation_sent()
            delivery = request.env["delivery.carrier"].sudo().with_context(lang='en_US').search([("base_delivery", "=", True)], limit=1)
            _logger.info("DELIVERY 8888=%s", delivery)
            if not delivery:
                product = request.env['product.product'].sudo().create({
                    'name': 'Normal Delivery Charges',
                    'type': 'service',
                    'list_price': 0.0,
                    'categ_id': request.env.ref('delivery.product_category_deliveries').id,
                })
                normal_delivery = request.env['delivery.carrier'].sudo().create({
                    'name': 'Normal Delivery Charges',
                    'fixed_price': 0,
                    'delivery_type': 'fixed',
                    'product_id': product.id,
                    "base_delivery": True,
                })
                delivery = request.env["delivery.carrier"].sudo().with_context(lang='en_US').search([("base_delivery", "=", True)], limit=1)
            
            delivery_wizard = Form(request.env['choose.delivery.carrier'].sudo().with_context({
                'default_order_id': order.id,
                'default_carrier_id': delivery.id,
            }))
            choose_delivery_carrier = delivery_wizard.save()
            choose_delivery_carrier.button_confirm()

        request.render("website_sale.header_cart_link", {})
        #request.website.sale_get_order()
        #values = self._prepare_portal_layout_values()
        print(base_url)
        # return {
        #     'type': 'ir.actions.act_url',
        #     'target': 'new',
        #     'url': base_url,
        # }
        return request.redirect('/my/quotes')

    @http.route(["/"], type="http", auth="public", website=True, sitemap=False)
    def redirect(self):
        return request.redirect("/my/home")

    @http.route(["/uk"], type="http", auth="public", website=True, sitemap=False)
    def redirect_from_uk(self):
        return request.redirect("/")

    @http.route(["/shop/cart"], type="http", auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive="", **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        order = request.website.sale_get_order()
        if order and order.state != "draft":
            request.session["sale_order_id"] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env["sale.order"].sudo().search([("access_token", "=", access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != "draft":  # abandoned cart already finished
                values.update({"abandoned_proceed": True})
            elif revive == "squash" or (revive == "merge" and not request.session.get("sale_order_id")):  # restore old cart or merge with unexistant
                request.session["sale_order_id"] = abandoned_order.id
                return request.redirect("/shop/cart")
            elif revive == "merge":
                abandoned_order.order_line.write({"order_id": request.session["sale_order_id"]})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get("sale_order_id"):  # abandoned cart found, user have to choose what to do
                values.update({"access_token": abandoned_order.access_token})

        values.update({
            "website_sale_order": order,
            "date": fields.Date.today(),
            "suggested_products": [],
        })

        partner = request.env.user.partner_id
        BuildingObject = request.env["building.object"].sudo()
        building_objects = BuildingObject.search(self._prepare_building_object_domain(partner))
        values.update({"building_objects": building_objects})
        if order:
            _logger.error("order.check_all_product_available()=%s", order.check_all_product_available_for_buy())
            values.update({"all_product_avaible": order.check_all_product_available_for_buy()})
            values.update({"is_need_seller_agreement": order.is_need_seller_agreement})

        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get("pricelist"):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values["suggested_products"] = _order._cart_accessories()

        if post.get("type") == "popover":
            # force no-cache so IE11 doesn"t cache this XHR
            return request.render("website_sale.cart_popover", values, headers={"Cache-Control": "no-cache"})

        return request.render("website_sale.cart", values)

    @http.route("/shop/payment", type="http", auth="public", website=True, sitemap=False)
    def shop_payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        _logger.info("Website shop_payment start")
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values["only_services"] = order and order.only_services or False
        if order:
            label_for_pay_now = request.env["sale.order"].sudo().label_for_pay_now(order)
            if label_for_pay_now:
                render_values["label_for_pay_now"] = label_for_pay_now
        if render_values["errors"]:
            render_values.pop("acquirers", "")
            render_values.pop("tokens", "")

        _logger.info("Website shop_payment end")
        return request.render("website_sale.payment", render_values)


    def _prepare_building_object_domain(self, partner):
        return [
            ("partner_id", "in", [partner.id])
        ]


class CustomerPortal(CustomerPortal):

    def _prepare_quotations_domain(self, partner):
        return [
            '|',
            ('partner_id', '=', partner.id),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),

            ('state', 'in', ['sent', 'cancel'])
        ]

    def _prepare_orders_domain(self, partner):
        return [
            '|',
            ('partner_id', '=', partner.id),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),

            ('state', 'in', ['sale', 'done'])
        ]


    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        _logger.info("values=%s", values)
        _logger.info("partner=%s", partner)
        domain = self._prepare_quotations_domain(partner)
        _logger.info("domain=%s", domain)
        searchbar_sortings = self._get_sale_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        _logger.info("domain=%s", domain)
        # count for pager
        quotation_count = SaleOrder.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        _logger.info("quotations=%s", quotations)

        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        _logger.info("values=%s", values)
        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = self._prepare_orders_domain(partner)

        searchbar_sortings = self._get_sale_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager
        orders = SaleOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_orders", values)


    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        _logger.error("post=%s", post)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                        _logger.error("values[field]=%s, int(values[field]=%s", values[field], int(values[field]))
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })
        _logger.error("values=%s", values)
        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response




    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not order_sudo.has_to_be_signed():
            return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        if not order_sudo.has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confirmation_mail()

        pdf = request.env.ref('mobius_sale_order_reports.action_report_sale_order_zamowienie').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[0]

        _message_post_helper(
            'sale.order', order_sudo.id, _('Order signed by %s') % (name,),
            attachments=[('%s.pdf' % order_sudo.name, pdf)],
            **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        BuildingObject = request.env["building.object"].sudo()

        values["building_count"] = BuildingObject.search_count(self._prepare_building_object_domain(partner))

        partner = request.env.user.partner_id
        _logger.info("partner=%s", partner)
        SaleOrder = request.env['sale.order'].sudo()
        if 'quotation_count' in counters:
            values['quotation_count'] = SaleOrder.sudo().search_count(self._prepare_quotations_domain(partner))
        if 'order_count' in counters:
            values['order_count'] = SaleOrder.sudo().search_count(self._prepare_orders_domain(partner))
        _logger.info("values=%s", values)

        return values

    # def _prepare_home_portal_values(self, counters):
    #     values = super()._prepare_home_portal_values(counters)
    #     partner = request.env.user.partner_id
    #     _logger.info("partner=%s", partner)
    #     SaleOrder = request.env['sale.order']
    #     if 'quotation_count' in counters:
    #         values['quotation_count'] = SaleOrder.sudo().search_count(self._prepare_quotations_domain(partner))
    #     if 'order_count' in counters:
    #         values['order_count'] = SaleOrder.sudo().search_count(self._prepare_orders_domain(partner))
    #     _logger.info("values=%s", values)
    #     return values

    def _prepare_building_object_domain(self, partner):
        return [
            ("partner_id", "in", [partner.id])
        ]

    @http.route(["/my/building_objects"], type="http", website = True)
    def buildingObjectListView(self, **kw):
        partner = request.env.user.partner_id
        BuildingObject = request.env["building.object"].sudo()

        orders = BuildingObject.search(self._prepare_building_object_domain(partner))

        return request.render("mobius_portal_aklima.building_objects_list", {"orders": orders, "page_name": "building_objects_list"})

    @http.route(['/my/building_objects/<model("building.object"):building_id>'], type="http", website=True)
    def buildingObjectFormView(self, building_id, **kw):
        #self.method_traceback()
        vals = {"object": building_id, "page_name": "building_objects_form"}
        return request.render("mobius_portal_aklima.building_objects_form", vals)

    @http.route(["/my/orders/<int:order_id>/confirm_order"], type="http", auth="public", website=True)
    def portal_proforma_confirm_order(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        retur_str = "/my/orders/{}".format(order_id)
        document = request.env["sale.order"].sudo().browse(order_id)
        if document.state in ["done", "sale", "cancel"]:
            return 0
        document.action_confirm()
        document.action_unlock()
        # Create an invoice with invoiceable lines only
        payment = request.env["sale.advance.payment.inv"].with_context({
            "active_model": "sale.order",
            "active_ids": [document.id],
            "active_id": document.id,
        }).sudo().create({
            "advance_payment_method": "percentage",
            "amount": 100,
        })
        payment.sudo().create_invoices()
        return request.redirect(retur_str)


    @http.route("/my/building_objects/<int:building_id>/edit", type="http", auth="user", website=True)
    def building_object_edit(self, building_id, redirect=None, **post):
        _logger.error("kw=%s", post)
        BuildingObject = request.env["building.object"].sudo()
        obj = BuildingObject.browse(building_id)

        values = {
        "obj": obj,
        }
        values.update({
            'error': {},
            'error_message': [],
        })
        partner = request.env.user.partner_id
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        _logger.error("post=%s, request.httprequest.method=%s", post, request.httprequest.method)
        _logger.error("12345 post=%s, request.httprequest.method=%s", post, request.httprequest.method)
        if post and request.httprequest.method == 'POST':
            _logger.error("4442=%s", post)
            date_start = None
            date_end = None
            if post.get("my_datetimepicker"):
                parts = str(post.get("my_datetimepicker")).rsplit(' ', 2)
                date_start = datetime.strptime(parts[0], '%m/%d/%Y').date()
            if post.get("my_datetimepickertwo"):
                parts_two = str(post.get("my_datetimepickertwo")).rsplit(' ', 2)
                date_end = datetime.strptime(parts_two[0], '%m/%d/%Y').date()
            _logger.error("request.env.context.get('uid')=%s", request.env.context.get("uid"))
            _logger.error("env.user.partner_id=%s", request.env.user.partner_id)
            obj.write({
                "name": post.get("name_buil_object"),
                "country_id": post.get("country_id"),
                "state_id": post.get("state_id"),
                "city": post.get("name_city"),
                "street": post.get("name_street"),
                "zip": post.get("name_zip"),
                "total_power": post.get("name_total_power"),
                "partner_id": request.env.user.partner_id.id,
                "start_date": date_start if date_start else obj.start_date,
                "end_date": date_end if date_end else obj.end_date,
                })
            _logger.error("44423=%s", obj)
            return request.redirect('/my/building_objects/{}'.format(obj.id))
            #vals = {"object": obj}
            #return request.render("mobius_portal_aklima.building_objects_form", vals)
            # error, error_message = self.details_form_validate(post)
            # values.update({'error': error, 'error_message': error_message})
            # values.update(post)
            # if not error:
            #     values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
            #     values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
            #     for field in set(['country_id', 'state_id']) & set(values.keys()):
            #         try:
            #             values[field] = int(values[field])
            #         except:
            #             values[field] = False
            #     values.update({'zip': values.pop('zipcode', '')})
            #     partner.sudo().write(values)
            #     if redirect:
            #         return request.redirect(redirect)
            #     return request.redirect('/my/home')

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
        })
        _logger.error("values=%s", values)
        response = request.render("mobius_portal_aklima.building_object_edit", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response




    @http.route(["/my/orders/<int:order_id>/proforma"], type="http", auth="public", website=True)
    def portal_proforma(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            document = request.env["sale.order"].sudo().browse(order_id)
            move = request.env["account.move"].sudo().search([("invoice_origin", "=", document.name)], limit=1)
            document_sudo = move.with_user(SUPERUSER_ID).exists()

        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(model=document_sudo, report_type="pdf", report_ref="mobius_sale_order_reports.action_report_sale_order_pro_forma", download=True)


    @http.route(["/my/orders/<int:order_id>"], type="http", auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access("sale.order", order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref="mobius_sale_order_reports.action_report_sale_order_zamowienie", download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get("view_quote_%s" % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session["view_quote_%s" % order_sudo.id] = now
                body = _("Quotation viewed by customer %s", order_sudo.partner_id.name)
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = {
            "sale_order": order_sudo,
            "message": message,
            "token": access_token,
            "landing_route": "/shop/payment/validate",
            "bootstrap_formatting": True,
            "partner_id": order_sudo.partner_id.id,
            "report_type": "html",
            "action": order_sudo._get_portal_return_action(),
        }
        if order_sudo.company_id:
            values["res_company"] = order_sudo.company_id

        # Payment values
        if order_sudo.has_to_be_paid():
            logged_in = not request.env.user._is_public()

            # Odoo 18: payment.acquirer renamed to payment.provider
            providers_sudo = request.env["payment.provider"].sudo()._get_compatible_providers(
                order_sudo.company_id.id,
                order_sudo.partner_id.id,
                order_sudo.amount_total,
                currency_id=order_sudo.currency_id.id,
                sale_order_id=order_sudo.id,
            )  # In sudo mode to read the fields of providers and partner (if not logged in)
            tokens = request.env["payment.token"].search([
                ("provider_id", "in", providers_sudo.ids),
                ("partner_id", "=", order_sudo.partner_id.id)
            ]) if logged_in else request.env["payment.token"]

            # Make sure that the partner's company matches the order's company.
            if not payment_portal.PaymentPortal._can_partner_pay_in_company(
                order_sudo.partner_id, order_sudo.company_id
            ):
                providers_sudo = request.env["payment.provider"].sudo()
                tokens = request.env["payment.token"]

            fees_by_provider = {
                provider: provider._compute_fees(
                    order_sudo.amount_total,
                    order_sudo.currency_id,
                    order_sudo.partner_id.country_id,
                ) for provider in providers_sudo.filtered("fees_active")
            }
            # Prevent public partner from saving payment methods but force it for logged in partners
            # buying subscription products
            show_tokenize_input = logged_in \
                and not request.env["payment.provider"].sudo()._is_tokenization_required(
                    sale_order_id=order_sudo.id
                )
            values.update({
                "providers": providers_sudo,
                "tokens": tokens,
                "fees_by_provider": fees_by_provider,
                "show_tokenize_input": show_tokenize_input,
                "amount": order_sudo.amount_total,
                "currency": order_sudo.pricelist_id.currency_id,
                "partner_id": order_sudo.partner_id.id,
                "access_token": order_sudo.access_token,
                "transaction_route": order_sudo.get_portal_url(suffix="/transaction"),
                "landing_route": order_sudo.get_portal_url(),
            })

        if order_sudo.state in ("draft", "sent", "cancel"):
            history = request.session.get("my_quotations_history", [])
        else:
            history = request.session.get("my_orders_history", [])
        values.update(get_records_pager(history, order_sudo))

        return request.render("sale.sale_order_portal_template", values)


class PortalAccount(CustomerPortal):

    @http.route(["/my/invoices/<int:invoice_id>"], type="http", auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        try:
            invoice_sudo = self._document_check_access("account.move", invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("html", "pdf", "text"):
            return self._show_report(model=invoice_sudo, report_type=report_type, report_ref="mobius_sale_order_reports.action_report_sale_order_pro_forma", download=download)

        values = self._invoice_get_page_view_values(invoice_sudo, access_token, **kw)
        return request.render("account.portal_invoice_page", values)

class WebsiteSaleDeliveryCustom(http.Controller):

    @http.route(['/shop/payment'], type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        _logger.info("WebsiteSaleDeliveryCustom shop_payment")
        _logger.info("post=%s", post)
        post['carrier_id'] = 9
        post['keep_carrier'] = True
        post['checked'] = True
        _logger.info("post=%s", post)
        return WebsiteSale().shop_payment(**post)

    @http.route(['/shop/carrier_rate_shipment'], type='json', auth='public', methods=['POST'], website=True)
    def cart_carrier_rate_shipment(self, carrier_id, **kw):
        order = request.website.sale_get_order(force_create=True)
        _logger.info("order=%s", order)
        if not int(carrier_id) in order._get_delivery_methods().ids:
            raise UserError(_('It seems that a delivery method is not compatible with your address. Please refresh the page and try again.'))

        Monetary = request.env['ir.qweb.field.monetary']

        res = {'carrier_id': carrier_id}
        carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id))

        rate = carrier.rate_shipment(order)
        _logger.info("rate=%s", rate)

        if rate.get('success'):
            _logger.info("carrier.name=%s", carrier.name)
            if carrier.base_delivery:
                _logger.info("22")
                res['status'] = True
                res['new_amount_delivery'] = Monetary.value_to_html(order.amount_delivery, {'display_currency': order.currency_id})
                res['is_free_delivery'] = not bool(rate['price'])
                res['is_base_delivery'] = carrier.base_delivery
                res['checked'] = True
                res['error_message'] = rate['warning_message']
                _logger.info("res=%s", res)
                return res
            tax_ids = carrier.product_id.taxes_id.filtered(lambda t: t.company_id == order.company_id)
            if tax_ids:
                fpos = order.fiscal_position_id
                tax_ids = fpos.map_tax(tax_ids)
                taxes = tax_ids.compute_all(
                    rate['price'],
                    currency=order.currency_id,
                    quantity=1.0,
                    product=carrier.product_id,
                    partner=order.partner_shipping_id,
                )
                if request.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                    rate['price'] = taxes['total_excluded']
                    _logger.info("price=%s", taxes['total_excluded'])
                else:
                    rate['price'] = taxes['total_included']
                    _logger.info("price=%s", taxes['total_included'])

            res['status'] = True
            res['new_amount_delivery'] = Monetary.value_to_html(rate['price'], {'display_currency': order.currency_id})
            _logger.info("113311 res['new_amount_delivery']=%s", res['new_amount_delivery'])
            res['is_free_delivery'] = not bool(rate['price'])
            res['is_base_delivery'] = carrier.base_delivery
            res['error_message'] = rate['warning_message']
        else:
            res['status'] = False
            res['new_amount_delivery'] = Monetary.value_to_html(0.0, {'display_currency': order.currency_id})
            res['is_base_delivery'] = carrier.base_delivery
            res['error_message'] = rate['error_message']
        _logger.info("res=%s", res)
        return res


    @http.route(['/shop/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        if order and carrier_id != order.carrier_id.id:
            if any(tx.state not in ("canceled", "error", "draft") for tx in order.transaction_ids):
                raise UserError(_('It seems that there is already a transaction for your order, you can not change the delivery method anymore'))
            order._check_carrier_quotation(force_carrier_id=carrier_id)
        _logger.info("order=%s, carrier_id=%s", order, carrier_id)
        _logger.info("order=%s, carrier_id=%s", order, carrier_id)
        return self._update_website_sale_delivery_return(order, **post)

    def _update_website_sale_delivery_return(self, order, **post):
        Monetary = request.env['ir.qweb.field.monetary']
        carrier_id = int(post['carrier_id'])
        currency = order.currency_id
        _logger.info("carrier_id=%s, currency=%s", carrier_id, currency)
        if request.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
            amount_delivery = sum(order.order_line.filtered('is_delivery').mapped('price_subtotal'))
        else:
            amount_delivery = sum(order.order_line.filtered('is_delivery').mapped('price_total'))
        if order:
            if float_is_zero(amount_delivery, precision_digits=2):
                is_free_delivery = True
            else:
                is_free_delivery = False
            d = {
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                'is_free_delivery': is_free_delivery,
                'new_amount_delivery': Monetary.value_to_html(amount_delivery, {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
                'new_amount_total_raw': order.amount_total,
            }
            _logger.info("d=%s", d)
            return {
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                # 'is_free_delivery': not bool(order.amount_delivery),
                'is_free_delivery': is_free_delivery,
                'new_amount_delivery': Monetary.value_to_html(amount_delivery, {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.amount_total, {'display_currency': currency}),
                'new_amount_total_raw': order.amount_total,
            }

        return {}