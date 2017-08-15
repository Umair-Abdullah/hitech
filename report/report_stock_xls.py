
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
#import datetime
#import pytz
from datetime import datetime
from dateutil import tz
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from xlsxwriter.utility import xl_rowcol_to_cell

# import time
# from odoo import models, fields, api
# from odoo.addons import decimal_precision as dp
# from odoo import api, fields, models, _
# from odoo.exceptions import UserError, AccessError, ValidationError

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
        get_warehouse = self.get_warehouse(data)
        count = len(get_warehouse[0])
        # raise ValidationError(_(count))
        lines = []
        categ = self.get_category(data)

        if categ:
            stock_history = self.env['product.product'].search([('categ_id', 'in', categ), ('default_code', '!=', '')])
        else:
            stock_history = self.env['product.product'].search([('default_code', '!=', '')])

        valuey = 0
        for obj in stock_history:
            valuex = 0
            # sale_value = 0
            # purchase_value = 0
            product = self.env['product.product'].browse(obj.id)
            # sale_obj = self.env['sale.order.line'].search([('order_id.state', '=', 'done'),
            #                                                ('product_id', '=', product.id),
            #                                                ('order_id.warehouse_id', '=', warehouse)])
            # for i in sale_obj:
            #     sale_value = sale_value + i.product_uom_qty

            # purchase_obj = self.env['purchase.order.line'].search([('order_id.state', '=', 'done'),
            #                                                        ('product_id', '=', product.id),
            #                                                        ('order_id.picking_type_id', '=', warehouse)])
            # for i in purchase_obj:
            #     purchase_value = purchase_value + i.product_qty

            available_qty = product.with_context({'warehouse': warehouse}).virtual_available + \
                            product.with_context({'warehouse': warehouse}).outgoing_qty - \
                            product.with_context({'warehouse': warehouse}).incoming_qty

            # raise ValidationError(_(warehouse))
            # get_warehouse = self.get_warehouse(data)
            # raise ValidationError(_(get_warehouse[1][0][1]))
            # for j in get_warehouse[1]:
            available_qtyx = product.with_context({'warehouse': get_warehouse[1]}).virtual_available + \
                             product.with_context({'warehouse': get_warehouse[1]}).outgoing_qty - \
                             product.with_context({'warehouse': get_warehouse[1]}).incoming_qty
                # raise ValidationError(_(j))

            value = available_qty * product.standard_price
            valuex = valuex + available_qtyx
            valuey = valuex

            min_qty = 0
            max_qty = 0
            brandx = ''
            typex = ''
            sizex = ''
            specx = ''
            miscx = ''

            for p in product:
                variant = ''

                min_qty = p.min_qty
                max_qty = p.max_qty
                brandx = p.brand_id.name
                typex = p.type_id.name
                sizex = p.size_id.name
                specx = p.spec_id.name
                miscx = p.misc_id.name

                # sop = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', p.id), ('warehouse_id', '=', warehouse)])

                for item in p.attribute_value_ids:
                    # print 'item:', item.attribute_id

                    if item.attribute_id.id <> 1:
                        variant += ', ' + item.name
                        # raise ValidationError(_(p.name))

