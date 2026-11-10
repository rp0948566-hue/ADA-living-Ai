"""Picks a voice-model tier from the machine Jev is running on, so one build works on an old laptop and a strong one.
Pure functions over read-only local facts (core count, RAM, GPU) -- no network, nothing sent anywhere.
`tier.py` alone on the command line prints the detected tier for a quick check."""
import os, re, shutil, subprocess

TIERS = {
    0: {'name': 'light',    'whisper': 'tiny',           'whisper_device': 'cpu', 'piper': 'low',    'both_warm': False},
    1: {'name': 'standard', 'whisper': 'base',           'whisper_device': 'cpu', 'piper': 'medium', 'both_warm': False},
    2: {'name': 'balanced', 'whisper': 'small',          'whisper_device': 'cpu', 'piper': 'medium', 'both_warm': True},
    3: {'name': 'max',      'whisper': 'large-v3-turbo', 'whisper_device': 'cuda','piper': 'medium', 'both_warm': True},
}


def cpu_count():
    return os.cpu_count() or 2


def mem_gb():
    try:
        with open('/proc/meminfo') as f:
            kb = int(re.search(r'MemTotal:\s*(\d+)', f.read())[1])
        return kb / 1024 / 1024
    except (OSError, TypeError, ValueError):
        return 4.0   # unknown: assume a modest machine rather than overcommit


def has_avx2():
    try:
        return 'avx2' in open('/proc/cpuinfo').read()
    except OSError:
        return False


def gpu_vram_gb():
    """NVIDIA VRAM in GB, or 0 if there is none or nvidia-smi isn't installed."""
    if not shutil.which('nvidia-smi'):
        return 0
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'],
                              capture_output=True, text=True, timeout=5).stdout.strip().splitlines()
        return max((float(x) for x in out), default=0) / 1024
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0


def choose_tier(cores=None, ram_gb=None, avx2=None, vram_gb=None):
    """The tier table in the plan: weak machines get the small models and only one loaded at a time;
    a real NVIDIA GPU gets the big accurate ear. Explicit args are for tests and the JEV_TIER override."""
    cores = cpu_count() if cores is None else cores
    ram_gb = mem_gb() if ram_gb is None else ram_gb
    avx2 = has_avx2() if avx2 is None else avx2
    vram_gb = gpu_vram_gb() if vram_gb is None else vram_gb
    if vram_gb >= 6:
        return 3
    if cores <= 2 or ram_gb <= 4 or not avx2:
        return 0
    if cores < 8 or ram_gb < 16:
        return 1
    return 2


def current_tier():
    """JEV_TIER=0..3 forces a tier (benchmarking, Settings override); otherwise probe the machine."""
    forced = os.environ.get('JEV_TIER')
    if forced and forced.isdigit() and int(forced) in TIERS:
        return int(forced)
    return choose_tier()


def profile():
    return TIERS[current_tier()]


if __name__ == '__main__':
    t = current_tier()
    print(t, TIERS[t]['name'], f'cores={cpu_count()} ram={mem_gb():.1f}GB avx2={has_avx2()} vram={gpu_vram_gb():.1f}GB')
