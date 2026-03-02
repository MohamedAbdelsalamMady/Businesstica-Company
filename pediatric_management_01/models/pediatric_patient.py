# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta  # Indispensable pour l'âge précis

class PediatricPatient(models.Model):
    _name = 'pediatric.patient'
    _description = 'Patient Pédiatrique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    # --- IDENTIFICATION ---
    ref = fields.Char(string='Référence Dossier', required=True, copy=False, readonly=True, default='Nouveau')
    last_name = fields.Char(string='Nom', required=True, tracking=True)
    first_name = fields.Char(string='Prénom', required=True, tracking=True)
    name = fields.Char(string='Nom complet', compute='_compute_name', store=True, readonly=True)
    photo = fields.Image(string="Photo", max_width=128, max_height=128)

    # --- DATES ET AGE ---
    date_of_birth = fields.Date(string='Date de naissance', required=True, tracking=True)
    
    # Champ entier pour les tris et graphiques
    age = fields.Integer(string="Âge (Années)", compute="_compute_age", store=True)
    
    # C'EST CE CHAMP QUI MANQUAIT ET QUI CAUSAIT L'ERREUR RPC
    age_display = fields.Char(
        string='Âge affiché', 
        compute='_compute_age_display', 
        store=True,
        help="Affiche l'âge sous forme '2 mois' ou '3 ans'"
    )
    
    # Pour le Dashboard (Statistiques par catégorie)
    age_group = fields.Selection([
        ('baby', 'Nourrisson (0-2 ans)'),
        ('child', 'Enfant (2-12 ans)'),
        ('teen', 'Adolescent (12+ ans)')
    ], string="Tranche d'âge", compute="_compute_age_group", store=True)

    gender = fields.Selection([('m', 'Masculin'), ('f', 'Féminin')], string='Sexe', required=True, tracking=True)

    # --- PARENTS & CONTACT ---
    parent_id = fields.Many2one('res.partner', string='Parent/Responsable', tracking=True)
    mobile = fields.Char(related='parent_id.mobile', readonly=False, string='Mobile Parent')
    email = fields.Char(related='parent_id.email', readonly=False)

    # --- DONNÉES MÉDICALES ---
    blood_group = fields.Selection([
        ('a_p', 'A+'), ('a_n', 'A-'), ('b_p', 'B+'), ('b_n', 'B-'),
        ('ab_p', 'AB+'), ('ab_n', 'AB-'), ('o_p', 'O+'), ('o_n', 'O-'),
    ], string='Groupe Sanguin')
    
    weight = fields.Float(string='Poids (kg)')
    height = fields.Float(string='Taille (cm)')

    consultation_ids = fields.One2many('pediatric.consultation', 'patient_id', string='Consultations')

    # --- CALCULS ---

    @api.depends('last_name', 'first_name')
    def _compute_name(self):
        for rec in self:
            nom = rec.last_name or ''
            prenom = rec.first_name or ''
            rec.name = f"{nom.upper()} {prenom.title()}".strip()

    @api.depends('date_of_birth')
    def _compute_age(self):
        """ Calcul simple de l'âge en années pour le tri """
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                dob = rec.date_of_birth
                rec.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                rec.age = 0

    @api.depends('date_of_birth')
    def _compute_age_display(self):
        """ Calcul précis pour l'affichage (ex: 14 mois) """
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                d = relativedelta(today, rec.date_of_birth)
                
                if d.years == 0:
                    rec.age_display = f"{d.months} mois"
                elif d.years == 1:
                    rec.age_display = f"{d.years} an {d.months} mois"
                else:
                    rec.age_display = f"{d.years} ans"
            else:
                rec.age_display = "N/A"

    @api.depends('age')
    def _compute_age_group(self):
        """ Détermine la catégorie pour les graphiques du dashboard """
        for rec in self:
            if rec.age < 2: 
                rec.age_group = 'baby'
            elif rec.age < 12: 
                rec.age_group = 'child'
            else: 
                rec.age_group = 'teen'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'Nouveau') == 'Nouveau':
                vals['ref'] = self.env['ir.sequence'].next_by_code('pediatric.patient') or 'Nouveau'
        return super(PediatricPatient, self).create(vals_list)