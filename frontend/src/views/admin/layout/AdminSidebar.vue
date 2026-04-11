<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const role = localStorage.getItem('admin_role');
const username = localStorage.getItem('admin_user');

const menuItems = computed(() => {
  const items = [
    { name: 'Dashboard', path: '/admin/dashboard', icon: '📊', roles: ['superadmin'] },
    { name: 'Moderatsiya', path: '/admin/moderation', icon: '🛡️', roles: ['superadmin', 'moderator'] },
    { name: 'Barcha E\'lonlar', path: '/admin/ads', icon: '📝', roles: ['superadmin', 'moderator'] },
    { name: 'Foydalanuvchilar', path: '/admin/users', icon: '👥', roles: ['superadmin'] },
    { name: 'Sozlamalar', path: '/admin/settings', icon: '⚙️', roles: ['superadmin'] },
    { name: 'Jamoa', path: '/admin/staff', icon: '👨‍✈️', roles: ['superadmin'] },
  ];
  return items.filter(item => item.roles.includes(role));
});

const handleLogout = () => {
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_user');
  localStorage.removeItem('admin_role');
  router.push('/admin/login');
};
</script>

<template>
  <aside class="admin-sidebar glass">
    <div class="sidebar-header">
      <div class="admin-profile">
        <div class="avatar">{{ username?.charAt(0).toUpperCase() }}</div>
        <div class="info">
          <p class="name">{{ username }}</p>
          <p class="role-badge">{{ role }}</p>
        </div>
      </div>
    </div>

    <nav class="sidebar-nav">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path" 
        :to="item.path"
        class="nav-link"
        :class="{ active: route.path === item.path }"
      >
        <span class="icon">{{ item.icon }}</span>
        <span class="text">{{ item.name }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <button @click="handleLogout" class="logout-btn">
        <span class="icon">🚪</span>
        <span class="text">Chiqish</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.admin-sidebar {
  width: 280px;
  height: calc(100vh - 40px);
  position: sticky;
  top: 20px;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  border-radius: 25px;
}

.sidebar-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.admin-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 45px;
  height: 45px;
  background: var(--accent-primary);
  color: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
}

.name {
  font-weight: 600;
  font-size: 1rem;
}

.role-badge {
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--accent-primary);
  letter-spacing: 1px;
  font-weight: 700;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 15px;
  color: var(--text-secondary);
  transition: all 0.3s;
  text-decoration: none;
}

.nav-link:hover, .nav-link.active {
  background: rgba(16, 185, 129, 0.08);
  color: var(--accent-primary);
}

.nav-link.active {
  border: 1px solid var(--accent-primary);
  font-weight: 600;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 15px;
  background: transparent;
  border: 1px solid transparent;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.2);
}
@media (max-width: 768px) {
  .admin-sidebar {
    display: none;
  }
}
</style>
