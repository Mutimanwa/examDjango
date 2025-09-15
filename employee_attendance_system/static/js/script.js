// JavaScript personnalisé pour le système de gestion des présences

document.addEventListener('DOMContentLoaded', function() {
    // Animation d'apparition des éléments
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Confirmation de suppression
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-hide des alertes
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Validation des formulaires
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Filtres de recherche en temps réel
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const targetSelector = this.getAttribute('data-search');
            const targetElements = document.querySelectorAll(targetSelector);
            
            targetElements.forEach(element => {
                const text = element.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    element.style.display = '';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    });

    // Mise à jour automatique de l'heure
    function updateTime() {
        const timeElements = document.querySelectorAll('.current-time');
        const now = new Date();
        const timeString = now.toLocaleTimeString('fr-FR');
        timeElements.forEach(element => {
            element.textContent = timeString;
        });
    }

    // Mettre à jour l'heure toutes les secondes
    setInterval(updateTime, 1000);
    updateTime(); // Mise à jour immédiate

    // Gestion des modales
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Gestion des onglets
    const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetTab = document.querySelector(this.getAttribute('href'));
            if (targetTab) {
                // Masquer tous les onglets
                const allTabs = document.querySelectorAll('.tab-pane');
                allTabs.forEach(tab => tab.classList.remove('show', 'active'));
                
                // Désactiver tous les liens
                const allLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
                allLinks.forEach(link => link.classList.remove('active'));
                
                // Activer l'onglet sélectionné
                this.classList.add('active');
                targetTab.classList.add('show', 'active');
            }
        });
    });

    // Export des données en CSV
    window.exportToCSV = function(tableId, filename) {
        const table = document.getElementById(tableId);
        if (!table) return;

        let csv = [];
        const rows = table.querySelectorAll('tr');
        
        rows.forEach(row => {
            const cols = row.querySelectorAll('td, th');
            const rowData = [];
            cols.forEach(col => {
                rowData.push('"' + col.textContent.replace(/"/g, '""') + '"');
            });
            csv.push(rowData.join(','));
        });

        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Fonction de formatage des nombres
    window.formatNumber = function(num) {
        return new Intl.NumberFormat('fr-FR').format(num);
    };

    // Fonction de formatage des devises
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    };

    // Gestion des filtres de date
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // Confirmation avant calcul des salaires
    const calculateSalaryBtn = document.querySelector('#calculate-salary-btn');
    if (calculateSalaryBtn) {
        calculateSalaryBtn.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir calculer les salaires pour ce mois ? Cette action ne peut pas être annulée.')) {
                e.preventDefault();
            }
        });
    }

    // Animation de chargement
    window.showLoading = function(element) {
        const originalContent = element.innerHTML;
        element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Chargement...';
        element.disabled = true;
        
        return function() {
            element.innerHTML = originalContent;
            element.disabled = false;
        };
    };

    // Gestion des erreurs AJAX
    window.handleAjaxError = function(xhr, status, error) {
        console.error('Erreur AJAX:', error);
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <strong>Erreur!</strong> Une erreur s'est produite lors du traitement de votre demande.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
    };

    // Fonction utilitaire pour les requêtes AJAX
    window.ajaxRequest = function(url, method = 'GET', data = null) {
        return fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: data ? JSON.stringify(data) : null
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur réseau');
            }
            return response.json();
        })
        .catch(error => {
            handleAjaxError(null, null, error);
            throw error;
        });
    };
});
