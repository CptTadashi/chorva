<script setup>
import { onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { filterState } from './services/filterService';

const router = useRouter();
const route = useRoute();

// Admin yo'nalishida ekanligimizni aniqlaymiz
const isAdminRoute = computed(() => route.path.startsWith('/admin'));

const handleFilterChange = () => {
  // Har qanday sahifada bo'lganda ham bosh sahifaga yo'naltiramiz
  if (route.path !== '/') {
    router.push('/');
  }
};

onMounted(() => {
  filterState.fetchCategories();
  filterState.fetchRegions();
});
</script>

<template>
  <div class="app-container">
    <nav class="navbar glass">
      <div class="nav-content">
        <!-- Logo: Contextga qarab yo'nalish o'zgaradi -->
        <router-link :to="isAdminRoute ? '/admin/dashboard' : '/'" class="logo">
          <img src="/logo.png" alt="Buqacha.uz" class="logo-img">
          <span class="logo-text">Buqacha<span class="accent">.uz</span></span>
        </router-link>

        <!-- Filtrlar: Faqat public saytda ko'rinadi -->
        <div v-if="!isAdminRoute" class="nav-filters">
          <div class="header-filter">
            <span class="filter-icon">📂</span>
            <select v-model="filterState.selectedCategory" @change="handleFilterChange" class="header-select">
              <option :value="null">Kategoriyalar</option>
              <option v-for="cat in filterState.categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="filter-divider"></div>
          <div class="header-filter">
            <span class="filter-icon">📍</span>
            <select v-model="filterState.selectedRegion" @change="handleFilterChange" class="header-select">
              <option :value="null">Barcha hududlar</option>
              <option v-for="reg in filterState.regions" :key="reg.id" :value="reg.id">
                {{ reg.name }}
              </option>
            </select>
          </div>
        </div>
        
        <!-- Nav Links: Faqat admin panelida ko'rinadi -->
        <div v-if="isAdminRoute" class="nav-links">
          <router-link to="/admin/dashboard" class="nav-item">Bosh sahifa</router-link>
          <router-link to="/" class="nav-item admin-link">Saytga o'tish</router-link>
        </div>

        <!-- Ommaviy harakatlar: E'lon berish tugmasi -->
        <div v-if="!isAdminRoute" class="nav-actions">
          <a href="https://t.me/buqachauzbot" target="_blank" class="btn-primary add-btn">
            <span class="btn-icon">➕</span>
            <span class="btn_text">E'lon</span>
          </a>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </main>

    <footer class="footer border-t">
      <p>&copy; 2026 Buqachauz e'lonlar sayti. Barcha huquqlar himoyalangan.</p>
    </footer>
  </div>
</template>

<style>
:root {
  --accent-primary: #10b981;
  --accent-secondary: #059669; /* To'qroq yashil */
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --bg-primary: #f9fafb;
  --border-color: rgba(0, 0, 0, 0.1);
  --card-bg: #ffffff;
}

body {
  margin: 0;
  font-family: 'Outfit', 'Inter', sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s, color 0.3s;
}

.glass {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
}

/* Navbar ichidagi matnlar */
.navbar .logo-text, .navbar .nav-item, .navbar .header-select {
  color: var(--text-primary) !important;
}

.navbar .accent {
  color: var(--accent-primary);
}

/* Select iconi */
.navbar .header-select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23111827' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
}

/* Filter pill foni */
.navbar .nav-filters {
  background: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.05);
}
</style>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  z-index: 1000;
  padding: 0 1.2rem;
  margin: 0.8rem 1rem;
  border-radius: 18px;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.3rem;
  font-weight: 800;
  text-decoration: none;
  color: white;
  min-width: 180px;
}

.logo .accent {
  color: var(--accent-primary);
}

.logo-img {
  height: 40px;
  width: auto;
  object-fit: contain;
}

/* Nav Filters Styles */
.nav-filters {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 99px;
  padding: 0 0.5rem;
  height: 44px;
  flex: 0 1 420px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
}

.nav-filters:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.nav-filters:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.header-filter {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 0.8rem;
  gap: 0.4rem;
  position: relative;
}

.filter-icon {
  font-size: 1rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.filter-divider {
  width: 1px;
  height: 20px;
  background: rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.header-select {
  flex: 1;
  padding: 0.4rem 1.4rem 0.4rem 0.2rem;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  outline: none;
  appearance: none;
  min-width: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%234b5563' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right center;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  min-width: 150px;
  justify-content: flex-end;
}

.nav-item {
  font-weight: 500;
  color: var(--text-secondary);
  transition: color 0.3s;
  text-decoration: none;
  font-size: 0.95rem;
}

.nav-item:hover, .router-link-active {
  color: var(--accent-primary);
}

.admin-link {
  font-size: 0.85rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.nav-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 0 0 160px;
}

.add-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.4rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.9rem;
  white-space: nowrap;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-icon {
  font-size: 1rem;
}

.main-content {
  margin-top: 80px; /* Biroz kamaytirildi */
  flex: 1;
  padding: 1.5rem 1rem;
  max-width: 1400px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.footer {
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
  background: #0a0a0a;
}

@media (max-width: 900px) {
  .logo-text { font-size: 1.1rem; }
}

@media (max-width: 650px) {
  .navbar { margin: 0.5rem; padding: 0 0.8rem; }
  .logo-text { display: none; }
  .logo { min-width: auto; }
  .nav-filters { 
    max-width: none; 
    flex: 0 0 auto;
    padding: 0 0.3rem;
  }

  .header-filter {
    position: relative;
    width: 36px;
    height: 36px;
    justify-content: center;
    padding: 0;
    flex: 0 0 auto;
  }

  .filter-icon {
    font-size: 1.1rem;
    position: relative;
    z-index: 1;
    pointer-events: none;
  }

  .header-select {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
    width: 100%;
    height: 100%;
    z-index: 2;
  }

  .filter-divider {
    height: 14px;
    margin: 0;
  }

  .nav-actions {
    flex: 1;
    justify-content: flex-end;
    min-width: auto;
  }
}

@media (max-width: 450px) {
  .nav-content { gap: 0.5rem; }
  .btn_text { display: none; }
  .add-btn { padding: 0.6rem; border-radius: 10px; }
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
</style>
