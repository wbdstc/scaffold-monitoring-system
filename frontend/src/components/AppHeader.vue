<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { sensorData } from '../composables/useWebSocket'

const currentTime = ref('00:00:00')
let timer: number | null = null

const statusText = computed(() => {
  if (sensorData.status === 'MONITORING') {
    return 'ACTIVE MONITORING'
  }

  return sensorData.status
})

function updateTime() {
  currentTime.value = new Date().toLocaleTimeString('zh-CN', {
    hour12: false
  })
}

onMounted(() => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<template>
  <header class="header">
    <div class="header-side">
      <div class="header-caption">STATUS</div>
      <div class="header-side-value" :style="{ color: sensorData.statusColor }">
        {{ statusText }}
      </div>
    </div>

    <div class="header-center">
      <div class="header-overline">STRUCTURAL HEALTH MONITORING COMMAND CENTER</div>
      <div class="header-title">SHM 结构健康监测指挥中心</div>
      <div class="header-underline"></div>
    </div>

    <div class="header-side header-side--right">
      <div class="header-caption">SYSTEM TIME</div>
      <div class="header-clock">{{ currentTime }}</div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: relative;
  display: grid;
  grid-template-columns: 260px 1fr 260px;
  align-items: center;
  min-height: 0;
  padding: 8px 14px 10px;
  border-bottom: 1px solid rgba(86, 246, 255, 0.18);
  background:
    linear-gradient(90deg, rgba(0, 0, 0, 0), rgba(86, 246, 255, 0.06) 50%, rgba(0, 0, 0, 0)),
    rgba(3, 10, 23, 0.42);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.03),
    0 18px 32px rgba(0, 0, 0, 0.18);
}

.header::before,
.header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  width: 18%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(86, 246, 255, 0.7), transparent);
}

.header::before {
  left: 0;
}

.header::after {
  right: 0;
}

.header-side {
  display: flex;
  flex-direction: column;
  gap: 4px;
  justify-content: center;
}

.header-side--right {
  align-items: flex-end;
  text-align: right;
}

.header-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.header-caption {
  color: var(--text-dim);
  font-size: 11px;
  letter-spacing: 2px;
}

.header-side-value,
.header-clock {
  color: var(--primary);
  font-family: var(--font-display);
  font-size: 22px;
  letter-spacing: 1.8px;
  text-shadow: 0 0 14px rgba(86, 246, 255, 0.32);
}

.header-overline {
  color: rgba(182, 226, 255, 0.54);
  font-size: 10px;
  letter-spacing: 3.2px;
}

.header-title {
  color: var(--text-main);
  font-family: var(--font-display);
  font-size: clamp(28px, 2.1vw, 40px);
  font-weight: 900;
  letter-spacing: 3px;
  text-shadow:
    0 0 14px rgba(86, 246, 255, 0.44),
    0 0 28px rgba(45, 220, 255, 0.16);
  background: linear-gradient(180deg, #ffffff 5%, #8efcff 55%, #44cfff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-underline {
  width: 280px;
  max-width: 48%;
  height: 3px;
  margin-top: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  box-shadow: 0 0 14px rgba(86, 246, 255, 0.44);
}
</style>