#                    variant += (' - ' + str(item.attribute_id.name) + ' : ' + item.name + ';\n')

                namex = variant and "%s %s" % (p.name, '[' + variant[2:] + ']') or p.name


                # for o in sop:
                #     min_qty += o.product_min_qty
                #     max_qty += o.product_max_qty

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
                'brand': brandx,
                'type': typex,
                'size': sizex,
                'spec': specx,
                'misc': miscx,
                'available': available_qty,
                'virtual': product.with_context({'warehouse': warehouse}).virtual_available,
                'incoming': product.with_context({'warehouse': warehouse}).incoming_qty,
                'outgoing': product.with_context({'warehouse': warehouse}).outgoing_qty,
                'net_on_hand': product.with_context({'warehouse': warehouse}).qty_available,
                'total_value': value,
                'total_valuex': valuex,
                'total_valuey': valuey,
                # 'sale_value': sale_value,
                # 'purchase_value': purchase_value,
            }
            lines.append(vals)

        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        get_warehouse = self.get_warehouse(data)
        count = len(get_warehouse[0]) * 2 + 12
        countx = len(get_warehouse[0])

        # raise ValidationError(_(count))
        sheet = workbook.add_worksheet("xxx")

        # format0 = workbook.add_format({'font_size': 16, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format00 = workbook.add_format({'font_size': 10, 'right': True, 'left': True,'bottom': True, 'top': True, 'align': 'vcenter', 'bold': True})
        # format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
        # format12 = workbook.add_format({'font_size': 12, 'right': True, 'left': True, 'bottom': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format10 = workbook.add_format({'font_size': 10, 'right': True, 'left': True,'bottom': True, 'top': True, 'align': 'vcenter', 'bold': True})
        # format3 = workbook.add_format({'bottom': True, 'top': True, 'align': 'vcenter', 'font_size': 12})

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
        gray_mark_16 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 16, 'align': 'vcenter', 'bold': True, 'bg_color': 'eeeeee'})
        gray_mark_16.set_align('center')
        gray_mark_14 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'align': 'vcenter', 'bold': True, 'bg_color': 'eeeeee'})
        gray_mark_14.set_align('center')
        gray_mark_12 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': 'eeeeee'})
        gray_mark_12.set_align('center')
        gray_mark_10 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 10, 'align': 'vcenter', 'bold': True, 'bg_color': 'eeeeee'})
        gray_mark_10.set_align('center')
        gray_mark_10r = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 10, 'align': 'vcenter', 'bold': True, 'bg_color': 'eeeeee'})
        gray_mark_10r.set_align('left')
        justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'align': 'vcenter', 'font_size': 12})
        justify.set_align('justify')

        # format3.set_align('center')
        font_size_8.set_align('center')
        font_size_8r.set_align('left')
        font_size_8x.set_align('center')
        # format0.set_align('center')
        format00.set_align('center')
        format00.set_text_wrap()
        # format1.set_align('center')
        # format12.set_align('center')
        format10.set_align('left')
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

        sheet.merge_range(0, 0, 1, count + 1, 'S t o c k  -  L e v e l s', gray_mark_16)
        sheet.merge_range('A3:K3', 'Report Date: ' + str(dt), gray_mark_14)
#        sheet.merge_range('A3:G3', 'Report Date: ' + str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M")), format1)
        sheet.merge_range(2, 11, 2, count + 1, 'Warehouses', gray_mark_14)
        sheet.merge_range('A4:K4', 'Product Information', gray_mark_12)
        w_col_no = 10
        w_col_no1 = 11

        for i in get_warehouse[0]:
            w_col_no = w_col_no + 2
            sheet.merge_range(3, w_col_no1, 3, w_col_no, i, gray_mark_12)
            w_col_no1 = w_col_no1 + 2

        sheet.write(4, 0, 'Code', gray_mark_10)
        sheet.set_column(0, 0, 10)
#        sheet.merge_range(4, 1, 4, 5, 'Name With Attributes', format21)
        sheet.write(4, 1, 'Name With Attributes', gray_mark_10)
        sheet.set_column(1, 1, 40)
#        sheet.merge_range(4, 6, 4, 7, 'Category', format21)
        sheet.write(4, 2, 'Category', gray_mark_10)
        sheet.set_column(2, 2, 15)
        sheet.write(4, 3, 'Brand', gray_mark_10)
        sheet.set_column(3, 3, 10)
        sheet.write(4, 4, 'Type', gray_mark_10)
        sheet.set_column(4, 4, 10)
        sheet.write(4, 5, 'Size', gray_mark_10)
        sheet.set_column(5, 5, 10)
        sheet.write(4, 6, 'Spec.', gray_mark_10)
        sheet.set_column(6, 6, 10)
        sheet.write(4, 7, 'Misc.', gray_mark_10)
        sheet.set_column(7, 7, 10)
        sheet.write(4, 8, 'Cost', gray_mark_10)
        sheet.write(4, 9, 'Min.', gray_mark_10)
        sheet.write(4, 10, 'Max.', gray_mark_10)
        p_col_no1 = 11

        for i in get_warehouse[0]:
            # sheet.write(4, p_col_no1, 'Min. Qty', format21)
            # sheet.write(4, p_col_no1 + 1, 'Max. Qty', format21)

            sheet.write(4, p_col_no1 + 0, 'Qty.', gray_mark_10)
#            sheet.write(4, p_col_no1 + 1, 'Virtual', format21)
#            sheet.write(4, p_col_no1 + 2, 'Incoming', format21)
#            sheet.write(4, p_col_no1 + 3, 'Outgoing', format21)
#            sheet.merge_range(4, p_col_no1 + 4, 4, p_col_no1 + 5, 'Net On Hand', format21)

