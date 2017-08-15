# -*- coding: utf-8 -*-

import time
from odoo import models, api, _
from odoo.exceptions import ValidationError

class ReportSaifQuery(models.AbstractModel):
    _name = "report.xxx.report_saif_query"

    # invoice_number = fields.Char('Invoice Reference', readonly=True)
    # date = fields.Date('Invoice Date', readonly=True)
    # state = fields.Selection([
    #     ('open', 'Open'),
    #     ('paid', 'Done'),
    #     ], string='Status', readonly=True)
    # user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    # team_id = fields.Many2one('crm.team', 'Sales Team', readonly=True, oldname='section_id')
    # partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    # product_id = fields.Many2one('product.product', 'Product', readonly=True)
    # categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    # quantity = fields.Float('Qty', readonly=True)
    # net_val = fields.Float('Net', readonly=True)

    def get_data(self, data):
        lst = []

        self._cr.execute('''
            SELECT
                sq.invoice_number,
                sq.date,
                sq.state,
                sq.order_number,
                sq.date_order,
                sq.date_order_confirm,
                sq.sales_person,
                sq.team_name,
                sq.customer_name,
                sq.city_name,
                sq.area_name,
                sq.product_code,
                sq.product_name,
                sq.product_brand,
                sq.product_size,
                sq.product_type,
                sq.product_spec,
                sq.product_misc,
                sq.product_category,
                sq.price_unit,
                sq.quantity,
                sq.product_uom,
                sq.discount,
                sq.gross_val,
                sq.net_val
            FROM
                ubw_saif_query_report AS sq
            WHERE
                sq.date >= %s
            AND
                sq.date <= %s
        ''', ((data['date_start']), (data['date_end']),))

        sq = self._cr.fetchall()
        # raise ValidationError(_(sq))

        res = {}

        if sq:
            print 'sq:', sq

            for i in sq:
                res = {
                    'invoice_number': i[0],
                    'date': i[1],
                    'state': i[2],
                    'order_number': i[3],
                    'date_order': i[4],
                    'date_order_confirm': i[5],
                    'sales_person': i[6],
                    'team_name': i[7],
                    'customer_name': i[8],
                    'city_name': i[9],
                    'area_name': i[10],
                    'product_code': i[11],
                    'product_name': i[12],
                    'product_brand': i[13],
                    'product_size': i[14],
                    'product_type': i[15],
                    'product_spec': i[16],
                    'product_misc': i[17],
                    'product_category': i[18],
                    'price_unit': i[19],
                    'quantity': i[20],
                    'product_uom': i[21],
                    'discount': i[22],
                    'gross_val': i[23],
                    'net_val': i[24],
                }

                lst.append(res)

        return lst

    @api.model
    def render_html(self, docids, data=None):
        # raise ValidationError(_(data['date_start']))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'data': data,
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'get_data': self.get_data(data),
        }
        return self.env['report'].render('xxx.report_saif_query', docargs)

    # @api.model_cr
    # def init(self):
    #     # self._table = sale_report
    #     # tools.drop_view_if_exists(self._cr, self._table)
    #     tools.drop_view_if_exists(self._cr, 'ubw_saif_query_report')
    #     self._cr.execute("""
    #         CREATE OR REPLACE VIEW ubw_saif_query_report AS (
    #         SELECT
    #             MIN(x.id) AS id,
    #             x.invoice_number,
    #             x.date_invoice AS date,
    #             x.state,
    #             x.user_id,
    #             x.team_id,
    #             x.partner_id,
    #             x.product_id,
    #             x.categ_id,
    #             x.quantity,
    #             x.net_val
    #         FROM
    #             (
    #                 SELECT
    #                     ai.id AS invoice_id,
    #                     ai.move_name AS invoice_number,
    #                     ai.date_invoice,
    #                     ai.state,
    #                     ai.user_id,
    #                     ai.team_id,
    #                     al.id,
    #                     al.partner_id,
    #                     al.product_id,
    #                     (SELECT categ_id FROM product_template WHERE id = (SELECT product_tmpl_id FROM product_product WHERE id = al.product_id)) AS categ_id,
    #                     al.price_unit,
    #                     al.quantity,
    #                     al.uom_id,
    #                     al.price_subtotal AS net_val
    #                 FROM
    #                     account_invoice AS ai
    #                 INNER JOIN
    #                     account_invoice_line AS al
    #                 ON
    #                     ai.id = al.invoice_id
    #                 WHERE
    #                     ai.type LIKE 'out_%'
    #                 AND
    #                     ai.amount_total > 0.0
    #                 AND
    #                     ai.state NOT IN ('draft', 'cancel', 'proforma', 'proforma2')
    #                 AND
    #                     ai.team_id <> 9
    #                 ORDER BY
    #                     ai.state
    #             ) AS x
    #         where
    #             x.quantity > 0.0
    #         GROUP BY
    #             x.invoice_number,
    #             x.date_invoice,
    #             x.state,
    #             x.user_id,
    #             x.team_id,
    #             x.partner_id,
    #             x.product_id,
    #             x.categ_id,
    #             x.quantity,
    #             x.net_val
    #     )""")
