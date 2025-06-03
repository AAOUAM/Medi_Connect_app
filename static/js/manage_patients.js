document.addEventListener('DOMContentLoaded', function () {
    // Confirmation de suppression améliorée
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            const patientName = event.target.querySelector('button[data-patient-name]')?.dataset.patientName || 'ce patient';
            const confirmation = confirm(`Êtes-vous sûr de vouloir supprimer ${patientName} ? Cette action est irréversible.`);
            if (!confirmation) {
                event.preventDefault(); // Annuler la soumission du formulaire
            }
        });
    });

    // Logique de recherche (simple filtre côté client pour l'exemple)
    const searchInput = document.getElementById('searchPatientInput');
    const searchButton = document.getElementById('searchPatientButton');
    const patientsTable = document.getElementById('patientsTable');
    const tableRows = patientsTable ? patientsTable.querySelectorAll('tbody tr') : [];

    function filterTable() {
        const searchTerm = searchInput.value.toLowerCase();
        tableRows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            if (rowText.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    if (searchButton) {
        searchButton.addEventListener('click', filterTable);
    }
    if (searchInput) {
        searchInput.addEventListener('keyup', function(event) {
            // Filtrer en temps réel ou sur Entrée
            if (event.key === 'Enter' || searchInput.value.length === 0 || searchInput.value.length > 2) {
                filterTable();
            }
        });
    }
    

    // Logique de tri des colonnes
    const sortableHeaders = document.querySelectorAll('.entity-table th[data-sortable="true"]');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function () {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            const currentSortOrder = this.dataset.sortOrder || 'desc'; // Default to desc for next sort
            const newSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
            this.dataset.sortOrder = newSortOrder;

            // Reset other headers' sort indicators
            sortableHeaders.forEach(th => {
                th.classList.remove('sorted', 'sorted-asc', 'sorted-desc');
                // Reset icon to default sort
                const sortIcon = th.querySelector('i.fas');
                if(sortIcon) {
                    sortIcon.classList.remove('fa-sort-up', 'fa-sort-down');
                    sortIcon.classList.add('fa-sort');
                }
            });
            
            // Set current header's sort indicator
            this.classList.add('sorted', newSortOrder === 'asc' ? 'sorted-asc' : 'sorted-desc');
            const sortIcon = this.querySelector('i.fas');
             if(sortIcon) {
                sortIcon.classList.remove('fa-sort', 'fa-sort-up', 'fa-sort-down');
                sortIcon.classList.add(newSortOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down');
            }


            const rowsArray = Array.from(tbody.querySelectorAll('tr'));

            rowsArray.sort((a, b) => {
                let valA = a.children[columnIndex].textContent.trim().toLowerCase();
                let valB = b.children[columnIndex].textContent.trim().toLowerCase();

                // Attempt to convert to number for numeric sort if applicable
                const numA = parseFloat(valA);
                const numB = parseFloat(valB);

                if (!isNaN(numA) && !isNaN(numB)) {
                    valA = numA;
                    valB = numB;
                } else if (this.dataset.column === 'date_naissance') { // Specific for date
                    // Assuming YYYY-MM-DD format for dates
                    valA = new Date(valA.split('/').reverse().join('-') || 0); // Convert DD/MM/YYYY to YYYY-MM-DD for Date obj
                    valB = new Date(valB.split('/').reverse().join('-') || 0);
                }


                if (valA < valB) {
                    return newSortOrder === 'asc' ? -1 : 1;
                }
                if (valA > valB) {
                    return newSortOrder === 'asc' ? 1 : -1;
                }
                return 0;
            });

            rowsArray.forEach(row => tbody.appendChild(row)); // Re-append rows in sorted order
        });
    });

});