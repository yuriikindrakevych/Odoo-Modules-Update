#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import _, exceptions, models

import barcode

class BarcodeGenerateMixin(models.AbstractModel):
    _name        = "barcode.generate.mixin.mobius"
    _description = "Generate Barcode Mixin"
    _inherit     = ["barcode.generate.mixin"]

    search_size = 500

    def _validate_barcode_unique(self, barcode_generated):
        items = self.env[self._name].search_read(["&", ("barcode", "=", barcode_generated), ("id", "!=", self.id)], fields=[])
        return not items

    @staticmethod
    def _extract_base(barcode_val):
        if not barcode_val or len(str(barcode_val)) != 13:
            raise exceptions.ValidationError(_("Invalid barcode format"))
        return int(str(barcode_val)[3:-1])

    def _get_max_base(self):
        pattern = str(self.barcode_rule_id.pattern)
        return 10 ** pattern.count(".") - 1

    def _get_prefix(self):
        pattern = str(self.barcode_rule_id.pattern)
        return pattern.split(".", maxsplit=1)[0]

    def _increment_prefix(self):
        pattern = str(self.barcode_rule_id.pattern)
        prefix  = self._get_prefix()
        pfx_len = len(prefix)
        rest    = pattern[pfx_len:]
        prefix  = int(prefix) + 1
        prefix  = f"{prefix:0{pfx_len}d}"
        self.barcode_rule_id.pattern = prefix + rest
        return prefix

    def _find_next_barcode_base(self, barcode_generated):
        prefix   = self._get_prefix()
        max_base = self._get_max_base()
        prev_barcode, prev_base = barcode_generated, self._extract_base(barcode_generated)
        model_name = self._name
        if model_name == "product.template":
            model_name = "product.product"

        while True:
            items = self.env[model_name].search_read(
                ["&", ("barcode", ">", prev_barcode), ("barcode", "like", prefix + "%")],
                fields=["barcode"],
                limit=self.search_size,
                order="barcode")
            items = list(filter(lambda item: len(str(item["barcode"])) == 13, items))

            for item in items:
                base = self._extract_base(item["barcode"])
                if base - prev_base > 1:
                    return self._move_seq_and_generate(prev_base + 1)
                prev_barcode, prev_base = item["barcode"], base

            if not items:
                if prev_base + 1 < max_base:
                    return self._move_seq_and_generate(prev_base + 1)
                prefix = self._increment_prefix()
                prev_base = 0

    def _generate_barcode_using_base(self):
        padding     = self.barcode_rule_id.padding
        str_base    = str(self.barcode_base).rjust(padding, "0")
        custom_code = self._get_custom_barcode(self)
        if custom_code:
            custom_code = custom_code.replace("." * padding, str_base)
            barcode_class = barcode.get_barcode_class(self.barcode_rule_id.encoding)
            barcode_generated = barcode_class(custom_code)
            if self._validate_barcode_unique(barcode_generated):
                # raise exceptions.ValidationError(_("The range of barcodes is full. Please switch the range").format())
                self.barcode = barcode_generated
                return
            self._find_next_barcode_base(barcode_generated)

    def _move_seq_and_generate(self, base):
        self.barcode_rule_id.sequence_id.number_next = base
        self._generate_step()

    def _set_rule(self):
        rules = self.env["barcode.rule"].search_read([("name", "=", "Mobius")], fields=["name"])
        if not rules:
            raise exceptions.ValidationError(_("Rule not found"))
        self.barcode_rule_id = rules[0]["id"]
        self.generate_type = self.barcode_rule_id.generate_type

    def generate_base(self):
        super().generate_base()
        if int(self.barcode_base) > self._get_max_base():
            self._increment_prefix()

    def _generate_step(self):
        self.generate_base()
        self.ensure_one()
        self._generate_barcode_using_base() # self.generate_barcode()

    def generate_all(self):
        self._set_rule()
        self._generate_step()
