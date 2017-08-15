from odoo import models, fields, api

class ProductX(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('ubw.product.brand', 'Brand', required=False)
    size_id = fields.Many2one('ubw.product.size', 'Size', required=False)
    type_id = fields.Many2one('ubw.product.type', 'Type', required=False)
    spec_id = fields.Many2one('ubw.product.spec', 'Specification', required=False)
    misc_id = fields.Many2one('ubw.product.misc', 'Miscellaneous', required=False)
    min_qty = fields.Float('Min. Qty', digits=0, store=True)
    max_qty = fields.Float('Max. Qty', digits=0, store=True)
