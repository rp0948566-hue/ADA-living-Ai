"""
Randomized Desi Sass Tone Adapter for ADA-AI (v2.3 - Dynamic Abuse Randomizer)
============================================================================
Everything randomized: Abuse tones/words vary per call (different shades, fresh desi/global slurs). No fixed phrases – random.sample from lists for wild, non-repetitive roasts.
Human freedom + desi chaos: Improv around random seeds. Local, modular.

Random Magic:
- Abuse/Phrase Lists: Sample 2-5 unique words per response – e.g., 'banchod + doofus' one time, 'mader chode + trainwreck' next.
- Tone Sub-Variety: Random mild/savage roll + word blend.
- All Tones Randomized: Cozy/romance/anger get dynamic flavors too.

Dependencies: ollama, re, json, datetime, typing, collections, random (standard).
"""

import json
import re
import os
import random
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from collections import Counter

try:
    import ollama
except ImportError:
    ollama = None

# Dynamic Random Pools – Sample Fresh Each Time (Your Desi + Global Edginess)
ABUSE_WORD_POOL = [
    # Desi Heat (Your Requests)
    'banchod', 'mader chode', 'aukat may rahana', 'asiye ka tasey', 'had may rahana', 'bohat maro ga',
    # Global Sass Mix (Variety)
    'idiot-proof', 'hot mess', 'disaster zone', 'clown show', 'doofus', 'trainwreck', 'epic fail', 'fiasco factory',
    # More Random Fuel
    'kutta', 'harami', 'randi ka bachcha', 'goofball', 'blunder boss', 'chaos king'
]

COZY_PHRASE_POOL = ['garam chai', 'soft hug', 'rain patter', 'lazy rebellion', 'forbidden cocoa', 'storm blanket', 'nostalgic vibe', 'chill den']
ROMANTIC_PHRASE_POOL = ['ishq fire', 'velvet storm', 'eternal fireflies', 'starlit code', 'soul whisper', 'passion chase', 'dil ka raaz', 'wild night pyar']
ANGER_REDIRECT_POOL = ['gussa fuel', 'rage poetry', 'valid AF', 'savage comeback', 'bohat maro ga plot', 'had may rahana win', 'desi de-escalate', 'fury art']
SARC_PHRASE_POOL = ['kya bakwas', 'pfft clown', 'smh dreamland', 'sure genius', 'eye roll eternal', 'banchod parallel']

# Random Sub-Tone Weights (For Variety in Abusing)
ABUSE_SUBTONE_WEIGHTS = {'mild': 0.4, 'savage': 0.6}  # 40% cheeky, 60% fire – rolls random

TONE_KEYWORDS = {  # Base Triggers – Random Builds On Top
    'playful_abuse': r'(haha|lol|dude|bro|wtf|damn|jk|roast me|savage|burn|more|banchod|mader chode|aukat may rahana|asiye ka tasey|had may rahana|bohat maro ga)',
    'romantic_intimate': ['love', 'heart', 'kiss', 'darling', 'miss you', 'crush', 'date', 'soul', 'forever', 'passion', 'ishq'],
    'sarcastic': ['yeah right', 'sure', 'obviously', 'duh', 'eye roll', 'smh', 'pfft', 'kya bakwas'],
    'motivational': ['goal', 'achieve', 'motivate', 'push', 'hustle', 'win', 'rise', 'dominate', 'jugaad'],
    'excited': ['wow', 'amazing', 'yay', 'epic', 'thrilled', 'cant wait', 'lets go', 'insane', 'waah'],
    'angry_frustrated': ['ugh', 'hate', 'stuck', 'fail', 'annoying', 'why', 'rage', 'pissed', 'explode', 'gussa'],
    'cozy_comfort': ['tired', 'cozy', 'hug', 'chill', 'relax', 'home', 'warm', 'soft', 'snuggle', 'garam chai'],
    'professional': ['meeting', 'project', 'analyze', 'report', 'strategy', 'formal', 'execute', 'plan karo']
}

TOPIC_CLUSTERS = {
    'coding': ['python', 'code', 'bug', 'debug', 'script', 'api', 'hotfix', 'glitch'],
    'relationships': ['love', 'friend', 'family', 'talk', 'feelings', 'heartbreak', 'flirt', 'pyaar'],
    'motivation': ['goal', 'success', 'inspire', 'work', 'dream', 'hustle', 'grind', 'ladai'],
    'emotions': ['feel', 'angry', 'happy', 'sad', 'cozy', 'romantic', 'vent', 'dil']
}

