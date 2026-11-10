Back to [[Home]]

# Agents get every Claude Code skill/plugin (2026-11-09)

- `user_agent_tools()` in `jev.py` now copies skills + commands from ALL 39 installed plugins (switched on or off in Claude Code) plus `~/.claude/skills` → 616 skills, incl. superpowers (15) and ECC (314). Skills load on demand.
- Still excluded on purpose: plugin hooks and CLAUDE.md (they'd inject text/run scripts every turn and break the spoken voice); MCP servers only from plugins switched ON (each server slows agent start).
- Main quick replies stay lean (no plugins) for zero delay; background agents (coding, research, long tasks) carry the full kit. Setting: `agentUserTools` (on by default).
