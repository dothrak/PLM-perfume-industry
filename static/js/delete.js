<script>
    // Fonction pour supprimer un produit
    function deleteProduct(productId) {
        // Confirmer la suppression avec l'utilisateur
        if (confirm("Are you sure you want to delete this product?")) {
            // Effectuer la requête DELETE avec fetch
            fetch(`/delete-product/${productId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => {
                if (response.ok) {
                    // Supprimer la carte du produit du DOM
                    document.getElementById(`product-card-${productId}`).remove();
                } else {
                    alert("Failed to delete product.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred while deleting the product.");
            });
        }
    }
</script>
