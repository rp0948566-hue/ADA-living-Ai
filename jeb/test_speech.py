from speech import speakable


def test_paths_urls_code_not_read_aloud():
    assert "slash" not in speakable("It is in /home/claude/Desktop/jeb/gate.py now").lower()
    assert "gate.py" in speakable("It is in /home/claude/Desktop/jeb/gate.py now")
    assert speakable("see https://example.com/a/b?x=1 please") == "see a link please"
    assert speakable("/lovable-downloads/x/x64/lovable") == "lovable"
    assert speakable("**Done** `ls -la`") == "Done ls -la"
    assert speakable("hash 46e0c10c039e019119339687c3c1757c") == "hash an ID"


def test_plain_speech_untouched_and_empty():
    assert speakable("You've got 760 gigabytes free.") == "You've got 760 gigabytes free."
    assert speakable("```  ///  ```") == ""


def test_acronyms_spelled_out():
    assert speakable("RAM is 8 GB, CPU at 12%") == "R A M is 8 gigabytes, C P U at 12%"
    assert speakable("video memory") == "video memory"
