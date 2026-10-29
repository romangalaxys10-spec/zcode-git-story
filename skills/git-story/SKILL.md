---
name: git-story
description: Draft commit messages from the actual staged diff, write structured PR descriptions (what / why / how tested), and produce weekly digests. Use when asked to write a commit message, explain what a staged change does, draft a PR body, or summarize the week of work.
---

# git-story

Narrate what actually changed. The source of truth is the diff, not the file
list and not the branch name. A file renamed is not a feature; a config file
touching `max_workers` is a fix candidate. If the diff does not support an
intent, the draft does not claim it.

## Voice rules
- Subject: imperative, under 72 characters, no trailing period.
- Body: 2 to 5 short sentences in plain prose. No em dashes. No "This PR
  improves" openers.
- Admit uncertainty out loud. If you cannot tell whether a change is a fix or
  a refactor, say which two readings the diff allows and which you picked.

## Workflow

### 1. Commit message (draft only, never commit)
```bash
git diff --cached --stat
git diff --cached
python3 scripts/commit_draft.py
```
Read the diff yourself first, then run the script for a draft. The script's
draft is a starting point. Edit it so the subject names the capability, not
the file. Keep the body's why-line only if the diff supports it.

Conventional form:
```
<type>(<scope>): <imperative summary>

<2-5 sentence body explaining WHY, tied to concrete hunks>
```
Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`,
`ci`. Scope = the component, not the filename (prefer the top directory the
change clusters around).

### 2. Pull request description
Structure in exactly this order:
```
## What
<one sentence: capability after, not files>

## Why
<the problem or follow-up that made this change necessary. Cite the commit
that introduced the old behavior if you know it: git log -S 'symbol'>

## How tested
<what was run. If the diff adds no tests, say so plainly: "No new tests;
verified by X." Never claim tests that the diff does not contain.>
```

```bash
git log <base>..HEAD --oneline
git diff <base>..HEAD --stat
```
Where `<base>` is the PR base branch (ask if unknown).

### 3. Weekly digest
```bash
python3 scripts/commit_draft.py --digest
```
Plain voice, grouped by theme (the script groups by commit type and prints a
list; you re-group by what the work was actually about). Target: a paragraph
per theme, each naming the outcome and the one commit that carries it.

Digest rules:
- No "shipped" used more than once per digest.
- Every sentence traces to a commit short hash or a diff.
- If the week is thin, say so. One commit is one line, not a paragraph.

## Honest limits
- This drafts. It does not commit, open a PR, or push. Review the draft.
- Intent is inferred from diffs. A diff that renames 400 files can be a
  migration or a bad reformat. The draft names the uncertainty instead of
  picking silently.
- For PRs, the base must be a commit the PR started from. If you pass the
  wrong base, the diff grows and the description inflates.
