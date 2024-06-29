from calulate_budget_methods import collect_items, calculate_shared_split_for_mock_values, \
    create_shared_summary_for_all_payments, save_budget, update_total, calculate_required_earnings, \
    calculate_required_earning_for_equal_salary, calculate_left_to_pay_value, static_calculate_budget

if __name__ == "__main__":
    # =========== Mock values =============
    mock_earnings = {
        "person1": 2000,  # Monthly Salary

        "person2": 1500, # Monthly Salary
    }

    mock_extra_sources = {
        "left over from last month": {"cost": 29.13},
        # other left-overs go in 'discount' key
    }

    mock_overdraft = 0

    mock_flex = {
        # "mock_stuff": {"cost": 230}

        "flex1": {"cost": 66},
        "flex2": {"cost": 34},
        "flex3": {"cost": 31},
        "flex4": {"cost": 23},
    }

    mock_direct_debits = {
        "rent": {"cost": 1200, "date": 29, "is_shared": True},
        "phone bill": {"cost": 15.0, "date": 2},
        "google storage": {"cost": 1.59, "date": 5},
        "spotify": {"cost": 19.99, "date": 22},
        "the gym": {"cost": 21.99, "date": 2},
    }

    # over the longest months (31 days) we have 7 days of the week * 4
    # 7 * 4 == 28, leaving 3 days left
    # the allowance below is the most expensive way the month can fall, in terms of which days are repeated
    mon, tues, wed, thur, fri, sat, sun = 4, 4, 4, 4, 5, 5, 5
    max_allowance = ((mon + tues + wed + thur + fri + sat + sun) * 5) + ((fri + sat) * 15) + (sun * 10)
    # = £350.0

    mock_left_to_pay_value = calculate_left_to_pay_value(max_allowance, mock_direct_debits, mock_flex)

    cleaning, babysitting = 15, 12
    in_child_care_account = 52.46

    # Food:
    food_shops = 500
    person1_extra_food = [1.20, 5.15, 1.99, 6.8, 8.6, 7.59, 3.15, 13.75]
    person2_extra_food = 60
    other_shop = 100
    total_food_shops = food_shops + sum(person1_extra_food) + person2_extra_food + other_shop

    other_food_contribution = round((total_food_shops / 4), 2)

    # Bills:
    water, wifi, energy, car_tax, council_tax = 49, 39, 180, 15.75, 173
    bills = round(((wifi + energy + council_tax) * (2 / 3)) + (water * (3 / 4)) + (car_tax / 4), 2)

    mock_separate_payments = {
        "elisa nursery": {"cost": 308.25 - in_child_care_account,
                          "discount": 63.85, "is_shared": True},
        'shopping': {"cost": total_food_shops, "discount": other_food_contribution, "is_shared": True},
        "mum bills": {"cost": bills,
                      "discount": 237.17,  # left over
                      "date": 29, "is_shared": True},
        "driving ticket": {"cost": 35 * 4},

        # TODO: separate these from total budget
        "person2's visa fee": {"cost": 250, "is_shared": True},
        "ale cleaning": {
            # # 3.5 on thursdays, plus 3 more this time
            # "cost": (3.5 * 4) * ale_cleaning,

            # Total From Last Month:
            "cost": 30 + 22.50 + 37.50 + 45 + 30,  # = £165
            "discount": 15,  # Left over
            "is_shared": True
        },
        # "ale cleaning left over": {"cost": 15},
        "ale elisa": {
            # # 4hrs on wednesday/tuesday + 1.5hrs thursday
            # "cost": ((4 + 1.5) * 4) * ale_elisa,

            # Total From Last Month:
            "cost": 48 + 48 + 30 + 30 + 30 + 42 + 33 + 42 + 30 + 40,  # = £373
            "is_shared": True
        },
        "rent": {"cost": 1250, "discount": 40, "is_shared": True},
        "bills": {"cost": 200, "is_shared": True},
        "food": {"cost": 600, "is_shared": True},
        "council tax": {"cost": 124, "discount": 30, "is_shared": True},
        "wifi": {"cost": 30, "is_shared": True},
    }
    static_calculate_budget(
        earnings=mock_earnings, extra_sources=mock_extra_sources,
        overdraft=mock_overdraft, init_flex=mock_flex,
        init_direct_debits=mock_direct_debits,
        init_separate_payments=mock_separate_payments
    )
