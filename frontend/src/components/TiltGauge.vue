<script setup lang="ts">
import { computed } from 'vue'
import { sensorData } from '../composables/useWebSocket'

// 计算气泡位置 (角度 -> X偏移)
const bubbleOffset = computed(() => {
  // 限制在 -30° ~ +30° 范围内映射到 -60 ~ +60 像素
  const clampedAngle = Math.max(-30, Math.min(30, sensorData.tiltAngle))
  return (clampedAngle / 30) * 60
})

const isAlert = computed(() => Math.abs(sensorData.tiltAngle) > 10)
const isCritical = computed(() => Math.abs(sensorData.tiltAngle) > 20)
</script>

<template>
  <div :class="['tilt-gauge', { alert: isAlert, critical: isCritical }]">
    <!-- 标题 -->
    <div class="tilt-header">
      <span class="tilt-label">TILT LEVEL / 水平仪</span>
      <span :class="['tilt-status', { alert: isAlert }]">
        {{ isAlert ? '⚠️ TILTING' : '✓ LEVEL' }}
      </span>
    </div>

    <!-- 水平仪容器 -->
    <div class="level-container">
      <svg class="level-svg" viewBox="0 0 200 60" preserveAspectRatio="xMidYMid meet">
        <!-- 背景管道 -->
        <defs>
          <linearGradient id="tubeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color: rgba(0,242,255,0.1)" />
            <stop offset="50%" style="stop-color: rgba(0,242,255,0.05)" />
            <stop offset="100%" style="stop-color: rgba(0,242,255,0.1)" />
          </linearGradient>
          <radialGradient id="bubbleGrad" cx="30%" cy="30%">
            <stop offset="0%" :style="`stop-color: ${isAlert ? '#ff6b6b' : '#7affff'}`" />
            <stop offset="100%" :style="`stop-color: ${isAlert ? '#ff0055' : '#00f2ff'}`" />
          </radialGradient>
        </defs>

        <!-- 管道外框 -->
        <rect x="10" y="15" width="180" height="30" rx="15" 
              fill="url(#tubeGrad)" 
              :stroke="isAlert ? 'var(--danger)' : 'var(--primary)'" 
              stroke-width="1.5" />
        
        <!-- 刻度线 -->
        <line x1="100" y1="18" x2="100" y2="42" stroke="rgba(255,255,255,0.3)" stroke-width="1" stroke-dasharray="2,2" />
        <line x1="60" y1="20" x2="60" y2="40" stroke="rgba(255,255,255,0.15)" stroke-width="1" />
        <line x1="140" y1="20" x2="140" y2="40" stroke="rgba(255,255,255,0.15)" stroke-width="1" />

        <!-- 刻度数字 -->
        <text x="60" y="55" class="scale-text">-20°</text>
        <text x="100" y="55" class="scale-text">0°</text>
        <text x="140" y="55" class="scale-text">+20°</text>

        <!-- 气泡 -->
        <circle 
          :cx="100 + bubbleOffset" 
          cy="30" 
          r="10"
          fill="url(#bubbleGrad)"
          :class="['bubble', { alert: isAlert }]"
        />
      </svg>
    </div>

    <!-- 角度数值 -->
    <div class="tilt-value-container">
      <span class="tilt-value" :class="{ alert: isAlert }">
        {{ sensorData.tiltAngle >= 0 ? '+' : '' }}{{ sensorData.tiltAngle.toFixed(1) }}
      </span>
      <span class="tilt-unit">°</span>
    </div>
  </div>
</template>

<style scoped>
.tilt-gauge {
  /* Removed heavy borders/backgrounds for embedded mode */
  padding: 0 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  transition: all 0.3s ease;
  width: 100%;
}

.tilt-gauge.alert {
  /* Only subtle indication or rely on internal alerts */
}

/* Reduced animation intensity for critical */
.tilt-gauge.critical {
  animation: none; 
}

/* ... existing keyframes ... */

@keyframes alertPulse {
  from { box-shadow: 0 0 10px rgba(255, 0, 85, 0.3); }
  to { box-shadow: 0 0 25px rgba(255, 0, 85, 0.6); }
}

.tilt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tilt-label {
  font-size: 11px;
  color: var(--text-dim);
  letter-spacing: 1px;
}

.tilt-status {
  font-size: 10px;
  color: var(--success);
  font-weight: bold;
}

.tilt-status.alert {
  color: var(--danger);
  animation: blink 0.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.level-container {
  width: 100%;
  height: 60px;
}

.level-svg {
  width: 100%;
  height: 100%;
}

.scale-text {
  font-size: 8px;
  fill: rgba(255, 255, 255, 0.4);
  text-anchor: middle;
  font-family: var(--font-tech);
}

.bubble {
  filter: drop-shadow(0 0 6px currentColor);
  transition: cx 0.15s ease-out;
}

.bubble.alert {
  filter: drop-shadow(0 0 10px var(--danger));
}

.tilt-value-container {
  text-align: center;
}

.tilt-value {
  font-family: var(--font-display);
  font-size: 28px;
  color: #fff;
  font-weight: bold;
  transition: color 0.3s;
}

.tilt-value.alert {
  color: var(--danger);
}

.tilt-unit {
  font-size: 16px;
  color: var(--primary);
  margin-left: 2px;
}
</style>
