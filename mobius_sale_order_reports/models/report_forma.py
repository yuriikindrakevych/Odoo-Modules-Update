from odoo import api, models, _
from odoo.exceptions import UserError


class ReportFormaDetails(models.AbstractModel):
    _name = "report.mobius_sale_order_reports.sale_order_pro_forma"
    _description = "Forma Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        sessions = self.env['account.move'].browse(docids)
        message = _("Printing is not possible, specify the bank!")
        for session in sessions:
            if not session.type_show_bank:
                raise UserError(message)

            if session.type_show_bank == "one":
                if not session.bank_account_id:
                    raise UserError(message)
            elif not session.profile_id:
                raise UserError(message)

            if session.move_type in ('out_refund', 'in_refund'):
                reversed_entry = session.reversed_entry_id
                if not reversed_entry:
                    raise UserError(_("Original invoice from credit note not found."))
                positive_product_id_counts = dict()
                for line in session.invoice_line_ids:
                    if line.product_id.id not in positive_product_id_counts:
                        positive_product_id_counts[line.product_id.id] = 1
                    else:
                        positive_product_id_counts[line.product_id.id] += 1

                positive_reversed_product_id_counts = dict()
                for line in reversed_entry.invoice_line_ids:
                    if line.product_id.id not in positive_product_id_counts:
                        continue
                    if line.product_id.id not in positive_reversed_product_id_counts:
                        positive_reversed_product_id_counts[line.product_id.id] = 1
                    else:
                        positive_reversed_product_id_counts[line.product_id.id] += 1

                for key in positive_reversed_product_id_counts:
                    if positive_reversed_product_id_counts[key] == positive_product_id_counts[key]:
                        continue

                    raise UserError(
                        _("Discrepancy found in product quantities between the credit note line "
                          "and the original invoice line. "
                          "Please verify the product list in both documents."))

        return {
            'doc_ids': docids,
            'doc_model': self.env['account.move'],
            'data': data,
            'docs': sessions,
        }


class ReportFormaEngDetails(models.AbstractModel):
    _name = "report.mobius_sale_order_reports.sale_order_pro_forma_en"
    _description = "Forma Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        sessions = self.env['account.move'].browse(docids)
        message = _("Printing is not possible, specify the bank!")
        for session in sessions:
            if not session.type_show_bank:
                raise UserError(message)

            if session.type_show_bank == "one":
                if not session.bank_account_id:
                    raise UserError(message)
            elif not session.profile_id:
                raise UserError(message)

        if session.move_type in ('out_refund', 'in_refund'):
            reversed_entry = session.reversed_entry_id
            if not reversed_entry:
                raise UserError(_("Original invoice from credit note not found."))
            positive_product_id_counts = dict()
            for line in session.invoice_line_ids:
                if line.product_id.id not in positive_product_id_counts:
                    positive_product_id_counts[line.product_id.id] = 1
                else:
                    positive_product_id_counts[line.product_id.id] += 1

            positive_reversed_product_id_counts = dict()
            for line in reversed_entry.invoice_line_ids:
                if line.product_id.id not in positive_product_id_counts:
                    continue
                if line.product_id.id not in positive_reversed_product_id_counts:
                    positive_reversed_product_id_counts[line.product_id.id] = 1
                else:
                    positive_reversed_product_id_counts[line.product_id.id] += 1

            for key in positive_reversed_product_id_counts:
                if positive_reversed_product_id_counts[key] == positive_product_id_counts[key]:
                    continue

                raise UserError(
                    _("Discrepancy found in product quantities between the credit note line "
                      "and the original invoice line. "
                      "Please verify the product list in both documents."))

        return {
            'doc_ids': docids,
            'doc_model': self.env['account.move'],
            'data': data,
            'docs': sessions,
        }
