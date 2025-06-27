
def calculate_personal_income_tax_from_foreign_gain(gain):
    """
    คำนวณภาษีจากกำไรต่างประเทศตามอัตราก้าวหน้าไทย (ปี 2567)
    """
    brackets = [
        (150000, 0.0),
        (300000, 0.05),
        (500000, 0.10),
        (750000, 0.15),
        (1000000, 0.20),
        (2000000, 0.25),
        (5000000, 0.30),
        (float('inf'), 0.35),
    ]

    tax = 0.0
    previous_limit = 0

    for limit, rate in brackets:
        if gain > limit:
            taxable = limit - previous_limit
            tax += taxable * rate
            previous_limit = limit
        else:
            taxable = gain - previous_limit
            tax += taxable * rate
            break

    return tax
