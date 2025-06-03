document.addEventListener('DOMContentLoaded', function () {
  // Graphique des statistiques générales (votre code existant est bon)
  const statsChartCanvas = document.getElementById('statsChart');
  if (statsChartCanvas) {
    const ctxStats = statsChartCanvas.getContext('2d');
    
    const nbPatients = parseInt(statsChartCanvas.dataset.nbPatients) || 0;
    const nbMedecins = parseInt(statsChartCanvas.dataset.nbMedecins) || 0;
    const nbConsultations = parseInt(statsChartCanvas.dataset.nbConsultations) || 0;
    const nbUtilisateurs = parseInt(statsChartCanvas.dataset.nbUtilisateurs) || 0;
    
    const maxStatValue = Math.max(nbPatients, nbMedecins, nbConsultations, nbUtilisateurs, 1);
    const stepSizeStats = Math.max(1, Math.ceil(maxStatValue / 10));

    new Chart(ctxStats, {
      type: 'bar',
      data: {
        labels: ['Patients', 'Médecins', 'Consultations', 'Utilisateurs'],
        datasets: [{
          label: 'Nombre total',
          data: [nbPatients, nbMedecins, nbConsultations, nbUtilisateurs],
          backgroundColor: [
            'rgba(52, 152, 219, 0.7)',
            'rgba(46, 204, 113, 0.7)',
            'rgba(230, 126, 34, 0.7)',
            'rgba(155, 89, 182, 0.7)'
          ],
          borderColor: [
            'rgba(52, 152, 219, 1)',
            'rgba(46, 204, 113, 1)',
            'rgba(230, 126, 34, 1)',
            'rgba(155, 89, 182, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
                stepSize: stepSizeStats
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
          title: {
            display: true,
            text: 'Aperçu des Entités du Système'
          }
        }
      }
    });
  }

  // Graphique de l'évolution mensuelle (MODIFIÉ)
  const anotherChartCanvas = document.getElementById('anotherChart');
  if (anotherChartCanvas) {
    const ctxAnother = anotherChartCanvas.getContext('2d');

    let monthlyLabels = [];
    let monthlyData = [];

    try {
        // Récupérer les chaînes JSON des attributs data-*
        const labelsJson = anotherChartCanvas.dataset.labels;
        const valuesJson = anotherChartCanvas.dataset.values;

        // Parser les chaînes JSON en tableaux JavaScript
        // S'assurer que les attributs existent avant de parser
        if (labelsJson) {
            monthlyLabels = JSON.parse(labelsJson);
        }
        if (valuesJson) {
            monthlyData = JSON.parse(valuesJson);
        }
    } catch (e) {
        console.error("Erreur lors du parsing des données du graphique mensuel:", e);
        // Fallback à des données vides ou un message d'erreur si le parsing échoue
        monthlyLabels = ['Erreur de données'];
        monthlyData = [0];
    }
    
    // S'assurer qu'il y a des données pour éviter les erreurs avec Math.max sur un tableau vide
    const maxMonthlyValue = monthlyData.length > 0 ? Math.max(...monthlyData, 1) : 1;
    const stepSizeMonthly = Math.max(1, Math.ceil(maxMonthlyValue / 10));

    new Chart(ctxAnother, {
        type: 'line',
        data: {
            labels: monthlyLabels, // Utiliser les labels parsés
            datasets: [{
                label: 'Consultations par Mois',
                data: monthlyData, // Utiliser les données parsées
                fill: true, // Remplissage sous la ligne
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1 // Lissage de la courbe
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: stepSizeMonthly // Échelonnement dynamique
                    }
                },
                x: { // Options pour l'axe X si beaucoup de labels
                    ticks: {
                        autoSkip: true, // Sauter des labels si trop nombreux
                        maxTicksLimit: 12 // Nombre max de labels affichés
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Évolution Mensuelle des Consultations' // Titre mis à jour
                },
                legend: {
                    display: true, // Afficher la légende
                    position: 'top'
                }
            }
        }
    });
  }

  // Gestion de la classe 'active' pour la sidebar
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll('.sidebar-nav li a');
  
  // URL de base du dashboard (à ajuster si votre route est différente)
  // Il est plus sûr de récupérer cette URL depuis un élément HTML si possible,
  // car la reconstruction en JS peut être faillible si la structure de l'URL change.
  // Pour l'instant, on se base sur une correspondance directe ou une URL racine.
  const dashboardAdminUrl = document.querySelector('.sidebar-nav li a[href*="dashboard_admin"]')?.getAttribute('href') || '/admin/dashboard'; // Fallback

  sidebarLinks.forEach(link => {
    const linkParent = link.parentElement;
    linkParent.classList.remove('active'); // D'abord, tout désactiver
    
    const linkHref = link.getAttribute('href');

    // Gérer le cas où le dashboard est à la racine de l'admin ou la page actuelle est la racine
    if (linkHref === currentPath) {
        linkParent.classList.add('active');
    } else if (currentPath === '/' && linkHref === dashboardAdminUrl) { // Si la page est la racine et le lien est le dashboard
        linkParent.classList.add('active');
    }
    // Si le lien est celui du tableau de bord et qu'aucune autre correspondance plus spécifique n'a été trouvée
    // ET que le chemin actuel commence par le chemin du tableau de bord (utile si dashboard_admin est un préfixe)
    // Cette dernière condition est plus complexe et peut ne pas être nécessaire si les liens sont exacts.
  });
  let isAnyLinkActive = false;
  sidebarLinks.forEach(link => {
      if (link.parentElement.classList.contains('active')) {
          isAnyLinkActive = true;
      }
  });

  if (!isAnyLinkActive) {
      sidebarLinks.forEach(link => {
          const linkHref = link.getAttribute('href');
          if (linkHref === dashboardAdminUrl && currentPath.startsWith(dashboardAdminUrl.substring(0, dashboardAdminUrl.lastIndexOf('/')))) { // Comparaison de base pour le dashboard
              link.parentElement.classList.add('active');
          } else if (linkHref === '/' && currentPath === '/') { // Cas racine
               link.parentElement.classList.add('active');
          }
      });
  }

});