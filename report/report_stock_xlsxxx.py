from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
#import datetime
#import pytz
from datetime import datetime
from dateutil import tz
from odoo import api, _
from odoo.exceptions import ValidationError

class StockReportXls(ReportXlsx):
    #
    def get_warehouse(self, data):
        if data.get('form', False) and data['form'].get('warehouse', False):
            l1 = []
            l2 = []
            obj = self.env['stock.warehouse'].search([('id', 'in', data['form']['warehouse'])])

            for j in obj:
                l1.append(j.name)
                l2.append(j.id)

        return l1, l2

    def get_category(self, data):
        if data.get('form', False) and data['form'].get('category', False):
            l2 = []
            obj = self.env['product.category'].search([('id', 'in', data['form']['category'])])

            for j in obj:
                l2.append(j.id)
            return l2

        return ''

    def get_lines(self, data, warehouse):
        lines = []
        categ = self.get_category(data)

        if categ:
            stock_history = self.env['product.product'].search([('categ_id', 'in', categ), ('default_code', '!=', '')])
        else:
            stock_history = self.env['product.product'].search([('default_code', '!=', '')])

        for obj in stock_history:
            sale_value = 0
            purchase_value = 0
            product = self.env['product.product'].browse(obj.id)
            sale_obj = self.env['sale.order.line'].search([('order_id.state', '=', 'done'),
                                                           ('product_id', '=', product.id),
                                                           ('order_id.warehouse_id', '=', warehouse)])
            for i in sale_obj:
                sale_value = sale_value + i.product_uom_qty

            purchase_obj = self.env['purchase.order.line'].search([('order_id.state', '=', 'done'),
                                                                   ('product_id', '=', product.id),
                                                                   ('order_id.picking_type_id', '=', warehouse)])
            for i in purchase_obj:
                purchase_value = purchase_value + i.product_qty

            available_qty = product.with_context({'warehouse': warehouse}).virtual_available + \
                            product.with_context({'warehouse': warehouse}).outgoing_qty - \
                            product.with_context({'warehouse': warehouse}).incoming_qty

            value = available_qty * product.standard_price

            for p in product:
                variant = ''
                min_qty = 0
                max_qty = 0

                sop = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', p.id), ('warehouse_id', '=', warehouse)])

                for item in p.attribute_value_ids:
                    # print 'item:', item.attribute_id

                    if item.attribute_id.id <> 1:
                        variant += ', ' + item.name
                        # raise ValidationError(_(p.name))

