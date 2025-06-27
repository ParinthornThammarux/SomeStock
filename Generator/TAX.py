def calc_dividend_tax(dividend_amount):
    tax_withheld = dividend_amount * 0.10
    tax_credit = dividend_amount / 9
    net_received = dividend_amount - tax_withheld
    return {
        "gross_dividend": dividend_amount,
        "tax_withheld": tax_withheld,
        "tax_credit": tax_credit,
        "net_received": net_received
    }

def calc_capital_gain_tax(sell_price, buy_price, fee=0.0, is_offmarket=False):
    gain = sell_price - buy_price - fee
    if is_offmarket:
        # Simplified: assume 10% flat tax for example
        tax_due = max(gain, 0) * 0.10
    else:
        tax_due = 0  # Not taxed in SET
    return {
        "gain": gain,
        "tax_due": tax_due
    }

def calc_derivative_tax(profit, previous_loss=0.0, fee=0.0, tax_rate=0.15):
    net_profit = profit - previous_loss - fee
    net_profit = max(net_profit, 0)
    tax_due = net_profit * tax_rate
    return {
        "net_profit": net_profit,
        "tax_due": tax_due
    }
