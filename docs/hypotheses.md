# Strategy hypotheses

## Session breakout

When London price closes beyond the completed Asian session range, continuation may persist far enough to cover realistic XAUUSD costs. The baseline enters at the next bar open, uses a stop just inside the broken range, and a configurable fixed R target. This hypothesis must be tested on the development period only and pass the validation gate before hold-out access.

## Trend momentum

When price is aligned above or below the fast and slow EMAs and ADX confirms directional strength, a breakout or pullback continuation may persist. The baseline enters on the next bar, places the stop at a configurable ATR distance, and targets a fixed R multiple.

## Mean reversion

In a range regime, extensions beyond a configurable ATR distance from rolling VWAP may revert toward that mean. The baseline fades the extension, uses a hard ATR stop, and targets VWAP; it is disabled in confirmed trend regimes.

## Liquidity sweep reversal

A sweep beyond a prior structural extreme followed by an engulfing reversal may trap breakout traders. The baseline enters on the next bar, places the stop beyond the sweep wick, and targets a configurable R multiple.
