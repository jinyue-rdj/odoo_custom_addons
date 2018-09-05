
from odoo import fields, models, api, _
from bs4 import BeautifulSoup
from openerp.http import request
from odoo.fields import Datetime
import werkzeug
import requests
import logging

_logger = logging.getLogger(__name__)


class InvestProjectStatus(models.Model):

    _name = 'invest.project.status'
    _description = 'Invest Project Status'

    name = fields.Char(string="Status", required=True, index=True)
    sequence = fields.Integer()
    is_enabled = fields.Boolean(string="Is Enabled", default=True)
    lexicon_explain_example_ids = fields.One2many('invest.project', 'invest_project_status_id',
                                                  "Project Status")


class InvestProjectCategory(models.Model):

    _name = 'invest.project.category'
    _description = 'Invest Project Category'

    name = fields.Char(string="Category", required=True, index=True)
    is_enabled = fields.Boolean(string="Is Enabled", default=True)


class InvestProject(models.Model):

    _name = 'invest.project'
    _description = 'Invest Project'

    name = fields.Char(string="Project", required=True, index=True)
    category_id = fields.Many2one('invest.project.category', 'Category')
    total_invest = fields.Char(string="Total Invest")
    invest_synopsis = fields.Text(string="Invest Synopsis", require=True)
    invest_demand = fields.Text(string="Invest Demand")
    is_published = fields.Boolean(string="Is Published", default=True)
    invest_project_status_id = fields.Many2one('invest.project.status', ondelete='restrict', required=True)
    manager_user_id = fields.Many2one('res.users', 'Manager User')
    invest_project_progress_ids = fields.One2many('invest.project.progress', 'invest_project_id', "Progress")
    invest_project_comment_ids = fields.One2many('invest.project.comment', 'invest_project_id', "Comments")
    follower_member_ids = fields.Many2many('res.users', 'invest_project_users_rel', 'project_id', 'user_id', string="Follower Members")

    def get_project_list(self, page_index, page_size, key_project):
        offset = (page_index-1) * page_size
        if key_project.strip():
            domain = [('is_published', '=', True), ('name', 'like', key_project)]
        else:
            domain = [('is_published', '=', True)]
        return self.get_project_detail(domain, offset, page_size)

    def get_follow_projects(self, page_index, page_size, user_id):
        offset = (page_index - 1) * page_size
        domain = [('is_published', '=', True), ('follower_member_ids', '=', user_id)]
        return self.get_project_detail(domain, offset, page_size)

    def get_my_projects(self, page_index, page_size, user_id):
        offset = (page_index - 1) * page_size
        domain = [('is_published', '=', True), ('manager_user_id', '=', user_id)]
        return self.get_project_detail(domain, offset, page_size)

    def get_project_detail(self, domain, offset, page_size):
        result = []
        list = self.search(domain, offset=offset, limit=page_size, order='create_date')
        for l in list:
            item = {}
            item['id'] = l.id
            item['name'] = l.name
            item['total_amount'] = l.total_invest
            item['synopsis'] = '%s %s' % (l.invest_synopsis, l.invest_demand)
            item['create_date'] = l.create_date
            item['status'] = l.invest_project_status_id.name
            item['manager_name'] = l.manager_user_id.name
            item['pictures'] = self.get_attachment_url(l.id)
            item['comments'] = []
            item['followers'] = []
            item['progress'] = []
            for c in l.invest_project_comment_ids:
                item['comments'].append({'name': c.name, 'user': c.comment_user_id.name})
            for follow_user in l.follower_member_ids:
                item['followers'].append(follow_user.name)
            for p in l.invest_project_progress_ids:
                item['progress'].append({'name': p.name, 'date': p.date_info})
            result.append(item)
        return result

    def get_attachment_url(self, project_id):
        result_urls = []
        url = request.httprequest.url_root + "web/image/%s"
        attachments = self.env["ir.attachment"].search([("res_id", "=", project_id), ("res_model", "=", self._name)])
        for att in attachments:
            result_urls.append(url % str(att.id))
        return result_urls

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = ['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)]

        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Pictures are attached to the project.</p>
                      '''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    def _compute_attached_images_count(self):
        attachment = self.env['ir.attachment']
        for model in self:
            model.image_count = attachment.search_count([
                '&', ('res_model', '=', self._name), ('res_id', '=', model.id)
            ])

    image_count = fields.Integer(compute='_compute_attached_images_count', string="Number of pictures attached")

    def follow_project(self, project_id, user_id):
        project = self.search([('id', '=', project_id), ('follower_member_ids', '=', user_id)], limit=1)
        if not project:
            value = [(4, user_id, 0)]
            project.write({'follower_member_ids': value})


class InvestProjectProgress(models.Model):

    _name = 'invest.project.progress'
    _description = 'Invest Project Progress'

    name = fields.Char(string="Progress", required=True, index=True)
    date_info = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    invest_project_id = fields.Many2one('invest.project', ondelete='restrict', required=True)


class InvestProjectComment(models.Model):

    _name = 'invest.project.comment'
    _description = 'Invest Project Comment'

    name = fields.Text(string="Content", required=True)
    invest_project_id = fields.Many2one('invest.project', ondelete='restrict', required=True)
    comment_user_id = fields.Many2one('res.users', 'Comment User')
    comment_date = fields.Datetime(string="Comment Date")

    def save_user_comment(self, project_id, user_id, content):
        self.create({'name': content, 'invest_project_id': project_id,
                     'comment_user_id': user_id, 'comment_date': Datetime.now()})
