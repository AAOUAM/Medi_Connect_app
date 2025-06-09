// static/js/dashboard_medecin.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Sélectionne tous les boutons/liens de suppression
    const deleteButtons = document.querySelectorAll('.btn-delete');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            // Empêche le lien de suivre son URL immédiatement
            event.preventDefault(); 

            // Affiche une boîte de dialogue de confirmation
            const userConfirmed = confirm("Êtes-vous sûr de vouloir supprimer cette consultation ? Cette action est irréversible.");

            // Si l'utilisateur clique sur "OK", on procède à la suppression
            if (userConfirmed) {
                // Redirige vers l'URL de suppression
                window.location.href = this.href;
            }
            // Si l'utilisateur clique sur "Annuler", rien ne se passe.
        });
    });

});