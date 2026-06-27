<template>
  <div class="app-chart" :style="{ height: height }">
    <component :is="chartComponent" :data="data" :options="mergedOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarController,
  LineController,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
} from 'chart.js'

// Register once (idempotent across imports).
ChartJS.register(
  BarController,
  LineController,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title
)

const props = defineProps({
  type: { type: String, default: 'bar' }, // 'bar' | 'line'
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) },
  height: { type: String, default: '280px' },
})

const chartComponent = computed(() => (props.type === 'line' ? Line : Bar))

// Shared defaults: RTL legend/tooltip, readable Persian font, gridlines.
const DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      display: true,
      rtl: true,
      labels: { font: { family: 'Vazir, sans-serif', size: 12 }, usePointStyle: true },
    },
    tooltip: {
      rtl: true,
      titleFont: { family: 'Vazir, sans-serif' },
      bodyFont: { family: 'Vazir, sans-serif' },
    },
  },
  scales: {
    x: {
      ticks: { font: { family: 'Vazir, sans-serif', size: 11 } },
      grid: { display: false },
    },
    y: {
      beginAtZero: true,
      ticks: { font: { family: 'Vazir, sans-serif', size: 11 } },
      grid: { color: 'rgba(0,0,0,0.06)' },
    },
  },
}

// Deep-ish merge so callers can override individual option branches.
const merge = (base, extra) => {
  const out = Array.isArray(base) ? [...base] : { ...base }
  for (const key of Object.keys(extra || {})) {
    const ev = extra[key]
    if (ev && typeof ev === 'object' && !Array.isArray(ev) && typeof out[key] === 'object') {
      out[key] = merge(out[key], ev)
    } else {
      out[key] = ev
    }
  }
  return out
}

const mergedOptions = computed(() => merge(DEFAULTS, props.options))
</script>

<style scoped>
.app-chart {
  position: relative;
  width: 100%;
}
</style>
