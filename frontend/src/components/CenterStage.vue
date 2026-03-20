<script setup lang="ts">
import { computed } from 'vue'
import { BorderBox11 as DvBorderBox11 } from '@kjgl77/datav-vue3'
import TiltGauge from './TiltGauge.vue'
import ScaffoldScene from './ScaffoldScene.vue'
import { sensorData } from '../composables/useWebSocket'

const loadUsage = computed(() => Math.round(sensorData.loadRatio * 100))

const stageState = computed(() => {
  if (sensorData.status === 'OVERLOAD') {
    return {
      title: 'LOAD WARNING',
      desc: '荷载超限风险',
      tone: 'danger'
    }
  }

  if (sensorData.status === 'TILT ALERT') {
    return {
      title: 'TILT WARNING',
      desc: '倾角异常偏移',
      tone: 'warn'
    }
  }

  if (sensorData.status === 'VIBRATION ALERT') {
    return {
      title: 'VIBRATION WATCH',
      desc: '振动响应偏高',
      tone: 'warn'
    }
  }

  return {
    title: 'ACTIVE MONITORING',
    desc: '系统运行稳定',
    tone: 'safe'
  }
})
</script>

<template>
  <dv-border-box11 class="center-shell" title="DIGITAL TWIN / 数字孪生监测场" :title-width="320">
    <div class="center-content">
      <div class="scanner"></div>
      <div class="radar-glow"></div>

      <div class="hud-panel hud-panel--left">
        <div class="hud-pill">
          <span>SAFETY SCORE</span>
          <strong>{{ sensorData.safetyScore }}</strong>
        </div>
        <div class="hud-pill">
          <span>实时振动</span>
          <strong>{{ sensorData.vibration.toFixed(2) }} g</strong>
        </div>
      </div>

      <div class="hud-panel hud-panel--right">
        <div :class="['alert-summary', `alert-summary--${stageState.tone}`]">
          <span>{{ stageState.desc }}</span>
          <strong>{{ stageState.title }}</strong>
        </div>
      </div>

      <div class="status-badge">
        <div class="status-label">STRUCTURE MODE</div>
        <div :class="['status-value', `status-value--${stageState.tone}`]">
          {{ stageState.title }}
        </div>
      </div>

      <ScaffoldScene class="scaffold-3d" />

      <div class="cockpit-footer">
        <div class="footer-section left">
          <div class="footer-label">SAFETY SCORE / 综合安全分</div>
          <div class="footer-value">{{ sensorData.safetyScore }}</div>
          <div class="footer-meta">Status: {{ sensorData.status }}</div>
        </div>

        <div class="footer-section center">
          <TiltGauge class="embedded-gauge" />
        </div>

        <div class="footer-section right">
          <div class="footer-label">LOAD UTILIZATION / 载荷占比</div>
          <div
            :class="[
              'footer-value',
              { warning: loadUsage >= 65, critical: loadUsage >= 90 }
            ]"
          >
            {{ loadUsage }}<span class="unit">%</span>
          </div>
          <div class="footer-meta">
            Tilt {{ sensorData.tiltAngle >= 0 ? '+' : '' }}{{ sensorData.tiltAngle.toFixed(1) }}°
          </div>
        </div>
      </div>
    </div>
  </dv-border-box11>
</template>

<style scoped>
.center-shell {
  height: 100%;
}

.center-content {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 55%, rgba(86, 246, 255, 0.06), transparent 34%),
    linear-gradient(180deg, rgba(5, 15, 34, 0.42), rgba(2, 8, 20, 0.7));
}

.radar-glow {
  position: absolute;
  left: 50%;
  bottom: 88px;
  width: 420px;
  height: 420px;
  transform: translateX(-50%);
  border-radius: 50%;
  background:
    radial-gradient(circle, rgba(86, 246, 255, 0.12) 0%, rgba(86, 246, 255, 0.04) 28%, transparent 70%);
  filter: blur(20px);
  pointer-events: none;
}

.hud-panel {
  position: absolute;
  top: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 3;
}

.hud-panel--left {
  left: 22px;
}

.hud-panel--right {
  right: 22px;
  align-items: flex-end;
}

.hud-pill,
.alert-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 150px;
  padding: 10px 14px;
  border: 1px solid rgba(86, 246, 255, 0.12);
  border-radius: 14px;
  background: rgba(5, 18, 38, 0.72);
  box-shadow: var(--shadow-panel);
  backdrop-filter: blur(10px);
}

.hud-pill span,
.alert-summary span {
  color: var(--text-dim);
  font-size: 11px;
  letter-spacing: 1px;
}

.hud-pill strong,
.alert-summary strong {
  color: var(--text-main);
  font-family: var(--font-display);
  font-size: 18px;
  letter-spacing: 1.2px;
}

.alert-summary--safe strong {
  color: var(--primary);
}

.alert-summary--warn strong {
  color: var(--accent);
}

.alert-summary--danger strong {
  color: var(--danger);
}

.status-badge {
  position: absolute;
  right: 24px;
  bottom: 124px;
  z-index: 3;
  text-align: right;
}

.status-label {
  color: var(--text-dim);
  font-size: 11px;
  letter-spacing: 1px;
}

.status-value {
  margin-top: 4px;
  font-family: var(--font-display);
  font-size: 18px;
  letter-spacing: 1.2px;
}

.status-value--safe {
  color: var(--success);
}

.status-value--warn {
  color: var(--accent);
}

.status-value--danger {
  color: var(--danger);
}

.scaffold-3d {
  position: relative;
  z-index: 2;
  flex: 1;
  min-height: 0;
  width: 100%;
}

.cockpit-footer {
  position: relative;
  z-index: 3;
  display: grid;
  grid-template-columns: 220px 1fr 220px;
  align-items: center;
  gap: 18px;
  min-height: 112px;
  padding: 16px 26px;
  border-top: 1px solid rgba(86, 246, 255, 0.2);
  background:
    linear-gradient(180deg, rgba(5, 16, 35, 0.88), rgba(3, 10, 22, 0.96));
  box-shadow: 0 -14px 28px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(12px);
}

.cockpit-footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  width: 42%;
  height: 2px;
  transform: translateX(-50%);
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  box-shadow: 0 0 12px rgba(86, 246, 255, 0.35);
}

.footer-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.footer-section.center {
  position: relative;
  height: 100%;
  padding: 0 18px;
}

.footer-section.center::before,
.footer-section.center::after {
  content: '';
  position: absolute;
  top: 18%;
  bottom: 18%;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(86, 246, 255, 0.24), transparent);
}

.footer-section.center::before {
  left: 0;
}

.footer-section.center::after {
  right: 0;
}

.footer-section.right {
  align-items: flex-end;
  text-align: right;
}

.footer-label {
  color: var(--text-dim);
  font-size: 11px;
  letter-spacing: 1.2px;
}

.footer-value {
  margin-top: 6px;
  color: var(--text-main);
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  text-shadow: 0 0 18px rgba(86, 246, 255, 0.18);
}

.footer-value.warning {
  color: var(--accent);
}

.footer-value.critical {
  color: var(--danger);
}

.footer-meta {
  margin-top: 7px;
  color: rgba(191, 226, 255, 0.6);
  font-size: 11px;
  letter-spacing: 1px;
}

.unit {
  margin-left: 4px;
  color: var(--primary);
  font-size: 16px;
}

.embedded-gauge {
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
}
</style>
