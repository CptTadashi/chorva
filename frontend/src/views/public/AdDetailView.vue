<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../../services/api';

const route = useRoute();
const ad = ref(null);
const loading = ref(true);

const fetchAd = async () => {
  loading.value = true;
  const adId = route.params.id;

  try {
    const response = await api.get(`/public/ads/${adId}`);
    ad.value = response.data;
  } catch (error) {
    console.error("E'lonni yuklashda xato:", error);
    ad.value = null;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchAd();
});
</script>

<template>
  <div class="ad-detail fade-in">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>E'lon yuklanmoqda...</p>
    </div>

    <div v-else-if="ad" class="detail-container">
      <div class="media-section glass">
        <!-- Media Display -->
        <div v-if="ad.media_files && ad.media_files.length" class="media-gallery">
          <div v-for="m in ad.media_files" :key="m.id" class="media-wrapper shadow-lg">
            <img v-if="m.media_type === 'photo'" :src="'/' + m.file_path" :alt="ad.title" loading="lazy">
            <video v-else controls playsinline :src="'/' + m.file_path"></video>
          </div>
        </div>
        <div v-else class="media-placeholder">
          <span>🖼️ Suratlar mavjud emas</span>
        </div>
      </div>

      <div class="info-section glass">
        <div class="ad-header">
          <span class="category-badge">{{ ad.category.name }}</span>
          <h1 class="title">{{ ad.title }}</h1>
          <p class="location">📍 {{ ad.region.name }}, {{ ad.district.name }}</p>
          <div class="price">{{ ad.price ? Number(ad.price).toLocaleString() + " so'm" : 'Kelishiladi' }}</div>
        </div>

        <div class="description-box">
          <h3>Tavsif</h3>
          <p>{{ ad.description }}</p>
        </div>

        <div class="contact-card border-t">
          <h3>Sotuvchi bilan bog'lanish</h3>
          <div class="contact-info">
            <div class="info-item">
              <span class="label">Telefon:</span>
              <a :href="'tel:' + ad.owner_phone" class="value">{{ ad.owner_phone }}</a>
            </div>
            <div v-if="ad.extra_contact" class="info-item">
              <span class="label">Qo'shimcha aloqa:</span>
              <span class="value">{{ ad.extra_contact }}</span>
            </div>
          </div>
          <a :href="'tel:' + ad.owner_phone" class="btn-primary call-btn">
            📱 Qo'ng'iroq qilish
          </a>
        </div>
      </div>
    </div>

    <div v-else class="error-state">
      <p>E'lon topilmadi yoki hali tasdiqlanmagan.</p>
      <router-link to="/" class="btn-primary">Bosh sahifaga qaytish</router-link>
    </div>
  </div>
</template>

<style scoped>
.detail-container {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 2rem;
  align-items: start;
}

.media-section {
  border-radius: 24px;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.media-gallery {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem;
}

.media-wrapper {
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  background: #000;
  line-height: 0;
}

.media-wrapper img, .media-wrapper video {
  width: 100%;
  height: auto;
  max-height: 600px;
  object-fit: contain;
  display: block;
}

.media-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--text-secondary);
}

.info-section {
  padding: 2.5rem;
  border-radius: 24px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 100px;
}

.category-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-primary);
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.8rem;
  margin-bottom: 1rem;
}

.title {
  font-size: 2.2rem;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}

.location {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

.price {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--accent-primary);
  margin-bottom: 2rem;
}

.description-box h3, .contact-card h3 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: var(--text-secondary);
}

.description-box p {
  font-size: 1.1rem;
  white-space: pre-wrap;
  margin-bottom: 2rem;
}

.contact-card {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.contact-info {
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
}

.label {
  color: var(--text-secondary);
}

.value {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-primary);
  text-decoration: none;
}

.call-btn {
  display: block;
  text-align: center;
  width: 100%;
}

@media (max-width: 900px) {
  .detail-container {
    grid-template-columns: 1fr;
  }
}
</style>
