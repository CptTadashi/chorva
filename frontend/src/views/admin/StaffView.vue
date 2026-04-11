<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const staff = ref([]);
const loading = ref(true);
const currentUsername = localStorage.getItem('admin_user');

// Form state
const showAddModal = ref(false);
const formData = ref({
  username: '',
  password: '',
  role: 'moderator'
});

const showPasswordModal = ref(false);
const selectedAdmin = ref(null);
const passwordForm = ref({
  new_password: ''
});

const fetchStaff = async () => {
  try {
    const response = await api.get('/admin/staff/staff');
    staff.value = response.data;
  } catch (err) {
    console.error("Jamoani yuklashda xato:", err);
  } finally {
    loading.value = false;
  }
};

const handleAddStaff = async () => {
  try {
    await api.post('/admin/staff/staff', formData.value);
    showAddModal.value = false;
    fetchStaff();
    formData.value = { username: '', password: '', role: 'moderator' };
  } catch (err) {
    alert(err.response?.data?.detail || "Moderator qo'shishda xatolik");
  }
};

const deleteStaff = async (id) => {
  if (!confirm("Haqiqatan ham ushbu adminni o'chirmoqchimisiz?")) return;
  try {
    await api.delete(`/admin/staff/staff/${id}`);
    fetchStaff();
  } catch (err) {
    alert("O'chirishda xatolik yuz berdi");
  }
};

const openPasswordModal = (admin) => {
  selectedAdmin.value = admin;
  passwordForm.value.new_password = '';
  showPasswordModal.value = true;
};

const handleUpdatePassword = async () => {
  try {
    await api.patch(`/admin/staff/staff/${selectedAdmin.value.id}/password`, passwordForm.value);
    showPasswordModal.value = false;
    alert("Parol muvaffaqiyatli yangilandi");
  } catch (err) {
    alert(err.response?.data?.detail || "Parolni yangilashda xatolik");
  }
};

onMounted(fetchStaff);
</script>

