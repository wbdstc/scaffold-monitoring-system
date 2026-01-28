<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { sensorData } from '../composables/useWebSocket'

const currentTime = ref('00:00:00')
let timer: number | null = null

onMounted(() => {
  timer = window.setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString()
  }, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <header class="header">
    <div class="header-info">
      STATUS: <span :style="{ color: sensorData.statusColor }">{{ sensorData.status }}</span>
    </div>
    <div class="header-title">SHM 结构健康监测指挥中心</div>
    <div class="header-info">{{ currentTime }}</div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(90deg, rgba(0, 0, 0, 0) 0%, rgba(0, 242, 255, 0.1) 50%, rgba(0, 0, 0, 0) 100%);
  border-bottom: 1px solid rgba(0, 242, 255, 0.3);
  position: relative;
}

.header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 3px;
  background: var(--primary);
  box-shadow: 0 0 10px var(--primary);
}

.header-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 900;
  letter-spacing: 4px;
  color: #fff;
  text-shadow: 0 0 15px var(--primary);
  background: linear-gradient(to bottom, #fff, var(--primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-info {
  font-family: var(--font-display);
  color: var(--primary);
  font-size: 18px;
  width: 200px;
  text-align: center;
}
</style>
