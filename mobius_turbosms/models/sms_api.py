# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, models
from odoo.addons.iap.tools import iap_tools
from odoo.addons.sms.models.sms_api import SmsApi as OriginalSmsApi

@api.model
def _send_sms_batch(self, messages):
    """ Send SMS using IAP in batch mode

    :param messages: list of SMS to send, structured as dict [{
        'res_id':  integer: ID of sms.sms,
        'number':  string: E164 formatted phone number,
        'content': string: content to send
    }]

    :return: return of /iap/sms/1/send controller which is a list of dict [{
        'res_id': integer: ID of sms.sms,
        'state':  string: 'insufficient_credit' or 'wrong_number_format' or 'success',
        'credit': integer: number of credits spent to send this SMS,
    }]

    :raises: normally none
    """
    turbosms = self.env["ir.config_parameter"].sudo().get_param("turbosms_enable")
    if turbosms:
        return self.env["crm.lead"]._sendTurboSMS_integration_odoo(messages)

    params = {
        'messages': messages
    }
    return self._contact_iap('/iap/sms/2/send', params)

OriginalSmsApi._send_sms_batch = _send_sms_batch
