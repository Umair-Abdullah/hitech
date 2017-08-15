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

    # @api.multi
    # def _get_display_price(self, product):
    #     if self.order_id.pricelist_id.discount_policy == 'with_discount':
    #         return product.with_context(pricelist=self.order_id.pricelist_id.id).price
    #
    #     price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
    #     pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
    #
    #     if (pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'with_discount'):
    #         price, rule_id = pricelist_item.base_pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
    #         return price

    @api.multi
    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            itemx = self.env['product.pricelist.item'].browse(vals.get('product_id'))
            # listx = self.env['product.pricelist.item'].browse(vals.get(itemx.pricelist_id[0]))
            pricex = self.env['product.pricelist.item'].search([('product_id', '=', itemx.id)])
            # pricex = pricex.order_id.id
            # raise UserError(_((pricex.fixed_price)))
            # price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            # pricelist_item = self.env['product.pricelist.item'].browse(rule_id)

            # if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = pricex.fixed_price

            self.update(vals)

            # raise UserError(_((vals.get('product_id').pricelist_id.price_unit)))
            # vals.update({'price_unit': self.env['product.product'].browse(vals.get('product_id')).price_unit})

            # self.update(
            #     {
            #         'price_unit': self.price_unit,
            #     }
            # )

        return super(SaleOrderLine, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     if vals.get('product_id'):
    #         vals.update({'discount': self.env['product.product'].browse(vals.get('partner_id')).discount})
    #     return super(SaleOrderLine, self).create(vals)

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