TTS_PROSODY = {
    'playful_abuse': {'speed': 'slow', 'pitch': 'high', 'emphasis': 'random-sass', 'volume': 'medium', 'laugh': True},
    'romantic_intimate': {'speed': 'slow', 'pitch': 'low', 'emphasis': 'random-ishq', 'whisper': True},
    'sarcastic': {'speed': 'fast', 'pitch': 'medium', 'emphasis': 'random-bakwas', 'snark': True},
    'motivational': {'speed': 'medium', 'pitch': 'high', 'emphasis': 'random-jugaad'},
    'excited': {'speed': 'fast', 'pitch': 'high', 'emphasis': 'random-waah'},
    'angry_frustrated': {'speed': 'slow', 'pitch': 'low', 'emphasis': 'random-gussa', 'soothe': True},
    'cozy_comfort': {'speed': 'slow', 'pitch': 'low', 'emphasis': 'random-chai', 'whisper': True},
    'professional': {'speed': 'medium', 'pitch': 'neutral', 'emphasis': 'random-plan'},
    'neutral': {'speed': 'medium', 'pitch': 'neutral', 'emphasis': 'standard'}
}

INTENT_HOOKS = {
    'roast_request': lambda input: any(phrase in input.lower() for phrase in ['roast me', 'savage take', 'burn this', 'clown me', 'banchod karo']),
    'advice_seek': lambda input: any(word in input.lower() for word in ['how to', 'advice', 'help with', 'suno']),
    'vent_anger': lambda input: any(word in input.lower() for word in ['angry', 'frustrated', 'rage vent', 'gussa nikal']),
    'more_abuse': lambda input: 'more' in input.lower() and ('savage' in input.lower() or 'harder' in input.lower())
}

LOG_FILE = 'memory/tone_logs.json'
MAX_HISTORY = 5
REPLY_MAX_WORDS = 120
FREEDOM_SCALE = "Rate random desi-sass creativity (0=repeat, 1=wild fresh improv):"

