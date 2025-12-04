# -*- coding: utf-8 -*-
"""
ABCD.py - AI LEARNING KNOWLEDGE BASE
Hindi-English Bilingual Educational Format for AI Learning

This file contains structured learning data for AI to understand:
  - Alphabet (ABCD & Devanagari)
  - Numbers & Mathematical Tables
  - Grammar Rules & Word Formation
  - Hindi-English Translation
  - Spelling & Silent Letters
  - Color Names & Human Tones
  - Word Breaking & Reconstruction
"""

# ============================================================================
# SECTION 1: ALPHABET & CHARACTER LEARNING (ABCD & DEVANAGARI)
# ============================================================================

ENGLISH_ALPHABET = {
    "uppercase": {
        "A": {"english": "Aay", "hindi": "अ", "sound": "aa", "example": "Apple"},
        "B": {"english": "Bee", "hindi": "ब", "sound": "b", "example": "Ball"},
        "C": {"english": "See", "hindi": "क", "sound": "k/s", "example": "Cat"},
        "D": {"english": "Dee", "hindi": "द", "sound": "d", "example": "Dog"},
        "E": {"english": "Ee", "hindi": "इ", "sound": "e", "example": "Egg"},
        "F": {"english": "Eff", "hindi": "फ", "sound": "f", "example": "Fish"},
        "G": {"english": "Gee", "hindi": "ग", "sound": "g", "example": "Goat"},
        "H": {"english": "Aitch", "hindi": "ह", "sound": "h", "example": "House"},
        "I": {"english": "Eye", "hindi": "ई", "sound": "i", "example": "Ice"},
        "J": {"english": "Jay", "hindi": "ज", "sound": "j", "example": "Jar"},
        "K": {"english": "Kay", "hindi": "क", "sound": "k", "example": "Kite"},
        "L": {"english": "Ell", "hindi": "ल", "sound": "l", "example": "Lion"},
        "M": {"english": "Em", "hindi": "म", "sound": "m", "example": "Moon"},
        "N": {"english": "En", "hindi": "न", "sound": "n", "example": "Nest"},
        "O": {"english": "Oh", "hindi": "ओ", "sound": "o", "example": "Orange"},
        "P": {"english": "Pee", "hindi": "प", "sound": "p", "example": "Pen"},
        "Q": {"english": "Cue", "hindi": "क्व", "sound": "kw", "example": "Queen"},
        "R": {"english": "Arr", "hindi": "र", "sound": "r", "example": "Rose"},
        "S": {"english": "Ess", "hindi": "स", "sound": "s", "example": "Sun"},
        "T": {"english": "Tee", "hindi": "त", "sound": "t", "example": "Tiger"},
        "U": {"english": "You", "hindi": "उ", "sound": "u", "example": "Umbrella"},
        "V": {"english": "Vee", "hindi": "व", "sound": "v", "example": "Van"},
        "W": {"english": "Double-You", "hindi": "व", "sound": "w", "example": "Water"},
        "X": {"english": "Ex", "hindi": "क्स", "sound": "x", "example": "Xray"},
        "Y": {"english": "Why", "hindi": "य", "sound": "y", "example": "Yak"},
        "Z": {"english": "Zee", "hindi": "ज़", "sound": "z", "example": "Zebra"},
    }
}

# Hindi Devanagari Alphabet (Varnamala)
HINDI_DEVANAGARI = {
    "vowels": {
        "अ": {"english": "A", "sound": "a", "word": "अमर", "english_word": "Immortal"},
        "आ": {"english": "AA", "sound": "aa", "word": "आम", "english_word": "Mango"},
        "इ": {"english": "I", "sound": "i", "word": "इंद्र", "english_word": "Indra"},
        "ई": {"english": "II", "sound": "ee", "word": "ईश्वर", "english_word": "God"},
        "उ": {"english": "U", "sound": "u", "word": "उपहार", "english_word": "Gift"},
        "ऊ": {"english": "UU", "sound": "oo", "word": "ऊंट", "english_word": "Camel"},
        "ऋ": {"english": "RI", "sound": "ri", "word": "ऋषि", "english_word": "Sage"},
        "ए": {"english": "E", "sound": "e", "word": "एक", "english_word": "One"},
        "ऐ": {"english": "AI", "sound": "ai", "word": "ऐतिहास", "english_word": "History"},
        "ओ": {"english": "O", "sound": "o", "word": "ओषधि", "english_word": "Medicine"},
        "औ": {"english": "AU", "sound": "au", "word": "औरत", "english_word": "Woman"},
    },
    "consonants": {
        "क": {"english": "KA", "sound": "ka", "word": "कमल", "english_word": "Lotus"},
        "ख": {"english": "KHA", "sound": "kha", "word": "खरगोश", "english_word": "Rabbit"},
        "ग": {"english": "GA", "sound": "ga", "word": "गीत", "english_word": "Song"},
        "घ": {"english": "GHA", "sound": "gha", "word": "घर", "english_word": "House"},
        "च": {"english": "CHA", "sound": "cha", "word": "चाँद", "english_word": "Moon"},
        "छ": {"english": "CHHA", "sound": "chha", "word": "छत्र", "english_word": "Umbrella"},
        "ज": {"english": "JA", "sound": "ja", "word": "जल", "english_word": "Water"},
        "झ": {"english": "JHA", "sound": "jha", "word": "झील", "english_word": "Lake"},
        "ट": {"english": "TA", "sound": "ta", "word": "टोपी", "english_word": "Hat"},
        "ठ": {"english": "THA", "sound": "tha", "word": "ठंड", "english_word": "Cold"},
        "ड": {"english": "DA", "sound": "da", "word": "डाक", "english_word": "Mail"},
        "ढ": {"english": "DHA", "sound": "dha", "word": "ढेर", "english_word": "Heap"},
        "त": {"english": "TA", "sound": "ta", "word": "तारा", "english_word": "Star"},
        "थ": {"english": "THA", "sound": "tha", "word": "थाली", "english_word": "Plate"},
        "द": {"english": "DA", "sound": "da", "word": "दर्पण", "english_word": "Mirror"},
        "ध": {"english": "DHA", "sound": "dha", "word": "धन", "english_word": "Money"},
        "प": {"english": "PA", "sound": "pa", "word": "पक्षी", "english_word": "Bird"},
        "फ": {"english": "PHA", "sound": "pha", "word": "फल", "english_word": "Fruit"},
        "ब": {"english": "BA", "sound": "ba", "word": "बाग", "english_word": "Garden"},
        "भ": {"english": "BHA", "sound": "bha", "word": "भाई", "english_word": "Brother"},
        "म": {"english": "MA", "sound": "ma", "word": "माँ", "english_word": "Mother"},
        "य": {"english": "YA", "sound": "ya", "word": "यज्ञ", "english_word": "Sacrifice"},
        "र": {"english": "RA", "sound": "ra", "word": "रंग", "english_word": "Color"},
        "ल": {"english": "LA", "sound": "la", "word": "लक्ष्य", "english_word": "Goal"},
        "व": {"english": "VA", "sound": "va", "word": "वाद", "english_word": "Debate"},
        "श": {"english": "SHA", "sound": "sha", "word": "शांति", "english_word": "Peace"},
        "ष": {"english": "SHHA", "sound": "shha", "word": "षड्भुज", "english_word": "Hexagon"},
        "स": {"english": "SA", "sound": "sa", "word": "सागर", "english_word": "Ocean"},
        "ह": {"english": "HA", "sound": "ha", "word": "हर्ष", "english_word": "Joy"},
    }
}

