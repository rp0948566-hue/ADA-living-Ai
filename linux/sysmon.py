"""Live system info without the model spending tokens on it: `sysinfo` prints one short block, and host.py runs watch() in the
background and alerts (desktop notification, spoken if "speak" is on) when the machine is overloaded or hot."""
import os, shutil, subprocess, time
import psutil

# alert when over these, held for HOLD seconds (a brief spike is normal)
LIMITS = {'cpu': 90, 'ram': 90, 'swap': 80, 'disk': 95, 'cpu_temp': 90, 'gpu_temp': 85, 'gpu_mem': 97}
HOLD, AGAIN = 30, 600   # seconds over the limit before an alert; seconds before the same alert repeats


def gpu():
    if not shutil.which('nvidia-smi'): return None
    try:
        r = subprocess.run(['nvidia-smi', '--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total',
                            '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=5)
        name, util, temp, used, total = [x.strip() for x in r.stdout.splitlines()[0].split(',')]
        return {'name': name, 'util': float(util), 'temp': float(temp), 'mem': 100 * float(used) / max(1, float(total)), 'used': float(used), 'total': float(total)}
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired): return None


def cpu_temp():
    t = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
    for key in ('coretemp', 'k10temp', 'zenpower', 'acpitz', 'thinkpad'):
        if t.get(key): return max(x.current for x in t[key])
    return max((x.current for v in t.values() for x in v), default=None)


def snapshot(cpu_interval=0.5):
    vm, sw, du = psutil.virtual_memory(), psutil.swap_memory(), psutil.disk_usage(os.path.expanduser('~'))
    s = {'cpu': psutil.cpu_percent(interval=cpu_interval), 'load': os.getloadavg(), 'cores': psutil.cpu_count(),
         'ram': vm.percent, 'ram_used': vm.used / 2**30, 'ram_total': vm.total / 2**30, 'swap': sw.percent,
         'disk': du.percent, 'disk_free': du.free / 2**30, 'cpu_temp': cpu_temp(), 'gpu': gpu()}
    b = psutil.sensors_battery() if hasattr(psutil, 'sensors_battery') else None
    s['battery'] = (b.percent, b.power_plugged) if b else None
    return s


def top(n=3):
    procs = [p.info for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])]
    time.sleep(0.3)
    procs = [p.info for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])]
    return sorted(procs, key=lambda p: (p['cpu_percent'] or 0) + (p['memory_percent'] or 0), reverse=True)[:n]


def text(s=None):
    s = s or snapshot()
    g = s['gpu']
    lines = [f"CPU {s['cpu']:.0f}% (load {s['load'][0]:.1f} on {s['cores']} cores)" + (f", {s['cpu_temp']:.0f}°C" if s['cpu_temp'] else ''),
             f"RAM {s['ram']:.0f}% ({s['ram_used']:.1f}/{s['ram_total']:.1f} GB), swap {s['swap']:.0f}%",
             f"Disk (home) {s['disk']:.0f}% used, {s['disk_free']:.0f} GB free"]
    if g: lines.append(f"GPU {g['name']}: {g['util']:.0f}%, {g['temp']:.0f}°C, memory {g['used']/1024:.1f}/{g['total']/1024:.1f} GB")
    if s['battery']: lines.append(f"Battery {s['battery'][0]:.0f}%" + (' charging' if s['battery'][1] else ' on battery'))
    lines.append('Busiest: ' + ', '.join(f"{p['name']} ({p['cpu_percent']:.0f}% CPU, {p['memory_percent']:.0f}% RAM)" for p in top()))
    warn = problems(s)
    return '\n'.join(lines + ([f'⚠️ {w}' for w in warn.values()] if warn else []))


def problems(s):
    g, out = s['gpu'] or {}, {}
    if s['cpu'] > LIMITS['cpu']: out['cpu'] = f"CPU is at {s['cpu']:.0f}%"
    if s['ram'] > LIMITS['ram']: out['ram'] = f"Memory is almost full ({s['ram']:.0f}%)"
    if s['swap'] > LIMITS['swap']: out['swap'] = f"Swap is {s['swap']:.0f}% used: the system may slow down"
    if s['disk'] > LIMITS['disk']: out['disk'] = f"Disk is almost full ({s['disk_free']:.1f} GB free)"
    if (s['cpu_temp'] or 0) > LIMITS['cpu_temp']: out['cpu_temp'] = f"CPU is hot: {s['cpu_temp']:.0f}°C"
    if g.get('temp', 0) > LIMITS['gpu_temp']: out['gpu_temp'] = f"GPU is hot: {g['temp']:.0f}°C"
    if g.get('mem', 0) > LIMITS['gpu_mem']: out['gpu_mem'] = f"GPU memory is full ({g['mem']:.0f}%)"
    if s['battery'] and s['battery'][0] < 15 and not s['battery'][1]: out['battery'] = f"Battery low: {s['battery'][0]:.0f}%"
    return out


def watch(alert, every=10, stop=lambda: False):
    """Calls alert(message) when a problem has held for HOLD seconds; the same problem again only after AGAIN seconds."""
    since, said = {}, {}
    while not stop():
        try: now, bad = time.time(), problems(snapshot(cpu_interval=1))
        except Exception: bad, now = {}, time.time()
        for k in list(since):
            if k not in bad: since.pop(k)
        for k, msg in bad.items():
            since.setdefault(k, now)
            if (now - since[k] >= HOLD or k in ('disk', 'battery')) and now - said.get(k, 0) >= AGAIN:
                said[k] = now; alert(msg)
        time.sleep(every)


if __name__ == '__main__':   # self-check: the limits fire on a made-up overloaded machine
    hot = {'cpu': 99, 'ram': 95, 'swap': 0, 'disk': 50, 'disk_free': 100, 'cpu_temp': 97, 'gpu': {'temp': 60, 'mem': 50}, 'battery': (10, False)}
    assert set(problems(hot)) == {'cpu', 'ram', 'cpu_temp', 'battery'}, problems(hot)
    print(text())
