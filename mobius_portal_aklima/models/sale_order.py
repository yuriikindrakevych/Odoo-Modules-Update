# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
import json
from odoo.http import request
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.tests import Form

from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


import inspect
import traceback

class Website(models.Model):
    _inherit = "website"

    def _get_building_objects(self):
        partner = self.env.user.partner_id
        BuildingObject = self.env["building.object"].sudo()

        values = BuildingObject.search(self._prepare_building_object_domain(partner))

        return values

    def _get_building_objects_shop(self):
        partner = self.env.user.partner_id
        BuildingObject = self.env["building.object"].sudo()
        values = []
        values.append({"id": False, "name": "None"})
        values_rec = BuildingObject.search(self._prepare_building_object_domain(partner))
        for rec in values_rec:
            values.append({"id": rec.id, "name": rec.name})
        _logger.info("values=%s", values)
        return values

    def _prepare_building_object_domain(self, partner):
        return [
            ("partner_id", "in", [partner.id])
        ]


    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        """ Return the current sales order after mofications specified by params.
        :param bool force_create: Create sales order if not already existing
        :param str code: Code to force a pricelist (promo code)
                         If empty, it's a special case to reset the pricelist with the first available else the default.
        :param bool update_pricelist: Force to recompute all the lines from sales order to adapt the price with the current pricelist.
        :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
        :returns: browse record for the current sales order
        """
        self.ensure_one()
        partner = self.env.user.partner_id
        sale_order_id = request.session.get("sale_order_id")
        check_fpos = False
        if not sale_order_id and not self.env.user._is_public():
            last_order = partner.last_website_so_id
            if last_order:
                available_pricelists = self.get_pricelist_available()
                # Do not reload the cart of this user last visit if the cart uses a pricelist no longer available.
                sale_order_id = last_order.pricelist_id in available_pricelists and last_order.id
                check_fpos = True

        # Test validity of the sale_order_id
        sale_order = self.env["sale.order"].with_company(request.website.company_id.id).sudo().browse(sale_order_id).exists() if sale_order_id else None

        # Ignore the current order if a payment has been initiated. We don't want to retrieve the
        # cart and allow the user to update it when the payment is about to confirm it.
        if sale_order and sale_order.get_portal_last_transaction().state in ("pending", "authorized", "done"):
            sale_order = None

        # Do not reload the cart of this user last visit if the Fiscal Position has changed.
        if check_fpos and sale_order:
            fpos_id = (
                self.env["account.fiscal.position"].sudo()
                .with_company(sale_order.company_id.id)
                .get_fiscal_position(sale_order.partner_id.id, delivery_id=sale_order.partner_shipping_id.id)
            ).id
            if sale_order.fiscal_position_id.id != fpos_id:
                sale_order = None

        if not (sale_order or force_create or code):
            if request.session.get("sale_order_id"):
                request.session["sale_order_id"] = None
            return self.env["sale.order"]

        if self.env["product.pricelist"].browse(force_pricelist).exists():
            pricelist_id = force_pricelist
            request.session["website_sale_current_pl"] = pricelist_id
            update_pricelist = True
        else:
            pricelist_id = request.session.get("website_sale_current_pl") or self.get_current_pricelist().id

        if not self._context.get("pricelist"):
            self = self.with_context(pricelist=pricelist_id)

        # cart creation was requested (either explicitly or to configure a promo code)
        if not sale_order:
            # TODO cache partner_id session
            pricelist = self.env["product.pricelist"].browse(pricelist_id).sudo()
            so_data = self._prepare_sale_order_values(partner, pricelist)
            sale_order = self.env["sale.order"].with_company(request.website.company_id.id).with_user(SUPERUSER_ID).create(so_data)

            # set fiscal position
            if request.website.partner_id.id != partner.id:
                sale_order.onchange_partner_shipping_id()
            else: # For public user, fiscal position based on geolocation
                country_code = request.session["geoip"].get("country_code")
                if country_code:
                    country_id = request.env["res.country"].search([("code", "=", country_code)], limit=1).id
                    sale_order.fiscal_position_id = request.env["account.fiscal.position"].sudo().with_company(request.website.company_id.id)._get_fpos_by_region(country_id)
                else:
                    # if no geolocation, use the public user fp
                    sale_order.onchange_partner_shipping_id()

            request.session["sale_order_id"] = sale_order.id

            # The order was created with SUPERUSER_ID, revert back to request user.
            sale_order = sale_order.with_user(self.env.user).sudo()

        # case when user emptied the cart
        if not request.session.get("sale_order_id"):
            request.session["sale_order_id"] = sale_order.id

        # check for change of pricelist with a coupon
        pricelist_id = pricelist_id or partner.property_product_pricelist.id

        # check for change of partner_id ie after signup
        if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
            flag_pricelist = False
            if pricelist_id != sale_order.pricelist_id.id:
                flag_pricelist = True
            fiscal_position = sale_order.fiscal_position_id.id

            # change the partner, and trigger the onchange
            sale_order.write({"partner_id": partner.id})
            sale_order.with_context(not_self_saleperson=True).onchange_partner_id()
            sale_order.write({"partner_invoice_id": partner.id})
            sale_order.onchange_partner_shipping_id() # fiscal position
            sale_order["payment_term_id"] = self.sale_get_payment_term(partner)

            # check the pricelist : update it if the pricelist is not the 'forced' one
            values = {}
            if sale_order.pricelist_id:
                if sale_order.pricelist_id.id != pricelist_id:
                    values["pricelist_id"] = pricelist_id
                    update_pricelist = True

            # if fiscal position, update the order lines taxes
            if sale_order.fiscal_position_id:
                sale_order._compute_tax_id()

            # if values, then make the SO update
            if values:
                sale_order.write(values)

            # check if the fiscal position has changed with the partner_id update
            recent_fiscal_position = sale_order.fiscal_position_id.id
            # when buying a free product with public user and trying to log in, SO state is not draft
            if (flag_pricelist or recent_fiscal_position != fiscal_position) and sale_order.state == "draft":
                update_pricelist = True

        if code and code != sale_order.pricelist_id.code:
            code_pricelist = self.env["product.pricelist"].sudo().search([("code", "=", code)], limit=1)
            if code_pricelist:
                pricelist_id = code_pricelist.id
                update_pricelist = True
        elif code is not None and sale_order.pricelist_id.code and code != sale_order.pricelist_id.code:
            # code is not None when user removes code and click on "Apply"
            pricelist_id = partner.property_product_pricelist.id
            update_pricelist = True

        # update the pricelist
        if update_pricelist:
            request.session["website_sale_current_pl"] = pricelist_id
            values = {"pricelist_id": pricelist_id}
            sale_order.write(values)
            for line in sale_order.order_line:
                if line.exists():
                    sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)

        return sale_order


    def _prepare_sale_order_values(self, partner, pricelist):
        self.ensure_one()
        affiliate_id = request.session.get("affiliate_id")
        salesperson_id = affiliate_id if self.env["res.users"].sudo().browse(affiliate_id).exists() else request.website.salesperson_id.id
        addr = partner.address_get(["delivery"])
        if not request.website.is_public_user():
            last_sale_order = self.env["sale.order"].sudo().search([("partner_id", "=", partner.id)], limit=1, order="date_order desc, id desc")
            if last_sale_order and last_sale_order.partner_shipping_id.active:  # first = me
                addr["delivery"] = last_sale_order.partner_shipping_id.id
        default_user_id = partner.parent_id.user_id.id or partner.user_id.id
        values = {
            "partner_id": partner.id,
            "pricelist_id": pricelist.id,
            "payment_term_id": self.sale_get_payment_term(partner),
            "team_id": self.salesteam_id.id or partner.parent_id.team_id.id or partner.team_id.id,
            "partner_invoice_id": partner.id,
            "partner_shipping_id": addr["delivery"],
            "user_id": salesperson_id or self.salesperson_id.id or default_user_id,
            "website_id": self._context.get("website_id"),
            "company_id": self.company_id.id,
        }
        return values


