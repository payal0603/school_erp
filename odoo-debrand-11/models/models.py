from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class OdooDebrand(models.Model):
    _inherit = 'website'

    @api.depends('favicon')
    def get_favicon(self):
        for record in self:
            record.favicon_url = 'data:image/png;base64,' + str(record.favicon.decode('UTF-8'))

    @api.depends('company_logo')
    def get_company_logo(self):
        for record in self:
            record.company_logo_url = 'data:image/png;base64,' + str(record.company_logo.decode('UTF-8'))

    company_logo = fields.Binary("Logo", attachment=True, help="This field holds the image used for the Company Logo")
    company_name = fields.Char("Company Name", help="Branding Name")
    company_website = fields.Char("Company URL")
    favicon_url = fields.Char("Url", compute='get_favicon')
    company_logo_url = fields.Char("Url", compute='get_company_logo')

class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    company_logo = fields.Binary(related='website_id.company_logo', string="Company Logo", help="This field holds the image used for the Company Logo", readonly=False)
    company_name = fields.Char(related='website_id.company_name', string="Company Name", readonly=False)
    company_website = fields.Char(related='website_id.company_website', readonly=False)

    # Sample Error Dialogue
    def error(self):
        raise UserError("This is a User Error!")

    # Sample Warning Dialogue
    def warning(self):  
        raise UserError("This is a Warning!")