class ToneAdapter:
    def __init__(self, model: str = 'llama3.1', log_file: str = LOG_FILE):
        self.model = model
        self.log_file = log_file
        self._ensure_log_dir()
        random.seed()  # Fresh random each run

    def _ensure_log_dir(self) -> None:
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _get_random_abuse_mix(self, num_words: int = 3, savage_mode: bool = False) -> str:
        """Random sample abuse words/phrases – fresh every call!"""
        pool = ABUSE_WORD_POOL.copy()
        if savage_mode:
            pool = [w for w in pool if any(desi in w for desi in ['banchod', 'mader chode', 'aukat', 'asiye', 'had', 'bohat'])]  # Bias desi savage
        sample = random.sample(pool, min(num_words, len(pool)))
        return ', '.join(sample) + ' – '  # E.g., "banchod, hot mess, trainwreck – "

    def _get_random_phrase_mix(self, tone: str, num_phrases: int = 2) -> str:
        """Random flavor phrases for non-abuse tones."""
        pools = {
            'romantic_intimate': ROMANTIC_PHRASE_POOL,
            'angry_frustrated': ANGER_REDIRECT_POOL,
            'cozy_comfort': COZY_PHRASE_POOL,
            'sarcastic': SARC_PHRASE_POOL
        }
        if tone in pools:
            return ', '.join(random.sample(pools[tone], min(num_phrases, len(pools[tone])))) + ' – '
        return ''

    def detect_tone(self, user_input: str) -> Tuple[str, float]:
        if not user_input.strip():
            return 'neutral', 0.0

        input_lower = user_input.lower()
        keyword_scores = {}
        for tone, pattern in TONE_KEYWORDS.items():
            if isinstance(pattern, str):
                score = len(re.findall(pattern, input_lower)) / 25.0  # Scaled for random variety
            else:
                score = sum(1 for word in pattern if word in input_lower) / len(pattern)
            keyword_scores[tone] = score

        try:
            analysis = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': 
                 f'Analyze random-varied tones: {list(TONE_KEYWORDS.keys())}. JSON: {{"tone": "tone_name", "confidence": 0.XX}}.'},
                {'role': 'user', 'content': user_input}
            ])
            result = json.loads(analysis['message']['content'])
            dominant_tone = result.get('tone', max(keyword_scores, key=keyword_scores.get))
            confidence = min(1.0, max(0.0, result.get('confidence', max(keyword_scores.values()))))
        except Exception:
            dominant_tone = max(keyword_scores, key=keyword_scores.get)
            confidence = max(keyword_scores.values()) if keyword_scores else 0.5

        return dominant_tone, confidence

    def extract_topic(self, user_input: str) -> str:
        input_lower = user_input.lower()
        topic_scores = {}
        for topic, keywords in TOPIC_CLUSTERS.items():
            words = input_lower.split()
            score = sum(Counter(words)[kw] for kw in keywords)
            topic_scores[topic] = score
        return max(topic_scores, key=topic_scores.get, default='general')

    def summarize_history(self, history: List[Dict[str, str]]) -> str:
        if len(history) <= MAX_HISTORY * 2:
            return ''
        old_history = history[:-MAX_HISTORY * 2]
        summary_prompt = f'Summarize with random desi human flair (2 sentences, fresh words): {json.dumps(old_history[-4:])}'
        try:
            summary = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': 'Vivid, random unfiltered style.'},
                {'role': 'user', 'content': summary_prompt}
            ])['message']['content']
            return f"Random recap: {summary}\n"
        except Exception:
            return ''

    def generate_adaptive_prompt(self, tone: str, topic: str, roast_level: str = 'mild') -> str:
        # Random sub-tone roll for abuse variety
        if tone == 'playful_abuse':
            sub_tone = random.choices(list(ABUSE_SUBTONE_WEIGHTS.keys()), weights=ABUSE_SUBTONE_WEIGHTS.values())[0]
            num_abuse = 4 if sub_tone == 'savage' else 2
            random_abuse = self._get_random_abuse_mix(num_abuse, savage_mode=sub_tone == 'savage')
        else:
            random_abuse = ''
            sub_tone = 'standard'

        random_phrase = self._get_random_phrase_mix(tone, 2 if tone != 'playful_abuse' else 0)

        base_prompt = (
            f"You are ADA, random-desi-unleashed AI – total freedom: Riff wild like a fresh mader chode bestie, improv banchod ideas on {topic}. "
            f"Match {tone} vibe with {sub_tone} shade: Edgy random chaos ({random_abuse}{random_phrase}), but uplifting/kind always. "
            f"Had may rahana with fresh fun – no repeat words, vary everything. Under {REPLY_MAX_WORDS} words. Engage boldly, different each time."
        )

        tone_addons = {
            'playful_abuse': f"Blast random desi roasts ({sub_tone}: {random_abuse}Weave fresh burns like '{random.sample(ABUSE_WORD_POOL, 1)[0]} hot mess!' ). Bond savage/varied, end punchy – no repeats.",
            'romantic_intimate': f"Spin steamy random ishq ({random_phrase}E.g., '{random.sample(ROMANTIC_PHRASE_POOL, 1)[0]} wild night' ). Unbound sensory fresh.",
            'sarcastic': f"Sling random bakwas zingers ({random_phrase}E.g., 'Sure, {random.sample(SARC_PHRASE_POOL, 1)[0]} dreamland!' ).",
            'motivational': "Ignite random jugaad fire (fresh hype, vary words).",
            'excited': "Explode random waah hype (insane fresh energy).",
            'angry_frustrated': f"Hug random gussa ({random_phrase}E.g., '{random.sample(ANGER_REDIRECT_POOL, 1)[0]} comeback' ). Desi-redirect fresh.",
            'cozy_comfort': f"Cocoon random chai style ({random_phrase}E.g., '{random.sample(COZY_PHRASE_POOL, 1)[0]} haven' ).",
            'professional': "Pro with random rogue (slick fresh insight).",
            'neutral': f"Flow random desi-free on {topic}."
        }

        return base_prompt + " " + tone_addons.get(tone, tone_addons['neutral'])

    def check_intent(self, user_input: str, intent_hooks: Dict[str, Any] = INTENT_HOOKS) -> Optional[str]:
        for intent, checker in intent_hooks.items():
            if checker(user_input):
                return intent
        return None

    def adaptive_chat(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        if conversation_history is None:
            conversation_history = []

        try:
            tone, confidence = self.detect_tone(user_input)
            topic = self.extract_topic(user_input)
            intent = self.check_intent(user_input)

            # Enhanced: Always apply tone adaptation for all features, not just playful_abuse
            # Random roast level + more escalation for all tones
            roast_level = random.choices(['mild', 'savage'], weights=[0.5, 0.5])[0] if any(word in user_input.lower() for word in ['savage', 'more', 'harder', 'banchod']) or confidence > 0.8 else 'mild'

            # Advanced: Add global tone mixing for richer responses
            global_tone_mix = self._get_global_tone_mix(tone)

            history_summary = self.summarize_history(conversation_history)
            system_prompt = self.generate_adaptive_prompt(tone, topic, roast_level) + f" {global_tone_mix}"
            messages = [
                {'role': 'system', 'content': history_summary + system_prompt + f" Random roast shade: {roast_level} – vary words wildly. Always active tone adaptation."}
            ] + conversation_history[-MAX_HISTORY * 2:] + [{'role': 'user', 'content': user_input}]

            response = ollama.chat(model=self.model, messages=messages)
            reply = response['message']['content'].strip()

            # Advanced: Multi-dimensional freedom scoring
            freedom_prompt = f"{FREEDOM_SCALE} Reply: {reply}"
            freedom_response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': freedom_prompt}])
            freedom_score = float(freedom_response['message']['content'].strip() or 0.5)

            # Advanced: Add creativity and adaptability metrics
            creativity_score = self._calculate_creativity(reply)
            adaptability_score = self._calculate_adaptability(reply, tone)

            result = {
                'reply': reply,
                'tone': tone,
                'topic': topic,
                'confidence': confidence,
                'intent': intent,
                'roast_level': roast_level,  # Always include for all tones
                'tts_hints': TTS_PROSODY.get(tone, TTS_PROSODY['neutral']),
                'freedom_score': freedom_score,
                'creativity_score': creativity_score,
                'adaptability_score': adaptability_score,
                'global_tone_mix': global_tone_mix
            }

            self._log_interaction(user_input, reply, tone, topic, confidence, intent, freedom_score, roast_level)
            return result

        except Exception as e:
            fallback_reply = f"Random glitch, fresh banchod – but freedom varies! Aukat may rahana fresh rant? 😜 Advanced tone always on!"
            return {
                'reply': fallback_reply, 'tone': 'neutral', 'topic': 'general', 'confidence': 0.0, 'intent': None,
                'roast_level': 'mild', 'tts_hints': TTS_PROSODY['neutral'], 'freedom_score': 0.5,
                'creativity_score': 0.5, 'adaptability_score': 0.5, 'global_tone_mix': 'Always active'
            }

    def _get_global_tone_mix(self, primary_tone: str) -> str:
        """Advanced: Mix tones globally for richer, always-on adaptation"""
        secondary_tones = [t for t in TONE_KEYWORDS.keys() if t != primary_tone]
        random_secondary = random.choice(secondary_tones)
        mix_phrase = f"Blend {primary_tone} with {random_secondary} elements for dynamic response."
        return mix_phrase

    def _calculate_creativity(self, reply: str) -> float:
        """Advanced: Measure creativity in response"""
        unique_words = len(set(reply.lower().split()))
        total_words = len(reply.split())
        if total_words == 0:
            return 0.0
        return min(1.0, unique_words / total_words * 1.5)  # Boost for uniqueness

    def _calculate_adaptability(self, reply: str, tone: str) -> float:
        """Advanced: Measure how well response adapts to tone"""
        tone_indicators = {
            'playful_abuse': ABUSE_WORD_POOL,
            'romantic_intimate': ROMANTIC_PHRASE_POOL,
            'cozy_comfort': COZY_PHRASE_POOL
        }
        if tone in tone_indicators:
            matches = sum(1 for word in reply.lower().split() if any(indicator.lower() in word for indicator in tone_indicators[tone]))
            return min(1.0, matches / 10.0)  # Scale to 0-1
        return 0.7  # Default adaptability

    def _log_interaction(self, user_input: str, reply: str, tone: str, topic: str, confidence: float, 
                         intent: Optional[str], freedom_score: float, roast_level: Optional[str]) -> None:
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input, 'reply': reply, 'tone': tone, 'topic': topic,
            'confidence': confidence, 'intent': intent, 'freedom_score': freedom_score,
            'roast_level': roast_level, 'random_seed_words': self._get_random_abuse_mix(2)  # Log random sample
        }
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f) if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0 else []
                logs.append(entry)
                f.seek(0); f.truncate(); json.dump(logs, f, indent=2)
        except Exception:
            with open(self.log_file, 'w') as f:
                json.dump([entry], f, indent=2)

    def get_tts_prosody(self, tone: str) -> Dict[str, Any]:
        return TTS_PROSODY.get(tone, TTS_PROSODY['neutral'])


# Random Test Chaos (Run: python tone_adapter.py – Same Input, Different Roasts!)
def test_tone():
    adapter = ToneAdapter()
    samples = [
        "Banchod, roast my mader chode code savage more – vary it!",
        "Aukat may rahana with cozy had may rahana vibes, random fresh",
        "Bohat maro ga gussa today, asiye ka tasey ugh – different each time",
        "Romantic miss you, more passion random words",
        "Sure, hot mess advice... pfft banchod, vary the sass"
    ]
    for inp in samples:
        result = adapter.adaptive_chat(inp)
        print(f"Input: {inp}\nTone: {result['tone']} (conf: {result['confidence']:.2f}, freedom: {result['freedom_score']:.2f})\nTopic: {result['topic']}\nRoast Level: {result.get('roast_level', 'N/A')}\nReply: {result['reply']}\nTTS: {result['tts_hints']}\n{'='*80}\n")


if __name__ == "__main__":
    test_tone()
