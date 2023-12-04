import imghdr
import json
import functools
import io
import odoo
import os
import sys
import jinja2
from odoo import http, tools
from odoo.addons.web.controllers.database import Database
from odoo.addons.web.controllers.binary import Binary
from odoo.addons.web.controllers.main import content_disposition, Home
from odoo.http import request


if hasattr(sys, 'frozen'):
    # When running on compiled windows binary,
    #  we don't have access to package loader.
    path = \
        os.path.realpath(os.path.join(os.path.dirname(__file__),
                                      '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.odoo-debrand-11', "views")
env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps


class BinaryCustom(Binary):
    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
    ], type='http', auth="public")
    def company_logo(self, dbname=None, **kw):
        imgname = 'logo'
        imgext = '.png'
        # Here we are changing the default
        #  logo with logo selected on debrand settings
        company_logo = request.env['website'].sudo().search([])[0].company_logo
        custom_logo = tools.image_resize_image(company_logo, (150, None))
        placeholder = \
            functools.partial(get_resource_path,
                              'web',
                              'static',
                              'src',
                              'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = http.db_monodb()

        if not uid:
            uid = odoo.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname + imgext))
        else:
            try:
                # create an empty registry
                registry = odoo.registry(dbname)
                if custom_logo:
                    image_data = io.BytesIO(custom_logo)
                    imgext = '.' + (imghdr.what(None, h=custom_logo) or 'png')
                    response = http.send_file(image_data,
                                              filename=imgname + imgext,
                                              mtime=None,
                                              mimetype='image/' + imgext,
                                              as_attachment=False)
                    response.headers.add('Content-Disposition', content_disposition(response, imgname + imgext))
                else:
                    with registry.cursor() as cr:
                        cr.execute("""SELECT c.logo_web, c.write_date
                                        FROM res_users u
                                   LEFT JOIN res_company c
                                          ON c.id = u.company_id
                                       WHERE u.id = %s
                                   """, (uid,))
                        row = cr.fetchone()
                        if row and row[0]:
                            image_data = io.BytesIO(row[0])
                            imgext = '.' + (imghdr.what(None, h=row[0]) or 'png')
                            response = http.send_file(image_data,
                                                      filename=imgname + imgext,
                                                      mtime=row[1],
                                                      mimetype='image/' + imgext,
                                                      as_attachment=False)
                            response.headers.add('Content-Disposition', content_disposition(response, imgname + imgext))
                        else:
                            response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname + imgext))
        return response


# class OdooDebrand(Home):
# 	# Render the Database management html page
# 	def _render_template(self, **d):
# 		d.setdefault('manage', True)
# 		d['insecure'] = odoo.tools.config.is_admin_passwd_valid('admin')
# 		d['list_db'] = odoo.tools.config['list_db']
# 		d['langs'] = http.request.env['ir.translation']._get_languages()
# 		d['countries'] = http.request.env['res.country'].sudo().search([])
# 		d['pattern'] = odoo.modules.db.DBNAME_PATTERN
# 		# databases list
# 		d['databases'] = []
# 		try:
# 			d['databases'] = http.request.session.db.list()
# 			d['incompatible_databases'] = \
# 			http.request.env['res.company']._get_incompatible_database_names(d['databases'])
# 		except AccessDenied:
# 			monodb = odoo.modules.registry.RegistryManager.get('').db_monodb()
# 			if monodb:
# 				d['databases'] = [monodb]

# 		try:
# 			website_id = http.request.env['website'].sudo().search([])
# 			d['company_name'] = website_id and website_id[0].company_name or ''
# 			d['favicon_url'] = website_id and website_id[0].favicon_url or ''
# 			d['company_logo_url'] = website_id and website_id[0].company_logo_url or ''
# 			template = http.request.env.ref("base.web_template_simple_bootstrap")._render({
# 				'menu_data': http.request.env['ir.ui.menu'].load_menus(http.request.session.debug),
# 				'db_monodb': http.db_monodb(),
# 				'company_name': d['company_name'],
# 				'company_logo_url': d['company_logo_url'],
# 				'favicon_url': d['favicon_url'],
# 			})
# 			d['menu_data'] = template.decode("utf-8")
# 			return http.request.render('database_manager_extend', d)
# 		except Exception as e:
# 			d['company_name'] = ''
# 			d['favicon_url'] = ''
# 			d['company_logo_url'] = ''
# 			return http.request.render('database_manager', d)

