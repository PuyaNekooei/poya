<template>
  <div class="windows-app">
    <!-- Header -->
    <div class="app-header">
      <!-- Brand -->
      <div class="header-brand">
        <div class="brand-logo">
          <el-icon><Shop /></el-icon>
        </div>
        <h1>نرم افزار فروش پویا</h1>
      </div>

      <!-- Actions -->
      <div class="header-actions">
        <!-- Navigation -->
        <div class="header-nav" v-if="navItems.length">
          <el-button
            v-for="item in navItems"
            :key="item.path"
            :type="item.type"
            :icon="item.icon"
            size="small"
            round
            @click="router.push(item.path)"
          >
            {{ item.label }}
          </el-button>
        </div>

        <span class="header-divider" v-if="navItems.length"></span>

        <!-- Tools -->
        <el-button
          type="primary"
          :icon="Printer"
          @click="testPrinter"
          :loading="printingLoading"
          size="small"
          round
        >
          تست چاپگر
        </el-button>

        <span class="header-divider"></span>

        <!-- Current user -->
        <div class="user-pill">
          <el-icon class="user-pill-icon"><User /></el-icon>
          <span class="user-pill-name">{{ username }}</span>
          <el-tag
            v-if="role"
            :type="roleTagType"
            size="small"
            effect="dark"
            round
          >
            {{ roleLabel }}
          </el-tag>
        </div>

        <!-- Logout -->
        <el-button
          :icon="SwitchButton"
          circle
          class="logout-btn"
          title="خروج"
          @click="handleLogout"
        />
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-container">
      <!-- Food List Section -->
      <div class="food-section">
        <h2>لیست غذاها</h2>
        
        <!-- Search Input -->
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="جستجو در غذاها..."
            prefix-icon="Search"
            clearable
            class="search-input"
          />
        </div>
        
        <div class="food-categories">
          <div v-if="Object.keys(foodsByCategory).length === 0 && searchQuery.trim()" class="no-search-results">
            <div class="no-results-icon">🔍</div>
            <div class="no-results-text">هیچ غذایی با این نام پیدا نشد</div>
            <div class="no-results-subtext">سعی کنید نام دیگری جستجو کنید</div>
          </div>
          <div 
            v-for="(foodsInCategory, category) in foodsByCategory" 
            :key="category"
            class="category-section"
          >
            <h3 class="category-header">{{ category }}</h3>
            <div class="food-grid">
              <div 
                v-for="food in foodsInCategory" 
                :key="food.id" 
                class="food-item"
                @click="addToCurrentCustomer(food)"
              >
                <div class="food-name">{{ food.name }}</div>
                <div class="food-price">{{ formatPrice(food.price) }} ریال</div>
                <div class="food-tax-info" v-if="food.vatRate > 0">
                  <span class="tax-badge">مالیات {{ food.vatRate }}%</span>
                </div>
                <div class="food-stock">موجودی: {{ food.stock }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Customer Tabs Section -->
      <div class="customer-section">
        <div class="tabs-header">
          <h2>سفارشات مشتریان</h2>
          <el-button 
            type="primary" 
            @click="addNewCustomer"
            class="add-customer-btn"
          >
            <el-icon><Plus /></el-icon>
            مشتری جدید
          </el-button>
        </div>

        <!-- Customer Tabs -->
        <el-tabs 
          v-model="activeTab" 
          type="card" 
          closable 
          @tab-remove="removeCustomer"
          class="customer-tabs"
        >
          <el-tab-pane 
            v-for="customer in customers" 
            :key="customer.id"
            :label="customer.isPreviousOrder ? `${customer.name || 'بدون نام'} (${formatOrderNumber(customer.originalOrderNumber)})${customer.isModified ? ' *' : ''}` : (customer.name || `مشتری ${customer.id}`)"
            :name="customer.id"
          >
            <!-- Customer Order Form -->
            <div class="customer-order">
              <div class="customer-info">
                <el-input
                  v-model="customer.name"
                  placeholder="نام مشتری"
                  class="customer-name-input"
                />
                <el-input
                  v-model="customer.phone"
                  placeholder="شماره تماس"
                  class="customer-phone-input"
                />
                <el-select
                  v-model="customer.tableId"
                  placeholder="انتخاب میز"
                  clearable
                  class="customer-table-select"
                >
                  <el-option
                    v-for="table in tables"
                    :key="table.id"
                    :label="table.name ? `${table.name} (${table.number})` : `میز ${table.number}`"
                    :value="table.id"
                  />
                </el-select>
              </div>

              <!-- Customer's Food List -->
              <div class="order-items">
                <h3>لیست سفارشات</h3>
                <div v-if="customer.items.length === 0" class="empty-order">
                  هیچ غذایی انتخاب نشده است
                </div>
                <div v-else class="order-list">
                  <div 
                    v-for="(item, index) in customer.items" 
                    :key="index"
                    class="order-item"
                  >
                    <div class="item-info">
                      <span class="item-name">{{ item.name }}</span>
                      <div class="item-price-details">
                        <span class="item-price">{{ formatPrice(item.price) }} ریال</span>
                        <span class="item-tax-badge" v-if="item.vatRate > 0">
                          (مالیات {{ item.vatRate }}%)
                        </span>
                      </div>
                    </div>
                    <div class="item-controls">
                      <el-input-number 
                        v-model="item.quantity" 
                        :min="1" 
                        :max="99"
                        size="small"
                        @change="updateCustomerTotal(customer)"
                      />
                      <el-button 
                        type="danger" 
                        size="small"
                        @click="removeItem(customer, index)"
                      >
                        حذف
                      </el-button>
                    </div>
                  </div>
                </div>

                <!-- Total and Actions -->
                <div class="order-summary">
                  <div class="tax-breakdown">
                    <div class="summary-row">
                      <span>جمع کالاها:</span>
                      <span>{{ formatPrice(calculateSubtotal(customer)) }} ریال</span>
                    </div>
                    <div class="summary-row tax-row">
                      <span>مالیات:</span>
                      <span>{{ formatPrice(calculateTax(customer)) }} ریال</span>
                    </div>
                    <div class="summary-row total-row">
                      <span>جمع کل:</span>
                      <span><strong>{{ formatPrice(customer.total) }} ریال</strong></span>
                    </div>
                  </div>
                  <div class="order-actions">
                    <el-button 
                      v-if="!customer.isPreviousOrder"
                      type="success" 
                      @click="acceptOrder(customer)"
                      :disabled="customer.items.length === 0"
                    >
                      تایید سفارش
                    </el-button>
                    <el-button
                      v-if="customer.isPreviousOrder"
                      type="success"
                      @click="updatePreviousOrder(customer)"
                      :disabled="customer.items.length === 0"
                    >
                      ذخیره تغییرات
                    </el-button>
                    <el-button
                      type="primary"
                      @click="printCustomerInvoice(customer)"
                      :disabled="customer.items.length === 0 || (!customer.isPreviousOrder && !customer.isConfirmed)"
                      :loading="printingLoading"
                    >
                      چاپ فاکتور
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>


      <!-- Previous Customers Sidebar -->
      <div class="previous-customers-sidebar">
        <h3>سفارشات امروز</h3>
        
        <!-- Tab Filter -->
        <div class="previous-orders-tabs">
          <el-tabs v-model="previousOrdersTab" class="compact-tabs">
            <el-tab-pane name="all">
              <template #label>
                <span>همه سفارشات</span>
                <el-badge :value="previousCustomers.length" class="tab-badge" />
              </template>
            </el-tab-pane>
            <el-tab-pane label="وضعیت سفارش‌ها" name="status" />
          </el-tabs>
        </div>

        <!-- All orders tab -->
        <template v-if="previousOrdersTab === 'all'">
          <div class="orders-refresh-controls">
            <el-button
              type="success"
              size="small"
              @click="loadPreviousOrders"
              :loading="loading"
            >
              بروزرسانی
            </el-button>
          </div>
          <div class="previous-customers-list">
            <div v-if="filteredPreviousCustomers.length === 0" class="no-previous">
              سفارش امروز وجود ندارد
            </div>
            <div
              v-for="customer in filteredPreviousCustomers"
              :key="customer.orderNumber"
              class="previous-customer-item"
            >
              <div class="previous-customer-content" @click="openPreviousCustomer(customer)">
                <div class="previous-customer-header">
                  <span class="order-number">{{ formatOrderNumber(customer.orderNumber) }}</span>
                  <span class="order-time">{{ formatTime(customer.completedAt) }}</span>
                </div>
                <div class="previous-customer-name">
                  {{ customer.name || 'بدون نام' }}
                  <span v-if="customer.phone" class="customer-phone">{{ customer.phone }}</span>
                </div>
                <div class="previous-customer-total">
                  {{ formatPrice(customer.total) }} ریال
                </div>
                <div class="previous-customer-items">
                  {{ customer.items.length }} آیتم
                </div>
              </div>
              <div class="previous-customer-actions">
                <el-button
                  type="primary"
                  size="small"
                  @click="printCustomerInvoice(customer)"
                  :loading="printingLoading"
                >
                  چاپ
                </el-button>
              </div>
            </div>
          </div>
        </template>

        <!-- Order-status tab -->
        <div v-else-if="previousOrdersTab === 'status'" class="status-tab-body">
          <OrderStatusBoard title="" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import {
  Plus,
  Printer,
  User,
  SwitchButton,
  Shop,
  KnifeFork,
  TrendCharts,
  Tickets,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '../api'
import PersianDate from 'persian-date'
import printerService from '../services/printerService'
import OrderStatusBoard from '../components/OrderStatusBoard.vue'

const router = useRouter()
const username = ref(localStorage.getItem('username') || 'کاربر')
// Current user's role for UI gating (admin / chef / cashier)
const role = ref(localStorage.getItem('role') || '')
// All groups the user belongs to. A user can be in several groups at once.
const roles = ref(JSON.parse(localStorage.getItem('roles') || '[]'))
const isAdmin = computed(() => role.value === 'admin' || roles.value.includes('admin'))
const roleLabels = { admin: 'مدیر', chef: 'آشپز', cashier: 'صندوقدار' }
const roleTagTypes = { admin: 'success', chef: 'warning', cashier: 'primary' }
const roleLabel = computed(() => roleLabels[role.value] || '')
const roleTagType = computed(() => roleTagTypes[role.value] || 'info')

// Header navigation targets. Each entry is shown only when the user belongs to
// one of its `roles` (admins implicitly see everything). Keep the `roles` here
// in sync with the route guards in router/index.js.
const NAV_TARGETS = [
  { path: '/kitchen', label: 'آشپزخانه', type: 'warning', icon: KnifeFork, roles: ['chef'] },
  { path: '/statistics', label: 'آمار و پیش‌بینی', type: 'info', icon: TrendCharts, roles: ['admin'] },
  { path: '/order-status', label: 'وضعیت سفارش‌ها', type: 'success', icon: Tickets, roles: ['customer'] },
]
const navItems = computed(() =>
  NAV_TARGETS.filter(
    (item) => isAdmin.value || item.roles.some((r) => roles.value.includes(r))
  )
)

// Food data loaded from API
const foods = ref([])
const loading = ref(false)
const printingLoading = ref(false)

// Dine-in tables loaded from API
const tables = ref([])

const loadTables = async () => {
  try {
    const response = await api.tables.active()
    tables.value = response.data.results ? response.data.results : response.data
  } catch (error) {
    console.error('Error loading tables:', error)
  }
}

// Search functionality
const searchQuery = ref('')

// Load foods from API
const loadFoods = async () => {
  try {
    loading.value = true
    const response = await api.menu.withInventory()
    foods.value = response.data.map(item => ({
      id: item.id,
      name: item.name,
      price: item.price,
      priceWithoutTax: item.price_without_tax ,
      vatRate: item.vat_rate || 0,
      stock: item.current_inventory || 0,
      category: item.category_name || 'بدون دسته‌بندی'
    }))
  } catch (error) {
    console.error('Error loading foods:', error)
    ElMessage.error('خطا در بارگذاری لیست غذاها')
  } finally {
    loading.value = false
  }
}

// Filter foods based on search query
const filteredFoods = computed(() => {
  if (!searchQuery.value.trim()) {
    return foods.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return foods.value.filter(food => 
    food.name.toLowerCase().includes(query) ||
    food.category.toLowerCase().includes(query)
  )
})

// Get unique categories from filtered foods
const categories = computed(() => {
  return [...new Set(filteredFoods.value.map(food => food.category))]
})

// Group filtered foods by category
const foodsByCategory = computed(() => {
  const grouped = {}
  filteredFoods.value.forEach(food => {
    if (!grouped[food.category]) {
      grouped[food.category] = []
    }
    grouped[food.category].push(food)
  })
  return grouped
})

// Previous customers list (all of today's orders)
const filteredPreviousCustomers = computed(() => previousCustomers.value)

// Customer management
const customers = ref([])
const activeTab = ref('')
let customerCounter = 1

// Previous customers (completed orders)
const previousCustomers = ref([])

// Tab filter for previous orders
const previousOrdersTab = ref('all')

// Orders polling timer
const ordersPollingInterval = ref(null)

// Start polling for orders updates
const startOrdersPolling = () => {
  // Load immediately
  loadPreviousOrders()
  
  // Then poll every 30 seconds
  ordersPollingInterval.value = setInterval(() => {
    loadPreviousOrders()
  }, 30000) // 30 seconds
}

// Stop polling for orders
const stopOrdersPolling = () => {
  if (ordersPollingInterval.value) {
    clearInterval(ordersPollingInterval.value)
    ordersPollingInterval.value = null
  }
}

// Load previous orders from API (today's orders only)
const loadPreviousOrders = async () => {
  try {
    const response = await api.orders.today()
    const newOrders = response.data.results ? response.data.results : response.data

    // Transform the data to match our frontend structure
    previousCustomers.value = newOrders.map(order => {
      // Transform order items to match our frontend structure
      const transformedItems = order.items ? order.items.map(item => ({
        id: item.menu_item,
        name: item.menu_item_details ? item.menu_item_details.name : (item.product_info ? item.product_info.product_name : 'Unknown Item'),
        price: item.unit_price,
        priceWithoutTax: item.menu_item_details ? item.menu_item_details.price_without_tax : item.unit_price,  // ✅ Add tax info
        vatRate: item.menu_item_details ? item.menu_item_details.vat_rate : 0,  // ✅ Add tax info
        quantity: item.quantity,
        has_menu_item: !!item.menu_item,
        product_info: item.product_info || null
      })) : []
      
      return {
        orderNumber: order.order_number || `ORD-${order.id}`,
        backendId: order.id,
        name: order.customer_name || 'بدون نام',
        phone: order.customer_phone || '',
        tableId: order.table || null,
        total: order.total_amount,
        completedAt: order.created_at,
        items: transformedItems,
        status: order.status,
      }
    })
  } catch (error) {
    console.error('Error loading today\'s orders:', error)
    ElMessage.error('خطا در بارگذاری سفارشات امروز')
  }
}


const addNewCustomer = () => {
  const newCustomer = {
    id: `customer-${customerCounter}`,
    name: '',
    phone: '',
    tableId: null,
    items: [],
    total: 0,
    isConfirmed: false
  }
  customers.value.push(newCustomer)
  activeTab.value = newCustomer.id
  customerCounter++
}

const removeCustomer = (targetName) => {
  const tabs = customers.value
  let activeName = activeTab.value
  if (activeName === targetName) {
    tabs.forEach((tab, index) => {
      if (tab.id === targetName) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) {
          activeName = nextTab.id
        }
      }
    })
  }
  activeTab.value = activeName
  customers.value = tabs.filter(tab => tab.id !== targetName)
}

const addToCurrentCustomer = (food) => {
  if (!activeTab.value) {
    ElMessage.warning('لطفا ابتدا یک مشتری اضافه کنید')
    return
  }

  const customer = customers.value.find(c => c.id === activeTab.value)
  if (!customer) return

  // Check if food already exists in customer's order
  const existingItem = customer.items.find(item => item.id === food.id)
  if (existingItem) {
    existingItem.quantity++
  } else {
    customer.items.push({
      id: food.id,
      name: food.name,
      price: food.price,
      priceWithoutTax: food.priceWithoutTax,  // ✅ Add tax info
      vatRate: food.vatRate,                   // ✅ Add tax info
      quantity: 1
    })
  }

  updateCustomerTotal(customer)
  
  // Mark previous orders as modified when items are added
  if (customer.isPreviousOrder) {
    customer.isModified = true
  }
  
  ElMessage.success(`${food.name} به سفارش اضافه شد`)
}

const removeItem = (customer, index) => {
  customer.items.splice(index, 1)
  updateCustomerTotal(customer)
  
  // Mark previous orders as modified when items are removed
  if (customer.isPreviousOrder) {
    customer.isModified = true
  }
}

const updateCustomerTotal = (customer) => {
  customer.total = customer.items.reduce((sum, item) => {
    return sum + (item.price * item.quantity)
  }, 0)
  
  // Mark previous orders as modified when changes are made
  if (customer.isPreviousOrder) {
    customer.isModified = true
  }
}


const acceptOrder = async (customer) => {
  if (customer.items.length === 0) {
    ElMessage.warning('لطفا حداقل یک غذا انتخاب کنید')
    return
  }
  
  try {
    // Mark order as confirmed
    customer.isConfirmed = true
    
    // Prepare order data for API
    const orderData = {
      customer_name: customer.name || 'بدون نام',
      customer_phone: customer.phone || '',
      total_amount: customer.total,
      status: 'pending',
      table: customer.tableId || null,
      items: customer.items.map(item => ({
        menu_item_id: item.id,
        quantity: item.quantity,
        notes: ''
      }))
    }

    // Save order to backend
    const response = await api.orders.create(orderData)

    // Attach backend identifiers to the current customer for consistent printing
    if (response && response.data) {
      customer.backendId = response.data.id
      customer.orderNumber = response.data.order_number || customer.orderNumber
    }

    // Reload previous orders to get the new order from backend
    await loadPreviousOrders()
    
    ElMessage.success(`سفارش با موفقیت ثبت شد`)
    console.log('Order accepted:', response.data)
    
  } catch (error) {
    console.error('Error saving order:', error)
    ElMessage.error('خطا در ثبت سفارش')
  }
}

const openPreviousCustomer = (customer) => {
  // Check if this previous order is already open
  const existingTab = customers.value.find(c => 
    c.isPreviousOrder && c.originalOrderNumber === customer.orderNumber
  )
  
  if (existingTab) {
    // If already open, just switch to that tab
    activeTab.value = existingTab.id
    ElMessage.info(`سفارش ${customer.orderNumber} در حال نمایش است`)
    return
  }
  
  // Create a new customer tab with the previous order data
  const newCustomer = {
    id: `customer-${customerCounter}`,
    name: customer.name || '',
    phone: customer.phone || '',
    items: [...customer.items], // Copy the items
    total: customer.total,
    isPreviousOrder: true, // Flag to indicate this is from previous order
    originalOrderNumber: customer.orderNumber,
    backendId: customer.backendId, // Ensure backendId is passed
    isModified: false, // Track if the order has been modified
    isConfirmed: true, // Previous orders are already confirmed
    // Carry over orderNumber for printing consistency
    orderNumber: customer.orderNumber
  }
  customers.value.push(newCustomer)
  activeTab.value = newCustomer.id
  customerCounter++
  
  ElMessage.info(`سفارش ${customer.orderNumber} باز شد - می‌توانید تغییرات اعمال کنید`)
}

const formatPrice = (price) => {
  return Math.round(price).toLocaleString('fa-IR')
}

// Calculate subtotal (price without tax)
const calculateSubtotal = (customer) => {
  if (!customer.items || customer.items.length === 0) return 0
  return customer.items.reduce((sum, item) => {
    // item.priceWithoutTax = قیمت بدون مالیات
    // If missing, calculate from price and vat_rate
    let priceWithoutTax = parseFloat(item.priceWithoutTax)
    if (!priceWithoutTax && item.price && item.vatRate) {
      // Calculate: price_without_tax = price_with_tax / (1 + vat_rate/100)
      priceWithoutTax = parseFloat(item.price) / (1 + parseFloat(item.vatRate) / 100)
    } else if (!priceWithoutTax) {
      // If no tax info, assume price is without tax
      priceWithoutTax = parseFloat(item.price)
    }
    return sum + (priceWithoutTax * item.quantity)
  }, 0)
}

// Calculate total tax
const calculateTax = (customer) => {
  if (!customer.items || customer.items.length === 0) return 0
  return customer.items.reduce((sum, item) => {
    // item.price = قیمت با مالیات (price WITH tax)
    // item.priceWithoutTax = قیمت بدون مالیات (price WITHOUT tax)
    const priceWithTax = parseFloat(item.price)
    
    let priceWithoutTax = parseFloat(item.priceWithoutTax)
    if (!priceWithoutTax && item.vatRate) {
      // Calculate: price_without_tax = price_with_tax / (1 + vat_rate/100)
      priceWithoutTax = priceWithTax / (1 + parseFloat(item.vatRate) / 100)
    } else if (!priceWithoutTax) {
      // No tax
      priceWithoutTax = priceWithTax
    }
    
    const taxAmount = (priceWithTax - priceWithoutTax) * item.quantity
    return sum + taxAmount
  }, 0)
}

const formatTime = (date) => {
  const persianDate = new PersianDate(new Date(date))
  return persianDate.format('HH:mm - YYYY/MM/DD')
}

const formatOrderNumber = (orderNumber) => {
  // Convert English numbers to Persian numbers
  const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
  
  // Check if order number has date format (ORD-YYYYMMDD-XXX)
  if (orderNumber.startsWith('ORD-') && orderNumber.includes('-')) {
    const parts = orderNumber.split('-')
    if (parts.length === 3) {
      const dateStr = parts[1] // YYYYMMDD
      const sequence = parts[2] // XXX
      
      // Convert Gregorian date to Persian date
      if (dateStr.length === 8) {
        const year = parseInt(dateStr.substring(0, 4))
        const month = parseInt(dateStr.substring(4, 6))
        const day = parseInt(dateStr.substring(6, 8))
        
        const gregorianDate = new Date(year, month - 1, day)
        const persianDate = new PersianDate(gregorianDate)
        const persianDateStr = persianDate.format('YYYYMMDD')
        
        // Convert all numbers to Persian (without ORD prefix)
        const persianOrderNumber = `${persianDateStr}-${sequence}`
        return persianOrderNumber.replace(/\d/g, (d) => persianNumbers[d])
      }
    }
  }
  
  // Fallback: just convert numbers to Persian
  return orderNumber.replace(/\d/g, (d) => persianNumbers[d])
}

const updatePreviousOrder = async (customer) => {
  if (customer.items.length === 0) {
    ElMessage.warning('لطفا حداقل یک غذا انتخاب کنید')
    return
  }
  

  
  if (!customer.backendId) {
    // If no backendId, create a new order instead of updating
    ElMessage.info('سفارش جدید ایجاد می‌شود')
    
    try {
      const orderData = {
        customer_name: customer.name || 'بدون نام',
        customer_phone: customer.phone || '',
        status: 'pending',
        table: customer.tableId || null,
        items: customer.items.map(item => ({
          menu_item_id: item.id,
          quantity: item.quantity,
          notes: ''
        }))
      }

      const response = await api.orders.create(orderData)
      
      // Reload previous orders to get the new order from backend
      await loadPreviousOrders()
      
      removeCustomer(customer.id)
      
      ElMessage.success('سفارش جدید با موفقیت ایجاد شد')
      return
      
    } catch (error) {
      console.error('Error creating new order:', error)
      ElMessage.error('خطا در ایجاد سفارش جدید')
      return
    }
  }
  
  try {
    // Prepare order data for API update
    const orderData = {
      customer_name: customer.name || 'بدون نام',
      customer_phone: customer.phone || '',
      status: 'pending',
      table: customer.tableId || null,
      items: customer.items.map(item => ({
        menu_item_id: item.id,
        quantity: item.quantity,
        notes: ''
      }))
    }



    // Update existing order in backend
    const response = await api.orders.update(customer.backendId, orderData)
    
    // Reload previous orders to get updated data from backend
    await loadPreviousOrders()
    
    ElMessage.success(`سفارش با موفقیت بروزرسانی شد`)
    console.log('Order updated:', response.data)
    
  } catch (error) {
    console.error('Error updating order:', error)
    ElMessage.error('خطا در بروزرسانی سفارش')
  }
}

// Printer functions
const printCustomerInvoice = async (customer) => {
  if (!customer.items || customer.items.length === 0) {
    ElMessage.warning('هیچ آیتمی برای چاپ وجود ندارد')
    return
  }

  try {
    printingLoading.value = true
    
    // Prefer backend-provided order number; fall back to originalOrderNumber
    const orderNumber = customer.orderNumber || customer.originalOrderNumber || `ORD-${Date.now()}`
    
    const receiptData = {
      customer: {
        name: customer.name || 'مشتری',
        phone: customer.phone || '',
        orderNumber: orderNumber,
        items: customer.items.map(item => ({
          name: item.name,
          quantity: item.quantity,
          price: parseFloat(item.price),
          priceWithoutTax: parseFloat(item.priceWithoutTax || item.price),
          vatRate: item.vatRate || 0
        })),
        total: parseFloat(customer.total)
      }
    }

    await printerService.printReceipt(receiptData)
    ElMessage.success('فاکتور با موفقیت چاپ شد')
    
    // Close tab after 2 seconds for all orders (both new and previous)
    setTimeout(() => {
      removeCustomer(customer.id)
    }, 2000)
    
  } catch (error) {
    console.error('Print error:', error)
    ElMessage.error('خطا در چاپ فاکتور')
  } finally {
    printingLoading.value = false
  }
}

const testPrinter = async () => {
  try {
    printingLoading.value = true
    await printerService.testPrinter()
    ElMessage.success('تست چاپگر موفقیت‌آمیز بود')
  } catch (error) {
    console.error('Printer test error:', error)
    ElMessage.error('خطا در تست چاپگر')
  } finally {
    printingLoading.value = false
  }
}

const handleLogout = async () => {
  try {
    await api.auth.logout()
    localStorage.removeItem('authToken')
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
    localStorage.removeItem('role')
    localStorage.removeItem('roles')
    localStorage.removeItem('isAdmin')
    ElMessage.success('خروج موفقیت‌آمیز بود')
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    // Even if logout fails, clear local storage
    localStorage.removeItem('authToken')
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
    localStorage.removeItem('role')
    localStorage.removeItem('roles')
    localStorage.removeItem('isAdmin')
    ElMessage.success('خروج موفقیت‌آمیز بود')
    router.push('/login')
  }
}

// Load data on component mount
onMounted(() => {
  loadFoods()
  loadTables()
  startOrdersPolling()
})

// Cleanup on component unmount
onUnmounted(() => {
  stopOrdersPolling()
})
</script>

<style>
body {
  direction: rtl;
  font-family: "Tahoma", "Arial", sans-serif;
  margin: 0;
  padding: 0;
  background: #f5f7fa;
}

.windows-app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
  color: white;
  padding: 12px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.18);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Brand: logo badge + title */
