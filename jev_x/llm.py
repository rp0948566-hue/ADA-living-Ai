"""OpenAI-compatible chat client (llama.cpp, Ollama, LM Studio, vLLM, or a hosted API later)."""
import json, os, urllib.request, urllib.error

CONFIG_PATH = os.path.expanduser(os.environ.get('JEV_X_CONFIG', '~/.config/jev-x/config.json'))
DEFAULTS = {'base_url': 'http://127.0.0.1:8089/v1', 'api_key': '', 'model': 'local', 'max_tokens': 400, 'temperature': 0.3,
            'max_steps': 12, 'timeout': 600}
ENV = {'base_url': 'JEV_X_BASE_URL', 'api_key': 'JEV_X_API_KEY', 'model': 'JEV_X_MODEL'}


def load_config():
    """Defaults < config file < env vars. Switching to a hosted API later = change base_url/api_key/model only."""
    cfg = dict(DEFAULTS)
    try:
        with open(CONFIG_PATH) as f: cfg.update(json.load(f))
    except (OSError, ValueError): pass
    for k, e in ENV.items():
        if os.environ.get(e): cfg[k] = os.environ[e]
    return cfg


def chat(messages, tools, cfg):
    body = {'model': cfg['model'], 'messages': messages, 'max_tokens': cfg['max_tokens'], 'temperature': cfg['temperature']}
    if tools: body['tools'] = tools
    req = urllib.request.Request(cfg['base_url'].rstrip('/') + '/chat/completions', json.dumps(body).encode(),
                                 {'content-type': 'application/json', 'authorization': 'Bearer ' + (cfg['api_key'] or 'none')})
    try:
        with urllib.request.urlopen(req, timeout=cfg['timeout']) as r: return json.load(r)['choices'][0]['message']
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'model server HTTP {e.code}: {e.read().decode(errors="replace")[:300]}')
    except (urllib.error.URLError, OSError) as e:
        raise RuntimeError(f'cannot reach model server at {cfg["base_url"]}: {e}')
