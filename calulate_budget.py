"""
Plan
i = input
c = computed

i overdraft
i extra money (manu's flex)

Budget
i left to pay
i BREAKDOWN
c sum of breakdown
c allowance
allowance = sum of breakdown - left to pay

i additional payments
c budget_total

Flex
i flex components

c flex_total

i pay

Totals:
print(f"SUM: £{pay} (pay) - £{budget_total} (total budget) - £{flex_total} (total flex payments) + £{extra_money} (extra money) - £{overdraft} (overdraft)")
remainder = pay - budget_toal - flex_total + extra_money - overdraft

summary = {}

print(f"REMAINDER = £{remainder})

for value in summary:
	print(f"value: £{summary[value]}")
"""
import json
import datetime as dt


def collect_items(question_string, item_type, has_payment_dates=False):
    summary = {}
    item_number = 0
    total = 0

    # Asking the question from the question string to discover if any of these items exist; if not skip the loop.
    question = input(question_string)
    if question == 'yes' or question == 'y' or question == '':
        while True:
            item_number += 1

            # Asking the name of the source, if empty string is entered, its assumed that there are no more sources
            name: str = input(f'\nName of {item_type} {item_number}: ')
            if name == "__list__":
                print([name for name in summary])
            elif name == "":
                # Double checking that there are no more sources
                final_question: str = input(f"Is that all of your {item_type}? y/n\n").lower()
                if final_question != 'n' and final_question != 'no':
                    break
                else:
                    # if there actually are more sources (n/no) then the item number needs to be reset
                    item_number -= 1
                    continue

            cost: float = float(input(f"How much £ from {name}?\n£"))
            total += cost
            if has_payment_dates:
                date: int = int(input("Date of payment: ").lower()
                                .replace('st', '').replace('nd', '').replace('rd', '').replace('th', ''))
                source_details = {"cost": cost, "date": date}
            else:
                source_details = {"cost": cost}

            summary[name] = source_details

        if has_payment_dates:
            summary = sort_payment_dates(summary)

        summary.update({"net": total})

    print(f"{item_type} summary: {summary}")
    return summary


def sort_payment_dates(payments):
    return dict(sorted(payments.items(), key=lambda x: x[1]['date']))

def copy_over_items(summary1, summary2, item_type):
    summary2[item_type] = summary1[item_type].copy()
    return summary2


def save_budget(**kwargs):
    today = str(dt.datetime.now())
    date = today[:today.find(" ")]

    filename = f"Budget:{date}"

    # for budget_name, budget in kwargs.items():
    with open(f"{filename}.json", "w") as budget_file:
        json.dump(kwargs, budget_file)


def calculate_budget(testing: bool):
    # date_today: int = int(str(dt.datetime.now().date()).split('-')[-1])
    # summary_from_today = {'total': 0, 'date_today': date_today}
    if testing:
        salary = 1841.22
    else:
        salary = float(input("How much were you paid this month?\n£"))

    month_tally = {'salary': salary}

    # =========================
    # Extra Sources of Money
    if testing:
        extra_sources = {
            "for manu's phone": {'cost': 58.0},
            "for manu's tickets to dublin": {'cost': 15.0},
            'left from last month': {'cost': 1.17}, 'net': 74.17
        }
    else:
        extra_sources = collect_items(
            'Do you have any extra sources of money?\ne.g. savings/payments. y/n\n',
            'extra sources of money'
        )
    month_tally['extra sources'] = extra_sources

    # ==========================
    # Overdraft
    if testing:
        overdraft = 0
    else:
        overdraft: float = float(input("How much overdraft is currently taken out?\n£"))

    month_tally['overdraft'] = overdraft

    # ==========================
    # Budget (includes left to pay + extra payments)
    """
    yet_to_pay includes all direct debits taken out of the budget pot, including:
    - daily allowance
    - direct debits
    - flex payments
    """
    if testing:
        left_to_pay_value = 1294.07
    else:
        left_to_pay_value = float(input("How much is to pay in 'left to pay' in monzo?\n£"))
    budget = {"total": left_to_pay_value, "left to pay": {"net": left_to_pay_value}}

    if testing:
        flex = {
            "manu's phone": {'cost': 58.0},
            "manu's tickets to dublin": {'cost': 15.0},
            'suit shoes': {'cost': 22.0},
            "elisa's horrible blood test": {'cost': 39.0},
            'my replacement phone ': {'cost': 77.0},
            'net': 211.0
        }
    else:
        flex = collect_items(
            "Do you have any payments split with Monzo Flex?\ny/n\n",
            "flex payment",
        )
    budget['left to pay']['flex'] = flex

    # Direct Debits
    if testing:
        direct_debits = {
            'the gym': {'cost': 24.99, 'date': 7},
            'mum rent': {'cost': 700.0, 'date': 29},
            'net': 724.99
        }
    else:
        direct_debits = collect_items(
            "Do you have any direct-debits or standing orders paid directly from your account?\ny/n\n",
            "direct debits",
            True
        )

    budget['left to pay']['direct debits'] = direct_debits
    allowance = round(left_to_pay_value - (flex['net'] + direct_debits['net']), 2)
    budget['left to pay']['allowance'] = allowance

    # Direct Debits Separate to Monzo
    if testing:
        separate_payments = {
            'boulder brighton': {'cost': 46.0, 'date': 1},
            "elisa's nursery": {'cost': 286.88, 'date': 3},
            'EE': {'cost': 13.5, 'date': 21},
            'spotify': {'cost': 16.99, 'date': 29},
            'net': 363.37
        }
    else:
        separate_payments = collect_items(
                "Do you have any direct-debits or standing orders that monzo cant auto pay for you?\ny/n\n",
                "separate payments",
                True
            )

    budget['separate payments'] = separate_payments
    budget['total'] += separate_payments['net']


    month_tally['budget'] = budget

    # Separate costs with 'elisa' in the name
    summary_totals = {
        "salary": month_tally['salary'],
        "extra sources": month_tally['extra sources']['net'],
        "NET IN": month_tally['salary'] + month_tally['extra sources']['net'],
        "overdraft": month_tally['overdraft'],
        "into budget": round(month_tally['budget']['total'], 2),
        "left to pay": left_to_pay_value,
        "flex": month_tally['budget']['left to pay']['flex']['net'],
        "direct debits": month_tally['budget']['left to pay']['direct debits']['net'],
        "allowance": month_tally['budget']['left to pay']['allowance'],
        "separate payments": month_tally['budget']['separate payments']['net'],
        "NET OUT": overdraft + left_to_pay_value + separate_payments['net']
    }

    remainder = round(
        summary_totals['NET IN'] - summary_totals['NET OUT'],
        2
    )

    print(f"After all your outgoings, there is £{remainder} left\n"
          f"Between Extra Expenses and Savings how would you like to split it?")
    summary_totals['extra_expenses'] = float(input("Extra Expenses:\n£"))
    summary_totals['savings'] = remainder - summary_totals['extra_expenses']
    print(f"Leaving Savings:\n£{summary_totals['savings']}")
    summary_totals['========'] = '==========='
    summary_totals['available'] = allowance + summary_totals['extra_expenses']

    save_budget(month_tally = month_tally, summary_totals = summary_totals)
    print("END")


if __name__ == "__main__":
    calculate_budget(testing=True)