# ============================================================================
# SECTION 2: NUMBERS 1 TO 100 WITH HINDI-ENGLISH MAPPING
# ============================================================================

NUMBERS_DATABASE = {}
HINDI_NUMBERS = {
    1: "एक", 2: "दो", 3: "तीन", 4: "चार", 5: "पाँच",
    6: "छः", 7: "सात", 8: "आठ", 9: "नौ", 10: "दस",
    11: "ग्यारह", 12: "बारह", 13: "तेरह", 14: "चौदह", 15: "पन्द्रह",
    16: "सोलह", 17: "सत्रह", 18: "अठारह", 19: "उन्नीस", 20: "बीस",
    30: "तीस", 40: "चालीस", 50: "पचास", 60: "साठ", 70: "सत्तर",
    80: "अस्सी", 90: "नब्बे", 100: "सौ"
}

# Generate numbers 1-100 with Hindi-English mapping
for num in range(1, 101):
    english_name = {
        1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
        6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
        11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
        16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty",
        30: "Thirty", 40: "Forty", 50: "Fifty", 60: "Sixty", 70: "Seventy",
        80: "Eighty", 90: "Ninety", 100: "Hundred"
    }.get(num, None)
    
    if not english_name:
        tens = (num // 10) * 10
        ones = num % 10
        tens_name = {30: "Thirty", 40: "Forty", 50: "Fifty", 60: "Sixty", 
                     70: "Seventy", 80: "Eighty", 90: "Ninety"}.get(tens)
        ones_name = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
                     6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}.get(ones)
        english_name = f"{tens_name}-{ones_name}"
    
    NUMBERS_DATABASE[num] = {
        "number": num,
        "english": english_name,
        "hindi": HINDI_NUMBERS.get(num, f"{HINDI_NUMBERS.get(num//10*10, '')}-{HINDI_NUMBERS.get(num%10, '')}"),
        "word_form": str(num),
        "spelling": " ".join(english_name)
    }

# ============================================================================
# SECTION 3: MATHEMATICAL TABLES (1 TO 12)
# ============================================================================

MULTIPLICATION_TABLES = {}
for table in range(1, 13):
    MULTIPLICATION_TABLES[table] = {
        "number": table,
        "table_data": []
    }
    for multiplier in range(1, 11):
        result = table * multiplier
        MULTIPLICATION_TABLES[table]["table_data"].append({
            "operation": f"{table} × {multiplier}",
            "result": result,
            "hindi_operation": f"{HINDI_NUMBERS.get(table, table)} × {HINDI_NUMBERS.get(multiplier, multiplier)}",
            "hindi_result": f"= {HINDI_NUMBERS.get(result, result)}"
        })

# ============================================================================
# SECTION 4: ENGLISH GRAMMAR RULES & WORD FORMATION
# ============================================================================

GRAMMAR_RULES = {
    "parts_of_speech": {
        "noun": {
            "definition": "Person, Place, Thing, or Idea",
            "hindi": "संज्ञा",
            "examples": ["Cat", "Delhi", "Table", "Happiness"],
            "rules": [
                "Always capitalize proper nouns: Delhi, Raj, India",
                "Can be singular or plural: cat/cats",
                "Can be countable or uncountable: water, sand"
            ]
        },
        "verb": {
            "definition": "Action or State of Being",
            "hindi": "क्रिया",
            "examples": ["Run", "Eat", "Sleep", "Is"],
            "rules": [
                "Must agree with subject: He runs (not He run)",
                "Has different tenses: past, present, future",
                "Can be active or passive: The cat ate the rat / The rat was eaten"
            ]
        },
        "adjective": {
            "definition": "Word that describes a noun",
            "hindi": "विशेषण",
            "examples": ["Beautiful", "Happy", "Red", "Big"],
            "rules": [
                "Usually comes before the noun: beautiful flower",
                "Can follow linking verbs: The flower is beautiful",
                "Can be comparative or superlative: big, bigger, biggest"
            ]
        },
        "adverb": {
            "definition": "Word that modifies verb, adjective, or another adverb",
            "hindi": "क्रियाविशेषण",
            "examples": ["Quickly", "Very", "Here", "Yesterday"],
            "rules": [
                "Often ends in -ly: quickly, beautifully",
                "Modifies action or quality: runs quickly, very happy",
                "Can be at beginning, middle, or end of sentence"
            ]
        },
        "pronoun": {
            "definition": "Replaces a noun",
            "hindi": "सर्वनाम",
            "examples": ["He", "She", "They", "You", "I"],
            "rules": [
                "Subject pronouns: I, you, he, she, it, we, they",
                "Object pronouns: me, you, him, her, it, us, them",
                "Possessive pronouns: mine, yours, his, hers, its, ours, theirs"
            ]
        },
        "preposition": {
            "definition": "Shows relationship between words",
            "hindi": "पूर्वसर्ग",
            "examples": ["In", "On", "At", "By", "With", "Under"],
            "rules": [
                "Shows location: in, on, at, under, above",
                "Shows direction: to, from, toward, away",
                "Shows time: before, after, during, since"
            ]
        }
    },
    
    "tenses": {
        "present_simple": {
            "hindi": "सरल वर्तमान",
            "structure": "Subject + Verb (base form)",
            "examples": [
                {"english": "I eat", "hindi": "मैं खाता हूँ"},
                {"english": "She runs", "hindi": "वह दौड़ती है"},
                {"english": "They play", "hindi": "वे खेलते हैं"}
            ]
        },
        "past_simple": {
            "hindi": "सरल भूतकाल",
            "structure": "Subject + Verb (past form) + ed",
            "examples": [
                {"english": "I ate", "hindi": "मैंने खाया"},
                {"english": "She ran", "hindi": "वह दौड़ी"},
                {"english": "They played", "hindi": "वे खेले"}
            ]
        },
        "future_simple": {
            "hindi": "सरल भविष्य",
            "structure": "Subject + Will + Verb (base form)",
            "examples": [
                {"english": "I will eat", "hindi": "मैं खाऊँगा"},
                {"english": "She will run", "hindi": "वह दौड़ेगी"},
                {"english": "They will play", "hindi": "वे खेलेंगे"}
            ]
        }
    },

    "sentence_structures": {
        "simple_sentence": {
            "definition": "One independent clause",
            "structure": "Subject + Verb + Object",
            "hindi": "सरल वाक्य",
            "example": "The cat eats the mouse.",
            "breakdown": {
                "subject": "The cat",
                "verb": "eats",
                "object": "the mouse"
            }
        },
        "compound_sentence": {
            "definition": "Two independent clauses joined by 'and', 'but', 'or'",
            "structure": "Clause1 + Conjunction + Clause2",
            "hindi": "मिश्र वाक्य",
            "example": "The cat eats the mouse, but the dog chases the cat.",
        },
        "complex_sentence": {
            "definition": "One independent clause + one or more dependent clauses",
            "structure": "Main clause + Subordinate clause",
            "hindi": "जटिल वाक्य",
            "example": "Because it was raining, the cat stayed inside."
        }
    },

    "word_formation_rules": {
        "pluralization": {
            "rule1": "Add -s to most nouns: cat → cats",
            "rule2": "Add -es to words ending in s, x, z, ch, sh: box → boxes",
            "rule3": "Change -y to -ies: baby → babies",
            "rule4": "Add -es to words ending in -o: potato → potatoes",
            "rule5": "Irregular plurals: child → children, man → men",
        },
        "verb_tense_formation": {
            "past_tense": "Most verbs + -ed: walk → walked",
            "present_participle": "Verb + -ing: run → running",
            "third_person_singular": "Verb + -s: he eat → he eats"
        },
        "adjective_formation": {
            "comparative": "Add -er or use 'more': big → bigger, beautiful → more beautiful",
            "superlative": "Add -est or use 'most': big → biggest, beautiful → most beautiful",
            "negation": "Add 'un-' or 'in-': happy → unhappy, correct → incorrect"
        }
    }
}

