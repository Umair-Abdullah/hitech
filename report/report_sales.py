# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class SaleReportX(models.Model):
    _name = "ubw.sales.report"
    _description = "Sales Orders Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    invoice_number = fields.Char('Invoice Reference', readonly=True)
    date = fields.Date('Invoice Date', readonly=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Done'),
        ], string='Status', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Team', readonly=True, oldname='section_id')
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    city_id = fields.Many2one('res.partner.city', 'City', readonly=True)
    area_id = fields.Many2one('res.partner.area', 'Market', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    brand_id = fields.Many2one('ubw.product.brand', 'Product Brand', readonly=True)
    size_id = fields.Many2one('ubw.product.size', 'Product Size', readonly=True)
    type_id = fields.Many2one('ubw.product.type', 'Product Type', readonly=True)
    spec_id = fields.Many2one('ubw.product.spec', 'Product Specification', readonly=True)
    misc_id = fields.Many2one('ubw.product.misc', 'Product Miscellaneous', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    quantity = fields.Float('Qty', readonly=True)
    net_val = fields.Float('Net', readonly=True)

    @api.model_cr
    def init(self):
        # self._table = sale_report
        # tools.drop_view_if_exists(self._cr, self._table)
        tools.drop_view_if_exists(self._cr, 'ubw_sales_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW ubw_sales_report AS (
            SELECT
                MIN(x.id) id,
                x.invoice_number,
                x.date_invoice date,
                x.state,
                x.user_id,
                x.team_id,
                x.partner_id,
                x.city_id,
                x.area_id,
                x.product_id,
                x.brand_id,
                x.size_id,
                x.type_id,
                x.spec_id,
                x.misc_id,
                x.categ_id,
                x.quantity,
                x.net_val
            FROM
                (
                    SELECT
                        ai.id invoice_id,
                        ai.move_name invoice_number,
                        ai.date_invoice,
                        ai.state,
                        ai.user_id,
                        ai.team_id,
                        al.id,
                        al.partner_id,
                        rp.city_id,
                        rp.area_id,
                        al.product_id,
                        pp.brand_id,
                        pp.size_id,
                        pp.type_id,
                        pp.spec_id,
                        pp.misc_id,
                        pt.categ_id,
                        al.price_unit,
                        al.quantity,
                        al.uom_id,
                        al.price_subtotal net_val
                    FROM
                        account_invoice ai
                    INNER JOIN
                        account_invoice_line al
                    ON
                        ai.id = al.invoice_id
                    inner join
                        res_partner rp
                    on
                        rp.id = al.partner_id
                    inner join
                        product_product pp
                    on
                        pp.id = al.product_id
                    inner join
                        product_template pt
                    on
                        pt.id = pp.product_tmpl_id
                    WHERE
                        ai.type LIKE 'out_%'
                    AND
                        ai.amount_total > 0.0
                    AND
                        ai.state NOT IN ('draft', 'cancel', 'proforma', 'proforma2')
                    AND
                        ai.team_id <> 9
                    ORDER BY
                        ai.state
                ) x
            where
                x.quantity > 0.0
            GROUP BY
                x.invoice_number,
                x.date_invoice,
                x.state,
                x.user_id,
                x.team_id,
                x.partner_id,
                x.city_id,
                x.area_id,
                x.product_id,
                x.brand_id,
                x.size_id,
                x.type_id,
                x.spec_id,
                x.misc_id,
                x.categ_id,
                x.quantity,
                x.net_val
        )""")
