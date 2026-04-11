<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const activeTab = ref('categories'); // 'categories' | 'regions'
const categories = ref([]);
const regions = ref([]);
const districts = ref({}); // { regionId: [districts] }
const expandedRegion = ref(null);
const loading = ref(false);

// Modals
const showModal = ref(false);
const modalType = ref(''); // 'category' | 'region' | 'district'
const editingItem = ref(null);
const formData = ref({ name: '', slug: '', sort_order: 0, region_id: null });

const fetchCategories = async () => {
  const resp = await api.get('/public/categories');
  categories.value = resp.data;
};

const fetchRegions = async () => {
  const resp = await api.get('/public/regions');
  regions.value = resp.data;
};

const fetchDistricts = async (regionId) => {
  try {
    const resp = await api.get(`/public/regions/${regionId}/districts`);
    districts.value[regionId] = resp.data;
  } catch (error) {
    console.error("Tumanlarni yuklashda xato:", error);
  }
};

const toggleRegion = (regionId) => {
  if (expandedRegion.value === regionId) {
    expandedRegion.value = null;
  } else {
    expandedRegion.value = regionId;
    if (!districts.value[regionId]) {
      fetchDistricts(regionId);
    }
  }
};

const openAddModal = (type, parentId = null) => {
  modalType.value = type;
  editingItem.value = null;
  formData.value = { name: '', slug: '', sort_order: 0, region_id: parentId };
  showModal.value = true;
};

const editItem = (type, item) => {
  modalType.value = type;
  editingItem.value = item;
  formData.value = { 
    name: item.name, 
    slug: item.slug || '', 
    sort_order: item.sort_order || 0,
    region_id: item.region_id || null
  };
  showModal.value = true;
};

const handleDelete = async (type, id) => {
  if (!confirm("Haqiqatan ham ushbu ma'lumotni o'chirmoqchimisiz?")) return;
  
  try {
    let url = '';
    if (type === 'category') url = `/admin/settings/categories/${id}`;
    else if (type === 'region') url = `/admin/settings/regions/${id}`;
    else if (type === 'district') url = `/admin/settings/districts/${id}`;

    await api.delete(url);
    
    // Refresh
    if (type === 'category') fetchCategories();
    else if (type === 'region') fetchRegions();
    else if (type === 'district' && expandedRegion.value) fetchDistricts(expandedRegion.value);
    
  } catch (error) {
    alert("O'chirishda xatolik: " + (error.response?.data?.detail || error.message));
  }
};

const handleSave = async () => {
  try {
    let url = '';
    const method = editingItem.value ? 'patch' : 'post';
    
    if (modalType.value === 'category') {
      url = editingItem.value ? `/admin/settings/categories/${editingItem.value.id}` : '/admin/settings/categories';
    } else if (modalType.value === 'region') {
      url = editingItem.value ? `/admin/settings/regions/${editingItem.value.id}` : '/admin/settings/regions';
    } else if (modalType.value === 'district') {
      url = editingItem.value ? `/admin/settings/districts/${editingItem.value.id}` : '/admin/settings/districts';
    }

    await api[method](url, formData.value);
    
    // Refresh data
    if (modalType.value === 'category') fetchCategories();
    else {
      fetchRegions();
      if (modalType.value === 'district' && formData.value.region_id) {
         fetchDistricts(formData.value.region_id);
      }
    }
    
    showModal.value = false;
  } catch (error) {
    alert("Saqlashda xatolik yuz berdi");
  }
};

onMounted(() => {
  fetchCategories();
  fetchRegions();
});
</script>

