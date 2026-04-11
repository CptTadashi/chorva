<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const pendingAds = ref([]);
const loading = ref(true);
const actionLoading = ref(null);
const showRejectModal = ref(false);
const showDetailModal = ref(false);
const selectedAdId = ref(null);
const selectedAd = ref(null);
const rejectReason = ref('');

const getMediaUrl = (path) => {
  if (!path) return '';
  // Agar path allaqachon media/ bilan boshlansa, uni / orqali chaqiramiz
  return '/' + path;
};

const openDetailModal = (ad) => {
  selectedAd.value = ad;
  showDetailModal.value = true;
};

const fetchPending = async () => {
  loading.value = true;
  try {
    const response = await api.get('/admin/ads/pending');
    pendingAds.value = response.data;
  } catch (error) {
    console.error("Yuklashda xato:", error);
  } finally {
    loading.value = false;
  }
};

const approveAd = async (adId) => {
  actionLoading.value = adId;
  try {
    await api.post(`/admin/ads/${adId}/approve`);
    pendingAds.value = pendingAds.value.filter(ad => ad.id !== adId);
    alert("✅ E'lon tasdiqlandi va saytga chiqarildi!");
  } catch (error) {
    alert("Xatolik yuz berdi");
  } finally {
    actionLoading.value = null;
  }
};

const openRejectModal = (adId) => {
  selectedAdId.value = adId;
  rejectReason.value = '';
  showRejectModal.value = true;
};

const handleReject = async () => {
  if (!rejectReason.value) return;
  
  actionLoading.value = selectedAdId.value;
  try {
    await api.post(`/admin/ads/${selectedAdId.value}/reject`, {
      reason: rejectReason.value
    });
    pendingAds.value = pendingAds.value.filter(ad => ad.id !== selectedAdId.value);
    showRejectModal.value = false;
    alert("❌ E'lon rad etildi");
  } catch (error) {
    alert("Xatolik yuz berdi");
  } finally {
    actionLoading.value = null;
    selectedAdId.value = null;
  }
};

onMounted(fetchPending);
</script>

