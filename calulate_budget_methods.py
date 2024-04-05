import json
import datetime as dt
import os
import glob
import json
import typing


def grab_latest_budget_file(calculation_type):
    list_of_files = glob.glob(f'{calculation_type.lower().capitalize()}*.json')
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Extracted file {latest_file}")

    return latest_file


def extract_json_from_file(json_file):
    with open(json_file, 'r') as json_file_read:
        json_ = json.load(json_file_read)

    return json_


def removing_totals_from_dict(dict_):
    """We don't want to keep out total values as they will be recalculated once the dict is complete"""
    dict_.pop('total', None)

    return dict_


def create_new_month_tally(last_month_tally):
    new_monthly_tally = {}
    for key, element in last_month_tally.items():
        print(f"============\nChecking {key}")
        if type(element) != dict:
            # Item is a single value
            # if element is just a single value its easy to change or keep it the same
            answer = input(f"is {key} still {element}?\ny/n\n").lower()
            if answer == 'n' or answer == 'no':
                new_value = float(input(f"How much is {key} this month?\n£"))
            else:
                new_value = element
            new_monthly_tally[key] = new_value
        else:
            # Contains items from last month
            # if element is a dict we'll need to go into it to check if everything is the same to last month
            print("\nElement == dict")
            element = removing_totals_from_dict(element)
            print("")
            if len(element) > 0:
                print(f"'{key}' has elements within")
                sub_items = []
                for sub_key, sub_element in element.items():
                    sub_items.append({"sub_key": sub_key, "sub_element": sub_element})
                question = input("Are all of these elements the same this month?\ny/n\n").lower()
                answer = False if question == 'n' or question == 'no' else True
                if answer:
                    new_monthly_tally[key] = element
                else:
                    while not answer:
                        print("Select an incorrect element:")
                        for sub_key, sub_element in element.items():
                            print(f"key: {sub_key}, element: {sub_element}")
                        answer2 = input("").lower()
            else:
                # No items last month
                # if the dict is empty we want to check if it should be empty this month or populated from new payments
                is_same_answer = input(f"Last month {key}, was empty, is that the same this month?\ny/n\n").lower()
                if is_same_answer == 'n' or is_same_answer == 'no':
                    print(f"- Changing {key}")

                else:
                    # element has not changed from last month
                    print(f"{key} is the same")
                    print(element)
                    new_monthly_tally[key] = element
    print(f"\n===============\n{new_monthly_tally}")


def trace_over_old_budget(calculation_type):
    last_budget_file = grab_latest_budget_file(calculation_type)
    last_budget_tally = extract_json_from_file(last_budget_file)['month_tally']

    new_month_tally = create_new_month_tally(last_budget_tally)

    return new_month_tally


# =======================================================================
# ======================  'Share' Functions =============================
# =======================================================================

def is_shared_payment() -> bool:
    shared = input("is this a shared payment?\ny/n\n").lower()

    if shared == 'y' or shared == 'yes':
        return True
    else:
        return False


def create_shared_summary_for_all_payments(**kwargs):
    # TODO: CHECK THIS
    # I think we just want to grab all instances of shared payments from this function...
    split_summary = {'total': {'oscar': 0, 'manu': 0, 'together': 0}}

    for key, element in kwargs.items():
        if element.get('shared', None):
            # An element could be shareable but has no instances of sharing,
            # this conditional checks if there's actually shared payments
            if element['shared']['total']['manu'] > 0:

                for sub_key, sub_element in element.items():
                    if type(sub_element) == dict and sub_element.get('split', None):
                        split_summary[key] = {sub_key: sub_element['split']}
                        split_summary[key][sub_key]['together'] = round(sub_element['split']['together'], 2)
                        if sub_element.get('date', None): split_summary[key][sub_key]['date'] = sub_element['date']

                        split_summary['total']['oscar'] += split_summary[key][sub_key]['oscar']
                        split_summary['total']['manu'] += split_summary[key][sub_key]['manu']
        elif key != 'earnings':
            split_summary[key] = {
                'total': {'oscar': 0, 'oscar percent': 0, 'manu': 0, 'manu percent': 0, 'together': 0}
            }

    split_summary['total']['total'] = round(split_summary['total']['oscar'] + split_summary['total']['manu'], 2)
    return split_summary


