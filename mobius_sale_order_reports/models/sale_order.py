from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import OrderedSet
import logging
import math
import re
_logger = logging.getLogger(__name__)
import inspect
import traceback

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_delivery = fields.Boolean(help="Technical field")

    def method_traceback(self):
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        _logger.error(''.join(stack_trace))

    def get_order_line_can_be_printed(self):
        if self.is_delivery:
            return True
        if self.product_id.detailed_type == "service":
            if self.product_uom_qty == 0:
                return False
        return True

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def check_can_print(self, price_subtotal, tax_amount=None, plus=None, only_price_subtotal=False):
        return True # TODO: either remove method or change logic. Prices below 1 must be included. I don't know what this logic is for
        
        if only_price_subtotal:
            if int(price_subtotal) == 0:
                return False
            else:
                return True
        brutto = None
        if plus:
            brutto = float(price_subtotal + (price_subtotal * tax_amount) / 100)
        else:
            brutto = float(price_subtotal + (price_subtotal * tax_amount) / 100)
        if int(brutto) == 0:
            return False
        else:
            return True

    def get_is_zamowienie(self):
        if self.state in ["draft", "sent", "cancel"]:
            return False
        else:
            return True

    def get_banks(self, currency_id):
        _logger.error("currency_id=%s", currency_id)
        search_banks = self.env["res.partner.bank"].search([("currency_id", "=", currency_id.id)])
        if search_banks:
            _logger.error("search_banks=%s", search_banks)
            return search_banks

    def get_int_or_float_qweb(self, float_m):
        value = math.modf(float_m)
        if abs(value[0]) > 0:
            return float_m
        else:
            return int(float_m)

    def _create_delivery_line(self, carrier, price_unit):
        res = super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
        res.write({
            "is_delivery": True
            })
        return res

    def get_delivery_in_order(self):
        mapped_data = self.order_line.filtered(lambda line: line.is_delivery == True)
        if mapped_data:
            mapped_data = mapped_data[0]
            return mapped_data.product_id.name
        else:
            return ""

    def is_vat_more_zero(self, str_m):
        number = re.sub(",", ".", str_m)
        number = re.findall(r"-[0-9.,]+|[0-9.,]+", number)
        _logger.error("number=%s", number)
        if float(number[0]) > 0.0:
            return True
        else:
            return False

    def is_discont(self, number):
        if number > 0.0:
            return True
        return False

    def get_price_netto(self, price_subtotal, product_uom_qty):
        _logger.error("price_subtotal=%s, product_uom_qty=%s", price_subtotal, product_uom_qty)
        if product_uom_qty == 0 or product_uom_qty == 0.0:
            return 0
        number = round((price_subtotal / product_uom_qty), 2)
        number = str(number).replace(".", ",")
        return number

    def is_tax_id_included_in_price(self, tax_id):
        return tax_id.price_include

        #if self.env.context.get('force_split_uom_id'):
       #     vals['product_uom'] = self.env.context['force_split_uom_id']
    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super()._create_invoices(grouped=grouped, final=final, date=date)
        _logger.error("RES=%s", res)
        delivered = self.env.context.get("delivered")
        _logger.error("delivered=%s", delivered)
        for move in res:
            move.advance_payment_method_delivered = delivered
        return res

class AccountMoveLine(models.Model):
    _inherit  = "account.move.line"

    line_down_payment = fields.Boolean(help="Technical field", default=False, store=True)

    def method_traceback(self):
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        _logger.error(''.join(stack_trace))

    @api.model_create_multi
    def create(self, vals_list):
        #self.method_traceback()
        _logger.error("self=%s, vals_list=%s", self, vals_list)
        for vals in vals_list:
            _logger.error("vals.get('product_id')=%s", vals.get("product_id"))
            if vals.get("product_id") == 11:
                vals["line_down_payment"] = True
        return super().create(vals_list)

