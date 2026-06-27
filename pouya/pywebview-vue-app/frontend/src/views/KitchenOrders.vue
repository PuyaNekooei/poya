<template>
  <div class="kitchen-app">
    <!-- Header -->
    <div class="kitchen-header">
      <h1>آشپزخانه - سفارشات</h1>
      <div class="header-right">
        <el-button size="small" @click="loadOrders" :loading="loading">
          بروزرسانی
        </el-button>
        <span class="username">{{ username }}</span>
        <el-tag v-if="role" :type="roleTagType" size="small" effect="dark">
          {{ roleLabel }}
        </el-tag>
        <el-button
          v-if="isAdmin"
          type="primary"
          size="small"
          @click="goToDashboard"
        >
          صفحه فروش
        </el-button>
        <el-button type="text" class="logout-btn" @click="handleLogout">
          خروج
        </el-button>
      </div>
    </div>

    <!-- Board -->
    <div class="kitchen-board">
      <div
        v-for="column in columns"
        :key="column.status"
        class="kitchen-column"
      >
        <div class="column-header" :class="`status-${column.status}`">
          <span>{{ column.title }}</span>
          <el-badge :value="ordersByStatus[column.status].length" />
        </div>

        <div class="column-body">
          <div
            v-if="ordersByStatus[column.status].length === 0"
            class="empty-column"
          >
            سفارشی نیست
          </div>

          <div
            v-for="order in ordersByStatus[column.status]"
            :key="order.id"
            class="order-card"
            :class="{ 'is-urgent': order.elapsedMinutes >= 15 }"
          >
            <div class="card-top">
              <span class="order-number">{{ order.orderNumber }}</span>
              <span class="order-time">{{ order.elapsedMinutes }} دقیقه پیش</span>
            </div>

            <div class="card-meta">
              <span v-if="order.tableLabel" class="table-badge">{{ order.tableLabel }}</span>
              <span class="customer-name">{{ order.name }}</span>
            </div>

            <ul class="item-list">
              <li v-for="(item, idx) in order.items" :key="idx">
                <span class="item-qty">{{ item.quantity }}×</span>
                <span class="item-name">{{ item.name }}</span>
                <span v-if="item.notes" class="item-notes">({{ item.notes }})</span>
              </li>
            </ul>

            <div class="card-actions">
              <el-button
                v-if="column.next"
                :type="column.nextType"
                size="small"
                :loading="updatingId === order.id"
                @click="advance(order, column.next)"
              >
                {{ column.nextLabel }}
              </el-button>
              <el-button
                v-if="column.status !== 'ready'"
                size="small"
                :loading="updatingId === order.id"
                @click="advance(order, 'cancelled')"
              >
                لغو
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const username = ref(localStorage.getItem('username') || 'کاربر')
const role = ref(localStorage.getItem('role') || '')
const isAdmin = computed(() => role.value === 'admin')
const roleLabels = { admin: 'مدیر', chef: 'آشپز', cashier: 'صندوقدار' }
const roleTagTypes = { admin: 'success', chef: 'warning', cashier: 'primary' }
const roleLabel = computed(() => roleLabels[role.value] || '')
const roleTagType = computed(() => roleTagTypes[role.value] || 'info')

const loading = ref(false)
const updatingId = ref(null)
const orders = ref([])
const pollingInterval = ref(null)

// Kitchen workflow columns
const columns = [
  { status: 'pending', title: 'در انتظار', next: 'preparing', nextLabel: 'شروع آماده‌سازی', nextType: 'warning' },
  { status: 'preparing', title: 'در حال آماده‌سازی', next: 'ready', nextLabel: 'آماده شد', nextType: 'success' },
  { status: 'ready', title: 'آماده', next: 'completed', nextLabel: 'تحویل شد', nextType: 'primary' },
]

const ordersByStatus = computed(() => {
  const grouped = { pending: [], preparing: [], ready: [] }
  for (const order of orders.value) {
    if (grouped[order.status]) grouped[order.status].push(order)
  }
  return grouped
})

