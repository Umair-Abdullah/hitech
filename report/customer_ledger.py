# -*- coding: utf-8 -*-

import time
import datetime
from odoo import models, api, _
from odoo.exceptions import ValidationError

class ReportCustomerLedger(models.AbstractModel):
    _name = "report.xxx.report_customer_ledger"

    def get_data(self, data):
        lst = []
        ds = datetime.datetime.strptime(data['date_start'], '%Y-%m-%d')
        od = ds - datetime.timedelta(days=1)
        od = datetime.datetime.strftime(od, '%Y-%m-%d')
        # raise ValidationError(_(do))

        self._cr.execute('''
            SELECT
                LPAD(ROW_NUMBER() OVER (ORDER BY p.move_id)::text, 3, '0') sn,
                p.account_name,
                --p.move_id,
                p.move_date,
                p.move_name,
                p.move_ref,
                p.narration,
                p.partner,
                p.debit,
                p.credit,
                p.balance
            FROM
            (
                SELECT
                    t.account_name,
                    t.move_id,
                    t.move_date,
                    t.move_name,
                    t.move_ref,
                    t.narration,
                    t.partner,
                    CASE
                        WHEN
                            t.move_id <> 1
                        THEN
                            t.debit
                        ELSE
                            0.0
                    END debit,
                    CASE
                        WHEN
                            t.move_id <> 1
                        THEN
                            t.credit
                        ELSE
                            0.0
                    END credit,
                    CASE
                        WHEN
                            t.move_id <> 1
                        THEN
                            SUM(t.debit - t.credit) OVER (partition by t.partner ORDER BY move_date, t.move_id) --balance
                        ELSE
                            SUM(t.debit - t.credit)
                    END balance
                FROM
                (
                    SELECT
                        'Initial Balance' account_name,
                        1 move_id,
                        %s move_date,
                        '' move_name,
                        '' move_ref,
                        '' narration,
                        rp.name partner,
                        COALESCE
                        (
                            CASE
                                WHEN
                                    SUM(aml.debit - aml.credit) > 0
                                THEN
                                    ROUND(SUM(aml.debit - aml.credit), 2)
                                ELSE
                                    0.0
                            END
                            , 0
                        ) debit,
                        COALESCE
                        (
                            CASE
                                WHEN
                                    SUM(aml.credit - aml.debit) > 0
                                THEN
                                    ROUND(SUM(aml.credit - aml.debit), 2)
                                ELSE
                                    0.0
                            END
                            , 0
                        ) credit,
                        0.0 balance
                    FROM
                        account_account aa
                    INNER JOIN
                        account_move_line aml
                    ON
                        aa.id = aml.account_id
                    INNER JOIN
                        account_move am
                    ON
                        aml.move_id = am.id
                    INNER JOIN
                        res_partner rp
                    ON
                        aml.partner_id = rp.id
                    WHERE
                        aml.date < %s
                    AND
                        aa.internal_type = 'receivable'
                    AND
                        rp.id = ANY(%s)
                    GROUP BY
                        rp.name
                    -------------------
                    UNION
                    -------------------
                    SELECT
                        aa.code account_name,
                        aml.id move_id,
                        aml.date move_date,
                        am.name move_name,
                        am.ref move_ref,
                        am.narration,
                        rp.name partner,
                        CASE
                            WHEN
                                SUM(aml.debit - aml.credit) > 0
                            THEN
                                ROUND(SUM(aml.debit - aml.credit), 2)
                            ELSE
                                0.0
                        END debit,
                        CASE
                            WHEN
                                SUM(aml.credit - aml.debit) > 0
                            THEN
                                ROUND(SUM(aml.credit - aml.debit), 2)
                            ELSE
                                0.0
                        END credit,
                        0.0 balance
                    FROM
                        account_account aa
                    INNER JOIN
                        account_move_line aml
                    ON
                        aa.id = aml.account_id
                    INNER JOIN
                        account_move am
                    ON
                        aml.move_id = am.id
                    LEFT OUTER JOIN
                        res_partner rp
                    ON
                        aml.partner_id = rp.id
                    WHERE
                        aml.date >= %s
                    AND
                        aml.date <= %s
                    AND
                        aa.internal_type = 'receivable'
                    AND
                        rp.id = ANY(%s)
                    GROUP BY
                        am.name,
                        am.ref,
                        am.narration,
                        rp.name,
                        aa.id,
                        aml.id,
                        aml.date
                ) t
                GROUP BY
                    t.account_name,
                    t.move_id,
                    t.move_date,
                    t.move_name,
                    t.move_ref,
                    t.narration,
                    t.partner,
                    t.debit,
                    t.credit
                ORDER BY
                    t.move_date,
                    t.move_id
            ) p
            ORDER BY
                p.move_date,
                p.move_id

        ''', (od, (data['date_start']), (data['partner_ids']), (data['date_start']), (data['date_end']), (data['partner_ids']),))
        # ''', ((data['partner_ids']),))
        # TO_DATE('2016-12-31', 'YYYY-MM-DD')

        ca = self._cr.fetchall()
        # raise ValidationError(_(sq))

        res = {}

        if ca:
            for i in ca:
                res = {
                    'sn': i[0],
                    'account_name': i[1],
                    'move_date': i[2],
                    'move_name': i[3],
                    'move_ref': i[4],
                    'narration': i[5],
                    'partner': i[6],
                    'debit': i[7],
                    'credit': i[8],
                    'balance': i[9],
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
            'pid': data['partner_ids'],
            'get_data': self.get_data(data),
        }
        return self.env['report'].render('xxx.report_customer_ledger', docargs)