def calculate_shared_split(
        cost: float, earnings: typing.Dict
) -> typing.Dict[str, float]:
    percent = cost / earnings['total']

    return {
        'oscar': round(percent * earnings['oscar'], 2),
        'manu': round(percent * earnings['manu'], 2),
        'percent': f'{round(percent * 100, 2)}%',
        'together': cost
    }


def calculate_shared_split_for_mock_values(mock_payments, earnings):
    print("Are any of the following split payments?")
    for name in mock_payments.keys():
        if name != 'total' and name != 'shared':
            print("- ", name)
    any_split_payments = input("y/n\n").lower()
    if any_split_payments == 'y' or any_split_payments == 'yes':
        number_of_split_payments = int(input("\nFrom this list, how many payments are split?\n"))
        if number_of_split_payments == 0:
            return mock_payments

        if mock_payments.get('total', None): mock_payments.pop('total')
        if mock_payments.get('shared', None): mock_payments.pop('shared')

        if number_of_split_payments == len(mock_payments):
            for payment in mock_payments.values():
                split = calculate_shared_split(payment['cost'], earnings)
                payment['cost'] = split['oscar']
                payment['split'] = split
        elif number_of_split_payments == 1:
            print("which payment is split?")
            for name in mock_payments.keys():
                if name != 'total' and name != 'shared':
                    print("- ", name)
            which_payment = input("").lower()
            split = calculate_shared_split(mock_payments[which_payment]['cost'], earnings)
            mock_payments[which_payment]['cost'] = split['oscar']
            mock_payments[which_payment]['split'] = split
        else:
            for name, payment in mock_payments.items():
                answer = input(f"Is '{name}' a shared payment?\ny/n\n").lower()

                if answer == 'y' or answer == 'yes':
                    split = calculate_shared_split(payment['cost'], earnings)
                    payment['cost'] = split['oscar']
                    payment['split'] = split

        # Because we're calculating the split we want to wipe 'total' and 'shared', if they exist (which they shouldn't).
        shared = {'total': {'oscar': 0, 'manu': 0}}
        total = {'oscar': 0, 'manu': 0}
        for name, payment in mock_payments.items():
            if payment.get('split', None):
                # First we add the split costs to both oscar and manu totals respectively
                total['oscar'] += payment['split']['oscar']
                total['manu'] += payment['split']['manu']

                # Second we add the split payment dict to shared dict by name
                shared[name] = payment['split']
                # Then we add the oscar and manu values to the shared total values, respectively
                shared['total']['oscar'] += payment['split']['oscar']
                shared['total']['manu'] += payment['split']['manu']
            else:
                total['oscar'] += payment['cost']

        total['together'] = total['oscar'] + total['manu']
        mock_payments['total'] = total

        shared['total']['together'] = shared['total']['oscar'] + shared['total']['manu']
        shared['total']['oscar percent'] = round((shared['total']['oscar'] / earnings['oscar']) * 100, 2)
        shared['total']['manu percent'] = round((shared['total']['manu'] / earnings['manu']) * 100, 2)
        mock_payments['shared'] = shared
    else:
        if mock_payments['total'].get('oscar', None) and mock_payments['total'].get('together', None):
            if not mock_payments['total'].get('manu', None):
                if mock_payments['total']['oscar'] == mock_payments['total']['together']:
                    mock_payments['total']['manu'] = 0
                else:
                    raise ValueError
        else:
            raise KeyError

    return mock_payments


def update_total(dict_, payment):
    dict_['total']['oscar'] += payment['total']['oscar']
    dict_['total']['manu'] += payment['total']['manu']
    dict_['total']['together'] += payment['total']['together']

    return dict_


# =======================================================================
# ==================  Main Budget Functions =============================
# =======================================================================


