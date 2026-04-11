<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';

const router = useRouter();
const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = "Iltimos, barcha maydonlarni to'ldiring";
    return;
  }

  loading.value = true;
  error.value = '';

  try {
    const response = await api.post('/admin/auth/login', {
      username: username.value,
      password: password.value
    });

    if (response.data && response.data.access_token) {
      // Token, username va rolini saqlash
      localStorage.setItem('admin_token', response.data.access_token);
      localStorage.setItem('admin_user', response.data.username);
      localStorage.setItem('admin_role', response.data.role);
      
      // Dashboard'ga (yoki moderatsiyaga) o'tish
      if (response.data.role === 'superadmin') {
        router.push('/admin/dashboard');
      } else {
        router.push('/admin/moderation');
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || "Kirishda xatolik yuz berdi";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="admin-login-view fade-in">
    <div class="login-card glass">
      <div class="login-header">
        <span class="icon">🛡️</span>
        <h2>Admin Login</h2>
        <p>Boshqaruv paneliga kirish</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <input 
            v-model="username" 
            type="text" 
            placeholder="Login" 
            class="input"
            :disabled="loading"
          >
        </div>
        <div class="input-group">
          <input 
            v-model="password" 
            type="password" 
            placeholder="Parol" 
            class="input"
            :disabled="loading"
          >
        </div>
        
        <p v-if="error" class="error-msg">{{ error }}</p>
        
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Kirilmoqda...' : 'Kirish' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.admin-login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.login-card {
  padding: 3.5rem;
  border-radius: 35px;
  text-align: center;
  max-width: 450px;
  width: 100%;
}

.login-header .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.login-header h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.login-header p {
  color: var(--text-secondary);
  font-size: 1rem;
}

.login-form {
  margin-top: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.input {
  width: 100%;
  padding: 1.2rem;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}

.input::placeholder {
  color: var(--text-secondary);
  opacity: 0.6;
}

.input:focus {
  border-color: var(--accent-primary);
  background: rgba(255, 255, 255, 0.07);
}

.error-msg {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  padding: 0.8rem;
  border-radius: 10px;
  font-size: 0.9rem;
}

.btn-primary {
  margin-top: 1rem;
  padding: 1.2rem;
  font-size: 1.1rem;
}
</style>
