#!/usr/bin/env python3
"""Talk to Jev from your phone through a Telegram bot. Settings: telegramToken (from @BotFather) and telegramChat (your chat number;
the bot tells you it on your first message). Only that one chat is answered; everyone else gets silence.
Requests from here run with JEV_REMOTE=1, so Jev only looks and answers: nothing is changed, sent, bought or deleted from the phone.
shortcut: text messages only, one at a time; upgrade to voice notes and files when someone needs them."""
import json, os, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.realpath(__file__))


def prefs():
    try:
        with open(os.path.join(os.environ.get('JEV_DIR') or os.path.expanduser('~/.config/jev'), 'settings.json')) as f: return json.load(f)
    except (OSError, ValueError): return {}


def api(token, method, **params):
    request = urllib.request.Request(f'https://api.telegram.org/bot{token}/{method}', json.dumps(params).encode(), {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=70) as r: return json.load(r).get('result')


def run(text):
    try:
        done = subprocess.run([sys.executable, os.path.join(HERE, 'jev.py'), text], env=dict(os.environ, JEV_REMOTE='1'), capture_output=True, text=True, timeout=600)
        return done.stdout.strip() or 'Done, with nothing to show.'
    except subprocess.TimeoutExpired: return 'That took more than 10 minutes, so I stopped.'


def reply_to(update, chat, run=run):
    """-> (chat id, text) to send back, or None. Unpaired: tell the sender their chat number. Paired: only the owner's chat is answered."""
    message = update.get('message') or {}
    text, sender = str(message.get('text') or '').strip(), str((message.get('chat') or {}).get('id', ''))
    if not text or not sender: return None
    if not chat: return sender, f'Your chat number is {sender}. Enter it in Jev Settings under Phone, then message me again.'
    if sender != str(chat).strip(): return None
    return sender, run(text)[:4000]


def main():
    offset = 0
    while os.getppid() != 1:   # stop when the app that started this is gone
        p = prefs(); token = str(p.get('telegramToken') or '').strip()
        if not token: time.sleep(30); continue
        try:
            for update in api(token, 'getUpdates', offset=offset, timeout=50) or []:
                offset = update['update_id'] + 1
                answer = reply_to(update, p.get('telegramChat'))
                if answer: api(token, 'sendMessage', chat_id=answer[0], text=answer[1])
        except Exception: time.sleep(15)   # offline or a bad token: wait and try again


if __name__ == '__main__':
    main()
