from calulate_budget_methods import collect_items, calculate_shared_split_for_mock_values, \
    create_shared_summary_for_all_payments, save_budget, update_total, calculate_required_earnings, \
    calculate_required_earning_for_equal_salary, calculate_left_to_pay_value, static_calculate_budget


def calculate_budget(
        test: bool, calculation_type: str, earnings_mock=None, extra_sources_mock=None, overdraft_mock=None,
        left_to_pay_value_mock=None, flex_mock=None, direct_debits_mock=None, separate_payments_mock=None
):
    print(f"Calculating {calculation_type.lower()}\n================\n")

    to_mock = True
    if test and to_mock:
        salary = earnings_mock["oscar"]
        earnings = earnings_mock
        earnings["total"] = salary + earnings["manu"]
    else:
        earnings = {"total": 0}

        if calculation_type == "budget":
            question_string = "How much were you paid this month?\n£"
        else:
            question_string = "How much do you have left this month?\n£"
        salary = round(float(input(question_string)), 2)
        earnings["oscar"] = salary
        earnings["manu"] = round(float(input("How much did manu earn this month?\n£")), 2)
        earnings["total"] = salary + earnings["manu"]
        print("")

    month_tally = {"salary": salary}

    # =========================
    # Extra Sources of Money
    to_mock = True
    if test and to_mock:

        extra_sources = extra_sources_mock
        extra_sources["total"] = sum(source["cost"] for source in extra_sources_mock.values())
    else:
        extra_sources = collect_items(
            "Do you have any extra sources of money?\ne.g. savings/payments. y/n\n",
            "extra sources of money"
        )
        print("")
    month_tally["extra sources"] = extra_sources

    # ==========================
    # Overdraft
    to_mock = True
    if test and to_mock:
        overdraft = overdraft_mock
    else:
        overdraft: float = float(input("\nHow much overdraft is currently taken out?\n£"))
        print("")

    month_tally["overdraft"] = overdraft

    # ==========================
    # Budget (includes left to pay + extra payments)
    """
    yet_to_pay includes all direct debits taken out of the budget pot, including:
    - daily allowance
    - direct debits
    - flex payments
    """
    to_mock = True
    if test and to_mock:
        left_to_pay_value = left_to_pay_value_mock
    else:
        left_to_pay_value = float(input("\nHow much is to pay in 'left to pay' in monzo?\n£"))
        print("")
    budget = {
        "total": {"oscar": left_to_pay_value, "manu": 0, "together": left_to_pay_value},
        "left to pay": {"value": left_to_pay_value,
                        "total": {"oscar": left_to_pay_value, "manu": 0, "together": left_to_pay_value}},
    }

    to_mock = True
    if test and to_mock:
        unsplit_flex = flex_mock
        tot_value = sum(val["cost"] for val in flex_mock.values())
        unsplit_flex["total"] = {"oscar": tot_value, "together": tot_value}

        flex = calculate_shared_split_for_mock_values(unsplit_flex, earnings)
    else:
        flex = collect_items(
            "\nDo you have any payments on Monzo Flex?\ny/n\n",
            "flex payments",
            False,
            True,
            earnings
        )
        print("")
    budget["left to pay"]["flex"] = flex
    budget["left to pay"] = update_total(budget["left to pay"], flex)

    # Direct Debits
    to_mock = True
    if test and to_mock:
        unsplit_direct_debits = direct_debits_mock

        direct_debits = calculate_shared_split_for_mock_values(unsplit_direct_debits, earnings)
    else:
        direct_debits = collect_items(
            "Do you have any direct-debits or standing orders with known payment date?\ny/n\n",
            "direct debits",
            True,
            True,
            earnings
        )
        print("")

    budget["left to pay"]["direct debits"] = direct_debits
    budget["left to pay"] = update_total(budget["left to pay"], direct_debits)

    # left to pay value from monzo doesn't know about splitting payments
    # this means that it captures the "together" totals and not the "oscar" total
    allowance = round(left_to_pay_value - (flex["total"]["together"] + direct_debits["total"]["together"]), 2)
    budget["left to pay"]["allowance"] = allowance

    # Direct Debits Separate to Monzo
    to_mock = True
    if test and to_mock:
        unsplit_separate_payments = separate_payments_mock

        separate_payments = calculate_shared_split_for_mock_values(unsplit_separate_payments, earnings)
    else:
        separate_payments = collect_items(
            "Do you have any direct-debits or standing orders that you're not sure when they'll be paid?\ny/n\n",
            "separate payments",
            False,
            True,
            earnings
        )
        print("")

    budget["separate payments"] = separate_payments
    budget = update_total(budget, separate_payments)

    month_tally["budget"] = budget
    shared_ = create_shared_summary_for_all_payments(
        flex=flex,
        direct_debits=direct_debits,
        separate_payments=separate_payments,
        earnings=earnings
    )
    summary_totals = {"salary": {
        "oscar": round(salary, 2),
        "manu": round(earnings["manu"])
    }, "extra sources": round(extra_sources["total"], 2), "NET IN": round(salary + extra_sources["total"], 2),
        "overdraft": round(overdraft, 2), "budget": {
            "oscar": round(budget["total"]["oscar"], 2),
            "=> into budget (together)": round(
                budget["left to pay"]["flex"]["total"]["together"] +
                budget["left to pay"]["direct debits"]["total"]["together"] +
                budget["left to pay"]["allowance"] +
                budget["separate payments"]["total"]["together"],
                2),
        }, "left to pay": round(left_to_pay_value, 2), "flex": {
            "oscar": round(flex["total"]["oscar"], 2),
            "manu": round(flex["total"]["manu"], 2),
            "together": round(flex["total"]["together"], 2)
        }, "direct debits": {
            "oscar": round(direct_debits["total"]["oscar"], 2),
            "manu": round(direct_debits["total"]["manu"], 2),
            "together": round(direct_debits["total"]["together"], 2)
        }, "allowance": round(allowance, 2), "separate payments": {
            "oscar": round(separate_payments["total"]["oscar"], 2),
            "manu": round(separate_payments["total"]["manu"], 2),
            "together": round(separate_payments["total"]["oscar"], 2)
        }, "NET OUT": {
            "oscar": {
                "total": round(
                    overdraft + left_to_pay_value + separate_payments["total"]["oscar"] + extra_sources["total"], 2
                ),
            },
            "manu": {
                "total": round(
                    shared_["total"]["manu"]
                ),
                "split payments": round(
                    shared_["total"]["manu"]
                ),
                "split percentage": round(
                    (shared_["total"]["manu"] / earnings["manu"]) * 100, 2
                )
            },
        }}
    summary_totals["NET OUT"]["oscar"]["personal (unshared)"] = round(
        summary_totals["NET OUT"]["oscar"]["total"] -
        shared_["total"]["oscar"],
        2
    )
    summary_totals["NET OUT"]["oscar"]["personal (without overdraft)"] = summary_totals["NET OUT"]["oscar"][
                                                                             "personal (unshared)"] - overdraft
    summary_totals["NET OUT"]["oscar"]["split payments"] = round(shared_["total"]["oscar"], 2)
    summary_totals["NET OUT"]["oscar"]["split percentage"] = round(
        (summary_totals["NET OUT"]["oscar"]["split payments"] / salary) * 100, 2
    )

    summary_totals["NET OUT"]["together"] = {
        "total out": round(
            summary_totals["NET OUT"]["oscar"]["total"] +
            summary_totals["NET OUT"]["manu"]["total"],
            2
        ),
        # This is the total price of the split payments
        "split total": round(
            shared_["total"]["oscar"] + shared_["total"]["manu"]
        )
    }

    summary_totals["manu remaining"] = round(earnings["manu"] - summary_totals["NET OUT"]["manu"]["total"], 2)
    #     "oscar total": round(
    #         overdraft + left_to_pay_value + separate_payments["total"]["oscar"] + extra_sources["total"], 2
    #     ),
    #     "oscar unshared":
    #     "together": round(overdraft + summary_totals["=> into budget (together)"] + extra_sources["total"], 2),
    # },
    # summary_totals[ "NET OUT OSCAR"] = round(
    #     overdraft +
    #     left_to_pay_value +
    #     separate_payments["total"]["oscar"] +
    #     extra_sources["total"],
    #     2)

    # summary_totals["NET OUT OSCAR"] =
    #     summary_totals["NET OSCAR UNSHARED OUT"] = round(summary_totals["NET OUT"]["oscar"] - shared_["total"]["oscar"], 2)
    #     summary_totals["NET OSCAR UNSHARED OUT (without overdraft)"] = round(
    #         summary_totals["NET OUT"]["oscar"] -
    #         (overdraft + shared_["total"]["oscar"])
    #         , 2)
    #     summary_totals["NET OSCAR SHARED OUT"] = round(shared_["total"]["oscar"], 2)
    #     summary_totals["NET OSCAR SHARED PERCENTAGE"] = round(
    #         summary_totals["NET OSCAR SHARED OUT"] / summary_totals["salary"], 8) * 100
    #     summary_totals["NET MANU SHARED OUT"] = round(shared_["total"]["manu"], 2)
    #     summary_totals["NET MANU SHARED PERCENTAGE"] = round(
    #         summary_totals["NET MANU SHARED OUT"] / summary_totals["manu salary"], 8) * 100
    #     summary_totals["manu remaining"] = summary_totals["manu salary"] - summary_totals["NET MANU SHARED OUT"]
    #     summary_totals["NET SHARED OUT"] = summary_totals["NET OSCAR SHARED OUT"] + summary_totals["NET MANU SHARED OUT"]
    #
    remainder = round(
        summary_totals["NET IN"] - summary_totals["NET OUT"]["oscar"]["total"] + summary_totals["NET OUT"]["manu"][
            "total"],
        2
    )

    if remainder < 0:
        print(f"""Bad News, you can"t afford this month.. 
        With all the outgoings minused from the net incomings you will be {remainder} in debt..""")
        summary_totals["savings"] = 0
        summary_totals["overdrawn"] = -remainder
        summary_totals["========"] = "==========="
        summary_totals["available"] = allowance + remainder
    elif remainder == 0:
        print(f"With your current budget you are scraping by with £0 for savings and for extra expenses..")
        summary_totals["savings"] = 0
        summary_totals["=> extra expenses"] = 0
        summary_totals["========"] = "==========="
        summary_totals["available"] = allowance + summary_totals["extra_expenses"]
    else:
        print(f"After all your outgoings, there is £{remainder} left\n"
              f"Between Extra Expenses and Savings how would you like to split it?")
        summary_totals["savings"] = float(input("Savings:\n£"))
        summary_totals["=> extra expenses"] = remainder - summary_totals["savings"]
        print(f"Leaving £{summary_totals['=> extra expenses']} in Extra Expenses")
        summary_totals["========"] = "==========="
        summary_totals["available"] = round(allowance + summary_totals["=> extra expenses"], 2)

    summary_totals_key = {
        "salary": "Money oscar received this month; from work",
        "manu salary": "Money manu received this month; from work",
        "extra sources": "Extra money received this month, excluding main salary",
        "NET IN": "salary + extra sources",
        "overdraft": "overdraft taking into the month coming",
        "oscar budget": "overall budget for oscar this month",
        "=> into budget (together)": "total money required for month coming, ignoring oscar/manu split",
        "left to pay": "value given by monzo of flex + direct debits + allowance"
    }

    save_budget(test=test, calculation_type=calculation_type, month_tally=month_tally, shared=shared_,
                summary_totals_key=summary_totals_key, summary_totals=summary_totals)
    print("END")


