import { ref, reactive, onMounted, onUnmounted } from 'vue'

// 阈值配置
const THRESHOLD_LOAD = 1000
const THRESHOLD_VIB = 1.0

// 响应式状态
export const sensorData = reactive({
    vibration: 0,
    load: 0,
    maxVibration: 0,
    maxLoad: 0,
    stability: 100,
    loadRatio: 0,
    status: 'MONITORING' as 'MONITORING' | 'VIBRATION ALERT' | 'OVERLOAD',
    statusColor: 'var(--success)'
})

export const vibHistory = ref<number[]>(Array(100).fill(0))
export const loadHistory = ref<number[]>(Array(60).fill(0))
export const logs = ref<Array<{ time: string; msg: string; type: string }>>([])

let ws: WebSocket | null = null
let audioCtx: AudioContext | null = null

// 报警声音
function beep(freq = 800) {
    if (!audioCtx) return
    const osc = audioCtx.createOscillator()
    const gain = audioCtx.createGain()
    osc.connect(gain)
    gain.connect(audioCtx.destination)
    osc.frequency.value = freq
    gain.gain.value = 0.1
    osc.start()
    setTimeout(() => osc.stop(), 200)
}

// 添加日志
export function addLog(msg: string, type: string = 'info') {
    const time = new Date().toLocaleTimeString()
    logs.value.unshift({ time, msg, type })
    if (logs.value.length > 50) logs.value.pop()
}

// 初始化音频
export function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)()
    }
}

// WebSocket 连接
export function useWebSocket() {
    const connected = ref(false)

    function connect() {
        // 根据当前页面地址构建 WebSocket URL
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsHost = window.location.hostname
        const wsPort = '8000' // 后端端口
        const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/ws`

        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            connected.value = true
            addLog('Connected to Server.', 'info')
        }

        ws.onclose = () => {
            connected.value = false
            addLog('Connection Lost.', 'danger')
            // 自动重连
            setTimeout(connect, 3000)
        }

        ws.onerror = () => {
            addLog('WebSocket Error.', 'danger')
        }

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            const v = parseFloat(data.v) // 震动 g
            const w = parseFloat(data.w) // 荷载 kg

            // 更新当前值
            sensorData.vibration = v
            sensorData.load = w

            // 峰值记录
            if (Math.abs(v) > sensorData.maxVibration) {
                sensorData.maxVibration = Math.abs(v)
            }
            if (w > sensorData.maxLoad) {
                sensorData.maxLoad = w
            }

            // 更新稳定性指数
            sensorData.stability = Math.max(0, 100 - (Math.abs(v) / 2.0 * 100))

            // 更新荷载比率
            sensorData.loadRatio = Math.min(1, w / THRESHOLD_LOAD)

            // 更新历史数据
            vibHistory.value.shift()
            vibHistory.value.push(v)

            loadHistory.value.shift()
            loadHistory.value.push(w)

            // 报警逻辑
            if (w > THRESHOLD_LOAD) {
                addLog(`荷载过载预警! Value: ${w}kg`, 'danger')
                beep(400)
                sensorData.status = 'OVERLOAD'
                sensorData.statusColor = 'var(--danger)'
            } else if (Math.abs(v) > THRESHOLD_VIB) {
                addLog(`震动异常! Value: ${v.toFixed(2)}g`, 'warn')
                beep(800)
                sensorData.status = 'VIBRATION ALERT'
                sensorData.statusColor = 'var(--accent)'
            } else {
                sensorData.status = 'MONITORING'
                sensorData.statusColor = 'var(--success)'
            }
        }
    }

    onMounted(() => {
        connect()
    })

    onUnmounted(() => {
        if (ws) {
            ws.close()
        }
    })

    return { connected }
}
