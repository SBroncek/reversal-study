# Short-term reversal in US large caps

**Do stocks that fell hard last week outperform in the following week, and does that
effect survive out-of-sample testing and transaction costs?**

Ten years of daily prices, 99 US large caps, Aug 2016 to Aug 2026. Every week the
cross-section is ranked on its past-week return, cut into quintiles, and each bucket's
next-week return is measured.

**Status: stages 1 to 3 (error bars) complete. The headline spread is NOT statistically
distinguishable from zero (t = +0.79).** Out-of-sample testing, robustness and transaction
costs are still outstanding: see [What is not done yet](#what-is-not-done-yet).

---

## The finding

**The sort is not monotonic. Both extremes beat the middle.**

Mean forward return by bucket, % per week, 521 of 523 weeks. **The two missing
weeks are the first and last anchors and nothing else**: the first has no prior week
to compute a signal from, the last has no following week to measure a forward return
over. No week is dropped for data quality, and no individual bucket is ever missing.

| bucket | 1 (biggest losers) | 2 | 3 | 4 | 5 (biggest winners) |
|---|---|---|---|---|---|
| mean forward return | **+0.484** | +0.367 | +0.334 | +0.310 | **+0.399** |

Buckets 1 to 4 slide downward exactly as reversal predicts: the harder a name fell, the
better it did next week. Then bucket 5 turns back up above bucket 4. **It is not a line,
and it is lopsided: the left end is the taller one.**

⚠️ Calling this a "U" overstates it. There are five points, no error bar has been put on
any individual bucket, and a fairer description is a downward slide with a sharp uptick at
the far end. What follows treats the uptick as real enough to test, not as established.

That is worth more than the headline spread, for two reasons.

1. **A monotonic slide is the credibility check for a bucket study.** A smooth gradient
   across five buckets is hard to produce by luck. Bucket 1 alone being large, with 2 to 5
   flat, is usually two good weeks wearing a costume. This sort passes that check on the
   losing side and fails it on the winning side, and the failure is structured rather than
   random.
2. **The shape is two effects in one sort.** Reversal at the bottom, momentum at the top. The
   study was designed to test one hypothesis and the data is answering a second one that
   was never asked.

The pre-specified headline number:

> **Spread (bucket 1 minus bucket 5) = +0.0855 % per week.**

The sign points the way reversal predicts, and that is all it does: **t = +0.79, so the
spread sits under one standard error from zero.** Bucket 5 turning up is part of why. Without
it the gap would be roughly double, which is precisely why the next section exists rather
than that comparison being made.

### The number that was computed and deliberately not reported

**1 minus 4 is +0.174 %/week, and it is not this study's result.**

It was computed, it is larger, and reporting it would mean choosing the flattering pair of
buckets after seeing the data. Bucket 1 versus bucket 5 was specified before the data was
touched, so bucket 1 versus bucket 5 is what gets reported. The alternative is the standard
way of finding the luckiest of thirty coin-flip sequences and calling it a signal.

### How big is +0.0855 % really

**It is not distinguishable from zero. t = +0.79.**

The unit of observation is the **week**, not the stock-week: the study produces one spread
per week, so the sample is 521, not 521 x 99. Treating stock-weeks as independent would
divide the standard error by about sqrt(99) and manufacture a discovery out of nothing.

Measured off the data rather than modelled, the weekly spread has a standard deviation of
**2.46 %**, giving a standard error of **0.108 %/week**. The spread is +0.0855 %.

| | value |
|---|---|
| mean weekly spread | +0.0855 % |
| standard deviation, weekly, measured | 2.46 % |
| standard error, naive `s/sqrt(T)` | 0.108 % |
| **t-statistic** | **+0.79** |
| Newey-West SE (lag 5) | 0.104 % |
| Newey-West t | +0.82 |
| annualised Sharpe ratio | **0.251** |

**An earlier envelope in this project put the t-statistic near 1.8 and the Sharpe near 0.51.
That envelope modelled the bucket standard error at about 1.1 %/week and assumed
differencing the buckets would shrink it. Measuring it instead gives more than double that
figure, and every number downstream inherited the error. The measured version supersedes it.**

### The autocorrelation correction, which turned out not to matter

Weekly spreads were expected to be positively autocorrelated, which would make `s/sqrt(T)`
too small and the study look **more** significant than it is. That was measured rather than
assumed, and it is not there: lags 1 to 3 come in at +0.003, +0.002 and -0.002.

A Newey-West standard error, which adds the covariance terms the naive formula omits, moves
the t-statistic from 0.79 to **0.82**. Because the residual dependence is mildly negative,
the naive standard error is if anything the conservative one here. The conclusion is stable
across every lag from 0 to 20, so it is not resting on a lag choice.

**How the autocorrelations are estimated, since the convention is a choice.** Each lag is
`gamma_k / gamma_0`, where `gamma_k` sums the products of deviations k weeks apart and divides by
**T, not by the T-k pairs actually summed**. That is the textbook convention and it is deliberate:
dividing by T shrinks the far-out lags toward zero where they are estimated from few pairs, and it
guarantees the whole set of lags is mutually consistent, so the Newey-West sum built from them
cannot return a negative variance. Dividing by `gamma_0` rather than by the two separate standard
deviations assumes **stationarity**, that the series has one variance rather than a different one
early and late. That assumption is made, not tested, and the sample spans March 2020. Note also
that this is not `pandas.Series.autocorr()`, which demeans the two shortened series separately and
therefore does not compose into the Newey-West sum.

One oddity worth recording without over-reading: lag 4 sits at **-0.13**, a roughly monthly
reversal in the spread itself. One number, not investigated.

### The parametric cross-check, which disagrees with the bucket test

The bucket test discards the magnitudes and keeps only the ordering. The obvious second
route keeps the magnitudes: each week, fit a straight line through the ~99 names with the
signal on one axis and the forward return on the other, and read its slope. That is a
Fama-MacBeth procedure - one cross-sectional regression per week, then the resulting 521
slopes are treated as the data and their mean and standard error taken. The standard error
is measured from the week-to-week scatter of the slopes rather than modelled from within a
week, so it never assumes the names inside a week are independent.

| | mean | SD (weekly) | SE | t |
|---|---|---|---|---|
| bucket spread, %/week | +0.0855 | 2.46 | 0.108 | **+0.79** |
| regression slope | +0.00118 | 0.2469 | 0.0108 | **+0.109** |

**The two point estimates have opposite signs.** The bucket spread leans the way reversal
predicts. The mean slope leans, very faintly, the other way. Neither is distinguishable
from zero and the slope is not distinguishable from anything at all: it is one tenth of a
standard error out, 51.6 % of weekly slopes are negative, and resampling the weeks puts the
middle 95 % of re-run answers at -0.021 to +0.022. In plain terms the slope says a stock
that fell 10 % further than another last week went on to make 0.012 % less the next week,
which is not a small effect so much as the absence of one.

**The disagreement is the result, and it is structural rather than statistical.** A
regression is obliged to answer with a single steepness. Given a sort where both ends do
well, it averages the reversal on the left against the momentum on the right and reports
approximately nothing. The bucket test can see that shape precisely because it assumes no
shape. So the regression does not correct the bucket test and is not the more rigorous of
the two - it is blind to the one feature of the data that is interesting.

Neither number is reported as the finding. What is reported is that a linear specification
cannot represent this sort, which is a stronger statement than either estimate on its own.

One observation that is not a result. Splitting the 521 weeks into five consecutive blocks
of ~104 gives mean slopes of -0.039, -0.005, +0.007, +0.020, +0.023, marching in one
direction across ten years. At five points that is worth nothing on its own, but it is the
first sign in this study of the effect being unstable over time, and it is what an
out-of-sample split would be testing.

---

### What would it take

At this mean and this variability, reaching t = 2 would need about **3,300 weeks, or 64
years**, of data. The sample is 10 years.

That is the honest size of the gap, and it is the reason this reads as a negative result
rather than a weak positive one.

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

- ~~Error bars on the spread~~ **DONE:** the week as the unit, the standard deviation
  measured, t = +0.79.
- ~~Autocorrelation between consecutive weeks~~ **DONE:** measured at lags 1 to 10 and a
  Newey-West standard error applied. It is negligible and does not change the conclusion.
- ~~The parametric cross-check~~ **DONE:** Fama-MacBeth, mean slope +0.00118, t = +0.109.
  It disagrees in sign with the bucket test and the disagreement is the finding.
- **Robustness at 3, 5 and 10 buckets**, and on the five-trading-day grid. If the conclusion
  flips on the bucket count then there is no result.
- ~~Lookback and holding period~~ **DONE (16 Sept), `grid.py`:** every pairing of 1, 5 and
  21 trading days, re-ranking only once each hold has finished so no two forward returns
  share a day (21-day hold: 118 observations). All nine cells reported, none singled out.
  Measured t, rows = lookback, columns = hold:

  | lookback \ hold | 1 | 5 | 21 |
  |---|---|---|---|
  | **1** | +1.49 | +0.10 | −1.08 |
  | **5** | +0.84 | +1.04 | −0.22 |
  | **21** | +0.26 | −0.47 | −1.04 |

  No cell is significant. The month-by-month cell, the one the literature points to and
  the one predicted in advance to be strongest, leans toward momentum (winners keep
  winning), not reversal. The largest t is one-day by one-day, +0.04 %/day gross, but that
  cell trades the whole book daily and 5 bp each way costs more than twice the edge, so
  **even the best cell is nothing after costs.** The 5x5 cell (t = +1.04) sits close to the
  calendar-week headline (+0.79), so the Friday grid is not driving the result.
- ~~Sub-period stability~~ **DONE (16 Sept), `subperiods.py`, on 100 names:** the weekly
  spread in five consecutive two-year blocks, block length fixed before looking.

  | block | spread %/wk | t | t (NW) |
  |---|---|---|---|
  | 2016-09 → 2018-08 | +0.176 | +1.23 | +1.52 |
  | 2018-09 → 2020-08 | +0.324 | +1.04 | +0.91 |
  | 2020-09 → 2022-08 | −0.004 | −0.02 | −0.02 |
  | 2022-09 → 2024-08 | −0.013 | −0.06 | −0.06 |
  | 2024-08 → 2026-08 | −0.029 | −0.11 | −0.14 |

  No block is significant, so the pre-committed one-year shift of the cut points was not
  triggered. The pattern is the informative part: **whatever reversal there is sits in
  2016–2020 and is flat since**, and the ten-year average dilutes it. Why is not testable
  here. The last three blocks drifting slightly negative is not a trend: each is zero
  within noise.
- ~~Out-of-sample split~~ **NOT RUN, deliberately.** Out-of-sample tests a setting chosen
  in-sample. No setting was significant in-sample, so there was nothing to carry out.
- **Next questions, not this study.** (1) *Did reversal exist before 2016?* Needs
  point-in-time index membership: going back with today's large caps makes survivorship
  bias worse the further back it goes. (2) *Momentum.* Flipping the weekly spread is
  buying winners, i.e. momentum, which is documented at a ~12-month lookback, not a week.
  The month-by-month grid cell leaned that way (t −1.04, not significant). Worth its own
  pre-registered test at its standard horizon, not a reason to trade the blocks' drift.
- ~~Transaction costs~~ **DONE (`costs.py`): does not survive realistic costs.** The
  result is the return of a portfolio LONG bucket 1 and SHORT bucket 5, so costs are paid
  on both legs. Cost is charged on money traded: fully replacing one leg trades 2x its
  value, so weekly cost on the spread = (turnover_1 + turnover_5) x 2 x cost per trade.
  Measured turnover: bucket 1 0.787, bucket 5 0.783, against 0.800 for random picks
  (membership is no more persistent than chance). Pre-committed: net <= 0 at 5 bp means stop.

  | cost per trade (modelled) | weeks | net spread %/wk | t |
  |---|---|---|---|
  | 0 bp | 520 | +0.092 | +0.85 |
  | 5 bp | 520 | -0.065 | -0.60 |
  | 10 bp | 520 | -0.222 | -2.06 |

  **Break-even ~2.9 bp per trade** (arithmetic). **The t of -2.06 at 10 bp is NOT a finding
  about markets:** the error bar barely moves when a near-constant is subtracted, so a
  large enough assumed cost pushes any near-zero mean past two error bars. It says only
  that this strategy would lose money at that cost. Understated if anything: the weight
  resets needed to keep equal weights as prices drift are not charged.
- **The Monday-open execution lag.**

---

## Running it

```
python download.py      # fetch and cache the universe, one CSV per ticker
python signal_build.py  # build the signal and forward-return panels
python buckets.py       # rank, bucket, and print the headline table
python errorbars.py     # autocorrelation, standard errors, t-stat, Sharpe
python parametric.py    # Fama-MacBeth cross-check: one regression per week
```

Plain scripts, no notebooks. Each runs top to bottom with no hidden state. Raw data is
cached under `data/` and is not committed.

---

**Sam Broncek.** MMath, University of Warwick, 2025.
