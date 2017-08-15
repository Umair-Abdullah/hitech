# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

class ProductX(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('ubw.product.brand', 'Brand', required=False)
    size_id = fields.Many2one('ubw.product.size', 'Size', required=False)
    type_id = fields.Many2one('ubw.product.type', 'Type', required=False)
    spec_id = fields.Many2one('ubw.product.spec', 'Specification', required=False)
    misc_id = fields.Many2one('ubw.product.misc', 'Miscellaneous', required=False)
    min_qty = fields.Float('Min. Qty', digits=0, store=True)
    max_qty = fields.Float('Max. Qty', digits=0, store=True)
    discount = fields.Float('Discount (%)', digits=0, store=True)

    @api.onchange('discount')
    def onchange_discount(self):
        if not (self.discount > -1 and self.discount <= 40):
            self.update(
                {
                    'discount': 0.0,
                }
            )
            return
