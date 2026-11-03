from gate import Gate, hollow_promise


def test_alt_tap_forces():
    g = Gate(); g.key("KEY_LEFTALT", True, 0); g.key("KEY_LEFTALT", False, 0.2)
    assert g.decide("blah", 1) == (True, "alt-tap")


def test_alt_shortcut_ignored():
    g = Gate(); g.key("KEY_LEFTALT", True, 0); g.key("KEY_TAB", True, 0.1)
    g.key("KEY_TAB", False, 0.15); g.key("KEY_LEFTALT", False, 0.3)
    assert g.force is False


def test_alt_long_hold_ignored():
    g = Gate(); g.key("KEY_LEFTALT", True, 0); g.key("KEY_LEFTALT", False, 2)
    assert g.force is False


def test_typing_blocks_unaddressed():
    g = Gate(); g.key("KEY_A", True, 10)
    assert g.decide("open the settings page", 10.5)[0] is False


def test_name_overrides_typing():
    g = Gate(); g.key("KEY_A", True, 10)
    assert g.decide("jeb are you there", 10.5)[0] is True


def test_side_talk_and_ambient():
    g = Gate()
    assert g.decide("yeah okay", 100) == (False, "side talk")
    assert g.decide("I think the weather is nice today", 100) == (False, "ambient")


def test_no_wake_word_no_reply():
    g = Gate()
    for t in ("open the door for him please", "what time is the meeting", "can you pass me the water"):
        assert g.decide(t, 100)[0] is False
    g.last_spoke_at = 95  # even right after Jeb spoke, chatter is not for him
    assert g.decide("what about the other one?", 100)[0] is False


def test_claps():
    assert Gate().decide("", 5, claps=3) == (True, "claps")


def test_answer_to_his_question():
    g = Gate(); g.last_spoke_at = 100; g.expect_reply = True
    assert g.decide("yeah the second one", 105) == (True, "answer")
    assert g.decide("yeah the second one", 106)[0] is False  # consumed
    g.expect_reply = True
    assert g.decide("yeah the second one", 120)[0] is False  # too late


def test_answer_ignores_side_talk_and_typing():
    g = Gate(); g.last_spoke_at = 100; g.expect_reply = True
    assert g.decide("thanks", 103)[0] is False
    g.key("KEY_A", True, 104)
    assert g.decide("the other one", 104.5)[0] is False


def test_wake_words():
    for t in ("Jeff what time is it", "hey jeb open that", "Jev, are you there"):
        assert Gate().decide(t, 100)[0] is True
    assert Gate().decide("listen to this you there", 100)[0] is False


def test_hollow_promise():
    assert hollow_promise("On it, opening the folder.", tool_ran=False) is True
    assert hollow_promise("On it, opening the folder.", tool_ran=True) is False
    assert hollow_promise("SQLite is a file on disk.", tool_ran=False) is False


def test_checking_without_tool_is_hollow():
    assert hollow_promise("Checking disk space. 345 GB free.", tool_ran=False) is True
