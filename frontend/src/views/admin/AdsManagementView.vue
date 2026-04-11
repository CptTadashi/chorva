<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '../../services/api';

const ads = ref([]);
const loading = ref(true);
const searchQuery = ref('');
const statusFilter = ref('');
const page = ref(1);
const limit = 20;

const getMediaUrl = (path) => {
  if (!path) return '';
  return '/' + path;
};

const fetchAllAds = async () => {
  loading.value = true;
  try {
    const params = {
      page: page.value,
      limit: limit
    };
    if (searchQuery.value) params.q = searchQuery.value;
    if (statusFilter.value) params.status = statusFilter.value;

    const response = await api.get('/admin/ads/all', { params });
    ads.value = response.data;
  } catch (err) {
    console.error("E'lonlarni yuklashda xato:", err);
  } finally {
    loading.value = false;
  }
};

const nextPage = () => {
  page.value++;
  fetchAllAds();
};

const prevPage = () => {
  if (page.value > 1) {
    page.value--;
    fetchAllAds();
  }
};

const deleteAd = async (id) => {
  if (!confirm("Haqiqatan ham ushbu e'lonni butunlay o'chirmoqchimisiz? Bu amalni ortga qaytarib bo'lmaydi.")) return;
  try {
    await api.delete(`/admin/ads/${id}`);
    fetchAllAds();
  } catch (err) {
    alert("O'chirishda xatolik yuz berdi");
  }
};

const getStatusLabel = (status) => {
  const map = {
    'pending_review': 'Kutilmoqda',
    'published': 'Faol',
    'rejected': 'Rad etilgan',
    'sold': 'Sotilgan',
    'archived': 'Arxiv'
  };
  return map[status] || status;
};

// Debounce search
let timeout = null;
watch(searchQuery, () => {
  clearTimeout(timeout);
  timeout = setTimeout(fetchAllAds, 500);
});

watch(statusFilter, fetchAllAds);

onMounted(fetchAllAds);
</script>

<template>
  <div class="ads-mgmt-view fade-in">
    <header class="page-header">
      <h1>E'lonlar Bazasi</h1>
      <p>Tizimdagi barcha e'lonlarni qidirish va filtrlash</p>
    </header>

    <div class="filters-bar glass">
      <div class="search-input">
        <span class="search-icon">🔍</span>
        <input v-model="searchQuery" type="text" placeholder="E'lon sarlavhasi bo'yicha qidirish...">
      </div>
      
      <div class="filter-group">
        <select v-model="statusFilter" class="select-filter">
          <option value="">Barcha holatlar</option>
          <option value="published">Faol (Sotuvda)</option>
          <option value="pending_review">Moderatsiyada</option>
          <option value="sold">Sotilganlar</option>
          <option value="rejected">Rad etilganlar</option>
        </select>
      </div>
    </div>

    <div class="table-container glass">
      <!-- Desktop Table -->
      <table v-if="!loading" class="data-table desktop-only">
        <thead>
          <tr>
            <th>ID</th>
            <th>Rasm</th>
            <th>Sarlavha</th>
            <th>Sotuvchi</th>
            <th>Narxi</th>
            <th>Holat</th>
            <th>Harakat</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ad in ads" :key="ad.id">
            <td>#{{ ad.id }}</td>
            <td>
              <img 
                v-if="ad.media_files?.length"
                :src="getMediaUrl(ad.media_files[0].file_path)" 
                class="ad-thumb"
                loading="lazy"
              >
              <div v-else class="no-thumb">🖼️</div>
            </td>
            <td class="title-cell">
              <strong>{{ ad.title }}</strong>
              <span class="cat-label">{{ ad.category?.name }}</span>
            </td>
            <td class="user-cell">
              {{ ad.user?.full_name || 'Ismsiz' }}
              <span class="phone">{{ ad.user?.phone_number }}</span>
            </td>
            <td class="price">{{ ad.price.toLocaleString() }} so'm</td>
            <td>
              <span class="status-badge" :class="ad.status">
                {{ getStatusLabel(ad.status) }}
              </span>
            </td>
            <td>
              <div class="actions">
                <router-link :to="`/ad/${ad.id}`" target="_blank" class="view-btn">👁️</router-link>
                <button @click="deleteAd(ad.id)" class="del-btn">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Mobile List -->
      <div v-if="!loading" class="mobile-only ad-cards">
        <div v-for="ad in ads" :key="ad.id" class="m-ad-card border-b">
          <div class="m-card-top">
            <img 
              v-if="ad.media_files?.length"
              :src="getMediaUrl(ad.media_files[0].file_path)" 
              class="m-ad-thumb"
            >
            <div v-else class="m-no-thumb">🖼️</div>
            <div class="m-info">
              <span class="m-cat">{{ ad.category?.name }}</span>
              <h4 class="m-title">{{ ad.title }}</h4>
              <span class="status-badge nano" :class="ad.status">{{ getStatusLabel(ad.status) }}</span>
            </div>
          </div>
          <div class="m-details">
            <div class="m-detail">
              <span class="lab">Narxi:</span>
              <span class="val accent">{{ ad.price.toLocaleString() }} so'm</span>
            </div>
            <div class="m-detail">
              <span class="lab">Sotuvchi:</span>
              <span class="val">{{ ad.user?.full_name || 'Ismsiz' }}</span>
            </div>
          </div>
          <div class="m-actions">
            <router-link :to="`/ad/${ad.id}`" target="_blank" class="m-btn view">Ko'rish</router-link>
            <button @click="deleteAd(ad.id)" class="m-btn del">O'chirish</button>
          </div>
        </div>
      </div>

      <!-- Pagination Footer -->
      <div v-if="!loading" class="pagination-footer">
        <button @click="prevPage" :disabled="page === 1" class="page-btn">« Oldingi</button>
        <span class="page-info">Sahifa: {{ page }}</span>
        <button @click="nextPage" :disabled="ads.length < limit" class="page-btn">Keyingi »</button>
      </div>

  <div v-if="loading" class="loading-padding">
    <div class="spinner"></div>
    <p>Yuklanmoqda...</p>
  </div>

      <div v-if="!loading && ads.length === 0" class="empty-padding">
        E'lonlar topilmadi.
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2rem; }