.header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #409eff 0%, #2f7bd6 100%);
  color: white;
  font-size: 22px;
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.35);
}

.app-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

/* Actions: nav + tools + user, separated into groups */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Element adds left-margin between adjacent buttons; we use flex `gap`
   instead, so neutralise it to keep spacing even. */
.header-actions .el-button + .el-button {
  margin-left: 0;
}

/* Unified "frosted glass" look for the header buttons so the icons +
   labels carry the meaning instead of a noisy rainbow of fills. */
.header-actions .el-button:not(.is-circle) {
  height: 34px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 500;
}

/* Keep the circular logout button square (and matched in height) */
.header-actions .el-button.is-circle {
  height: 34px;
  width: 34px;
}

.header-nav .el-button {
  --el-button-bg-color: rgba(255, 255, 255, 0.08);
  --el-button-border-color: rgba(255, 255, 255, 0.16);
  --el-button-text-color: #eef2f6;
  --el-button-hover-bg-color: rgba(255, 255, 255, 0.2);
  --el-button-hover-border-color: rgba(255, 255, 255, 0.32);
  --el-button-hover-text-color: #ffffff;
  --el-button-active-bg-color: rgba(255, 255, 255, 0.26);
  transition: transform 0.15s ease, background-color 0.2s ease;
}

