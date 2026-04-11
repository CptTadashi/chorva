<script setup>
import AdminSidebar from './AdminSidebar.vue';
import AdminBottomNav from './AdminBottomNav.vue';
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar />
    <AdminBottomNav />
    <main class="admin-main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  gap: 2rem;
  padding: 1.5rem;
  min-height: 100vh;
  background: var(--bg-color);
}

.admin-main-content {
  flex: 1;
  min-width: 0; /* Flex childlar uchun overflow oldini oladi */
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
    padding: 1rem 1rem 80px 1rem;
    gap: 1rem;
  }
}
</style>