# ============================================================================
# SECTION 5: COLOR NAMES - ENGLISH, HINDI & HUMAN PERCEPTION
# ============================================================================

COLORS = {
    "primary_colors": {
        "red": {
            "english": "Red",
            "hindi": "लाल",
            "hex": "#FF0000",
            "rgb": (255, 0, 0),
            "tone": "Warm, energetic, passionate",
            "hindi_description": "गरम, ऊर्जावान, जुनूनी",
            "examples": ["Apple", "Rose", "Fire"],
            "hindi_examples": ["सेब", "गुलाब", "आग"]
        },
        "blue": {
            "english": "Blue",
            "hindi": "नीला",
            "hex": "#0000FF",
            "rgb": (0, 0, 255),
            "tone": "Cool, calm, peaceful",
            "hindi_description": "ठंडा, शांत, सौम्य",
            "examples": ["Sky", "Ocean", "Water"],
            "hindi_examples": ["आकाश", "महासागर", "पानी"]
        },
        "yellow": {
            "english": "Yellow",
            "hindi": "पीला",
            "hex": "#FFFF00",
            "rgb": (255, 255, 0),
            "tone": "Bright, cheerful, optimistic",
            "hindi_description": "चमकदार, खुशनुमा, आशावादी",
            "examples": ["Sun", "Banana", "Gold"],
            "hindi_examples": ["सूरज", "केला", "सोना"]
        }
    },
    
    "secondary_colors": {
        "green": {
            "english": "Green",
            "hindi": "हरा",
            "hex": "#008000",
            "rgb": (0, 128, 0),
            "tone": "Fresh, natural, growth",
            "hindi_description": "ताज़ा, प्राकृतिक, वृद्धि",
            "examples": ["Grass", "Tree", "Leaf"],
            "hindi_examples": ["घास", "पेड़", "पत्ता"]
        },
        "orange": {
            "english": "Orange",
            "hindi": "नारंगी",
            "hex": "#FFA500",
            "rgb": (255, 165, 0),
            "tone": "Warm, energetic, social",
            "hindi_description": "गरम, ऊर्जावान, सामाजिक",
            "examples": ["Orange (fruit)", "Sunset", "Carrot"],
            "hindi_examples": ["संतरा", "सूर्यास्त", "गाजर"]
        },
        "purple": {
            "english": "Purple",
            "hindi": "बैंगनी",
            "hex": "#800080",
            "rgb": (128, 0, 128),
            "tone": "Royal, mysterious, creative",
            "hindi_description": "शाही, रहस्यमय, रचनात्मक",
            "examples": ["Grape", "Flower", "Night Sky"],
            "hindi_examples": ["अंगूर", "फूल", "रात का आकाश"]
        }
    },

    "neutral_colors": {
        "black": {
            "english": "Black",
            "hindi": "काला",
            "hex": "#000000",
            "rgb": (0, 0, 0),
            "tone": "Formal, elegant, powerful",
            "hindi_description": "औपचारिक, सुंदर, शक्तिशाली"
        },
        "white": {
            "english": "White",
            "hindi": "सफेद",
            "hex": "#FFFFFF",
            "rgb": (255, 255, 255),
            "tone": "Pure, clean, simple",
            "hindi_description": "शुद्ध, स्वच्छ, सरल"
        },
        "gray": {
            "english": "Gray",
            "hindi": "ग्रे/धूसर",
            "hex": "#808080",
            "rgb": (128, 128, 128),
            "tone": "Neutral, balanced, professional",
            "hindi_description": "तटस्थ, संतुलित, व्यावहारिक"
        }
    }
}

# ============================================================================
# SECTION 6: SPELLING & SILENT LETTERS (PHONETICS)
# ============================================================================

