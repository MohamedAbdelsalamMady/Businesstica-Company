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

from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestTreatmentFlow(TransactionCase):

    def setUp(self):
        super().setUp()
        self.hospital = self.env.ref('pharmacy_management_system.hospital_general')
        self.patient = self.env.ref('pharmacy_management_system.partner_patient_amy')
        self.stage = self.env.ref('pharmacy_management_system.treatment_stage_assessment')

    def test_telemedicine_tokens_base64(self):
        Treatment = self.env['hospital.treatment']
        treatment = Treatment.create({
            'patient_id': self.patient.id,
            'hospital_id': self.hospital.id,
            'stage_id': self.stage.id,
            'telemedicine_enabled': True,
            'telemedicine_session_id': 'plain-session',
            'telemedicine_session_url': 'https://telemed.local/session/1',
            'telemedicine_join_token': 'join-token',
        })
        for field in ('telemedicine_session_id', 'telemedicine_session_url', 'telemedicine_join_token'):
            value = treatment[field]
            self.assertRegex(
                value or '',
                r'^[A-Za-z0-9+/]+={0,2}$',
                f"{field} should be stored in base64 format.",
            )

