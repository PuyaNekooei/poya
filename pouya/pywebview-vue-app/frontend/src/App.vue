<script setup>
import { onMounted, onUnmounted } from 'vue'

// Handle F11 key to toggle fullscreen
const handleKeyDown = (event) => {
  if (event.key === 'F11') {
    event.preventDefault()
    if (window.pywebview && window.pywebview.api) {
      // PyWebView environment - can't toggle fullscreen easily
      console.log('F11 pressed - fullscreen toggle not available in PyWebView')
    } else {
      // Browser environment
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen()
      } else {
        document.exitFullscreen()
      }
    }
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <router-view />
</template>

<style>
/* Import Vazir font locally */
@import './assets/fonts/vazir.css';

/* Global styles */
body {
  direction: rtl;
  font-family: "Vazir", "Tahoma", "Arial", sans-serif;
  margin: 0;
  padding: 0;
}

* {
  box-sizing: border-box;
}
</style>
