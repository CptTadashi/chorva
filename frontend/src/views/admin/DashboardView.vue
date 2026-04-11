<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const stats = ref(null);
const loading = ref(true);

const fetchStats = async () => {
  try {
    const response = await api.get('/admin/stats/stats');
    stats.value = response.data;
  } catch (error) {
    console.error("Statistikani yuklashda xato:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<template>
  <div class="dashboard-view fade-in">
    <header class="page-header">
      <h1>Boshqaruv Paneli</h1>
      <p>Tizimning umumiy holati va statistikasi</p>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Ma'lumotlar yuklanmoqda...</p>
    </div>

    <div v-else-if="stats" class="stats-grid">
      <!-- Summary Cards -->
      <div class="stat-card glass">
        <div class="icon">📢</div>
        <div class="data">
          <h3>{{ stats.total_ads }}</h3>
          <p>Jami E'lonlar</p>
        </div>
      </div>
      <div class="stat-card glass accent">
        <div class="icon">⏳</div>
        <div class="data">
          <h3>{{ stats.pending_ads }}</h3>
          <p>Kutilmoqda</p>
        </div>
      </div>
      <div class="stat-card glass success">
        <div class="icon">✅</div>
        <div class="data">
          <h3>{{ stats.published_ads }}</h3>
          <p>Tasdiqlangan</p>
        </div>
      </div>
      <div class="stat-card glass info">
        <div class="icon">💰</div>
        <div class="data">
          <h3>{{ stats.sold_ads }}</h3>
          <p>Sotilgan</p>
        </div>
      </div>
      <div class="stat-card glass users">
        <div class="icon">👥</div>
        <div class="data">
          <h3>{{ stats.total_users }}</h3>
          <p>Foydalanuvchilar</p>
        </div>
      </div>
    </div>

    <div v-if="!loading && stats" class="charts-section">
      <div class="chart-card glass">
        <h3>Kategoriyalar bo'yicha</h3>
        <div class="bar-chart">
          <div v-for="cat in stats.ads_by_category" :key="cat.name" class="bar-row">
            <span class="label">{{ cat.name }}</span>
            <div class="bar-container">
              <div 
                class="bar" 
                :style="{ width: (cat.count / stats.total_ads * 100) + '%' }"
              ></div>
            </div>
            <span class="count">{{ cat.count }}</span>
          </div>
        </div>
      </div>

      <div class="chart-card glass">
        <h3>Hududlar bo'yicha</h3>
        <div class="bar-chart">
          <div v-for="reg in stats.ads_by_region" :key="reg.name" class="bar-row">
            <span class="label">{{ reg.name }}</span>
            <div class="bar-container">
              <div 
                class="bar-secondary" 
                :style="{ width: (reg.count / stats.total_ads * 100) + '%' }"
              ></div>
            </div>
            <span class="count">{{ reg.count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 2.5rem;
}

.page-header h1 {
  font-size: 2.2rem;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: var(--text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  padding: 2rem;
  border-radius: 25px;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card .icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
}

.stat-card .data h3 {
  font-size: 2rem;
  line-height: 1;
  margin-bottom: 0.2rem;
}

.stat-card .data p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.stat-card.accent { border-left: 4px solid var(--accent-secondary); }
.stat-card.success { border-left: 4px solid var(--accent-primary); }
.stat-card.info { border-left: 4px solid #3b82f6; }
.stat-card.users { border-left: 4px solid #a855f7; }

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.chart-card {
  padding: 2rem;
  border-radius: 25px;
}

.chart-card h3 {
  margin-bottom: 2rem;
  font-size: 1.2rem;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.bar-row {
  display: grid;
  grid-template-columns: 100px 1fr 40px;
  align-items: center;
  gap: 1rem;
}

.label {
  font-size: 0.9rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-container {
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: var(--grad-primary);
  border-radius: 4px;
}

.bar-secondary {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2dd4bf);
  border-radius: 4px;
}

.count {
  font-weight: 600;
  text-align: right;
  font-size: 0.9rem;
}

.loading-state {
  text-align: center;
  padding: 5rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1000px) {
  .charts-section {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .page-header h1 { font-size: 1.8rem; }
  .stats-grid { gap: 1rem; }
  .stat-card { padding: 1.5rem; gap: 1rem; }
  .stat-card .icon { font-size: 2rem; width: 50px; height: 50px; }
  .stat-card .data h3 { font-size: 1.5rem; }
  
  .chart-card { padding: 1.5rem; }
  .bar-row { grid-template-columns: 80px 1fr 30px; gap: 0.8rem; }
  .label { font-size: 0.8rem; }
}
</style>
