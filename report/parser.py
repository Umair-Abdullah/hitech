from odoo.addons import jasper_reports
from odoo import models, api, _
from odoo.exceptions import ValidationError
# from odoo import pooler
# from datetime import date
# from dateutil.rrule import rrule, MONTHLY
# from dateutil.relativedelta import relativedelta
# from datetime import datetime
# from openerp.osv import fields,osv
# import string
# import mx.DateTime

#-------- Master Sales Report --------#
@api.v7
def report_master_sales(cr, uid, ids, data, context):
    date_start = data['form']['date_start']
    date_end   = data['form']['date_end']

    print 'date1:' , date_start
    print 'date2:' , date_end

    return {
        'parameters': {
            'date_start': date_start,
            'date_end'  : date_end,
        },
   }

jasper_reports.ReportJasper('report.master_sales_report', 'account.invoice', parser=report_master_sales)
