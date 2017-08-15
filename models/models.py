# -*- coding: utf-8 -*-

import time
# from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError

#-------------------------------------------------------------------------------
# GatePass Tags
#-------------------------------------------------------------------------------
class ubw_gp_tags(models.Model):
    _name = 'ubw.gp.tags'
    _description = 'GatePass Tags'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer('Color')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _("Tag name already exists !")),
    ]

#-------------------------------------------------------------------------------
# GatePass Inward
#-------------------------------------------------------------------------------
class ubw_gp_inward(models.Model):
    _name = 'ubw.gp.inward'
    # _inherit = ['mail.thread']
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _description = 'GatePass Inward'

    @api.model
    def _get_default_tag_id(self):
        tag_id = self.env['ubw.gp.tags'].search([('name', '=', 'Inward')], limit=1)

        return tag_id

    name = fields.Char('GatePass', size=50, readonly=True, default='New')
    date = fields.Date('Date', readonly=True, default=fields.Date.context_today)
    tag_ids = fields.Many2many('ubw.gp.tags', string='Tags', default=_get_default_tag_id, domain=[('name', '=', 'Inward')], required=True, states={'inchecking': [('readonly', True)], 'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', 'Partner / Party', required=True,
                                domain=['|', ('employee', '=', True),('supplier', '=', True)],
                                ondelete='cascade', states={'inchecking': [('readonly', True)], 'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'User', readonly=True, default=lambda self: self.env.uid)
    src_location_id = fields.Many2one('stock.location', 'From', domain=[('usage', '!=', 'view')], ondelete='cascade', states={'inchecking': [('readonly', True)], 'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    dest_location_id = fields.Many2one('stock.location', 'To', domain=[('usage', '!=', 'view')], ondelete='cascade', states={'inchecking': [('readonly', True)], 'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    shipment_id = fields.Many2one('stock.picking', 'Incoming Shipment',
                                ondelete='cascade', states={'inchecking': [('readonly', True)], 'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    # shipment_id = fields.Many2one('stock.picking', 'Incoming Shipment',
    #                             domain=[('name', 'like', '%IN%'),('state', 'in', ('confirmed','assigned'))],
    #                             ondelete='cascade', states={'inchecking': [('readonly', True)], 'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    inward_gp_line = fields.One2many('ubw.gp.inward.line', 'gp_id', string='Lines', states={'inchecking': [('readonly', True)], 'cancelled': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    note = fields.Text('Notes', states={'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('inchecking', 'In-Checking'),
                              ('cancelled', 'Cancelled'),
                              ('done', 'Done')],
                              'Status', default='draft')

    @api.multi
    def unlink(self):
        if self.filtered(lambda x: x.state not in ('xxx')):
            raise UserError(_('Cannot delete !'))
        return super(ubw_gp_inward, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('ubw.gp.inward') or '/'

        return super(ubw_gp_inward, self).create(vals)

    # @api.one
    # def send_mail_to_client(self):
    #     ir_model_data = self.env['ir.model.data']
    #     email_tmp_obj = self.env['mail.template']
    #
    #     context = self._context.copy()
    #     context['base_url'] = self.env['ir.config_parameter'].get_param('web.base.url')
    #     # Obtain the accion for the related object to mail
    #     context['action_id'] = ir_model_data.get_object_reference('xxx', 'email_template_ubw_gp_inward')[1]
    #     # Obtain Id template
    #     template_id = ir_model_data.get_object_reference('xxx', 'email_template_ubw_gp_inward')[1]
    #     mail = email_tmp_obj.with_context(context)
    #     self.pool.get('mail.template').send_mail(self._cr, self._uid, template_id, self.id, force_send=True, context=context)
    #     return True

    @api.onchange('dest_location_id')
    def onchange_dest_location_id(self):
        if self.dest_location_id and self.src_location_id:
            if self.dest_location_id == self.src_location_id:
                raise UserError(_('Locations cannot be the same !'))

    @api.multi
    def send_mail_template(self):
        # Find the e-mail template
        template = self.env.ref('xxx.email_template_ubw_gp_inward')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.one
    def action_inchecking(self):
        if not self.inward_gp_line:
            raise UserError(_('Where are the Lines ?'))

        # if self.env.context.get('send_email'):
        #     raise UserError(_('I am here...'))

        # self.send_mail_to_client()
        self.write({'state': 'inchecking'})
        # self.send_mail_template()

    @api.one
    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.one
    def action_done(self):
        self.write({'state': 'done'})

    @api.multi
    def action_print(self):
        return self.env['report'].get_action(self, 'xxx.report_gp_inward')

    @api.onchange('shipment_id')
    def onchange_shipment_id(self):
        if not self.partner_id:
            self.shipment_id = None

        return {}

    @api.multi
    def action_get_shipment_lines(self):
        if self.shipment_id:
            self._cr.execute('''
                DELETE FROM ubw_gp_inward_line WHERE gp_id = %s
            ''', (self.id,))

            self._cr.execute('''
                SELECT
                    sm.picking_id,
                    sm.product_id,
                    sm.ordered_qty,
                    (SELECT name FROM product_uom WHERE id = sm.product_uom) product_uom
                FROM
                    stock_move sm
                WHERE
                    sm.picking_id = %s
            ''', ((self.shipment_id.id),))

            res = self._cr.fetchall()

            if res:
                print 'res:', res

                for i in res:
                    self._cr.execute('''
                        INSERT INTO ubw_gp_inward_line
                        (create_uid, create_date, gp_id, shipment_id, product_id, ordered_qty, product_qty, product_uom)
                        VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s)
                    ''', (self.env.uid, self.id, i[0], i[1], i[2], i[2], i[3]))
        else:
            raise UserError(_('The requested operation cannot be processed because of Incoming-Shipment is not selected, you can also make it by manual entry if there is no Incoming-Shipment available or not required.'))

#-------------------------------------------------------------------------------
# GatePass Inward Line
#-------------------------------------------------------------------------------
class ubw_gp_inward_line(models.Model):
    _name = 'ubw.gp.inward.line'
    _description = 'GatePass Inward Line'

    gp_id = fields.Many2one('ubw.gp.inward', string='Reference', required=False, ondelete='cascade', index=True, copy=False)
    shipment_id = fields.Many2one('stock.picking', 'Shipment', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Item/Material', domain=[('type', 'in', ['product', 'consu'])], index=True, required=False)
    use_alternate = fields.Boolean('Use Alternate', default=False)
    product_text = fields.Char('Alternate Product', size=50, readonly=False)
    product_uom = fields.Char(related='product_id.uom_id.name', string='UOM', store=True, readonly=True)
    product_uom_text = fields.Char('Alternate UOM', size=10, readonly=False)
    ordered_qty = fields.Float('Ordered Qty', digits=0, store=True, readonly=True)
    product_qty = fields.Float('Real Qty', digits=0, store=True)

    @api.multi
    def write(self, values):
        values = self._get_uom(values)

        return super(ubw_gp_inward_line, self).write(values)

    def _get_uom(self, values):
        values = dict(values or {})

        if not values.get('shipment_id'):
            values['ordered_qty'] = 0.0

        return values

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id
        self.product_uom = product.uom_id.id
        self.ordered_qty = 0.0
        self.product_qty = 1.0

        return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}

    @api.onchange('use_alternate')
    def onchange_use_alternate(self):
        if self.use_alternate:
            self.product_id = None
        else:
            self.product_text = None

        return {}

#-------------------------------------------------------------------------------
# GatePass Outward
#-------------------------------------------------------------------------------
class ubw_gp_outward(models.Model):
    _name = 'ubw.gp.outward'
    # _inherit = ['mail.thread']
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'GatePass Outward'

    @api.model
    def _get_default_tag_id(self):
        tag_id = self.env['ubw.gp.tags'].search([('name', '=', 'Outward')], limit=1)

        return tag_id

    name = fields.Char('GatePass', size=50, readonly=True, default='New')
    date = fields.Date('Date', readonly=True, default=fields.Date.context_today)
    return_date = fields.Date('Expected Return Date', readonly=False, default=fields.Date.context_today, states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    actual_return_date = fields.Datetime('Actual Return Date', readonly=True)
    tag_ids = fields.Many2many('ubw.gp.tags', string='Tags', default=_get_default_tag_id, domain=[('name', '!=', 'Inward')], required=True, states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', 'Partner / Party',
                                domain=['|', ('employee', '=', True), ('customer', '=', True)],
                                ondelete='cascade', states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'User', readonly=True, default=lambda self: self.env.uid)
    manager_id = fields.Many2one('res.users', 'Approved By', readonly=True)
    src_location_id = fields.Many2one('stock.location', 'From', required=True, domain=[('usage', '!=', 'view')], ondelete='cascade', states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    dest_location_id = fields.Many2one('stock.location', 'To', required=True, domain=[(('usage', '!=', 'view'))], ondelete='cascade', states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    shipment_id = fields.Many2one('stock.picking', 'Outgoing Shipment',
                                ondelete='cascade', states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    consolidate = fields.Boolean('Consolidate', default=False, states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    returnable = fields.Boolean('Returnable', default=False)
    flagx = fields.Boolean('Flag', default=False)
    outward_gp_line = fields.One2many('ubw.gp.outward.line', 'gp_id', string='Lines', copy=True, states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    outward_gp_print = fields.One2many('ubw.gp.outward.print', 'gp_id', string='Lines', copy=True)
    note = fields.Text('Notes', states={'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit'),
                              ('cancelled', 'Cancelled'),
                              ('approved', 'Approved'),
                              ('done', 'Done')],
                              'Status', default='draft', readonly=True, copy=False, index=True, track_visibility='onchange')

    @api.onchange('returnable')
    def onchange_returnable(self):
        self.return_date = None
        self.actual_return_date = None

        return {}

    @api.onchange('consolidate')
    def onchange_consolidate(self):
        self.partner_id = None
        self.flagx = False

        if self.consolidate:
            for x in self.outward_gp_line:
                x.consolidate = True
        else:
            for x in self.outward_gp_line:
                x.consolidate = False

        return {}

    @api.onchange('tag_ids')
    def onchange_tag_ids(self):
        for x in self.tag_ids:
            if x.name == 'Returnable':
                self.returnable = True
            else:
                self.returnable = False

        return {}

    @api.onchange('dest_location_id')
    def onchange_dest_location_id(self):
        if self.dest_location_id and self.src_location_id:
            if self.dest_location_id == self.src_location_id:
                raise UserError(_('Locations cannot be the same !'))

    @api.multi
    def unlink(self):
        if self.filtered(lambda x: x.state not in ('xxx')):
            raise UserError(_('Cannot delete !'))
        return super(ubw_gp_outward, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('ubw.gp.outward') or '/'

        return super(ubw_gp_outward, self).create(vals)

#    @api.multi
#    def write(self, values):
#        if self.state == 'submit':
#            values['actual_return_date'] = time.strftime("%c")

#        return super(ubw_gp_outward, self).write(values)

    @api.multi
    def action_print(self):
        self._cr.execute('''
            SELECT COALESCE(COUNT(id), 0) FROM ubw_gp_outward_print WHERE gp_id = %s
        ''', ((self.id),))

        gpcnt = self._cr.fetchone()

        if gpcnt:
            if gpcnt[0] == 0:
                self._cr.execute('''
                    INSERT INTO ubw_gp_outward_print
                    (create_uid, create_date, gp_id, name)
                    VALUES (%s, NOW(), %s, %s)
                ''', (self.env.uid, self.id, 'Copy 1'))
            else:
                x = 0
                x = gpcnt[0]
                x += 1
                # raise UserError(x)
                self._cr.execute('''
                    INSERT INTO ubw_gp_outward_print
                    (create_uid, create_date, gp_id, name)
                    VALUES (%s, NOW(), %s, %s)
                ''', (self.env.uid, self.id, 'Copy ' + str(x)))

                # self._cr.execute('''
                #     UPDATE ubw_gp_outward_print
                #     SET name =  %s
                #     WHERE gp_id = %s
                # ''', ('Copy ' + str(x), self.id, ))

        return self.env['report'].get_action(self, 'xxx.report_gp_outward')

    @api.one
    def action_submit(self):
        if not self.outward_gp_line:
            raise UserError(_('Where are the Lines ?'))

        self.write({'state': 'submit'})

    @api.one
    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.one
    def action_approve(self):
        self.write({'manager_id': self.env.uid})
        self.write({'state': 'approved'})

    @api.one
    def action_done(self):
        if self.returnable:
            print 'Returnable:', self.returnable
            self.write({'actual_return_date': time.strftime("%c")})

        self.write({'state': 'done'})

    @api.onchange('shipment_id')
    def onchange_shipment_id(self):
        if (not self.consolidate) and (not self.partner_id):
            self.shipment_id = None

        return {}

    @api.multi
    def action_get_shipment_lines(self):
        if self.src_location_id.id == self.dest_location_id.id:
            raise UserError(_('Source & Destination Locations cannot be same!'))

        if self.shipment_id:
            self._cr.execute('''
                SELECT COUNT(id) FROM ubw_gp_outward_line WHERE shipment_id = %s
            ''', (self.shipment_id.id,))

            shipment = self._cr.fetchone()

            # if shipment:
            #     if shipment[0] > 0:
            #         raise UserError(_('This shipment/delivery is already used.'))

            self._cr.execute('''
                SELECT
                    sm.picking_id,
                    sm.product_id,
                    sm.ordered_qty,
                    sm.partner_id,
                    (SELECT name FROM product_uom WHERE id = sm.product_uom) product_uom
                FROM
                    stock_move sm
                WHERE
                    sm.picking_id = %s
            ''', ((self.shipment_id.id),))

            res = self._cr.fetchall()

            if res:
                print 'res:', res

                for i in res:
                    # raise UserError(_(sm.partner_id))
                    self._cr.execute('''
                        INSERT INTO ubw_gp_outward_line
                        (create_uid, create_date, gp_id, shipment_id, product_id, ordered_qty, product_qty, partner_id, product_uom, consolidate)
                        VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (self.env.uid, self.id, i[0], i[1], i[2], i[2], i[3], i[4], self.consolidate, ))

            print 'self.consolidate:', self.consolidate

            if not self.consolidate:
                self.flagx = True
        else:
            raise UserError(_('The requested operation cannot be processed because of Incoming-Shipment is not selected, you can also make it by manual entry if there is no Incoming-Shipment available or not required.'))

#-------------------------------------------------------------------------------
# GatePass Outward Line
#-------------------------------------------------------------------------------
class ubw_gp_outward_line(models.Model):
    _name = 'ubw.gp.outward.line'
    _description = 'GatePass Outward Line'

    gp_id = fields.Many2one('ubw.gp.outward', string='Reference', required=False, ondelete='cascade', index=True, copy=False)
    shipment_id = fields.Many2one('stock.picking', 'Shipment', ondelete='cascade')
    consolidate = fields.Boolean('Consolidate', copy=True)
    product_id = fields.Many2one('product.product', 'Item/Material', domain=[('type', 'in', ['product', 'consu'])], index=True, required=False)
    use_alternate = fields.Boolean('Use Alternate', default=False)
    product_text = fields.Char('Alternate', size=50, readonly=False)
    product_uom = fields.Char(related='product_id.uom_id.name', string='UOM', store=True, readonly=True)
    ordered_qty = fields.Float('Ordered Qty', digits=0, store=True, readonly=True)
    # readonlytest = fields.Boolean('R/O Test', default=True)
    product_qty = fields.Float('Real Qty', digits=0, store=True)
    partner_id = fields.Many2one('res.partner', 'Partner / Party', required=False,
                                domain=['|', ('employee', '=', True),('customer', '=', True)],
                                ondelete='cascade')
    no_of_bag = fields.Integer(string='No. of Bag(s)', default=0)
    qty_per_bag = fields.Integer(string='Qty Per Bag', default=0)
    no_of_carton = fields.Integer(string='No. of Carton(s)', default=0)
    carton_number = fields.Char('Carton Number', size=25)

    @api.multi
    def write(self, values):
        values = self._get_uom(values)

        return super(ubw_gp_outward_line, self).write(values)

    def _get_uom(self, values):
        values = dict(values or {})

#        if not values.get('shipment_id'):
#            if not self.shipment_id:
#                values['ordered_qty'] = 0.0

        return values

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id
        self.product_uom = product.uom_id.id
        self.ordered_qty = 0.0
        self.product_qty = 1.0

        return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}

    @api.onchange('use_alternate')
    def onchange_use_alternate(self):
        self.product_id = None
        self.product_text = None

        return {}

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        print 'self.ordered_qty:', self.ordered_qty
        if self.ordered_qty > 0.0:
            if self.product_qty > self.ordered_qty:
                raise UserError(_('Qty is exceeding...!'))


#-------------------------------------------------------------------------------
# GatePass Outward Print
#-------------------------------------------------------------------------------
class ubw_gp_outward_print(models.Model):
    _name = 'ubw.gp.outward.print'
    _description = 'GatePass Outward Print'

    gp_id = fields.Many2one('ubw.gp.outward', string='Reference', required=False, ondelete='cascade', index=True, copy=False)
    name = fields.Char('Name', size=50, readonly=True)

#-------------------------------------------------------------------------------
# Purchase Request
#-------------------------------------------------------------------------------
class ubw_pr_master(models.Model):
    _name = 'ubw.pr.master'
    _inherit = ['mail.thread']
    _description = 'Purchase Request'

    name = fields.Char('Name', size=50, readonly=True, default='New')
    date_request = fields.Date('Request Date', readonly=True, default=fields.Date.context_today)
    date_required = fields.Date('Required Date', readonly=True, default=fields.Date.context_today)
    date_submit = fields.Datetime('Submit Date', readonly=True)
    date_approve = fields.Datetime('Approve Date', readonly=True)
    date_done = fields.Datetime('Done Date', readonly=True)
    user_id_1 = fields.Many2one('res.users', 'User', readonly=True, default=lambda self: self.env.uid)
    partner_id = fields.Many2one('res.partner', 'Request For', required=True,
                                domain=[('employee', '=', True)],
                                ondelete='cascade',
                                states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    user_id_2 = fields.Many2one('res.users', 'Approved By', readonly=True)
    dest_location_id = fields.Many2one('stock.location', 'Destination Location',
                                domain=[('location_id', '!=', False)],
                                ondelete='cascade',
                                states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})
    note = fields.Text('Notes', states={'cancelled': [('readonly', True)], 'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit'),
                              ('cancelled', 'Cancelled'),
                              ('approved', 'Approved'),
                              ('done', 'Done')],
                              'Status', default='draft', readonly=True, copy=False, index=True, track_visibility='onchange')
    purchase_request_line = fields.One2many('ubw.pr.line', 'pr_id',
                                string='Lines',
                                copy=True,
                                states={'cancelled': [('readonly', True)], 'submit': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]})

    @api.multi
    def unlink(self):
        if self.filtered(lambda x: x.state not in ('xxx')):
            raise UserError(_('Cannot delete !'))
        return super(ubw_pr_master, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('ubw.purchase.request') or '/'

        return super(ubw_pr_master, self).create(vals)

    @api.one
    def action_submit(self):
        if not self.purchase_request_line:
            raise UserError(_('Where are the Lines ?'))

        self.write({'date_submit': time.strftime("%c")})
        self.write({'state': 'submit'})

    @api.one
    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.one
    def action_approve(self):
        self.write({'user_id_2': self.env.uid})
        self.write({'date_approve': time.strftime("%c")})
        self.write({'state': 'approved'})

    @api.one
    def action_done(self):
        self.write({'date_done': time.strftime("%c")})
        self.write({'state': 'done'})

    @api.multi
    def action_print(self):
        return self.env['report'].get_action(self, 'xxx.report_purchase_request')

#-------------------------------------------------------------------------------
# Purchase Request Line
#-------------------------------------------------------------------------------
class ubw_pr_line(models.Model):
    _name = 'ubw.pr.line'
    _description = 'Purchase Request Line'

    pr_id = fields.Many2one('ubw.pr.master', string='Reference', required=False, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', 'Item/Material', domain=[('type', 'in', ['product', 'consu'])], index=True, required=True)
    product_uom = fields.Char(related='product_id.uom_id.name', string='UOM', store=True, readonly=True)
    product_qty = fields.Float('Required Qty', digits=0, store=True)

    @api.multi
    def write(self, values):
        values = self._get_uom(values)

        return super(ubw_pr_line, self).write(values)

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id
        self.product_uom = product.uom_id.id
        self.product_qty = 1.0

        return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}

#-------------------------------------------------------------------------------
# GatePass Email Setup
#-------------------------------------------------------------------------------
class ubw_gp_email_setup(models.Model):
    _name = 'ubw.gp.email.setup'
    _description = 'GatePass Email setup'

    name = fields.Char('Email Title', size=50, required=True)
    email_address = fields.Char('Email Address', size=50, required=True)
    inward = fields.Boolean('Inward', default=True)
    outward = fields.Boolean('Outward', default=True)