def collect_items(question_string, item_type, has_payment_dates=False, is_source_shareable=False, earnings=None):
    summary = {'total': 0}
    item_number = 0
    total = 0
    if is_source_shareable: shared = {'total': {'oscar': 0, 'manu': 0}}

    # Asking the question from the question string to discover if any of these items exist; if not skip the loop.
    question = input(question_string).lower()
    if question == 'yes' or question == 'y' or question == '':
        while True:
            item_number += 1
            source_details = {}

            # Asking the name of the source, if empty string is entered, its assumed that there are no more sources
            name: str = input(f'\nName of {item_type} {item_number}: ').lower()

            # If the user wants to check which items they've already entered
            # Entering __list__ will list them all in the console
            if name == "__list__":
                print([name for name in summary])
                item_number -= 1
                continue
            elif name == "":
                # Double-checking that there are no more sources
                final_question: str = input(f"Is that all of your {item_type}? y/n\n").lower()
                if final_question != 'n' and final_question != 'no':
                    break
                else:
                    # if there actually are more sources (n/no) then the item number needs to be reset
                    item_number -= 1
                    continue

            # Gathering the full cost of the source
            cost: float = float(input(f"How much £ from {name}?\n£"))

            # Here we calculate the split if the payment is split
            if is_source_shareable and is_shared_payment():
                # Using the shared dictionary to additionally have all the shared params collected separate in summary
                # TURN INTO 'SHARED' FUNCTION {
                split = calculate_shared_split(
                    cost,
                    earnings
                )
                # Adding the split costs to the name dictionary, along with total
                source_details['cost'] = split['oscar']
                source_details['split'] = split

                # Adding this source to the shared dict
                shared[name] = source_details
                # Here, I think that total should show all mine and manu's payments, plus all together
                shared['total']['oscar'] += split['oscar']
                shared['total']['manu'] += split['manu']
            # } CLOSE 'SHARED' FUNCTION

            else:
                source_details['cost'] = cost

            if has_payment_dates:
                date: int = int(input("Date of payment: ").lower()
                                .replace('st', '').replace('nd', '').replace('rd', '').replace('th', ''))
                source_details["date"] = date

            summary['total'] += source_details['cost']
            summary[name] = source_details

        if has_payment_dates: summary = order_payments_by_date(summary)
        if is_source_shareable: summary.update({'shared': order_payment_elements(shared)})

    print(f"{item_type} summary: {summary}")
    return summary


def order_payment_elements(payments):
    rearranged_payments = {}

    if payments.get('total', None):
        rearranged_payments['total'] = payments['total']
        payments.pop('total')

    for key, element in payments.items():
        if key != 'total':
            rearranged_payments[key] = {'cost': element['cost']}
            if element.get('date', None): rearranged_payments[key]['date'] = element['date']
            if element.get('split', None):
                rearranged_payments[key]['split'] = element['split']
                rearranged_payments[key]['total cost'] = element['total cost']

    return rearranged_payments


def order_payments_by_date(payments):
    total = payments.pop('total')

    rearranged_payments = order_payment_elements(payments)

    sorted_payments = dict(sorted(rearranged_payments.items(), key=lambda x: x[1].get('date', None)))

    ordered_payments = {'total': total}
    for key, element in sorted_payments.items():
        ordered_payments[key] = element

    return ordered_payments


def copy_over_items(summary1, summary2, item_type):
    summary2[item_type] = summary1[item_type].copy()
    return summary2


def rearrange_date(date):
    division = date.split("-")

    return f"{division[-1]}-{division[-2]}-{division[-3]}", int(division[-2])


def calculate_left_to_pay_value(allowance, direct_debits, flex):
    total = allowance

    for key, value in direct_debits.items():
        if key != 'total':
            total += value['cost']

    for key, value in flex.items():
        if key != 'total':
            total += value['cost']

    return round(total, 2)


def save_budget(test, calculation_type, **kwargs):
    today = str(dt.datetime.now())
    date, month_int = rearrange_date(today[:today.find(" ")])

    test_tag = '' if not test else '-Test'

    months = [
        'January',
        'February',
        'March',
        'April',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December',
    ]

    # If the budget is calculated before the 11th then its most likely re-calculating for the current month
    month_name = months[month_int -1] if int(date.split("-")[0]) < 11 else months[month_int]

    filename = f"{month_name}:{date}:{calculation_type.lower().capitalize()}{test_tag}"

    # for budget_name, budget in kwargs.items():
    with open(f"{filename}.json", "w") as budget_file:
        json.dump(kwargs, budget_file)

    print(f"\nSaved budget to {filename}")


