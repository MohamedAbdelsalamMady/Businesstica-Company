/** @odoo-module **/

import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PediatricDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.monthlyChartRef = useRef("monthly_chart");
        this.consultationPieRef = useRef("consultation_pie");
        
        onMounted(() => {
            this.loadDashboardData();
            this.initCharts();
        });
    }

    async loadDashboardData() {
        try {
            // Charger les données du tableau de bord
            const today = new Date().toISOString().split('T')[0];
            const startOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0];
            
            // Statistiques du jour
            const todayStats = await this.orm.call("pediatric.consultation", "search_count", [
                [["consultation_date", ">=", today + " 00:00:00"], ["consultation_date", "<=", today + " 23:59:59"]]
            ]);
            
            // Mettre à jour les KPIs
            this.updateKPIs({
                today_patients: todayStats,
                today_consultations: todayStats,
                today_vaccinations: Math.floor(todayStats * 0.3),
                today_revenue: todayStats * 50
            });
            
        } catch (error) {
            console.error("Erreur lors du chargement des données:", error);
        }
    }

    updateKPIs(data) {
        // Mettre à jour les éléments du DOM avec les nouvelles données
        const elements = {
            'today_patients': data.today_patients,
            'today_consultations': data.today_consultations,
            'today_vaccinations': data.today_vaccinations,
            'today_revenue': data.today_revenue + '€'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                // Animation de compteur
                this.animateCounter(element, 0, parseInt(value) || 0);
            }
        });
    }

    animateCounter(element, start, end, duration = 1000) {
        if (isNaN(end)) return;
        
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current) + (element.textContent.includes('€') ? '€' : '');
        }, 16);
    }

    initCharts() {
        // Initialiser les graphiques avec Chart.js
        this.initMonthlyChart();
        this.initConsultationPieChart();
    }

    initMonthlyChart() {
        const ctx = this.monthlyChartRef.el?.getContext('2d');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
                datasets: [{
                    label: 'Chiffre d\'Affaires (€)',
                    data: [8500, 9200, 10100, 11500, 12200, 13100, 12800, 13500, 12900, 14200, 13800, 12450],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '€';
                            }
                        }
                    }
                }
            }
        });
    }

    initConsultationPieChart() {
        const ctx = this.consultationPieRef.el?.getContext('2d');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Consultations', 'Vaccinations', 'Contrôles', 'Urgences'],
                datasets: [{
                    data: [71, 17, 10, 2],
                    backgroundColor: [
                        '#4facfe',
                        '#43e97b',
                        '#fa709a',
                        '#ffecd2'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    async refreshDashboard() {
        // Actualiser les données du tableau de bord
        await this.loadDashboardData();
        
        // Afficher une notification
        this.env.services.notification.add("Tableau de bord actualisé", {
            type: "success"
        });
    }
}

PediatricDashboard.template = "pediatric_management.Dashboard";

// Enregistrer le composant
registry.category("actions").add("pediatric_dashboard", PediatricDashboard);

// Fonctions utilitaires pour les graphiques
window.PediatricDashboardUtils = {
    // Formater les nombres
    formatNumber: (num) => {
        return new Intl.NumberFormat('fr-FR').format(num);
    },
    
    // Formater les montants
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    },
    
    // Calculer les pourcentages
    calculatePercentage: (value, total) => {
        return total > 0 ? Math.round((value / total) * 100) : 0;
    },
    
    // Générer des couleurs aléatoires pour les graphiques
    generateColors: (count) => {
        const colors = [
            '#4facfe', '#43e97b', '#fa709a', '#ffecd2',
            '#667eea', '#764ba2', '#f093fb', '#f5576c'
        ];
        return colors.slice(0, count);
    }
};

// Auto-actualisation du tableau de bord toutes les 5 minutes
setInterval(() => {
    const dashboard = document.querySelector('.o_pediatric_dashboard');
    if (dashboard) {
        // Actualiser seulement si le tableau de bord est visible
        window.location.reload();
    }
}, 300000); // 5 minutes