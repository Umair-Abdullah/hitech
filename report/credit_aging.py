# -*- coding: utf-8 -*-

import time
from odoo import models, api, _
from odoo.exceptions import ValidationError

class ReportCreditAging(models.AbstractModel):
    _name = "report.xxx.report_credit_aging"

    def get_data(self, data):
        lst = []

        if data['allx']:
            allx = 'True'

        if not data['allx']:
            allx = 'False'

        if allx == 'False':
            # raise ValidationError(_(data['allx']))
            self._cr.execute('''
                SELECT
                    ca.partner_id,
                    ca.partner_name,
                    ca.partner_code,
                    (SELECT credit_limit FROM res_partner where id = ca.partner_id) limitx,
                    ca.user_id,
                    ca.user_name,
                    ca.team_id,
                    ca.team_name,
                    ca.city_id,
                    ca.city_name,
                    (SELECT area_id FROM res_partner WHERE id = ca.partner_id) area_id,
                    (SELECT name FROM res_partner_area WHERE id = (SELECT area_id FROM res_partner WHERE id = ca.partner_id)) area_name,
                    ca.d0130,
                    ca.d3160,
                    ca.d6190,
                    ca.d91120,
                    ca.d120plus,
                    ca.total
                FROM
                    ubw_credit_aging_report ca
                WHERE
                    ca.user_id = ANY(%s)
                ORDER BY
                    ca.team_id,
                    ca.city_id,
                    ca.user_id,
                    ca.partner_id
            ''', ((data['user_ids']),))

        if allx == 'True':
            # raise ValidationError(_(data['allx']))
            self._cr.execute('''
                SELECT
                    ca.partner_id,
                    ca.partner_name,
                    ca.partner_code,
                    (SELECT credit_limit FROM res_partner where id = ca.partner_id) limitx,
                    ca.user_id,
                    ca.user_name,
                    ca.team_id,
                    ca.team_name,
                    ca.city_id,
                    ca.city_name,
                    (SELECT area_id FROM res_partner WHERE id = ca.partner_id) area_id,
                    (SELECT name FROM res_partner_area WHERE id = (SELECT area_id FROM res_partner WHERE id = ca.partner_id)) area_name,
                    ca.d0130,
                    ca.d3160,
                    ca.d6190,
                    ca.d91120,
                    ca.d120plus,
                    ca.total
                FROM
                    ubw_credit_aging_report ca
                ORDER BY
                    ca.team_id,
                    ca.city_id,
                    ca.user_id,
                    ca.partner_id
            ''')

        ca = self._cr.fetchall()
        # raise ValidationError(_(sq))

        res = {}

        if ca:
            for i in ca:
                res = {
                    'partner_id': i[0],
                    'partner_name': i[1],
                    'partner_code': i[2],
                    'limitx': i[3],
                    'user_id': i[4],
                    'user_name': i[5],
                    'team_id': i[6],
                    'team_name': i[7],
                    'city_id': i[8],
                    'city_name': i[9],
                    'area_id': i[10],
                    'area_name': i[11],
                    'd0130': i[12],
                    'd3160': i[13],
                    'd6190': i[14],
                    'd91120': i[15],
                    'd120plus': i[16],
                    'total': i[17],
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
            'get_data': self.get_data(data),
        }

        if data['allx']:
            allx = 'True'

        if not data['allx']:
            allx = 'False'

        # raise ValidationError(_(allx))
        if allx == 'True':
            # raise ValidationError(_(allx))
            return self.env['report'].render('xxx.report_credit_agingx', docargs)

        if allx == 'False':
            # raise ValidationError(_(allx))
            return self.env['report'].render('xxx.report_credit_aging', docargs)
