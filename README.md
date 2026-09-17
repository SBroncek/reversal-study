# Short-term reversal in US large caps, a negative result

**Over ten years, last week's biggest losers did not reliably beat last week's biggest
winners the following week, and a strategy long the losers and short the winners loses
money once trading costs of 5 basis points are charged.**

100 US large caps, weekly, September 2016 to August 2026. Every week the stocks are
ranked against each other on their past week's return and cut into five equal buckets.
The result reported throughout is the return of a portfolio that is long bucket 1, the
biggest losers, and short bucket 5, the biggest winners.

| | spread, % per week | t |
|---|---|---|
| before costs | +0.091 | +0.84 |
| after 5 basis points | -0.065 | -0.60 |

Even the before-costs figure is flattered. The universe is today's survivors, which
matters most for a strategy that buys losers. See [Where this study is
wrong](#where-this-study-is-wrong).

**The sample is 521 weeks throughout, and 520 wherever costs are charged.** The week is
the unit of observation, not the stock-week. Every number below is measured on the data
unless it is labelled modelled.

---

## What was done

| stage | status |
|---|---|
| Universe, prices, caching | done |
| Signal, forward return, alignment verified by hand | done |
| Buckets and the headline spread | done |
| Standard errors, autocorrelation, Newey-West | done |
| Parametric cross-check, Fama-MacBeth | done |
| Robustness, bucket count, lookback and holding grid, sub-periods | done |
| Transaction costs | done, and the result does not survive them |
| Out-of-sample split | not run, deliberately, and the reason is below |
| Monday-open execution lag | not run |

---

## The headline

Mean forward return by bucket, in % per week, over 521 weeks.

| bucket | 1, biggest losers | 2 | 3 | 4 | 5, biggest winners |
|---|---|---|---|---|---|
| mean forward return | **+0.487** | +0.370 | +0.331 | +0.306 | **+0.396** |

> **Spread, bucket 1 minus bucket 5, is +0.091 % per week, t = +0.84.**

The sign points the way reversal predicts and that is all it does. The spread sits less
than one standard error from zero.

**One observation about the shape, recorded and not built on.** Buckets 1 to 4 slide
downward as reversal predicts, and bucket 5 then turns back up above bucket 4. That could
be reversal at one end and momentum at the other, but it is five points with no error bar
on any individual bucket, and it is not offered as a finding. The sub-period test below
shows the spread itself is not stable over the decade, which is a reason to treat any
feature of a ten-year average sort cautiously.

### The number that was computed and deliberately not reported

**Bucket 1 minus bucket 4 is +0.182 % per week, and it is not this study's result.**

It was computed, it is twice the headline, and reporting it would mean choosing the
flattering pair of buckets after seeing the data. Bucket 1 against bucket 5 was specified
before the data was touched, so that is what gets reported. The alternative is the
standard way of finding the luckiest of thirty coin-flip sequences and calling it a signal.

### How big is +0.091 % really

**It is not distinguishable from zero.**

The unit of observation is the week. The study produces one spread per week, so the sample
is 521 and not 521 times 99. Treating stock-weeks as independent would divide the standard
error by roughly the square root of 100 and manufacture a discovery out of nothing.

| | value |
|---|---|
| mean weekly spread | +0.0910 % |
| weekly standard deviation, measured | 2.4599 % |
| standard error, s over root T | 0.1078 % |
| **t-statistic** | **+0.84** |
| Newey-West standard error, lag 5 | 0.1042 % |
| Newey-West t | +0.87 |
| annualised Sharpe ratio | **0.267** |

**An earlier envelope in this project put the t-statistic near 1.8 and the Sharpe near
0.51.** That envelope modelled the bucket standard error at about 1.1 % per week and
assumed that differencing the buckets would shrink it. Measuring it instead gives more
than double that figure, and every number downstream inherited the error. The measured
version supersedes it, and the old figures should be treated as withdrawn.

At this mean and this variability, reaching t = 2 would need about **2,900 weeks, or 56
years**, of data. The sample is 10 years. That is the honest size of the gap, and it
assumes the observed mean is the truth, so it is a scale for the gap rather than a power
calculation. If the true mean is smaller, it is worse.

---

## The autocorrelation correction, which turned out not to matter

Weekly spreads were expected to be positively autocorrelated, which would make the naive
standard error too small and the study look more significant than it is. That was measured
rather than assumed, and it is not there. Lags 1 to 3 come in at +0.003, +0.002 and +0.001.

A Newey-West standard error, which adds the covariance terms the naive formula omits,
moves the t-statistic from +0.84 to +0.87. Because the residual dependence is mildly
negative overall, the naive standard error is if anything the conservative one here. The
conclusion is stable across every lag from 0 to 20, the most generous of which reaches
t = +1.01, so it does not rest on a lag choice.

**How the autocorrelations are estimated, since the convention is a choice.** Each lag is
gamma_k over gamma_0, where gamma_k sums the products of deviations k weeks apart and
divides by T rather than by the T minus k pairs actually summed. That is the textbook
convention and it is deliberate, for two reasons. Dividing by T shrinks the far-out lags
toward zero where they are estimated from few pairs, and it guarantees the whole set of
lags is mutually consistent, so the Newey-West sum built from them cannot return a
negative variance. Dividing by gamma_0 rather than by two separate standard deviations
assumes stationarity, meaning the series has one variance rather than a different one
early and late. That assumption is made and not tested, and the sample spans March 2020.
Note also that this is not `pandas.Series.autocorr()`, which demeans the two shortened
series separately and therefore does not compose into the Newey-West sum.

One oddity worth recording without over-reading. Lag 4 sits at -0.135, a roughly monthly
reversal in the spread itself. One number, not investigated.

---

## The parametric cross-check, which leans the other way

The bucket test discards the magnitudes and keeps only the ordering. The obvious second
route keeps the magnitudes. Each week, fit a straight line through the roughly 99 names
with the signal on one axis and the forward return on the other, and read its slope. That
is a Fama-MacBeth procedure, one cross-sectional regression per week, after which the 521
slopes are treated as the data and their mean and standard error taken. The standard error
comes from the week-to-week scatter of the slopes rather than from inside a week, so it
never assumes the names within a week are independent.

| | mean | weekly SD | SE | t |
|---|---|---|---|---|
| bucket spread, % per week | +0.0910 | 2.4599 | 0.1078 | **+0.84** |
| regression slope | +0.00090 | 0.24658 | 0.01080 | **+0.083** |

**The two lean in opposite economic directions, which is not the same as differing in
printed sign.** Both numbers are positive on the page. The signal is the past week's
return, so a positive slope says last week's winners did better, which is momentum. A
positive bucket spread is losers minus winners, which is reversal. Same sign, opposite
claim about the world.

Neither is distinguishable from zero, and the slope is not distinguishable from anything
at all. It is one twelfth of a standard error from zero and 51.4 % of weekly slopes are
negative. In plain terms the slope says a stock that fell 10 % further than another last
week went on to make about 0.01 % less the next week, which is not a small effect so much
as the absence of one.

**The disagreement is structural rather than statistical, and that is the point.** A
regression is obliged to answer with a single steepness. Given a sort where both ends do
well, it averages whatever is happening on the left against whatever is happening on the
right and reports approximately nothing. The bucket test can see an uneven sort precisely
because it assumes no shape. So the regression does not correct the bucket test and is not
the more rigorous of the two. It is blind to the one feature of the data that is
interesting.

Neither number is reported as the finding. What is reported is that a linear specification
cannot represent this sort, which is a stronger statement than either estimate alone.

---

## Robustness

**Bucket count.** The conclusion does not depend on cutting the cross-section into five.

| buckets | names per bucket | spread, % per week | t | t, Newey-West |
|---|---|---|---|---|
| 3 | 33 | +0.073 | +0.87 | +0.90 |
| 5 | 20 | +0.091 | +0.84 | +0.87 |
| 10 | 10 | +0.149 | +1.05 | +1.06 |

The spread keeps its sign and grows as the buckets narrow, which is what a concentrated
signal would do, but no cut is close to significant. Ten buckets of ten names is also
where an individual bucket stops being an average and starts being a handful of stocks.

**Lookback and holding period.** Every pairing of 1, 5 and 21 trading days, re-ranking
only once each hold has finished so that no two forward returns share a day. The 21 day
hold leaves 118 observations. All nine cells are reported and none is singled out. Values
are t-statistics, rows are the lookback and columns are the hold.

| lookback, hold | 1 | 5 | 21 |
|---|---|---|---|
| **1** | +1.55 | +0.11 | -1.10 |
| **5** | +0.88 | +1.07 | -0.24 |
| **21** | +0.31 | -0.42 | -0.94 |

No cell is significant. The month by month cell, the one the literature points to and the
one predicted in advance to be strongest, leans toward momentum rather than reversal. The
largest t is one day by one day at +0.04 % per day gross, but that cell trades the whole
book every day and 5 basis points each way costs more than twice the edge, so even the
best cell is nothing after costs. The five by five cell at t = +1.07 sits close to the
calendar-week headline, so the Friday grid is not driving the result.

**Sub-period stability.** The weekly spread in five consecutive two-year blocks, with the
block length fixed before looking.

| block | spread, % per week | t | t, Newey-West |
|---|---|---|---|
| 2016-09 to 2018-08 | +0.176 | +1.23 | +1.52 |
| 2018-09 to 2020-08 | +0.324 | +1.04 | +0.91 |
| 2020-09 to 2022-08 | -0.004 | -0.02 | -0.02 |
| 2022-09 to 2024-08 | -0.013 | -0.06 | -0.06 |
| 2024-08 to 2026-08 | -0.029 | -0.11 | -0.14 |

No block is significant, so the pre-committed one-year shift of the cut points was not
triggered. The pattern is the informative part. Whatever reversal is in this sample sits
in 2016 to 2020 and is flat since, and the ten-year average dilutes it. Why is not
testable here. The last three blocks drifting slightly negative is not a trend, because
each is zero within noise.

---

## Transaction costs, and the result does not survive them

The result is the return of a portfolio long bucket 1 and short bucket 5, so costs are
paid on both legs. Cost is charged on money traded rather than per order, and fully
replacing one leg trades twice its value, so the weekly cost on the spread is
(turnover of bucket 1 plus turnover of bucket 5) times 2 times the cost per trade.

**Turnover is measured. The cost level is modelled.** Measured weekly turnover is 0.787
for bucket 1 and 0.783 for bucket 5, against 0.800 for random picks, so bucket membership
is no more persistent than chance. The rule was fixed in advance, which was that a net
spread at or below zero at 5 basis points means stop.

| cost per trade, modelled | weeks | net spread, % per week | t |
|---|---|---|---|
| 0 | 520 | +0.092 | +0.85 |
| 5 basis points | 520 | -0.065 | -0.60 |
| 10 basis points | 520 | -0.222 | -2.06 |

**Break-even is about 2.9 basis points per trade**, by arithmetic. The rule fired.

**The t of -2.06 at 10 basis points is not a finding about markets.** The error bar barely
moves when a near-constant is subtracted, so a large enough assumed cost pushes any
near-zero mean past two standard errors. It says only that this strategy would lose money
at that cost. If anything the figures are understated, because the weight resets needed to
keep the legs equally weighted as prices drift are not charged.

---

## Method

**Universe.** 100 US large caps, chosen from today's index membership. Daily adjusted
closes from Yahoo Finance, cached to local CSV.

**Week.** A calendar week anchored on the Friday close. 96 of the 521 weeks, or 18.4 %,
are holiday-shortened to four trading days.

**Signal.** For each stock, its return over the past week. All names are then ranked
against each other that week, so the question is never whether a stock fell 3 % but
whether it fell further than the other 99.

**Forward return.** The same stock's return over the following week, sharing no days with
the signal window. Verified by hand rather than asserted, see below.

**Buckets.** The ranked cross-section is cut into 5 equal-sized groups of about 20. Bucket
1 holds the biggest losers and bucket 5 the biggest winners. Cutting on ranks rather than
raw returns keeps every bucket the same size every week. Cutting on raw values would give
equal-width return bands, so a calm week might put 2 names in bucket 1 and 60 in bucket 3.

**The reported spread is averaged, not differenced at the end.** The spread is computed
each week and those weekly numbers are averaged, rather than averaging each bucket over
ten years and subtracting once. The two agree exactly when both buckets exist in every
week, and when they do not, the weekly version never compares bucket 1 over one set of
weeks against bucket 5 over a different set.

**Missing data is dropped, never imputed.** A stock with no signal in a given week is
excluded from that week's ranking. Imputing would place a company that did not yet exist
into the middle bucket, and an invented number is worse than no number, because a missing
value announces itself and a fabricated one does not.

**A week must carry at least 40 names on both sides.** The same threshold applies to the
signal and to the forward return. This is what ends the sample at 21 August 2026 rather
than at whatever date the price cache happens to reach, so re-downloading the data cannot
move a published number without moving the stated end date with it. Of the 526 candidate
anchors, the first is dropped for having no prior week, and the last four are dropped
because only one ticker in the cache has prices past 25 August 2026.

### Alignment verified by hand

The failure mode in a study like this is not conceptual, it is a shift of one in the wrong
direction. One character, no error raised, and the forward return becomes the signal
column itself, so the study reports a perfect relationship.

Checked directly on a single name. AAPL, anchor Friday 27 March 2026, gives 247.55, then
248.36, then 255.46, so a signal of +0.33 % and a forward return of +2.86 %, both confirmed
against the three dates read in order. Three structural checks also pass. The signal is
all-missing on the first anchor, the forward return is all-missing on the last, and the
signal at week t plus one equals the forward return at week t exactly, which is the
no-shared-days rule showing up as an equation rather than as a promise.

---

## Where this study is wrong

The honest answer to the research question may be no, and it is. These are the ways the
headline is flattered, in descending order of how much they matter.

**1. Survivorship, and it is the big one.** The universe is today's membership, so the
panel contains zero delistings over ten years. A real 100-stock universe tracked over a
decade does not have zero delistings. Every name in this sample survived by construction.
That biases the study toward optimism and it does so most sharply for a signal that buys
losers, since the historical names that fell hard and never recovered are precisely the
ones absent from the sample. The study tests buying the dip on a sample where every dip
had someone left to recover.

**2. The universe is a genuine look-ahead.** Bucket membership at week t uses only prices
up to t, so the test itself does not look forward. Picking the tickers, however, required
knowing which firms still exist in 2026. That leak is baked in and cannot be removed
without point-in-time index membership data.

**3. Equal weighting flatters the result.** Equal weight was chosen because any weighting
scheme is a second hypothesis bolted onto the first, and if the study fails you cannot
tell which half failed. The cost is real. Equal weight tilts toward smaller and less
liquid names, which is exactly where reversal is strongest and where trading costs are
highest, so the costs charged above are the optimistic version.

**4. Short weeks are not identically scaled.** A four-day return carries about 89 % of a
five-day one's volatility. The ranking is unaffected, since all names share the same short
window that week, so a rank-based study absorbs it. Where it bites is the error bar, which
assumes the weekly observations are the same kind of object, and under a calendar grid
they are not quite. This is roughly an 11 % scale difference on 18.4 % of the observations
and it is not corrected for.

**5. Execution assumes the closing auction.** Positions are assumed to be entered at the
same Friday close used to compute the signal. That is achievable through the closing
auction, where a large volume genuinely does trade at the official closing print, but
market-on-close orders must be submitted a few minutes before the bell, so the decision is
really made on near-close prices. Reversal is a short-horizon effect and therefore the
kind of signal that decays fastest with delay. The lagged version, entering at Monday's
open, is not tested here.

### Parameter inventory

Every choice in the study, and whether it was tested or merely declared.

| parameter | chosen | alternative | status |
|---|---|---|---|
| Bucket count | 5 | 3, 10 | tested, conclusion unchanged |
| Lookback and hold | 5 and 5 trading days | 1, 5, 21 in every pairing | tested, no cell significant |
| Sample period | 10 years, one block | five two-year blocks | tested, effect confined to 2016 to 2020 |
| Grid | calendar weeks on Friday | 5 trading-day blocks | tested via the grid, close agreement |
| Standard error | naive s over root T | Newey-West, lags 0 to 20 | tested, conclusion stable |
| Specification | buckets | cross-sectional regression | tested, the two lean opposite ways |
| Cost level | 0, 5, 10 basis points | any other level | modelled, break-even about 2.9 |
| Weighting | equal weight | market cap | declared only, no market cap in the data |
| Universe | 100 current large caps | point-in-time membership | declared only, needs data not held |
| Execution | Friday close | Monday open | declared only, not run |

---

## What is not done, and why

- **The Monday-open execution lag.** The Open column exists in the cached data, so this is
  runnable and simply has not been run.
- **Market cap weighting.** Not possible with the data held, which is prices only.
- **Out-of-sample split, and this one is deliberate.** An out-of-sample test validates a
  setting chosen in-sample. No setting was significant in-sample, so there was nothing to
  carry out. Running one anyway would be theatre.
- **Two questions this study cannot answer.** First, whether reversal existed before 2016,
  which needs point-in-time index membership, because reaching back with today's large
  caps makes the survivorship problem worse the further back it goes. Second, momentum.
  Flipping the weekly spread is buying winners, which is documented at a roughly 12-month
  lookback rather than a weekly one. The month by month grid cell leaned that way without
  being significant. That deserves its own pre-registered test at its own horizon, and it
  is not a reason to trade the drift in these blocks.

---

## Running it

```
python download.py      # fetch and cache the universe, one CSV per ticker
python signal_build.py  # build the signal and forward-return panels
python buckets.py       # rank, bucket, and print the headline table
python errorbars.py     # autocorrelation, standard errors, t-stat, Sharpe
python parametric.py    # Fama-MacBeth cross-check, one regression per week
python robustness.py    # 3, 5 and 10 buckets
python grid.py          # lookback by holding-period grid
python subperiods.py    # two-year blocks
python costs.py         # turnover and the net spread after costs
```

Plain scripts and no notebooks. Each runs top to bottom with no hidden state. Raw data is
cached under `data/` and is not committed.

---

**Sam Broncek.** MMath, University of Warwick, 2025.
