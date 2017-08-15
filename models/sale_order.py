# from odoo import models, fields, api
# from odoo.exceptions import ValidationError

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('user_id')
    def onchange_user_id(self):
        # partnerx = self.user_id.partner_id
        # raise ValidationError('patnerx')

        if not self.user_id:
            self.update(
                {
                    'team_id': False,
                    'warehouse_id': False,
                }
            )
            return

        values = {}
        values['team_id'] = self.user_id.sale_team_id.id
        values['warehouse_id'] = self.user_id.sale_team_id.warehouse_id.id
        self.update(values)

    @api.multi
    def check_limit(self):
        # raise UserError(_((self.env.user.id)))
        # self._cr.execute('''SELECT residual FROM ubw_get_total_credit''')
        self._cr.execute('''SELECT SUM(total) residual FROM ubw_credit_aging_report''')
        tc = self._cr.fetchone()
        today_dt = datetime.strftime(datetime.now().date(), DF)
        tdt = datetime.strptime(today_dt, '%Y-%m-%d')
        ##################################
        # Setting Credit Sales Threshold #
        ##################################
        red_line = 127000000.00
        # raise UserError(_((tc[0])))

        if (tc[0]) > red_line:
            # raise UserError(_(('x')))
            if self.env.user.id > 1:
                msg = 'Can Not Confirm Order, Current Residual Amount Is: %s As On %s...' % ('{0:,.2f}'.format(tc[0]) + '/=', tdt.strftime('%d-%b-%Y').upper())
                raise UserError(_('COMPANY\'s CREDIT LIMIT IS EXCEEDING !!!\n\n' + msg))
                # raise UserError(_((self.env.user.id)))

        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search([('partner_id', '=', partner.id), ('account_id.user_type_id.name', 'in', ['Receivable', 'Payable']), ('full_reconcile_id', '=', False)])

        debit, credit = 0.0, 0.0

        for line in movelines:
            # if line.date_maturity < today_dt:
            if line.date < today_dt:
                credit += line.debit
                debit += line.credit

        # raise UserError(_((credit - debit + self.amount_total)))
        if (credit - debit + self.amount_total) > partner.credit_limit:
            if self.env.user.id > 1:
                msg = 'Can Not Confirm Order, Current Residual Amount Is: %s As On %s...' % ('{0:,.2f}'.format((credit - debit)) + '/=', tdt.strftime('%d-%b-%Y').upper())
                raise UserError(_('CUSTOMER\'s CREDIT LIMIT IS EXCEEDING !!!\n\n' + msg))
        else:
            return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            # Calling the function for checking credit limit
            order.check_limit()

        return res