# ====================================================================
# ======================== What Earnings for rent ====================
def calculate_required_earnings(shared_payments, personal_earnings, personal_spending, extras):
    net_shared_payments = round(sum(shared_payments.values()), 2)
    net_personal_spending = round(sum(personal_spending.values()), 2)
    net_extras = round(sum(extras.values()), 2)

    denominator = personal_earnings - (net_personal_spending + net_extras)

    net_earnings = round(net_shared_payments * (personal_earnings / denominator), 2)
    print(f"== EARNINGS ==\nnet earnings required: £{net_earnings}")
    print(f"personal earnings: £{personal_earnings}")
    partner_earnings = round(net_earnings - personal_earnings, 2)
    print(f"partner earnings: £{partner_earnings}\n")

    print(f"== SHARED ==\n{shared_payments}")
    print(f"net shared payments: £{net_shared_payments}")
    personal_shared_percent = round(net_shared_payments / net_earnings, 4)
    print(
        f"personally paying {round(personal_earnings * personal_shared_percent, 2)} ({personal_shared_percent * 100}%)")
    partner_shared_percent = round(net_shared_payments / net_earnings, 4)
    print(f"partner paying {round(partner_earnings * partner_shared_percent, 2)} ({partner_shared_percent * 100}%)\n")

    print(f"== SPENDING ==\n{personal_spending}")
    print(f"net personal spending: £{net_personal_spending}\n")

    print(f"== EXTRAS ==\n{extras}")
    print(f"net extras: £{net_extras}\n")


def calculate_required_earning_for_equal_salary(shared_payments, personal_spending, extras):
    net_shared_payments = round(sum(shared_payments.values()), 2)
    print(f"net shared payments: £{net_shared_payments}")

    net_personal_spending = round(sum(personal_spending.values()), 2)
    print(f"net personal spending: £{net_personal_spending}")

    net_extras = round(sum(extras.values()), 2)
    print(f"net extras: £{net_extras}")

    numerator = net_shared_payments + net_personal_spending + net_extras

    equal_earning = round(0.5 * numerator, 2)

    print(f"you both have to earn £{equal_earning} per month")


def calculate_remainder_given_earnings(personal_earning, partner_earning, shared_payments, personal_spending):
    print(f"personal earning: £{personal_earning}")
    print(f"partner earning: £{partner_earning}")
    net_earning = round(personal_earning + partner_earning, 2)
    print(f"\nnet earning: £{net_earning}\n")

    net_shared_payments = round(sum(shared_payments.values()), 2)
    print(f"net shared payments: £{net_shared_payments}")

    net_personal_spending = round(sum(personal_spending.values()), 2)
    print(f"net personal spending: £{net_personal_spending}")

    fraction = (net_shared_payments * personal_earning) / net_earning
    bracket = personal_spending + fraction

    remainder = round(personal_earning - bracket, 2)
    print(f"remainder: £{remainder}")


# ====================================================================
# ==================== No input Budget Calculator ====================
def calculate_total(parent_dict):
    total = 0
    for dict_ in parent_dict.values():
        total += dict_['cost']

    return round(total, 2)


def calculate_total_earnings(earnings):
    return sum(earnings.values())


def order_dict_by_payment_date(parent_dict):
    # if there's no "date" attribute we return the parent dict
    for _dict in parent_dict.values():
        if _dict.get("date", False):
            break
        else:
            return parent_dict

    dict_sorted_by_date = dict(sorted(parent_dict.items(), key=lambda x: x[1]['date']))
    return dict_sorted_by_date


def update_dict_with_shared_split(earnings, parent_dict):
    for _dict in parent_dict.values():
        if _dict.get("is_shared", False):
            _dict['payment split'] = calculate_shared_split(_dict['cost'], earnings)

    return parent_dict


