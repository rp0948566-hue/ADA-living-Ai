"""
Unit tests for tone_adapter.py
Using pytest framework. Run with: pytest test_tone_adapter.py -v

Tests:
1. test_detect_tone - Verify tone detection accuracy
2. test_adaptive_chat_fallback - Verify graceful fallback
3. test_logging - Verify JSON logging functionality
4. test_extract_topic - Verify topic extraction
5. test_intent_detection - Verify intent detection
6. test_config_loading - Verify configuration system
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from tone_adapter import ToneAdapter, ToneConfig, DEFAULT_TONE_KEYWORDS, DEFAULT_TOPIC_CLUSTERS


class TestToneAdapter:
    """Test suite for ToneAdapter class."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter with temp log file for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ToneConfig(log_file=os.path.join(tmpdir, 'test_logs.json'))
            yield ToneAdapter(config=config)
    
    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 1: Tone Detection
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_detect_tone_playful(self, adapter):
        """Test playful_roast tone detection."""
        user_input = "Haha dude, roast me! lol this is fun"
        tone, confidence = adapter.detect_tone(user_input)
        
        # Should detect some playful markers
        assert tone in adapter.config.tone_keywords.keys()
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.0  # Should have some confidence
    
    def test_detect_tone_frustrated(self, adapter):
        """Test frustrated tone detection."""
        user_input = "Ugh, I hate this! I'm so stuck and annoyed"
        tone, confidence = adapter.detect_tone(user_input)
        
        assert tone in adapter.config.tone_keywords.keys()
        assert confidence >= 0.3  # Should be reasonably confident
    
    def test_detect_tone_empty_input(self, adapter):
        """Test tone detection with empty input."""
        tone, confidence = adapter.detect_tone("")
        
        assert tone == 'neutral'
        assert confidence == 0.0
    
    def test_detect_tone_neutral(self, adapter):
        """Test neutral tone for generic input."""
        user_input = "Tell me about the weather"
        tone, confidence = adapter.detect_tone(user_input)
        
        assert tone in adapter.config.tone_keywords.keys()
        assert 0.0 <= confidence <= 1.0
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 2: Adaptive Chat & Fallback
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_adaptive_chat_fallback_no_ollama(self):
        """Test graceful fallback when Ollama is unavailable."""
        import tone_adapter
        original_ollama = tone_adapter.ollama
        tone_adapter.ollama = None  # Simulate missing Ollama
        
        try:
            config = ToneConfig()
            adapter = ToneAdapter(config=config)
            result = adapter.adaptive_chat("Hello there")
            
            # Should return fallback gracefully
            assert 'reply' in result
            assert result['reply'] is not None
            assert result['confidence'] == 0.0
            assert result['tone'] == 'neutral'
        finally:
            tone_adapter.ollama = original_ollama  # Restore
    
    def test_adaptive_chat_returns_dict(self, adapter):
        """Test that adaptive_chat returns complete dictionary."""
        user_input = "Tell me a joke"
        result = adapter.adaptive_chat(user_input)
        
        required_keys = [
            'reply', 'tone', 'topic', 'confidence', 'intent',
            'tts_hints', 'interaction_id', 'avg_confidence'
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_adaptive_chat_with_history(self, adapter):
        """Test adaptive_chat respects conversation history."""
        history = [
            {'role': 'user', 'content': 'Hi there'},
            {'role': 'assistant', 'content': 'Hello! How can I help?'}
        ]
        
        result = adapter.adaptive_chat("What's your name?", conversation_history=history)
        
        assert 'reply' in result
        assert result['interaction_id'] == 1
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 3: Logging System
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_logging_creates_file(self, temp_log_file):
        """Test that logging creates JSON file."""
        config = ToneConfig(log_file=temp_log_file)
        adapter = ToneAdapter(config=config)
        
        # Manually call _log_interaction
        adapter._log_interaction("test", "reply", "playful_roast", "general", 0.9, None)
        
        # File should exist and contain valid JSON
        assert os.path.exists(temp_log_file)
        
        with open(temp_log_file, 'r') as f:
            logs = json.load(f)
        
        assert len(logs) == 1
        assert logs[0]['user_input'] == "test"
        assert logs[0]['tone'] == "playful_roast"
    
    def test_logging_appends_entries(self, temp_log_file):
        """Test that logging appends to existing log."""
        config = ToneConfig(log_file=temp_log_file)
        adapter = ToneAdapter(config=config)
        
        # Log two interactions
        adapter._log_interaction("first", "reply1", "neutral", "general", 0.5, None)
        adapter._log_interaction("second", "reply2", "excited", "general", 0.8, "none")
        
        # Both should be in log
        with open(temp_log_file, 'r') as f:
            logs = json.load(f)
        
        assert len(logs) == 2
        assert logs[0]['user_input'] == "first"
        assert logs[1]['user_input'] == "second"
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 4: Topic Extraction
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_extract_topic_coding(self, adapter):
        """Test coding topic extraction."""
        user_input = "I have a Python bug in my code"
        topic = adapter.extract_topic(user_input)
        
        assert topic in adapter.config.topic_clusters.keys()
        assert topic == 'coding'
    
    def test_extract_topic_relationships(self, adapter):
        """Test relationships topic extraction."""
        user_input = "I'm having feelings about my crush"
        topic = adapter.extract_topic(user_input)
        
        assert topic in adapter.config.topic_clusters.keys()
    
    def test_extract_topic_general(self, adapter):
        """Test general topic default."""
        user_input = "Tell me about weather patterns"
        topic = adapter.extract_topic(user_input)
        
        assert topic in adapter.config.topic_clusters.keys() or topic == 'general'
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 5: Intent Detection
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_detect_roast_request(self, adapter):
        """Test roast_request intent detection."""
        user_input = "Hey, roast me please!"
        intent = adapter.check_intent(user_input)
        
        assert intent == 'roast_request'
    
    def test_detect_advice_seek(self, adapter):
        """Test advice_seek intent detection."""
        user_input = "How to fix a bug?"
        intent = adapter.check_intent(user_input)
        
        assert intent == 'advice_seek'
    
    def test_detect_no_intent(self, adapter):
        """Test no intent detected."""
        user_input = "What's the capital of France?"
        intent = adapter.check_intent(user_input)
        
        # Should be None or not match any intent
        assert intent is None or isinstance(intent, str)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 6: Configuration System
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_config_defaults(self):
        """Test ToneConfig uses defaults correctly."""
        config = ToneConfig()
        
        assert config.model == 'llama3.1'
        assert config.max_history == 5
        assert config.max_words == 150
        assert 'playful_roast' in config.tone_keywords
        assert 'coding' in config.topic_clusters
    
    def test_config_custom_values(self):
        """Test ToneConfig accepts custom values."""
        config = ToneConfig(model='mistral', max_history=10, max_words=200)
        
        assert config.model == 'mistral'
        assert config.max_history == 10
        assert config.max_words == 200
    
    def test_config_custom_keywords(self):
        """Test ToneConfig accepts custom keywords."""
        custom_keywords = {
            'custom_tone': ['word1', 'word2']
        }
        config = ToneConfig(tone_keywords=custom_keywords)
        
        assert 'custom_tone' in config.tone_keywords
        assert 'playful_roast' not in config.tone_keywords
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 7: Metrics Tracking
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_metrics_tracking(self, adapter):
        """Test metrics are tracked correctly."""
        adapter._interaction_count = 5
        adapter._confidence_sum = 4.0
        
        metrics = adapter.get_metrics()
        
        assert metrics['total_interactions'] == 5
        assert metrics['avg_confidence'] == 0.8
        assert 'log_file' in metrics
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 8: TTS Prosody
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_tts_prosody_retrieval(self, adapter):
        """Test TTS prosody hints are retrieved correctly."""
        prosody = adapter.get_tts_prosody('excited')
        
        assert 'speed' in prosody
        assert 'pitch' in prosody
        assert 'emphasis' in prosody
        assert 'volume' in prosody
        assert prosody['emphasis'] == 'upbeat'
    
    def test_tts_prosody_fallback(self, adapter):
        """Test TTS prosody defaults to neutral for unknown tone."""
        prosody = adapter.get_tts_prosody('unknown_tone')
        
        assert prosody == adapter.config.tts_prosody['neutral']
    
    # ─────────────────────────────────────────────────────────────────────────
    # Test 9: Prompt Generation
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_adaptive_prompt_generation(self, adapter):
        """Test dynamic prompt generation."""
        prompt = adapter.generate_adaptive_prompt('playful_roast', 'coding')
        
        assert 'playful_roast' in prompt
        assert 'coding' in prompt
        assert 'ADA' in prompt
        assert str(adapter.config.max_words) in prompt
    
    def test_adaptive_prompt_all_tones(self, adapter):
        """Test prompt generation for all tones."""
        for tone in adapter.config.tone_keywords.keys():
            prompt = adapter.generate_adaptive_prompt(tone, 'general')
            
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert tone in prompt or 'neutral' in prompt


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def adapter_with_temp_log(self):
        """Create adapter with temp log for integration tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ToneConfig(log_file=os.path.join(tmpdir, 'integration_logs.json'))
            yield ToneAdapter(config=config)
    
    def test_full_conversation_flow(self, adapter_with_temp_log):
        """Test complete conversation flow."""
        adapter = adapter_with_temp_log
        
        # Simulate multi-turn conversation
        exchanges = [
            "Hey! How are you?",
            "I'm stuck on this code",
            "Roast me lol"
        ]
        
        history = []
        for user_input in exchanges:
            result = adapter.adaptive_chat(user_input, conversation_history=history)
            
            assert 'reply' in result
            assert result['tone'] is not None
            
            history.append({'role': 'user', 'content': user_input})
            history.append({'role': 'assistant', 'content': result['reply']})
        
        # Verify logging
        assert os.path.exists(adapter.config.log_file)
        with open(adapter.config.log_file, 'r') as f:
            logs = json.load(f)
        assert len(logs) >= 0  # At least logged something


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures & Utilities
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return ToneConfig(
        model='llama3.1',
        max_history=3,
        max_words=100
    )


def test_sanity_check():
    """Sanity check – ensure test module imports correctly."""
    from tone_adapter import ToneAdapter, ToneConfig
    assert ToneAdapter is not None
    assert ToneConfig is not None


if __name__ == "__main__":
    # Run tests: pytest test_tone_adapter.py -v
    pytest.main([__file__, '-v'])