.filters-bar {
  display: flex;
  gap: 1.5rem;
  padding: 1.2rem;
  border-radius: 20px;
  margin-bottom: 2rem;
  align-items: center;
}

.search-input {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.search-input input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.8rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  outline: none;
}

.search-input input::placeholder {
  color: var(--text-secondary);
  opacity: 0.6;
}

.select-filter {
  padding: 0.8rem 1rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  outline: none;
}

.select-filter option { background: #05070a; }

.table-container { border-radius: 25px; overflow: hidden; padding: 1rem; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border-color); }

.ad-thumb { width: 60px; height: 60px; object-fit: cover; border-radius: 10px; }
.no-thumb { width: 60px; height: 60px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; border-radius: 10px; }

.title-cell { display: flex; flex-direction: column; gap: 0.2rem; }
.cat-label { font-size: 0.75rem; color: var(--accent-primary); font-weight: 600; }

.user-cell { display: flex; flex-direction: column; }
.phone { font-size: 0.8rem; color: var(--text-secondary); }

.price { font-weight: 700; color: var(--accent-secondary); white-space: nowrap; }

.status-badge {
  padding: 0.3rem 0.7rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
}
.status-badge.published { background: rgba(16, 185, 129, 0.1); color: var(--accent-primary); }
.status-badge.pending_review { background: rgba(245, 158, 11, 0.1); color: var(--accent-secondary); }
.status-badge.sold { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.status-badge.rejected { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

.actions { display: flex; gap: 0.8rem; }
.view-btn, .del-btn { background: none; border: none; cursor: pointer; font-size: 1.1rem; }
.del-btn:hover { transform: scale(1.2); }

.pagination-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  border-top: 1px solid var(--border-color);
}

.page-btn {
  padding: 0.6rem 1.2rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-info {
  font-weight: 600;
  color: var(--text-secondary);
}

.loading-padding, .empty-padding { padding: 4rem; text-align: center; color: var(--text-secondary); }
.spinner { width: 30px; height: 30px; border: 3px solid var(--border-color); border-top: 3px solid var(--accent-primary); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }

.mobile-only { display: none; }

@media (max-width: 768px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }

  .filters-bar { flex-direction: column; gap: 1rem; align-items: stretch; border-radius: 18px; padding: 1rem; }
  .table-container { padding: 0.5rem; border-radius: 18px; }
  
  .m-ad-card { padding: 1.2rem 0.5rem; }
  .m-card-top { display: flex; gap: 1rem; margin-bottom: 1rem; }
  .m-ad-thumb, .m-no-thumb { width: 80px; height: 80px; border-radius: 12px; object-fit: cover; }
  .m-no-thumb { background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
  
  .m-info { flex: 1; display: flex; flex-direction: column; gap: 0.2rem; }
  .m-cat { font-size: 0.7rem; font-weight: 700; color: var(--accent-primary); text-transform: uppercase; }
  .m-title { font-size: 1rem; margin: 0; color: var(--text-primary); }
  .status-badge.nano { font-size: 0.6rem; padding: 0.2rem 0.5rem; width: fit-content; margin-top: 0.3rem; }

  .m-details { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; background: rgba(0,0,0,0.02); padding: 0.8rem; border-radius: 10px; margin-bottom: 1rem; }
  .m-detail { display: flex; flex-direction: column; }
  .m-detail .lab { font-size: 0.7rem; color: var(--text-secondary); }
  .m-detail .val { font-size: 0.85rem; font-weight: 600; }
  .m-detail .val.accent { color: var(--accent-secondary); }

  .m-actions { display: flex; gap: 0.5rem; }
  .m-btn { flex: 1; padding: 0.8rem; border-radius: 10px; font-weight: 700; font-size: 0.85rem; text-decoration: none; text-align: center; border: 1px solid var(--border-color); }
  .m-btn.view { background: rgba(16, 185, 129, 0.1); color: var(--accent-primary); border-color: var(--accent-primary); }
  .m-btn.del { background: rgba(239, 68, 68, 0.05); color: #ef4444; border-color: #ef4444; }

  .pagination-footer { padding: 1.5rem 0.5rem; gap: 1rem; }
  .page-btn { padding: 0.6rem 0.8rem; font-size: 0.8rem; }
}
</style>