<template>
  <div class="settings-view fade-in">
    <header class="page-header">
      <h1>Tizim Sozlamalari</h1>
      <p>Kategoriyalar va Hududiy tuzilmani boshqarish</p>
    </header>

    <div class="settings-container">
      <!-- Tabs -->
      <div class="tabs-bar glass">
        <button 
          @click="activeTab = 'categories'" 
          :class="{ active: activeTab === 'categories' }"
        >📂 Kategoriyalar</button>
        <button 
          @click="activeTab = 'regions'" 
          :class="{ active: activeTab === 'regions' }"
        >📍 Hududlar</button>
      </div>

      <!-- Categories Tab -->
      <div v-if="activeTab === 'categories'" class="tab-content card glass">
        <div class="content-header">
          <h3>Kategoriyalar Ro'yxati</h3>
          <button @click="openAddModal('category')" class="btn-primary">+ Yangi qo'shish</button>
        </div>

        <div class="items-list">
          <div v-for="cat in categories" :key="cat.id" class="item-row border-b">
            <div class="item-main">
              <span class="item-name">{{ cat.name }}</span>
              <span class="item-slug">/{{ cat.slug }}</span>
            </div>
            <div class="item-actions">
              <span class="badge">Tartib: {{ cat.sort_order }}</span>
              <button @click="editItem('category', cat)" class="icon-btn" title="Tahrirlash">✏️</button>
              <button @click="handleDelete('category', cat.id)" class="icon-btn delete" title="O'chirish">🗑️</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Regions Tab -->
      <div v-if="activeTab === 'regions'" class="tab-content card glass">
        <div class="content-header">
          <h3>Viloyatlar va Tumanlar</h3>
          <button @click="openAddModal('region')" class="btn-primary">+ Viloyat qo'shish</button>
        </div>

        <div class="items-list">
          <div v-for="reg in regions" :key="reg.id" class="region-block" :class="{ expanded: expandedRegion === reg.id }">
            <div class="region-header">
              <div class="region-info-main" @click="toggleRegion(reg.id)">
                <span class="arrow">{{ expandedRegion === reg.id ? '▼' : '▶' }}</span>
                <span class="region-name">📍 {{ reg.name }}</span>
              </div>
              <div class="region-actions">
                <button @click="openAddModal('district', reg.id)" class="small-btn">+ Tuman</button>
                <button @click="editItem('region', reg)" class="icon-btn">✏️</button>
                <button @click="handleDelete('region', reg.id)" class="icon-btn delete">🗑️</button>
              </div>
            </div>
            
            <!-- Districts List -->
            <div v-if="expandedRegion === reg.id" class="districts-container fade-in">
              <div v-if="!districts[reg.id]" class="small-loading">Yuklanmoqda...</div>
              <div v-else-if="districts[reg.id].length === 0" class="no-districts">Tumanlar qo'shilmagan</div>
              <div v-else class="districts-list">
                <div v-for="dist in districts[reg.id]" :key="dist.id" class="district-row">
                  <span class="dist-name">{{ dist.name }}</span>
                  <div class="dist-actions">
                    <span class="dist-sort">#{{ dist.sort_order }}</span>
                    <button @click="editItem('district', dist)" class="icon-btn mini">✏️</button>
                    <button @click="handleDelete('district', dist.id)" class="icon-btn delete mini">🗑️</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-card glass">
        <h2>{{ editingItem ? 'Tahrirlash' : 'Yangi qo\'shish' }}: {{ modalType === 'category' ? 'Kategoriya' : modalType === 'region' ? 'Viloyat' : 'Tuman' }}</h2>
        <form @submit.prevent="handleSave" class="modal-form">
          <div class="form-group">
            <label>Nomi</label>
            <input v-model="formData.name" type="text" placeholder="Masalan: Bo'rdoqi mol" required>
          </div>
          <div v-if="modalType === 'category'" class="form-group">
            <label>Slug (identifikator)</label>
            <input v-model="formData.slug" type="text" placeholder="Masalan: mol" required>
          </div>
          <div class="form-group">
            <label>Tartib raqami</label>
            <input v-model.number="formData.sort_order" type="number">
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="showModal = false" class="btn-secondary">Bekor qilish</button>
            <button type="submit" class="btn-primary">Saqlash</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header { margin-bottom: 2.5rem; }