class AccountMove(models.Model):
    _inherit = "account.move"

    type_show_bank = fields.Selection([
        ("one", "Only one bank"),
        ("profile", "Profile with banks"),
        ], string="Type bank for print")

    bank_account_id = fields.Many2one("res.partner.bank",
        string="Bank Account",
        domain="[('currency_id','=', currency_id)]")
    profile_id = fields.Many2one("profile.res.partner.bank", "Profile Banks")

    name_file_pro_forma = fields.Char(compute="_compute_name_file_pro_forma", help="Technical field")

    invoice_date = fields.Date(string="Invoice/Bill Date", readonly=True, index=True, copy=False,
        states={"draft": [("readonly", False)]}, required=True)

    advance_payment_method_delivered = fields.Boolean(help="Technical  field")

    @api.model_create_multi
    def create(self, vals_list):
        for invoice in vals_list:
            if invoice.get('currency_id'):
                currency = self.env["res.currency"].search([("id", "=", invoice.get('currency_id'))], limit=1)
                if currency:
                    invoice["type_show_bank"] = "one"
                    invoice["bank_account_id"] = currency.default_bank_id.id
            if not invoice.get('invoice_date'):
                invoice["invoice_date"] = fields.Date.today()
        return super().create(vals_list)

    def action_post(self):
        res = super(AccountMove, self).action_post()

        # Check taxes between invoice and related sale order
        for move in self:
            if move.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order:
                    # Ensure each invoice line matches a sale order line by product and tax
                    for invoice_line in move.invoice_line_ids.filtered(lambda l: not l.display_type):
                        corresponding_order_line = sale_order.order_line.filtered(
                            lambda l: l.product_id == invoice_line.product_id
                        )

                        if not corresponding_order_line:
                            raise UserError(_('The product %s in the invoice does not match any sale order line.')
                                            % invoice_line.product_id.display_name)

                        # Compare taxes on the corresponding sale order line and invoice line
                        invoice_taxes = invoice_line.tax_ids
                        order_taxes = corresponding_order_line.tax_id

                        if set(invoice_taxes.ids) != set(order_taxes.ids):
                            raise UserError(_('The taxes for product %s in the invoice has been changed!.')
                                            % invoice_line.product_id.display_name)

        return res

    def get_banks_invoice(self):
        zero = OrderedSet()
        if self.type_show_bank == "one":
            return self.bank_account_id
        if self.type_show_bank == "profile":
            return self.profile_id.bank_ids
        return zero


    def _compute_name_file_pro_forma(self):
        for move in self:
            sale_order = move.get_from_invoice_sale_order()
            move.name_file_pro_forma = "PRO-FORMA {}".format(move.name)
            if sale_order:
                move.name_file_pro_forma = "PRO-FORMA {}".format(sale_order.name)
            if move.state == "posted" and not move.advance_payment_method_delivered:
                move.name_file_pro_forma = "Faktura zaliczkowa VAT {}".format(move.name)
            if move.state == "posted" and move.advance_payment_method_delivered:
                move.name_file_pro_forma = "Faktura VAT {}".format(move.name)

    def get_from_invoice_sale_order(self):
        search_sale_order = self.env["sale.order"].search([("name", "=", self.invoice_origin)])
        if search_sale_order:
            return search_sale_order

    def get_price_netto(self, price_subtotal, product_uom_qty):
        _logger.error("price_subtotal=%s, product_uom_qty=%s", price_subtotal, product_uom_qty)
        if product_uom_qty == 0 or product_uom_qty == 0.0:
            return 0
        _logger.error("price_subtotal=%s, product_uom_qty=%s", price_subtotal, product_uom_qty)
        number = round((price_subtotal / product_uom_qty), 2)
        number = str(number).replace(".", ",")
        return number

    def get_price_netto_float(self, price_subtotal, product_uom_qty):
        _logger.error("price_subtotal=%s, product_uom_qty=%s", price_subtotal, product_uom_qty)
        if product_uom_qty == 0 or product_uom_qty == 0.0:
            return 0
        _logger.error("price_subtotal=%s, product_uom_qty=%s", price_subtotal, product_uom_qty)
        number = round((price_subtotal / product_uom_qty), 2)
        return number

    def get_order_line_can_be_printed(self):
        if self.product_id.detailed_type == "service":
            if self.product_uom_qty == 0:
                return False
        if self.is_delivery:
            return False
        return True

    def get_int_or_float_qweb(self, float_m):
        value = math.modf(float_m)
        if abs(value[0]) > 0:
            return float_m
        else:
            return int(float_m)

    def is_tax_id_included_in_price(self, tax_id):
        return tax_id.price_include

    def is_discont(self, number):
        if number > 0.0:
            return True
        return False

    def wartosc_brutto(self, price_subtotal, tax_amount, plus):
        price_subtotal_abs = abs(price_subtotal)
        _logger.error("price_subtotal_abs=%s, price_subtotal=%s, tax_amount=%s, plus=%s", price_subtotal_abs, price_subtotal, tax_amount, plus)
        if plus:
            if price_subtotal < 0:
                _logger.error("price_subtotal < 0")
                _logger.error(float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100) * -1)

                return float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100) * -1
            else:
                _logger.error("ELSE price_subtotal > 0")
                _logger.error(float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100))

                return float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100)
        else:
            if price_subtotal < 0:
                _logger.error("price_subtotal < 0")
                _logger.error(float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100) * -1)

                return float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100) * -1
            else:
                _logger.error("ELSE price_subtotal > 0")
                _logger.error(float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100))

                return float(price_subtotal_abs + (price_subtotal_abs * tax_amount) / 100)

    def check_can_print(self, price_subtotal, tax_amount=None, plus=None, only_price_subtotal=False):
        return True # TODO: either remove method or change logic. Prices below 1 must be included. I don't know what this logic is for

        if only_price_subtotal:
            if int(price_subtotal) == 0:
                return False
            else:
                return True
        brutto = self.wartosc_brutto(price_subtotal, tax_amount, plus)
        if int(brutto) == 0:
            return False
        else:
            return True

    def get_invoice_difference(self, org_line, line):
        org_wartosc_brutto = org_line.price_subtotal
        vat_percent = "0 %"
        if org_line.tax_ids and org_line.tax_ids.amount:
            if self.is_tax_id_included_in_price(org_line.tax_ids):
                org_wartosc_brutto = self.wartosc_brutto(org_line.price_subtotal, org_line.tax_ids.amount, False)
            else:
                org_wartosc_brutto = self.wartosc_brutto(org_line.price_subtotal, org_line.tax_ids.amount, True)

            if org_line.tax_ids.description:
                vat_percent = org_line.tax_ids.description
            else:
                vat_percent = ""

        wartosc_brutto = line.price_subtotal
        if line.tax_ids and line.tax_ids.amount:
            if self.is_tax_id_included_in_price(line.tax_ids):
                wartosc_brutto = self.wartosc_brutto(line.price_subtotal, line.tax_ids.amount, False)
            else:
                wartosc_brutto = self.wartosc_brutto(line.price_subtotal, line.tax_ids.amount, True)

        price_subtotal_diff = line.price_subtotal - org_line.price_subtotal
        wartosc_brutto_diff = wartosc_brutto - org_wartosc_brutto
        vat_diff = wartosc_brutto_diff - price_subtotal_diff

        return {
            "price_subtotal": price_subtotal_diff,
            "vat_percent" : vat_percent,
            "vat": vat_diff,
            "wartosc_brutto": wartosc_brutto_diff,
        }

    def get_invoice_line_info(self, line):
        wartosc_brutto = line.price_subtotal
        vat_percent = "0 %"
        if line.tax_ids and line.tax_ids.amount:
            if self.is_tax_id_included_in_price(line.tax_ids):
                wartosc_brutto = self.wartosc_brutto(line.price_subtotal, line.tax_ids.amount, False)
            else:
                wartosc_brutto = self.wartosc_brutto(line.price_subtotal, line.tax_ids.amount, True)

            if line.tax_ids.description:
                vat_percent = line.tax_ids.description
            else:
                vat_percent = ""

        return {
            "price_subtotal": line.price_subtotal,
            "vat_percent": vat_percent,
            "vat": wartosc_brutto - line.price_subtotal,
            "wartosc_brutto": wartosc_brutto,
        }

    def get_original_invoice_lines_map(self):
        self.ensure_one()
        if not self.reversed_entry_id:
            return {}

        original_lines = list(self.reversed_entry_id.invoice_line_ids)
        result = dict()
        for line in self.invoice_line_ids:
            found = False
            for org_line in original_lines:
                if org_line.product_id == line.product_id:
                    result[line.id] = [org_line, self.get_invoice_difference(org_line, line)]
                    original_lines.remove(org_line)
                    found = True
                    break
            if not found:
                result[line.id] = [None, self.get_invoice_line_info(line)]

        return result

    def group_correction_by_vat(self):
        """Groups invoice by vat % and returns sums of price_subtotal, vat, wartosc_brutoo."""
        grouped_vats = dict()
        correction_sum = {
            "price_subtotal": 0,
            "vat_percent": None,
            "vat": 0,
            "wartosc_brutto": 0,
        }
        for line in self.invoice_line_ids:
            line_res = self.get_invoice_line_info(line)

            vat_percent = line_res["vat_percent"]
            price_subtotal = -line_res["price_subtotal"]
            vat = -line_res["vat"]
            wartosc_brutto = -line_res["wartosc_brutto"]

            correction_sum["price_subtotal"] += price_subtotal
            correction_sum["vat"] += vat
            correction_sum["wartosc_brutto"] += wartosc_brutto

            if vat_percent not in grouped_vats:
                grouped_vats[vat_percent] = {
                    "price_subtotal": price_subtotal,
                    "vat": vat,
                    "vat_percent": vat_percent,
                    "wartosc_brutto": wartosc_brutto,
                }
                continue
            grouped_vats[vat_percent]["price_subtotal"] += price_subtotal
            grouped_vats[vat_percent]["vat"] += vat
            grouped_vats[vat_percent]["wartosc_brutto"] += wartosc_brutto

        return grouped_vats.values(), correction_sum
