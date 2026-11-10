Back to [[Home]]

# Tests

- `tests/test_persona.py` 4/4 (personality once in prompt, safety words, coding rule, switched-off plugin → skills yes, MCP no). Existing `test_task_only_plugins_do_not_copy_hooks_or_claude_instructions` still passes.
- `test_disabled_tool_and_prompt_budget` fails on Linux only: Linux prompt was 13,877 chars before this work (Mac-only 10,050 budget); budget now + `len(PERSONALITY)`.
