<script setup lang="ts">
import { BorderBox1 as DvBorderBox1 } from '@kjgl77/datav-vue3'
import { logs } from '../composables/useWebSocket'
</script>

<template>
  <dv-border-box1>
    <div class="event-log-content">
      <div class="panel-title-inner" style="padding: 4px 10px; font-size: 12px;">
        >>> SYSTEM EVENTS / 系统事件
      </div>
      <div class="log-container">
        <div 
          v-for="(log, index) in logs" 
          :key="index" 
          :class="['log-entry', log.type]"
        >
          [{{ log.time }}] {{ log.msg }}
        </div>
      </div>
    </div>
  </dv-border-box1>
</template>

<style scoped>
.event-log-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 5px;
}
</style>
