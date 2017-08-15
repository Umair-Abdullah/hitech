from odoo import models, fields, api

class SalesTeamX(models.Model):
    _inherit = 'crm.team'

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=False)
