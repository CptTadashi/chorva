import { createRouter, createWebHistory } from 'vue-router';

// Kelajakda yaratiladigan sahifalar uchun placeholderlar
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/public/HomeView.vue')
  },
  {
    path: '/ad/:id',
    name: 'AdDetail',
    component: () => import('../views/public/AdDetailView.vue')
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/admin/LoginView.vue')
  },
  {
    path: '/admin',
    component: () => import('../views/admin/layout/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/admin/DashboardView.vue')
      },
      {
        path: 'moderation',
        name: 'AdminModeration',
        component: () => import('../views/admin/ModerationView.vue')
      },
      {
        path: 'ads',
        name: 'AdsManagement',
        component: () => import('../views/admin/AdsManagementView.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/admin/UsersView.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/admin/SettingsView.vue')
      },
      {
        path: 'staff',
        name: 'Staff',
        component: () => import('../views/admin/StaffView.vue')
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