#            sheet.merge_range(4, p_col_no1 + 6, 4, p_col_no1 + 7, 'Total Sold', format21)
#            sheet.merge_range(4, p_col_no1 + 8, 4, p_col_no1 + 9, 'Total Purchased', format21)

            # sheet.merge_range(4, p_col_no1 + 1, 4, p_col_no1 + 2, 'Total Sold', format21)
            # sheet.merge_range(4, p_col_no1 + 3, 4, p_col_no1 + 4, 'Total Purchased', format21)
            sheet.write(4, p_col_no1 + 1, 'Val.', gray_mark_10)
            p_col_no1 = p_col_no1 + 2

        prod_row = 5
        prod_col = 0

        for i in get_warehouse[1]:
            get_line = self.get_lines(data, i)

            for each in get_line:
                sheet.write(prod_row, prod_col, each['sku'], font_size_8r)
                # sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 1, each['name'], font_size_8r)
                # sheet.merge_range(prod_row, prod_col + 6, prod_row, prod_col + 7, each['category'], font_size_8r)
                sheet.write(prod_row, prod_col + 1, each['name'], font_size_8r)
                sheet.write(prod_row, prod_col + 2, each['category'], font_size_8r)
                sheet.write(prod_row, prod_col + 3, each['brand'] or None, font_size_8r)
                sheet.write(prod_row, prod_col + 4, each['type'] or None, font_size_8r)
                sheet.write(prod_row, prod_col + 5, each['size'] or None, font_size_8r)
                sheet.write(prod_row, prod_col + 6, each['spec'] or None, font_size_8r)
                sheet.write(prod_row, prod_col + 7, each['misc'] or None, font_size_8r)
                sheet.write(prod_row, prod_col + 8, each['cost_price'], font_size_8x)
                sheet.write(prod_row, prod_col + 9, each['min_qty'], font_size_8)
                sheet.write(prod_row, prod_col + 10, each['max_qty'], font_size_8)
                prod_row = prod_row + 1
            break

        prod_row = 5
        prod_col = 11

        for i in get_warehouse[1]:
            get_line = self.get_lines(data, i)
            # raise ValidationError(_(get_line[0]))

            greenx = 0
            bluex = 0
            redx = 0
            nax = 0
            totalx = 0

            for each in get_line:
                # sheet.write(prod_row, prod_col - 2, each['min_qty'], font_size_8)
                # sheet.write(prod_row, prod_col - 1, each['max_qty'], font_size_8)

                # if each['available'] == 0:
                #     sheet.write(prod_row, prod_col, each['available'], yellow_mark)
                # elif each['available'] > each['max_qty']:
                #     sheet.write(prod_row, prod_col, each['available'], blue_mark)
                # elif each['available'] < each['min_qty']:
                #     sheet.write(prod_row, prod_col, each['available'], red_mark)
                # elif each['available'] > each['min_qty'] and each['available'] < each['max_qty']:
                #     sheet.write(prod_row, prod_col, each['available'], green_mark)
                    # raise ValidationError(_(each['min_qty']))

                sheet.write(prod_row, prod_col, each['available'], font_size_8)

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
                # sheet.merge_range(prod_row, prod_col + 1, prod_row, prod_col + 2, each['sale_value'], font_size_8)

                # if each['purchase_value'] < 0:
                #     sheet.merge_range(prod_row, prod_col + 3, prod_row, prod_col + 4, each['purchase_value'], red_mark)
                # else:
                # sheet.merge_range(prod_row, prod_col + 3, prod_row, prod_col + 4, each['purchase_value'], font_size_8)

                # if each['total_value'] < 0:
                #     sheet.write(prod_row, prod_col + 5, each['total_value'], red_mark)
                # else:
                sheet.write(prod_row, prod_col + 1, each['total_value'], font_size_8x)
                sheet.write(prod_row, prod_col + 2, each['total_valuey'], font_size_8)

                if each['total_valuey'] > 0:
                    if each['max_qty'] > 0:
                        sheet.write(prod_row, prod_col + 3, '{0:,.2f}%'.format((each['total_valuey'] / each['max_qty']) * 100), font_size_8)
                    else:
                        sheet.write(prod_row, prod_col + 3, '{0:,.2f}%'.format(0.00), font_size_8)
                else:
                    sheet.write(prod_row, prod_col + 3, '{0:,.2f}%'.format(0.00), font_size_8)

                # =IF(H7>M7,"BLUE",IF(H7<L7,"RED",IF(L7<H7>M7,"GREEN","NA")))
                if each['total_valuey'] == 0:
                    sheet.write(prod_row, prod_col + 4, 'YELLOW', yellow_mark)
                    nax += 1
                elif each['total_valuey'] > each['max_qty']:
                    sheet.write(prod_row, prod_col + 4, 'BLUE', blue_mark)
                    bluex += 1
                elif each['total_valuey'] < each['min_qty']:
                    sheet.write(prod_row, prod_col + 4, 'RED', red_mark)
                    redx += 1
                elif each['total_valuey'] > each['min_qty'] and each['total_valuey'] < each['max_qty']:
                    sheet.write(prod_row, prod_col + 4, 'GREEN', green_mark)
                    greenx += 1


                # if countx == 1:
                #     sheet.write(prod_row, prod_col + 3, '=G' + str((prod_row+1)) + '*1')
                #
                # if countx > 1:
                #     for x in range(1, countx):
                #         for i in range(7, count - 1):
                #             cell = xl_rowcol_to_cell(prod_row, i)
                #             cell = cell + '+' + cell
                #             raise ValidationError(_(cell))
                #             sheet.write(prod_row, prod_col + 3, '=' + cell + '*1')
                #             i = i + 2

                prod_row = prod_row + 1

            prod_row = 5
            prod_col = prod_col + 2

        # sheet.write(prod_row, prod_col + 1, 'Test', font_size_8x)
        sheet.merge_range(3, prod_col, 3, prod_col + 2, 'Total', gray_mark_12)
        sheet.write(4, prod_col, 'Quantity', gray_mark_10)
        sheet.set_column(prod_col, prod_col, 10)
        hx = ' Of Max.'
        sheet.write(4, prod_col + 1, "%% %s" % hx, gray_mark_10)
        sheet.set_column(prod_col + 1, prod_col + 1, 10)
        sheet.write(4, prod_col + 2, 'Status', gray_mark_10)
        # sheet.merge_range(4, prod_col + 1, 4, prod_col + 1, 'Status', format00)

        sheet.merge_range(4, prod_col + 4, 4, prod_col + 6, 'Summary', gray_mark_12)

        sheet.write(5, prod_col + 4, 'GREEN', gray_mark_10)
        sheet.write(6, prod_col + 4, 'BLUE', gray_mark_10)
        sheet.write(7, prod_col + 4, 'RED', gray_mark_10)
        sheet.write(8, prod_col + 4, 'YELLOW', gray_mark_10)
        sheet.write(9, prod_col + 4, 'TOTAL', gray_mark_10)

        sheet.write(5, prod_col + 5, greenx, format00)
        sheet.write(6, prod_col + 5, bluex, format00)
        sheet.write(7, prod_col + 5, redx, format00)
        sheet.write(8, prod_col + 5, nax, format00)
        sheet.write(9, prod_col + 5, (greenx + bluex + redx + nax), gray_mark_10)

        totalx = (greenx + bluex + redx + nax)

        # totaly = 0.00
        # totaly = '{0:,.2f}%'.format((float(greenx) / float(totalx)) * 100)
        # raise ValidationError(_(totaly))

        sheet.write(5, prod_col + 6, '{0:,.2f}%'.format((float(greenx) / float(totalx)) * 100), format00)
        sheet.write(6, prod_col + 6, '{0:,.2f}%'.format((float(bluex) / float(totalx)) * 100), format00)
        sheet.write(7, prod_col + 6, '{0:,.2f}%'.format((float(redx) / float(totalx)) * 100), format00)
        sheet.write(8, prod_col + 6, '{0:,.2f}%'.format((float(nax) / float(totalx)) * 100), format00)

        # sheet.write(3, prod_col + 4, 'Green = Total Qty > Min. AND Total Qty < Max.', gray_mark_10)

        sheet.merge_range(11, prod_col + 4, 11, prod_col + 7, 'Color Conditions', gray_mark_12)
        sheet.write(12, prod_col + 4, 'GREEN', gray_mark_10)
        sheet.write(13, prod_col + 4, 'BLUE', gray_mark_10)
        sheet.write(14, prod_col + 4, 'RED', gray_mark_10)
        sheet.write(15, prod_col + 4, 'YELLOW', gray_mark_10)
        # sheet.merge_range(9, prod_col + 4, 9, prod_col + 4, 'GREEN', gray_mark_10r)
        # sheet.merge_range(10, prod_col + 4, 10, prod_col + 4, 'BLUE', gray_mark_10r)
        # sheet.merge_range(11, prod_col + 4, 11, prod_col + 4, 'RED', gray_mark_10r)
        # sheet.merge_range(12, prod_col + 4, 12, prod_col + 4, 'YELLOW', gray_mark_10r)

        sheet.merge_range(12, prod_col + 5, 12, prod_col + 7, 'Qty. BETWEEN (Min. AND Max.)', format10)
        sheet.merge_range(13, prod_col + 5, 13, prod_col + 7, 'Qty. GREATER THAN Max.', format10)
        sheet.merge_range(14, prod_col + 5, 14, prod_col + 7, 'Qty. LESS THAN Min.', format10)
        sheet.merge_range(15, prod_col + 5, 15, prod_col + 7, 'Qty. EQUALS TO 0 (Zero)', format10)

        # c = 7
        # for i in countx:
        # if countx == 1:
        #     sheet.write('J6', '=G6*1')

StockReportXls('report.xxx.stock_report_xls.xlsx', 'product.product')