def complete_dictionary(earnings, parent_dict):
    ordered_parent_dict_by_payment_date = order_dict_by_payment_date(parent_dict)

    ordered_dict_with_calculated_split = update_dict_with_shared_split(earnings, ordered_parent_dict_by_payment_date)

    ordered_dict_with_calculated_split['total'] = calculate_total(ordered_dict_with_calculated_split)

    return ordered_dict_with_calculated_split


def extract_shared_split(parent_dict):
    split = {'total': {'payments': [], 'oscar': 0, 'manu': 0}}

    for payment, details in parent_dict.items():
        if type(details) is dict:
            for key, element in details.items():
                if key == "payment split":
                    split['total']['oscar'] += element['oscar']
                    split['total']['manu'] += element['manu']
                    split['total']['payments'].append(payment)
                    split[payment] = element

    split['total']['together'] = split['total']['oscar'] + split['total']['manu']

    return split


def sum_totals(flex, direct_debits, separate_payments, target):
    total = 0
    if flex['total'].get(target, False):
        total += flex['total'][target]
    if direct_debits['total'].get(target, False):
        total += direct_debits['total'][target]
    if separate_payments['total'].get(target, False):
        total += separate_payments['total'][target]

    return total


def tally_shared_split(flex, direct_debits, separate_payments):
    shared = {'total': {'oscar': 0, 'manu': 0, 'together': 0}}

    flex_split = extract_shared_split(flex)
    shared['flex'] = flex_split

    direct_debits_split = extract_shared_split(direct_debits)
    shared['direct debits'] = direct_debits_split

    separate_payments_split = extract_shared_split(separate_payments)
    shared['separate debits'] = separate_payments_split

    shared['total']['oscar'] = sum_totals(flex_split, direct_debits_split, separate_payments_split, 'oscar')
    shared['total']['manu'] = sum_totals(flex_split, direct_debits_split, separate_payments_split, 'manu')
    shared['total']['together'] = sum_totals(flex_split, direct_debits_split, separate_payments_split, 'together')

    return shared


def split_remainder(remainder, allowance):
    if remainder < 0:
        print(f"""Bad News, you can"t afford this month.. 
        With all the outgoings minused from the net incomings you will be {remainder} in debt..""")
        savings = 0
        extra_expenses = None
        overdrawn = -remainder
        available = allowance + remainder
    elif remainder == 0:
        print(f"With your current budget you are scraping by with £0 for savings and for extra expenses..")
        savings = 0
        extra_expenses = 0
        overdrawn = 0
        available = allowance
    else:
        print(f"After all your outgoings, there is £{remainder} left")
        print(f"Between Extra Expenses and Savings how would you like to split it?")
        savings = float(input("Savings:\n£"))
        extra_expenses = remainder - savings
        overdrawn = 0
        print(f"Leaving £{extra_expenses} in Extra Expenses")

        available = round(allowance + extra_expenses, 2)

    return dict(savings=savings, extra_expenses=extra_expenses, overdrawn=overdrawn, available=available)