SPELLING_RULES = {
    "silent_letters": {
        "silent_b": {
            "rule": "B is silent when it comes after M at the end of words",
            "examples": [
                {"word": "Dumb", "pronunciation": "DUM", "explanation": "B is not pronounced"},
                {"word": "Numb", "pronunciation": "NUM", "explanation": "B is not pronounced"},
                {"word": "Climb", "pronunciation": "CLIME", "explanation": "B is not pronounced"},
                {"word": "Lamb", "pronunciation": "LAM", "explanation": "B is not pronounced"}
            ]
        },
        "silent_c": {
            "rule": "C is silent when it comes before T or I in certain words",
            "examples": [
                {"word": "Muscle", "pronunciation": "MUSSEL", "explanation": "C is not pronounced"},
                {"word": "Sciatic", "pronunciation": "SY-AT-IC", "explanation": "First C is silent"},
                {"word": "Scene", "pronunciation": "SEEN", "explanation": "C is not pronounced"}
            ]
        },
        "silent_d": {
            "rule": "D is silent when preceded by G or W",
            "examples": [
                {"word": "Edge", "pronunciation": "EJ", "explanation": "D is not pronounced"},
                {"word": "Bridge", "pronunciation": "BRIJ", "explanation": "D is not pronounced"},
                {"word": "Wedge", "pronunciation": "WEJ", "explanation": "D is not pronounced"}
            ]
        },
        "silent_e": {
            "rule": "E at the end of words is often silent and changes vowel sound",
            "examples": [
                {"word": "Make", "pronunciation": "MAKE", "explanation": "Silent E makes A say its name"},
                {"word": "Time", "pronunciation": "TIME", "explanation": "Silent E makes I say its name"},
                {"word": "Hope", "pronunciation": "HOPE", "explanation": "Silent E makes O say its name"}
            ]
        },
        "silent_g": {
            "rule": "G is silent when followed by N",
            "examples": [
                {"word": "Knight", "pronunciation": "NITE", "explanation": "G and K are not pronounced"},
                {"word": "Design", "pronunciation": "DI-ZINE", "explanation": "G is not pronounced"},
                {"word": "Gnome", "pronunciation": "NOME", "explanation": "G is not pronounced"},
                {"word": "Gnat", "pronunciation": "NAT", "explanation": "G is not pronounced"}
            ]
        },
        "silent_h": {
            "rule": "H is silent in certain words and positions",
            "examples": [
                {"word": "Hour", "pronunciation": "OUR", "explanation": "H is not pronounced"},
                {"word": "Honest", "pronunciation": "ON-EST", "explanation": "H is not pronounced"},
                {"word": "Heir", "pronunciation": "AIR", "explanation": "H is not pronounced"},
                {"word": "Ghost", "pronunciation": "GOST", "explanation": "H is not pronounced"}
            ]
        },
        "silent_k": {
            "rule": "K is silent when followed by N at the beginning",
            "examples": [
                {"word": "Knight", "pronunciation": "NITE", "explanation": "K is not pronounced"},
                {"word": "Knee", "pronunciation": "NEE", "explanation": "K is not pronounced"},
                {"word": "Knife", "pronunciation": "NIFE", "explanation": "K is not pronounced"},
                {"word": "Know", "pronunciation": "NO", "explanation": "K is not pronounced"}
            ]
        },
        "silent_l": {
            "rule": "L is silent in certain positions",
            "examples": [
                {"word": "Could", "pronunciation": "KUD", "explanation": "L is not pronounced"},
                {"word": "Would", "pronunciation": "WUD", "explanation": "L is not pronounced"},
                {"word": "Should", "pronunciation": "SHUD", "explanation": "L is not pronounced"},
                {"word": "Half", "pronunciation": "HAF", "explanation": "L is not pronounced"}
            ]
        },
        "silent_p": {
            "rule": "P is silent when it comes before S, N, or T",
            "examples": [
                {"word": "Psychology", "pronunciation": "SY-KOL-O-JEE", "explanation": "P is not pronounced"},
                {"word": "Pneumonia", "pronunciation": "NU-MO-NYA", "explanation": "P is not pronounced"},
                {"word": "Receipt", "pronunciation": "RI-SEET", "explanation": "P is not pronounced"}
            ]
        },
        "silent_w": {
            "rule": "W is silent when it comes before R",
            "examples": [
                {"word": "Write", "pronunciation": "RITE", "explanation": "W is not pronounced"},
                {"word": "Wrong", "pronunciation": "RONG", "explanation": "W is not pronounced"},
                {"word": "Wrap", "pronunciation": "RAP", "explanation": "W is not pronounced"}
            ]
        }
    },

    "phonetic_patterns": {
        "long_vowels": {
            "a": {"sound": "ay", "examples": ["Make", "Take", "Cake"], "rule": "Usually silent E at end"},
            "e": {"sound": "ee", "examples": ["Me", "We", "See"], "rule": "At end of word"},
            "i": {"sound": "eye", "examples": ["Time", "Fine", "Mine"], "rule": "Before silent E"},
            "o": {"sound": "oh", "examples": ["Home", "Rope", "Note"], "rule": "Before silent E"},
            "u": {"sound": "oo", "examples": ["Tune", "Flute", "Cute"], "rule": "Before silent E"}
        },
        "short_vowels": {
            "a": {"sound": "ah", "examples": ["Cat", "Hat", "Bat"], "rule": "In closed syllables"},
            "e": {"sound": "eh", "examples": ["Bed", "Red", "Get"], "rule": "In closed syllables"},
            "i": {"sound": "ih", "examples": ["Sit", "Big", "Hit"], "rule": "In closed syllables"},
            "o": {"sound": "ah", "examples": ["Dog", "Hot", "Lot"], "rule": "In closed syllables"},
            "u": {"sound": "uh", "examples": ["Bug", "Cup", "But"], "rule": "In closed syllables"}
        }
    }
}

# ============================================================================
# SECTION 7: AI WORD BREAKING & RECONSTRUCTION ENGINE
# ============================================================================

