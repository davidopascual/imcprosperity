# Prosperity Trading Algorithm (trader.py) - README

## Overview
This repository contains the Python implementation of a trading algorithm (`trader.py`) designed for the Prosperity trading simulation, specifically for the tutorial round. The algorithm trades two products on the island exchange: **Rainforest Resin** and **Kelp**, with the goal of maximizing profit in **SeaShells**, the archipelago’s currency. It leverages quantitative strategies to make informed trading decisions based on market data, respecting position limits and simulation constraints.

The algorithm was tested in the tutorial round, achieving a **profit of 1,750 SeaShells over 1,000 iterations**, as shown in the algorithmic trading results dashboard. This README provides a detailed description of the strategy, assets, profit analysis, decision-making rationale, and technical implementation.

---

## Trading Strategy
### Quantitative Strategy: Moving Average-Based Mean Reversion
The algorithm employs a **moving average-based mean reversion strategy**, tailored to the price dynamics of the two tradable assets. It assumes that prices tend to revert to a historical mean over time and uses this assumption to identify profitable trading opportunities.

### Key Components:
#### Moving Averages:
- **Rainforest Resin:** Uses a **100-iteration moving average** window due to its stable price history, smoothing out noise and capturing its consistent value.
- **Kelp:** Uses a **10-iteration moving average** window to adapt to its volatile, fluctuating price, enabling quick responses to short-term price movements.
- The moving average of **mid-prices** (calculated as `(best_bid + best_ask) / 2`) serves as the "acceptable price," representing the fair value for trading decisions.

#### Trading Logic:
- **Buy Orders:** If the **best ask price** (lowest sell order) is below the acceptable price, the algorithm places a **buy order**, interpreting the price as undervalued.
- **Sell Orders:** If the **best bid price** (highest buy order) is above the acceptable price, the algorithm places a **sell order**, viewing the price as overvalued.
- Orders **respect position limits** (50 for both products) to avoid rejection and manage risk.

#### Market-Making Elements:
- The algorithm reacts to the **order book** (buy and sell orders from bots) to capture immediate liquidity, incorporating basic market-making principles while prioritizing mean reversion.

#### Time Series Analysis:
- Maintains a **historical price series** (mid-prices) for each product, stored in `traderData` and updated each iteration, to compute moving averages dynamically.

---

## Profit Analysis
- **Achieved Profit:** The algorithm generated a **net profit of 1,750 SeaShells over 1,000 iterations** in the tutorial round, as displayed in the dashboard graph.

### Graph Insights:
- The profit trend started at a **loss of -396.04 SeaShells**, indicating initial adjustments or mispricings, but recovered to end at **1,750 SeaShells** with some volatility.
- The **upward trajectory** suggests the mean-reversion strategy effectively captured profitable opportunities over time.
- **Profit Per Iteration:** Approximately **0.00875 SeaShells per iteration**, indicating **small but consistent gains**. This could be improved by increasing trading frequency or refining parameters.

---

## Traded Assets
### 1. Rainforest Resin
- **Characteristics:** Known for a **stable value** throughout the archipelago’s history, making it ideal for a **long-term mean-reversion strategy**.
- **Position Limit:** 50 (cannot hold more than 50 units long or short).

#### Strategy Rationale:
- A **100-iteration moving average** is used to smooth out price fluctuations and identify consistent undervaluation or overvaluation.
- Trades are executed when the best ask is below or the best bid is above the moving average, betting on **price reversion to stability**.
- The longer window **minimizes noise**, aligning with the product’s stable nature, but may **miss rapid opportunities**.

### 2. Kelp
- **Characteristics:** Exhibits **upward and downward price fluctuations** over time, requiring a **dynamic, short-term strategy**.
- **Position Limit:** 50 (cannot hold more than 50 units long or short).

#### Strategy Rationale:
- A **10-iteration moving average** captures rapid price changes, enabling the algorithm to react quickly to volatility.
- Trades are triggered when the best ask is below or the best bid is above the moving average, exploiting **short-term mispricings**.
- The shorter window **increases responsiveness** but risks **overreacting to noise or false signals**.

---

## Technical Implementation
### Code Structure
- **File:** `trader.py`
- **Class:** `Trader` with a single `run` method, adhering to the provided `Trader` class specification.

### Libraries Used:
- `datamodel`: Provided for `OrderDepth`, `TradingState`, `Order`, etc.
- `json`: For serializing/deserializing `traderData` to maintain price history.
- **No external libraries** beyond those supported (e.g., pandas, NumPy) to comply with simulation rules.

### Key Methods:
#### `run(self, state: TradingState)`
- Processes `TradingState` data (e.g., `order_depths`, `position`) to generate orders.
- Calculates **mid-prices**, updates **price history**, computes **moving averages**, and places orders based on **mean-reversion logic**.
- Returns a tuple `(result, conversions, traderData)`, where:
  - `result`: Dictionary mapping products to lists of `Order` objects.
  - `conversions`: Set to `0` (no conversions in tutorial round).
  - `traderData`: JSON-serialized price history for state persistence.

### Performance Considerations
- **Execution Time:** Designed to run within **900ms per iteration**, using lightweight operations (e.g., simple arithmetic, basic dictionary operations).
- **Scalability:** Handles **multiple products efficiently**, with **dynamic window sizes** for each asset.

---

## Profit Optimization and Future Improvements
### Current Performance
- **Profit:** 1,750 SeaShells over 1,000 iterations, indicating a successful but potentially modest outcome.

### Areas for Improvement:
- Increase **trading frequency** by adjusting **moving average windows**.
- Incorporate **order book depth** or **volume analysis** to enhance decision-making.
- Add **momentum or trend-following strategies** for Kelp to complement mean reversion.
- Optimize `acceptable_price` thresholds and window sizes.




---


