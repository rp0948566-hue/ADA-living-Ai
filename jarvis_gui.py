# nova_full_ada.py
# A.D.A HUD — v2.3 (With Dynamic Particle Network)
# Requirements: PySide6 (required), psutil (optional), opencv-python (optional)
# Run: pip install PySide6 psutil opencv-python
# Save as nova_full_ada.py and run: python nova_full_ada.py

import sys, math, random, time, os
from datetime import datetime, timedelta
try:
    import psutil
except:
    psutil = None

cv2 = None

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QSize, QObject, Signal, QThread
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QLinearGradient, QRadialGradient, QImage,
    QPixmap, QBrush, QFontInfo
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QGridLayout, QPushButton, QListWidget, QTextEdit, QSlider,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QSpinBox
)

# --------------------- Helpers & Themes ---------------------
def clamp(v, lo, hi): return max(lo, min(hi, v))
def safe_now_str(): return datetime.now().strftime("%Y%m%d_%H%M%S")

THEMES = {
    "blue": {"bg": (5, 12, 20), "accent": (60, 200, 255), "glow": (60,200,255,180)},
    "red": {"bg": (18, 6, 8), "accent": (255,110,90), "glow": (255,110,90,180)},
    "green": {"bg": (6, 18, 12), "accent": (80,220,120), "glow": (80,220,120,180)},
    "purple": {"bg": (12, 6, 18), "accent": (180, 80, 255), "glow": (180,80,255,180)},
    "cyan": {"bg": (6, 18, 18), "accent": (80, 220, 255), "glow": (80,220,255,180)}
}
THEME_ORDER = ["blue","purple","cyan","red","green"]

