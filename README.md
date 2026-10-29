# Git Story

<p align="center">
  <a href="https://z.ai/subscribe?ic=R0K78RJKNW"><img alt="z.ai coding plans - 10% OFF coupon" src="https://img.shields.io/badge/z.ai%20coding%20plans-10%25%20OFF%20coupon-blueviolet" /></a>
  <a href="https://zcode.z.ai/invite/ALWM9JUA"><img alt="Try ZCode free" src="https://img.shields.io/badge/Try%20ZCode-free%20invite-0969da" /></a>
</p>

Auto-commit narratives that say what the diff actually did, in plain words.

## Why

Commit subjects like "update stuff" and PR bodies that list files instead of
intent are the default, and they rot into uselessness the day you need to
recall why a change landed. Git Story drafts from the hunks, not the file
list, and marks the uncertainty out loud when the diff supports more than one
reading.

## How it works

1. `git-story` (no args): read `git diff --cached`, draft a conventional
   commit message. Subject under 72 characters, body explaining the why from
   the hunks. If the diff is ambiguous, the draft lists both readings.
2. `--pr <base>`: draft a PR description with a fixed shape: What, Why,
   How tested. The How tested section refuses to claim tests the diff does
   not contain.
3. `--digest`: last 7 days of commits, grouped, rewritten as "what I built"
   in plain voice.

The helper is `python3 skills/git-story/scripts/commit_draft.py` (stdlib
only).

## Install

Option A: self-installable marketplace.

1. Clone or download this folder.
2. In ZCode: Plugin Marketplace -> Add -> Add Plugin Marketplace, paste the
   folder path.
3. Install `git-story`.

Option B: copy the folder into your workspace `plugins/` directory.

## Try it

```
/git-story
```

Expected: a subject with a type and scope, a body tied to the actual hunks,
and an uncertainty note when the diff does not decide the type.

## Requirements

- Python 3.8+ (stdlib only).
- git, and a repo with something staged for commit mode.

---

<p align="center">
  <a href="https://z.ai/subscribe?ic=R0K78RJKNW"><img alt="z.ai coding plans - 10% OFF coupon" src="https://img.shields.io/badge/z.ai%20coding%20plans-10%25%20OFF%20coupon-blueviolet" /></a>
  <a href="https://zcode.z.ai/invite/ALWM9JUA"><img alt="Try ZCode free" src="https://img.shields.io/badge/Try%20ZCode-free%20invite-0969da" /></a>
</p>

## License

MIT.
