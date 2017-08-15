# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CreditAgingReport(models.TransientModel):
    """Credit Aging Report Wizard"""

    _name = 'credit.aging'
    _description = 'Credit Aging Report Wizard'

    user_ids = fields.Many2many('res.users', string='Salesperson', required=False, domain=[('sale_team_id', '!=', False)])
#    user_ids = fields.Many2many('res.users', string='Salesperson', required=False)
    allx = fields.Boolean('All Customers', default=False)

    @api.onchange('allx')
    def onchange_allx(self):
        self.user_ids = None
        return {}

    @api.multi
    def button_export_pdf(self):
        user_ids = self.user_ids
        allx = self.allx
        data = self.read(['user_ids','allx'])[0]
        # raise ValidationError(_(data))

        return self.env['report'].get_action(self, 'xxx.report_credit_aging', data=data)
        # if not data['allx']:
        #     return self.env['report'].get_action(self, 'xxx.report_credit_aging', data=data)
        # else:
        #     return self.env['report'].get_action(self, 'xxx.report_credit_agingx', data=data)