#                    variant += (' - ' + str(item.attribute_id.name) + ' : ' + item.name + ';\n')

                namex = variant and "%s %s" % (p.name, '[' + variant[2:] + ']') or p.name

                for o in sop:
                    min_qty += o.product_min_qty
                    max_qty += o.product_max_qty

                # pending = self.env['sale.order.line'].search([('product_id', '=', p.id), ('order_id.warehouse_id', '=', warehouse)])
                #
                # for o in pending:
                #     print o.q

            vals = {
                'sku': product.default_code,
                'name': namex,
                # 'name': product.name,
                'category': product.categ_id.name,
                'cost_price': product.standard_price,
                'min_qty': min_qty,
                'max_qty': max_qty,
                'available': available_qty,
                'virtual': product.with_context({'warehouse': warehouse}).virtual_available,
                'incoming': product.with_context({'warehouse': warehouse}).incoming_qty,
                'outgoing': product.with_context({'warehouse': warehouse}).outgoing_qty,
                'net_on_hand': product.with_context({'warehouse': warehouse}).qty_available,
                'total_value': value,
                'sale_value': sale_value,
                'purchase_value': purchase_value,
            }
            lines.append(vals)

        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        get_warehouse = self.get_warehouse(data)
        count = len(get_warehouse[0]) * 8 + 8
        sheet = workbook.add_worksheet("xxx")
        # raise ValidationError(_(sheet))

        format0 = workbook.add_format({'font_size': 16, 'bottom': False, 'right': False, 'left': False, 'top': False, 'align': 'vcenter', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'right': True, 'left': True, 'bottom': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'right': True, 'left': True,'bottom': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'align': 'vcenter', 'font_size': 12})

        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'align': 'vcenter', 'font_size': 9})
        font_size_8.set_num_format('#,##0')
        font_size_8r = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'align': 'vcenter', 'font_size': 9})
        font_size_8x = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'align': 'vcenter', 'font_size': 9})
        font_size_8x.set_num_format('#,##0.00')

        red_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 9, 'align': 'vcenter', 'bg_color': 'ff3333'})
        red_mark.set_num_format('#,##0')
        blue_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 9, 'align': 'vcenter', 'bg_color': '6666ff'})
        blue_mark.set_num_format('#,##0')
        green_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 9, 'align': 'vcenter', 'bg_color': '99ff66'})
        green_mark.set_num_format('#,##0')
        yellow_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 9, 'align': 'vcenter', 'bg_color': 'ffff99'})
        yellow_mark.set_num_format('#,##0')
        justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'align': 'vcenter', 'font_size': 12})

        format3.set_align('center')
        font_size_8.set_align('center')
        font_size_8r.set_align('left')
        font_size_8x.set_align('center')
        justify.set_align('justify')
        format0.set_align('center')
        format1.set_align('center')
        format11.set_align('center')
        format21.set_align('center')
        red_mark.set_align('center')
        blue_mark.set_align('center')
        green_mark.set_align('center')
        yellow_mark.set_align('center')

        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Asia/Karachi')
        utc = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        utc = datetime.strptime(utc, '%Y-%m-%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        pkt = utc.astimezone(to_zone)
        dt = pkt.replace(tzinfo=None)

        sheet.merge_range(0, 0, 1, count, 'Stock Report', format0)
        sheet.merge_range('A3:I3', 'Report Date: ' + str(dt), format1)
#        sheet.merge_range('A3:G3', 'Report Date: ' + str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M")), format1)
        sheet.merge_range(2, 9, 2, count, 'Warehouses', format1)
        sheet.merge_range('A4:I4', 'Product Information', format11)
        w_col_no = 8
        w_col_no1 = 9

        for i in get_warehouse[0]:
            w_col_no = w_col_no + 8
            sheet.merge_range(3, w_col_no1, 3, w_col_no, i, format11)
            w_col_no1 = w_col_no1 + 8

        sheet.write(4, 0, 'SKU', format21)
        sheet.merge_range(4, 1, 4, 5, 'Name With Attributes', format21)
        sheet.merge_range(4, 6, 4, 7, 'Category', format21)
        sheet.write(4, 8, 'Cost', format21)
        # sheet.write(4, 7, 'Min. Qty', format21)
        # sheet.write(4, 8, 'Max. Qty', format21)
        p_col_no1 = 9

        for i in get_warehouse[0]:
            sheet.write(4, p_col_no1, 'Min. Qty', format21)
            sheet.write(4, p_col_no1 + 1, 'Max. Qty', format21)
            sheet.write(4, p_col_no1 + 2, 'Available', format21)
#            sheet.write(4, p_col_no1 + 1, 'Virtual', format21)
#            sheet.write(4, p_col_no1 + 2, 'Incoming', format21)
#            sheet.write(4, p_col_no1 + 3, 'Outgoing', format21)
#            sheet.merge_range(4, p_col_no1 + 4, 4, p_col_no1 + 5, 'Net On Hand', format21)

#            sheet.merge_range(4, p_col_no1 + 6, 4, p_col_no1 + 7, 'Total Sold', format21)
#            sheet.merge_range(4, p_col_no1 + 8, 4, p_col_no1 + 9, 'Total Purchased', format21)

            sheet.merge_range(4, p_col_no1 + 3, 4, p_col_no1 + 4, 'Total Sold', format21)
            sheet.merge_range(4, p_col_no1 + 5, 4, p_col_no1 + 6, 'Total Purchased', format21)
            sheet.write(4, p_col_no1 + 7, 'Valuation', format21)
            p_col_no1 = p_col_no1 + 8

        prod_row = 5
        prod_col = 0

        for i in get_warehouse[1]:
            # raise ValidationError(_(i))
            get_line = self.get_lines(data, i)

            for each in get_line:
                sheet.write(prod_row, prod_col, each['sku'], font_size_8r)
                sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 5, each['name'], font_size_8r)
                sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['category'], font_size_8r)
                sheet.write(prod_row, prod_col + 8, each['cost_price'], font_size_8x)
                sheet.write(prod_row, prod_col + 7, each['min_qty'], font_size_8)
                sheet.write(prod_row, prod_col + 8, each['max_qty'], font_size_8)
                prod_row = prod_row + 1
            break

        prod_row = 5
        prod_col = 11

        for i in get_warehouse[1]:
            get_line = self.get_lines(data, i)
            # raise ValidationError(_(get_line))

            for each in get_line:
                # sheet.write(prod_row, prod_col - 2, each['min_qty'], font_size_8)
                # sheet.write(prod_row, prod_col - 1, each['max_qty'], font_size_8)

                if each['available'] == 0:
                    sheet.write(prod_row, prod_col, each['available'], yellow_mark)
                elif each['available'] > each['max_qty']:
                    sheet.write(prod_row, prod_col, each['available'], blue_mark)
                elif each['available'] < each['min_qty']:
                    sheet.write(prod_row, prod_col, each['available'], red_mark)
                elif each['available'] > each['min_qty'] and each['available'] < each['max_qty']:
                    sheet.write(prod_row, prod_col, each['available'], green_mark)
                    # raise ValidationError(_(each['min_qty']))

                # if each['available'] <= 0:
                #     sheet.write(prod_row, prod_col, each['available'], red_mark)
                # else:
                #     sheet.write(prod_row, prod_col, each['available'], font_size_8)


