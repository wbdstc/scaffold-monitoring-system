<script setup lang="ts">
import { BorderBox11 as DvBorderBox11 } from '@kjgl77/datav-vue3'
import { sensorData } from '../composables/useWebSocket'
import { computed } from 'vue'

const isAlert = computed(() => sensorData.status !== 'MONITORING')
</script>

<template>
  <dv-border-box11 title="DIGITAL TWIN / 数字孪生" :title-width="280">
    <div class="center-content">
      <!-- 扫描线 -->
      <div class="scanner"></div>
      
      <!-- SVG 脚手架 -->
      <svg class="scaffold-svg" viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet">
        <!-- 基座 -->
        <ellipse cx="200" cy="360" rx="150" ry="20" fill="none" stroke="var(--primary)" 
                 stroke-width="1" stroke-dasharray="5,5" opacity="0.5" />

        <!-- 结构体 -->
        <g id="structure">
          <path d="M120 350 L120 50 L280 50 L280 350" class="s-beam" />
          <path d="M120 150 L280 150" class="s-beam" />
          <path d="M120 250 L280 250" class="s-beam" />
          <!-- 交叉支撑 -->
          <path d="M120 350 L280 250" class="s-beam-inner" />
          <path d="M120 250 L280 150" class="s-beam-inner" />
          <path d="M120 150 L280 50" class="s-beam-inner" />
        </g>

        <!-- 传感器节点 -->
        <circle cx="120" cy="50" :class="['s-node', { alert: isAlert }]" r="4" />
        <circle cx="280" cy="50" :class="['s-node', { alert: isAlert }]" r="4" />
        <circle cx="120" cy="150" :class="['s-node', { alert: isAlert }]" r="4" />
        <circle cx="280" cy="150" :class="['s-node', { alert: isAlert }]" r="4" />
        <circle cx="120" cy="250" :class="['s-node', { alert: isAlert }]" r="4" />
        <circle cx="280" cy="250" :class="['s-node', { alert: isAlert }]" r="4" />
      </svg>

      <!-- 浮动状态标牌 -->
      <div class="status-badge">
        <div class="status-label">SYSTEM MODE</div>
        <div class="status-value">ACTIVE MONITORING</div>
      </div>
    </div>
  </dv-border-box11>
</template>

<style scoped>
.center-content {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: radial-gradient(circle, rgba(0, 242, 255, 0.05) 0%, transparent 70%);
}

.status-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  text-align: right;
}

.status-label {
  font-size: 12px;
  color: var(--text-dim);
}

.status-value {
  font-size: 16px;
  color: var(--primary);
  font-weight: bold;
}
</style>
