# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CustomerLedgerReport(models.TransientModel):
    """Customer Ledger Report Wizard"""

    _name = 'customer.ledger'
    _description = 'Customer Ledger Report Wizard'

    date_start = fields.Date('Start Date', default=time.strftime('%Y-%m-01'), required=True)
    date_end = fields.Date('End Date', default=fields.Date.context_today, required=True)
    partner_ids = fields.Many2many('res.partner', string='Customer', required=True, domain=[('active', '=', True), ('customer', '=', True)])

    @api.multi
    def button_export_pdf(self):
        date_start = fields.Date.from_string(self.date_start)
        date_end = fields.Date.from_string(self.date_end)
        partner_ids = self.partner_ids

        if date_start > date_end:
            raise ValidationError(_("End Date cannot be set before Start Date."))
        else:
            data = self.read(['date_start', 'date_end', 'partner_ids'])[0]

        # raise ValidationError(_(data))

        return self.env['report'].get_action(self, 'xxx.report_customer_ledger', data=data)