const elapsedMinutes = (createdAt) => {
  if (!createdAt) return 0
  const diffMs = Date.now() - new Date(createdAt).getTime()
  return Math.max(0, Math.floor(diffMs / 60000))
}

const tableLabel = (order) => {
  const t = order.table_details
  if (!t) return ''
  return t.name ? `میز ${t.number} - ${t.name}` : `میز ${t.number}`
}

const loadOrders = async () => {
  try {
    loading.value = true
    const response = await api.orders.today()
    const data = response.data.results ? response.data.results : response.data
    orders.value = data.map(order => ({
      id: order.id,
      orderNumber: order.order_number || `ORD-${order.id}`,
      name: order.customer_name || 'بدون نام',
      status: order.status,
      orderType: order.order_type || 'manual',
      tableLabel: tableLabel(order),
      elapsedMinutes: elapsedMinutes(order.created_at),
      items: (order.items || []).map(item => ({
        name: item.menu_item_details
          ? item.menu_item_details.name
          : (item.product_info ? item.product_info.product_name : 'نامشخص'),
        quantity: item.quantity,
        notes: item.notes || '',
      })),
    }))
  } catch (error) {
    console.error('Error loading kitchen orders:', error)
    ElMessage.error('خطا در بارگذاری سفارشات')
  } finally {
    loading.value = false
  }
}

const advance = async (order, newStatus) => {
  try {
    updatingId.value = order.id
    await api.orders.updateStatus(order.id, newStatus)
    await loadOrders()
    const labels = { preparing: 'در حال آماده‌سازی', ready: 'آماده', completed: 'تحویل شد', cancelled: 'لغو شد' }
    ElMessage.success(`سفارش ${order.orderNumber}: ${labels[newStatus] || newStatus}`)
  } catch (error) {
    console.error('Error updating order status:', error)
    ElMessage.error('خطا در تغییر وضعیت سفارش')
  } finally {
    updatingId.value = null
  }
}

const goToDashboard = () => router.push('/dashboard')

const handleLogout = async () => {
  try {
    await api.auth.logout()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    ;['authToken', 'isAuthenticated', 'username', 'userId', 'role', 'isAdmin']
      .forEach(key => localStorage.removeItem(key))
    router.push('/login')
  }
}

onMounted(() => {
  loadOrders()
  pollingInterval.value = setInterval(loadOrders, 15000)
})

onUnmounted(() => {
  if (pollingInterval.value) clearInterval(pollingInterval.value)
})
</script>

<style scoped>
.kitchen-app {
  direction: rtl;
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

.kitchen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #2c3e50;
  color: #fff;
  padding: 12px 20px;
}

.kitchen-header h1 {
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

.kitchen-board {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px;
  align-items: start;
}

.kitchen-column {
  background: #e9edf1;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  min-height: 200px;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  font-weight: 700;
  color: #fff;
  border-radius: 10px 10px 0 0;
}

.column-header.status-pending { background: #e6a23c; }
.column-header.status-preparing { background: #409eff; }
.column-header.status-ready { background: #67c23a; }

.column-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-column {
  text-align: center;
  color: #909399;
  padding: 24px 0;
  font-size: 14px;
}

.order-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  border-right: 4px solid #dcdfe6;
}

.order-card.is-urgent {
  border-right-color: #f56c6c;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.order-number {
  font-weight: 700;
  color: #2c3e50;
}

.order-time {
  font-size: 12px;
  color: #909399;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.table-badge {
  background: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
}

.customer-name {
  font-size: 13px;
  color: #606266;
}

.item-list {
  list-style: none;
  margin: 0 0 10px 0;
  padding: 0;
}

.item-list li {
  display: flex;
  gap: 6px;
  padding: 3px 0;
  font-size: 15px;
  border-bottom: 1px dashed #f0f0f0;
}

.item-qty {
  font-weight: 700;
  color: #409eff;
  min-width: 32px;
}

.item-notes {
  color: #e6a23c;
  font-size: 13px;
}

.card-actions {
  display: flex;
  gap: 8px;
}
</style>
