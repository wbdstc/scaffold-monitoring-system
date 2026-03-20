<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { BorderBox8 as DvBorderBox8 } from '@kjgl77/datav-vue3'
import * as echarts from 'echarts'
import { sensorData, vibHistory } from '../composables/useWebSocket'

const waveformChartRef = ref<HTMLDivElement | null>(null)
const spectrumChartRef = ref<HTMLDivElement | null>(null)

let waveformChart: echarts.ECharts | null = null
let spectrumChart: echarts.ECharts | null = null

const vibrationRisk = computed(() =>
  Math.min(100, Math.max(0, Math.abs(sensorData.vibration) * 50))
)

const vibrationState = computed(() => {
  if (vibrationRisk.value >= 70) {
    return { label: 'CRITICAL', tone: 'danger' }
  }

  if (vibrationRisk.value >= 40) {
    return { label: 'WATCH', tone: 'warn' }
  }

  return { label: 'STABLE', tone: 'safe' }
})

const spectrumData = computed(() => {
  const source = vibHistory.value
  const bucketCount = 24
  const step = Math.max(1, Math.floor(source.length / bucketCount))

  return Array.from({ length: bucketCount }, (_, index) => {
    const start = index * step
    const end = index === bucketCount - 1 ? source.length : Math.min(source.length, start + step)
    const slice = source.slice(start, end)
    const average =
      slice.reduce((sum, item) => sum + Math.abs(item), 0) / Math.max(slice.length, 1)
    const sculpt = 0.06 + Math.sin(index * 0.6) * 0.025

    return Number((average * 0.9 + sculpt).toFixed(3))
  })
})

function createWaveformOption(): echarts.EChartsOption {
  const yLimit = Math.max(
    1.2,
    Math.ceil(Math.max(...vibHistory.value.map((item) => Math.abs(item)), 1) * 1.4 * 10) / 10
  )

  return {
    animationDuration: 300,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(3, 14, 30, 0.94)',
      borderColor: 'rgba(79, 246, 255, 0.35)',
      textStyle: { color: '#effbff' },
      axisPointer: {
        lineStyle: { color: 'rgba(79, 246, 255, 0.45)' }
      },
      formatter: (params: any) => {
        const point = Array.isArray(params) ? params[0] : params
        return `振动值: ${Number(point?.data ?? 0).toFixed(3)} g`
      }
    },
    grid: {
      top: 26,
      right: 18,
      bottom: 28,
      left: 50
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: vibHistory.value.map((_, index) => `${index + 1}`),
      axisLine: {
        lineStyle: { color: 'rgba(79, 246, 255, 0.18)' }
      },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(173, 222, 255, 0.62)',
        fontSize: 10,
        interval: 19,
        formatter: (value: string) => `T${value}`
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: 'rgba(79, 246, 255, 0.06)'
        }
      }
    },
    yAxis: {
      type: 'value',
      min: -yLimit,
      max: yLimit,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(173, 222, 255, 0.62)',
        fontSize: 10,
        formatter: (value: number) => `${value.toFixed(1)}`
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(79, 246, 255, 0.08)',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '振动波形',
        type: 'line',
        data: vibHistory.value,
        smooth: 0.3,
        showSymbol: false,
        lineStyle: {
          width: 3,
          color: '#4ff6ff',
          shadowBlur: 16,
          shadowColor: 'rgba(79, 246, 255, 0.45)'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(79, 246, 255, 0.28)' },
            { offset: 0.65, color: 'rgba(30, 119, 255, 0.12)' },
            { offset: 1, color: 'rgba(1, 11, 32, 0)' }
          ])
        },
        markLine: {
          symbol: 'none',
          lineStyle: {
            type: 'dashed',
            color: 'rgba(255, 212, 82, 0.55)'
          },
          label: {
            color: 'rgba(255, 224, 135, 0.8)',
            formatter: '预警阈值'
          },
          data: [{ yAxis: 1 }]
        }
      }
    ]
  }
}

