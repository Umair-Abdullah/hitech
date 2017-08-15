# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockReport(models.TransientModel):
    _name = "ubw.wizard.stock.history"
    _description = "Stock History"

    warehouse = fields.Many2many('stock.warehouse', string='Warehouse', required=True)
    category = fields.Many2many('product.category', string='Category', required=True, domain=[('parent_id', '=', 4), ('child_id', '=', False)])
    # warehouse = fields.Many2many('stock.warehouse', 'wh_wiz_rel', 'wh', 'wiz', string='Warehouse', required=False)
    # category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Category', required=False, domain=[('child_id', '=', False)])
    # analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'product.product'
        datas['form'] = self.read()[0]

        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        if context.get('xls_export'):
            return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'xxx.stock_report_xls.xlsx',
                        'datas': datas,
                        'name': 'StockReport'
                   }
