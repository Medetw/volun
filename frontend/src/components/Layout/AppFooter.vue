<template>
  <footer class="bg-gray-900 text-white">
    <div class="container-custom py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- Logo and description -->
        <div class="col-span-1 md:col-span-2">
          <div class="flex items-center space-x-2 mb-4">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg
                class="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            </div>
            <span class="text-xl font-bold">Волонтерская платформа</span>
          </div>
          <p class="text-gray-300 mb-4">
            Соединяем волонтеров и организации для создания позитивных изменений в обществе. 
            Присоединяйтесь к нашему сообществу и помогайте делать мир лучше!
          </p>
          <div class="flex space-x-4">
            <!-- Instagram -->
            <a
              href="https://www.instagram.com/newmanhub.kz?vrfl=cGg1dGU4NGEwNXZ2"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-400 hover:text-white transition-colors"
            >
              <svg
                class="w-6 h-6"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 110 6.666 3.333 3.333 0 010-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" />
              </svg>
            </a>
            <!-- TikTok -->
            <a
              href="https://www.tiktok.com/@newmanhub?_r=1&_t=ZS-9APTJOWhLS4"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-400 hover:text-white transition-colors"
            >
              <svg
                class="w-6 h-6"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.34 6.34 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.18 8.18 0 004.78 1.52V6.76a4.85 4.85 0 01-1.01-.07z" />
              </svg>
            </a>
          </div>
        </div>

        <!-- Quick links -->
        <div>
          <h3 class="text-lg font-semibold mb-4">
            Быстрые ссылки
          </h3>
          <ul class="space-y-2">
            <li>
              <router-link
                to="/projects"
                class="text-gray-300 hover:text-white transition-colors"
              >
                Найти проекты
              </router-link>
            </li>
            <li>
              <router-link
                to="/register/volunteer"
                class="text-gray-300 hover:text-white transition-colors"
              >
                Стать волонтером
              </router-link>
            </li>
            <li>
              <router-link
                to="/register/organization"
                class="text-gray-300 hover:text-white transition-colors"
              >
                Для организаций
              </router-link>
            </li>
            <li>
              <router-link
                to="/news"
                class="text-gray-300 hover:text-white transition-colors"
              >
                Новости
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Support -->
        <div>
          <h3 class="text-lg font-semibold mb-4">
            Поддержка
          </h3>
          <ul class="space-y-2">
            <li>
              <a
                href="#"
                class="text-gray-300 hover:text-white transition-colors"
              >
                Помощь
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-gray-300 hover:text-white transition-colors"
              >
                FAQ
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-gray-300 hover:text-white transition-colors"
              >
                Контакты
              </a>
            </li>
            <li>
              <a
                href="#"
                class="text-gray-300 hover:text-white transition-colors"
              >
                Политика конфиденциальности
              </a>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h3 class="text-lg font-semibold mb-4">
            Контакты
          </h3>
          <div class="space-y-2">
            <div class="flex items-center space-x-2">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
              <span class="text-gray-300">info@volunteer-platform.kz</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                />
              </svg>
              <span class="text-gray-300">+7 (727) 123-45-67</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span class="text-gray-300">г. Алматы, ул. Абая 120</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom section -->
      <div class="mt-12 pt-8 border-t border-gray-800">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-gray-400 text-sm">
            © {{ currentYear }} Волонтерская платформа. Все права защищены.
          </p>
          <div class="flex space-x-6 mt-4 md:mt-0">
            <a
              href="#"
              class="text-gray-400 hover:text-white text-sm transition-colors"
            >
              Условия использования
            </a>
            <a
              href="#"
              class="text-gray-400 hover:text-white text-sm transition-colors"
            >
              Политика конфиденциальности
            </a>
            <a
              href="#"
              class="text-gray-400 hover:text-white text-sm transition-colors"
            >
              Cookie политика
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>
