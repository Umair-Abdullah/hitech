# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaifQuery(models.TransientModel):
    """Saif Query Report Wizard"""

    _name = 'saif.query'
    _description = 'Saif Query Report Wizard'

    date_start = fields.Date('Start Date', default=time.strftime('%Y-%m-01'), required=True)
    date_end = fields.Date('End Date', default=fields.Date.context_today, required=True)

    @api.multi
    def button_export_pdf(self):
        date_start = fields.Date.from_string(self.date_start)
        date_end = fields.Date.from_string(self.date_end)

        if date_start > date_end:
            raise ValidationError(_("End Date cannot be set before Start Date."))
        else:
            data = self.read(['date_start', 'date_end'])[0]
            return self.env['report'].get_action(self, 'xxx.report_saif_query', data=data)

    @api.multi
    def button_export_xls(self):
        self.ensure_one()
        return self._export(xlsx_report=True)
