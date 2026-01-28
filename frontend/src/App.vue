<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import VibrationPanel from './components/VibrationPanel.vue'
import LoadPanel from './components/LoadPanel.vue'
import CenterStage from './components/CenterStage.vue'
import EventLog from './components/EventLog.vue'
import { useWebSocket, initAudio, addLog } from './composables/useWebSocket'

// 初始化 WebSocket 连接
useWebSocket()

// 启动页状态
const showIntro = ref(true)
const introExiting = ref(false)

function handleEnter() {
  introExiting.value = true
  initAudio()
  
  setTimeout(() => {
    showIntro.value = false
    addLog('System Initialized.', 'info')
    addLog('Establishing WebSocket connection...', 'info')
    
    // 延迟触发 resize 事件，让 ECharts 重新计算尺寸
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'))
    }, 100)
  }, 800)
}
</script>

<template>
  <!-- GIF 背景启动页 -->
  <div 
    v-if="showIntro" 
    :class="['intro-overlay', { 'fade-out': introExiting }]"
    @click="handleEnter"
  >
    <!-- GIF 背景 -->
    <img class="intro-bg" src="/video/background.gif" alt="background" />
    
    <!-- 主标题 -->
    <div class="intro-content">
      <h1 class="intro-title">脚手架监测系统</h1>
      <p class="intro-subtitle">SCAFFOLD MONITORING SYSTEM</p>
    </div>
    
    <!-- 点击提示 -->
    <div class="intro-hint">点击任意位置进入系统</div>
  </div>

  <!-- 主系统界面（带 GIF 背景） -->
  <div v-show="!showIntro" class="app-container">
    <AppHeader />
    <div class="main-content">
      <VibrationPanel />
      <div class="center-stage">
        <CenterStage />
        <EventLog />
      </div>
      <LoadPanel />
    </div>
  </div>
</template>

<style scoped>
/* === 启动页样式 === */
.intro-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
  cursor: pointer;
  overflow: hidden;
  background: #000;
}

.intro-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 100%;
  min-height: 100%;
  width: auto;
  height: auto;
  transform: translate(-50%, -50%);
  object-fit: cover;
}

/* 主标题区域 */
.intro-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
}

/* 大标题 - 冲击力动画 */
.intro-title {
  font-family: var(--font-display);
  font-size: clamp(40px, 8vw, 80px);
  font-weight: 900;
  letter-spacing: 10px;
  color: #fff;
  margin: 0;
  white-space: nowrap;
  opacity: 0;
  animation: titleImpact 1.5s cubic-bezier(0.16, 1, 0.3, 1) 0.3s forwards;
}

@keyframes titleImpact {
  0% {
    opacity: 0;
    transform: scale(3) translateY(-20px);
    filter: blur(20px);
  }
  40% {
    opacity: 1;
    transform: scale(0.95) translateY(5px);
    filter: blur(0);
  }
  60% {
    transform: scale(1.02) translateY(-2px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
    filter: blur(0);
  }
}

/* 副标题 */
.intro-subtitle {
  font-family: var(--font-tech);
  font-size: clamp(14px, 2vw, 24px);
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 8px;
  margin-top: 20px;
  opacity: 0;
  animation: fadeIn 1s ease-out 1.5s forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 点击提示 */
.intro-hint {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  font-family: var(--font-tech);
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 5px;
  opacity: 0;
  animation: pulseHint 2s ease-in-out infinite 2s;
}

@keyframes pulseHint {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 退出动画 */
.intro-overlay.fade-out {
  animation: overlayExit 0.8s ease-in-out forwards;
}

@keyframes overlayExit {
  0% { opacity: 1; }
  100% { opacity: 0; pointer-events: none; }
}

/* === 主系统样式 === */
.center-stage {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 100%;
  min-height: 0;
}

.center-stage > :first-child {
  flex: 1;
  min-height: 0;
}

.center-stage > :last-child {
  height: 100px;
  flex-shrink: 0;
}
</style>
