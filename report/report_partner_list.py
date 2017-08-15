# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists


class ReportPartnerList(models.Model):
    _name = 'report.partner.list'
    _description = 'Partner List'
    _auto = False

    partner_id = fields.Many2one('res.partner', 'Customer')
    user_id = fields.Many2one('res.users', 'Salesperson')

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'report_partner_list')
        self._cr.execute("""
                CREATE OR REPLACE VIEW report_partner_list AS 
                (
                    SELECT 
                        id,
                        id AS partner_id,
                        user_id
                    FROM 
                        res_partner
                    WHERE 
                        active = True
                    AND
                        customer = True
                    
                )""")


