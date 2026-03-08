<script setup lang="ts">
import { BorderBox11 as DvBorderBox11 } from '@kjgl77/datav-vue3'
import TiltGauge from './TiltGauge.vue'
import ScaffoldScene from './ScaffoldScene.vue'
</script>

<template>
  <dv-border-box11 title="DIGITAL TWIN / 数字孪生" :title-width="280">
    <div class="center-content">
      <!-- 扫描线 -->
      <div class="scanner"></div>
      
      <!-- 3D 脚手架 -->
      <ScaffoldScene class="scaffold-3d" />

      <!-- 浮动状态标牌 -->
      <div class="status-badge">
        <div class="status-label">SYSTEM MODE</div>
        <div class="status-value">ACTIVE MONITORING</div>
      </div>

      <!-- 底部控制台 (Cockpit Footer) -->
      <div class="cockpit-footer">
        <!-- 左侧数据 -->
        <div class="footer-section left">
          <div class="footer-label">ENV TEMP / 环境温度</div>
          <div class="footer-value">24.5<span class="unit">°C</span></div>
        </div>

        <!-- 核心仪表 (Tilt Gauge) -->
        <div class="footer-section center">
          <TiltGauge class="embedded-gauge" />
        </div>

        <!-- 右侧状态 -->
        <div class="footer-section right">
          <div class="footer-label">CONN STATUS / 连接</div>
          <div class="footer-value success">STABLE</div>
        </div>
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
  flex-direction: column;
  background: radial-gradient(circle, rgba(0, 242, 255, 0.05) 0%, transparent 70%);
}

.scaffold-3d {
  flex: 1;
  width: 100%;
  min-height: 0;
  z-index: 10;
}

/* ... (Status badge styles remain unchanged) ... */
.status-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  text-align: right;
  z-index: 20;
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

/* === Cockpit Footer === */
.cockpit-footer {
  height: 100px; /* Fixed height for stability */
  width: 100%;
  background: rgba(0, 10, 20, 0.85);
  border-top: 1px solid rgba(0, 242, 255, 0.3);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  padding: 0 30px;
  gap: 20px;
  position: relative;
  z-index: 30;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.5);
}

/* Decoration lines for footer */
.cockpit-footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 2px;
  background: var(--primary);
  box-shadow: 0 0 10px var(--primary);
}

.footer-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.footer-section.left, .footer-section.right {
  width: 20%;
}

.footer-section.right {
  align-items: flex-end;
  text-align: right;
}

.footer-section.center {
  flex: 1;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

/* Vertical dividers */
.footer-section.center::before,
.footer-section.center::after {
  content: '';
  position: absolute;
  top: 20%;
  bottom: 20%;
  width: 1px;
  background: linear-gradient(to bottom, transparent, rgba(0, 242, 255, 0.2), transparent);
}

.footer-section.center::before { left: 0; }
.footer-section.center::after { right: 0; }

.footer-label {
  font-size: 11px;
  color: var(--text-dim);
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.footer-value {
  font-family: var(--font-display);
  font-size: 24px;
  color: #fff;
  font-weight: bold;
}

.footer-value.success {
  color: var(--success);
}

.unit {
  font-size: 14px;
  color: var(--text-dim);
  margin-left: 4px;
}

/* Embed TiltGauge style overrides */
.embedded-gauge {
  width: 100%;
  max-width: 320px;
}
</style>
