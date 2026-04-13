<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '../../services/api';
import { filterState } from '../../services/filterService';

const ads = ref([]);
const loading = ref(true);
const loadingMore = ref(false);
const page = ref(1);
const hasMore = ref(true);
const limit = 12;

const fetchAds = async (isLoadMore = false) => {
  if (isLoadMore) loadingMore.value = true;
  else {
    loading.value = true;
    page.value = 1;
  }
  
  try {
    const params = {
      page: page.value,
      limit: limit
    };
    if (filterState.selectedCategory) params.category_id = filterState.selectedCategory;
    if (filterState.selectedRegion) params.region_id = filterState.selectedRegion;
    
    console.log("--- DEBUG: HomeView FETCH ---");
    console.log("Params:", params);
    
    const response = await api.get('/public/ads', { params });
    const newAds = response.data;
    
    console.log("Response data length:", newAds.length);
    console.log("Response data:", newAds);
    
    if (isLoadMore) {
      ads.value = [...ads.value, ...newAds];
    } else {
      ads.value = newAds;
    }
    
    hasMore.value = newAds.length === limit;
  } catch (error) {
    console.error("E'lonlarni yuklashda xato:", error);
  } finally {
    loading.value = false;
    loadingMore.value = false;
  }
};

const loadMore = () => {
  page.value++;
  fetchAds(true);
};

// Global filtrlar o'zgarganda e'lonlarni qayta yuklaymiz
watch(
  () => [filterState.selectedCategory, filterState.selectedRegion],
  () => {
    fetchAds();
  }
);

onMounted(() => {
  fetchAds();
});
</script>

<template>
  <div class="home-view fade-in">
    <!-- Hero Section -->
    <header class="hero">
      <h1 class="hero-title">Buqacha<span class="accent">.uz</span></h1>
      <p class="hero-subtitle">O'zbekistondagi eng yirik chorva va yem-xashak e'lonlari portali.</p>
    </header>

    <!-- Ads Grid -->
    <div v-if="loading && ads.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>Yuklanmoqda...</p>
    </div>

    <section v-else class="ads-grid">
      <router-link 
        v-for="ad in ads" 
        :key="ad.id" 
        :to="'/ad/' + ad.id"
        class="ad-card card-glass"
      >
        <div class="ad-image-container">
          <img 
            v-if="ad.media_files && ad.media_files.length" 
            :src="ad.media_files[0].file_path.startsWith('http') ? ad.media_files[0].file_path : '/' + ad.media_files[0].file_path.replace(/^\/+/, '')" 
            :alt="ad.title"
            class="ad-image"
            loading="lazy"
          >
          <div v-else class="ad-image-placeholder">
            <span>{{ ad.category?.slug === 'mol' ? '🐂' : ad.category?.slug === 'qoy' ? '🐑' : '🌾' }}</span>
          </div>
          <div class="ad-badge">{{ ad.category?.name }}</div>
        </div>
        <div class="ad-info">
          <h3 class="ad-title">{{ ad.title }}</h3>
          <div class="ad-meta">
            <span class="ad-location">📍 {{ ad.region?.name }}</span>
            <span class="ad-date" v-if="ad.published_at">{{ new Date(ad.published_at).toLocaleDateString() }}</span>
          </div>
          <div class="ad-price-row">
            <p class="ad-price">{{ ad.price ? Number(ad.price).toLocaleString() + " so'm" : 'Kelishiladi' }}</p>
            <span class="view-btn">Ko'rish</span>
          </div>
        </div>
      </router-link>
    </section>

    <div v-if="!loading && hasMore" class="load-more-container">
      <button @click="loadMore" class="btn-primary" :disabled="loadingMore">
        {{ loadingMore ? 'Yuklanmoqda...' : 'Yana yuklash' }}
      </button>
    </div>

    <div v-if="!loading && ads.length === 0" class="no-results">
      <div class="empty-icon">📂</div>
      <p>Ushbu parametrlar bo'yicha e'lonlar topilmadi.</p>
      <button @click="filterState.resetFilters()" class="btn-text">
        Filtrlarni tozalash
      </button>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  padding-bottom: 5rem;
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
  padding: 3rem 1rem;
  background: radial-gradient(circle at top, rgba(16, 185, 129, 0.05) 0%, transparent 70%);
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 900;
  margin-bottom: 1rem;
  letter-spacing: -2px;
  color: var(--text-primary);
}

.hero-subtitle {
  color: var(--text-secondary);
  font-size: 1.2rem;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.accent {
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Filter Bar Styles */
.filter-section {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 4rem;
  padding: 2rem;
  border-radius: 24px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  flex: 1;
  max-width: 300px;
}

.filter-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-left: 0.5rem;
}

.filter-select {
  padding: 0.8rem 1.2rem;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  outline: none;
  transition: all 0.3s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%234b5563' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.8rem center;
  background-size: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.filter-select:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.filter-select:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.filter-select option {
  background: #ffffff;
  color: var(--text-primary);
}

/* Ads Grid */
.ads-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2.5rem;
}

.ad-card {
  background: var(--card-bg);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  text-decoration: none;
}

.ad-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border-color: var(--accent-primary);
}

.ad-image-container {
  height: 220px;
  position: relative;
  background: #f3f4f6;
}

.ad-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ad-image-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  background: linear-gradient(45deg, #f3f4f6, #e5e7eb);
  color: #9ca3af;
}

.ad-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  padding: 0.4rem 0.8rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-primary);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 2;
}

.ad-info {
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.ad-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 3.1rem;
}

.ad-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.ad-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.ad-price {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--accent-primary);
  margin: 0;
}

.view-btn {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-primary);
  padding: 0.4rem 0.8rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 5rem;
}

.no-results {
  text-align: center;
  padding: 6rem 2rem;
  grid-column: 1 / -1;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.btn-primary {
  padding: 1rem 2.5rem;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(0, 255, 135, 0.3);
}

.btn-text {
  background: none;
  border: none;
  color: var(--accent-primary);
  text-decoration: underline;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 600;
}

.loading-state {
  text-align: center;
  padding: 5rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(16, 185, 129, 0.1);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .hero-title { font-size: 2.8rem; }
  .filter-section {
    flex-direction: column;
    gap: 1.5rem;
    padding: 1.5rem;
  }
  .filter-group { max-width: none; }
  .ads-grid { grid-template-columns: 1fr; }
}
</style>
