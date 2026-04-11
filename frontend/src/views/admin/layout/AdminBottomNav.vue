<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const role = localStorage.getItem('admin_role');

const menuItems = computed(() => {
  const items = [
    { name: 'Dash', path: '/admin/dashboard', icon: '📊', roles: ['superadmin'] },
    { name: 'Mod.', path: '/admin/moderation', icon: '🛡️', roles: ['superadmin', 'moderator'] },
    { name: 'E\'lon', path: '/admin/ads', icon: '📝', roles: ['superadmin', 'moderator'] },
    { name: 'Sozl.', path: '/admin/settings', icon: '⚙️', roles: ['superadmin'] },
    { name: 'Jamoa', path: '/admin/staff', icon: '👨‍✈️', roles: ['superadmin'] },
  ];
  return items.filter(item => item.roles.includes(role));
});
</script>

<template>
  <div class="admin-bottom-nav glass">
    <router-link 
      v-for="item in menuItems" 
      :key="item.path" 
      :to="item.path"
      class="nav-tab"
      :class="{ active: route.path === item.path }"
    >
      <span class="icon">{{ item.icon }}</span>
      <span class="label">{{ item.name }}</span>
    </router-link>
  </div>
</template>

<style scoped>
.admin-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 65px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 0.5rem;
  z-index: 2000;
  border-top: 1px solid var(--border-color);
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -5px 25px rgba(0, 0, 0, 0.05);
  display: none; /* Desktopda yashirin */
}

.nav-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: var(--text-secondary);
  gap: 4px;
  flex: 1;
  transition: all 0.3s;
}

.nav-tab .icon {
  font-size: 1.2rem;
}

.nav-tab .label {
  font-size: 0.65rem;
  font-weight: 600;
}

.nav-tab.active {
  color: var(--accent-primary);
}

.nav-tab.active .icon {
  transform: scale(1.2);
}

@media (max-width: 768px) {
  .admin-bottom-nav {
    display: flex;
  }
}
</style>
