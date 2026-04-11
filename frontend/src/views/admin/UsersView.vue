<script setup>
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const users = ref([]);
const loading = ref(true);

const fetchUsers = async () => {
  try {
    const response = await api.get('/admin/users/users');
    users.value = response.data;
  } catch (error) {
    console.error("Foydalanuvchilarni yuklashda xato:", error);
  } finally {
    loading.value = false;
  }
};

const toggleStatus = async (user) => {
  try {
    const response = await api.post(`/admin/users/users/${user.id}/toggle-status`);
    user.is_active = response.data.is_active;
  } catch (error) {
    alert("Holatni o'zgartirishda xatolik yuz berdi");
  }
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString();
};

onMounted(() => {
  fetchUsers();
});
</script>

<template>
  <div class="users-view fade-in">
    <header class="page-header">
      <h1>Foydalanuvchilar</h1>
      <p>Botdan ro'yxatdan o'tgan barcha foydalanuvchilar boshqaruvi</p>
    </header>

    <div class="table-container glass">
      <table v-if="!loading" class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Ism / Telegram</th>
            <th>Telefon</th>
            <th>Sana</th>
            <th>Holat</th>
            <th>Harakat</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>#{{ user.id }}</td>
            <td>
              <div class="user-cell">
                <span class="name">{{ user.full_name || 'Ism kiritilmagan' }}</span>
                <span class="tg-id">ID: {{ user.telegram_id }}</span>
              </div>
            </td>
            <td>{{ user.phone_number }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <span class="status-badge" :class="user.is_active ? 'active' : 'blocked'">
                {{ user.is_active ? 'Faol' : 'Bloklangan' }}
              </span>
            </td>
            <td>
              <button 
                @click="toggleStatus(user)" 
                class="action-btn"
                :class="user.is_active ? 'btn-danger' : 'btn-success'"
              >
                {{ user.is_active ? 'Bloklash' : 'Faollashtirish' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="loading" class="loading-padding">
        <p>Yuklanmoqda...</p>
      </div>

      <div v-if="!loading && users.length === 0" class="empty-state">
        <p>Foydalanuvchilar topilmadi.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 2.5rem;
}

.table-container {
  border-radius: 25px;
  overflow: hidden;
  padding: 1rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  padding: 1.2rem;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 1.2rem;
  border-bottom: 1px solid var(--border-color);
}

.user-cell {
  display: flex;
  flex-direction: column;
}

.user-cell .name {
  font-weight: 600;
}

.user-cell .tg-id {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.status-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 100px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-primary);
}

.status-badge.blocked {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn {
  padding: 0.5rem 1rem;
  border-radius: 10px;
  border: none;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-danger:hover {
  background: #ef4444;
  color: white;
}

.btn-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-primary);
}

.btn-success:hover {
  background: var(--accent-primary);
  color: white;
}

.loading-padding, .empty-state {
  padding: 4rem;
  text-align: center;
  color: var(--text-secondary);
}
</style>
