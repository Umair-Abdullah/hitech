# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MasterSalesReport(models.TransientModel):
    """Master Sales Report Wizard"""

    _name = 'master.sales'
    _description = 'Master Sales Report Wizard'

    date_start = fields.Date('Start Date', default=time.strftime('%Y-%m-01'), required=True)
    date_end = fields.Date('End Date', default=fields.Date.context_today, required=True)
    category = fields.Many2one('product.category', 'Category', required=True, ondelete='cascade', domain=[('parent_id', '=', 4), ('child_id', '=', False)])

    @api.multi
    def button_export_pdf(self):
        date_start = fields.Date.from_string(self.date_start)
        date_end = fields.Date.from_string(self.date_end)

        if date_start > date_end:
            raise ValidationError(_("End Date cannot be set before Start Date."))
        else:
            data = self.read(['date_start', 'date_end', 'category'])[0]
            return self.env['report'].get_action(self, 'xxx.report_master_sales', data=data)
