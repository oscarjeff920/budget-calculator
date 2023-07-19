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
import typing

import datetime as dt


def counting_loop(question_string: str, obj_name: str, obj: typing.Dict, date_today: int = 0):
    question: str = input(question_string).lower()

    _ = 0
    while question != 'n' and question != 'no':
        _ += 1

        name: str = input(f'\nName of {obj_name} {_}: ')
        if name == "":
            final_question: str = input(f"Is that all of your {obj_name}? y/n\n").lower()
            if final_question != 'n' and final_question != 'no':
                break
            else:
                _ -= 1
                continue
        value: float = float(input(f"How much £ from {name}?\n£"))
        if date_today:
            date: int = int(input("Date of payment: ").lower()
                            .replace('st', '').replace('nd', '').replace('rd', '').replace('th', ''))
            # As my bank is dynamic and automatically takes payments out
            # I need to account for that by only adding payments yet to be taken out of my account
            if date_today < int(date):
                obj['not paid'][name] = dict(value=value, date=date)
                obj['not paid']['total'] += value

        obj['total'] += value
        obj[name] = dict(value=value, date=date)

    # Might be better to have separate payments and not_paid dictionaries so that they can be easily ordered
    # after they're sorted by date, the totals for each are added as a key and
    # they're put together in a single dict after
    # {'payments': {}, 'not paid': {}}
    if date_today:
        type(obj)
        obj = sorted(obj.items(), key=lambda x: x[1]['date'])

    return obj


