import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import fa from 'element-plus/dist/locale/fa.mjs'
import { createI18n } from 'vue-i18n'
import messages from './locales/messages'

const i18n = createI18n({
  locale: 'fa',
  fallbackLocale: 'fa',
  messages,
})

const app = createApp(App)
app.use(router)
app.use(ElementPlus, {
  locale: fa,
  rtl: true,
})
app.use(i18n)
app.mount('#app')


