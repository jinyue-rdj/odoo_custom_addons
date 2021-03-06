# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger("workflow_ebilling")


class BillingRequest(models.Model):

        _inherit = ['workflow.mixin', 'base_state_model.mixin']
        _name = 'ebilling.request.header'

        WORKFLOW_STATE_SELECTION = [
            ("draft", "Draft"),
            ("submit", "Submit"),
            ("approving", "Approving"),
            ("completed", "Completed"),
            ("cancel", "Cancel")
        ]

        request_no = fields.Char(string="No.", readonly=True)
        project = fields.Char(string="Project Name", required=True)
        bp_code = fields.Char(string="Business Partner Code", required=True)
        po_no = fields.Char(string="Customer PO NO.", required=True)
        company_billing = fields.Char(string="Company Billing", required=True)
        company = fields.Char(string="Site Company", required=True)
        nature_of_billing = fields.Char(string="Nature of Billing", required=True)
        currency = fields.Char(required=True)
        remark = fields.Text()
        total_amount = fields.Float(compute="_compute_total_amount", string="Total Amount", store=False)
        detail_ids = fields.One2many("ebilling.request.detail", "header_id")
        state = fields.Selection(WORKFLOW_STATE_SELECTION, default="draft", readonly=False, groups="english.group_english_manager")

        @api.multi
        @api.depends('detail_ids.amount')
        def _compute_total_amount(self):
                for head in self:
                        head.total_amount = sum(detail.amount for detail in head.detail_ids)

        @api.multi
        def workflow_draft(self):
                _logger.info("draft")
                self.state = 'draft'
                return True

        @api.multi
        def workflow_submit(self):
                self.state = 'submit'
                _logger.info("submit")
                _logger.info(self.bp_code)
                return True

        @api.multi
        def workflow_approving(self):
                self.state = 'approving'
                action = self.get_tree_view()
                return action

        @api.multi
        def workflow_completed(self):
                self.state = 'completed'
                action = self.get_tree_view()
                return action

        @api.multi
        def workflow_cancel(self):
                self.state = 'cancel'
                return True

        def get_tree_view(self):
                action_ref = self.env.ref('workflow_ebilling.workflow_ebilling_request_action', False)
                action = action_ref.read()[0]
                if action.pop('view_type', 'form') != 'form':
                        return action

                if 'view_mode' in action:
                        action['view_mode'] = ','.join(
                                mode if mode != 'tree' else 'list'
                                for mode in action['view_mode'].split(','))
                action['views'] = [
                        [id, mode if mode != 'tree' else 'list']
                        for id, mode in action['views']
                ]
                return action


class BillingRequestDetail(models.Model):

        _name = "ebilling.request.detail"

        header_id = fields.Many2one("ebilling.request.header", ondelete='cascade', required=True)
        part_number = fields.Char(string="PartNumber", required=True)
        qty = fields.Float(string="Qty", required=True)
        unit_price = fields.Float(string="Unit Price", required=True)
        amount = fields.Float(computer="_compute_amount", string="Amount", store=True)

        @api.multi
        @api.depends("qty", "unit_price")
        @api.onchange("qty", "unit_price")
        def _compute_amount(self):
                for line in self:
                        amount = line.qty * line.unit_price
                        line.update({"qty": line.qty, "unit_price":line.unit_price, "amount":amount})

        @api.model
        def write(self, values):
                if "unit_price" in values and "qty" not in values:
                    values['amount'] = self.qty * values['unit_price']
                if "unit_price" not in values and "qty" in values:
                    values['amount'] = self.unit_price * values['qty']
                if "unit_price" in values and "qty" in values:
                    values['amount'] = values['unit_price'] * values['qty']
                return super(BillingRequestDetail, self).write(values)

        @api.model
        def create(self, values):
                if "unit_price" in values and "qty" in values:
                    values['amount'] = values['unit_price'] * values['qty']
                return super(BillingRequestDetail, self).create(values)