def calculate_budget(testing: bool):
    date_today: int = int(str(dt.datetime.now().date()).split('-')[-1])
    if testing:
        overdraft = 55
    else:
        overdraft: float = float(input("How much overdraft is currently taken out?\n£"))

    # if testing:
    #     extra_sources =
    # try:
    #     extra_sources: typing.Dict = counting_loop(
    #         question_string='Do you have any extra sources of money?\ne.g. savings/payments. y/n\n',
    #         obj_name='extra sources',
    #         obj={'total': 0}
    #     )
    # except ValueError:
    #     print("\nWhoops that didn't go right, try again\n")
    #     extra_sources: typing.Dict = counting_loop(
    #         question_string='Do you have any extra sources of money?\ne.g. savings/payments. y/n\n',
    #         obj_name='extra sources',
    #         obj={'total': 0}
    #     )

    extra_sources = {'total': 88.0, 'll': 33.0, 'js': 55.0}
    print(f"\n{len(extra_sources) - 1} extra sources of money.\nTotal extra_money = £{extra_sources['total']}")

    print("BUDGET")

    try:
        outgoings: typing.Dict = counting_loop(
            question_string='List your Monzo tracked outgoings:',
            obj_name='outgoings',
            obj={'total': 0, 'not paid': {'total': 0},
                 '(left to pay)': float(input("'Left to pay' in monzo budget pot:\n£"))},
            date_today=date_today
        )
    except ValueError:
        print("\nWhoops that didn't go right, try again\n")
        outgoings: typing.Dict = counting_loop(
            question_string='List your Monzo tracked outgoings:',
            obj_name='outgoings',
            obj={'total': 0, 'not paid': {'total': 0},
                 '(left to pay)': float(input("'Left to pay' in monzo budget pot:\n£"))},
            date_today=date_today
        )

    print(f"outgoings: {outgoings}")

    try:
        extra_outgoings: typing.Dict = counting_loop(
            question_string="\n\nAre there any outgoings not accounted for, "
                            "e.g. standing orders or payments monzo isn't aware of? y/n\n",
            obj_name='extra outgoings',
            obj={'total': 0, 'not paid': {'total': 0}},
            date_today=date_today
        )
    except ValueError:
        print("\nWhoops that didn't go right, try again\n")
        extra_outgoings: typing.Dict = counting_loop(
            question_string="\n\nAre there any outgoings not accounted for, "
                            "e.g. standing orders or payments monzo isn't aware of? y/n\n",
            obj_name='extra outgoings',
            obj={'total': 0, 'not paid': {'total': 0}},
            date_today=date_today
        )

    print(f"extra_outgoings: {extra_outgoings}")

    budget = {
        'total': 0,
        'not paid': {'total': outgoings['not paid']['total'], 'outgoings': outgoings['not paid']},
        'allowance': outgoings['(left to pay)'] - outgoings['not paid']['total'],
        'outgoings': outgoings,
        'extra outgoings': extra_outgoings}

    # for val in budget.keys():
    #     print(val)

    # print("\n\nBUDGET")
    # budget = {'total': 0, 'sum_total': 0}
    #
    #
    # print('Monzo tracked outgoings:')
    # l = 0
    # while True:
    #     l += 1
    #     name_ = input(f"\nName of outgoing {l}: ")
    #     if name_ == "":
    #         outgoings_question = input("\nIs that all of your outgoings? y/n\n").lower()
    #         if outgoings_question != 'n' and outgoings_question != 'no':
    #             break
    #         else:
    #             l -= 1
    #             continue
    #
    #     value = float(input("Cost: £"))
    #     date = input("Date of payment: ")
    #
    #     # As my bank is dynamic and automatically takes payments out I need to account for that by only adding payments
    #     # yet to be taken out of my account
    #     if date_today < int(date):
    #         outgoings['sum_total'] += value
    #     outgoings['total'] += value
    #     outgoings[name_] = {'value': value, 'date': date}
    #
    # outgoings = sorted(outgoings.items(), key=lambda x: x[1]['date'])
    #
    # extra_outgoings = {'total': 0, 'sum_total': 0}
    # extra_outgoings_question = input(
    #     "\n\nAre there any outgoings not accounted for, e.g. standing orders or payments monzo isn't aware of? y/n\n"
    # ).lower()
    # while extra_outgoings_question != 'n' or extra_outgoings_question != 'no':
    #     name = input('Name of extra outgoing: ')
    #
    #     if name == "":
    #         final_extra_outgoings_question = input('\nIs that all of your outgoings? y/n\n').lower()
    #         if final_extra_outgoings_question != 'n' and final_extra_outgoings_question != 'no':
    #             break
    #         else:
    #             l -= 1
    #             continue
    #
    #     value = float(input(f"Cost\n£"))
    #     date = input("Date of payment: ")
    #
    #     # As my bank is dynamic and automatically takes payments out I need to account for that by only adding payments
    #     # yet to be taken out of my account
    #     if date_today < int(date):
    #         extra_outgoings['sum_total'] += value
    #     extra_outgoings['total'] += value
    #     extra_outgoings[name] = value
    # extra_outgoings = sorted(extra_outgoings.items(), key=lambda x: x[1]['date'])
    #
    # outgoings['extra_outgoings'] = extra_outgoings
    # outgoings['total'] += extra_outgoings['total']
    #
    # budget['total'] += outgoings['total']
    # budget['outgoings'] = outgoings
    #
    # budget['allowance'] = outgoings['(left_to_pay)'] - outgoings['total']
    # budget['total'] += budget['allowance']
    #
    # print(f"\nOverdraft: ${overdraft}\nExtra Sources: ${extra_sources}\nBudget: ${budget}")
    # print("FLEX:")
    # flex = {'total': 0}
    # flex_question = input('Do you have any flex payments to make?\n')
    # _ = 0
    # while flex_question != 'n' and flex_question != 'no':
    #     i = 0
    #     sources_question = input("Do you have any extra sources of money?\ne.g. savings/payments. y/n\n").lower()
    #     while sources_question != 'n' and sources_question != 'no':
    #         i += 1
    #
    #         name_ = input(f"\nName of source {i}: ")
    #         if name_ == "":
    #             final_sources_question = input("Is that all of your outgoings? y/n\n").lower()
    #             if final_sources_question != 'n' or final_sources_question != 'no':
    #                 break
    #             else:
    #                 i -= 1
    #                 continue
    #         value = float(input(f"How much £ from {name_}?\n£"))
    #
    #         extra_sources['total'] += value
    #         extra_sources[name_] = value


if __name__ == "__main__":
    calculate_budget(testing=True)
