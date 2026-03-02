from odoo import models, fields, api
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class PediatricDashboard(models.TransientModel):
    _name = 'pediatric.dashboard'
    _description = 'Tableau de Bord Pédiatrique'

    @api.model
    def get_dashboard_data(self):
        """Récupérer toutes les données pour le tableau de bord"""
        today = date.today()
        start_of_month = today.replace(day=1)
        start_of_week = today - timedelta(days=today.weekday())
        
        return {
            'today_stats': self._get_today_stats(),
            'week_stats': self._get_week_stats(),
            'month_stats': self._get_month_stats(),
            'financial_stats': self._get_financial_stats(),
            'alerts': self._get_alerts(),
            'charts_data': self._get_charts_data()
        }
    
    def _get_today_stats(self):
        """Statistiques du jour"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        appointments_today = self.env['pediatric.appointment'].search_count([
            ('appointment_date', '>=', today),
            ('appointment_date', '<', tomorrow)
        ])
        
        consultations_today = self.env['pediatric.consultation'].search_count([
            ('consultation_date', '>=', today),
            ('consultation_date', '<', tomorrow),
            ('state', '=', 'done')
        ])
        
        vaccinations_today = self.env['pediatric.vaccination'].search_count([
            ('vaccination_date', '=', today.date()),
            ('state', '=', 'done')
        ])
        
        # Calcul du taux de présence
        confirmed_appointments = self.env['pediatric.appointment'].search_count([
            ('appointment_date', '>=', today),
            ('appointment_date', '<', tomorrow),
            ('state', 'in', ['done', 'confirmed'])
        ])
        
        presence_rate = (confirmed_appointments / appointments_today * 100) if appointments_today > 0 else 0
        
        return {
            'patients': appointments_today,
            'consultations': consultations_today,
            'vaccinations': vaccinations_today,
            'presence_rate': round(presence_rate, 1)
        }
    
    def _get_week_stats(self):
        """Statistiques de la semaine"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        appointments_week = self.env['pediatric.appointment'].search_count([
            ('appointment_date', '>=', start_of_week),
            ('appointment_date', '<=', end_of_week)
        ])
        
        consultations_week = self.env['pediatric.consultation'].search_count([
            ('consultation_date', '>=', start_of_week),
            ('consultation_date', '<=', end_of_week),
            ('state', '=', 'done')
        ])
        
        vaccinations_week = self.env['pediatric.vaccination'].search_count([
            ('vaccination_date', '>=', start_of_week),
            ('vaccination_date', '<=', end_of_week),
            ('state', '=', 'done')
        ])
        
        return {
            'patients': appointments_week,
            'consultations': consultations_week,
            'vaccinations': vaccinations_week
        }
    
    def _get_month_stats(self):
        """Statistiques du mois"""
        today = date.today()
        start_of_month = today.replace(day=1)
        
        # Nouveaux patients ce mois
        new_patients = self.env['pediatric.patient'].search_count([
            ('create_date', '>=', start_of_month)
        ])
        
        consultations_month = self.env['pediatric.consultation'].search_count([
            ('consultation_date', '>=', start_of_month),
            ('state', '=', 'done')
        ])
        
        vaccinations_month = self.env['pediatric.vaccination'].search_count([
            ('vaccination_date', '>=', start_of_month),
            ('state', '=', 'done')
        ])
        
        return {
            'new_patients': new_patients,
            'consultations': consultations_month,
            'vaccinations': vaccinations_month
        }
    
    def _get_financial_stats(self):
        """Statistiques financières"""
        today = date.today()
        start_of_month = today.replace(day=1)
        
        # Récupérer la configuration des tarifs
        config = self.env['pediatric.config'].search([], limit=1)
        if not config:
            return {'error': 'Configuration manquante'}
        
        # Consultations du mois par type
        consultations = self.env['pediatric.consultation'].search([
            ('consultation_date', '>=', start_of_month),
            ('state', '=', 'done')
        ])
        
        revenue_by_type = {
            'consultation': 0,
            'control': 0,
            'vaccination': 0,
            'emergency': 0
        }
        
        for consultation in consultations:
            if consultation.consultation_type == 'consultation':
                revenue_by_type['consultation'] += config.consultation_price
            elif consultation.consultation_type == 'control':
                revenue_by_type['control'] += config.control_price
            elif consultation.consultation_type == 'vaccination':
                revenue_by_type['vaccination'] += config.vaccination_price
            elif consultation.consultation_type == 'emergency':
                revenue_by_type['emergency'] += config.emergency_price
        
        total_revenue = sum(revenue_by_type.values())
        
        # Factures impayées
        overdue_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('invoice_date_due', '<', today)
        ])
        
        overdue_amount = sum(overdue_invoices.mapped('amount_residual'))
        
        return {
            'total_revenue': total_revenue,
            'revenue_by_type': revenue_by_type,
            'overdue_amount': overdue_amount,
            'collection_rate': ((total_revenue - overdue_amount) / total_revenue * 100) if total_revenue > 0 else 0
        }
    
    def _get_alerts(self):
        """Récupérer les alertes et notifications"""
        alerts = {
            'urgent': [],
            'follow_up': []
        }
        
        today = date.today()
        
        # RDV manqués
        missed_appointments = self.env['pediatric.appointment'].search([
            ('state', '=', 'no_show'),
            ('appointment_date', '>=', today - timedelta(days=1)),
            ('appointment_date', '<', today)
        ])
        
        for appointment in missed_appointments:
            alerts['urgent'].append({
                'type': 'missed_appointment',
                'message': f'RDV manqué: {appointment.patient_id.name} ({appointment.appointment_date.strftime("%H:%M")})',
                'action': 'call_patient'
            })
        
        # Vaccins en retard
        overdue_vaccines = self.env['pediatric.vaccination'].search([
            ('next_dose_date', '<', today),
            ('state', '=', 'scheduled')
        ])
        
        for vaccine in overdue_vaccines:
            days_overdue = (today - vaccine.next_dose_date).days
            alerts['urgent'].append({
                'type': 'overdue_vaccine',
                'message': f'Vaccin en retard: {vaccine.patient_id.name} - {vaccine.vaccine_id.name} (retard: {days_overdue} jours)',
                'action': 'schedule_vaccine'
            })
        
        # RDV de demain
        tomorrow = today + timedelta(days=1)
        tomorrow_appointments = self.env['pediatric.appointment'].search([
            ('appointment_date', '>=', tomorrow),
            ('appointment_date', '<', tomorrow + timedelta(days=1)),
            ('state', 'in', ['scheduled', 'confirmed'])
        ])
        
        for appointment in tomorrow_appointments:
            alerts['follow_up'].append({
                'type': 'reminder',
                'message': f'RDV demain: {appointment.patient_id.name} ({appointment.appointment_date.strftime("%H:%M")})',
                'action': 'send_reminder'
            })
        
        return alerts
    
    def _get_charts_data(self):
        """Données pour les graphiques"""
        # Évolution mensuelle des 12 derniers mois
        monthly_data = []
        for i in range(12):
            month_date = date.today().replace(day=1) - relativedelta(months=i)
            next_month = month_date + relativedelta(months=1)
            
            consultations = self.env['pediatric.consultation'].search_count([
                ('consultation_date', '>=', month_date),
                ('consultation_date', '<', next_month),
                ('state', '=', 'done')
            ])
            
            monthly_data.append({
                'month': month_date.strftime('%b'),
                'consultations': consultations
            })
        
        monthly_data.reverse()
        
        # Répartition par type de consultation ce mois
        today = date.today()
        start_of_month = today.replace(day=1)
        
        consultation_types = self.env['pediatric.consultation'].read_group([
            ('consultation_date', '>=', start_of_month),
            ('state', '=', 'done')
        ], ['consultation_type'], ['consultation_type'])
        
        return {
            'monthly_evolution': monthly_data,
            'consultation_distribution': consultation_types
        }