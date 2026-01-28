<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { BorderBox10 as DvBorderBox10 } from '@kjgl77/datav-vue3'
import * as echarts from 'echarts'
import 'echarts-liquidfill'
import { sensorData, loadHistory } from '../composables/useWebSocket'

const liquidChartRef = ref<HTMLDivElement | null>(null)
const loadChartRef = ref<HTMLDivElement | null>(null)
let liquidChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null

onMounted(() => {
  // 初始化液位图
  if (liquidChartRef.value) {
    liquidChart = echarts.init(liquidChartRef.value)
    liquidChart.setOption({
      series: [{
        type: 'liquidFill',
        data: [0, 0],
        radius: '90%',
        color: ['rgba(0, 102, 255, 0.6)', 'rgba(0, 242, 255, 0.5)'],
        backgroundStyle: { color: 'rgba(0,0,0,0.2)' },
        outline: { show: false },
        label: {
          fontSize: 24,
          color: '#fff',
          fontFamily: 'Orbitron',
          formatter: (p: any) => (p.value * 100).toFixed(0) + '%'
        }
      }]
    })
  }

  // 初始化趋势图
  if (loadChartRef.value) {
    loadChart = echarts.init(loadChartRef.value)
    loadChart.setOption({
      grid: { top: 10, bottom: 20, left: 30, right: 10 },
      xAxis: { type: 'category', show: false },
      yAxis: {
        type: 'value',
        splitLine: { show: false },
        axisLabel: { color: '#666', fontSize: 10 }
      },
      series: [{
        type: 'bar',
        data: loadHistory.value,
        itemStyle: { color: '#0066ff' },
        barWidth: '60%'
      }]
    })
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  liquidChart?.dispose()
  loadChart?.dispose()
})

function handleResize() {
  liquidChart?.resize()
  loadChart?.resize()
}

// 监听荷载比率更新液位图
watch(() => sensorData.loadRatio, (newVal) => {
  const color = newVal > 0.9
    ? ['#ff0055', 'rgba(255,0,85,0.5)']
    : ['#0066ff', 'rgba(0,242,255,0.5)']
  liquidChart?.setOption({
    series: [{
      data: [newVal, newVal - 0.05],
      color
    }]
  })
})

// 监听荷载历史更新趋势图
watch(() => loadHistory.value, () => {
  loadChart?.setOption({ series: [{ data: loadHistory.value }] })
}, { deep: true })
</script>

<template>
  <dv-border-box10>
    <div class="dv-border-content">
      <div class="panel-title-inner">荷载安全监测 / LOAD SAFETY</div>
      
      <!-- 核心指标 -->
      <div class="digital-readout">
        <div>
          <div class="dr-label">实时荷载 Current Load</div>
          <div class="dr-value">
            {{ sensorData.load.toFixed(0) }}<span class="dr-unit">kg</span>
          </div>
        </div>
        <div style="text-align: right;">
          <div class="dr-label">最大荷载 Peak Load</div>
          <div class="dr-value" style="color: var(--accent);">
            {{ sensorData.maxLoad.toFixed(0) }}<span class="dr-unit">kg</span>
          </div>
        </div>
      </div>

      <!-- 液位图 -->
      <div class="chart-section liquid">
        <div class="dr-label" style="text-align: center; margin-bottom: 3px; font-size: 11px;">
          Capacity Usage 承载率
        </div>
        <div ref="liquidChartRef" class="chart-full"></div>
      </div>

      <!-- 趋势图 -->
      <div class="chart-section trend">
        <div class="dr-label" style="font-size: 11px;">60s Trend 荷载趋势</div>
        <div ref="loadChartRef" class="chart-full"></div>
      </div>
    </div>
  </dv-border-box10>
</template>

<style scoped>
.chart-section {
  display: flex;
  flex-direction: column;
}

.chart-section.liquid {
  flex: 1.2;
  padding: 5px 0;
}

.chart-section.trend {
  flex: 1.2;
  border-top: 1px dashed rgba(255, 255, 255, 0.1);
  padding-top: 5px;
}
</style>
