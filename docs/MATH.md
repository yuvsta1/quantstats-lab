# Mathematical definitions and limitations

> Created by Yuvi with the assistance of AI (OpenAI ChatGPT) for software development, testing, and documentation.

This documentation is normative for QuantStats Lab `v0.1.0`. All returns used by the risk functions are **simple period returns in decimal form**: `r_t=(P_t/P_(t−1))−1` for a pure price series. Dividends, splits, and cash flows must be handled *before* supplying returns. Raw prices are not accepted as returns.

## 1. Distribution functions

Probability functions are evaluated using SciPy frozen distributions. Continuous distributions return a **density** `f(x)`, which is *not* `P(X=x)`; discrete distributions return a probability mass. `F(x)=P(X<=x)`, `SF(x)=P(X>x)` (`sf` is used directly to improve upper-tail precision). Quantiles are evaluated with `ppf` at 0.05, 0.5 and 0.95.

| Distribution | Parameterisation |
| --- | --- |
| Normal | mean `mean`, standard deviation `std > 0` |
| Student-t | degrees of freedom `df > 0`, location `loc`, scale `scale > 0` |
| Binomial | integer trials `n >= 0`, success probability `0 <= p <= 1` |
| Poisson | arrival rate `rate > 0` |
| Exponential | scale `scale > 0`; mean equals scale |
| Lognormal | SciPy `shape > 0` (sigma of underlying log variable) and positive `scale` |

Student-t mean is undefined for `df <= 1` and variance is undefined/infinite for `df <= 2`. Nonfinite moments are displayed as such; they should **not** be interpreted as valid finite estimates.

## 2. Geometric Brownian motion

The model is `dS_t = μ S_t dt + σ S_t dW_t`, with *constant* annual drift `μ` and volatility `σ`. We use the exact one-step solution:

`S_(t+Δt) = S_t · exp[(μ − σ²/2)Δt + σ sqrt(Δt) Z_t]`, where independent `Z_t ~ Normal(0,1)` and `Δt=1/periods_per_year`.

The expected terminal value under this model is `S_0 exp(μ T)` and the median is `S_0 exp((μ−σ²/2)T)`, `T=steps/periods_per_year`. Tests check deterministic σ=0 against the analytic formula and Monte Carlo sample means against analytic expectations.

**Caveats:** constant volatility, normally distributed log increments, fixed drift and independence are strong simplifications. The simulation is **not** an estimated forecast and is not calibrated to live markets.

## 3. Independent historical-return bootstrap

Each simulated period independently samples *one observed simple return* with replacement from the input. Wealth evolves as `S_t=S_(t−1)(1+r_t)`. This intentionally discards autocorrelation, clustered volatility, chronology, regime changes and correlations across assets. Returns must be >= −1 and fully finite.

Only use this method if the independent identically distributed approximation is defensible; consider block bootstrapping for serially dependent data (not part of this release).

## 4. Mean inference

### Student-t confidence interval

For sample mean `x_bar`, sample standard deviation `s` with `ddof=1` and sample size `n`, the two-sided `(1−α)` interval is:

`x_bar ± t_(1−α/2,n−1) · s/sqrt(n)`.

This assumes independent observations and a distribution where the t approximation is appropriate. A constant sample returns the point `[mean,mean]` rather than an undefined interval; that does not prove absence of population uncertainty.

### Bootstrap percentile interval

We sample `n` observations *with replacement* `B` times, calculate means, then return the empirical `α/2` and `1−α/2` quantiles. The random generator is local to each call, and the seed controls reproducibility. No bias correction or acceleration is applied. It may have poor coverage for small, skewed or dependent samples.

### Hypothesis tests

A one-sample two-sided t-test of `H0: μ=μ0` and a two-sample Welch t-test of equal population means are provided. The null reference distributions are evaluated by SciPy. Constant-input special cases produce 0/1 p-values, not spurious floating-point warnings; inference on deterministic samples should be interpreted carefully.

