<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

const authStore = useAuthStore()
const router = useRouter()

const showNavbar = computed(() => {
  return authStore.isAuthenticated
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar v-if="showNavbar" />
    <main :class="showNavbar ? 'pt-16' : ''">
      <router-view />
    </main>
  </div>
</template>
