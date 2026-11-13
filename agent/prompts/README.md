# System prompts

Customize the system prompt Cappy uses on each bot surface by adding a markdown
file here. These files are versioned with the rest of your context, so prompt
changes stay reviewable in pull requests just like `RULES.md`.

## Files

One file per surface:

- `system.md` — applies to every surface (Cappy web Bot, Slack, Teams, …).
- `slack.md` — Slack Bot only.
- `teams.md` — Microsoft Teams Bot only.
- `telegram.md` — Telegram Bot only.
- `mattermost.md` — Mattermost Bot only.
- `whatsapp.md` — WhatsApp Bot only.
- `automation.md` — scheduled automations only.

A surface-specific file (e.g. `slack.md`) takes precedence over `system.md`.
Delete a file to fall back to Cappy's built-in prompt for that surface.

## Replace vs. extend: `{{ cappy_prompt }}`

By default a prompt file **fully replaces** Cappy's built-in prompt for that
surface. If instead you want to **keep** the default and only add to it, include
the `{{ cappy_prompt }}` placeholder somewhere in the file: it is replaced at
runtime with Cappy's default prompt for the corresponding surface (in `slack.md`
it expands to the default Slack prompt, in `system.md` to the web prompt, …).

Example `slack.md` that extends the default instead of overriding it:

```md
{{ cappy_prompt }}

## House rules
- Always answer with amounts in EUR.
- Keep responses to 5 bullet points or fewer.
```

Without `{{ cappy_prompt }}`, the file content becomes the entire prompt.