.header-nav .el-button:hover {
  transform: translateY(-1px);
}

.header-nav .el-button .el-icon {
  font-size: 15px;
}

/* Printer stays the single blue accent action */
.header-actions .el-button--primary {
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
}

/* Thin vertical separator between action groups */
.header-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.15);
}

/* Current-user "pill" */
.user-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-pill-icon {
  font-size: 16px;
  color: #cdd6e0;
}

.user-pill-name {
  font-size: 14px;
  font-weight: 500;
  color: #f5f7fa;
}

/* Logout: subtle by default, red on hover */
.logout-btn {
  color: #cdd6e0;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: all 0.2s ease;
}

.logout-btn:hover,
.logout-btn:focus {
  color: #fff;
  background: #f56c6c;
  border-color: #f56c6c;
}

.main-container {
  flex: 1;
  display: flex;
  gap: 25px;
  padding: 25px 25px 0 25px;
  overflow: hidden;
  min-height: 0;
  max-height: calc(100vh - 120px);
}


.previous-customers-sidebar {
  flex: 0 0 350px;
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: 1px solid #e1e8ed;
  overflow-y: auto;
  min-width: 350px;
  max-width: 350px;
}

.previous-customers-sidebar h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.previous-orders-tabs {
  margin-bottom: 15px;
}

