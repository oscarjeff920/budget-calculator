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
        salary = 1842.82
    else:
        salary = float(input("How much were you paid this month?\n£"))

    month_tally = {'salary': salary}

    # =========================
    # Extra Sources of Money
    if testing:
        extra_sources = { "manu's phone": { "cost": 58.0 }, "manu's flight": { "cost": 15.0 }, "net": 73.0 }
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
    # Budget
    budget = {'total': 0}
    if testing:
        flex = {
            "manu's ireland flight": { "cost": 15.0 },
            "manu's new phone": { "cost": 58.0 },
            "new shoes": {  "cost": 22.0 },
            "elisa's blood test": { "cost": 39.0 },
            "new phone": { "cost": 77.0 },
            "net": 211.0
        }
    else:
        flex = collect_items(
            "Do you have any payments split with Monzo Flex?\ny/n\n",
            "flex payment",
        )

    budget['flex'] = flex
    budget['total'] += flex['net']

    if testing:
        yet_to_pay = 1100
        direct_debits = {
            "boulder brighton": { "cost": 46.0, "date": 1 },
            "elisa swimming": { "cost": 29.68, "date": 3 },
            "the gym": { "cost": 24.99, "date": 7 },
            "EE": { "cost": 13.5, "date": 25  },
            "mum": { "cost": 700.0, "date": 29 },
            "spotify": { "cost": 16.99, "date": 29 },
            "net": 831.16
        }
    else:
        yet_to_pay = float(input("How much is to pay in 'left to pay' in monzo?\n£"))
        # Direct Debits
        direct_debits = collect_items(
            "Do you have any direct-debits or standing orders paid directly from your account?\ny/n\n",
            "direct debits",
            True
        )
    # Separate direct debits with 'elisa' in the name
    allowance = round(yet_to_pay - direct_debits['net'], 2)
    budget['yet to pay'] = {'net': yet_to_pay, 'direct debits': direct_debits, 'allowance': allowance}
    budget['total'] += yet_to_pay

    # Direct Debits Separate to Monzo
    if testing:
        separate_payments = {
            "elisa's nursery": { "cost": 382.5, "date": 2 },
            "net": 382.5
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
    # print("")
    # for item, value in month_tally.items():
    #     if type(value) != dict:
    #         print(f"{item}: {value}")
    #     else:
    #         print(f"{item}:")
    #         for item1, value1 in value.items():
    #             if type(value1) != dict:
    #                 print(f"    - {item1}: {value1}")
    #             else:
    #                 print(f"    - {item1}:")
    #                 for item2, value2 in value1.items():
    #                     if type(value2) != dict:
    #                         print(f"        - {item2}: {value2}")
    #                     else:
    #                         print(f"        - {item2}:")
    #                         for item3, value3 in value2.items():
    #                             print(f"            - {item3}: {value3}")

    summary_totals = {
        "salary": month_tally['salary'],
        "extra sources": month_tally['extra sources']['net'],
        "NET IN": month_tally['salary'] + month_tally['extra sources']['net'],
        "overdraft": month_tally['overdraft'],
        "direct debits": month_tally['budget']['yet to pay']['direct debits']['net'],
        "allowance": month_tally['budget']['yet to pay']['allowance'],
        "separate payments": month_tally['budget']['separate payments']['net'],
        "flex": month_tally['budget']['flex']['net'],
        "NET OUT": overdraft + yet_to_pay + separate_payments['net'] + flex['net']
    }

    summary_totals['remainder'] = round(
        summary_totals['salary'] + summary_totals['extra sources'] - (
        summary_totals['overdraft'] + summary_totals['direct debits'] + summary_totals['separate payments'] +
        summary_totals['allowance'] + summary_totals['flex']),
        2
    )

    save_budget(month_tally = month_tally, summary_totals = summary_totals)
    print("END")


if __name__ == "__main__":
    calculate_budget(testing=True)
