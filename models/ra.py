# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

#-------------------------------------------------------------------------------
# Product Brand
#-------------------------------------------------------------------------------
class ubw_product_brand(models.Model):
    _name = 'ubw.product.brand'
    _description = 'Product Brand'
    _order = 'name'

    name = fields.Char(required = True)
    code = fields.Char('Code', size = 10, required = True)
    active = fields.Boolean('Active', default = True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _("Brand name already exists !")),
    ]

#-------------------------------------------------------------------------------
# Product Size
#-------------------------------------------------------------------------------
class ubw_product_size(models.Model):
    _name = 'ubw.product.size'
    _description = 'Product Size'
    _order = 'name'

    name = fields.Char(required = True)
    code = fields.Char('Code', size = 10, required = True)
    active = fields.Boolean('Active', default = True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _("Size name already exists !")),
    ]

#-------------------------------------------------------------------------------
# Product Type
#-------------------------------------------------------------------------------
class ubw_product_type(models.Model):
    _name = 'ubw.product.type'
    _description = 'Product Type'
    _order = 'name'

    name = fields.Char(required = True)
    code = fields.Char('Code', size = 10, required = True)
    active = fields.Boolean('Active', default = True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _("Type name already exists !")),
    ]

#-------------------------------------------------------------------------------
# Product Specification
#-------------------------------------------------------------------------------
class ubw_product_spec(models.Model):
    _name = 'ubw.product.spec'
    _description = 'Product Specification'
    _order = 'name'

    name = fields.Char(required = True)
    code = fields.Char('Code', size = 10, required = True)
    active = fields.Boolean('Active', default = True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _("Specification name already exists !")),
    ]

#-------------------------------------------------------------------------------
# Product Misc.
#-------------------------------------------------------------------------------
class ubw_product_misc(models.Model):
    _name = 'ubw.product.misc'
    _description = 'Product Miscellaneous Attributes'
    _order = 'name'

    name = fields.Char(required = True)
    code = fields.Char('Code', size = 10, required = True)
    active = fields.Boolean('Active', default = True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _("Miscellaneous Attribute name already exists !")),
    ]
