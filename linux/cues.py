"""Sound cues, the counterpart of the Mac cue(): soundStart / soundRelease / soundDone / soundStop at "volume" (settings.json).
macOS system-sound names map to the freedesktop theme; "None" is silent. Played in the background by paplay/pw-play."""
import json, os, shutil, subprocess

DIR = '/usr/share/sounds/freedesktop/stereo'
MAP = {'Pop': 'message-new-instant', 'Bottle': 'audio-volume-change', 'Glass': 'complete', 'Tink': 'dialog-information',
       'Basso': 'dialog-error', 'Blow': 'bell', 'Frog': 'window-attention', 'Funk': 'dialog-warning', 'Hero': 'service-login',
       'Morse': 'window-question', 'Ping': 'message', 'Purr': 'device-added', 'Sosumi': 'suspend-error', 'Submarine': 'service-logout'}
DEFAULT = {'soundStart': 'Pop', 'soundRelease': 'Bottle', 'soundDone': 'Glass', 'soundStop': 'Tink'}


def prefs():
    for p in (os.environ.get('JEV_DIR'), os.path.expanduser('~/.config/jev')):
        try:
            with open(os.path.join(p, 'settings.json')) as f: return json.load(f)
        except (TypeError, OSError, ValueError): continue
    return {}


def play(name, volume):
    """Play one named sound at volume 0...1 (the Mac scale; 0.16 default). Returns the Popen or None."""
    f = os.path.join(DIR, MAP.get(name, name) + '.oga')
    if name == 'None' or not os.path.exists(f) or volume <= 0: return None
    for argv in (['paplay', f'--volume={int(min(1, volume) * 65536)}', f], ['pw-play', f'--volume={min(1, volume)}', f]):
        if shutil.which(argv[0]):
            return subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return None


def cue(key):
    p = prefs()
    return play(p.get(key, DEFAULT[key]), float(p.get('volume', 0.16)))


if __name__ == '__main__':
    import sys
    assert all(os.path.exists(os.path.join(DIR, v + '.oga')) for v in MAP.values()), 'missing theme sound'
    if sys.argv[1:]: play(sys.argv[1], float(sys.argv[2]) if sys.argv[2:] else .16).wait()
    print('cues ok')
