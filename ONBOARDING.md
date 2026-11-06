# First-run onboarding

Use this flow when a person says they want to set up Class Prep Email Digest. Ask one question or request one connection at a time; do not show a long form.

## 1. Explain the scope

Say: “I’ll send one daily class-prep email using your active Canvas courses and your upcoming calendar. I will not download course files, change Canvas, or modify your calendar.”

## 2. Connect Google services

Ask the person to connect or authorize, in this order:

1. **Gmail send access** — used only to send the digest back to their authenticated address.
2. **Google Calendar read access** — used only to read upcoming commitments.

Use the host's native OAuth / connector consent screen. Never collect a Google password, OAuth code, or refresh token in chat or a project file. If either connection is unavailable, stop and tell the user which connection must be completed.

## 3. Collect Canvas access

Ask the user to set their token from the terminal with hidden input:

```sh
read -s "CANVAS_ACCESS_TOKEN?Paste Canvas token: "
export CANVAS_ACCESS_TOKEN
```

Never request that the token be pasted into the agent chat. This stores it only for the current terminal session.

Validate access by running `python3 fetch_canvas_snapshot.py`. If it fails, identify whether the URL, token, or Canvas permissions need correction without echoing the token.

## 4. Collect schedule

Ask: “What time and timezone should I send your daily digest?”

Save the timezone in `config.json` and create a daily recurring task with the agent host at the requested local time. Do not ask the user to choose courses, content sections, or Drive behavior.

## 5. Confirm and send the first digest

Report the number of active Canvas courses detected and the recipient email returned by Gmail. Send the first digest only after the person confirms setup is complete, then enable the recurring schedule.

## Returning users

Do not rerun onboarding. Use their existing connector authorizations, `config.json`, and schedule. Reconnect only the service that fails.
