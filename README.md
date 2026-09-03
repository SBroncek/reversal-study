# Short-term reversal in US large caps

**Do stocks that fell hard last week outperform in the following week, and does that
effect survive out-of-sample testing and transaction costs?**

Ten years of daily prices, 99 US large caps, Aug 2016 to Aug 2026. Every week the
cross-section is ranked on its past-week return, cut into quintiles, and each bucket's
next-week return is measured.

**Status: stages 1 and 2 complete. The number below has no error bar on it yet.**
Read the [What is not done yet](#what-is-not-done-yet) section before quoting anything here.

---

## The finding

**The sort is not monotonic. Both extremes beat the middle.**

Mean forward return by bucket, % per week, 521 of 523 weeks:

| bucket | 1 (biggest losers) | 2 | 3 | 4 | 5 (biggest winners) |
|---|---|---|---|---|---|
| mean forward return | **+0.484** | +0.367 | +0.334 | +0.310 | **+0.399** |

Buckets 1 to 4 slide downward exactly as reversal predicts: the harder a name fell, the
better it did next week. Then bucket 5 turns back up above bucket 4. The shape is a **U**,
not a line.

That is worth more than the headline spread, for two reasons.

1. **A monotonic slide is the credibility check for a bucket study.** A smooth gradient
   across five buckets is hard to produce by luck. Bucket 1 alone being large, with 2 to 5
   flat, is usually two good weeks wearing a costume. This sort passes that check on the
   losing side and fails it on the winning side, and the failure is structured rather than
   random.
2. **The U is two effects in one sort.** Reversal at the bottom, momentum at the top. The
   study was designed to test one hypothesis and the data is answering a second one that
   was never asked.

The pre-specified headline number:

> **Spread (bucket 1 minus bucket 5) = +0.0855 % per week.**

The sign points the way reversal predicts. Bucket 5 turning up is what costs the study its
headline: without it the gap would be roughly double.

### The number that was computed and deliberately not reported

**1 minus 4 is +0.174 %/week, and it is not this study's result.**

It was computed, it is larger, and reporting it would mean choosing the flattering pair of
buckets after seeing the data. Bucket 1 versus bucket 5 was specified before the data was
touched, so bucket 1 versus bucket 5 is what gets reported. The alternative is the standard
way of finding the luckiest of thirty coin-flip sequences and calling it a signal.

### How big is +0.0855 % really

Small enough that it is not yet a result.

A crude envelope on the standard error of the final averaged spread puts it near
0.05 %/week, which makes the headline about **1.8 standard errors**. Computing the same
thing with a measured weekly standard deviation rather than a modelled one gives roughly
**1.6**. Both are short of any conventional bar, and both are optimistic, because weeks are
not independent: positive autocorrelation makes a standard error too small, which makes a
study look **more** significant than it is, not less.

On the same crude basis the annualised Sharpe ratio is about **0.51**, against a bar nearer
1 for a fund strategy, and that is **before** transaction costs.

**So: suggestive, not established.** Stage 3 does this properly.

---

## Method

**Universe.** 99 US large caps, chosen from today's index membership. Daily adjusted closes
from Yahoo Finance, cached to local CSV. One further name (MMC) fails to download and is
dropped, leaving 99 of an intended 100.

**Week.** A calendar week anchored on the Friday close. 18.5 % of weeks in the sample are
holiday-shortened to four trading days.

**Signal.** For each stock, its return over the past week. All names are then ranked
**against each other** that week, so the question is never "did it fall 3 %" but "did it
fall further than the other 98 names".

**Forward return.** The same stock's return over the following week, **sharing no days with
the signal window**. Verified by hand rather than asserted: see below.

**Buckets.** The ranked cross-section is cut into 5 equal-sized groups of about 20. Bucket 1
is the biggest losers, bucket 5 the biggest winners. Cutting on **ranks** rather than raw
returns keeps every bucket the same size every week; cutting on raw values would give equal
width return bands, so a calm week might put 2 names in bucket 1 and 60 in bucket 3.

**The reported spread is averaged, not differenced at the end.** The spread is computed
each week and those are averaged, rather than averaging each bucket over ten years and
subtracting once. The two agree exactly when both buckets exist in every week, and when
they do not, the weekly version never compares bucket 1 over one set of weeks against
bucket 5 over a different set.

**Missing data is dropped, never imputed.** A stock with no signal in a given week is
excluded from that week's ranking. Imputing would place a company that did not yet exist
into the middle bucket, and an invented number is worse than no number: a missing value
announces itself, a fabricated one does not.

### Alignment verified by hand

The failure mode in a study like this is not conceptual, it is `.shift(1)` where
`.shift(-1)` was meant. One character, no error raised, and the "forward" return becomes the
signal column itself, so the study reports a perfect relationship.

Checked directly on a single name. AAPL, anchor Friday 27 Mar 2026: 247.55, then 248.36,
then 255.46, giving a signal of +0.33 % and a forward return of +2.86 %, both confirmed
against the three dates read in order. Three structural checks also pass: the signal is
all-NaN on the first anchor, the forward return is all-NaN on the last, and
`signal[t+1] == forward[t]` exactly, which is the no-shared-days rule showing up as an
equation rather than as a promise.

---

## Where this study is wrong

The honest answer to the research question may be no. These are the ways the number above
is flattered, in descending order of how much they matter.

**1. Survivorship, and it is the big one.** The universe is today's membership, so the panel
contains **zero delistings over ten years**. A real 100-stock universe tracked over a decade
does not have zero delistings. Every name in this sample survived by construction. That
biases the study toward optimism, and it does so **most sharply for a signal that buys
losers**, since the historical names that fell hard and then never recovered are precisely
the ones absent from the sample. The study tests "buy the dip" on a sample where every dip
had someone left to recover.

**2. The universe is a genuine look-ahead.** Bucket membership at week t uses only prices up
to t, so the test itself does not look forward. But *picking* the tickers required knowing
which firms still exist in 2026. That leak is baked in and cannot be removed without
point-in-time index membership data.

**3. Equal weighting flatters the result.** Equal weight was chosen because any weighting
scheme is a second hypothesis bolted onto the first, and if the study fails you cannot tell
which half failed. Its cost is real: equal weight tilts toward smaller, less liquid names,
which is exactly where reversal is strongest and where trading costs are highest. The
headline is therefore optimistic and stage 4 is where it gets the bill.

**4. Short weeks are not identically scaled.** A four-day return carries about 89 % of a
five-day one's volatility. The **ranking** is unaffected, since all 99 names share the same
short window that week, so a rank-based study absorbs it. Where it bites is the error bar,
which assumes the weekly observations are the same kind of object, and under a calendar grid
they are not quite. This is roughly an 11 % scale difference on about a fifth of the
observations and is not corrected for.

**5. Execution assumes the closing auction.** Positions are assumed to be entered at the
same Friday close used to compute the signal. That is achievable through the closing
auction, where a large volume genuinely does trade at the official closing print, but
market-on-close orders must be submitted a few minutes before the bell, so the decision is
really made on near-close prices. Reversal is a short-horizon effect and therefore exactly
the kind of signal that decays fastest with delay, so this is measured rather than waved
away: the lagged version, entering at Monday's open, is tested in stage 4.

**6. The grid was a choice.** A week is a calendar week rather than a block of five trading
days. Calendar weeks were chosen because that is the grid a strategy would actually be
rebalanced on, where a five-trading-day block drifts through the weekdays and is not
tradeable as a schedule. The block grid is re-run as a robustness check to confirm the
result does not depend on the choice.

---

## What is not done yet

- **Error bars on the spread**, computed properly, with the week as the unit of observation
  and the weekly standard deviation measured rather than modelled. The numbers in this
  README are envelopes.
- **Autocorrelation** between consecutive weeks, which the current standard error ignores
  and which pushes the result in the unfavourable direction.
- **The parametric cross-check:** regress forward return on signal and read the slope and
  its standard error. It fails differently from the bucket test, since a regression assumes
  linearity and would average a tail-only effect into a weak slope, while buckets assume
  nothing. Agreement between the two is evidence; disagreement is more interesting than
  either number.
- **Robustness at 3, 5 and 10 buckets**, and on the five-trading-day grid. If the conclusion
  flips on the bucket count then there is no result.
- **Out-of-sample split.**
- **Transaction costs.** Does the spread survive 5 bp? 10 bp? At +0.0855 %/week, 5 bp of
  round-trip cost is a large fraction of the whole effect.
- **The Monday-open execution lag.**

---

## Running it

```
python download.py      # fetch and cache the universe, one CSV per ticker
python signal_build.py  # build the signal and forward-return panels
python buckets.py       # rank, bucket, and print the headline table
```

Plain scripts, no notebooks. Each runs top to bottom with no hidden state. Raw data is
cached under `data/` and is not committed.

---

**Sam Broncek.** MMath, University of Warwick, 2025.
