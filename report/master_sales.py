# -*- coding: utf-8 -*-

import time
from odoo import models, api, _
from odoo.exceptions import ValidationError

class ReportMasterSales(models.AbstractModel):
    _name = "report.xxx.report_master_sales"

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
                sq.product_code,
                sq.product_name,
                sq.product_brand,
                sq.product_size,
                sq.product_type,
                sq.product_spec,
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
                    'product_code': i[9],
                    'product_name': i[10],
                    'product_brand': i[11],
                    'product_size': i[12],
                    'product_type': i[13],
                    'product_spec': i[14],
                    'product_category': i[15],
                    'price_unit': i[16],
                    'quantity': i[17],
                    'product_uom': i[18],
                    'discount': i[19],
                    'gross_val': i[20],
                    'net_val': i[21],
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
        return self.env['report'].render('xxx.report_master_sales', docargs)
