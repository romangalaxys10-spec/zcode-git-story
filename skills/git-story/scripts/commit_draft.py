#!/usr/bin/env python3
"""commit_draft.py -- draft commit messages and digests from git.

Stdlib only. Python 3.8+. Cross-OS.

Modes:
  default  draft a conventional commit message from `git diff --cached`
  --pr     draft a PR description skeleton (what/why/how tested) from the
           working tree vs a base ref
  --digest grouped weekly digest from `git log` (last 7 days)

The draft is always a starting point, never an assertion. If the change type
is ambiguous, the draft says so explicitly and lists the two readings.

Exit codes:
  0 success
  1 git error / nothing staged / not a repo
  2 bad arguments
"""

import argparse
import re
import subprocess
import sys


def fail(code, msg):
    sys.stderr.write(msg + "\n")
    sys.exit(code)


def git(repo, *args, allow_fail=False):
    p = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True)
    if p.returncode != 0 and not allow_fail:
        fail(1, "git error: %s\n%s" % (" ".join(args), p.stderr.strip()))
    return p


# ---------------------------------------------------------------- parsing


def parse_diff(text):
    """Parse a unified diff into per-file entries."""
    files = []
    cur = None
    added = removed = 0
    for line in text.splitlines():
        m = re.match(r"^diff --git a/(.+?) b/(.+)$", line)
        if m:
            if cur is not None:
                cur["add"] = added
                cur["del"] = removed
                files.append(cur)
            cur = {"path": m.group(2), "add": 0, "del": 0, "kind": "modified",
                   "hints": []}
            added = removed = 0
            continue
        if cur is None:
            continue
        if line.startswith("new file mode"):
            cur["kind"] = "added"
        elif line.startswith("deleted file mode"):
            cur["kind"] = "deleted"
        elif line.startswith("rename from"):
            cur["kind"] = "renamed"
        elif line.startswith("+++ ") and not line.startswith("+++ /dev/null"):
            pass
        elif line.startswith("--- ") and not line.startswith("--- /dev/null"):
            pass
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    if cur is not None:
        cur["add"] = added
        cur["del"] = removed
        files.append(cur)
    return files


def scope_from(files):
    """Pick the most common top-level dir across changed paths."""
    tops = {}
    for f in files:
        p = f["path"]
        top = p.split("/", 1)[0] if "/" in p else p
        tops[top] = tops.get(top, 0) + 1
    if not tops:
        return ""
    top, n = max(tops.items(), key=lambda kv: kv[1])
    return top if n >= 1 and len(tops) == 1 else (top if n * 2 > len(files) else "mixed")


HINTS = {
    "test": ("test", "spec", "conftest"),
    "docs": ("readme", "docs/", ".md", "doc/"),
    "ci": (".github/workflows", ".gitlab-ci", "ci/"),
    "build": ("package.json", "setup.py", "pyproject.toml", "cargo", "build"),
    "chore": (".prettierrc", ".eslintrc", "Makefile", "docker", ".gitignore"),
}


def classify(files):
    """Classify type with an explicit confidence. Returns (type, note)."""
    added_n = sum(1 for f in files if f["kind"] == "added")
    deleted_n = sum(1 for f in files if f["kind"] == "deleted")
    renamed_n = sum(1 for f in files if f["kind"] == "renamed")
    total = len(files)
    low_paths = [f["path"].lower() for f in files]

    hints = []
    for key, needles in HINTS.items():
        if any(any(n in p for n in needles) for p in low_paths):
            hints.append(key)

    if renamed_n == total and total > 0:
        return "refactor", "all changes are renames"
    only_docs = all(any(n in p for n in HINTS["docs"]) for p in low_paths)
    if only_docs:
        return "docs", "only documentation files touched"
    if set(hints) <= {"test"}:
        return "test", "only test files touched"
    if set(hints) <= {"ci"}:
        return "ci", "only CI files touched"
    if added_n == total:
        return "feat", "every file is new"
    if added_n >= 1 and deleted_n >= 1 and (added_n + deleted_n) == total:
        return "feat", "adds new files; removing old ones may be a refactor instead (uncertain)"
    if deleted_n == total:
        return "chore", "only deletions"
    if "docs" in hints and "test" in hints:
        return "chore", "mixed docs and test changes; the real intent is unclear from the diff"
    return "feat", "mixed changes; could equally be fix or refactor (uncertain)"


# ---------------------------------------------------------------- drafting