# --------------------- Particle System ---------------------
class Particle:
    """Represents a single particle in the network"""
    def __init__(self, x, y, vx, vy, size, color, alpha, energy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.alpha = alpha
        self.energy = energy
        self.birth_time = time.time()
    
    def update(self, width, height, dt):
        """Update particle with random acceleration"""
        # Random acceleration for organic movement
        ax = random.uniform(-50, 50)
        ay = random.uniform(-50, 50)
        
        self.vx += ax * dt
        self.vy += ay * dt
        
        # Damping
        self.vx *= 0.98
        self.vy *= 0.98
        
        # Speed limit
        max_speed = 80
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Bounce off edges
        if self.x < 0 or self.x > width:
            self.vx = -self.vx * random.uniform(0.7, 1.0)
            self.x = max(0, min(width, self.x))
        
        if self.y < 0 or self.y > height:
            self.vy = -self.vy * random.uniform(0.7, 1.0)
            self.y = max(0, min(height, self.y))
        
        # Pulsating energy
        age = time.time() - self.birth_time
        self.energy = 0.5 + 0.5 * math.sin(age * 2.0 + self.x * 0.01)

class ParticleNetworkCore(QWidget):
    """Dynamic particle network - the heart of A.D.A"""
    def __init__(self):
        super().__init__()
        self.particles = []
        self.num_particles = 80
        self.connection_distance = 100
        self.speed = 1.0
        self.theme = THEMES['blue']
        self.last_time = time.time()
        
        self.setMinimumSize(420, 420)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Create particles with theme colors"""
        self.particles.clear()
        
        # Get colors based on current theme
        base_color = self.theme['accent']
        colors = [
            base_color,
            (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40)),
            (max(0, base_color[0] - 40), max(0, base_color[1] - 40), max(0, base_color[2] - 40))
        ]
        
        w, h = self.width(), self.height()
        for _ in range(self.num_particles):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            vx = random.uniform(-30, 30)
            vy = random.uniform(-30, 30)
            size = random.uniform(2, 5)
            color = random.choice(colors)
            alpha = random.randint(150, 255)
            energy = random.uniform(0, 1)
            
            self.particles.append(Particle(x, y, vx, vy, size, color, alpha, energy))
    
    def set_theme(self, k):
        """Update theme and reinitialize particles"""
        self.theme = THEMES.get(k, self.theme)
        self._initialize_particles()
        self.update()
    
    def set_speed(self, v):
        self.speed = max(0.1, float(v))
    
    def set_particles(self, n):
        self.num_particles = clamp(int(n), 10, 200)
        self._initialize_particles()
    
    def set_connection_distance(self, d):
        self.connection_distance = clamp(int(d), 50, 200)
    
    def animate_step(self, dt=0.016):
        """Update all particles"""
        current_time = time.time()
        actual_dt = (current_time - self.last_time) * self.speed
        self.last_time = current_time
        
        w, h = self.width(), self.height()
        for particle in self.particles:
            particle.update(w, h, min(actual_dt, 0.05))
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        rect = self.rect()
        w, h = rect.width(), rect.height()
        cx, cy = w // 2, h // 2
        
        # Background gradient
        bg = QRadialGradient(QPointF(cx, cy), min(w, h) * 0.5)
        bg.setColorAt(0.0, QColor(12, 16, 22))
        bg.setColorAt(1.0, QColor(6, 8, 12, 0))
        painter.fillRect(rect, bg)
        
        # Draw connections between nearby particles
        painter.setPen(Qt.NoPen)
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                dist = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
                
                if dist < self.connection_distance:
                    # Line opacity based on distance
                    opacity = int(255 * (1 - dist / self.connection_distance) * 0.3)
                    
                    # Blend colors
                    color = QColor(
                        (p1.color[0] + p2.color[0]) // 2,
                        (p1.color[1] + p2.color[1]) // 2,
                        (p1.color[2] + p2.color[2]) // 2,
                        opacity
                    )
                    
                    pen = QPen(color, 1)
                    painter.setPen(pen)
                    painter.drawLine(QPointF(p1.x, p1.y), QPointF(p2.x, p2.y))
        
        # Draw particles with glow
        painter.setPen(Qt.NoPen)
        for particle in self.particles:
            x, y = particle.x, particle.y
            
            # Glow layers
            for i in range(3):
                glow_size = particle.size * (4 - i) * particle.energy
                glow_alpha = int(40 * particle.energy / (i + 1))
                
                glow_color = QColor(*particle.color, glow_alpha)
                painter.setBrush(QBrush(glow_color))
                painter.drawEllipse(QPointF(x, y), glow_size, glow_size)
            
            # Core particle
            core_alpha = int(particle.alpha * (0.7 + 0.3 * particle.energy))
            core_color = QColor(*particle.color, core_alpha)
            painter.setBrush(QBrush(core_color))
            painter.drawEllipse(QPointF(x, y), particle.size, particle.size)
            
            # Bright center
            center_size = max(1.0, particle.size * 0.5)
            center_color = QColor(
                min(255, particle.color[0] + 100),
                min(255, particle.color[1] + 100),
                min(255, particle.color[2] + 100)
            )
            painter.setBrush(QBrush(center_color))
            painter.drawEllipse(QPointF(x, y), center_size, center_size)
        
        # Draw A.D.A text
        painter.setPen(QColor(220, 240, 255))
        font_name = "Orbitron" if QFontInfo(QFont("Orbitron")).family().lower() == "orbitron" else "Segoe UI"
        painter.setFont(QFont(font_name, 32, QFont.Black))
        painter.drawText(rect, Qt.AlignCenter, "A.D.A")

# --------------------- Background Worker for Performance ---------------------
class SystemWorker(QObject):
    """Runs all blocking psutil calls in a separate thread"""
    stats_updated = Signal(dict)
    network_updated = Signal(dict)
    processes_updated = Signal(list, str)
    
    def __init__(self):
        super().__init__()
        self._is_running = True
        self.last_net = None
        self.last_net_time = time.time()

    def stop(self):
        self._is_running = False

    def run(self):
        if not psutil:
            while self._is_running:
                stats = {
                    'cpu': random.uniform(5, 80),
                    'temp': 40 + 8 * math.sin(time.time() / 8.0) + random.uniform(-2, 2),
                    'batt': 72 + 6 * math.sin(time.time() / 20.0),
                    'mem': random.uniform(20, 70),
                    'disk': random.uniform(10, 80)
                }
                self.stats_updated.emit(stats)
                
                net = {
                    'up': (1.0 + math.sin(time.time()/3.0))*0.5 + random.random()*0.2,
                    'dn': (1.2 + math.cos(time.time()/2.5))*0.5 + random.random()*0.3
                }
                self.network_updated.emit(net)
                
                processes = [("System Idle", 90.0), ("python.exe", 5.0), ("chrome.exe", 2.0)]
                self.processes_updated.emit(processes, "Uptime: N/A")
                
                time.sleep(1)
            return

        counter = 0
        while self._is_running:
            stats = self._get_system_stats()
            self.stats_updated.emit(stats)
            
            net = self._get_network_stats()
            self.network_updated.emit(net)
            
            if counter % 3 == 0:
                processes, uptime = self._get_process_list()
                self.processes_updated.emit(processes, uptime)
            
            counter += 1
            time.sleep(1)

    def _get_system_stats(self):
        try: cpu = psutil.cpu_percent()
        except: cpu = 0
        try: mem = psutil.virtual_memory().percent
        except: mem = 0
        try: disk = psutil.disk_usage('/').percent
        except: disk = 0
        
        temp = None
        try:
            temps = psutil.sensors_temperatures()
            if temps: temp = next((v[0].current for k, v in temps.items() if v), None)
        except: pass
        if temp is None: temp = 40 + 8*math.sin(time.time()/8.0)
        
        batt = None
        try:
            if hasattr(psutil, 'sensors_battery'):
                b = psutil.sensors_battery()
                if b: batt = b.percent
        except: pass
        if batt is None: batt = 72 + 6*math.sin(time.time()/20.0)
        
        return {'cpu': cpu, 'mem': mem, 'disk': disk, 'temp': temp, 'batt': batt}

    def _get_network_stats(self):
        now = time.time()
        try:
            counters = psutil.net_io_counters()
            if self.last_net is None:
                self.last_net, self.last_net_time = counters, now
                return {'up': 0, 'dn': 0}
            
            dt = now - self.last_net_time if now > self.last_net_time else 1.0
            up = (counters.bytes_sent - self.last_net.bytes_sent) / dt / (1024*1024)
            dn = (counters.bytes_recv - self.last_net.bytes_recv) / dt / (1024*1024)
            self.last_net, self.last_net_time = counters, now
            return {'up': up, 'dn': dn}
        except:
            return {'up': 0, 'dn': 0}

    def _get_process_list(self):
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = str(timedelta(seconds=(datetime.now() - boot_time).seconds))
            
            processes = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)
            process_data = [(p.info['name'], p.info['cpu_percent']) for p in processes[:7]]
            return process_data, f"Uptime: {uptime}"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return [], "Uptime: N/A"

# --------------------- UI Components ---------------------
class SectionTitle(QLabel):
    def __init__(self, text):
        super().__init__(text.upper())
        self.setStyleSheet("color:#CFE7FF; font-weight:700; font-size:10px; letter-spacing:0.6px; margin-bottom: 4px;")

class CameraWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border-radius:8px; } QLabel{ color:#DCECFB; }")
        layout = QVBoxLayout(self); layout.setContentsMargins(8,8,8,8)
        self.title = SectionTitle("Live Camera Feed")
        self.video_label = QLabel("Camera: Offline"); self.video_label.setAlignment(Qt.AlignCenter); self.video_label.setMinimumHeight(180)
        layout.addWidget(self.title); layout.addWidget(self.video_label,1)
        global cv2
        try:
            if cv2 is None: import cv2 as _cv2; cv2 = _cv2
        except: cv2 = None
        self.capture = None; self.face_cascade = None
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_frame)

    def start_camera(self):
        if cv2 is None: return False
        try:
            if self.capture and self.capture.isOpened(): return True
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                self.capture.release(); self.capture = None; return False
            try: self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            except: self.face_cascade = None
            self.timer.start(33); return True
        except Exception as e: print("Camera start error:", e); return False

    def update_frame(self):
        if not self.capture or not self.capture.isOpened(): return
        ret, frame = self.capture.read()
        if not ret: return
        frame = cv2.resize(frame, (320,240))
        if self.face_cascade:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x,y,w,h) in faces: cv2.rectangle(frame, (x,y), (x+w,y+h), (100,220,255), 2)
        h,w,ch = frame.shape
        self.video_label.setPixmap(QPixmap.fromImage(QImage(frame.data, w, h, ch*w, QImage.Format_BGR888)))

    def snapshot(self, path):
        if not self.capture or not self.capture.isOpened(): return False
        ret, frame = self.capture.read()
        if not ret: return False
        return cv2.imwrite(path, frame)

    def stop_camera(self):
        self.timer.stop()
        if self.capture: self.capture.release(); self.capture = None
        self.video_label.setText("Camera: Offline")

class ProcessListWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QListWidget { background: transparent; border: none; color: #DCECFB; font-size: 11px; }
            QListWidget::item { padding: 3px; }
        """)
        layout = QVBoxLayout(self); layout.setContentsMargins(8,8,8,8)
        layout.addWidget(SectionTitle("Top Processes"))
        self.list_widget = QListWidget()
        self.uptime_label = QLabel("Uptime: --"); self.uptime_label.setStyleSheet("color: #A0C0E0; font-size: 11px; margin-top: 4px;")
        layout.addWidget(self.list_widget, 1); layout.addWidget(self.uptime_label)

    def update_data(self, processes, uptime_str):
        self.list_widget.clear()
        for name, percent in processes:
            self.list_widget.addItem(f"{name[:20]:<20} {percent:.1f}%")
        self.uptime_label.setText(uptime_str)
        if not psutil: self.list_widget.addItem("psutil not installed")

class WeatherWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.conditions = [("☀️", "Clear Sky"), ("☁️", "Cloudy"), ("⛅", "Partly Cloudy"), ("🌧️", "Light Rain"), ("💨", "Windy")]
        self.current_condition_idx = 0
        layout = QHBoxLayout(self); layout.setContentsMargins(10,4,10,4)
        self.icon_label = QLabel(self.conditions[0][0]); self.icon_label.setStyleSheet("font-size: 28px;")
        v_layout = QVBoxLayout(); v_layout.setSpacing(0)
        self.temp_label = QLabel("--°C"); self.temp_label.setStyleSheet("color: #EAF6FF; font-size: 18px; font-weight: bold;")
        self.condition_label = QLabel("Loading..."); self.condition_label.setStyleSheet("color: #A0C0E0; font-size: 11px;")
        v_layout.addWidget(self.temp_label); v_layout.addWidget(self.condition_label)
        layout.addWidget(self.icon_label); layout.addLayout(v_layout); layout.addStretch()
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_weather); self.timer.start(60000)
        self.update_weather()
    def update_weather(self):
        base_temp = 18.0; temp = base_temp + 4 * math.sin(time.time() / 3600) + random.uniform(-0.5, 0.5)
        self.temp_label.setText(f"{temp:.1f}°C")
        if random.random() < 0.1: self.current_condition_idx = (self.current_condition_idx + 1) % len(self.conditions)
        icon, text = self.conditions[self.current_condition_idx]
        self.icon_label.setText(icon); self.condition_label.setText(text)

