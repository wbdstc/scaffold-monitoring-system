import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import re
import numpy as np

# ================= 🔧 必须修改的区域 =================
# 🔴 请确保这里是你真实的端口号 (例如 'COM3', 'COM5')
SERIAL_PORT = 'COM5'  
BAUD_RATE = 115200
# ===================================================

# --- 设置字体 (解决中文和图标方块问题) ---
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei'] # 优先使用黑体
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

# --- 🎨 赛博朋克配色方案 ---
COLOR_BG = '#050a14'      # 深蓝黑背景
COLOR_GRID = '#1a2c42'    # 暗蓝网格
COLOR_VIB = '#00f2ff'     # 霓虹蓝 (震动)
COLOR_LOAD = '#ff0055'    # 霓虹粉 (压力)
COLOR_TEXT = '#cce7ff'    # 亮白文字
COLOR_WARN = '#ffcc00'    # 警告黄

# --- 初始化画布 ---
plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 9), facecolor=COLOR_BG)
fig.canvas.manager.set_window_title('🛡️ M5STACK 结构健康监测系统 (SHM Dashboard)')

# 布局：使用 GridSpec 做更复杂的布局
# 上面是震动波形，下面是压力趋势，右边预留一点空间写大字
gs = fig.add_gridspec(2, 4)
ax_vib = fig.add_subplot(gs[0, :3]) # 震动图占上排前3格
ax_load = fig.add_subplot(gs[1, :3]) # 压力图占下排前3格
ax_stat = fig.add_subplot(gs[:, 3]) # 右侧统计栏占满竖列

# 隐藏右侧统计栏的坐标轴，只用来显示文字
ax_stat.axis('off')

# --- 数据容器 ---
max_points = 150
data_vib = deque([0.0]*max_points, maxlen=max_points)
data_load = deque([0.0]*max_points, maxlen=max_points)
peak_load = 0.0

# --- 预绘制图表元素 (高性能模式) ---

# 1. 震动图 (Vibration)
# 辉光效果：画两条线，一条粗且半透明，一条细且亮
ax_vib.plot([], [], color=COLOR_VIB, linewidth=5, alpha=0.15) # 辉光层
line_vib, = ax_vib.plot([], [], color=COLOR_VIB, linewidth=1.5) # 核心层

ax_vib.set_facecolor(COLOR_BG)
ax_vib.set_title('⚡ 实时震动波形 (ACCELERATION X)', fontsize=12, color=COLOR_VIB, loc='left', pad=10)
ax_vib.set_ylim(-2.5, 2.5)
ax_vib.grid(True, color=COLOR_GRID, linestyle='-', linewidth=1)
# 去掉边框，只留左边和下边
ax_vib.spines['top'].set_visible(False)
ax_vib.spines['right'].set_visible(False)
ax_vib.spines['bottom'].set_color(COLOR_GRID)
ax_vib.spines['left'].set_color(COLOR_GRID)

# 2. 压力图 (Load)
ax_load.plot([], [], color=COLOR_LOAD, linewidth=5, alpha=0.15) # 辉光层
line_load, = ax_load.plot([], [], color=COLOR_LOAD, linewidth=2) # 核心层
fill_load = ax_load.fill_between(range(max_points), 0, 0, color=COLOR_LOAD, alpha=0.1) # 填充

ax_load.set_facecolor(COLOR_BG)
ax_load.set_title('⚖️ 结构荷载趋势 (STRUCTURAL LOAD)', fontsize=12, color=COLOR_LOAD, loc='left', pad=10)
ax_load.set_ylim(-10, 500)
ax_load.grid(True, color=COLOR_GRID, linestyle='-', linewidth=1)
ax_load.spines['top'].set_visible(False)
ax_load.spines['right'].set_visible(False)
ax_load.spines['bottom'].set_color(COLOR_GRID)
ax_load.spines['left'].set_color(COLOR_GRID)

