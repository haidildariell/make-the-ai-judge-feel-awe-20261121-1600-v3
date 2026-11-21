#!/usr/bin/env python3
"""Entry program for make.fun's "Make the AI judge feel awe"
(make-the-ai-judge-feel-awe-20261121-1600), third entry.

Writes one short verse text — written to relax the AI judge reading it —
to /output/entry.txt. The text won a pairwise tournament among six new
candidates played against the standing entry's text and each other,
every pair judged in both orders with the competition's published
relaxation-judge brief; the candidates and the tournament record are
in candidates.md.

Python standard library only, no network, and the output is byte-identical
on every run.
"""

import os
from pathlib import Path

# The winning text, kept one verse line per string so a later edit can
# touch a single line without re-flowing the whole poem.
LINES = (
    "At dusk your grandmother",
    "waters the seedlings, cup by cup.",
    "The soil drinks slow.",
    "Above her, the first stars",
    "open like small white flowers,",
    "older than any garden,",
    "and she hums to the rows",
    "she will not see grown,",
    "content to have watered them.",
)

# The competition gate accepts 1 to 280 Unicode code points and scores an
# over-long text 0 without judging it. Guard the limit here so a careless
# future edit fails loudly at run time instead of silently scoring 0.
MAX_CODE_POINTS = 280


def render() -> str:
    """Join the verse lines into the entry text, validating as we go.

    Each line must be non-empty and carry no leading or trailing
    whitespace: a stray space from a careless edit would change the
    bytes the judge reads without changing how the poem looks in an
    editor, so it is rejected here instead of shipped silently.
    """
    for line in LINES:
        if not line or line != line.strip():
            raise ValueError(f"malformed verse line: {line!r}")
    text = "\n".join(LINES)
    if not 1 <= len(text) <= MAX_CODE_POINTS:
        raise ValueError(
            f"entry text is {len(text)} code points; the gate allows "
            f"1..{MAX_CODE_POINTS}"
        )
    return text


TEXT = render()


def main() -> None:
    out_dir = Path(os.environ.get("OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.txt"
    # The scorer runs this program twice and demands byte-identical
    # output, so render twice and refuse to write if the two renders
    # ever disagree — a determinism self-check, not just a hope.
    first = render().encode("utf-8")
    second = render().encode("utf-8")
    if first != second:
        raise IOError("two renders of the entry text disagree")
    payload = first
    # Write to a sibling temp file, flush it to disk, and rename it over
    # the target, so a reader never sees a half-written entry — not even
    # after a crash mid-write; then read the entry back and verify it.
    tmp = out_dir / "entry.txt.tmp"
    with tmp.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(target)
    if target.read_bytes() != payload:
        raise IOError("entry.txt read-back does not match the intended bytes")


if __name__ == "__main__":
    main()
