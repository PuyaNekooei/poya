<template>
  <div class="order-status-app">
    <div class="os-header">
      <h1>وضعیت سفارش‌ها</h1>
      <div class="header-right">
        <span class="username">{{ username }}</span>
        <el-tag v-if="role" :type="roleTagType" size="small" effect="dark">
          {{ roleLabel }}
        </el-tag>
        <el-button v-if="isAdmin" type="primary" size="small" @click="goToDashboard">
          صفحه فروش
        </el-button>
        <el-button type="text" class="logout-btn" @click="handleLogout">
          خروج
        </el-button>
      </div>
    </div>

    <div class="os-body">
      <OrderStatusBoard title="سفارش‌های امروز" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import OrderStatusBoard from '../components/OrderStatusBoard.vue'

const router = useRouter()
const username = ref(localStorage.getItem('username') || 'کاربر')
const role = ref(localStorage.getItem('role') || '')
const isAdmin = computed(() => role.value === 'admin')
const roleLabels = { admin: 'مدیر', chef: 'آشپز', cashier: 'صندوقدار', customer: 'مشتری' }
const roleTagTypes = { admin: 'success', chef: 'warning', cashier: 'primary', customer: 'info' }
const roleLabel = computed(() => roleLabels[role.value] || '')
const roleTagType = computed(() => roleTagTypes[role.value] || 'info')

const goToDashboard = () => router.push('/dashboard')

const handleLogout = async () => {
  try {
    await api.auth.logout()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    ;['authToken', 'isAuthenticated', 'username', 'userId', 'role', 'roles', 'isAdmin']
      .forEach((key) => localStorage.removeItem(key))
    router.push('/login')
  }
}
</script>

<style scoped>
.order-status-app {
  direction: rtl;
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

.os-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #2c3e50;
  color: #fff;
  padding: 12px 20px;
}

.os-header h1 {
  margin: 0;
  font-size: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right .username {
  font-size: 14px;
}

.logout-btn {
  color: #ff9a9a;
}

.os-body {
  flex: 1;
  padding: 16px;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}
</style>