<template>
  <div class="staff-view fade-in">
    <header class="page-header">
      <div class="header-flex">
        <div>
          <h1>Jamoani Boshqarish</h1>
          <p>Adminlar va moderatorlar ro'yxati</p>
        </div>
        <button @click="showAddModal = true" class="btn-primary">+ Yangi qo'shish</button>
      </div>
    </header>

    <div class="table-container glass">
      <!-- Desktop Table -->
      <table v-if="!loading" class="data-table desktop-only">
        <thead>
          <tr>
            <th>Username</th>
            <th>Rol</th>
            <th>Holat</th>
            <th>Qo'shilgan sana</th>
            <th>Harakat</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="admin in staff" :key="admin.id">
            <td class="username-cell">
              <span class="avatar-sm">{{ admin.username.charAt(0).toUpperCase() }}</span>
              {{ admin.username }} 
              <span v-if="admin.username === currentUsername" class="self-badge">(Siz)</span>
            </td>
            <td>
              <span class="role-badge" :class="admin.role">
                {{ admin.role === 'superadmin' ? 'Superadmin' : 'Moderator' }}
              </span>
            </td>
            <td>
              <span class="status-dot" :class="{ active: admin.is_active }"></span>
              {{ admin.is_active ? 'Faol' : 'Nofaol' }}
            </td>
            <td>{{ new Date(admin.created_at).toLocaleDateString() }}</td>
            <td>
              <div class="actions-cell">
                <button 
                  @click="openPasswordModal(admin)" 
                  class="action-btn"
                  title="Parolni yangilash"
                >🔐</button>
                <button 
                  v-if="admin.username !== currentUsername" 
                  @click="deleteStaff(admin.id)" 
                  class="delete-btn"
                  title="O'chirish"
                >🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Mobile List -->
      <div v-if="!loading" class="mobile-only staff-cards">
        <div v-for="admin in staff" :key="admin.id" class="staff-card border-b">
          <div class="card-header">
            <div class="user-info">
              <span class="avatar-sm">{{ admin.username.charAt(0).toUpperCase() }}</span>
              <div class="name-box">
                <span class="name">{{ admin.username }}</span>
                <span v-if="admin.username === currentUsername" class="self-badge">(Siz)</span>
              </div>
            </div>
            <span class="role-badge" :class="admin.role">
              {{ admin.role === 'superadmin' ? 'Super' : 'Mod' }}
            </span>
          </div>
          <div class="card-body">
             <div class="item">
               <span class="label">Holat:</span>
               <span class="val">{{ admin.is_active ? 'Faol' : 'Nofaol' }}</span>
             </div>
             <div class="item">
               <span class="label">Sana:</span>
               <span class="val">{{ new Date(admin.created_at).toLocaleDateString() }}</span>
             </div>
          </div>
          <div class="card-actions">
            <button @click="openPasswordModal(admin)" class="btn-m-action">Parolni almashtirish</button>
            <button v-if="admin.username !== currentUsername" @click="deleteStaff(admin.id)" class="btn-m-delete">O'chirish</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showAddModal" class="modal-overlay">
      <div class="modal-card glass">
        <h2>Yangi xodim qo'shish</h2>
        <form @submit.prevent="handleAddStaff" class="modal-form">
          <div class="form-group">
            <label>Login (Username)</label>
            <input v-model="formData.username" type="text" required>
          </div>
          <div class="form-group">
            <label>Parol</label>
            <input v-model="formData.password" type="password" required>
          </div>
          <div class="form-group">
            <label>Rol</label>
            <select v-model="formData.role" class="select-input">
              <option value="moderator">Moderator</option>
              <option value="superadmin">Superadmin</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Bekor qilish</button>
            <button type="submit" class="btn-primary">Qo'shish</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Password Update Modal -->
    <div v-if="showPasswordModal" class="modal-overlay">
      <div class="modal-card glass">
        <h2>Parolni yangilash</h2>
        <p class="modal-subtitle">Admin: {{ selectedAdmin?.username }}</p>
        <form @submit.prevent="handleUpdatePassword" class="modal-form">
          <div class="form-group">
            <label>Yangi parol</label>
            <input v-model="passwordForm.new_password" type="password" required placeholder="Kamida 6 ta belgi">
          </div>
          <div class="modal-actions">
            <button type="button" @click="showPasswordModal = false" class="btn-secondary">Bekor qilish</button>
            <button type="submit" class="btn-primary">Yangilash</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-container {
  border-radius: 25px;
  overflow: hidden;
  padding: 1.5rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 1.2rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.username-cell {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-weight: 600;
}

.avatar-sm {
  width: 32px;
  height: 32px;
  background: var(--grad-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.self-badge {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 400;
}

.role-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.role-badge.superadmin { background: rgba(245, 158, 11, 0.1); color: var(--accent-secondary); }
.role-badge.moderator { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9ca3af;
  margin-right: 0.5rem;
}

.status-dot.active { background: #10b981; }

.delete-btn {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.delete-btn:hover { transform: scale(1.2); }

.actions-cell {
  display: flex;
  gap: 0.8rem;
  align-items: center;
}

.action-btn {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.action-btn:hover { transform: scale(1.2); }

.modal-subtitle {
  color: var(--text-secondary);
  margin-top: -1.5rem;
  margin-bottom: 1rem;
}

/* Modal Styles restated for StaffView specifically if needed, but reusable */
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
  max-width: 450px;
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
}

.form-group input, .select-input {
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

.select-input option { background: #05070a; }

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

.mobile-only { display: none; }

@media (max-width: 768px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }

  .table-container { padding: 0.8rem; border-radius: 20px; }
  
  .staff-card { padding: 1.2rem 0; }
  .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
  .user-info { display: flex; align-items: center; gap: 0.8rem; }
  .name-box { display: flex; flex-direction: column; }
  .name { font-weight: 700; font-size: 1.1rem; }

  .card-body { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.2rem; }
  .card-body .item { display: flex; flex-direction: column; }
  .card-body .label { font-size: 0.75rem; color: var(--text-secondary); }
  .card-body .val { font-weight: 600; font-size: 0.9rem; }

  .card-actions { display: flex; gap: 0.5rem; }
  .btn-m-action, .btn-m-delete {
    flex: 1;
    padding: 0.8rem;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid var(--border-color);
    background: rgba(255,255,255,0.05);
  }
  .btn-m-action { color: var(--accent-primary); border-color: var(--accent-primary); }
  .btn-m-delete { color: #ef4444; border-color: #ef4444; }

  .modal-card { padding: 1.5rem; border-radius: 20px; width: 95%; max-width: none; }
  .modal-subtitle { margin-top: -0.5rem; font-size: 0.9rem; }
}
</style>
