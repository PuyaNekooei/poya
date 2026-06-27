<template>
  <div class="stats-app">
    <!-- Header -->
    <div class="stats-header">
      <h1>آمار و پیش‌بینی</h1>
      <div class="header-right">
        <el-select v-model="days" size="small" style="width: 130px" @change="loadAll">
          <el-option :value="7" label="۷ روز اخیر" />
          <el-option :value="14" label="۱۴ روز اخیر" />
          <el-option :value="30" label="۳۰ روز اخیر" />
          <el-option :value="90" label="۹۰ روز اخیر" />
        </el-select>
        <el-button size="small" @click="loadAll" :loading="loading">بروزرسانی</el-button>
        <el-button type="primary" size="small" @click="router.push('/dashboard')">صفحه فروش</el-button>
        <el-button type="text" class="logout-btn" @click="handleLogout">خروج</el-button>
      </div>
    </div>

    <div v-loading="loading" class="stats-body">
      <el-empty v-if="stats && !stats.has_data" description="هنوز داده‌ای برای نمایش وجود ندارد" />

      <template v-else-if="stats">
        <!-- KPI cards -->
        <div class="kpi-row">
          <div class="kpi-card">
            <div class="kpi-label">درآمد امروز</div>
            <div class="kpi-value">{{ formatPrice(stats.kpis.today_revenue) }}</div>
            <div class="kpi-sub" :class="trendClass(stats.kpis.today_revenue, stats.kpis.yesterday_revenue)">
              {{ comparePct(stats.kpis.today_revenue, stats.kpis.yesterday_revenue) }} نسبت به دیروز
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">سفارشات امروز</div>
            <div class="kpi-value">{{ stats.kpis.today_orders }}</div>
            <div class="kpi-sub" :class="trendClass(stats.kpis.today_orders, stats.kpis.yesterday_orders)">
              {{ comparePct(stats.kpis.today_orders, stats.kpis.yesterday_orders) }} نسبت به دیروز
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">میانگین ارزش سفارش</div>
            <div class="kpi-value">{{ formatPrice(stats.kpis.avg_order_value) }}</div>
            <div class="kpi-sub">در بازه انتخابی</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">درآمد بازه ({{ stats.days }} روز)</div>
            <div class="kpi-value">{{ formatPrice(stats.kpis.range_revenue) }}</div>
            <div class="kpi-sub">{{ stats.kpis.range_orders }} سفارش</div>
          </div>
        </div>

        <!-- Revenue & orders trend -->
        <div class="panel">
          <h2>روند درآمد و سفارشات</h2>
          <AppChart
            v-if="stats.revenue_trend.length"
            type="bar"
            :data="revenueTrendData"
            :options="revenueTrendOptions"
            height="300px"
          />
          <div v-else class="muted">داده‌ای نیست</div>
        </div>

        <div class="grid-2">
          <!-- Top items -->
          <div class="panel">
            <h2>پرفروش‌ترین غذاها</h2>
            <el-table v-if="stats.top_items.length" :data="stats.top_items" size="small" stripe>
              <el-table-column type="index" label="#" width="45" />
              <el-table-column prop="name" label="نام" />
              <el-table-column prop="category" label="دسته" width="110" />
              <el-table-column prop="quantity" label="تعداد" width="70" align="center" />
              <el-table-column label="درآمد" width="120" align="left">
                <template #default="{ row }">{{ formatPrice(row.revenue) }}</template>
              </el-table-column>
            </el-table>
            <div v-else class="muted">داده‌ای نیست</div>
          </div>

          <!-- Orders by hour -->
          <div class="panel">
            <h2>سفارشات بر اساس ساعت</h2>
            <AppChart
              type="bar"
              :data="ordersByHourData"
              :options="ordersByHourOptions"
              height="260px"
            />
          </div>
        </div>

        <div class="grid-2">
          <!-- Status + type -->
          <div class="panel">
            <h2>وضعیت و نوع سفارشات</h2>
            <div class="chip-row">
              <div v-for="(v, code) in stats.by_status" :key="code" class="chip">
                <span>{{ v.label }}</span><strong>{{ v.count }}</strong>
              </div>
            </div>
            <div class="chip-row">
              <div class="chip type"><span>دستی</span><strong>{{ stats.by_type.manual }}</strong></div>
            </div>
          </div>

          <!-- By table -->
          <div class="panel">
            <h2>فعالیت میزها</h2>
            <el-table v-if="stats.by_table.length" :data="stats.by_table" size="small" stripe max-height="260">
              <el-table-column label="میز" width="120">
                <template #default="{ row }">{{ row.name ? `${row.table} - ${row.name}` : `میز ${row.table}` }}</template>
              </el-table-column>
              <el-table-column prop="orders" label="سفارشات" align="center" />
              <el-table-column label="درآمد" align="left">
                <template #default="{ row }">{{ formatPrice(row.revenue) }}</template>
              </el-table-column>
            </el-table>
            <div v-else class="muted">سفارشی به میز اختصاص نیافته است</div>
          </div>
        </div>

        <!-- ============ PREDICTIONS ============ -->
        <div class="section-title">
          <h2>پیش‌بینی‌ها</h2>
          <span v-if="predictions && predictions.has_data" class="muted">
            روش: میانگین فصلی روز هفته + میانگین متحرک ۷ روزه — بر پایه {{ predictions.history_days }} روز داده
          </span>
        </div>

        <el-empty
          v-if="predictions && !predictions.has_data"
          description="برای پیش‌بینی به داده‌ی فروش اخیر بیشتری نیاز است"
        />

        <template v-else-if="predictions">
          <!-- Daily sales forecast -->
          <div class="panel">
            <h2>پیش‌بینی فروش روزانه ({{ predictions.horizon }} روز آینده)</h2>
            <AppChart
              v-if="predictions.daily_sales_forecast.length"
              type="bar"
              :data="forecastData"
              :options="forecastOptions"
              height="300px"
            />
            <div v-else class="muted">داده‌ای نیست</div>
          </div>

          <!-- Busy hours + busiest weekday -->
          <div class="panel">
            <h2>ساعات و روزهای شلوغ پیش‌بینی‌شده</h2>
            <div class="busy-summary">
              <div>
                <span class="muted">ساعات اوج: </span>
                <el-tag v-for="h in predictions.peak_hours" :key="h" type="warning" size="small" class="peak-tag">
                  {{ h }}:00
                </el-tag>
                <span v-if="!predictions.peak_hours.length" class="muted">—</span>
              </div>
              <div v-if="predictions.busiest_weekday">
                <span class="muted">شلوغ‌ترین روز: </span>
                <el-tag type="danger" size="small">
                  {{ predictions.busiest_weekday.name }} (میانگین {{ predictions.busiest_weekday.avg_orders }} سفارش)
                </el-tag>
              </div>
            </div>
            <AppChart
              type="bar"
              :data="busyHoursData"
              :options="busyHoursOptions"
              height="260px"
            />
          </div>

          <div class="grid-2">
            <!-- Per-item demand -->
            <div class="panel">
              <h2>پیش‌بینی تقاضای غذاها</h2>
              <el-table v-if="predictions.item_demand.length" :data="predictions.item_demand" size="small" stripe max-height="320">
                <el-table-column prop="name" label="نام غذا" />
                <el-table-column prop="predicted_next_day" label="فردا" width="80" align="center" />
                <el-table-column prop="predicted_horizon" :label="`${predictions.horizon} روز`" width="90" align="center" />
              </el-table>
              <div v-else class="muted">تقاضای قابل توجهی پیش‌بینی نشد</div>
            </div>

            <!-- Restock suggestions -->
            <div class="panel">
              <h2>پیشنهاد تأمین موجودی (فردا)</h2>
              <el-table v-if="predictions.restock_suggestions.length" :data="predictions.restock_suggestions" size="small" stripe max-height="320">
                <el-table-column prop="name" label="نام غذا" />
                <el-table-column prop="predicted_next_day" label="تقاضا" width="75" align="center" />
                <el-table-column prop="current_inventory" label="موجودی" width="75" align="center" />
                <el-table-column label="تأمین" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.suggested_restock > 0 ? 'danger' : 'success'" size="small">
                      {{ row.suggested_restock }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <div v-else class="muted">پیشنهادی برای تأمین موجودی نیست</div>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '../api'
import AppChart from '../components/AppChart.vue'

const router = useRouter()
const loading = ref(false)
const days = ref(30)
const stats = ref(null)
const predictions = ref(null)

const formatPrice = (n) => (n == null ? '0' : Number(n).toLocaleString('en-US'))

// Reusable axis-title style with the app's Persian font.
const axisTitle = (text) => ({
  display: true,
  text,
  font: { family: 'Vazir, sans-serif', size: 12, weight: '600' },
  color: '#606266',
})

const PALETTE = {
  blue: '#409eff',
  blueFill: 'rgba(64,158,255,0.65)',
  orange: '#e6a23c',
  orangeFill: 'rgba(230,162,60,0.85)',
  green: '#67c23a',
  greenFill: 'rgba(103,194,58,0.6)',
}

// --- Chart 1: revenue (bars) + orders (line) trend, dual axis ---
const revenueTrendData = computed(() => {
  const t = stats.value?.revenue_trend || []
  return {
    labels: t.map((d) => d.jdate),
    datasets: [
      {
        type: 'bar',
        label: 'درآمد (ریال)',
        data: t.map((d) => d.revenue),
        backgroundColor: PALETTE.blueFill,
        borderColor: PALETTE.blue,
        borderWidth: 1,
        yAxisID: 'y',
        order: 2,
      },
      {
        type: 'line',
        label: 'تعداد سفارش',
        data: t.map((d) => d.orders),
        borderColor: PALETTE.orange,
        backgroundColor: PALETTE.orange,
        pointRadius: 3,
        tension: 0.3,
        yAxisID: 'y1',
        order: 1,
      },
    ],
  }
})
const revenueTrendOptions = computed(() => ({
  scales: {
    x: { title: axisTitle('تاریخ') },
    y: {
      position: 'right',
      title: axisTitle('درآمد (ریال)'),
      ticks: { callback: (v) => formatPrice(v) },
    },
    y1: {
      position: 'left',
      beginAtZero: true,
      grid: { drawOnChartArea: false },
      title: axisTitle('تعداد سفارش'),
      ticks: { precision: 0, font: { family: 'Vazir, sans-serif', size: 11 } },
    },
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: (ctx) =>
          ctx.dataset.yAxisID === 'y'
            ? `درآمد: ${formatPrice(ctx.parsed.y)} ریال`
            : `سفارش: ${ctx.parsed.y}`,
      },
    },
  },
}))