class NeonBar(QWidget):
    def __init__(self, title, init=0.0, style='rainbow'):
        super().__init__()
        self.title=title; self.value=float(init); self.style=style
        self.setMinimumHeight(44); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    def setValue(self, v): self.value=clamp(float(v),0.0,100.0); self.update()
    def paintEvent(self, event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); r=self.rect().adjusted(6,6,-6,-6)
        p.setPen(Qt.NoPen); p.setBrush(QColor(16,20,28,220)); p.drawRoundedRect(self.rect(),8,8)
        p.setPen(QColor(170,190,210)); p.setFont(QFont("Segoe UI",9,QFont.Bold)); p.drawText(r.x(),r.y()-2,r.width(),16,Qt.AlignLeft|Qt.AlignTop,self.title.upper())
        bar=QRectF(r.x(),r.y()+18,r.width(),12); p.setBrush(QColor(24,30,40,220)); p.setPen(Qt.NoPen); p.drawRoundedRect(bar,6,6)
        fill=QRectF(bar.x(),bar.y(),bar.width()*(self.value/100.0),bar.height())
        grad=QLinearGradient(fill.topLeft(),fill.topRight())
        if self.style=='rainbow': grad.setColorAt(0.0,QColor(30,220,140)); grad.setColorAt(0.5,QColor(255,200,60)); grad.setColorAt(1.0,QColor(255,90,80))
        elif self.style=='pink': grad.setColorAt(0.0,QColor(255,100,220)); grad.setColorAt(1.0,QColor(200,50,255))
        elif self.style=='green': grad.setColorAt(0.0,QColor(40,220,120)); grad.setColorAt(1.0,QColor(20,160,100))
        else: grad.setColorAt(0.0,QColor(80,200,255)); grad.setColorAt(1.0,QColor(150,120,255))
        p.setBrush(grad); p.drawRoundedRect(fill,6,6)
        p.setPen(QColor(230,240,255)); p.setFont(QFont("Consolas",10,QFont.DemiBold)); p.drawText(r,Qt.AlignRight|Qt.AlignVCenter,f"{int(self.value)}%")

