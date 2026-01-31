<template>
  <div id="app" class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">Волонтерская платформа</h1>
          </div>
          <nav class="flex items-center space-x-4">
            <a href="#" class="text-gray-600 hover:text-gray-900">Главная</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">Проекты</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">О нас</a>
            <button class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
              Войти
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- Hero Section -->
      <section class="text-center py-12">
        <h2 class="text-4xl font-bold text-gray-900 mb-4">
          Добровольцы меняют мир
        </h2>
        <p class="text-xl text-gray-600 mb-8">
          Присоединяйтесь к сообществу людей, которые делают мир лучше
        </p>
        <div class="space-x-4">
          <button class="bg-blue-600 text-white px-6 py-3 rounded-md text-lg hover:bg-blue-700">
            Стать волонтером
          </button>
          <button class="bg-green-600 text-white px-6 py-3 rounded-md text-lg hover:bg-green-700">
            Создать проект
          </button>
        </div>
      </section>

      <!-- Features -->
      <section class="py-12">
        <h3 class="text-2xl font-bold text-center text-gray-900 mb-8">
          Как это работает
        </h3>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span class="text-blue-600 text-2xl">1</span>
            </div>
            <h4 class="text-lg font-semibold mb-2">Найдите проект</h4>
            <p class="text-gray-600">Выберите из сотен волонтерских проектов</p>
          </div>
          <div class="text-center">
            <div class="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span class="text-green-600 text-2xl">2</span>
            </div>
            <h4 class="text-lg font-semibold mb-2">Присоединяйтесь</h4>
            <p class="text-gray-600">Подайте заявку и станьте частью команды</p>
          </div>
          <div class="text-center">
            <div class="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span class="text-purple-600 text-2xl">3</span>
            </div>
            <h4 class="text-lg font-semibold mb-2">Делайте добро</h4>
            <p class="text-gray-600">Помогайте другим и меняйте мир к лучшему</p>
          </div>
        </div>
      </section>

      <!-- Stats -->
      <section class="bg-white rounded-lg shadow p-8">
        <h3 class="text-2xl font-bold text-center text-gray-900 mb-8">
          Наша статистика
        </h3>
        <div class="grid md:grid-cols-4 gap-6 text-center">
          <div>
            <div class="text-3xl font-bold text-blue-600">1,234</div>
            <div class="text-gray-600">Волонтеров</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-green-600">567</div>
            <div class="text-gray-600">Проектов</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-purple-600">89</div>
            <div class="text-gray-600">Организаций</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-orange-600">12,345</div>
            <div class="text-gray-600">Часов помощи</div>
          </div>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-8">
          <div>
            <h4 class="text-lg font-semibold mb-4">О платформе</h4>
            <p class="text-gray-300">
              Соединяем волонтеров с организациями, которые нуждаются в помощи
            </p>
          </div>
          <div>
            <h4 class="text-lg font-semibold mb-4">Быстрые ссылки</h4>
            <ul class="space-y-2 text-gray-300">
              <li><a href="#" class="hover:text-white">Как это работает</a></li>
              <li><a href="#" class="hover:text-white">Найти проект</a></li>
              <li><a href="#" class="hover:text-white">Создать проект</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-lg font-semibold mb-4">Поддержка</h4>
            <ul class="space-y-2 text-gray-300">
              <li><a href="#" class="hover:text-white">FAQ</a></li>
              <li><a href="#" class="hover:text-white">Контакты</a></li>
              <li><a href="#" class="hover:text-white">Правила</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-lg font-semibold mb-4">Следите за нами</h4>
            <div class="flex space-x-4">
              <a href="#" class="text-gray-300 hover:text-white">Facebook</a>
              <a href="#" class="text-gray-300 hover:text-white">Twitter</a>
              <a href="#" class="text-gray-300 hover:text-white">Instagram</a>
            </div>
          </div>
        </div>
        <div class="border-t border-gray-700 mt-8 pt-8 text-center text-gray-300">
          <p>&copy; 2024 Волонтерская платформа. Все права защищены.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Простая тестовая страница без зависимостей от API
console.log('TestApp loaded successfully!')
</script>
