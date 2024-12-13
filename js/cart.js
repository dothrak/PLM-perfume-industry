const addToCart = (productName, productPrice) => {
    const product = {
        name: productName,
        price: productPrice
    };

    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart.push(product);
    localStorage.setItem("cart", JSON.stringify(cart));

    updateCartIcon();
};

const updateCartIcon = () => {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const cartCount = cart.length;
    
    // Mettez à jour le bon élément pour afficher le compteur
    const cartIcon = document.querySelector("#cart-count");
    if (cartIcon) {
        cartIcon.textContent = cartCount;
    }
};

window.onload = () => {
    updateCartIcon();
};

document.querySelectorAll(".add-to-cart").forEach(cartButton => {
    cartButton.addEventListener("click", function() {
        const productName = this.closest(".card").querySelector("h3").textContent;
        const productPrice = this.closest(".card").querySelector("p.text-center").textContent.trim();

        addToCart(productName, productPrice);
    });
});
const updateCartPopup = () => {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const cartItemsList = document.getElementById("cart-items");
    const cartTotal = document.getElementById("cart-total");

    cartItemsList.innerHTML = '';  // Clear previous items
    let total = 0;

    cart.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.name} - ${item.price}`;
        cartItemsList.appendChild(li);

        const price = parseFloat(item.price.replace(/[^0-9.-]+/g,""));  // Parse price
        total += price;
    });

    cartTotal.textContent = `$${total.toFixed(2)}`;
};

