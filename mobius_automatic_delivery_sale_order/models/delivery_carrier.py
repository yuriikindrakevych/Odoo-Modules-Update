#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError, ValidationError
from itertools import chain

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    base_delivery = fields.Boolean("Base Delivery")

    @api.constrains("base_delivery")
    def _check_base_delivery(self):
        checked_bool = self.search([("base_delivery", "=", True)])
        if len(checked_bool) > 1:
            raise ValidationError(_("Only one delivery can be used like base"))

    def _match_address(self, partner):
        res = super()._match_address(partner)
        _logger.info('Method _match_address res: %s', res)
        return res

    def fixed_rate_shipment(self, order):
        res = super().fixed_rate_shipment(order)
        _logger.info('Method fixed_rate_shipment res: %s', res)
        return res

    def rate_shipment(self, order):
        res = super().rate_shipment(order)
        _logger.info('Method rate_shipment res: %s', res)
        return res

class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        Date in context can be a date, datetime, ...

            :param products_qty_partner: list of tuples products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        _logger.info(
            f"Starting price rule computation with {len(products_qty_partner)} product-quantity-partner entries")

        self.ensure_one()

        try:
            if not date:
                date = self._context.get('date') or fields.Datetime.now()
                _logger.info(f"Date set to: {date}")

            if not uom_id and self._context.get('uom'):
                uom_id = self._context['uom']
                _logger.info(f"UoM ID set from context: {uom_id}")

            if uom_id:
                # rebrowse with uom if given
                products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
                products_qty_partner = [(products[index], data_struct[1], data_struct[2])
                                        for index, data_struct in enumerate(products_qty_partner)]
                _logger.info(f"Rebrowsed {len(products)} products with specified UoM")
            else:
                products = [item[0] for item in products_qty_partner]
                _logger.info("No UoM specified, using default product UoM")

            if not products:
                _logger.warning("No products provided for price rule computation")
                return {}

            # Collect all category IDs, including parent categories
            categ_ids = {}
            for p in products:
                categ = p.categ_id
                while categ:
                    categ_ids[categ.id] = True
                    categ = categ.parent_id
            categ_ids = list(categ_ids)
            _logger.info(f"Collected {len(categ_ids)} unique category IDs")

            is_product_template = products[0]._name == "product.template"
            if is_product_template:
                prod_tmpl_ids = [tmpl.id for tmpl in products]
                # all variants of all products
                prod_ids = [p.id for p in
                            list(chain.from_iterable([t.product_variant_ids for t in products]))]
                _logger.info(f"Processing product templates: {len(prod_tmpl_ids)} templates, {len(prod_ids)} variants")
            else:
                prod_ids = [product.id for product in products]
                prod_tmpl_ids = [product.product_tmpl_id.id for product in products]
                _logger.info(f"Processing product variants: {len(prod_ids)} products")

            items = self._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids,
                                                       categ_ids)
            _logger.info(f"Retrieved {len(items)} : {items} pricing rule items")

            results = {}
            for product, qty, partner in products_qty_partner:
                results[product.id] = 0.0
                suitable_rule = False

                # Quantity UoM handling
                qty_uom_id = self._context.get('uom') or product.uom_id.id
                qty_in_product_uom = qty
                if qty_uom_id != product.uom_id.id:
                    try:
                        qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty,
                                                                                                                  product.uom_id)
                        _logger.info(
                            f"Converted quantity from {qty_uom_id} to {product.uom_id.id}: {qty} -> {qty_in_product_uom}")
                    except UserError:
                        _logger.warning(f"Could not convert quantity for product {product.id}. Using default UoM.")
                        pass

                # Initial price computation
                price = product.price_compute('list_price')[product.id]
                _logger.info(f"Initial price for product {product.id}: {price}")

                price_uom = self.env['uom.uom'].browse([qty_uom_id])

                for rule in items:
                    if not rule._is_applicable_for(product, qty_in_product_uom):
                        _logger.info(f"Rule {rule.id} not applicable for product {product.id}")
                        continue

                    if rule.base == 'pricelist' and rule.base_pricelist_id:
                        price = \
                        rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][
                            0]
                        src_currency = rule.base_pricelist_id.currency_id
                        _logger.info(f"Using base pricelist {rule.base_pricelist_id.id}, new price: {price}")
                    else:
                        price = product.price_compute(rule.base)[product.id]
                        if rule.base == 'standard_price':
                            src_currency = product.cost_currency_id
                        else:
                            src_currency = product.currency_id
                        _logger.info(f"Using base {rule.base}, price: {price}")

                    if src_currency != self.currency_id:
                        price = src_currency._convert(
                            price, self.currency_id, self.env.company, date, round=False)
                        _logger.info(
                            f"Currency conversion: {src_currency.name} -> {self.currency_id.name}, price: {price}")

                    if price is not False:

                        price = rule._compute_price(price, price_uom, product, quantity=qty, partner=partner)
                        suitable_rule = rule
                        _logger.info(f"Found suitable rule {rule.id}, final price: {price}")
                        break

                if not suitable_rule:
                    cur = product.currency_id
                    price = cur._convert(price, self.currency_id, self.env.company, date, round=False)
                    _logger.warning(f"No suitable rule found for product {product.id}, default conversion applied")

                results[product.id] = (price, suitable_rule and suitable_rule.id or False)
                _logger.info(
                    f"Final result for product {product.id}: price={price}, rule={suitable_rule and suitable_rule.id or 'None'}")

            _logger.info(f"Price rule computation completed. Processed {len(results)} products")
            return results

        except Exception as e:
            _logger.error(f"Error in price rule computation: {str(e)}", exc_info=True)
            raise

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        """Compute the unit price of a product in the context of a pricelist application.
           The unused parameters are there to make the full context available for overrides.
        """
        _logger.info(f"Starting price computation for product {product.id}")
        _logger.info(f"Initial parameters: price={price}, price_uom={price_uom}, quantity={quantity}")

        try:
            self.ensure_one()

            # Logging conversion function
            def convert_to_price_uom(price):
                converted_price = product.uom_id._compute_price(price, price_uom)
                _logger.info(f"Price conversion: {price} -> {converted_price}")
                return converted_price

            # Logging initial conditions and price computation method
            _logger.info(f"Price computation method: {self.compute_price}")

            # Fixed price computation
            if self.compute_price == 'fixed':
                _logger.info(f"Using fixed price: {self.fixed_price}")
                price = convert_to_price_uom(self.fixed_price)
                _logger.info(f"Converted fixed price: {price}")

            # Percentage price computation
            elif self.compute_price == 'percentage':
                _logger.info(f"Applying percentage discount: {self.percent_price}%")
                original_price = price
                price = (price - (price * (self.percent_price / 100))) or 0.0
                _logger.info(f"Percentage price change: {original_price} -> {price}")

            # Complete formula price computation
            else:
                _logger.info("Using complete price computation formula")
                price_limit = price
                _logger.info(f"Initial price limit: {price_limit}")

                # Price discount
                original_price = price
                price = (price - (price * (self.price_discount / 100))) or 0.0
                _logger.info(f"Price after discount: {original_price} -> {price}")

                # Price rounding
                if self.price_round:
                    _logger.info(f"Applying price rounding: {self.price_round}")
                    price = tools.float_round(price, precision_rounding=self.price_round)
                    _logger.info(f"Rounded price: {price}")

                # Price surcharge
                if self.price_surcharge:
                    surcharge = convert_to_price_uom(self.price_surcharge)
                    _logger.info(f"Applying price surcharge: {self.price_surcharge}")
                    price += surcharge
                    _logger.info(f"Price after surcharge: {price}")

                # Minimum margin
                if self.price_min_margin:
                    price_min_margin = convert_to_price_uom(self.price_min_margin)
                    _logger.info(f"Applying minimum margin: {self.price_min_margin}")
                    price = max(price, price_limit + price_min_margin)
                    _logger.info(f"Price after minimum margin: {price}")

                # Maximum margin
                if self.price_max_margin:
                    price_max_margin = convert_to_price_uom(self.price_max_margin)
                    _logger.info(f"Applying maximum margin: {self.price_max_margin}")
                    price = min(price, price_limit + price_max_margin)
                    _logger.info(f"Price after maximum margin: {price}")

            _logger.info(f"Final computed price: {price}")
            return price

        except Exception as e:
            _logger.error(f"Error in price computation: {str(e)}", exc_info=True)
            raise