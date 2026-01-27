<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/Layout/AppHeader.vue'
import AppFooter from '@/components/Layout/AppFooter.vue'

const authStore = useAuthStore()

onMounted(async () => {
  // Initialize authentication state
  await authStore.initializeAuth()
})
</script>

<template>
  <div id="app" class="min-h-screen flex flex-col">
    <AppHeader />
    
    <main class="flex-grow">
      <router-view />
    </main>
    
    <AppFooter />
  </div>
</template>

<style>
/* Global styles are in assets/main.css */
</style>
