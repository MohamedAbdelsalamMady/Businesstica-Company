# -- coding: utf-8 --

##############################################################################
#                                                                            #
# Part of WebbyCrown Solutions (Website: www.webbycrown.com).                #
# Copyright © 2025 WebbyCrown Solutions. All Rights Reserved.                #
#                                                                            #
# This module is developed and maintained by WebbyCrown Solutions.           #
# Unauthorized copying of this file, via any medium, is strictly prohibited. #
# Licensed under the terms of the WebbyCrown Solutions License Agreement.    #
#                                                                            #
##############################################################################

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PharmacyJsonRPCController(http.Controller):

    @http.route('/pharmacy/jsonrpc/treatments', type='json', auth='user', csrf=False, methods=['POST'])
    def rpc_treatments(self, **payload):
        params = payload.get('params', {}) if isinstance(payload, dict) else {}
        limit = params.get('limit', 50)
        hospital_code = params.get('hospital_code')
        domain = []
        if hospital_code:
            hospital = request.env['hospital.hospital'].sudo().search([('code', '=', hospital_code)], limit=1)
            if not hospital:
                return self._jsonrpc_error(payload, f'Hospital with code {hospital_code} not found.')
            domain.append(('hospital_id', '=', hospital.id))
        treatments = request.env['hospital.treatment'].sudo().search(domain, limit=limit, order='start_datetime desc')
        result = [
            {
                'name': treatment.name,
                'patient': treatment.patient_id.name,
                'hospital': treatment.hospital_id.name,
                'state': treatment.state,
                'stage': treatment.stage_id.name if treatment.stage_id else False,
                'telemedicine_enabled': treatment.telemedicine_enabled,
                'telemedicine_session_id': treatment.telemedicine_session_id,
                'telemedicine_session_url': treatment.telemedicine_session_url,
                'telemedicine_join_token': treatment.telemedicine_join_token,
                'start_datetime': treatment.start_datetime,
                'end_datetime': treatment.end_datetime,
                'portal_visible': treatment.portal_visible,
            }
            for treatment in treatments
        ]
        return self._jsonrpc_result(payload, result)

    def _jsonrpc_result(self, payload, result):
        return {
            'jsonrpc': '2.0',
            'id': payload.get('id'),
            'result': result,
        }

    def _jsonrpc_error(self, payload, message):
        _logger.warning("JSON-RPC error: %s", message)
        return {
            'jsonrpc': '2.0',
            'id': payload.get('id'),
            'error': {
                'code': 400,
                'message': message,
            },
        }

    @http.route('/pharmacy/jsonrpc/availability', type='json', auth='user', csrf=False, methods=['POST'])
    def rpc_availability(self, **payload):
        """JSON-RPC endpoint for availability queries."""
        params = payload.get('params', {}) if isinstance(payload, dict) else {}
        pharmacy_code = params.get('pharmacy_code')
        user_id = params.get('user_id')
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        
        domain = [('state', '=', 'published')]
        if pharmacy_code:
            pharmacy = request.env['pharmacy.pharmacy'].sudo().search([('code', '=', pharmacy_code)], limit=1)
            if pharmacy:
                domain.append(('pharmacy_id', '=', pharmacy.id))
        if user_id:
            domain.append(('user_id', '=', user_id))
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        availabilities = request.env['pharmacy.resource.availability'].sudo().search(domain)
        result = [
            {
                'id': av.id,
                'user': av.user_id.name if av.user_id else False,
                'pharmacy': av.pharmacy_id.name if av.pharmacy_id else False,
                'date': av.date.isoformat() if av.date else False,
                'start_time': av.start_time,
                'end_time': av.end_time,
                'capacity': av.capacity,
            }
            for av in availabilities
        ]
        return self._jsonrpc_result(payload, result)