class WordBreaker:
    """
    AI Engine to break down words and reconstruct them from components
    This helps AI learn patterns and create new words
    """
    
    @staticmethod
    def break_word(word):
        """
        Break a word into its components:
        - Prefix (if any)
        - Root
        - Suffix (if any)
        """
        prefixes = ["un", "re", "pre", "dis", "mis", "over", "under", "in", "im", "il", "ir"]
        suffixes = ["ing", "ed", "er", "est", "ly", "ness", "ment", "tion", "sion", "able", "ible"]
        
        word_lower = word.lower()
        components = {
            "original_word": word,
            "prefix": None,
            "root": word_lower,
            "suffix": None,
            "structure": None
        }
        
        for prefix in prefixes:
            if word_lower.startswith(prefix):
                components["prefix"] = prefix
                components["root"] = word_lower[len(prefix):]
                break
        
        for suffix in suffixes:
            if components["root"].endswith(suffix):
                components["suffix"] = suffix
                components["root"] = components["root"][:-len(suffix)]
                break
        
        components["structure"] = f"{components['prefix'] or ''}-{components['root']}-{components['suffix'] or ''}"
        return components
    
    @staticmethod
    def reconstruct_word(prefix=None, root="", suffix=None):
        """Reconstruct a word from its components"""
        word = ""
        if prefix:
            word += prefix
        word += root
        if suffix:
            word += suffix
        return word
    
    @staticmethod
    def find_word_family(root_word):
        """Find all words from the same root"""
        word_broken = WordBreaker.break_word(root_word)
        root = word_broken["root"]
        
        prefixes = ["un", "re", "dis", "mis"]
        suffixes = ["ing", "ed", "er", "est", "ly", "ness"]
        
        family = {
            "root": root,
            "variations": []
        }
        
        for prefix in prefixes:
            family["variations"].append(WordBreaker.reconstruct_word(prefix, root))
        
        for suffix in suffixes:
            family["variations"].append(WordBreaker.reconstruct_word(None, root, suffix))
        
        return family

# ============================================================================
# SECTION 8: HINDI-ENGLISH VOCABULARY BRIDGE
# ============================================================================

HINDI_ENGLISH_BRIDGE = {
    "common_words": [
        {
            "english": "Mother",
            "hindi": "माँ",
            "transliteration": "Maa",
            "pronunciation": "M-ah",
            "family": ["Mother", "Motherhood", "Motherly"],
            "hindi_family": ["माँ", "मातृत्व", "मातृ"],
            "usage": "Female parent",
            "hindi_meaning": "महिला माता-पिता"
        },
        {
            "english": "Father",
            "hindi": "पिता",
            "transliteration": "Pita",
            "pronunciation": "P-ee-tah",
            "family": ["Father", "Fatherhood", "Fatherly"],
            "hindi_family": ["पिता", "पितृत्व", "पितृ"],
            "usage": "Male parent",
            "hindi_meaning": "पुरुष माता-पिता"
        },
        {
            "english": "House",
            "hindi": "घर",
            "transliteration": "Ghar",
            "pronunciation": "G-har",
            "family": ["House", "Housekeeper", "Household"],
            "hindi_family": ["घर", "गृहस्थी", "आवास"],
            "usage": "Place of residence",
            "hindi_meaning": "रहने की जगह"
        },
        {
            "english": "Water",
            "hindi": "पानी",
            "transliteration": "Pani",
            "pronunciation": "P-ah-nee",
            "family": ["Water", "Watery", "Waterproof"],
            "hindi_family": ["पानी", "जलीय", "जल"],
            "usage": "Liquid H2O",
            "hindi_meaning": "तरल एच2ओ"
        },
        {
            "english": "Friend",
            "hindi": "दोस्त",
            "transliteration": "Dost",
            "pronunciation": "D-ost",
            "family": ["Friend", "Friendly", "Friendship"],
            "hindi_family": ["दोस्त", "दोस्ताना", "दोस्ती"],
            "usage": "Person you trust",
            "hindi_meaning": "विश्वस्त व्यक्ति"
        }
    ]
}

# ============================================================================
# SECTION 9: ADVANCED AI LEARNING STRUCTURE
# ============================================================================

class AILearningStructure:
    """
    Advanced data structure for AI to learn, remember, and create new knowledge
    """
    
    def __init__(self):
        self.knowledge_graph = {}
        self.pattern_recognition = {}
        self.memory_cache = {}
    
    def create_concept(self, name, properties):
        """
        Create a concept that AI can understand and use
        
        Example:
            name = "Dog"
            properties = {
                "category": "Animal",
                "characteristics": ["Bark", "Four legs", "Loyal"],
                "hindi": "कुत्ता",
                "examples": ["Labrador", "German Shepherd"]
            }
        """
        self.knowledge_graph[name] = {
            "name": name,
            "properties": properties,
            "relationships": [],
            "learned_from": "training_data",
            "confidence": 0.95
        }
        return self.knowledge_graph[name]
    
    def link_concepts(self, concept1, concept2, relationship):
        """Link two concepts with a relationship"""
        if concept1 in self.knowledge_graph:
            self.knowledge_graph[concept1]["relationships"].append({
                "target": concept2,
                "type": relationship
            })
    
    def extract_pattern(self, data_set):
        """Extract patterns from a dataset"""
        patterns = {
            "frequency": {},
            "sequences": [],
            "rules": []
        }
        return patterns
    
    def generate_new_word(self, components):
        """
        Generate a new word from learned components
        Uses pattern recognition to create plausible words
        """
        generated = {
            "components": components,
            "possible_words": [],
            "confidence_score": 0.0
        }
        return generated

# ============================================================================
# SECTION 10: COMPLETE LEARNING DATABASE INITIALIZATION
# ============================================================================

def initialize_ai_knowledge_base():
    """
    Initialize complete AI learning database with all sections
    """
    knowledge_base = {
        "alphabet": ENGLISH_ALPHABET,
        "devanagari": HINDI_DEVANAGARI,
        "numbers": NUMBERS_DATABASE,
        "multiplication_tables": MULTIPLICATION_TABLES,
        "grammar": GRAMMAR_RULES,
        "colors": COLORS,
        "spelling": SPELLING_RULES,
        "hindi_english_bridge": HINDI_ENGLISH_BRIDGE,
    }
    return knowledge_base

# ============================================================================
# SECTION 11: MULTI-LANGUAGE SUPPORT (12 ADDITIONAL LANGUAGES)
# ============================================================================

