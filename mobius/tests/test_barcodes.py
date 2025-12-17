#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo.tests import SavepointCase

# https://www.gs1.ch/en/home/offer/barcode/check-digit-calculator-and-ean-13-barcode-generator
# 2400000000013
# 2400000000020
# 2400000000037
# 2400000000044
# 2400000000051
# 2400000000068
# 2400000000075
# 2400000000082
# 2400000000099
# 2400000000105
#
# 2409999999988
# 2409999999995
#
# 2410000000005
# 2410000000012
# 2410000000029
# 2410000000036
# 2410000000043

class TestBarcodesGeneratorAbstract(SavepointCase):
    def init(self, pattern, number_next, existing_codes=None):
        barcode_seq = self.env["ir.sequence"].create({
            "name":             "mobius_sequence",
            "implementation":   "standard",
            "number_next":      number_next,
            "number_increment": 1,
        })
        self.env["barcode.rule"].create({
            "name":                    "Mobius",
            "barcode_nomenclature_id": self.env.ref("barcodes.default_barcode_nomenclature").id,
            "type":                    "product",
            "sequence":                999,
            "encoding":                "ean13",
            "pattern":                 pattern,
            "generate_type":           "sequence",
            "sequence_id":             barcode_seq.id,
        })
        for i, code in enumerate(existing_codes or []):
            self.env["product.product"].create({
                "name":           f"Test{i}",
                "barcode":        code,
            })

    def test_generate(self):
        self.init("240.........", 1)
        product = self.env["product.product"].create({
            "name": "Test",
        })

        product.generate_all()
        self.assertEqual(product.barcode, "2400000000013")

    def test_omit_duplicates(self):
        existing_codes = [
            "2400000000013",
            "2400000000020",
            "2400000000037",
            # empty
            "2400000000051",
            #empty ...
            "2410000000005",
            "2410000000012",
            "2410000000029",
            "2410000000036",
            "2410000000043",
        ]
        self.init("240.........", 2, existing_codes)
        product = self.env["product.product"].create({
            "name": "Test",
        })

        product.generate_all()
        self.assertEqual(product.barcode, "2400000000044")

        product.generate_all()
        self.assertEqual(product.barcode, "2400000000068")

        product.generate_all()
        self.assertEqual(product.barcode, "2400000000075")

    def test_increment_prefix(self):
        existing_codes = [
            "2409999999988",
            "2409999999995",
            "2410000000005",
            "2410000000012",
            "2410000000029",
        ]
        self.init("240.........", 999999998, existing_codes)
        product = self.env["product.product"].create({
            "name": "Test",
        })

        product.generate_all()
        self.assertEqual(product.barcode, "2410000000036")

        product.generate_all()
        self.assertEqual(product.barcode, "2410000000043")
