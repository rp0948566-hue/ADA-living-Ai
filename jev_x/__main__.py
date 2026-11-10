"""python -m jev_x [task...] | --doctor | --serve [port]"""
import json, sys
from . import agent, llm, osctl, web


def doctor():
    cfg = llm.load_config()
    print(json.dumps(osctl.capabilities(), indent=1))
    try:
        r = llm.chat([{'role': 'user', 'content': 'Say ok'}], None, {**cfg, 'max_tokens': 5})
        print('model server OK:', cfg['base_url'], '->', repr(r.get('content')))
    except RuntimeError as e:
        print('model server FAIL:', e); return 1
    return 0


def main(argv):
    if argv[:1] == ['--doctor']: return doctor()
    if argv[:1] == ['--serve']: return web.serve(int(argv[1]) if len(argv) > 1 else 7777)
    hist = []
    if argv:
        print(agent.run(' '.join(argv))[0]); return 0
    print('Jev-X. Type a task, Ctrl-D to quit.')
    while True:
        try: task = input('> ').strip()
        except EOFError: return 0
        if task:
            try: ans, hist = agent.run(task, history=hist)
            except RuntimeError as e: ans = f'error: {e}'
            print(ans)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