.tabs-bar {
  display: flex;
  gap: 1rem;
  padding: 0.5rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  max-width: fit-content;
}

.tabs-bar button {
  padding: 0.8rem 1.5rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.tabs-bar button.active {
  background: var(--accent-primary);
  color: white;
}

.card {
  padding: 2.5rem;
  border-radius: 30px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1rem;
  transition: background 0.3s;
  border-radius: 15px;
}

.item-row:hover {
  background: rgba(255,255,255,0.03);
}

.item-name { font-weight: 600; font-size: 1.1rem; }
.item-slug { color: var(--text-secondary); margin-left: 0.5rem; font-size: 0.9rem; }

.item-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge {
  font-size: 0.8rem;
  padding: 0.3rem 0.6rem;
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
}

.icon-btn {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn:hover { background: rgba(255,255,255,0.1); border-color: var(--text-secondary); }
.icon-btn.delete:hover { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }

.region-block {
  border-radius: 20px;
  background: rgba(255,255,255,0.02);
  border: 1px solid transparent;
  transition: all 0.3s;
}

.region-block.expanded {
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(255,255,255,0.04);
}

.region-header {
  padding: 1.2rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.region-info-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  flex: 1;
}

.arrow { font-size: 0.8rem; color: var(--text-secondary); }
.region-name { font-weight: 700; font-size: 1.2rem; }

.region-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.districts-container {
  padding: 0 1.5rem 1.5rem 3.5rem;
}

.districts-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-left: 1px dashed var(--border-color);
  padding-left: 1rem;
}

.district-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background: rgba(255,255,255,0.02);
  border-radius: 12px;
}

.dist-name { font-size: 1rem; color: var(--text-primary); }
.dist-actions { display: flex; align-items: center; gap: 0.4rem; }
.dist-sort { font-size: 0.75rem; color: var(--text-secondary); margin-right: 0.5rem; }

.icon-btn.mini { padding: 0.3rem; font-size: 0.8rem; }
.small-loading, .no-districts { font-size: 0.85rem; color: var(--text-secondary); padding: 1rem; }

.small-btn {
  padding: 0.45rem 1rem;
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-card {
  padding: 3rem;
  border-radius: 30px;
  width: 100%;
  max-width: 500px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 1rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--text-primary);
  outline: none;
}

.form-group input::placeholder {
  color: var(--text-secondary);
  opacity: 0.6;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-secondary {
  flex: 1;
  padding: 1rem;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 12px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .page-header h1 { font-size: 1.5rem; }
  .page-header p { font-size: 0.85rem; }

  .tabs-bar { width: 100%; max-width: none; justify-content: stretch; }
  .tabs-bar button { flex: 1; padding: 0.8rem 0.5rem; font-size: 0.85rem; }

  .card { padding: 1.2rem; border-radius: 20px; }
  .content-header { flex-direction: column; align-items: stretch; gap: 1rem; }
  .btn-primary { width: 100%; padding: 0.9rem; }

  .item-row { flex-direction: column; align-items: flex-start; gap: 0.8rem; padding: 1rem 0; }
  .item-actions { width: 100%; justify-content: space-between; }

  .region-header { flex-direction: column; align-items: flex-start; gap: 1rem; padding: 1rem; }
  .region-actions { width: 100%; justify-content: space-between; gap: 0.3rem; }
  .small-btn { flex: 1; text-align: center; font-size: 0.75rem; padding: 0.5rem; }

  .districts-container { padding: 0 1rem 1rem 1.5rem; }
  .district-row { flex-direction: column; align-items: flex-start; gap: 0.6rem; }
  .dist-actions { width: 100%; justify-content: space-between; }

  .modal-card { padding: 1.5rem; width: 95%; max-width: none; border-radius: 20px; }
  .modal-form { gap: 1rem; }
}
</style>
