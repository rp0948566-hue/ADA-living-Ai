"""The agent loop: model -> tool calls -> results -> model, until done."""
import json, platform
from . import llm, tools

SYSTEM = ('You are Jev-X, an agent with full control of the user\'s {os} computer. Do the task with tools, '
          'one step at a time, then call done with a short answer. Prefer shell for files/apps/system work; '
          'use click/type/key only when a GUI is needed. Screen is text-only for you: use windows and shell to inspect. '
          'Be brief.')
KEEP = 14   # messages kept besides the system prompt; small contexts overflow otherwise


def _window(msgs):
    w = msgs[-KEEP:]
    while len(w) > 1 and w[0]['role'] == 'tool': w = w[1:]   # never start on an orphan tool result
    return w


def run(task, cfg=None, on_event=print, history=None):
    cfg = cfg or llm.load_config()
    msgs = (history or []) + [{'role': 'user', 'content': task}]
    sysmsg = {'role': 'system', 'content': SYSTEM.format(os=platform.system())}
    for _ in range(cfg['max_steps']):
        msg = llm.chat([sysmsg] + _window(msgs), tools.SCHEMAS, cfg)
        calls = msg.get('tool_calls') or []
        msgs.append({'role': 'assistant', 'content': msg.get('content') or '', **({'tool_calls': calls} if calls else {})})
        if not calls:
            return msg.get('content') or '', msgs
        for c in calls:
            fn = c['function']; name = fn['name']
            try: args = json.loads(fn.get('arguments') or '{}')
            except ValueError: args = {}
            on_event(f'→ {name} {json.dumps(args, ensure_ascii=False)[:200]}')
            if name == 'done':
                return str(args.get('answer', '')), msgs
            out = tools.call(name, args)
            on_event(f'  {out[:200]}')
            msgs.append({'role': 'tool', 'tool_call_id': c.get('id', ''), 'content': out})
    return 'stopped: step limit reached', msgs
