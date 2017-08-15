# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartnerCity(models.Model):
    _name = 'res.partner.city'
    _description = __doc__
    _order = 'name asc'

    name = fields.Char('Name', required = True)
    code = fields.Char('Code', size = 15, required = True)

class ResPartnerArea(models.Model):
    _name = 'res.partner.area'
    _description = __doc__
    _order = 'name asc'

    name = fields.Char('Name', required = True)
    code = fields.Char('Code', size = 15, required = True)
    city_id = fields.Many2one('res.partner.city', 'City', required = True)
