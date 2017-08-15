# -*- coding: utf-8 -*-
{
    'name': "UBW",

    'summary': """
        Odoo Extension Module for UBW
    """,

    'description': """
        Customized Development by UBW-IT
    """,

    'author': "Aamir Riaz",
    'website': "http://www.unibrush.com",

    'category': 'Custom',
    'version': '0.1',

    'depends': [
                'base',
                'mail',
                'product',
                'stock',
                'sales_team',
                'sale',
                'purchase',
                'report_xlsx',
                'report',
                # 'jasper_reports',
               ],

    'data': [
        'data/gp_data.xml',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'views/views.xml',
        'views/ra_view.xml',
        'views/product_view.xml',
        'views/sales_team_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner_area_view.xml',
        'views/res_partner_view.xml',
        'views/templates.xml',
        'views/stock_report_wizard_view.xml',
        'views/saif_query_wizard_view.xml',
        'views/master_sales_report_wizard_view.xml',
        'views/credit_aging_report_wizard_view.xml',
        'views/customer_ledger_report_wizard_view.xml',
        'report/gp_report_menu.xml',
        'report/report_gp_inward.xml',
        'report/report_gp_outward.xml',
        'report/report_purchase_request.xml',
        'report/report_journal_voucher.xml',
        'report/report_partner_list.xml',
        'report/report_sales_view.xml',
        'report/layouts.xml',
        'report/report_saif_query.xml',
        'report/report_master_sales.xml',
        'report/report_credit_aging.xml',
        'report/report_credit_agingx.xml',
        'report/report_customer_ledger.xml',
        'report/sales_report_menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
