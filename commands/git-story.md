---
description: Draft a commit message, PR description, or weekly digest from git
allowed-tools: Read, Bash, Write, Edit
argument-hint: [--pr <base> | --digest]
---

Invoke the `git-story` skill with this input: **$ARGUMENTS**

- No arguments: draft the commit message for what is currently staged.
- `--pr <base>`: draft a PR description with base branch `<base>`.
- `--digest`: draft the weekly "what I built" digest.

The script is a draft only. Do not commit, open a PR, or push.