class AnimatedGridBackground(QWidget):
    def __init__(self,theme_key='blue'):
        super().__init__(); self.offset=0.0; self.num_particles=18; self.grid_spacing=40; self.grid_opacity=18
        self.particles=[(random.random(),random.random(),random.random()*2+0.2) for _ in range(self.num_particles)]
        self.timer=QTimer(self); self.timer.timeout.connect(self.step); self.timer.start(33)
        self.setAttribute(Qt.WA_TransparentForMouseEvents); self.theme_key=theme_key
    def set_theme(self,k): self.theme_key=k
    def set_particles(self,n):
        self.num_particles=clamp(int(n),0,100)
        while len(self.particles)<self.num_particles: self.particles.append((random.random(),random.random(),random.random()*2+0.2))
        self.particles=self.particles[:self.num_particles]
    def set_grid_spacing(self,s): self.grid_spacing=clamp(int(s),10,100)
    def set_grid_opacity(self,o): self.grid_opacity=clamp(int(o),0,100)
    def step(self):
        self.offset=(self.offset+0.6)%1000
        for i in range(len(self.particles)): x,y,s=self.particles[i]; self.particles[i]=(x,(y+0.001*(0.5+s))%1.0,s)
        self.update()
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); rect=self.rect(); w,h=rect.width(),rect.height()
        theme=THEMES.get(self.theme_key,THEMES['blue']); p.fillRect(rect,QColor(*theme['bg']))
        p.setPen(QColor(*theme['accent'],self.grid_opacity)); spacing=self.grid_spacing; ofs=int(self.offset)%spacing
        for x in range(-spacing,w+spacing,spacing): p.drawLine(x+ofs,0,x+ofs,h)
        for y in range(-spacing,h+spacing,spacing): p.drawLine(0,y+ofs,w,y+ofs)
        for x,y,s in self.particles:
            p.setBrush(QColor(*theme['accent'],int(120*s))); p.setPen(Qt.NoPen); p.drawEllipse(QPointF(x*w,y*h),int(1+s*3),int(1+s*3))

