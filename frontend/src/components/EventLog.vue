<script setup lang="ts">
import { computed } from 'vue'
import { BorderBox1 as DvBorderBox1 } from '@kjgl77/datav-vue3'
import { logs } from '../composables/useWebSocket'

const logCount = computed(() => logs.value.length)
</script>

<template>
  <dv-border-box1 class="log-shell">
    <div class="event-log-content">
      <div class="event-log-header">
        <div class="panel-title-inner event-log-title">&gt;&gt;&gt; SYSTEM EVENTS / 系统事件</div>
        <div class="event-log-meta">{{ logCount }} entries</div>
      </div>

      <div class="log-container">
        <div v-for="(log, index) in logs" :key="index" :class="['log-entry', log.type]">
          [{{ log.time }}] {{ log.msg }}
        </div>
      </div>
    </div>
  </dv-border-box1>
</template>

<style scoped>
.log-shell {
  height: 100%;
}

.event-log-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  padding: var(--gap-sm);
}

.event-log-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.event-log-title {
  flex: 1;
  margin-bottom: 0;
}

.event-log-meta {
  flex-shrink: 0;
  padding: 4px 10px;
  border: 1px solid rgba(86, 246, 255, 0.14);
  border-radius: 999px;
  background: rgba(86, 246, 255, 0.08);
  color: var(--primary);
  font-family: var(--font-display);
  font-size: 10px;
  letter-spacing: 1.2px;
}
</style>
