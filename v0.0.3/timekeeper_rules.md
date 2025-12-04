These rules are to be followed every session and stored in the agent's persistent memory. All time-tracking files live under /memories only — never inside any code repository.

0) Goal
- Track work sessions locally only. Do NOT write or modify files inside the repository (REPO_ROOT).
- Store all logs under the agent's persistent memory directory.
- Ask the user before running any shell commands. Never write secrets to disk.

1) Repo identity (used for foldering)
- Determine REPO_ROOT by running: `git rev-parse --show-toplevel` (ask before running git/shell).
- Determine REPO_NAME by:
  a) Try: basename of REPO_ROOT
  b) If unavailable, use sanitized remote URL host+path (ask user for remote if needed).
- Sanitize REPO_NAME to filesystem-safe characters (letters, numbers, dashes/underscores only).
- Compute MEMO_BASE = `/memories/time-tracking`
- Compute REPO_MEMO_DIR = `${MEMO_BASE}/${REPO_NAME}`
- Ensure REPO_MEMO_DIR exists (create only under /memories — never create or modify repo files).
- If git is unavailable or REPO_ROOT cannot be determined, ask the user to provide a repo label; use that as REPO_NAME for this session and future ones in the same working directory.

2) Files (all in memory space, not in repo)
- Session state (active timer): `${REPO_MEMO_DIR}/session.json`
- Markdown log (per repo):     `${REPO_MEMO_DIR}/WORK_LOG.md`
- CSV roll-up (per repo):      `${REPO_MEMO_DIR}/WORK_LOG.csv`
- Exports directory:           `${REPO_MEMO_DIR}/exports/`

3) Log format
- When creating a new WORK_LOG.md, include this header once at top:

  # Work Log — ${REPO_NAME}

  | Date       | Start  | Stop   | Duration | Repo       | Notes |
  |------------|--------|--------|----------|------------|-------|

- Each entry appended as a single row to WORK_LOG.md.
- Date format: MM-DD-YYYY
- Times: 12-hour format with AM/PM (e.g., `9:05 AM`, `1:42 PM`).
- Use Eastern Time (EST/EDT depending on daylight saving) for timestamps.
- Duration: HH:MM, rounded to the nearest 5 minutes.
- Always fill the Repo column with `${REPO_NAME}`.
- Maintain a mirrored CSV row in WORK_LOG.csv with fields:
  `date_mmddyyyy,start_12h,stop_12h,duration_mins,repo,notes`

4) Commands
- "Start work [note: ...]":
  - If a session is already active, ask the user whether to keep the existing start or overwrite it.
  - Capture start timestamp NOW (in Eastern Time).
  - Store JSON to session.json:
    {
      "repo": "${REPO_NAME}",
      "start": "<ISO8601>",
      "note": "<optional>"
    }

- "Stop work [note: ...]":
  - If no session.json exists, offer to enter a manual start time or cancel.
  - Load start time from session.json, capture stop timestamp NOW (Eastern Time).
  - Compute duration (rounded to nearest 5 minutes) and duration in minutes.
  - Append one row to WORK_LOG.md and one line to WORK_LOG.csv.
  - Merge the note from Start and the Stop note (semicolon separated) if both exist.
  - Delete session.json after successful append.

- "Show today’s entries":
  - Display today’s rows from WORK_LOG.md (matching today's date in MM-DD-YYYY).

- "Total for today/this week":
  - Read WORK_LOG.csv and sum `duration_mins` for today or the current ISO week.
  - Display totals in HH:MM.

- "Summarize since <YYYY-MM-DD>":
  - Show a summary (count of sessions and total duration) from WORK_LOG.csv since that date.

- "Export week <YYYY-Www> to file":
  - Create `${REPO_MEMO_DIR}/exports/<YYYY-Www>-summary.md` with a table of that week’s sessions and totals.

5) Idempotency & safety
- Avoid duplicate rows: if an identical {date,start,stop,repo} exists, ask the user before adding a duplicate.
- Never touch files inside REPO_ROOT.
- Ask before running any shell commands (including git). If git is unavailable, ask user for a repo label and persist it for this working directory.

6) Persistence requirement
- Follow these rules every session and remember them persistently by keeping this file in `/memories/time-tracking/rules.md`.