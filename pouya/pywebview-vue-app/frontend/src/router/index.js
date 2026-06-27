import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import KitchenOrders from '../views/KitchenOrders.vue'
import Statistics from '../views/Statistics.vue'
import OrderStatus from '../views/OrderStatus.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, roles: ['admin', 'chef', 'cashier'] }
  },
  {
    path: '/kitchen',
    name: 'Kitchen',
    component: KitchenOrders,
    meta: { requiresAuth: true, roles: ['chef', 'admin'] }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/order-status',
    name: 'OrderStatus',
    component: OrderStatus,
    meta: { requiresAuth: true, roles: ['customer', 'chef', 'cashier', 'admin'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Home route per role. Admins always get the dashboard. Otherwise: chefs land on
// the kitchen board, pure customers on the order-status page, everyone else on
// the sales dashboard.
const homeForRoles = (roles) => {
  if (roles.includes('admin')) return '/dashboard'
  if (roles.includes('chef')) return '/kitchen'
  if (roles.includes('customer') && !roles.includes('cashier')) return '/order-status'
  return '/dashboard'
}

// Navigation guard for authentication + role-based access. A user can belong to
// several groups, so access is granted when ANY of their groups is allowed.
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  const roles = JSON.parse(localStorage.getItem('roles') || '[]')
  const isAdmin = roles.includes('admin') || localStorage.getItem('role') === 'admin'
  const canAccess = (allowed) => isAdmin || allowed.some((r) => roles.includes(r))

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next(homeForRoles(roles))
  } else if (to.meta.roles && isAuthenticated && !canAccess(to.meta.roles)) {
    // Authenticated but lacks the required group(s) for this route
    next(homeForRoles(roles))
  } else {
    next()
  }
})

export default router 