class SaleOrder(models.Model):
    _inherit = "sale.order"

    created_from_website = fields.Boolean(help="Technical field")
    amount_delivery = fields.Monetary(string="Delivery", store=True, compute="_amount_all")
    amount_total_custom = fields.Monetary(string="Total Custom", store=True, compute="_amount_all")
    amount_tax_custom = fields.Monetary(string="Taxes Custom", store=True, compute="_amount_all")
    is_need_seller_agreement = fields.Boolean(string="Need Seller Agreement", compute='_compute_is_need_seller_agreement', store=True)

    @api.depends('order_line.product_id', 'order_line.product_template_id')
    def _compute_is_need_seller_agreement(self):
        for order in self:
            for line in order.order_line:
                if line.product_id and line.product_id.is_seller_agreement or line.product_template_id and line.product_template_id.is_seller_agreement:
                    order.is_need_seller_agreement = True
                    break
                else:
                    order.is_need_seller_agreement = False

    def _check_carrier_quotation(self, force_carrier_id=None):
        # Setup logger for this method
        _logger = logging.getLogger(__name__)

        # replace base method
        self.ensure_one()
        DeliveryCarrier = self.env['delivery.carrier']

        # Log initial method entry
        _logger.info(f"Starting carrier quotation check for order {self.name}")
        _logger.info(f"Force Carrier ID: {force_carrier_id}")
        _logger.info(f"Only Services: {self.only_services}")

        if self.only_services:
            _logger.info("Only services mode: Clearing carrier and removing delivery line")
            self.write({'carrier_id': None})
            self._remove_delivery_line()
            return True
        else:
            self = self.with_company(self.company_id)
            keep_carrier = self.env.context.get('keep_carrier', False)

            # Log carrier selection logic
            _logger.info(f"Keep Carrier: {keep_carrier}")

            # attempt to use partner's preferred carrier
            if not force_carrier_id and self.partner_shipping_id.property_delivery_carrier_id and not keep_carrier:
                force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id
                _logger.info(f"Using partner's preferred carrier: {force_carrier_id}")

            carrier = force_carrier_id and DeliveryCarrier.browse(force_carrier_id) or self.carrier_id
            available_carriers = self._get_delivery_methods()

            _logger.info(f"Initial Carrier: {carrier.name if carrier else 'None'}")
            _logger.info(f"Available Carriers: {', '.join(c.name for c in available_carriers)}")

            if carrier:
                if carrier not in available_carriers:
                    _logger.info(f"Carrier {carrier.name} not in available carriers")
                    carrier = DeliveryCarrier
                else:
                    # set the forced carrier at the beginning of the list to be verfied first below
                    available_carriers -= carrier
                    available_carriers = carrier + available_carriers
                    _logger.info(f"Reordered carriers with {carrier.name} first")

            if force_carrier_id or not carrier or carrier not in available_carriers:
                _logger.info("Searching for a verified carrier")
                for delivery in available_carriers:
                    verified_carrier = delivery._match_address(self.partner_shipping_id)
                    if verified_carrier:
                        carrier = delivery
                        _logger.info(f"Found verified carrier: {carrier.name}")
                        break

                self.write({'carrier_id': carrier.id})
                _logger.info(f"Assigned carrier: {carrier.name}")

            self._remove_delivery_line()

            if carrier:
                _logger.info(f"Attempting to rate shipment with carrier: {carrier.name}")
                res = carrier.rate_shipment(self)

                if res.get('success'):
                    _logger.info(f"Shipment rating successful. Price: {res['price']}")
                    self.set_delivery_line(carrier, res['price'])
                    self.delivery_rating_success = True
                    self.delivery_message = res['warning_message']

                    if res['warning_message']:
                        _logger.warning(f"Carrier warning: {res['warning_message']}")
                else:
                    _logger.error(f"Shipment rating failed. Error: {res['error_message']}")
                    self.set_delivery_line(carrier, 0.0)
                    self.delivery_rating_success = False
                    self.delivery_message = res['error_message']

        _logger.info(f"Carrier quotation check completed. Carrier found: {bool(carrier)}")
        return bool(carrier)


    def set_amount_delivery_default(self):
        self.update({
            "amount_delivery": 0,
            "amount_total_custom": self.amount_total + 0,
            "amount_tax_custom": self.amount_tax + 0,
            })

    @api.depends("order_line.price_total")
    def _amount_all(self):
        _logger.error("test 4242")
        res = super()._amount_all()
        delivery = self.env["delivery.carrier"].sudo().with_context(lang='en_US').search([("base_delivery", "=", True)])
        _logger.info("DELIVERY 8888=%s", delivery)
        _logger.info("self=%s", self)
        _logger.info("res=%s", res)
        for order in self:
            _logger.error("order=%s", order)
            template = order.get_template_automatic_delivery_sale_order()
            if not order.is_enable_use_automatic_delivery_sale_order() or not template:
                _logger.error("return res #1")
                order.set_amount_delivery_default()
                return res

            _logger.error("res delivery=%s, template=%s, template.name=%s", res, template, template.name)
            _logger.error("tax_totals_json=%s", order.amount_total)
            total = order.amount_total
            if not template.the_price_is_suitable(total):
                _logger.error("return res #2")
                order.set_amount_delivery_default()
                return res

            weight = order.calculate_weight_in_order()
            get_tax_product = delivery.product_id.taxes_id
            sum_tax = 0
            clc_tax = 0.0
            delivery_condition = 0
            for tax in get_tax_product:
                sum_tax += tax.amount

            condition_is_met = template.the_weight_is_suitable(weight)
            
            _logger.error("amount_total_custom=%s", order.amount_total_custom)
            _logger.error("amount_delivery=%s", order.amount_delivery)

            if condition_is_met:
                delivery_condition = template.automatic_delivery_condition_is_met
            else:
                delivery_condition = template.automatic_delivery_condition_is_not_met

            if sum_tax != 0:
                clc_tax = round((delivery_condition / 100 * sum_tax), 2)
            _logger.error("delivery_condition=%s, clc_tax=%s", delivery_condition, clc_tax)

            order.update({
                "amount_delivery": delivery_condition,
                "amount_total_custom": order.amount_total + delivery_condition + clc_tax,
                "amount_tax_custom": order.amount_tax + clc_tax,
            })
            _logger.error("amount_delivery=%s", order.amount_delivery)
            _logger.error("amount_delivery 2=%s", delivery_condition)


            _logger.error("order.amount_tax=%s", order.amount_tax)
            _logger.error("order.amount_tax=%s", order.amount_total_custom)

            _logger.error("amount_total_custom=%s", order.amount_total)
            _logger.error("amount_total_custom=%s", order.amount_total_custom)
        return res


    def check_all_product_available(self):
        self = self.sudo()
        self._amount_all()
        wh_warehouse = self.env["stock.location"].sudo().search([("barcode", "=", "WH-STOCK")])

        wh_warehouse = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
        if not self.order_line:
            _logger.error("END 1 (bad)")
            return False
        for line in self.order_line:
            if line.product_id.detailed_type == "consu":
                _logger.error("END 3 (bad)")
                return False
            _logger.error("first line prod.name=%s", line.product_id.name)
            if line.product_id.detailed_type == "product":
                available_quantity = self.env["stock.quant"].with_user(SUPERUSER_ID)._get_available_quantity_m(line.product_id, wh_warehouse)
                _logger.error("available_quantity=%s, qty_need=%s", available_quantity, line.product_uom_qty)
                if available_quantity <= 0 and line.product_uom_qty > 0:
                    _logger.error("END 2 (bad)")
                    return False

        return True

    def check_all_product_available_for_buy(self):
        self = self.sudo()
        self._amount_all()
        wh_warehouse = self.env["stock.location"].sudo().search([("barcode", "=", "WH-STOCK")])

        wh_warehouse = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
        if not self.order_line:
            _logger.error("END 1 (bad)")
            return False

        for line in self.order_line:
            if line.product_id.detailed_type == "consu":
                _logger.error("END 3 (bad)")
                return False
            _logger.error("first line prod.name=%s", line.product_id.name)
            if line.product_id.detailed_type == "product":
                available_quantity = self.env["stock.quant"].with_user(SUPERUSER_ID)._get_available_quantity_m(line.product_id, wh_warehouse, key="check_for_portal_shop")
                _logger.error("available_quantity=%s, qty_need=%s", available_quantity, line.product_uom_qty)
                if available_quantity <= 0:
                    _logger.error("END 2 (bad)")
                    return False
        return True

    def has_all_available(self):
        _logger.error("Self=%s", self)
        return self.check_all_product_available()

    def label_for_pay_now(self, order):
        self = self.sudo()
        wh_warehouse = self.env["stock.location"].with_user(SUPERUSER_ID).search([("barcode", "=", "WH-STOCK")])

        wh_warehouse = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
        record = order
        can_confirm = True
        for prod in record.order_line:
            if prod.product_template_id.id == 3 or prod.product_id.id == 3:
                continue
            if prod.product_id:
                available_quantity = 0
                product = self.env["product.product"].with_user(SUPERUSER_ID).search([("id", "=", prod.product_id.id)], limit=1)
                available_quantity = self.env["stock.quant"]._get_available_quantity_m(product, wh_warehouse)
            elif prod.product_template_id:
                product = self.env["product.product"].with_user(SUPERUSER_ID).search([("product_tmpl_id", "=", prod.product_template_id.id)], limit=1)
                available_quantity = self.env["stock.quant"]._get_available_quantity_m(product, wh_warehouse)
            if available_quantity < prod.product_uom_qty:
                can_confirm = False
                break
        if can_confirm:
            return (_("Confirm Order"))
        else:
            return (_("Create Quotation"))



    def scheduler_use_validity_period_for_order_created_with_website(self):
        if not self.env['ir.config_parameter'].sudo().get_param("use_validity_period_for_order_created_with_website"):
            return 0

        validity_period_days = int(self.env['ir.config_parameter'].sudo().get_param("validity_period_for_order_created_with_website_days"))
        if validity_period_days <= 0:
            return 0

        team_id = self.env["crm.team"].search([("name", "=", "Website")], limit=1)
        if not team_id:
            return 0

        sale_orders = self.env["sale.order"].search([("state", "in", ["sent", "sale", "done"]), ("team_id", "=", team_id.id)])

        to_cancel = []
        for order in sale_orders:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            if invoices:
                posted_invoice = invoices.filtered(lambda i: i.state == "posted")
                if not posted_invoice:
                    create_date = order.create_date
                    now_date = datetime.now()
                    delta = now_date - create_date
                    if delta.days > validity_period_days:
                        to_cancel.append(order.id)
        filtered_to_cancel = sale_orders.filtered(lambda s: s.id in to_cancel)
        for order in filtered_to_cancel:
            order.action_cancel()

    def can_download_pro_forma_p(self):
        if self:
            move = self.env["account.move"].sudo().search([("invoice_origin", "=", self.name)], limit=1)
            if move:
                return True
        return False


    def download_pro_forma(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        url = self.access_url + "/proforma" + "%s?access_token=%s%s%s%s%s" % ("",
            self._portal_ensure_token(),
            "&report_type=%s" % report_type if report_type else "",
            "&download=true" if download else "",
            query_string if query_string else "",
            "#%s" % anchor if anchor else ""
        )
        return url

    def confirm_order_m(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        url = self.access_url + "/confirm_order" + "%s?access_token=%s" % ("", self._portal_ensure_token())
        return url

    def method_traceback(self):
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        _logger.error("".join(stack_trace))


    def write(self, values):
        _logger.error("self=%s, values=%s", self, values)
        self.method_traceback()
        return super().write(values)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def method_traceback(self):
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        _logger.error("".join(stack_trace))

    @api.model_create_multi
    def create(self, vals_list):
        _logger.error("create 123 vals_list=%s", vals_list)

        for vals in vals_list:
            if vals.get('product_id'):
                product = self.env['product.product'].browse(vals['product_id'])
                _logger.info("product=%s, is_seller_agreement=%s", product, product.is_seller_agreement)
                if product.is_seller_agreement:
                    _logger.error("111 Default price of product %s", product.name)
                    vals['price_unit'] = 0.0
            if vals.get('product_tmpl_id'):
                product_tmpl = self.env['product.template'].browse(vals['product_tmpl_id'])
                _logger.info("product=%s, is_seller_agreement=%s", product_tmpl, product_tmpl.is_seller_agreement)
                if product_tmpl.is_seller_agreement:
                    _logger.error("222 Default price of product %s", product_tmpl.name)
                    vals['price_unit'] = 0.0
        _logger.error("vals_list=%s", vals_list)
        records = super().create(vals_list)
        _logger.error("records=%s", records)
        # for record in records:
        #     if record.product_id.is_seller_agreement:
        #         _logger.error("Default price of product %s", record.product_id.name)
        #         record.price_unit = 0.0
        self.method_traceback()
        return records

    def write(self, values):
        _logger.error("write 123self=%s, values=%s", self, values)
        if values.get('product_id'):
            product = self.env['product.product'].browse(values['product_id'])
            _logger.info("product=%s, is_seller_agreement=%s", product, product.is_seller_agreement)
            if product.is_seller_agreement:
                _logger.error("111 Default price of product %s", product.name)
                values['price_unit'] = 0.0
                values['discount'] = 0.0
        self.method_traceback()
        return super().write(values)

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _set_pending(self, state_message=None):
        """ Override of payment to send the quotations automatically. """
        self = self.sudo()
        for record in self:
            sales_orders = record.sale_order_ids.filtered(lambda so: so.state in ["draft", "sent"])
            sales_orders.filtered(lambda so: so.state == "draft")
            wh_warehouse = self.env["stock.location"].with_user(SUPERUSER_ID).search([("barcode", "=", "WH-STOCK")])

            wh_warehouse = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
            for record in sales_orders:
                can_confirm = True
                for prod in record.order_line:
                    if prod.product_template_id.detailed_type != "product" or prod.product_id.detailed_type != "product":
                        continue
                    if prod.product_id:
                        available_quantity = 0
                        product = self.env["product.product"].with_user(SUPERUSER_ID).search([("id", "=", prod.product_id.id)], limit=1)
                        available_quantity = self.env["stock.quant"]._get_available_quantity_m(product, wh_warehouse)
                    elif prod.product_template_id:
                        product = self.env["product.product"].with_user(SUPERUSER_ID).search([("product_tmpl_id", "=", prod.product_template_id.id)], limit=1)
                        available_quantity = self.env["stock.quant"]._get_available_quantity_m(product, wh_warehouse)
                    if available_quantity < prod.product_uom_qty:
                        can_confirm = False
                        break
                _logger.info("222 can_confirm=%s", can_confirm)
                if can_confirm:
                    document = request.env["sale.order"].sudo().browse(record.id)
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

                    delivery = self.env["delivery.carrier"].sudo().with_context(lang='en_US').search([("base_delivery", "=", True)], limit=1)
                    _logger.error("DELIVERY 8888=%s", delivery)
                    if not delivery:
                        product = self.env['product.product'].sudo().create({
                            'name': 'Normal Delivery Charges',
                            'type': 'service',
                            'list_price': 0,
                            'categ_id': self.env.ref('delivery.product_category_deliveries').id,
                        })
                        normal_delivery = self.env['delivery.carrier'].sudo().create({
                            'name': 'Normal Delivery Charges',
                            'fixed_price': 0,
                            'delivery_type': 'fixed',
                            'product_id': product.id,
                            "base_delivery": True,
                        })
                        delivery = self.env["delivery.carrier"].sudo().with_context(lang='en_US').search([("base_delivery", "=", True)], limit=1)
                    
                    delivery_wizard = Form(self.env['choose.delivery.carrier'].sudo().with_context({
                        'default_order_id': record.id,
                        'default_carrier_id': delivery.id,
                    }))
                    choose_delivery_carrier = delivery_wizard.save()
                    choose_delivery_carrier.button_confirm()
                else:
                    pass
        return super(PaymentTransaction, self)._set_pending(state_message=state_message)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_seller_agreement = fields.Boolean("Agree with seller")

    # Disabled for Odoo 18 - method signature changed, causes RecursionError
    # Templates using this data (is_seller_agreement, show_available_info) were removed
    # def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
    #     d = super(ProductTemplate, self)._get_combination_info(combination=combination,
    #         product_id=product_id, add_qty=add_qty, pricelist=pricelist, parent_combination=parent_combination, only_template=only_template)
    #
    #     if not self.env['ir.config_parameter'].sudo().get_param("use_product_show_availability"):
    #         d["show_available_info"] = False
    #         return d
    #     d["show_available_info"] = True
    #
    #     self = self.sudo()
    #     wh_warehouse = self.env["stock.location"].with_user(SUPERUSER_ID).search([("barcode", "=", "WH-STOCK")])
    #     product = False
    #     wh_warehouse = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
    #     available_quantity = 0
    #     _logger.info("product=%s, template=%s", d.get("product_id"), d.get("product_template_id"))
    #     if d.get("product_id"):
    #         product = self.env["product.product"].with_user(SUPERUSER_ID).search([("id", "=", d.get("product_id"))], limit=1)
    #         available_quantity = self.env["stock.quant"]._get_available_quantity_m(product, wh_warehouse)
    #     elif d.get("product_template_id"):
    #         product = self.env["product.product"].with_user(SUPERUSER_ID).search([("product_tmpl_id", "=", d.get("product_template_id"))], limit=1)
    #         available_quantity = self.env["stock.quant"]._get_available_quantity_m(product, wh_warehouse)

    #     available_threshold = self.env['ir.config_parameter'].sudo().get_param("available_threshold") #like 5
    #
    #     if product:
    #         if available_quantity <= available_threshold:
    #             d["stock_message"] = (_("Availability is negotiated with the seller"))
    #
    #         elif available_quantity > available_threshold:
    #             available_quantity = self.env["stock.quant"]._get_available_quantity_m(product, wh_warehouse, key="check_for_portal_shop")
    #             if available_quantity > 0:
    #                 d["stock_message"] = (_("Available"))
    #             elif available_quantity <= 0:
    #                 d["stock_message"] = (_("Available within 5 days"))
    #
    #         d["is_seller_agreement"] = product.is_seller_agreement
    #         if product.is_seller_agreement:
    #             _logger.info("d['price'] = %s", d['price'])
    #             _logger.info("d['list_price'] = %s", d['list_price'])
    #             _logger.info("d['price_extra'] = %s", d['price_extra'])
    #             _logger.info("d['has_discounted_price'] = %s", d['has_discounted_price'])
    #             d['price'] = 0.0
    #             d['list_price'] = 0.0
    #             d['price_extra'] = 0.0
    #             d['has_discounted_price'] = False
    #
    #         d["available_quantity"] = available_quantity
    #
    #     return d


    def _get_available_quantity_m(self, product):
        self = self.sudo()
        wh_warehouse = self.env["stock.location"].search([("barcode", "=", "WH-STOCK")])

        wh_warehouse = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
        available_quantity = self.env["stock.quant"].with_user(SUPERUSER_ID)._get_available_quantity_m(product, wh_warehouse)
        return available_quantity

class ProductProduct(models.Model):
    _inherit = "product.product"

    rounding = fields.Float(related="uom_id.rounding", store=True)

class Location(models.Model):
    _inherit = "stock.location"

    add_quant_to_website = fields.Boolean("Stock For WebSite")
    customs_cleared_product = fields.Boolean("Custom Cleared Product")

class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_available_quantity_m(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False, key=False):
        """ Return the available quantity, i.e. the sum of `quantity` minus the sum of
        `reserved_quantity`, for the set of quants sharing the combination of `product_id,
        location_id` if `strict` is set to False or sharing the *exact same characteristics*
        otherwise.
        This method is called in the following usecases:
            - when a stock move checks its availability
            - when a stock move actually assign
            - when editing a move line, to check if the new value is forced or not
            - when validating a move line with some forced values and have to potentially unlink an
              equivalent move line in another picking
        In the two first usecases, `strict` should be set to `False`, as we don't know what exact
        quants we'll reserve, and the characteristics are meaningless in this context.
        In the last ones, `strict` should be set to `True`, as we work on a specific set of
        characteristics.

        :return: available quantity as a float
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
        quants = quants.filtered(lambda x: x.location_id.add_quant_to_website == True)
        _logger.info("quants=%s", quants)
        if key == "check_for_portal_shop":
            quants = quants.filtered(lambda x: x.location_id.customs_cleared_product == True)

        if not quants:
            return 0.0
        _logger.info("product_id=%s", product_id)
        rounding = product_id.rounding

        _logger.info("rounding=%s", rounding)
        _logger.info("product_id=%s, product_id.name=%s", product_id, product_id.name)
        if product_id.tracking == "none":
            available_quantity = (sum(quants.mapped("quantity")) - sum(quants.mapped("reserved_quantity")))
            if allow_negative:
                return available_quantity
            else:
                return available_quantity if float_compare(available_quantity, 0.0, precision_rounding=rounding) >= 0.0 else 0.0
        else:
            availaible_quantities = {lot_id: 0.0 for lot_id in list(set(quants.mapped("lot_id"))) + ["untracked"]}
            for quant in quants:
                if not quant.lot_id:
                    availaible_quantities["untracked"] += quant.quantity - quant.reserved_quantity
                else:
                    availaible_quantities[quant.lot_id] += quant.quantity - quant.reserved_quantity
            if allow_negative:
                return sum(availaible_quantities.values())
            else:
                summ = 0.0
                _logger.info("availaible_quantities=%s, availaible_quantities.values()=%s", availaible_quantities, availaible_quantities.values())
                for available_quantity in availaible_quantities.values():
                    _logger.info("available_quantity=%s", available_quantity)
                    if float_compare(available_quantity, 0, precision_rounding=rounding) > 0.0:
                        summ += available_quantity
                return summ
                return sum([available_quantity for available_quantity in availaible_quantities.values() if float_compare(available_quantity, 0, precision_rounding=rounding) > 0])

