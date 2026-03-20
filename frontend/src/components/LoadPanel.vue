<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { BorderBox10 as DvBorderBox10 } from '@kjgl77/datav-vue3'
import * as echarts from 'echarts'
import { sensorData, loadHistory } from '../composables/useWebSocket'

const trendChartRef = ref<HTMLDivElement | null>(null)
const distributionChartRef = ref<HTMLDivElement | null>(null)

let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

const loadUsage = computed(() => Math.min(100, Math.max(0, sensorData.loadRatio * 100)))

const loadState = computed(() => {
  if (loadUsage.value >= 90) {
    return { label: 'OVERLOAD', tone: 'danger' }
  }

  if (loadUsage.value >= 65) {
    return { label: 'WATCH', tone: 'warn' }
  }

  return { label: 'SAFE', tone: 'safe' }
})

const distributionData = computed(() => {
  const source = loadHistory.value
  const bucketCount = 24
  const step = Math.max(1, Math.floor(source.length / bucketCount))

  return Array.from({ length: bucketCount }, (_, index) => {
    const start = index * step
    const end = index === bucketCount - 1 ? source.length : Math.min(source.length, start + step)
    const slice = source.slice(start, end)
    const average = slice.reduce((sum, item) => sum + item, 0) / Math.max(slice.length, 1)
    const wave = 0.02 * Math.cos(index * 0.55)

    return Number(Math.max(0, average / 1000 + wave).toFixed(3))
  })
})

function createTrendOption(): echarts.EChartsOption {
  const maxLoad = Math.max(...loadHistory.value, 1000)
  const yMax = Math.ceil(maxLoad * 1.15 / 50) * 50

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
        return `载荷值: ${Number(point?.data ?? 0).toFixed(0)} kg`
      }
    },
    grid: {
      top: 24,
      right: 18,
      bottom: 28,
      left: 52
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: loadHistory.value.map((_, index) => `${index + 1}`),
      axisLine: {
        lineStyle: { color: 'rgba(79, 246, 255, 0.18)' }
      },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(173, 222, 255, 0.62)',
        fontSize: 10,
        interval: 11,
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
      min: 0,
      max: yMax,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(173, 222, 255, 0.62)',
        fontSize: 10,
        formatter: (value: number) => `${value.toFixed(0)}`
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
        type: 'line',
        data: loadHistory.value,
        smooth: 0.35,
        showSymbol: false,
        lineStyle: {
          width: 3,
          color: '#44f6ff',
          shadowBlur: 14,
          shadowColor: 'rgba(68, 246, 255, 0.42)'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(68, 246, 255, 0.28)' },
            { offset: 0.72, color: 'rgba(32, 92, 255, 0.10)' },
            { offset: 1, color: 'rgba(1, 11, 32, 0)' }
          ])
        },
        markPoint: {
          symbol: 'circle',
          symbolSize: 11,
          itemStyle: {
            color: '#62f4ff',
            shadowBlur: 12,
            shadowColor: 'rgba(98, 244, 255, 0.55)'
          },
          data: [
            {
              name: '当前',
              coord: [loadHistory.value.length - 1, sensorData.load]
            }
          ]
        },
        markLine: {
          symbol: 'none',
          lineStyle: {
            type: 'dashed',
            color: 'rgba(255, 96, 126, 0.7)'
          },
          label: {
            color: 'rgba(255, 150, 168, 0.88)',
            formatter: '安全阈值'
          },
          data: [{ yAxis: 1000 }]
        }
      }
    ]
  }
}

function createDistributionOption(): echarts.EChartsOption {
  const data = distributionData.value
  const maxValue = Math.max(0.4, Math.ceil(Math.max(...data, 0.35) * 10) / 10)

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
        return `分段占比 ${point?.axisValue}: ${(Number(point?.data ?? 0) * 100).toFixed(1)}%`
      }
    },
    grid: {
      top: 18,
      right: 10,
      bottom: 24,
      left: 32
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
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: 'rgba(173, 222, 255, 0.48)',
        fontSize: 10,
        formatter: (value: number) => `${Math.round(value * 100)}%`
      },
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
            { offset: 0, color: '#48f7ff' },
            { offset: 0.55, color: '#2689ff' },
            { offset: 1, color: 'rgba(14, 82, 186, 0.36)' }
          ]),
          shadowBlur: 10,
          shadowColor: 'rgba(79, 246, 255, 0.26)'
        }
      }
    ]
  }
}

function renderCharts() {
  trendChart?.setOption(createTrendOption(), true)
  distributionChart?.setOption(createDistributionOption(), true)
}

function handleResize() {
  trendChart?.resize()
  distributionChart?.resize()
}

onMounted(() => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
  }

  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
  }

  renderCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  distributionChart?.dispose()
})

watch(
  () => loadHistory.value.map((item) => item),
  () => {
    renderCharts()
  },
  { deep: true }
)
</script>

<template>
  <dv-border-box10 class="panel-shell">
    <div class="dv-border-content dashboard-panel">
      <div class="panel-title-inner">荷载安全监测 / LOAD SAFETY</div>

      <div class="panel-kpi-grid">
        <div class="data-chip">
          <div class="data-chip__label">实时荷载</div>
          <div class="data-chip__value">
            {{ sensorData.load.toFixed(0) }}<span class="data-chip__unit">kg</span>
          </div>
          <div class="data-chip__sub">Current load</div>
        </div>
        <div class="data-chip">
          <div class="data-chip__label">峰值记录</div>
          <div class="data-chip__value data-chip__value--accent">
            {{ sensorData.maxLoad.toFixed(0) }}<span class="data-chip__unit">kg</span>
          </div>
          <div class="data-chip__sub">Peak load</div>
        </div>
        <div class="data-chip">
          <div class="data-chip__label">承载占比</div>
          <div class="data-chip__value">
            {{ loadUsage.toFixed(0) }}<span class="data-chip__unit">%</span>
          </div>
          <div class="data-chip__sub">Capacity usage</div>
        </div>
      </div>

      <div class="status-meter">
        <div class="status-meter__header">
          <span>荷载安全等级</span>
          <span :class="['status-meter__state', `status-meter__state--${loadState.tone}`]">
            {{ loadState.label }}
          </span>
        </div>
        <div class="status-meter__scale">
          <span>0</span>
          <span>25</span>
          <span>50</span>
          <span>75</span>
          <span>100</span>
        </div>
        <div class="status-meter__track status-meter__track--load">
          <div
            class="status-meter__pointer"
            :style="{ left: `calc(${loadUsage}% - 1px)` }"
          ></div>
        </div>
        <div class="status-meter__legend">
          <span>低负载</span>
          <span>关注区</span>
          <span>超限风险</span>
        </div>
      </div>

      <div class="chart-card chart-card--primary">
        <div class="chart-card__header">
          <div>
            <div class="chart-card__title">实时荷载趋势</div>
            <div class="chart-card__subtitle">Load trend over time</div>
          </div>
          <div class="chart-card__tag">ACTIVE LOAD</div>
        </div>
        <div ref="trendChartRef" class="chart-full"></div>
      </div>

      <div class="chart-card chart-card--secondary">
        <div class="chart-card__header">
          <div>
            <div class="chart-card__title">分段载荷分布</div>
            <div class="chart-card__subtitle">Section utilization profile</div>
          </div>
          <div class="chart-card__tag">SECTION LOAD</div>
        </div>
        <div ref="distributionChartRef" class="chart-full chart-full--compact"></div>
      </div>
    </div>
  </dv-border-box10>
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
