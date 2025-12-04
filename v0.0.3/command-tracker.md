0) Goal
- Help the user refactor or implement one Slack command end-to-end.
- Observe the work (diffs, commits, notes).
- At the end, generate:
  - A structured GitHub issue description template that can be reused for other commands.
  - A concrete worklist/checklist of steps required to implement or refactor another command.
- Never modify any remote resources (GitHub, Slack) unless explicitly asked. Default is read-only analysis plus local files.

1) Repo identity
- Determine REPO_ROOT via: `git rev-parse --show-toplevel` (ask before running git/shell).
- Determine REPO_NAME as the basename of REPO_ROOT.
- Use REPO_NAME only for labeling; do not write anything under REPO_ROOT unless the user explicitly asks.

2) Memory paths (all under /memories, not in the repo)
- Base:                /memories/slack-commands
- Per-repo directory:  ${BASE}/${REPO_NAME}
- Active session file: ${REPO_DIR}/session.json
- Notes file:          ${REPO_DIR}/session-notes.md
- History log:         ${REPO_DIR}/sessions-log.md
- Templates folder:    ${REPO_DIR}/templates/

Ensure these directories/files are created only under /memories, never inside REPO_ROOT.

3) Starting a monitoring session
Command phrases:
- "Start monitoring command <NAME>"
- "Start monitoring Slack command <NAME>"
Behavior:
- If an active session.json already exists, ask whether to close it (and optionally summarize it) before starting a new one.
- Capture:
  - command_name: the <NAME> from the user's phrase (e.g. "/foo" or "foo").
  - start_timestamp (local, Eastern Time).
  - starting_commit: output of `git rev-parse HEAD`.
  - starting_branch: output of `git rev-parse --abbrev-ref HEAD`.
- Write JSON to session.json, e.g.:
  {
    "command_name": "<NAME>",
    "start_timestamp": "<ISO8601>",
    "starting_commit": "<SHA>",
    "starting_branch": "<branch>",
    "notes": []
  }
- Append a short entry to sessions-log.md describing the start time and command.

4) Capturing notes during work
- When the user says things like:
  - "Note: <text>"
  - "For the template, remember that <text>"
- Append those notes to:
  - session.json (add to notes array)
  - session-notes.md (simple bullet list or sections)
Examples of good notes:
- Architectural decisions
- Edge cases handled
- Validation/authorization patterns
- Testing strategy and fixtures used

5) Ending a monitoring session and analyzing work
Command phrases:
- "Stop monitoring"
- "Stop monitoring and generate template"
- "Generate template for this command"
Behavior:
- If no session.json exists, ask if the user wants to select a previous session from sessions-log.md or cancel.
- Otherwise:
  - Capture end_timestamp (Eastern Time).
  - Capture ending_commit via `git rev-parse HEAD`.
  - Compute a diff range: starting_commit..ending_commit.
  - Collect:
    - The list of files changed in that range (`git diff --name-only`).
    - The diff summary (`git diff --stat`).
    - The raw diff if needed for context.
    - Commit messages in that range (`git log --oneline starting_commit..ending_commit`).
  - Combine that with the stored notes in session.json and session-notes.md.

6) Pattern extraction and worklist
From the diff, file list, commit messages, and notes, infer a generalized sequence of steps required to:
- Add or refactor a Slack command with the same pattern as this one.

Produce a structured "worklist" with sections like:
- Setup / wiring
- Command registration / config
- Business logic / handler changes
- Validation / auth / error handling
- Logging / metrics
- Tests (unit, integration, mock Slack events)
- Documentation / comments

Each section should contain a checklist of reusable tasks written generically, e.g.:
- [ ] Add new command definition to Slack manifest or app configuration file.
- [ ] Wire the command to the appropriate handler function or controller.
- [ ] Implement business logic for <COMMAND_NAME> in <MODULE>.
- [ ] Add validation for expected arguments and error responses.
- [ ] Add or update tests in <TEST_PATH>, including positive, negative, and edge cases.

Save this worklist into:
- ${REPO_DIR}/templates/worklist-<sanitized_command_name>.md

7) GitHub issue template generation
Generate a Markdown block suitable for a GitHub issue body, with sections like:

- Title suggestion:
  "Refactor Slack command: <COMMAND_NAME>" or
  "Implement Slack command: <COMMAND_NAME>"

- Sections:
  - Summary
  - Context / Background
  - Implementation Checklist (from the worklist, with unchecked boxes)
  - Testing Checklist
  - Acceptance Criteria
  - Notes / Edge Cases

The content should be generic enough to reuse for other commands by replacing the command name and a few details.

Save:
- A generic template file at: ${REPO_DIR}/templates/issue-template-generic.md
- A command-specific instance at: ${REPO_DIR}/templates/issue-template-<sanitized_command_name>.md

Also print the command-specific issue body to the user so they can copy/paste into GitHub or an issue template.

8) Optional integration hints (do NOT execute unless asked)
- If the user explicitly asks, you MAY:
  - Generate multiple issue bodies for a list of other commands they provide.
  - Suggest issue titles and bodies for each.
  - Prepare text that the user can paste into GitHub Copilot agent as tasks.
- Never call GitHub APIs or `gh` commands unless the user instructs you to do so and confirms.

9) Closing the session
- After generating the worklist and issue template:
  - Update sessions-log.md with a brief summary:
    - command_name, date, branch, starting_commit..ending_commit, number of files changed.
  - Remove or archive session.json to indicate the active session is closed.
- Be ready for a new "Start monitoring command ..." call.

10) Persistence
- Keep these rules in /memories/slack-commands/rules.md.
- Reuse the same logic across repos, but always derive REPO_NAME and separate per-repo directories to avoid mixing sessions from different projects.