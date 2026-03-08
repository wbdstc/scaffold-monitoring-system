<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, computed } from 'vue'
import * as THREE from 'three'
import { sensorData } from '../composables/useWebSocket'

const container = ref<HTMLDivElement | null>(null)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let scaffoldGroup: THREE.Group
let animationId: number
let resizeObserver: ResizeObserver

// 保存原始材质颜色用于恢复
const normalColor = new THREE.Color(0x00f2ff)
const alertColor = new THREE.Color(0xff0055)
let materials: THREE.MeshStandardMaterial[] = []

// 报警状态
const isAlert = computed(() => sensorData.status !== 'MONITORING')

// 创建钢管几何体
function createPipe(start: THREE.Vector3, end: THREE.Vector3, radius: number = 0.05): THREE.Mesh {
  const direction = new THREE.Vector3().subVectors(end, start)
  const length = direction.length()
  
  const geometry = new THREE.CylinderGeometry(radius, radius, length, 8)
  const material = new THREE.MeshStandardMaterial({
    color: normalColor,
    metalness: 0.8,
    roughness: 0.3,
    emissive: normalColor,
    emissiveIntensity: 0.1
  })
  materials.push(material)
  
  const mesh = new THREE.Mesh(geometry, material)
  
  // 定位到中点
  mesh.position.copy(start).add(end).multiplyScalar(0.5)
  
  // 旋转到正确方向
  mesh.quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction.clone().normalize()
  )
  
  return mesh
}

// 创建节点球
function createNode(position: THREE.Vector3, radius: number = 0.08): THREE.Mesh {
  const geometry = new THREE.SphereGeometry(radius, 12, 12)
  const material = new THREE.MeshStandardMaterial({
    color: normalColor,
    metalness: 0.9,
    roughness: 0.2,
    emissive: normalColor,
    emissiveIntensity: 0.3
  })
  materials.push(material)
  
  const mesh = new THREE.Mesh(geometry, material)
  mesh.position.copy(position)
  return mesh
}

// 压力传感器材质 (底部4个)
let pressureSensorMats: THREE.MeshStandardMaterial[] = []
// 偏移传感器材质 (顶部4个)
let tiltSensorMats: THREE.MeshStandardMaterial[] = []
// 偏移传感器天线 (用于旋转)
let tiltAntennas: THREE.Mesh[] = []

// 创建压力传感器 (底部荷载监测)
function createPressureSensor(position: THREE.Vector3): THREE.Group {
  const group = new THREE.Group()
  
  // 底座 - 扁平圆柱
  const baseGeom = new THREE.CylinderGeometry(0.1, 0.12, 0.04, 16)
  const baseMat = new THREE.MeshStandardMaterial({
    color: 0x00ff66,
    metalness: 0.7,
    roughness: 0.3,
    emissive: 0x00ff66,
    emissiveIntensity: 0.4
  })
  pressureSensorMats.push(baseMat)
  const base = new THREE.Mesh(baseGeom, baseMat)
  group.add(base)
  
  // 顶部发光环
  const ringGeom = new THREE.TorusGeometry(0.08, 0.012, 8, 24)
  const ringMat = new THREE.MeshStandardMaterial({
    color: 0x00ff66,
    emissive: 0x00ff66,
    emissiveIntensity: 0.6
  })
  const ring = new THREE.Mesh(ringGeom, ringMat)
  ring.rotation.x = Math.PI / 2
  ring.position.y = 0.025
  group.add(ring)
  
  group.position.copy(position)
  group.position.y = position.y - 0.02
  return group
}

// 创建偏移晃动传感器 (顶部偏移监测)
function createTiltSensor(position: THREE.Vector3): THREE.Group {
  const group = new THREE.Group()
  
  // 传感器主体 - 球形
  const bodyGeom = new THREE.SphereGeometry(0.05, 12, 12)
  const bodyMat = new THREE.MeshStandardMaterial({
    color: 0x0066ff,
    metalness: 0.8,
    roughness: 0.2,
    emissive: 0x0066ff,
    emissiveIntensity: 0.4
  })
  tiltSensorMats.push(bodyMat)
  const body = new THREE.Mesh(bodyGeom, bodyMat)
  group.add(body)
  
  // 天线指示器 - 会根据倾斜角度旋转
  const antennaGeom = new THREE.CylinderGeometry(0.008, 0.008, 0.12, 8)
  const antennaMat = new THREE.MeshStandardMaterial({
    color: 0xff6600,
    emissive: 0xff6600,
    emissiveIntensity: 0.5
  })
  const antenna = new THREE.Mesh(antennaGeom, antennaMat)
  antenna.position.y = 0.08
  tiltAntennas.push(antenna)
  group.add(antenna)
  
  // 顶部小球指示灯
  const tipGeom = new THREE.SphereGeometry(0.015, 8, 8)
  const tipMat = new THREE.MeshStandardMaterial({
    color: 0xff6600,
    emissive: 0xff6600,
    emissiveIntensity: 0.8
  })
  const tip = new THREE.Mesh(tipGeom, tipMat)
  tip.position.y = 0.14
  antenna.add(tip)
  
  group.position.copy(position)
  group.position.y = position.y + 0.08
  return group
}