.compact-tabs .el-tabs__header {
  margin: 0;
}

.compact-tabs .el-tabs__nav-wrap {
  padding: 0;
}

.compact-tabs .el-tabs__item {
  padding: 8px 12px;
  font-size: 12px;
  height: auto;
  line-height: 1.2;
}

.compact-tabs .el-tabs__item.is-active {
  color: #409eff;
  font-weight: 600;
}

.tab-badge {
  margin-right: 5px;
}

.tab-badge .el-badge__content {
  font-size: 10px;
  height: 16px;
  line-height: 16px;
  padding: 0 4px;
  min-width: 16px;
}

.orders-refresh-controls {
  margin-bottom: 20px;
  text-align: center;
}

.no-previous {
  text-align: center;
  color: #6c757d;
  padding: 50px 25px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 2px dashed #adb5bd;
  font-style: italic;
}

.previous-customers-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.previous-customer-item {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 0;
  transition: all 0.3s ease;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  display: flex;
  overflow: hidden;
}

.previous-customer-item:hover {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #2196f3;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.15);
}

.previous-customer-content {
  flex: 1;
  padding: 10px;
  cursor: pointer;
}

.previous-customer-actions {
  display: flex;
  align-items: center;
  padding: 10px 8px;
  background: rgba(0, 0, 0, 0.02);
  border-left: 1px solid #e9ecef;
}

