<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { BorderBox8 as DvBorderBox8 } from '@kjgl77/datav-vue3'
import * as echarts from 'echarts'
import { sensorData, vibHistory } from '../composables/useWebSocket'

const vibChartRef = ref<HTMLDivElement | null>(null)
const gaugeChartRef = ref<HTMLDivElement | null>(null)
let vibChart: echarts.ECharts | null = null
let gaugeChart: echarts.ECharts | null = null

onMounted(() => {
  // 初始化震动波形图
  if (vibChartRef.value) {
    vibChart = echarts.init(vibChartRef.value)
    vibChart.setOption({
      backgroundColor: 'transparent',
      grid: { top: 5, bottom: 5, left: 0, right: 0 },
      xAxis: { type: 'category', show: false, data: vibHistory.value },
      yAxis: { type: 'value', min: -2, max: 2, show: false },
      series: [{
        type: 'line',
        data: vibHistory.value,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#00f2ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,242,255,0.3)' },
            { offset: 1, color: 'rgba(0,242,255,0)' }
          ])
        }
      }]
    })
  }

  // 初始化稳定性仪表盘
  if (gaugeChartRef.value) {
    gaugeChart = echarts.init(gaugeChartRef.value)
    gaugeChart.setOption({
      series: [{
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        pointer: { show: false },
        progress: {
          show: true,
          overlap: false,
          roundCap: true,
          clip: false,
          itemStyle: { color: '#00f2ff' }
        },
        axisLine: { lineStyle: { width: 10, color: [[1, 'rgba(255,255,255,0.1)']] } },
        splitLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        detail: {
          fontSize: 24,
          offsetCenter: [0, '20%'],
          formatter: (val: number) => val.toFixed(1) + '%',
          color: '#fff',
          fontFamily: 'Orbitron'
        },
        data: [{ value: 100, name: 'STABILITY' }],
        title: { offsetCenter: [0, '60%'], fontSize: 10, color: 'rgba(255,255,255,0.5)' }
      }]
    })
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  vibChart?.dispose()
  gaugeChart?.dispose()
})

function handleResize() {
  vibChart?.resize()
  gaugeChart?.resize()
}

// 监听数据变化更新图表
watch(() => vibHistory.value, () => {
  vibChart?.setOption({ series: [{ data: vibHistory.value }] })
}, { deep: true })

watch(() => sensorData.stability, (newVal) => {
  const color = newVal < 60 ? '#ff0055' : (newVal < 80 ? '#f59e0b' : '#00f2ff')
  gaugeChart?.setOption({
    series: [{
      data: [{ value: newVal }],
      itemStyle: { color }
    }]
  })
})
</script>

<template>
  <dv-border-box8 :dur="3">
    <div class="dv-border-content">
      <div class="panel-title-inner">震动特征分析 / VIBRATION</div>
      
      <!-- 核心指标 -->
      <div class="digital-readout">
        <div>
          <div class="dr-label">实时加速度 Current</div>
          <div class="dr-value">
            {{ sensorData.vibration.toFixed(2) }}<span class="dr-unit">g</span>
          </div>
        </div>
        <div style="text-align: right;">
          <div class="dr-label">峰值保持 Peak Hold</div>
          <div class="dr-value" style="color: var(--accent);">
            {{ sensorData.maxVibration.toFixed(2) }}<span class="dr-unit">g</span>
          </div>
        </div>
      </div>

      <!-- 实时波形 -->
      <div class="chart-section waveform">
        <div class="dr-label chart-label">Real-time Waveform 实时波形</div>
        <div ref="vibChartRef" class="chart-full"></div>
      </div>

      <!-- 稳定性仪表 -->
      <div class="chart-section gauge">
        <div class="dr-label">Stability Index 结构稳定性指数</div>
        <div ref="gaugeChartRef" class="chart-full"></div>
      </div>
    </div>
  </dv-border-box8>
</template>

<style scoped>
.chart-section {
  border: 1px solid rgba(0, 242, 255, 0.1);
  background: rgba(0, 0, 0, 0.3);
  padding: 4px;
  display: flex;
  flex-direction: column;
}

.chart-section.waveform {
  flex: 1.8;
}

.chart-section.gauge {
  flex: 1.2;
}

.chart-label {
  padding-left: 5px;
  font-size: 11px;
}
</style>
