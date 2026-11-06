# Class Prep Email Digest

One daily email that tells a student what matters next. It reads their active Canvas courses, relevant upcoming calendar commitments, and a few high-signal inbox actions, then sends a concise, phone-friendly class-prep digest.

The purpose is to replace repetitive checking across Canvas, Calendar, and Gmail with one reliable morning view: what is due, what changed, and what needs preparation. It is deliberately email-only—no Drive sync, dashboard, course picker, or content-download pipeline.

## What it does

- Finds every active Canvas course, including paginated course, assignment, and module results.
- Highlights overdue, unsubmitted, due-today, and seven-day upcoming Canvas work.
- Compares the most recent Canvas snapshot with the previous one to surface meaningful changes.
- Reads the next seven days of Google Calendar and includes only commitments relevant to preparation.
- Identifies a small set of time-sensitive academic or meeting actions from recent Gmail, excluding newsletters, receipts, and promotions.
- Sends one compact HTML email to the same authenticated Gmail account, at a time selected by the user.
- Avoids duplicate sends within a local calendar day.

It never modifies Canvas or Google Calendar, downloads course content, creates Drive folders, or stores credentials in this repository.

## What each person authorizes

1. **Canvas API token** — read active courses, assignments, and modules.
2. **Google Calendar read access** — include commitments that affect class preparation.
3. **Gmail send access** — send the digest back to the user's authenticated email address.
4. **Time and timezone** — the only user preference.

The workflow automatically covers active Canvas courses. It does not ask users to customize individual courses or sections.

## Run with Codex or Claude Code

Both agents read the same portable workflow:

| Agent | Entry file |
| --- | --- |
| Codex | `CODEX.md` |
| Claude Code | `CLAUDE.md` |

The host agent needs Gmail and Google Calendar tools/connectors available. This repository does not store Google passwords, OAuth refresh tokens, or Canvas tokens.

### First-time onboarding

On the first run, the agent uses its native connection choices to request Gmail and Google Calendar authorization, then asks only:

1. What is your Canvas school URL?
2. Open the agent terminal and set the Canvas token with hidden input.
3. What time and timezone should the digest arrive?

`ONBOARDING.md` makes that sequence identical for Codex and Claude Code. Returning users skip these questions unless a connection fails.

## Setup

### Prerequisites

- Python 3.10 or later.
- A Canvas account that permits personal access tokens.
- Gmail permission to send an email to the authenticated user.
- Google Calendar read permission.
- Codex or Claude Code with their Gmail and Google Calendar integrations connected.

### 1. Clone and configure

```sh
cd class-prep-email-digest
cp config.example.json config.json
```

Edit the ignored `config.json` with the Canvas URL and timezone. You can use the user’s Gmail account by keeping `"recipient": "me"`.

### 2. Create and set a Canvas token

In Canvas, go to **Account** → **Settings** → **Approved Integrations** → **+ New Access Token**. Give it a recognizable name, create it, and copy it immediately.

In the Codex or Claude Code terminal, set the token with hidden input:

```sh
read -s "CANVAS_ACCESS_TOKEN?Paste Canvas token: "
export CANVAS_ACCESS_TOKEN
```

Paste the token when prompted and press Return. It will not appear on screen. The token is never placed in chat, `config.json`, or Git.

### 3. Test Canvas

```sh
python3 fetch_canvas_snapshot.py
```

On success, the command reports a course count and creates `state/current.json`. This credential-free snapshot is what the agent reads to compose the digest.

### 4. Run and schedule with your preferred agent

Then tell Codex or Claude Code: “Read `AGENTS.md` and `AUTOMATION_PROMPT.md`, then run my daily class prep digest.” Connect Gmail and Google Calendar when prompted.

To schedule it, use the agent host's built-in recurring-task feature at the chosen time, rather than a machine-specific cron job. The workflow protects against duplicate daily emails in `state/last-successful-send-date`.

## Privacy and limits

- Canvas access stays read-only and the token exists only in the process environment.
- Calendar is read-only.
- Gmail only sends one digest to the authenticated user.
- Course material is not downloaded, summarized, or uploaded to a third-party storage service.
- Email results depend on what Canvas exposes through its API and what the user grants Google access to.

## Agent compatibility

The workflow is provider-neutral: Canvas retrieval happens through Python, while email and calendar operations use the host agent's configured integrations.

| Capability | Codex | Claude Code |
| --- | --- | --- |
| Daily instructions | `CODEX.md` | `CLAUDE.md` |
| Shared safety and workflow rules | `AGENTS.md`, `AUTOMATION_PROMPT.md` | `AGENTS.md`, `AUTOMATION_PROMPT.md` |
| Gmail / Calendar authorization | Connectors in the host | Integrations available in the host |
| Schedule | Host recurring-task feature | Host recurring-task feature |

The repository does not depend on one proprietary email SDK or Canvas library. An agent host only needs to provide Gmail send and Calendar read access.

## Repository layout

```text
AGENTS.md                shared operational and safety rules
ONBOARDING.md            first-run conversational setup
AUTOMATION_PROMPT.md     shared daily workflow
CODEX.md / CLAUDE.md     agent-specific entry points
fetch_canvas_snapshot.py portable Canvas API reader
config.example.json      safe configuration template
state/                   ignored local snapshots and duplicate-send guard
```

## Contributing

Keep credentials, real snapshots, private email content, and personal course data out of commits. Run `python3 -m py_compile fetch_canvas_snapshot.py` before opening a pull request.