def static_calculate_budget(
        earnings, extra_sources, overdraft,
        init_flex, init_direct_debits, init_separate_payments,
        allowance=355.0
):
    earnings["total"] = calculate_total_earnings(earnings)

    extra_sources["total"] = calculate_total(extra_sources)

    flex = complete_dictionary(earnings, init_flex)
    direct_debits = complete_dictionary(earnings, init_direct_debits)

    left_to_pay_value = calculate_left_to_pay_value(allowance, direct_debits, flex)

    separate_payments = complete_dictionary(earnings, init_separate_payments)

    shared = tally_shared_split(flex=flex, direct_debits=direct_debits, separate_payments=separate_payments)

    budget = {
        "left to pay": left_to_pay_value,
        "allowance": allowance,
        "flex": flex,
        "direct debits": direct_debits,
        "separate payments": separate_payments,
        "total": left_to_pay_value + separate_payments['total']
    }

    # Summary
    break_down = {
        "oscar salary": earnings['oscar'],
        "manu salary": earnings['manu'],
        "combined salary": earnings['total'],
        "extra sources": extra_sources,
        "overdraft": overdraft,
        "NET IN": earnings['oscar'] + extra_sources['total'] + shared['total']['manu'],
        "NET OUT": left_to_pay_value + separate_payments['total'] + overdraft,
        "NET OUT SHARED": shared['total']['together'],
        "budget": budget,
    }

    oscar_out_actual = budget['total'] - shared['total']['manu']

    remainder = round(break_down['NET IN'] - break_down['NET OUT'], 2)

    result = split_remainder(remainder, allowance)
    key = {
        "oscar salary": "£ earned by oscar this month",
        "extra sources": "Extra £ brought in this month",
        "OSCAR NET IN": "oscar salary + extra sources + MANU OUT",
        "NET OUT": "left_to_pay_value + separate_payments['total'] + overdraft",
        "OSCAR ACTUAL OUT": "NET OUT - MANU OUT",
        "OSCAR OUT UNSHARED": "NET OUT - total shared",
        "OSCAR OUT SHARED": shared['total']['oscar'],
        "manu salary": earnings['manu'],
        "MANU OUT": shared['total']['manu'],
        "manu shared": shared['total']['manu'],
        "overdraft": overdraft,
        "=> budget": budget['total'],
        "   - flex": flex['total'],
        "   - direct debits": direct_debits['total'],
        "   - separate payments": separate_payments['total'],
        "   - allowance": allowance,
        "=> extra expenses": result['extra_expenses'],
        "=> savings": result['savings'],
        "overdrawn": result['overdrawn'],
        "available": result['available'],
        "manu remainder": earnings['manu'] - shared['total']['manu']
    }
    summary = {
        "oscar salary": earnings['oscar'],
        "extra sources": extra_sources['total'],
        "OSCAR NET IN": round(earnings['oscar'] + extra_sources['total'] + shared['total']['manu'], 2),
        "NET OUT": left_to_pay_value + separate_payments['total'] + overdraft,
        "SHARED OUT TOTAL": shared['total']['together'],
        "OSCAR ACTUAL OUT": round(oscar_out_actual, 2),
        "OSCAR OUT UNSHARED": round(oscar_out_actual - shared['total']['oscar'], 2),
        "OSCAR OUT SHARED": shared['total']['oscar'],
        "oscar shared earnings %": round(shared['total']['oscar'] / earnings['oscar'], 4),
        "manu salary": earnings['manu'],
        "MANU OUT": shared['total']['manu'],
        "manu shared": shared['total']['manu'],
        "manu shared earnings %": round(shared['total']['manu'] / earnings['manu'], 4),
        "overdraft": overdraft,
        "=> budget": budget['total'],
        "   - flex": flex['total'],
        "   - direct debits": direct_debits['total'],
        "   - separate payments": separate_payments['total'],
        "   - allowance": allowance,
        "=> extra expenses": result['extra_expenses'],
        "=> savings": result['savings'],
        "overdrawn": result['overdrawn'],
        "available": result['available'],
        "manu remainder": earnings['manu'] - shared['total']['manu']
    }

    summary_check = {
        "OSCAR NET IN": "oscar salary + extra sources + manu's shared total",
        "NET OUT": "flex + direct debit + separate_payments + overdraft",
        "SHARED OUT TOTAL": "oscar shared out + manu shared out",
        "OSCAR ACTUAL OUT": "oscar personal (flex, direct debit) + oscar shared out",
        "OSCAR OUT UNSHARED": "oscar total - oscar shared",
        "OSCAR OUT SHARED": "oscar shared",
        "oscar shared earnings %": "percent of oscars earnings spent on sh",
        "manu salary": earnings['manu'],
        "MANU OUT": shared['total']['manu'],
        "manu shared": shared['total']['manu'],
        "manu shared earnings %": round(shared['total']['manu'] / earnings['manu'], 4),
        "overdraft": overdraft,
        "=> budget": budget['total'],
        "   - flex": flex['total'],
        "   - direct debits": direct_debits['total'],
        "   - separate payments": separate_payments['total'],
        "   - allowance": allowance,
        "=> extra expenses": result['extra_expenses'],
        "=> savings": result['savings'],
        "overdrawn": result['overdrawn'],
        "available": result['available'],
        "manu remainder": earnings['manu'] - shared['total']['manu']
    }

    save_budget(False, 'static_budget', shared=shared, break_down=break_down, summary=summary)
