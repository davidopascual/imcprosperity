from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import json

class Trader:
    def run(self, state: TradingState):
        """
        Executes trading logic for each iteration, generating orders based on market conditions.

        Args:
            state (TradingState): Contains market data including order depths, positions, etc.

        Returns:
            tuple: (result, conversions, traderData)
                - result (dict): Product to list of orders mapping.
                - conversions (int): Number of conversions (set to 0 for now).
                - traderData (str): Serialized state data for next iteration.
        """
        # Define moving average window sizes for each product
        N = {
            "RAINFOREST_RESIN": 100,  # Longer window for stable price
            "KELP": 10                 # Shorter window for fluctuating price
        }
        
        # Deserialize traderData to get previous price history
        if state.traderData:
            price_history = json.loads(state.traderData)
        else:
            price_history = {product: [] for product in state.order_depths}
        
        result = {}
        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders = []

            # Calculate mid-price if both buy and sell orders exist
            if order_depth.buy_orders and order_depth.sell_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) / 2
                price_history[product].append(mid_price)
                if len(price_history[product]) > N.get(product, 10):
                    price_history[product] = price_history[product][-N[product]:]
                acceptable_price = sum(price_history[product]) / len(price_history[product])
            else:
                # If no orders, use last known acceptable price if available
                if price_history[product]:
                    acceptable_price = sum(price_history[product]) / len(price_history[product])
                else:
                    acceptable_price = 0  # Default value, adjust as necessary

            # Get current position and position limit
            P = state.position.get(product, 0)
            L = 50  # Position limit for both products

            # Generate buy orders
            if order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_amount = order_depth.sell_orders[best_ask]  # Negative quantity
                if best_ask < acceptable_price:
                    buy_quantity = min(-best_ask_amount, L - P)
                    if buy_quantity > 0:
                        orders.append(Order(product, best_ask, buy_quantity))

            # Generate sell orders
            if order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_amount = order_depth.buy_orders[best_bid]  # Positive quantity
                if best_bid > acceptable_price:
                    sell_quantity = min(best_bid_amount, P + L)
                    if sell_quantity > 0:
                        orders.append(Order(product, best_bid, -sell_quantity))

            result[product] = orders

        # Serialize updated price history back to traderData
        traderData = json.dumps(price_history)
        conversions = 0  # Set to 0 for now, as conversions are unclear
        return result, conversions, traderData