<template>
  <div class="moderation-view fade-in">
    <div class="page-header header glass">
      <div class="header-left">
        <h1>Moderatsiya Paneli</h1>
        <p class="subtitle">Kutayotgan e'lonlarni tekshiring va tasdiqlang</p>
      </div>
      <div class="header-right">
        <span class="badge">{{ pendingAds.length }} ta kutilmoqda</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>E'lonlar yuklanmoqda...</p>
    </div>

    <div v-else class="ads-list">
      <div v-for="ad in pendingAds" :key="ad.id" class="ad-card">
        <div class="ad-grid">
          <div class="ad-media" @click="openDetailModal(ad)">
            <div v-if="ad.media_files && ad.media_files.length" class="media-container clickable">
              <img v-if="ad.media_files[0].media_type === 'photo'" :src="getMediaUrl(ad.media_files[0].file_path)" loading="lazy">
              <video v-else :src="getMediaUrl(ad.media_files[0].file_path)"></video>
              <div class="media-badge" v-if="ad.media_files.length > 1">
                <span>+{{ ad.media_files.length - 1 }}</span>
              </div>
              <div class="view-overlay">🔍 Ko'rish</div>
            </div>
            <div v-else class="no-media-placeholder">
              <span>🖼️</span>
              <p>Rasm yo'q</p>
            </div>
          </div>

          <div class="ad-content">
            <div class="ad-meta">
              <span class="category-tag">{{ ad.category.name }}</span>
              <span class="timestamp">{{ new Date(ad.created_at).toLocaleDateString() }}</span>
            </div>
            <h3 class="ad-title">{{ ad.title }}</h3>
            <p class="ad-desc">{{ ad.description }}</p>
            
            <div class="ad-details-grid">
              <div class="detail-item">
                <span class="label">Narxi:</span>
                <span class="value price">{{ ad.price ? Number(ad.price).toLocaleString() + " so'm" : 'Kelishiladi' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Manzil:</span>
                <span class="value">{{ ad.region.name }}, {{ ad.district.name }}</span>
              </div>
              <div class="detail-item">
                <span class="label">User:</span>
                <span class="value">{{ ad.user?.full_name || 'Ismsiz' }} ({{ ad.owner_phone || ad.user?.phone_number }})</span>
              </div>
            </div>
          </div>

          <div class="ad-actions">
            <button 
              @click="approveAd(ad.id)" 
              class="action-btn approve"
              :disabled="actionLoading === ad.id"
            >
              <span v-if="actionLoading === ad.id" class="mini-spinner"></span>
              <span v-else>✅ Tasdiqlash</span>
            </button>
            <button 
              @click="openRejectModal(ad.id)" 
              class="action-btn reject"
              :disabled="actionLoading === ad.id"
            >
              ❌ Rad etish
            </button>
          </div>
        </div>
      </div>

      <div v-if="pendingAds.length === 0" class="empty-state">
        <div class="empty-icon">🎉</div>
        <h2>Hammasi joyida!</h2>
        <p>Hozircha tekshiriladigan yangi e'lonlar yo'q.</p>
        <button @click="fetchPending" class="btn-refresh">Yangilash</button>
      </div>
    </div>

    <!-- Reject Modal -->
    <transition name="modal">
      <div v-if="showRejectModal" class="modal-overlay" @click.self="showRejectModal = false">
        <div class="modal shadow-premium">
          <div class="modal-header">
            <h3>Rad etish sababi</h3>
            <button @click="showRejectModal = false" class="btn-close">&times;</button>
          </div>
          <div class="modal-body">
            <p>Foydalanuvchiga nima uchun e'lon rad etilganini tushuntiring:</p>
            <textarea 
              v-model="rejectReason" 
              placeholder="Masalan: Rasm sifati juda past yoki taqiqlangan ma'lumotlar mavjud."
              class="premium-textarea"
            ></textarea>
          </div>
          <div class="modal-footer">
            <button @click="showRejectModal = false" class="btn-secondary">Bekor qilish</button>
            <button 
              @click="handleReject" 
              class="btn-danger" 
              :disabled="!rejectReason || actionLoading"
            >
              Rad etishni tasdiqlash
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Ad Detail Modal -->
    <transition name="modal">
      <div v-if="showDetailModal && selectedAd" class="modal-overlay" @click.self="showDetailModal = false">
        <div class="modal detail-modal shadow-premium">
          <div class="modal-header sticky">
            <h3>E'lon Tafsilotlari</h3>
            <button @click="showDetailModal = false" class="btn-close">&times;</button>
          </div>
          <div class="modal-body scrollable">
            <div class="detail-gallery">
              <div v-for="(file, idx) in selectedAd.media_files" :key="idx" class="gallery-item glass">
                <img v-if="file.media_type === 'photo'" :src="getMediaUrl(file.file_path)" />
                <video v-else :src="getMediaUrl(file.file_path)" controls playsinline></video>
              </div>
            </div>
            
            <div class="detail-info-box card glass">
              <div class="info-header">
                <span class="category-tag">{{ selectedAd.category?.name }}</span>
                <span class="price-large">{{ selectedAd.price ? Number(selectedAd.price).toLocaleString() + " so'm" : 'Kelishiladi' }}</span>
              </div>
              <h2 class="detail-title">{{ selectedAd.title }}</h2>
              <div class="meta-row">
                <span>📍 {{ selectedAd.region?.name }}, {{ selectedAd.district?.name }}</span>
                <span>📅 {{ new Date(selectedAd.created_at).toLocaleDateString() }}</span>
              </div>
              <p class="detail-description">{{ selectedAd.description }}</p>
              
              <div class="contact-card">
                <p><strong>Egasi:</strong> {{ selectedAd.user?.full_name || 'Ismsiz' }}</p>
                <p><strong>Telefon:</strong> {{ selectedAd.owner_phone || selectedAd.user?.phone_number }}</p>
                <p v-if="selectedAd.extra_contact"><strong>Qo'shimcha:</strong> {{ selectedAd.extra_contact }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer sticky">
            <button @click="showDetailModal = false" class="btn-secondary">Yopish</button>
            <div class="action-group">
              <button 
                @click="approveAd(selectedAd.id); showDetailModal = false" 
                class="btn-primary"
                :disabled="actionLoading"
              >✅ Tasdiqlash</button>
              <button 
                @click="openRejectModal(selectedAd.id); showDetailModal = false" 
                class="btn-danger"
              >❌ Rad etish</button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.moderation-view {
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  padding: 1.5rem 2rem;
  border-radius: 20px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
  color: var(--text-primary);
}

.subtitle {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.badge {
  background: var(--accent-primary);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 100px;
  font-weight: 700;
  font-size: 0.85rem;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.ads-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.ad-card {
  background: white;
  border-radius: 20px;
  padding: 1.2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.03);
  transition: transform 0.2s;
}

.ad-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
}

.ad-grid {
  display: grid;
  grid-template-columns: 180px 1fr 180px;
  gap: 1.5rem;
  align-items: start;
}

.media-container {
  position: relative;
  width: 180px;
  height: 135px;
  border-radius: 12px;
  overflow: hidden;
  background: #f3f4f6;
}

.media-container img, .media-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.media-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  backdrop-filter: blur(4px);
}

.no-media-placeholder {
  width: 180px;
  height: 135px;
  background: #f9fafb;
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.no-media-placeholder span { font-size: 1.5rem; }
.no-media-placeholder p { font-size: 0.75rem; margin: 4px 0 0; }

.ad-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.category-tag {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--accent-primary);
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.timestamp {
  font-size: 0.75rem;
  color: #9ca3af;
}

.ad-title {
  font-size: 1.2rem;
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.ad-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ad-details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem 1rem;
  background: #f9fafb;
  padding: 0.8rem;
  border-radius: 10px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item .label {
  font-size: 0.7rem;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-item .value {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
}

.value.price {
  color: var(--accent-secondary);
  font-weight: 700;
}

.ad-actions {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  height: 100%;
}

.action-btn {
  padding: 0.8rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.85rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.action-btn.approve {
  background: var(--accent-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.action-btn.approve:hover {
  background: var(--accent-secondary);
  transform: translateY(-2px);
}

.action-btn.reject {
  background: #fee2e2;
  color: #ef4444;
}

.action-btn.reject:hover {
  background: #fecaca;
}

/* Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(17, 24, 39, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  width: 90%;
  max-width: 500px;
  border-radius: 24px;
  overflow: hidden;
}

.modal-header {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f3f4f6;
}

.modal-header.sticky {
  position: sticky;
  top: 0;
  background: white;
  z-index: 100;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 { margin: 0; font-size: 1.25rem; }

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #9ca3af;
  cursor: pointer;
}

.modal-body { padding: 1.5rem 2rem; }

.modal-body p { margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.95rem; }

.premium-textarea {
  width: 100%;
  height: 120px;
  padding: 1rem;
  border-radius: 15px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  font-family: inherit;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s;
}

.premium-textarea:focus {
  border-color: var(--accent-primary);
  background: white;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

/* Detail Modal Styling */
.detail-modal {
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-body.scrollable {
  overflow-y: auto;
  padding: 1.5rem;
}

.detail-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.gallery-item {
  border-radius: 15px;
  overflow: hidden;
  aspect-ratio: 4/3;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gallery-item img, .gallery-item video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-info-box {
  padding: 2rem;
}

.price-large {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--accent-secondary);
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.detail-title { margin-bottom: 1rem; }

.meta-row {
  display: flex;
  gap: 1.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.detail-description {
  white-space: pre-wrap;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.contact-card {
  background: rgba(0,0,0,0.03);
  padding: 1.5rem;
  border-radius: 15px;
}

.modal-footer.sticky {
  position: sticky;
  bottom: 0;
  background: white;
  border-top: 1px solid var(--border-color);
  z-index: 10;
}

.action-group {
  display: flex;
  gap: 0.5rem;
}

.media-container.clickable {
  cursor: pointer;
  position: relative;
}

.view-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.3s;
}

.media-container:hover .view-overlay {
  opacity: 1;
}

@media (max-width: 768px) {
  .detail-modal { width: 100%; height: 100vh; max-height: 100vh; border-radius: 0; }
  .detail-gallery { grid-template-columns: 1fr; }
  .modal-footer.sticky { flex-direction: column-reverse; }
  .action-group { flex-direction: column; width: 100%; }
}


.modal-footer {
  padding: 1.5rem 2rem;
  background: #f9fafb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-secondary {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 500;
  cursor: pointer;
}

.btn-danger {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 30px;
  margin-top: 2rem;
}

.empty-icon { font-size: 4rem; margin-bottom: 1rem; }

.btn-refresh {
  margin-top: 1.5rem;
  background: var(--accent-primary);
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}

.mini-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: rotate 0.6s linear infinite;
  display: inline-block;
}

@keyframes rotate { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .ad-grid { grid-template-columns: 1fr; }
  .ad-media, .media-container { width: 100%; height: 200px; }
  .ad-actions { flex-direction: row; }
}
</style>