// 构建脚手架模型
function buildScaffold(): THREE.Group {
  const group = new THREE.Group()
  
  // 定义节点位置 (单位: 米)
  const h1 = 0, h2 = 1.0, h3 = 2.0, h4 = 3.0 // 高度层
  const w = 1.0 // 宽度
  const d = 0.5 // 深度
  
  // 前面左立柱
  const fl: THREE.Vector3[] = [
    new THREE.Vector3(-w/2, h1, d/2),
    new THREE.Vector3(-w/2, h2, d/2),
    new THREE.Vector3(-w/2, h3, d/2),
    new THREE.Vector3(-w/2, h4, d/2)
  ]
  
  // 前面右立柱
  const fr: THREE.Vector3[] = [
    new THREE.Vector3(w/2, h1, d/2),
    new THREE.Vector3(w/2, h2, d/2),
    new THREE.Vector3(w/2, h3, d/2),
    new THREE.Vector3(w/2, h4, d/2)
  ]
  
  // 后面左立柱
  const bl: THREE.Vector3[] = [
    new THREE.Vector3(-w/2, h1, -d/2),
    new THREE.Vector3(-w/2, h2, -d/2),
    new THREE.Vector3(-w/2, h3, -d/2),
    new THREE.Vector3(-w/2, h4, -d/2)
  ]
  
  // 后面右立柱
  const br: THREE.Vector3[] = [
    new THREE.Vector3(w/2, h1, -d/2),
    new THREE.Vector3(w/2, h2, -d/2),
    new THREE.Vector3(w/2, h3, -d/2),
    new THREE.Vector3(w/2, h4, -d/2)
  ]
  
  // 立柱
  for (let i = 0; i < 3; i++) {
    group.add(createPipe(fl[i]!, fl[i+1]!))
    group.add(createPipe(fr[i]!, fr[i+1]!))
    group.add(createPipe(bl[i]!, bl[i+1]!))
    group.add(createPipe(br[i]!, br[i+1]!))
  }
  
  // 横梁
  for (let i = 1; i <= 3; i++) {
    // 前后横梁
    group.add(createPipe(fl[i]!, fr[i]!))
    group.add(createPipe(bl[i]!, br[i]!))
    // 左右横梁
    group.add(createPipe(fl[i]!, bl[i]!))
    group.add(createPipe(fr[i]!, br[i]!))
  }
  
  // 斜撑 (X形)
  for (let i = 0; i < 3; i++) {
    // 前面斜撑
    group.add(createPipe(fl[i]!, fr[i+1]!, 0.03))
    group.add(createPipe(fr[i]!, fl[i+1]!, 0.03))
  }
  
  // 节点球
  for (let i = 0; i < 4; i++) {
    group.add(createNode(fl[i]!))
    group.add(createNode(fr[i]!))
    group.add(createNode(bl[i]!))
    group.add(createNode(br[i]!))
  }
  
  // === 添加传感器 ===
  // 底部压力传感器 (监测荷载)
  group.add(createPressureSensor(fl[0]!))
  group.add(createPressureSensor(fr[0]!))
  group.add(createPressureSensor(bl[0]!))
  group.add(createPressureSensor(br[0]!))
  
  // 顶部偏移传感器 (监测晃动/偏移)
  group.add(createTiltSensor(fl[3]!))
  group.add(createTiltSensor(fr[3]!))
  group.add(createTiltSensor(bl[3]!))
  group.add(createTiltSensor(br[3]!))
  
  // 将模型中心移到原点
  group.position.y = -1.5
  
  return group
}