MULTILANGUAGE_DATABASE = {
    "spanish": {
        "language": "Spanish",
        "native_name": "Español",
        "code": "es",
        "alphabet": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "Ñ", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
        "numbers": {1: "Uno", 2: "Dos", 3: "Tres", 4: "Cuatro", 5: "Cinco", 10: "Diez", 20: "Veinte", 100: "Cien"},
        "common_words": [
            {"spanish": "Hola", "meaning": "Hello", "hindi": "नमस्ते"},
            {"spanish": "Gracias", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"spanish": "Agua", "meaning": "Water", "hindi": "पानी"},
            {"spanish": "Casa", "meaning": "House", "hindi": "घर"}
        ]
    },
    "french": {
        "language": "French",
        "native_name": "Français",
        "code": "fr",
        "alphabet": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
        "numbers": {1: "Un", 2: "Deux", 3: "Trois", 4: "Quatre", 5: "Cinq", 10: "Dix", 20: "Vingt", 100: "Cent"},
        "common_words": [
            {"french": "Bonjour", "meaning": "Hello", "hindi": "नमस्ते"},
            {"french": "Merci", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"french": "Eau", "meaning": "Water", "hindi": "पानी"},
            {"french": "Maison", "meaning": "House", "hindi": "घर"}
        ]
    },
    "german": {
        "language": "German",
        "native_name": "Deutsch",
        "code": "de",
        "alphabet": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "Ä", "Ö", "Ü", "ß"],
        "numbers": {1: "Eins", 2: "Zwei", 3: "Drei", 4: "Vier", 5: "Fünf", 10: "Zehn", 20: "Zwanzig", 100: "Hundert"},
        "common_words": [
            {"german": "Hallo", "meaning": "Hello", "hindi": "नमस्ते"},
            {"german": "Danke", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"german": "Wasser", "meaning": "Water", "hindi": "पानी"},
            {"german": "Haus", "meaning": "House", "hindi": "घर"}
        ]
    },
    "portuguese": {
        "language": "Portuguese",
        "native_name": "Português",
        "code": "pt",
        "alphabet": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
        "numbers": {1: "Um", 2: "Dois", 3: "Três", 4: "Quatro", 5: "Cinco", 10: "Dez", 20: "Vinte", 100: "Cem"},
        "common_words": [
            {"portuguese": "Olá", "meaning": "Hello", "hindi": "नमस्ते"},
            {"portuguese": "Obrigado", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"portuguese": "Água", "meaning": "Water", "hindi": "पानी"},
            {"portuguese": "Casa", "meaning": "House", "hindi": "घर"}
        ]
    },
    "italian": {
        "language": "Italian",
        "native_name": "Italiano",
        "code": "it",
        "alphabet": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
        "numbers": {1: "Uno", 2: "Due", 3: "Tre", 4: "Quattro", 5: "Cinque", 10: "Dieci", 20: "Venti", 100: "Cento"},
        "common_words": [
            {"italian": "Ciao", "meaning": "Hello", "hindi": "नमस्ते"},
            {"italian": "Grazie", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"italian": "Acqua", "meaning": "Water", "hindi": "पानी"},
            {"italian": "Casa", "meaning": "House", "hindi": "घर"}
        ]
    },
    "japanese": {
        "language": "Japanese",
        "native_name": "日本語",
        "code": "ja",
        "alphabet": ["ひ", "ら", "が", "な"],
        "numbers": {1: "一 (Ichi)", 2: "二 (Ni)", 3: "三 (San)", 4: "四 (Shi/Yon)", 5: "五 (Go)", 10: "十 (Juu)", 20: "二十 (Ni-juu)", 100: "百 (Hyaku)"},
        "common_words": [
            {"japanese": "こんにちは", "meaning": "Hello", "hindi": "नमस्ते"},
            {"japanese": "ありがとう", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"japanese": "水", "meaning": "Water", "hindi": "पानी"},
            {"japanese": "家", "meaning": "House", "hindi": "घर"}
        ]
    },
    "chinese": {
        "language": "Chinese (Mandarin)",
        "native_name": "中文",
        "code": "zh",
        "alphabet": ["常用汉字"],
        "numbers": {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 10: "十", 20: "二十", 100: "一百"},
        "common_words": [
            {"chinese": "你好", "meaning": "Hello", "hindi": "नमस्ते"},
            {"chinese": "谢谢", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"chinese": "水", "meaning": "Water", "hindi": "पानी"},
            {"chinese": "房子", "meaning": "House", "hindi": "घर"}
        ]
    },
    "korean": {
        "language": "Korean",
        "native_name": "한국어",
        "code": "ko",
        "alphabet": ["가", "나", "다", "라"],
        "numbers": {1: "하나", 2: "둘", 3: "셋", 4: "넷", 5: "다섯", 10: "열", 20: "스물", 100: "백"},
        "common_words": [
            {"korean": "안녕하세요", "meaning": "Hello", "hindi": "नमस्ते"},
            {"korean": "감사합니다", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"korean": "물", "meaning": "Water", "hindi": "पानी"},
            {"korean": "집", "meaning": "House", "hindi": "घर"}
        ]
    },
    "russian": {
        "language": "Russian",
        "native_name": "Русский",
        "code": "ru",
        "alphabet": ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И"],
        "numbers": {1: "Один", 2: "Два", 3: "Три", 4: "Четыре", 5: "Пять", 10: "Десять", 20: "Двадцать", 100: "Сто"},
        "common_words": [
            {"russian": "Привет", "meaning": "Hello", "hindi": "नमस्ते"},
            {"russian": "Спасибо", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"russian": "Вода", "meaning": "Water", "hindi": "पानी"},
            {"russian": "Дом", "meaning": "House", "hindi": "घर"}
        ]
    },
    "arabic": {
        "language": "Arabic",
        "native_name": "العربية",
        "code": "ar",
        "alphabet": ["ا", "ب", "ت", "ث", "ج"],
        "numbers": {1: "واحد", 2: "اثنان", 3: "ثلاثة", 4: "أربعة", 5: "خمسة", 10: "عشرة", 20: "عشرون", 100: "مائة"},
        "common_words": [
            {"arabic": "مرحبا", "meaning": "Hello", "hindi": "नमस्ते"},
            {"arabic": "شكراً", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"arabic": "ماء", "meaning": "Water", "hindi": "पानी"},
            {"arabic": "بيت", "meaning": "House", "hindi": "घर"}
        ]
    },
    "bengali": {
        "language": "Bengali",
        "native_name": "বাংলা",
        "code": "bn",
        "alphabet": ["ক", "খ", "গ", "ঘ", "ঙ"],
        "numbers": {1: "এক", 2: "দুই", 3: "তিন", 4: "চার", 5: "পাঁচ", 10: "দশ", 20: "বিশ", 100: "একশত"},
        "common_words": [
            {"bengali": "নমস্কার", "meaning": "Hello", "hindi": "नमस्ते"},
            {"bengali": "ধন্যবাদ", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"bengali": "পানি", "meaning": "Water", "hindi": "पानी"},
            {"bengali": "বাড়ি", "meaning": "House", "hindi": "घर"}
        ]
    },
    "tamil": {
        "language": "Tamil",
        "native_name": "தமிழ்",
        "code": "ta",
        "alphabet": ["க", "ங", "ச", "ஞ", "ட"],
        "numbers": {1: "ஒன்று", 2: "இரண்டு", 3: "மூன்று", 4: "நான்கு", 5: "ஐந்து", 10: "பத்து", 20: "இருபது", 100: "நூறு"},
        "common_words": [
            {"tamil": "வணக்கம்", "meaning": "Hello", "hindi": "नमस्ते"},
            {"tamil": "நன்றி", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"tamil": "நீர்", "meaning": "Water", "hindi": "पानी"},
            {"tamil": "வீடு", "meaning": "House", "hindi": "घर"}
        ]
    },
    "marathi": {
        "language": "Marathi",
        "native_name": "मराठी",
        "code": "mr",
        "alphabet": ["क", "ख", "ग", "घ", "ङ"],
        "numbers": {1: "एक", 2: "दोन", 3: "तीन", 4: "चार", 5: "पाच", 10: "दहा", 20: "वीस", 100: "शत"},
        "common_words": [
            {"marathi": "नमस्कार", "meaning": "Hello", "hindi": "नमस्ते"},
            {"marathi": "धन्यवाद", "meaning": "Thank you", "hindi": "धन्यवाद"},
            {"marathi": "पाणी", "meaning": "Water", "hindi": "पानी"},
            {"marathi": "घर", "meaning": "House", "hindi": "घर"}
        ]
    }
}