For `m` tests, Benjamini–Hochberg adjusted p-values are computed as:

`q_(i) = min(1, min_{j>=i}(m·p_(j)/j))` for sorted p-values, then restored to original order.

BH controls false-discovery rate under independence and certain positive-dependence assumptions; arbitrary dependence may require a different method.

## 5. Stochastic processes

**Ornstein–Uhlenbeck (OU):** `dX_t=θ(m−X_t)dt+σ dW_t`, `θ>0`; exact conditional update uses `a=exp(−θ dt)` and innovation standard deviation `σ sqrt((1−exp(−2 θ dt))/(2 θ))`. We implement `−expm1(−2 θ dt)` to improve small-step numerical precision.

**AR(1):** `X_t=m+φ(X_(t−1)−m)+ε_t`, independent normal innovations with user-selected standard deviation. Stationarity is required (`|φ|<1`). Both models describe general **states**; a negative state is allowed. Neither should automatically be treated as a price model.

## 6. Risk metrics

### Historical value at risk (VaR)

For losses `L_t=−r_t`, `VaR_c = max(0, empirical_quantile(L,c))`, using NumPy's **linear** sample-quantile interpolation. VaR is reported as a **positive loss fraction**, not a negative return.

### Historical expected shortfall (ES)

Let `k=(1−c)n`, `m=floor(k)` and `f=k−m`. Sort losses ascending. Average the `m` largest losses plus `f` times the next largest, divided by `k`. Clamp negative ES to zero. This **fractional tail-weight** convention avoids a misleading empty tail when `n` is small or `c` is very high. Other implementations may use different quantile/tail conventions, producing different estimates on short samples.

ES from this convention will not fall below VaR on valid data. A zero sample-loss output does not mean zero future risk.

### Total return, annualisation, volatility and Sharpe

- Total simple compounded return: `Π(1+r_t)−1`.
- Annualised compounded return: `(Π(1+r_t))^(periods_per_year/n)−1`, when observations are equally spaced.
- Annualised sample volatility: `std(r,ddof=1)·sqrt(periods_per_year)`.
- Periodic risk-free return: `(1+annual_rf)^(1/periods_per_year)−1`.
- Annualised arithmetic Sharpe: `mean(r−rf_period) / std(r−rf_period,ddof=1) · sqrt(periods_per_year)`. Undefined when the sample volatility is zero; the API returns `None`.

### Maximum drawdown

Wealth is initialised at 1; at each time `V_t=Π_(i=1)^t (1+r_i)` and high-water mark `H_t=max_(i<=t) V_i`, **including initial wealth**. Drawdown is `V_t/H_t−1` and the reported maximum drawdown is its negative minimum (a nonnegative fraction).

## 7. Validation and numerical conventions

- Input vectors must be one-dimensional, finite and normally contain at least two values; no NaN dropping/imputation occurs.
- For risk and wealth simulations, simple returns below −100% are rejected.
- Simulation size is limited to 3 million step/path combinations (per call) to constrain memory use.
- Use the **same seed** for reproducible output, not as a claim of predictability.
- Some extremely large but finite parameters can overflow floating-point operations and raise an error; use realistic scales.
- Data loaded from CSV are not independently checked for price vs return semantics. Users must supply correct units and frequency.

## 8. Sources and references

- SciPy continuous/discrete distribution documentation: https://docs.scipy.org/doc/scipy/reference/stats.html
- SciPy t-test and mean-interval reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html
- NumPy sample quantile definitions: https://numpy.org/doc/stable/reference/generated/numpy.quantile.html
- Benjamini, Y. and Hochberg, Y. (1995), *Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing*, JRSS B 57(1), 289–300.
- Hull, J., *Options, Futures, and Other Derivatives*, for GBM notation and lognormal dynamics.
- Glasserman, P., *Monte Carlo Methods in Financial Engineering*, Springer, for simulation methodology and assumptions.

No source code from these references is copied here. The implementation relies on NumPy and SciPy for the specified numerical primitives.