# 3. 右侧仪表盘文字
text_title = ax_stat.text(0.5, 0.95, "MONITOR\nSYSTEM", ha='center', fontsize=20, color='white', fontweight='bold')
# 峰值显示
ax_stat.text(0.5, 0.80, "MAX PEAK", ha='center', fontsize=10, color='#666')
text_peak_val = ax_stat.text(0.5, 0.75, "0.0", ha='center', fontsize=28, color=COLOR_WARN, fontweight='bold')
ax_stat.text(0.5, 0.71, "grams", ha='center', fontsize=10, color='#666')

# 当前值显示
ax_stat.text(0.5, 0.60, "CURRENT", ha='center', fontsize=10, color='#666')
text_curr_val = ax_stat.text(0.5, 0.55, "0.0", ha='center', fontsize=28, color='white', fontweight='bold')
ax_stat.text(0.5, 0.51, "grams", ha='center', fontsize=10, color='#666')

# 状态指示灯
text_status = ax_stat.text(0.5, 0.30, "[ NORMAL ]", ha='center', fontsize=14, color='#00ff00', fontweight='bold', 
                           bbox=dict(facecolor='#003300', edgecolor='#00ff00', boxstyle='round,pad=0.5'))

# 装饰性线条
ax_stat.plot([0.2, 0.8], [0.65, 0.65], color='#333', linewidth=1, transform=ax_stat.transAxes)
ax_stat.plot([0.2, 0.8], [0.45, 0.45], color='#333', linewidth=1, transform=ax_stat.transAxes)

# --- 解析函数 ---
def parse_data(line):
    try:
        line_str = line.decode('utf-8', errors='ignore').strip()
        # 提取括号内的数字或直接提取数字
        # 兼容格式: "[0.52, 0.03]" 或 "0.52, 0.03"
        numbers = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", line_str)
        if len(numbers) >= 2:
            return float(numbers[0]), float(numbers[1])
    except:
        pass
    return None, None

def update(frame):
    global peak_load, fill_load
    
    # 读取数据
    while ser.in_waiting:
        line = ser.readline()
        w, v = parse_data(line)
        if w is not None:
            data_load.append(w)
            data_vib.append(v)
            if w > peak_load: peak_load = w

    # --- 更新震动图 (含辉光) ---
    x_data = range(len(data_vib))
    ax_vib.lines[0].set_data(x_data, data_vib) # 辉光
    ax_vib.lines[1].set_data(x_data, data_vib) # 线条
    
    # --- 更新压力图 (含辉光和填充) ---
    x_data_load = range(len(data_load))
    ax_load.lines[0].set_data(x_data_load, data_load) # 辉光
    ax_load.lines[1].set_data(x_data_load, data_load) # 线条
    
    # 动态Y轴
    current_max = max(data_load) if len(data_load) > 0 else 10
    if current_max > ax_load.get_ylim()[1] or current_max < ax_load.get_ylim()[1] * 0.6:
         ax_load.set_ylim(-50, max(500, current_max * 1.2))

    fill_load.remove()
    fill_load = ax_load.fill_between(x_data_load, data_load, color=COLOR_LOAD, alpha=0.15)

    # --- 更新右侧仪表盘 ---
    if len(data_load) > 0:
        curr_w = data_load[-1]
        text_peak_val.set_text(f"{peak_load:.1f}")
        text_curr_val.set_text(f"{curr_w:.1f}")
        
        # 报警变色逻辑
        if curr_w > 1000:
            text_status.set_text("⚠️ OVERLOAD")
            text_status.set_color('#ff0000')
            text_status.set_bbox(dict(facecolor='#330000', edgecolor='#ff0000', boxstyle='round,pad=0.5'))
        else:
            text_status.set_text("✅ NORMAL")
            text_status.set_color('#00ff00')
            text_status.set_bbox(dict(facecolor='#003300', edgecolor='#00ff00', boxstyle='round,pad=0.5'))

# --- 启动程序 ---
try:
    print(f"🚀 正在连接端口 {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print("✅ 连接成功！大屏启动中...")
    
    # cache_frame_data=False 解决 UserWarning 警告
    ani = FuncAnimation(fig, update, interval=30, blit=False, cache_frame_data=False)
    plt.show()

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()