# ============================================================================
# SECTION 12: HINDI NUMBER COUNTING SYSTEM
# ============================================================================

HINDI_NUMBER_SYSTEM = {
    "units": {
        0: "शून्य", 1: "एक", 2: "दो", 3: "तीन", 4: "चार", 5: "पाँच",
        6: "छः", 7: "सात", 8: "आठ", 9: "नौ"
    },
    "teens": {
        10: "दस", 11: "ग्यारह", 12: "बारह", 13: "तेरह", 14: "चौदह",
        15: "पन्द्रह", 16: "सोलह", 17: "सत्रह", 18: "अठारह", 19: "उन्नीस"
    },
    "tens": {
        20: "बीस", 30: "तीस", 40: "चालीस", 50: "पचास",
        60: "साठ", 70: "सत्तर", 80: "अस्सी", 90: "नब्बे"
    },
    "higher": {
        100: "सौ", 1000: "हजार", 100000: "लाख", 10000000: "करोड़"
    }
}

def convert_number_to_hindi(num):
    """Convert any number to Hindi text format"""
    if num == 0:
        return HINDI_NUMBER_SYSTEM["units"][0]
    
    result = ""
    
    # Handle crores (10 million)
    if num >= 10000000:
        crores = num // 10000000
        result += HINDI_NUMBER_SYSTEM["units"].get(crores, str(crores)) + " " + HINDI_NUMBER_SYSTEM["higher"][10000000]
        num = num % 10000000
        if num > 0:
            result += " "
    
    # Handle lakhs (100,000)
    if num >= 100000:
        lakhs = num // 100000
        result += HINDI_NUMBER_SYSTEM["units"].get(lakhs, str(lakhs)) + " " + HINDI_NUMBER_SYSTEM["higher"][100000]
        num = num % 100000
        if num > 0:
            result += " "
    
    # Handle thousands
    if num >= 1000:
        thousands = num // 1000
        result += HINDI_NUMBER_SYSTEM["units"].get(thousands, str(thousands)) + " " + HINDI_NUMBER_SYSTEM["higher"][1000]
        num = num % 1000
        if num > 0:
            result += " "
    
    # Handle hundreds
    if num >= 100:
        hundreds = num // 100
        result += HINDI_NUMBER_SYSTEM["units"].get(hundreds, str(hundreds)) + " " + HINDI_NUMBER_SYSTEM["higher"][100]
        num = num % 100
        if num > 0:
            result += " "
    
    # Handle tens and units
    if num >= 20:
        tens = (num // 10) * 10
        result += HINDI_NUMBER_SYSTEM["tens"].get(tens, str(tens))
        num = num % 10
        if num > 0:
            result += " " + HINDI_NUMBER_SYSTEM["units"][num]
    elif num >= 10:
        result += HINDI_NUMBER_SYSTEM["teens"][num]
    elif num > 0:
        result += HINDI_NUMBER_SYSTEM["units"][num]
    
    return result.strip()

# ============================================================================
# SECTION 13: CONTINUOUS LEARNING & MEMORY SYSTEM
# ============================================================================

class ContinuousLearningSystem:
    """
    AI learning system that continuously learns, generates words,
    stores meanings, and expands knowledge base infinitely
    """
    
    def __init__(self):
        self.learned_words = {}
        self.generated_words = []
        self.pattern_library = {}
        self.meaning_cache = {}
        self.silence_words = set()
    
    def learn_new_word(self, word, meaning, language="english", tags=None):
        """Learn a new word with meaning and tags"""
        self.learned_words[word] = {
            "meaning": meaning,
            "language": language,
            "tags": tags or [],
            "learned_at": "auto",
            "frequency": 1,
            "related_words": []
        }
        return self.learned_words[word]
    
    def generate_new_word(self, prefix, root, suffix, language="english"):
        """Generate new words from components"""
        generated = {
            "original_components": f"{prefix}-{root}-{suffix}",
            "generated_word": WordBreaker.reconstruct_word(prefix, root, suffix),
            "potential_meanings": self._predict_meaning(root),
            "language": language,
            "confidence": 0.85
        }
        self.generated_words.append(generated)
        return generated
    
    def _predict_meaning(self, root):
        """Predict possible meanings based on root word"""
        predictions = []
        if root in self.learned_words:
            base_meaning = self.learned_words[root]["meaning"]
            predictions.append(base_meaning)
            predictions.append(f"Related to {base_meaning}")
        return predictions
    
    def add_silent_word(self, word):
        """Add word to silent learning (no output)"""
        self.silence_words.add(word)
    
    def learn_silently(self, words_list):
        """Silently learn multiple words without output"""
        for word_data in words_list:
            if isinstance(word_data, dict):
                self.learn_new_word(
                    word_data.get("word"),
                    word_data.get("meaning"),
                    word_data.get("language", "english")
                )
                self.silence_words.add(word_data.get("word"))
    
    def get_word_family(self, word):
        """Get all related words and their meanings"""
        if word in self.learned_words:
            return {
                "base_word": word,
                "data": self.learned_words[word],
                "related": self.learned_words[word].get("related_words", [])
            }
        return None
    
    def continuous_expand(self, new_data):
        """Continuously expand knowledge from new data"""
        if isinstance(new_data, dict):
            for key, value in new_data.items():
                if isinstance(value, str):
                    self.learn_new_word(key, value)
        return {"status": "expanded", "new_entries": len(new_data)}

# ============================================================================
# SECTION 14: DEMONSTRATION & USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        AI LEARNING KNOWLEDGE BASE - ABCD.py INITIALIZED        ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Initialize knowledge base
    kb = initialize_ai_knowledge_base()
    print("✓ Knowledge base initialized")
    print(f"✓ Total sections: {len(kb)}")
    print(f"✓ Database ready for AI learning and training\n")
    
    # Example 1: Show Alphabet
    print("─" * 70)
    print("EXAMPLE 1: ALPHABET LEARNING")
    print("─" * 70)
    alphabet = kb["alphabet"]["uppercase"]
    for letter in ['A', 'B', 'C', 'D', 'E']:
        info = alphabet[letter]
        print(f"{letter}: {info['english']} | Hindi: {info['hindi']} | Sound: {info['sound']}")
    
    # Example 2: Show Numbers
    print("\n" + "─" * 70)
    print("EXAMPLE 2: NUMBERS 1-10")
    print("─" * 70)
    for i in range(1, 11):
        num_data = kb["numbers"][i]
        print(f"{i:2d}. {num_data['english']:10s} | {num_data['hindi']:10s}")
    
    # Example 3: Show Multiplication Table
    print("\n" + "─" * 70)
    print("EXAMPLE 3: MULTIPLICATION TABLE OF 5")
    print("─" * 70)
    table_5 = kb["multiplication_tables"][5]["table_data"]
    for item in table_5[:5]:
        print(f"{item['operation']} = {item['result']}")
    
    # Example 4: Grammar Rules
    print("\n" + "─" * 70)
    print("EXAMPLE 4: PARTS OF SPEECH")
    print("─" * 70)
    parts = kb["grammar"]["parts_of_speech"]
    for pos, data in list(parts.items())[:3]:
        print(f"\n{pos.upper()} ({data['hindi']})")
        print(f"Definition: {data['definition']}")
        print(f"Examples: {', '.join(data['examples'])}")
    
    # Example 5: Colors
    print("\n" + "─" * 70)
    print("EXAMPLE 5: PRIMARY COLORS")
    print("─" * 70)
    colors = kb["colors"]["primary_colors"]
    for color_name, color_data in colors.items():
        print(f"\n{color_data['english']} ({color_data['hindi']})")
        print(f"Tone: {color_data['tone']}")
        print(f"Examples: {', '.join(color_data['examples'])}")
    
    # Example 6: Word Breaking
    print("\n" + "─" * 70)
    print("EXAMPLE 6: WORD BREAKING & RECONSTRUCTION")
    print("─" * 70)
    words_to_break = ["Running", "Unhappy", "Dislike"]
    for word in words_to_break:
        broken = WordBreaker.break_word(word)
        print(f"\nWord: {word}")
        print(f"  Structure: {broken['structure']}")
        print(f"  Prefix: {broken['prefix']}, Root: {broken['root']}, Suffix: {broken['suffix']}")
    
    # Example 7: Hindi-English Bridge
    print("\n" + "─" * 70)
    print("EXAMPLE 7: HINDI-ENGLISH VOCABULARY BRIDGE")
    print("─" * 70)
    for word_pair in kb["hindi_english_bridge"]["common_words"][:3]:
        print(f"\nEnglish: {word_pair['english']} | Hindi: {word_pair['hindi']}")
        print(f"Pronunciation: {word_pair['pronunciation']}")
        print(f"Meaning: {word_pair['usage']}")
    
    # Example 8: Silent Letters
    print("\n" + "─" * 70)
    print("EXAMPLE 8: SILENT LETTERS LEARNING")
    print("─" * 70)
    silent_letters = kb["spelling"]["silent_letters"]
    for letter_type, data in list(silent_letters.items())[:3]:
        print(f"\n{data['rule']}")
        for example in data['examples'][:2]:
            print(f"  {example['word']:15s} → {example['pronunciation']}")
    
    # Example 9: Multi-language Support
    print("\n" + "─" * 70)
    print("EXAMPLE 9: MULTI-LANGUAGE SUPPORT (12 LANGUAGES)")
    print("─" * 70)
    for lang_code, lang_data in list(MULTILANGUAGE_DATABASE.items())[:4]:
        print(f"\n{lang_data['language']} ({lang_data['native_name']})")
        for word in lang_data['common_words'][:2]:
            word_key = list(word.keys())[0]
            print(f"  {word[word_key]:15s} = {word['meaning']:15s} ({word['hindi']})")
    
    # Example 10: Hindi Number Counting
    print("\n" + "─" * 70)
    print("EXAMPLE 10: HINDI NUMBER COUNTING (1-100)")
    print("─" * 70)
    for num in [1, 10, 25, 50, 75, 100]:
        hindi_num = convert_number_to_hindi(num)
        print(f"{num:3d} = {hindi_num}")
    
    # Example 11: Continuous Learning System
    print("\n" + "─" * 70)
    print("EXAMPLE 11: CONTINUOUS LEARNING SYSTEM")
    print("─" * 70)
    cls = ContinuousLearningSystem()
    
    # Silent learning
    test_words = [
        {"word": "elephant", "meaning": "large animal", "language": "english"},
        {"word": "हाथी", "meaning": "large animal", "language": "hindi"},
        {"word": "run", "meaning": "move fast", "language": "english"},
        {"word": "दौड़", "meaning": "move fast", "language": "hindi"}
    ]
    cls.learn_silently(test_words)
    print(f"✓ Silently learned {len(test_words)} words (no output)")
    
    # Generate new words
    generated = cls.generate_new_word("un", "happy", "ness")
    print(f"\nGenerated word: {generated['generated_word']}")
    print(f"Potential meanings: {generated['potential_meanings']}")
    
    # Example 12: Word Breaking Advanced
    print("\n" + "─" * 70)
    print("EXAMPLE 12: ADVANCED WORD FAMILY ANALYSIS")
    print("─" * 70)
    test_word = "Beautiful"
    family = WordBreaker.find_word_family(test_word)
    print(f"Root word: {test_word}")
    print(f"Word family variations:")
    for var in family["variations"][:5]:
        print(f"  → {var}")
    
    print("\n" + "=" * 70)
    print("AI TRAINING DATABASE READY FOR LEARNING AND WORD GENERATION")
    print("=" * 70)
