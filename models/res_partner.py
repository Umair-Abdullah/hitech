from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'
    supplier_id = fields.Many2many('ubw.wizard.stock.history', 'supp_wiz_rel', 'wiz', 'supp', invisible=True)

class Category(models.Model):
    _inherit = 'product.category'
    obj = fields.Many2many('ubw.wizard.stock.history', 'categ_wiz_rel', 'wiz', 'categ', invisible=True)

class Warehouse(models.Model):
    _inherit = 'stock.warehouse'
    obj = fields.Many2many('ubw.wizard.stock.history',  'wh_wiz_rel', 'wiz', 'wh', invisible=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    area_id = fields.Many2one('res.partner.area', 'Area', required=False)
    city_id = fields.Many2one('res.partner.city', 'City', required=False)

    @api.onchange('area_id')
    def onchange_area_id(self):
        if not self.area_id:
            self.update(
                {
                    'city_id': False,
                }
            )
            return

        values = {}
        values['city_id'] = self.area_id.city_id.id
        self.update(values)