class TitleBar(QFrame):
    def __init__(self, title, on_theme, on_console, on_voice, on_settings):
        super().__init__()
        self.setStyleSheet("QFrame{background:rgba(8,12,16,200);border-bottom:1px solid rgba(100,140,200,20);}QLabel{color:#DDEFFB;}")
        lay=QHBoxLayout(self); lay.setContentsMargins(10,6,10,6); lbl=QLabel(title)
        font_name="Orbitron" if QFontInfo(QFont("Orbitron")).family().lower()=="orbitron" else "Segoe UI"
        lbl.setFont(QFont(font_name,12,QFont.Bold)); lay.addWidget(lbl); lay.addStretch()
        for tooltip, char, func in [("Cycle Theme","🎨",on_theme),("Toggle Console","💬",on_console),("Voice Mode","🎙️",on_voice),("Settings","⚙️",on_settings)]:
            btn=QPushButton(char); btn.setToolTip(tooltip); btn.clicked.connect(func); btn.setFixedSize(36,28)
            btn.setStyleSheet("QPushButton{border-radius:6px;background:rgba(100,140,200,12);}"); lay.addWidget(btn)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle("A.D.A Settings")
        self.setModal(True)
        self.setFixedSize(400, 420)
        self.config = config or {}

        stylesheet = """
            QDialog { background-color: rgb(10, 14, 20); border: 1px solid rgba(60, 200, 255, 100); font-family: Segoe UI, sans-serif; }
            QSpinBox { background-color: rgb(20, 30, 45); border: 1px solid rgb(60, 120, 180); border-radius: 4px; color: #EAF6FF; font-size: 12px; min-height: 24px; padding-left: 8px; }
            QSpinBox:hover { border-color: rgb(100, 220, 255); }
            QSlider::groove:horizontal { background: rgb(24, 30, 40); border: 1px solid rgb(60, 120, 180); height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: rgb(60, 200, 255); border: 1px solid rgb(100, 220, 255); width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }
            QPushButton { background-color: rgba(25, 45, 70, 200); border: 1px solid rgb(60, 200, 255); border-radius: 5px; padding: 6px 12px; font-weight: bold; color: #EAF6FF; }
            QPushButton:hover { background-color: rgb(40, 80, 120); border: 1px solid white; }
            QPushButton:pressed { background-color: rgb(60, 200, 255); color: rgb(10, 14, 20); }
        """
        self.setStyleSheet(stylesheet)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        form_widget = QWidget()
        layout = QFormLayout(form_widget)
        layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(8)
        
        label_style = "color: #A0C0E0; font-size: 11px;"

        # Particle Network Settings
        layout.addRow(SectionTitle("PARTICLE NETWORK"))
        self.spin_speed = QSpinBox(); self.spin_speed.setRange(1, 300); self.spin_speed.setValue(int(self.config.get('speed', 1.0) * 10))
        anim_speed_label = QLabel("Anim Speed (x0.1):"); anim_speed_label.setStyleSheet(label_style)
        layout.addRow(anim_speed_label, self.spin_speed)

        self.spin_particle_count = QSpinBox(); self.spin_particle_count.setRange(10, 200); self.spin_particle_count.setValue(self.config.get('particle_count', 80))
        particle_count_label = QLabel("Particle Count:"); particle_count_label.setStyleSheet(label_style)
        layout.addRow(particle_count_label, self.spin_particle_count)

        self.spin_connection_dist = QSpinBox(); self.spin_connection_dist.setRange(50, 200); self.spin_connection_dist.setValue(self.config.get('connection_dist', 100))
        connection_dist_label = QLabel("Connection Distance:"); connection_dist_label.setStyleSheet(label_style)
        layout.addRow(connection_dist_label, self.spin_connection_dist)

        # Background Animation
        layout.addRow(SectionTitle("BACKGROUND ANIMATION"))
        self.spin_bg_particles = QSpinBox(); self.spin_bg_particles.setRange(0, 100); self.spin_bg_particles.setValue(self.config.get('bg_particles', 18))
        bg_particles_label = QLabel("BG Particles:"); bg_particles_label.setStyleSheet(label_style)
        layout.addRow(bg_particles_label, self.spin_bg_particles)

        self.spin_grid_space = QSpinBox(); self.spin_grid_space.setRange(10, 100); self.spin_grid_space.setValue(self.config.get('grid_spacing', 40))
        grid_spacing_label = QLabel("Grid Spacing:"); grid_spacing_label.setStyleSheet(label_style)
        layout.addRow(grid_spacing_label, self.spin_grid_space)

        self.slider_opacity = QSlider(Qt.Horizontal); self.slider_opacity.setRange(0, 100); self.slider_opacity.setValue(self.config.get('grid_opacity', 18))
        grid_opacity_label = QLabel("Grid Opacity:"); grid_opacity_label.setStyleSheet(label_style)
        layout.addRow(grid_opacity_label, self.slider_opacity)

        main_layout.addWidget(form_widget)
        main_layout.addStretch()

        btn_box = QHBoxLayout()
        btn_ok = QPushButton("Apply"); btn_ok.clicked.connect(self.accept)
        btn_reset = QPushButton("Reset"); btn_reset.clicked.connect(self.reset_defaults)
        
        btn_box.addStretch()
        btn_box.addWidget(btn_reset)
        btn_box.addWidget(btn_ok)
        main_layout.addLayout(btn_box)

    def get_values(self):
        return {
            "speed": self.spin_speed.value()/10.0,
            "particle_count": self.spin_particle_count.value(),
            "connection_dist": self.spin_connection_dist.value(),
            "bg_particles": self.spin_bg_particles.value(),
            "grid_spacing": self.spin_grid_space.value(),
            "grid_opacity": self.slider_opacity.value()
        }

    def reset_defaults(self):
        self.spin_speed.setValue(10)
        self.spin_particle_count.setValue(80)
        self.spin_connection_dist.setValue(100)
        self.spin_bg_particles.setValue(18)
        self.spin_grid_space.setValue(40)
        self.slider_opacity.setValue(18)

