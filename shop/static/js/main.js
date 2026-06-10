document.addEventListener('DOMContentLoaded', () => {
    const productList = document.getElementById('product-list');
    const spinner = document.getElementById('loading-spinner');

    // 1. Функция загрузки товаров с API
    async function loadProducts() {
        try {
            spinner.style.display = 'block';
            const response = await fetch('/api/products/');
            
            if (!response.ok) throw new Error('Ошибка загрузки данных с сервера');
            
            const products = await response.json();
            // В main.js, где вы формируете productHTML:
    productList.innerHTML += `
        <div class="col-md-4 mb-4">
            <div class="card h-100 shadow-sm p-3"> <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text text-muted">${product.price} ₽</p>
                    <div class="mt-auto">
                        <a href="/catalog/${product.id}/" class="btn btn-outline-primary w-100 mb-2">Подробнее</a>
                        <button class="btn btn-success w-100 add-to-cart" data-id="${product.id}">
                            Добавить в корзину
                        </button>
                    </div>
                </div>
            </div>
        </div>`;

            products.forEach(product => {
    productList.innerHTML += `
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text text-muted">${product.price} ₽</p>
                    
                    <div class="mt-auto">
                        <a href="/catalog/${product.id}/" class="btn btn-outline-primary w-100 mb-2">
                            Подробнее
                        </a>
                        
                        <button class="btn btn-success w-100 add-to-cart" data-id="${product.id}">
                            В корзину
                        </button>
                    </div>
                </div>
            </div>
        </div>`;
});
        } catch (error) {
            console.error(error);
            productList.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger text-center">
                        Не удалось загрузить товары: ${error.message}
                    </div>
                </div>`;
        } finally {
            spinner.style.display = 'none';
        }
    }

    // 2. Делегирование событий: слушаем клики на весь список
    productList.addEventListener('click', (e) => {
        if (e.target.classList.contains('add-to-cart')) {
            const productId = e.target.dataset.id;
            addToCart(productId);
        }
    });

    // 3. Функция добавления в корзину (POST запрос)
    async function addToCart(productId) {
        // Получаем CSRF-токен из мета-тега или скрытого поля
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        try {
            const response = await fetch('/api/cart/add/', {
                method: 'POST',
                headers: { 
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify({ product_id: productId })
            });

            if (response.ok) {
                showToast('Товар успешно добавлен в корзину!', 'success');
            } else {
                throw new Error('Не удалось добавить товар');
            }
        } catch (error) {
            showToast(error.message, 'danger');
        }
    }

    // 4. Уведомления (Bootstrap Toast)
    function showToast(message, type) {
        const toastContainer = document.getElementById('toast-container');
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>`;
        
        toastContainer.innerHTML = toastHTML;
        const toastElement = new bootstrap.Toast(toastContainer.querySelector('.toast'));
        toastElement.show();
    }

    // Запуск при загрузке страницы
    loadProducts();
});