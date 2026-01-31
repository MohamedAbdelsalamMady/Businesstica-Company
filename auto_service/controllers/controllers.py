# -*- coding: utf-8 -*-
# from odoo import http


# class AutoService(http.Controller):
#     @http.route('/auto_service/auto_service', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auto_service/auto_service/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('auto_service.listing', {
#             'root': '/auto_service/auto_service',
#             'objects': http.request.env['auto_service.auto_service'].search([]),
#         })

#     @http.route('/auto_service/auto_service/objects/<model("auto_service.auto_service"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auto_service.object', {
#             'object': obj
#         })