// --- Chart 2: orders by hour ---
const ordersByHourData = computed(() => {
  const h = stats.value?.by_hour || []
  return {
    labels: h.map((x) => `${x.hour}:00`),
    datasets: [
      {
        label: 'تعداد سفارش',
        data: h.map((x) => x.orders),
        backgroundColor: PALETTE.greenFill,
        borderColor: PALETTE.green,
        borderWidth: 1,
      },
    ],
  }
})
const ordersByHourOptions = computed(() => ({
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.y} سفارش` } },
  },
  scales: {
    x: { title: axisTitle('ساعت روز') },
    y: { title: axisTitle('تعداد سفارش'), ticks: { precision: 0 } },
  },
}))

// --- Chart 3: predicted busy hours (peaks highlighted) ---
const busyHoursData = computed(() => {
  const h = predictions.value?.busy_hours || []
  return {
    labels: h.map((x) => `${x.hour}:00`),
    datasets: [
      {
        label: 'میانگین سفارش',
        data: h.map((x) => x.avg_orders),
        backgroundColor: h.map((x) => (x.is_peak ? PALETTE.orangeFill : PALETTE.greenFill)),
        borderColor: h.map((x) => (x.is_peak ? PALETTE.orange : PALETTE.green)),
        borderWidth: 1,
      },
    ],
  }
})
const busyHoursOptions = computed(() => ({
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => {
          const peak = predictions.value?.busy_hours?.[ctx.dataIndex]?.is_peak
          return `میانگین: ${ctx.parsed.y} سفارش${peak ? ' (اوج)' : ''}`
        },
      },
    },
  },
  scales: {
    x: { title: axisTitle('ساعت روز') },
    y: { title: axisTitle('میانگین سفارش') },
  },
}))

// --- Chart 4: daily sales forecast (revenue bars + orders line) ---
const forecastData = computed(() => {
  const f = predictions.value?.daily_sales_forecast || []
  return {
    labels: f.map((d) => d.jdate),
    datasets: [
      {
        type: 'bar',
        label: 'درآمد پیش‌بینی‌شده (ریال)',
        data: f.map((d) => d.predicted_revenue),
        backgroundColor: PALETTE.blueFill,
        borderColor: PALETTE.blue,
        borderWidth: 1,
        yAxisID: 'y',
        order: 2,
      },
      {
        type: 'line',
        label: 'سفارش پیش‌بینی‌شده',
        data: f.map((d) => d.predicted_orders),
        borderColor: PALETTE.orange,
        backgroundColor: PALETTE.orange,
        pointRadius: 3,
        tension: 0.3,
        yAxisID: 'y1',
        order: 1,
      },
    ],
  }
})
const forecastOptions = computed(() => ({
  scales: {
    x: { title: axisTitle('تاریخ') },
    y: {
      position: 'right',
      title: axisTitle('درآمد (ریال)'),
      ticks: { callback: (v) => formatPrice(v) },
    },
    y1: {
      position: 'left',
      beginAtZero: true,
      grid: { drawOnChartArea: false },
      title: axisTitle('تعداد سفارش'),
      ticks: { precision: 0, font: { family: 'Vazir, sans-serif', size: 11 } },
    },
  },
  plugins: {
    tooltip: {
      callbacks: {
        label: (ctx) =>
          ctx.dataset.yAxisID === 'y'
            ? `درآمد: ${formatPrice(ctx.parsed.y)} ریال`
            : `سفارش: ${ctx.parsed.y}`,
      },
    },
  },
}))

const comparePct = (current, previous) => {
  if (!previous) return current ? '+∞٪' : '۰٪'
  const pct = Math.round(((current - previous) / previous) * 100)
  return `${pct >= 0 ? '+' : ''}${pct}٪`
}
const trendClass = (current, previous) =>
  current >= previous ? 'up' : 'down'

const loadAll = async () => {
  try {
    loading.value = true
    const [s, p] = await Promise.all([
      api.analytics.statistics(days.value),
      api.analytics.predictions(7),
    ])
    stats.value = s.data
    predictions.value = p.data
  } catch (error) {
    console.error('Error loading analytics:', error)
    ElMessage.error('خطا در بارگذاری آمار')
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  try { await api.auth.logout() } catch (e) { /* ignore */ }
  ;['authToken', 'isAuthenticated', 'username', 'userId', 'role', 'isAdmin']
    .forEach(key => localStorage.removeItem(key))
  router.push('/login')
}

onMounted(loadAll)
</script>

<style scoped>
.stats-app {
  direction: rtl;
  min-height: 100vh;
  background: #f0f2f5;
}

.stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #2c3e50;
  color: #fff;
  padding: 12px 20px;
}
.stats-header h1 { margin: 0; font-size: 20px; }
.header-right { display: flex; align-items: center; gap: 10px; }
.logout-btn { color: #ff9a9a; }

.stats-body { padding: 16px; min-height: 300px; }

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.kpi-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}
.kpi-label { color: #909399; font-size: 13px; }
.kpi-value { font-size: 24px; font-weight: 700; color: #2c3e50; margin: 6px 0; }
.kpi-sub { font-size: 12px; color: #909399; }
.kpi-sub.up { color: #67c23a; }
.kpi-sub.down { color: #f56c6c; }

.panel {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}
.panel h2 { margin: 0 0 14px 0; font-size: 16px; color: #2c3e50; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.chip-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
.chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f4f6f9;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
}
.chip strong { color: #409eff; font-size: 16px; }
.chip.type strong { color: #e6a23c; }

.section-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 24px 0 12px;
  border-top: 2px solid #dcdfe6;
  padding-top: 16px;
}
.section-title h2 { margin: 0; color: #2c3e50; }

.busy-summary { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.peak-tag { margin-left: 4px; }

.muted { color: #909399; font-size: 13px; }
</style>
