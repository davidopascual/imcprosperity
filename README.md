# Prosperity Trading Algorithm (trader.py) - README

## Overview
This repository contains the Python implementation of a trading algorithm (`trader.py`) designed for the Prosperity trading simulation, specifically for the tutorial round. The algorithm trades two products on the island exchange: **Rainforest Resin** and **Kelp**, aiming to maximize profit in **SeaShells**, the archipelago’s currency. Using a **quantitative mean-reversion strategy**, the algorithm identifies profitable trading opportunities based on market data while respecting position limits and simulation constraints.

The algorithm was tested in the tutorial round, achieving a **profit of 3,642 SeaShells over 1,000 iterations**, as shown in the algorithmic trading results dashboard. This README provides a detailed breakdown of the trading strategy, profit analysis, decision-making rationale, and technical implementation.

---

## Trading Strategy
### Quantitative Strategy: Moving Average-Based Mean Reversion
The algorithm follows a **mean-reversion approach**, assuming that asset prices tend to revert to a historical average over time. By identifying deviations from this average, the strategy captures profit opportunities by buying undervalued assets and selling overvalued ones.

### Key Components:
#### Moving Averages:
- **Rainforest Resin:** Uses a **100-iteration moving average** to track long-term stability and smooth out price fluctuations.
- **Kelp:** Uses a **10-iteration moving average** to account for its volatility, enabling quick adaptation to short-term price movements.
- The **mid-price** (calculated as `(best_bid + best_ask) / 2`) serves as the reference price, guiding buy and sell decisions.

#### Trading Logic:
- **Buy Orders:** If the **best ask price** is below the moving average, the asset is considered undervalued, triggering a buy order.
- **Sell Orders:** If the **best bid price** is above the moving average, the asset is considered overvalued, triggering a sell order.
- **Risk Management:** The algorithm respects **position limits** (50 units per asset) to prevent overexposure and ensure compliance with simulation constraints.

#### Market-Making Principles:
- By reacting to the **order book** (current market buy/sell orders), the algorithm provides liquidity and capitalizes on pricing inefficiencies.

#### Time Series Analysis:
- Maintains a **historical price series** to compute moving averages dynamically, ensuring adaptability to changing market conditions.

---

## Profit Analysis
- **Achieved Profit:** The algorithm generated a **net profit of 3,642 SeaShells over 1,000 iterations**, broken down as follows:
  - **Kelp:** 1,954 SeaShells
  - **Rainforest Resin:** 1,688 SeaShells

### Performance Insights:
- The strategy initially faced **minor drawdowns**, but consistent execution of the mean-reversion approach led to an overall **upward profit trend**.
- **Profit Per Iteration:** Approximately **3.64 SeaShells per iteration**, showcasing the effectiveness of the trading logic.
- The results suggest that **trading Kelp was more profitable**, likely due to its higher volatility allowing more frequent profitable trades.

---

## Traded Assets
### 1. Rainforest Resin
- **Characteristics:** Historically stable, making it ideal for a **longer-term mean-reversion strategy**.
- **Position Limit:** 50 units.

#### Strategy Rationale:
- Uses a **100-iteration moving average** to capture long-term price stability and trade on deviations.
- **Pros:** Stability ensures fewer false signals.
- **Cons:** May react slowly to sudden price movements.

### 2. Kelp
- **Characteristics:** More volatile than Rainforest Resin, requiring a **short-term strategy**.
- **Position Limit:** 50 units.

#### Strategy Rationale:
- Uses a **10-iteration moving average** to capitalize on rapid price fluctuations.
- **Pros:** High responsiveness enables frequent profit-taking.
- **Cons:** Higher risk of reacting to noise in price movements.

---

## Technical Implementation
### Code Structure
- **File:** `trader.py`
- **Class:** `Trader`, implementing the `run` method as per simulation requirements.

### Libraries Used:
- `datamodel`: Provides `OrderDepth`, `TradingState`, and `Order` classes.
- `json`: Used for serializing/deserializing `traderData` to maintain price history.
- **No external libraries** beyond those supported in the simulation environment.

### Key Methods:
#### `run(self, state: TradingState)`
- Processes `TradingState` to extract **order book depth, position holdings, and historical price data**.
- Computes **moving averages**, evaluates trading signals, and places orders accordingly.
- Returns `(result, conversions, traderData)`, where:
  - `result`: Dictionary of product orders.
  - `conversions`: Always `0` (no conversions allowed in this round).
  - `traderData`: Serialized price history for state persistence.

### Performance Considerations
- **Execution Time:** Optimized for under **900ms per iteration**, ensuring smooth performance.
- **Scalability:** The architecture allows for **easy expansion to additional assets or trading enhancements**.

---

## Profit Optimization and Future Improvements
### Current Performance
- **Total Profit:** 3,642 SeaShells over 1,000 iterations, with **Kelp contributing the most**.

### Areas for Enhancement:
- **Adaptive Window Sizes:** Dynamically adjusting moving averages based on market volatility.
- **Volume-Based Signals:** Incorporating order book depth to refine trade execution.
- **Hybrid Strategies:** Combining mean-reversion with momentum-based signals for improved trade timing.
- **Dynamic Risk Management:** Adjusting position limits based on historical volatility and profitability trends.

The results demonstrate that the **moving average mean-reversion approach is effective**, but further refinements could increase profit potential. Future iterations may incorporate **additional technical indicators** or **machine learning techniques** to enhance decision-making.

---

