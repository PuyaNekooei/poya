<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">🍽️</div>
        <h1>نرم افزار فروش پویا</h1>
        <p>لطفا برای ورود به سیستم، اطلاعات خود را وارد کنید</p>
      </div>
      
      <el-form 
        :model="loginForm" 
        :rules="rules" 
        ref="loginFormRef" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="نام کاربری"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="رمز عبور"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            ورود به سیستم
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>نسخه 1.0.0</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: 'لطفا نام کاربری را وارد کنید', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'لطفا رمز عبور را وارد کنید', trigger: 'blur' },
    { min: 4, message: 'رمز عبور باید حداقل 4 کاراکتر باشد', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    const response = await api.post('/auth/login/', {
      username: loginForm.username,
      password: loginForm.password
    })
    
    // Store authentication data
    localStorage.setItem('authToken', response.data.token)
    localStorage.setItem('isAuthenticated', 'true')
    localStorage.setItem('username', response.data.user.username)
    localStorage.setItem('userId', response.data.user.id)
    // Role info for UI gating. `role` is the primary role; `roles` is the full
    // list of groups the user belongs to (a user can be in several groups).
    localStorage.setItem('role', response.data.user.role || '')
    localStorage.setItem('roles', JSON.stringify(response.data.user.roles || []))
    localStorage.setItem('isAdmin', response.data.user.is_admin ? 'true' : 'false')

    ElMessage.success(response.data.message || 'ورود موفقیت‌آمیز بود')
    // Land each role on its home page: chef -> kitchen, customer -> order status,
    // everyone else -> sales dashboard.
    const primaryRole = response.data.user.role
    const home =
      primaryRole === 'chef'
        ? '/kitchen'
        : primaryRole === 'customer'
        ? '/order-status'
        : '/dashboard'
    router.push(home)
    
  } catch (error) {
    console.error('Login error:', error)
    
    let errorMessage = 'خطا در ورود به سیستم'
    
    if (error.response) {
      // Server responded with error status
      switch (error.response.status) {
        case 401:
          errorMessage = error.response.data?.error || 'نام کاربری یا رمز عبور اشتباه است'
          break
        case 400:
          errorMessage = error.response.data?.error || 'اطلاعات ورودی نامعتبر است'
          break
        case 500:
          errorMessage = 'خطای سرور - لطفا دوباره تلاش کنید'
          break
        default:
          errorMessage = error.response.data?.error || 'خطا در ورود - لطفا دوباره تلاش کنید'
      }
    } else if (error.request) {
      // Request was made but no response received
      errorMessage = 'خطای اتصال - لطفا اتصال اینترنت خود را بررسی کنید'
    } else {
      // Something else happened
      errorMessage = 'خطای غیرمنتظره - لطفا دوباره تلاش کنید'
    }
    
    ElMessage.error(errorMessage)
    
    // Clear any existing auth data on error
    localStorage.removeItem('authToken')
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
    localStorage.removeItem('role')
    localStorage.removeItem('roles')
    localStorage.removeItem('isAdmin')

  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.login-header {
  margin-bottom: 30px;
}

.logo {
  font-size: 4rem;
  margin-bottom: 20px;
}

.login-header h1 {
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.login-header p {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
}

.login-form {
  margin-bottom: 30px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.login-button {
  width: 100%;
  height: 50px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.4);
}

.login-footer {
  border-top: 1px solid #ecf0f1;
  padding-top: 20px;
}

.login-footer p {
  color: #95a5a6;
  font-size: 12px;
  margin: 0;
}

/* RTL specific styles */
.login-form :deep(.el-input__prefix) {
  right: 12px;
  left: auto;
}

.login-form :deep(.el-input__inner) {
  text-align: right;
  padding-right: 40px;
  padding-left: 12px;
}
</style> 