function createSpectrumOption(): echarts.EChartsOption {
  const data = spectrumData.value
  const maxValue = Math.max(0.25, Math.ceil(Math.max(...data, 0.2) * 10) / 10)

  return {
    animationDuration: 300,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(3, 14, 30, 0.94)',
      borderColor: 'rgba(79, 246, 255, 0.35)',
      textStyle: { color: '#effbff' },
      formatter: (params: any) => {
        const point = Array.isArray(params) ? params[0] : params
        return `频带 ${point?.axisValue}: ${Number(point?.data ?? 0).toFixed(3)}`
      }
    },
    grid: {
      top: 18,
      right: 10,
      bottom: 24,
      left: 14
    },
    xAxis: {
      type: 'category',
      data: data.map((_, index) => `${String(index + 1).padStart(2, '0')}`),
      axisLine: {
        lineStyle: { color: 'rgba(79, 246, 255, 0.18)' }
      },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(173, 222, 255, 0.55)',
        fontSize: 10,
        interval: 3
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: maxValue,
      axisLabel: { show: false },
      axisTick: { show: false },
      axisLine: { show: false },
      splitLine: {
        lineStyle: {
          color: 'rgba(79, 246, 255, 0.06)',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        type: 'bar',
        data,
        barWidth: '55%',
        itemStyle: {
          borderRadius: [7, 7, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#63f7ff' },
            { offset: 0.55, color: '#2d8eff' },
            { offset: 1, color: 'rgba(15, 74, 191, 0.35)' }
          ]),
          shadowBlur: 10,
          shadowColor: 'rgba(79, 246, 255, 0.3)'
        }
      }
    ]
  }
}

function renderCharts() {
  waveformChart?.setOption(createWaveformOption(), true)
  spectrumChart?.setOption(createSpectrumOption(), true)
}

function handleResize() {
  waveformChart?.resize()
  spectrumChart?.resize()
}

onMounted(() => {
  if (waveformChartRef.value) {
    waveformChart = echarts.init(waveformChartRef.value)
  }

  if (spectrumChartRef.value) {
    spectrumChart = echarts.init(spectrumChartRef.value)
  }

  renderCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  waveformChart?.dispose()
  spectrumChart?.dispose()
})

watch(
  () => vibHistory.value.map((item) => item),
  () => {
    renderCharts()
  },
  { deep: true }
)
</script>

<template>
  <dv-border-box8 class="panel-shell" :dur="3">
    <div class="dv-border-content dashboard-panel">
      <div class="panel-title-inner">振动特征分析 / VIBRATION SIGNATURE</div>

      <div class="panel-kpi-grid">
        <div class="data-chip">
          <div class="data-chip__label">实时振幅</div>
          <div class="data-chip__value">
            {{ sensorData.vibration.toFixed(2) }}<span class="data-chip__unit">g</span>
          </div>
          <div class="data-chip__sub">Current response</div>
        </div>
        <div class="data-chip">
          <div class="data-chip__label">峰值保持</div>
          <div class="data-chip__value data-chip__value--accent">
            {{ sensorData.maxVibration.toFixed(2) }}<span class="data-chip__unit">g</span>
          </div>
          <div class="data-chip__sub">Peak hold</div>
        </div>
        <div class="data-chip">
          <div class="data-chip__label">稳定指数</div>
          <div class="data-chip__value">
            {{ sensorData.stability.toFixed(0) }}<span class="data-chip__unit">%</span>
          </div>
          <div class="data-chip__sub">Structural stability</div>
        </div>
      </div>

      <div class="status-meter">
        <div class="status-meter__header">
          <span>结构响应风险等级</span>
          <span :class="['status-meter__state', `status-meter__state--${vibrationState.tone}`]">
            {{ vibrationState.label }}
          </span>
        </div>
        <div class="status-meter__scale">
          <span>0</span>
          <span>25</span>
          <span>50</span>
          <span>75</span>
          <span>100</span>
        </div>
        <div class="status-meter__track">
          <div
            class="status-meter__pointer"
            :style="{ left: `calc(${vibrationRisk}% - 1px)` }"
          ></div>
        </div>
        <div class="status-meter__legend">
          <span>正常巡检</span>
          <span>预警关注</span>
          <span>危险告警</span>
        </div>
      </div>

      <div class="chart-card chart-card--primary">
        <div class="chart-card__header">
          <div>
            <div class="chart-card__title">时域波形监测</div>
            <div class="chart-card__subtitle">Real-time vibration waveform</div>
          </div>
          <div class="chart-card__tag">ACTIVE MONITORING</div>
        </div>
        <div ref="waveformChartRef" class="chart-full"></div>
      </div>

      <div class="chart-card chart-card--secondary">
        <div class="chart-card__header">
          <div>
            <div class="chart-card__title">频带能量分布</div>
            <div class="chart-card__subtitle">Band energy profile</div>
          </div>
          <div class="chart-card__tag">SPECTRUM</div>
        </div>
        <div ref="spectrumChartRef" class="chart-full chart-full--compact"></div>
      </div>
    </div>
  </dv-border-box8>
</template>

<style scoped>
.panel-shell {
  height: 100%;
}

.chart-card--primary {
  flex: 1.55;
}

.chart-card--secondary {
  flex: 1;
  min-height: 180px;
}
</style>