#                if each['virtual'] < 0:
#                    sheet.write(prod_row, prod_col + 1, each['virtual'], red_mark)
#                else:
#                    sheet.write(prod_row, prod_col + 1, each['virtual'], font_size_8)
#                if each['incoming'] < 0:
#                    sheet.write(prod_row, prod_col + 2, each['incoming'], red_mark)
#                else:
#                    sheet.write(prod_row, prod_col + 2, each['incoming'], font_size_8)
#                if each['outgoing'] < 0:
#                    sheet.write(prod_row, prod_col + 3, each['outgoing'], red_mark)
#                else:
#                    sheet.write(prod_row, prod_col + 3, each['outgoing'], font_size_8)
#                if each['net_on_hand'] < 0:
#                    sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'], red_mark)
#                else:
#                    sheet.merge_range(prod_row, prod_col + 4, prod_row, prod_col + 5, each['net_on_hand'], font_size_8)


                # if each['sale_value'] < 0:
                #     sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 2, each['sale_value'], red_mark)
                # else:
                sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 2, each['sale_value'], font_size_8)

                # if each['purchase_value'] < 0:
                #     sheet.merge_range(prod_row, prod_col + 3, prod_row, prod_col + 4, each['purchase_value'], red_mark)
                # else:
                sheet.merge_range(prod_row, prod_col + 3, prod_row, prod_col + 4, each['purchase_value'], font_size_8)

                # if each['total_value'] < 0:
                #     sheet.write(prod_row, prod_col + 5, each['total_value'], red_mark)
                # else:
                sheet.write(prod_row, prod_col + 5, each['total_value'], font_size_8x)

                prod_row = prod_row + 1

            prod_row = 5
            prod_col = prod_col + 8

StockReportXls('report.xxx.stock_report_xls.xlsx', 'product.product')
