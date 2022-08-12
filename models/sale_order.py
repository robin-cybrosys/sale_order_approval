from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = ['sale.order']
    # Method(Without Over writing state(s))
    state = fields.Selection(
        selection_add=[('waiting', 'Waiting Approval'),('sent',)],ondelete={'waiting': 'set default'})
    # state = fields.Selection([
    #     ('draft', 'Quotation'),
    #     ('waiting', 'Waiting Approval'),
    #     ('sent', 'Quotation Sent'),
    #     ('sale', 'Sales Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled'),
    # ], string='Status', readonly=True, copy=False, index=True, tracking=True,
    #     default='draft')

    # boolean for changing visibility of 'send to manager button'
    btn_visibility = fields.Boolean(string='Visible', default=False)

    # validation ()
    def check(self):
        for rec in self.order_line:
            if rec.product_id.lst_price != rec.price_unit:
                raise ValidationError(
                    "The following Product's selling Price have been altered."
                    " This operation needs an Authorized Employee/Manager"
                    " to approve the Quotation!")

    # on confirm button
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self.order_line:
            if rec.product_id.lst_price != rec.price_unit:
                if self.env.user.has_group('sales_team.group_sale_manager'):
                    return res
                else:
                    self.check()

    # on send quote
    def action_quotation_send(self):
        res = super(SaleOrder, self).action_quotation_send()
        self.check()
        return res

    # on unit price change
    @api.onchange('order_line')
    def _onchange_discount(self):
        for rec in self.order_line:
            if rec.product_id.lst_price != rec.price_unit:
                self.btn_visibility = True
            else:
                self.btn_visibility = False

    # Approval button for manager
    def btn_approve(self):
        for item in self:
            item.state = "sent"
        record = super(SaleOrder, self).action_quotation_send()
        for rec in self.order_line:
            if rec.product_id.lst_price != rec.price_unit:
                return record

    # Disapproval button for manager
    def btn_disapprove(self):
        super(SaleOrder, self).action_draft()
        # self.action_draft()
        self.state = "draft"

    # 'Send to manager' button
    def btn_send_to_manager(self):
        self.state = 'waiting'
        self.btn_visibility = False

    # return {'warning': {'title': "Warning", 'message': (
    #     "The following Product's selling Price have been altered."
    #     " This operation needs an Authorized Employee/Manager"
    #     " to approve the Quotation!")}}