def why_line(files):
    """Build the why-line from concrete hunks. Conservative on purpose."""
    bits = []
    for f in files:
        if f["kind"] == "added":
            bits.append("new file %s (+%d)" % (f["path"], f["add"]))
        elif f["kind"] == "deleted":
            bits.append("removed %s (-%d)" % (f["path"], f["del"]))
        elif f["kind"] == "renamed":
            bits.append("renamed %s" % f["path"])
        else:
            bits.append("%s (+%d/-%d)" % (f["path"], f["add"], f["del"]))
    return "Changed " + ", ".join(bits) + "."


def subject_type(type_, scope, summary):
    s = type_
    if scope:
        s += "(%s)" % scope
    s += ": " + summary
    # keep total subject <= 72 chars
    while len(s) > 72 and len(summary) > 3:
        summary = summary[:-1]
        s = "%s%s: %s" % (type_, ("(%s)" % scope) if scope else "", summary)
    return s


def draft_commit(repo):
    p = git(repo, "diff", "--cached", allow_fail=True)
    if p.returncode != 0:
        fail(1, p.stderr.strip())
    files = parse_diff(p.stdout)
    if not files:
        fail(1, "nothing staged. Stage files with `git add` first.")
    type_, note = classify(files)
    scope = scope_from(files)
    print("# DRAFT -- review before committing.\n")
    print("## Classification")
    print("type: %s  (confidence: %s)" % (type_, "low" if "uncertain" in note or "could" in note else "medium"))
    print("note: %s" % note)
    print()
    print("## Subject options (pick one, keep it <= 72 chars)")
    print("  %s" % subject_type(type_, scope, "update %s" % (scope or "files")))
    print("  %s" % subject_type(type_, scope, "clarify %s" % (scope or "files")))
    print()
    print("## Body (why, from the actual hunks)")
    print()
    print(why_line(files))
    print()
    print("## Uncertainty")
    print("The diff does not state intent. Pick the subject that matches the")
    print("reason you made the change; the body above is derived only from")
    print("what the hunks do. If this is a fix, add one line naming the")
    print("symptom it removes. If it is a refactor, add one line naming the")
    print("invariant it preserves.")


def draft_pr(repo, base):
    p = git(repo, "diff", "%s..HEAD" % base, "--stat", allow_fail=True)
    if p.returncode != 0:
        fail(1, "base ref %r does not resolve here. Is it a commit the PR started from?\n%s" % (base, p.stderr.strip()))
    p2 = git(repo, "log", "%s..HEAD" % base, "--oneline", allow_fail=True)
    files = parse_diff(git(repo, "diff", "%s..HEAD" % base).stdout)
    type_, note = classify(files)
    commits = [l for l in p2.stdout.splitlines() if l.strip()]
    print("## What")
    print("<one sentence: the capability after this PR, not a file list>")
    print()
    print("## Why")
    print("<the problem or follow-up that made this necessary>")
    print("Commit count: %d. Classification hint: %s (%s)" % (len(commits), type_, note))
    print()
    print("## How tested")
    print("<what was run. If the diff adds no test files, say: 'No new tests;")
    print("verified by <manual step>'. Never claim tests the diff does not contain.>")
    print()
    print("Reference commits:")
    for c in commits:
        print("  " + c)


def draft_digest(repo, days):
    p = git(repo, "log", "--since=%d days ago" % days, "--no-merges",
            "--pretty=format:%h\t%s")
    lines = [l for l in p.stdout.splitlines() if "\t" in l]
    if not lines:
        fail(1, "no commits in the last %d days." % days)
    print("# Weekly digest draft (%d commits)" % len(lines))
    print()
    print("Re-group these by what the work was actually about. One paragraph")
    print("per theme. Name the outcome and the commit that carries it.")
    print()
    for sha, subject in lines:
        print("  %s  %s" % (sha, subject))
    print()
    print("Rules: no 'shipped' more than once; every sentence traces to a")
    print("hash; a thin week is one line, not a paragraph.")


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description="Draft commit messages and digests from git.")
    ap.add_argument("--repo", default=".", help="path to repo root (default .)")
    ap.add_argument("--pr", action="store_true", help="draft a PR description instead of a commit")
    ap.add_argument("--digest", action="store_true", help="draft a weekly digest instead of a commit")
    ap.add_argument("--base", default="main", help="base ref for --pr mode")
    ap.add_argument("--days", type=int, default=7, help="window for --digest mode")
    a = ap.parse_args()

    git(a.repo, "rev-parse", "--git-dir")
    if a.pr:
        draft_pr(a.repo, a.base)
    elif a.digest:
        draft_digest(a.repo, a.days)
    else:
        draft_commit(a.repo)
    sys.exit(0)


if __name__ == "__main__":
    main()