.previous-customer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.order-number {
  font-weight: bold;
  color: #1976d2;
  font-size: 10px;
}

.order-time {
  color: #6c757d;
  font-size: 9px;
}

.previous-customer-name {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 2px;
  font-size: 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.customer-phone {
  font-weight: normal;
  color: #6c757d;
  font-size: 10px;
  direction: ltr;
  text-align: right;
}

.previous-customer-total {
  color: #2e7d32;
  font-weight: bold;
  margin-bottom: 2px;
  font-size: 11px;
}

.previous-customer-items {
  color: #6c757d;
  font-size: 9px;
}

.status-tab-body {
  margin-top: 8px;
}

.food-section {
  flex: 0 0 35%;
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: 1px solid #e1e8ed;
  overflow-y: auto;
  min-width: 300px;
  max-width: 400px;
}

.food-section h2 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.search-container {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
}

.search-input .el-input__inner {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  padding: 12px 15px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input .el-input__inner:focus {
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.no-search-results {
  text-align: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 2px dashed #adb5bd;
  margin: 20px 0;
}

.no-results-icon {
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.6;
}

.no-results-text {
  font-size: 16px;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 8px;
}

.no-results-subtext {
  font-size: 14px;
  color: #adb5bd;
  font-style: italic;
}

.food-categories {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.category-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-header {
  margin: 0;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 0;
  border-bottom: 1px solid #ecf0f1;
  text-align: right;
  position: relative;
}

.category-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  right: 0;
  width: 30px;
  height: 1px;
  background: #3498db;
  border-radius: 1px;
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
}

.food-item {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.food-item:hover {
  border-color: #2196f3;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(33, 150, 243, 0.2);
}

.food-name {
  font-weight: 600;
  margin-bottom: 4px;
  color: #2c3e50;
  font-size: 13px;
}

.food-price {
  color: #2e7d32;
  font-weight: bold;
  margin-bottom: 2px;
  font-size: 14px;
}

.food-tax-info {
  margin: 4px 0;
}

.tax-badge {
  display: inline-block;
  padding: 2px 8px;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.food-stock {
  color: #6c757d;
  font-size: 10px;
  font-weight: 500;
}

.customer-section {
  flex: 1 1 auto;
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: 1px solid #e1e8ed;
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-height: 100vh;
  min-width: 400px;
}

.tabs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.tabs-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.add-customer-btn {
  background: #27ae60;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.2);
  transition: all 0.3s ease;
}

.add-customer-btn:hover {
  background: #2ecc71;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.customer-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-height: calc(100vh - 200px);
}

.customer-tabs .el-tabs__content {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  max-height: calc(100vh - 250px);
}

.customer-tabs .el-tab-pane {
  height: 100%;
  overflow-y: auto;
  min-height: 0;
}

.customer-order {
  padding: 20px 0;
  height: 100%;
  overflow-y: auto;
  min-height: 0;
  max-height: calc(100vh - 300px);
}

.customer-info {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.customer-name-input,
.customer-phone-input {
  flex: 1;
}

.order-items h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 14px;
}

.empty-order {
  text-align: center;
  color: #6c757d;
  padding: 40px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
}

.order-list {
  margin-bottom: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 6px;
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-price-details {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.item-tax-badge {
  font-size: 11px;
  color: #1976d2;
  background-color: #e3f2fd;
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: 500;
  gap: 2px;
}

.item-name {
  font-weight: bold;
  color: #2c3e50;
  font-size: 13px;
}

.item-price {
  color: #28a745;
  font-size: 11px;
}

.item-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.order-summary {
  border-top: 2px solid #e9ecef;
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-price {
  font-size: 16px;
  color: #2c3e50;
}

.tax-breakdown {
  flex: 1;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
  color: #495057;
}

.tax-row {
  color: #1976d2;
  font-weight: 500;
}

.total-row {
  border-top: 2px solid #dee2e6;
  margin-top: 6px;
  padding-top: 10px;
  font-size: 16px;
  color: #2e7d32;
  font-weight: bold;
}

.order-actions {
  display: flex;
  gap: 10px;
}

/* Element Plus RTL overrides */
.el-tabs__header {
  margin-bottom: 0;
}

.el-tabs__nav-wrap {
  padding-right: 0;
}

.el-tabs__item {
  text-align: right;
}
</style> 