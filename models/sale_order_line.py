from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    islocked = fields.Boolean('Locked', default=True)

    # @api.multi
    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     vals = {}
    #
    #     if self.product_id:
    #         vals['discount'] = self.product_id.discount
    #         # raise UserError(_((self.product_id.discount)))
    #
    #     self.update(vals)


    @api.onchange('discount')
    def onchange_discount(self):
        if self.discount > self.product_id.discount:
            self.update(
                {
                    'discount': 0.0,
                }
            )
            return

        #     raise ValidationError(_((self.product_id.discount)))
        #
        # if not (self.discount > -1 and self.discount < 40):
        #     raise UserError(_(('Discount should be > -1 AND < 40')))
