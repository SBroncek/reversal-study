# reversal-study

A short-term reversal study on US large-cap equities. Portfolio project for quant
research applications (systematic funds: QRT, G-Research, Squarepoint, Man AHL).

**Owner: Sam Broncek.** MMath Warwick 2025. Strong maths and statistics, competent
Python (pandas, NumPy), no prior experience with financial time series.

## The research question

Do stocks that fell hard last week outperform in the following week, and does that
effect survive out-of-sample testing and transaction costs?

The honest answer may be no. **A well-executed negative result is a success here.**

## What "done" looks like

1. Daily prices for ~100 US large caps, ~10 years, cached to disk.
2. Signal: previous week's return, negated. One number per stock per week.
3. Each week, sort into 5 buckets by signal, hold one week, compare mean forward returns.
4. Out-of-sample split, with a standard error on the top-minus-bottom spread.
5. Transaction costs applied. Does the spread survive 5bp? 10bp?
6. A README that states the finding plainly, including the ways it could be wrong.

## HOW TO WORK WITH SAM ON THIS  <-- read this before writing any code

The point of this repo is that Sam can defend **every line** of it in an interview.
Code he did not write and cannot explain is worse than no code at all.

- **You write:** environment setup, data download, plotting, pandas idioms, bug fixes.
- **Sam writes:** the signal construction, the forward-return alignment, the bucketing,
  and every evaluation decision. Do not write these for him.
- For Sam's lines: **explain the shape and let him type it.** Propose, do not implement.
  If he is stuck, give the smallest hint that unblocks him, not the answer.
- **One step at a time.** Do not run ahead to the next stage of the study.
- **Do not teach the finance. Build, and gloss in passing.** One sentence per term,
  plain English, no lecture. Deep explanation happens in a separate mentor session and
  a wall of domain theory here just blocks the build. If a concept needs more than a
  sentence, say "worth asking your mentor session about X" and carry on coding.
- **Never overwrite an existing file without reading it first** (a .gitignore was
  clobbered this way on day one).
- Be blunt about lookahead bias, survivorship bias, and overfitting whenever the code
  gets near them. These are the failure modes the whole project exists to demonstrate.

## Conventions

- **Claude commits, without being asked** (Sam's call, 28 Aug). At any point the tree
  is in a coherent state -- a script runs, a check passes, a decision lands -- commit
  it, with a message that says *why*, not just what. Pushing is fine too. Do not sit
  on two sessions of work again: `universe.py` and `signal_build.py` went uncommitted
  from 25-28 Aug, so the repo showed one commit while three days of work existed.
  (This is the opposite of the vault rule, where the Obsidian Git plugin owns commits.
  Different repo, different rule.)
- **Explain every line you write, as you write it** (restated by Sam, 28 Aug). Not a
  summary afterwards. This does not replace the rule above about which lines are
  Sam's to type -- it applies to the lines that are Claude's.

- Plain `.py` scripts, not notebooks. Scripts diff cleanly and read better on GitHub.
- Raw data cached under `data/` and gitignored. Never re-download in a hot loop.
- Every script runs top to bottom on its own with no hidden state.

## Strategy context lives elsewhere

Career strategy, target firms and prep sit in Sam's Obsidian vault
(`03 Projects/Employment`), which is the mentor side of this work. Do not expect it
here. Context flows one way: vault -> this file.
