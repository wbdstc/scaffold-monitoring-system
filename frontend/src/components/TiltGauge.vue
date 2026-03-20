<script setup lang="ts">
import { computed } from 'vue'
import { sensorData } from '../composables/useWebSocket'

const bubbleOffset = computed(() => {
  const clampedAngle = Math.max(-30, Math.min(30, sensorData.tiltAngle))
  return (clampedAngle / 30) * 60
})

const isAlert = computed(() => Math.abs(sensorData.tiltAngle) > 10)
const isCritical = computed(() => Math.abs(sensorData.tiltAngle) > 20)

const tiltStateText = computed(() => {
  if (isCritical.value) {
    return 'CRITICAL'
  }

  if (isAlert.value) {
    return 'WATCH'
  }

  return 'LEVEL'
})
</script>

<template>
  <div :class="['tilt-gauge', { alert: isAlert, critical: isCritical }]">
    <div class="tilt-header">
      <span class="tilt-label">TILT MONITOR / 倾角水平仪</span>
      <span :class="['tilt-status', { alert: isAlert, critical: isCritical }]">
        {{ tiltStateText }}
      </span>
    </div>

    <div class="level-container">
      <svg class="level-svg" viewBox="0 0 200 60" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="tubeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="rgba(86, 246, 255, 0.16)" />
            <stop offset="50%" stop-color="rgba(86, 246, 255, 0.08)" />
            <stop offset="100%" stop-color="rgba(86, 246, 255, 0.16)" />
          </linearGradient>
          <radialGradient id="bubbleGrad" cx="30%" cy="30%">
            <stop offset="0%" :stop-color="isAlert ? '#ffd29d' : '#c6ffff'" />
            <stop offset="100%" :stop-color="isAlert ? '#ff536f' : '#56f6ff'" />
          </radialGradient>
        </defs>

        <rect
          x="10"
          y="15"
          width="180"
          height="30"
          rx="15"
          fill="url(#tubeGrad)"
          :stroke="isAlert ? 'var(--danger)' : 'var(--primary)'"
          stroke-width="1.5"
        />

        <line
          x1="100"
          y1="18"
          x2="100"
          y2="42"
          stroke="rgba(255,255,255,0.28)"
          stroke-width="1"
          stroke-dasharray="2,2"
        />
        <line x1="60" y1="20" x2="60" y2="40" stroke="rgba(255,255,255,0.15)" stroke-width="1" />
        <line x1="140" y1="20" x2="140" y2="40" stroke="rgba(255,255,255,0.15)" stroke-width="1" />

        <text x="60" y="55" class="scale-text">-20°</text>
        <text x="100" y="55" class="scale-text">0°</text>
        <text x="140" y="55" class="scale-text">+20°</text>

        <circle
          :cx="100 + bubbleOffset"
          cy="30"
          r="10"
          fill="url(#bubbleGrad)"
          :class="['bubble', { alert: isAlert }]"
        />
      </svg>
    </div>

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
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  padding: 0 8px;
}

.tilt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tilt-label {
  color: var(--text-dim);
  font-size: 11px;
  letter-spacing: 1px;
}

.tilt-status {
  color: var(--success);
  font-family: var(--font-display);
  font-size: 10px;
  letter-spacing: 1px;
}

.tilt-status.alert {
  color: var(--accent);
}

.tilt-status.critical {
  color: var(--danger);
}

.level-container {
  width: 100%;
  height: 62px;
}

.level-svg {
  width: 100%;
  height: 100%;
}

.scale-text {
  fill: rgba(209, 234, 255, 0.45);
  font-family: var(--font-tech);
  font-size: 8px;
  text-anchor: middle;
}

.bubble {
  filter: drop-shadow(0 0 8px rgba(86, 246, 255, 0.56));
  transition: cx 0.18s ease-out;
}

.bubble.alert {
  filter: drop-shadow(0 0 10px rgba(255, 83, 111, 0.48));
}

.tilt-value-container {
  text-align: center;
}

.tilt-value {
  color: var(--text-main);
  font-family: var(--font-display);
  font-size: 30px;
  font-weight: 700;
  line-height: 1;
}

.tilt-value.alert {
  color: var(--danger);
}

.tilt-unit {
  margin-left: 3px;
  color: var(--primary);
  font-size: 16px;
}
</style>