// 初始化场景
function initScene() {
  if (!container.value) return
  
  const width = container.value.clientWidth
  const height = container.value.clientHeight
  
  // 场景
  scene = new THREE.Scene()
  scene.background = null // 透明背景
  
  // 相机
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100)
  camera.position.set(4, 2.5, 4)
  camera.lookAt(0, 0, 0)
  
  // 渲染器
  renderer = new THREE.WebGLRenderer({ 
    antialias: true, 
    alpha: true 
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  container.value.appendChild(renderer.domElement)
  
  // 灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
  scene.add(ambientLight)
  
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(5, 10, 5)
  scene.add(directionalLight)
  
  const pointLight = new THREE.PointLight(0x00f2ff, 1, 10)
  pointLight.position.set(0, 2, 2)
  scene.add(pointLight)
  
  // 创建脚手架
  scaffoldGroup = buildScaffold()
  scene.add(scaffoldGroup)
  
  // 地面网格
  const gridHelper = new THREE.GridHelper(4, 20, 0x00f2ff, 0x003344)
  gridHelper.position.y = -1.5
  scene.add(gridHelper)
}

// 动画循环
function animate() {
  animationId = requestAnimationFrame(animate)
  
  if (!scaffoldGroup) return
  
  // 基础旋转 (缓慢自转)
  scaffoldGroup.rotation.y += 0.002
  
  // 震动效果：根据 vibration 值添加随机抖动
  const vibrationIntensity = Math.abs(sensorData.vibration) * 0.02
  scaffoldGroup.position.x = (Math.random() - 0.5) * vibrationIntensity
  scaffoldGroup.position.z = (Math.random() - 0.5) * vibrationIntensity
  
  // 倾斜效果：根据 tiltAngle 倾斜模型
  const tiltRad = (sensorData.tiltAngle * Math.PI) / 180
  scaffoldGroup.rotation.z = tiltRad
  
  // === 压力传感器颜色更新 ===
  const loadRatio = sensorData.loadRatio
  let pressureColor: THREE.Color
  if (loadRatio > 0.9) {
    // 超载 - 红色闪烁
    const flash = Math.sin(Date.now() * 0.01) > 0 ? 1 : 0.5
    pressureColor = new THREE.Color(0xff0055).multiplyScalar(flash)
  } else if (loadRatio > 0.6) {
    // 警告 - 黄色
    pressureColor = new THREE.Color(0xffcc00)
  } else {
    // 正常 - 绿色
    pressureColor = new THREE.Color(0x00ff66)
  }
  pressureSensorMats.forEach(mat => {
    mat.color.copy(pressureColor)
    mat.emissive.copy(pressureColor)
    mat.emissiveIntensity = loadRatio > 0.9 ? 0.8 : 0.4
  })
  
  // === 偏移传感器颜色和天线更新 ===
  const absAngle = Math.abs(sensorData.tiltAngle)
  let tiltColor: THREE.Color
  if (absAngle > 10) {
    // 严重偏移 - 红色
    tiltColor = new THREE.Color(0xff0055)
  } else if (absAngle > 5) {
    // 警告 - 黄色
    tiltColor = new THREE.Color(0xffcc00)
  } else {
    // 正常 - 蓝色
    tiltColor = new THREE.Color(0x0066ff)
  }
  tiltSensorMats.forEach(mat => {
    mat.color.copy(tiltColor)
    mat.emissive.copy(tiltColor)
    mat.emissiveIntensity = absAngle > 5 ? 0.6 : 0.4
  })
  
  // 天线跟随倾斜角度旋转
  tiltAntennas.forEach(antenna => {
    antenna.rotation.z = tiltRad
  })
  
  renderer.render(scene, camera)
}

// 处理大小变化
function handleResize() {
  if (!container.value || !camera || !renderer) return
  
  const width = container.value.clientWidth
  const height = container.value.clientHeight
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// 监听报警状态变化，更新材质颜色
watch(isAlert, (alert) => {
  const color = alert ? alertColor : normalColor
  const emissiveIntensity = alert ? 0.5 : 0.1
  
  materials.forEach(mat => {
    mat.color.copy(color)
    mat.emissive.copy(color)
    mat.emissiveIntensity = emissiveIntensity
  })
})

onMounted(() => {
  initScene()
  animate()
  
  // 监听容器大小变化
  if (container.value) {
    resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(container.value)
  }
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  resizeObserver?.disconnect()
  renderer?.dispose()
  materials = []
  pressureSensorMats = []
  tiltSensorMats = []
  tiltAntennas = []
})
</script>

<template>
  <div ref="container" class="scaffold-3d"></div>
</template>

<style scoped>
.scaffold-3d {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

.scaffold-3d canvas {
  display: block;
}
</style>