# --------------------- Main HUD ---------------------
class NovaHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A.D.A HUD — v2.3")
        self.resize(1280, 800)
        self.settings = {"speed":1.0,"particle_count":80,"connection_dist":100,"bg_particles":18,"grid_spacing":40,"grid_opacity":18}
        self.theme_index=0; self.theme_key=THEME_ORDER[self.theme_index]
        
        self.setup_ui()
        self.setup_timers_and_threads()
        
        self.apply_settings(self.settings)
        self.append_console("[A.D.A] Systems online. Ready to assist.")

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(6,6,6,6); root.setSpacing(8)
        title = TitleBar("A.D.A VISION INTERFACE 2.3", self.cycle_theme, self.toggle_console, self.fake_voice, self.open_settings)
        root.addWidget(title)
        self.bg_widget = AnimatedGridBackground(self.theme_key); self.bg_widget.setParent(central); self.bg_widget.lower()
        body = QGridLayout(); body.setSpacing(10); root.addLayout(body,1)
        
        # Left Side
        left_card=QFrame(); left_card.setStyleSheet("QFrame{background:rgba(10,14,20,220);border-radius:10px;}"); left_layout=QVBoxLayout(left_card); left_layout.setContentsMargins(8,8,8,8)
        left_layout.addWidget(SectionTitle("SYSTEM METRICS")); self.cpu_util=NeonBar("CPU UTILIZATION"); left_layout.addWidget(self.cpu_util)
        self.cpu_temp=NeonBar("CPU TEMPERATURE"); left_layout.addWidget(self.cpu_temp); self.battery=NeonBar("BATTERY"); left_layout.addWidget(self.battery)
        self.process_list=ProcessListWidget(); left_layout.addWidget(self.process_list,1); self.camera=CameraWidget(); left_layout.addWidget(self.camera,0); body.addWidget(left_card,0,0,2,1)
        
        # Center - Particle Network
        self.particle_core = ParticleNetworkCore(); body.addWidget(self.particle_core,0,1,2,1)

        # Right Side
        right_top=QFrame(); right_top.setStyleSheet("QFrame{background:rgba(10,14,20,220);border-radius:10px;}"); rt_layout=QVBoxLayout(right_top); rt_layout.setContentsMargins(8,8,8,8)
        rt_layout.addWidget(SectionTitle("STORAGE & NETWORK")); self.mem=NeonBar("MEMORY USAGE",style='pink'); rt_layout.addWidget(self.mem)
        self.disk=NeonBar("DISK USAGE",style='green'); rt_layout.addWidget(self.disk); self.weather=WeatherWidget(); rt_layout.addWidget(self.weather)
        net_box=QHBoxLayout(); self.net_up=QLabel("Up: 0.0 MB/s"); self.net_dn=QLabel("Down: 0.0 MB/s"); self.net_up.setStyleSheet("color:#DCECFB;"); self.net_dn.setStyleSheet("color:#DCECFB;")
        net_box.addWidget(self.net_up); net_box.addWidget(self.net_dn); rt_layout.addLayout(net_box)
        self.clockLbl=QLabel("--:--:--"); self.clockLbl.setStyleSheet("font-size:26px;color:#EAF6FF;"); self.clockLbl.setAlignment(Qt.AlignRight); rt_layout.addWidget(self.clockLbl)
        self.console=QTextEdit(); self.console.setReadOnly(True); self.console.setFixedHeight(180); self.console.hide(); rt_layout.addWidget(self.console); body.addWidget(right_top,0,2,1,1)

        right_bottom=QFrame(); rb_layout=QVBoxLayout(right_bottom); rb_layout.setContentsMargins(8,8,8,8); rb_layout.addWidget(SectionTitle("ACTIONS"))
        self.btn_cam_toggle=QPushButton("Start Camera"); self.btn_cam_toggle.clicked.connect(self.toggle_camera); self.btn_snapshot=QPushButton("Snapshot"); self.btn_snapshot.clicked.connect(self.camera_snapshot)
        self.btn_screenshot=QPushButton("HUD Screenshot"); self.btn_screenshot.clicked.connect(self.save_screenshot)
        for b in (self.btn_cam_toggle,self.btn_snapshot,self.btn_screenshot): b.setFixedHeight(34); rb_layout.addWidget(b)
        body.addWidget(right_bottom,1,2,1,1)

        body.setColumnStretch(0,1); body.setColumnStretch(1,2); body.setColumnStretch(2,1); body.setRowStretch(0,2); body.setRowStretch(1,1)

    def setup_timers_and_threads(self):
        self.anim_timer = QTimer(self); self.anim_timer.timeout.connect(self.particle_core.animate_step); self.anim_timer.start(16)
        self.clock_timer = QTimer(self); self.clock_timer.timeout.connect(self.tick); self.clock_timer.start(1000)

        self.thread = QThread()
        self.worker = SystemWorker()
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.stats_updated.connect(self.update_stats_ui)
        self.worker.network_updated.connect(self.update_network_ui)
        self.worker.processes_updated.connect(self.process_list.update_data)
        
        self.thread.start()

    def update_stats_ui(self, stats):
        self.cpu_util.setValue(stats['cpu']); self.mem.setValue(stats['mem']); self.disk.setValue(stats['disk'])
        self.cpu_temp.setValue(stats['temp']); self.battery.setValue(stats['batt'])

    def update_network_ui(self, net_stats):
        self.net_up.setText(f"Up: {net_stats['up']:.2f} MB/s")
        self.net_dn.setText(f"Down: {net_stats['dn']:.2f} MB/s")

    def tick(self):
        self.clockLbl.setText(datetime.now().strftime("%H:%M:%S"))
        if random.random() < 0.05:
            self.append_console("[A.D.A] " + random.choice(["Monitoring systems.","All subsystems nominal.","Network stable."]))

    def apply_settings(self, s):
        self.settings=s
        self.particle_core.set_speed(s['speed'])
        self.particle_core.set_particles(s['particle_count'])
        self.particle_core.set_connection_distance(s['connection_dist'])
        self.bg_widget.set_particles(s['bg_particles'])
        self.bg_widget.set_grid_spacing(s['grid_spacing'])
        self.bg_widget.set_grid_opacity(s['grid_opacity'])

    def open_settings(self):
        dlg = SettingsDialog(self, config=self.settings)
        if dlg.exec(): self.apply_settings(dlg.get_values()); self.append_console("[A.D.A] Settings applied.")

    def cycle_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEME_ORDER); self.theme_key = THEME_ORDER[self.theme_index]
        self.particle_core.set_theme(self.theme_key); self.bg_widget.set_theme(self.theme_key); self.append_console(f"[A.D.A] Theme set to {self.theme_key.upper()}.")

    def toggle_console(self):
        self.console.setVisible(not self.console.isVisible()); self.append_console(f"[A.D.A] Console {'visible' if self.console.isVisible() else 'hidden'}.")

    def fake_voice(self):
        self.append_console("[A.D.A] Voice mode activated — listening...")
        self.particle_core.set_speed(self.settings['speed']*2.5)
        QTimer.singleShot(2200, lambda: (self.particle_core.set_speed(self.settings['speed']), self.append_console("[A.D.A] Voice mode idle.")))

    def toggle_camera(self):
        self.camera_running = getattr(self.camera.capture, 'isOpened', lambda: False)()
        if not self.camera_running:
            if self.camera.start_camera(): self.btn_cam_toggle.setText("Stop Camera"); self.append_console("[A.D.A] Camera started.")
            else: QMessageBox.warning(self, "Camera", "Unable to start camera."); self.append_console("[A.D.A] Camera start failed.")
        else: self.camera.stop_camera(); self.btn_cam_toggle.setText("Start Camera"); self.append_console("[A.D.A] Camera stopped.")

    def camera_snapshot(self):
        if not getattr(self.camera.capture, 'isOpened', lambda: False)(): QMessageBox.information(self, "Snapshot", "Camera is not running."); return
        path, _ = QFileDialog.getSaveFileName(self, "Save Snapshot", f"snapshot_{safe_now_str()}.png", "PNG Files (*.png)")
        if path and self.camera.snapshot(path): self.append_console(f"[A.D.A] Snapshot saved."); QMessageBox.information(self, "Snapshot", "Saved.")
        elif path: self.append_console("[A.D.A] Snapshot failed."); QMessageBox.warning(self, "Snapshot", "Failed to save.")

    def save_screenshot(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save HUD Screenshot", f"hud_{safe_now_str()}.png", "PNG Files (*.png)")
        if path:
            try: self.grab().save(path); self.append_console(f"[A.D.A] Screenshot saved."); QMessageBox.information(self, "Screenshot", "Saved.")
            except Exception as e: self.append_console(f"[A.D.A] Screenshot failed: {e}"); QMessageBox.warning(self, "Screenshot", "Failed to save.")

    def resizeEvent(self, event): self.bg_widget.setGeometry(self.centralWidget().rect()); super().resizeEvent(event)
    def append_console(self, text): self.console.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")
    def closeEvent(self, event):
        self.append_console("[A.D.A] Shutting down...")
        self.camera.stop_camera()
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)

# --------------------- Run ---------------------
def main():
    app = QApplication(sys.argv)
    hud = NovaHUD()
    hud.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()