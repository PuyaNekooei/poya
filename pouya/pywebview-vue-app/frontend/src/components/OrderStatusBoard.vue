<template>
  <div class="status-board">
    <div class="status-board-header" :class="{ 'no-title': !title }">
      <h3 v-if="title">{{ title }}</h3>
      <el-button size="small" :loading="loading" @click="loadOrders">
        بروزرسانی
      </el-button>
    </div>

    <div v-if="orders.length === 0 && !loading" class="status-empty">
      امروز سفارشی ثبت نشده است
    </div>

    <div v-else class="status-list">
      <div v-for="order in orders" :key="order.id" class="status-row">
        <div class="status-row-main">
          <span class="order-number">{{ order.order_number }}</span>
          <span v-if="order.customer_name" class="customer-name">
            {{ order.customer_name }}
          </span>
          <span v-if="order.table_number" class="table-badge">
            میز {{ order.table_number }}
          </span>
        </div>
        <div class="status-row-side">
          <span class="order-time">{{ elapsedLabel(order.created_at) }}</span>
          <el-tag :type="statusType(order.status)" effect="dark" size="small">
            {{ statusLabel(order) }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const props = defineProps({
  title: { type: String, default: 'وضعیت سفارش‌ها' },
  // Auto-refresh interval in ms; pass 0 to disable polling.
  pollMs: { type: Number, default: 15000 },
})

// Status key -> { label fallback, el-tag type }. Backend also sends
// status_display, which we prefer for the label.
const STATUS_META = {
  pending: { label: 'در انتظار', type: 'warning' },
  preparing: { label: 'در حال آماده‌سازی', type: 'primary' },
  ready: { label: 'آماده', type: 'success' },
  completed: { label: 'تکمیل شده', type: 'info' },
  cancelled: { label: 'لغو شده', type: 'danger' },
}

const orders = ref([])
const loading = ref(false)
let timer = null

const statusType = (status) => STATUS_META[status]?.type || 'info'
const statusLabel = (order) =>
  order.status_display || STATUS_META[order.status]?.label || order.status

const elapsedLabel = (createdAt) => {
  if (!createdAt) return ''
  const minutes = Math.max(0, Math.floor((Date.now() - new Date(createdAt).getTime()) / 60000))
  if (minutes < 1) return 'هم‌اکنون'
  if (minutes < 60) return `${minutes} دقیقه پیش`
  return `${Math.floor(minutes / 60)} ساعت پیش`
}

const loadOrders = async () => {
  try {
    loading.value = true
    const response = await api.orders.statusBoard()
    orders.value = response.data.results ? response.data.results : response.data
  } catch (error) {
    console.error('Error loading order status board:', error)
    ElMessage.error('خطا در بارگذاری وضعیت سفارشات')
  } finally {
    loading.value = false
  }
}

defineExpose({ loadOrders })

onMounted(() => {
  loadOrders()
  if (props.pollMs > 0) timer = setInterval(loadOrders, props.pollMs)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.status-board {
  direction: rtl;
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.status-board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

/* When embedded without a title, keep the refresh button aligned to the start */
.status-board-header.no-title {
  justify-content: flex-end;
}

.status-board-header h3 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.status-empty {
  text-align: center;
  color: #909399;
  padding: 24px 0;
  font-size: 14px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  background: #f7f8fa;
  border-right: 3px solid #dcdfe6;
}

.status-row-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.order-number {
  font-weight: 700;
  color: #2c3e50;
}

.customer-name {
  font-size: 13px;
  color: #606266;
}

.table-badge {
  background: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
}

.status-row-side {
  display: flex;
  align-items: center;
  gap: 10px;
}

.order-time {
  font-size: 12px;
  color: #909399;
}
</style>
