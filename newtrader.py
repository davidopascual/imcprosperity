import json
import numpy as np
from statistics import mean
from typing import Any, List, Dict
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState

# Logger class for logging output
class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(
            self.to_json(
                [
                    self.compress_state(state, ""),
                    self.compress_orders(orders),
                    conversions,
                    "",
                    "",
                ]
            )
        )
        max_item_length = (self.max_log_length - base_length) // 3
        print(
            self.to_json(
                [
                    self.compress_state(state, self.truncate(state.traderData, max_item_length)),
                    self.compress_orders(orders),
                    conversions,
                    self.truncate(trader_data, max_item_length),
                    self.truncate(self.logs, max_item_length),
                ]
            )
        )
        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])
        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]
        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append(
                    [
                        trade.symbol,
                        trade.price,
                        trade.quantity,
                        trade.buyer,
                        trade.seller,
                        trade.timestamp,
                    ]
                )
        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sugarPrice,     # actually 'sunlight' from the constructor -> used as sugar price
                observation.sunlightIndex,  # actually 'humidity' from the constructor -> used as sunlight index
            ]
        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])
        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value
        return value[: max_length - 3] + "..."

logger = Logger()

class Trader:
    def __init__(self):
        # Product-specific parameters
        self.params = {
            "RAINFOREST_RESIN": {
                "ma_window": 100,     # Moving average window
                "position_limit": 50,  # Max position
                "spread_factor": 0.5,  # Aggressiveness of spread (lower = tighter)
                "volatility_adjust": True  # Whether to adjust based on volatility
            },
            "KELP": {
                "ma_window": 10,
                "position_limit": 50,
                "spread_factor": 0.3,  # More aggressive for KELP
                "volatility_adjust": True
            }
        }
        
    def calculate_volatility(self, prices, window=20):
        """Calculate rolling volatility of prices"""
        if len(prices) < window:
            return 0
        return np.std(prices[-window:])
        
    def run(self, state: TradingState):
        """
        Executes trading logic for each iteration, generating orders based on market conditions.
        """
        # Deserialize trader data to get price history and volatility
        if state.traderData:
            data = json.loads(state.traderData)
            price_history = data["price_history"]
            volatility_history = data.get("volatility_history", {})
        else:
            price_history = {product: [] for product in state.order_depths}
            volatility_history = {product: [] for product in state.order_depths}
        
        # Initialize result dictionary
        result = {}
        
        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders = []
            
            # Skip if there are no orders for this product
            if not product in self.params:
                result[product] = []
                continue
                
            # Set product parameters
            params = self.params.get(product, {
                "ma_window": 20,
                "position_limit": 50,
                "spread_factor": 0.5,
                "volatility_adjust": False
            })
            
            # Log current state
            logger.print(f"Processing {product} - Position: {state.position.get(product, 0)}")
            
            # Calculate mid price and update price history
            if order_depth.buy_orders and order_depth.sell_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) / 2
                
                logger.print(f"Market - Bid: {best_bid}, Ask: {best_ask}, Mid: {mid_price:.2f}")
                
                # Update price history
                price_history.setdefault(product, []).append(mid_price)
                if len(price_history[product]) > params["ma_window"]:
                    price_history[product] = price_history[product][-params["ma_window"]:]
                
                # Calculate moving average
                ma_price = sum(price_history[product]) / len(price_history[product])
                
                # Calculate volatility and update history
                volatility = self.calculate_volatility(price_history[product])
                volatility_history.setdefault(product, []).append(volatility)
                if len(volatility_history[product]) > params["ma_window"]:
                    volatility_history[product] = volatility_history[product][-params["ma_window"]:]
                
                logger.print(f"Analysis - MA: {ma_price:.2f}, Volatility: {volatility:.2f}")
                
                # Get current position and limit
                position = state.position.get(product, 0)
                position_limit = params["position_limit"]
                
                # Calculate dynamic spread based on volatility and position
                base_spread = (best_ask - best_bid) * params["spread_factor"]
                position_factor = abs(position) / position_limit  # How full is our position
                
                # Adjust spread based on volatility if enabled
                if params["volatility_adjust"] and volatility_history[product]:
                    avg_volatility = sum(volatility_history[product]) / len(volatility_history[product])
                    volatility_factor = volatility / avg_volatility if avg_volatility > 0 else 1
                    adjusted_spread = base_spread * (1 + volatility_factor * 0.5)
                else:
                    adjusted_spread = base_spread
                
                # Adjust prices based on our position (mean reversion)
                # If we have a large long position, we're more eager to sell (higher sell price)
                # If we have a large short position, we're more eager to buy (lower buy price)
                position_adjustment = adjusted_spread * position_factor * np.sign(position)
                
                # Calculate our bid and ask prices
                our_bid = mid_price - adjusted_spread/2 - position_adjustment
                our_ask = mid_price + adjusted_spread/2 - position_adjustment
                
                # Make sure our prices are competitive
                our_bid = min(our_bid, best_bid)
                our_ask = max(our_ask, best_ask)
                
                logger.print(f"Pricing - Our Bid: {our_bid:.2f}, Our Ask: {our_ask:.2f}, Spread: {adjusted_spread:.2f}")
                
                # Smart order quantity based on position limits and order book depth
                buy_quantity_available = abs(sum(order_depth.sell_orders.values()))
                sell_quantity_available = sum(order_depth.buy_orders.values())
                
                # Adjust quantities based on current position
                max_buy = position_limit - position
                max_sell = position_limit + position
                
                # Lower quantities as we approach position limits
                position_scalar = 1 - (abs(position) / position_limit)
                buy_quantity = min(buy_quantity_available, max(1, int(max_buy * position_scalar)))
                sell_quantity = min(sell_quantity_available, max(1, int(max_sell * position_scalar)))
                
                # Place orders
                if buy_quantity > 0 and our_bid > 0 and our_bid < best_ask:
                    orders.append(Order(product, int(our_bid), buy_quantity))
                    logger.print(f"Placing BUY order: {product} x {buy_quantity} @ {int(our_bid)}")
                
                if sell_quantity > 0 and our_ask > best_bid:
                    orders.append(Order(product, int(our_ask), -sell_quantity))
                    logger.print(f"Placing SELL order: {product} x {sell_quantity} @ {int(our_ask)}")
                
                # Market-taking orders for opportunities with significant edge
                # Buy if the best ask is significantly below our calculated fair value
                if best_ask < ma_price * 0.98:  # 2% discount to fair value
                    take_quantity = min(-order_depth.sell_orders[best_ask], max_buy)
                    if take_quantity > 0:
                        orders.append(Order(product, best_ask, take_quantity))
                        logger.print(f"Taking liquidity - BUY: {product} x {take_quantity} @ {best_ask}")
                
                # Sell if the best bid is significantly above our calculated fair value
                if best_bid > ma_price * 1.02:  # 2% premium to fair value
                    take_quantity = min(order_depth.buy_orders[best_bid], max_sell)
                    if take_quantity > 0:
                        orders.append(Order(product, best_bid, -take_quantity))
                        logger.print(f"Taking liquidity - SELL: {product} x {take_quantity} @ {best_bid}")
            
            result[product] = orders
        
        # Update trader data for next iteration
        data = {
            "price_history": price_history,
            "volatility_history": volatility_history
        }
        trader_data = json.dumps(data)
        
        # Return orders, conversions, and trader data
        conversions = 0
        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data