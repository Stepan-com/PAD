document.addEventListener('DOMContentLoaded', function() {
    // Функция для сохранения города в Local Storage
    function saveCityToLocalStorage(city) {
        let visitedCities = JSON.parse(localStorage.getItem('visited_cities')) || [];
        if (!visitedCities.includes(city)) {
            visitedCities.push(city);
        }
        if (visitedCities.length > 5) {
            visitedCities.shift();  // Удаляем старейший город, если их больше 5
        }
        localStorage.setItem('visited_cities', JSON.stringify(visitedCities));
    }

    // Функция для отображения списка посещённых городов на странице
    function displayVisitedCities() {
        let visitedCities = JSON.parse(localStorage.getItem('visited_cities')) || [];
        let listElement = document.getElementById('visited-cities-list');
        listElement.innerHTML = '';  // Очистить текущее содержимое

        visitedCities.forEach(city => {
            let listItem = document.createElement('li');
            listItem.textContent = city;
            listElement.appendChild(listItem);
        });
    }

    // Обновляем список при загрузке страницы
    displayVisitedCities();

    // Обрабатываем отправку формы
    document.getElementById('city-form').addEventListener('submit', function(event) {
        let city = document.getElementById('id_city').value.trim();
        if (city) {
            saveCityToLocalStorage(city);
        }
        // Не нужно отменять стандартное поведение формы, иначе данные не будут отправлены на сервер
    });
});