if __name__ == "__main__":
    # =========== Mock values =============
    mock_earnings = {
        # "oscar": 3571.96,  #55k
        # "oscar": 2530.91,  #40k
        # "oscar": 2253.84,  #35k
        # "oscar": 2140.00,  #33k
        "oscar": 1911.04,  # 28.8k - now

        "manu": 1601,
        # "manu": 689.92,  # Manu Maternity
    }

    sandra_flights = 156.47
    mock_extra_sources = {
        "sandra flights to brazil": {"cost": sandra_flights},
        "left over": {"cost": 13.84},
    }

    mock_overdraft = 0  # 38.53

    mock_flex = {
        # "mock_stuff": {"cost": 150}

        "sandra flights to brazil": {"cost": sandra_flights},
        "shared flights to brazil": {"cost": 319 - sandra_flights, "is_shared": True},
        "elisa's iPad": {"cost": 74},
    }

    mock_direct_debits = {
        "mum bills": {"cost": 810/2, "date": 29, "is_shared": True},
        "mum rent": {"cost": 200/2, "date": 29, "is_shared": True},
        "ee": {"cost": 9.0, "date": 2},
        "google storage": {"cost": 1.59, "date": 5},
        "spotify": {"cost": 17.99, "date": 29},
        "BJJ": {"cost": 40, "date": 1},
        "The Union": {"cost": 8.33, "date": 1},
        "the gym": {"cost": 25.99, "date": 7},
    }

    # over the longest months (31 days) we have 7 days of the week * 4
    # 7 * 4 == 28, leaving 3 days left
    # the allowance below is the most expensive way the month can fall, in terms of which days are repeated
    mon, tues, wed, thur, fri, sat, sun = 4, 4, 4, 4, 5, 5, 5
    max_allowance = ((mon + tues + wed + thur + fri + sat + sun) * 5) + ((fri + sat) * 15) + (sun * 10)
    # = £350.0

    mock_left_to_pay_value = calculate_left_to_pay_value(max_allowance, mock_direct_debits, mock_flex)

    mock_separate_payments = {
        # "elisa nursery": {"cost": 839.5 - 158.62, "is_shared": True},
        "elisa nursery": {"cost": 308.25 - 158.62, "is_shared": True},

        # TODO: separate these from total budget
        "manu's visa fee": {"cost": 250, "is_shared": True},
        "ale": {"cost": (2.5 * 12) * 2 * (4/2), "is_shared": True},

        # "elisa nursery": {"cost": 311.5 * 0.8, "is_shared": True},
        # "rent": {"cost": 1250, "is_shared": True},
        # "bills": {"cost": 200, "is_shared": True},
        # "food": {"cost": 600, "is_shared": True},
        # "council tax": {"cost": 124, "is_shared": True},
        # "wifi": {"cost": 30, "is_shared": True},
        # "boulder brighton x10 pass": {"cost": 27},
    }
    static_calculate_budget(
        earnings=mock_earnings, extra_sources=mock_extra_sources,
        overdraft=mock_overdraft, init_flex=mock_flex,
        init_direct_debits=mock_direct_debits,
        init_separate_payments=mock_separate_payments
    )
    # calculate_budget(
    #     True, calculation_type="budget",
    #     earnings_mock=mock_earnings, extra_sources_mock=mock_extra_sources, overdraft_mock=mock_overdraft,
    #     left_to_pay_value_mock=mock_left_to_pay_value, flex_mock=mock_flex, direct_debits_mock=mock_direct_debits,
    #     separate_payments_mock=mock_separate_payments
    #                  )

    # ================= Required Earnings ==============
    spa, happy_days, brazil_school = 105 * 4, 450, 180 / 3
    shared_payments = {
        "child care (with discount)": happy_days,
        "house rent": 700,
        "bills": 0,
        "food": 0
    },
    flex = {
        "manu's phone": 58,
        "h&m elisa": 23,
        "manu lingerie": 21.91,
        "pride": 19,
        "petrol": 18.80,
        "manu's dublin flights": 15
    }
    personal_spending = {
        "boulder brighton": 46,
        "ee": 10,
        "google storage": 1.59,
        "the gym": 24.99,
        "spotify": 16.99,
        "disney+": 7.99
    }
    extras = {
        "extra spending": 100,
        "savings": 100
    }
    # calculate_required_earnings(shared_payments, 1841.02, personal_spending, extras)
    # calculate_required_earning_for_equal_salary(shared_payments, personal_spending, extras)
