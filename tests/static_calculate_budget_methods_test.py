import unittest

from calulate_budget_methods import order_dict_by_payment_date, calculate_total, calculate_total_earnings, \
    calculate_shared_split, update_dict_with_shared_split, complete_dictionary, calculate_left_to_pay_value


class MyTestCase(unittest.TestCase):
    def test_calculate_total_earnings(self):
        earnings = {"oscar": 1889.21, "manu": 820}
        expected_total = 1889.21 + 820  # 2709.21

        calculated_total = calculate_total_earnings(earnings)

        self.assertEqual(calculated_total, expected_total)

    def test_calculate_total(self):
        parent_dict = {
            "ee": {"cost": 10, "date": 4},
            "boulder brighton": {"cost": 44, "date": 1},
            "spotify": {"cost": 17, "date": 2}
        }
        expected_total = 10 + 44 + 17
        calculated_total = calculate_total(parent_dict)

        self.assertEqual(calculated_total, expected_total)

    def test_order_payments_by_date(self):
        payments = {
            "ee": {"cost": 10, "date": 4},
            "boulder brighton": {"cost": 44, "date": 1},
            "spotify": {"cost": 17, "date": 2}
        }
        ordered_payments = {
            "boulder brighton": {"cost": 44, "date": 1},
            "spotify": {"cost": 17, "date": 2},
            "ee": {"cost": 10, "date": 4},
        }

        funct_ordered_payments = order_dict_by_payment_date(payments)

        self.assertEqual(funct_ordered_payments, ordered_payments)

    def test_calculate_shared_split(self):
        earnings = {"oscar": 1889.21, "manu": 820, "total": 2709.21}
        cost = 478

        expected_split = {
            'oscar': 333.32,
            'manu': 144.68,
            'percent': f'{17.64}%',
            'together': 478
        }

        calculated_split = calculate_shared_split(cost=cost, earnings=earnings)

        self.assertEqual(expected_split, calculated_split)

    def test_update_dict_with_shared_split(self):
        earnings = {"oscar": 1889.21, "manu": 820, "total": 2709.21}
        payments = {
            "elisa nursery": {"cost": 478, "is_shared": True},
            "boulder brighton x10 pass": {"cost": 90},
        }

        expected_payments_with_split = {
            "elisa nursery": {
                "cost": 478, "is_shared": True, 'payment split': {
                    'oscar': 333.32,
                    'manu': 144.68,
                    'percent': f'{17.64}%',
                    'together': 478
                }
            },
            "boulder brighton x10 pass": {"cost": 90},
        }

        result_payments_with_split = update_dict_with_shared_split(earnings=earnings, parent_dict=payments)

        self.assertEqual(result_payments_with_split, expected_payments_with_split)

    def test_complete_dictionary_with_dates_no_split(self):
        earnings = {"oscar": 1889.21, "manu": 820, "total": 2709.21}
        payment = {
            "the gym": {"cost": 24.99, "date": 7},
            "spotify": {"cost": 17.99, "date": 29},
            "google storage": {"cost": 1.59, "date": 5},
            "ee": {"cost": 10.0, "date": 2},
        }

        expected_complete_dictionary = {
            "ee": {"cost": 10.0, "date": 2},
            "google storage": {"cost": 1.59, "date": 5},
            "the gym": {"cost": 24.99, "date": 7},
            "spotify": {"cost": 17.99, "date": 29},
            "total": round(10.0 + 1.59 + 24.99 + 17.99, 2)
        }

        result_complete_dictionary = complete_dictionary(earnings=earnings, parent_dict=payment)

        self.assertEqual(expected_complete_dictionary, result_complete_dictionary)

    def test_complete_dictionary_with_dates_with_split(self):
        earnings = {"oscar": 1889.21, "manu": 820, "total": 2709.21}
        direct_debits = {
            "the gym": {"cost": 24.99, "date": 7},
            "spotify": {"cost": 17.99, "date": 29},
            "google storage": {"cost": 1.59, "date": 5},
            "mum rent": {"cost": 700, "date": 29, "is_shared": True},
            "ee": {"cost": 10.0, "date": 2},
        }

        expected_complete_dictionary = {
            "ee": {"cost": 10.0, "date": 2},
            "google storage": {"cost": 1.59, "date": 5},
            "the gym": {"cost": 24.99, "date": 7},
            "spotify": {"cost": 17.99, "date": 29},
            "mum rent": {"cost": 700, "date": 29, "is_shared": True, 'payment split': {
                    'oscar': 488.13,
                    'manu': 211.87,
                    'percent': f'{25.84}%',
                    'together': 700
                }},
            'total': round(10.0 + 1.59 + 24.99 + 17.99 + 700, 2)
        }

        result_complete_dictionary = complete_dictionary(earnings=earnings, parent_dict=direct_debits)

        self.assertEqual(result_complete_dictionary, expected_complete_dictionary)

    def test_complete_dictionary_without_dates_no_split(self):
        earnings = {"oscar": 1889.21, "manu": 820, "total": 2709.21}
        flex = {
            "manu's phone": {"cost": 58},
            "h&m elisa": {"cost": 23, "is_shared": True},
            "manu lingerie": {"cost": 21.91},
            "pride": {"cost": 19},
            "petrol": {"cost": 18.80},
            "manu's dublin flights": {"cost": 15}
        }

        expected_complete_dictionary = {
            "manu's phone": {"cost": 58},
            "h&m elisa": {"cost": 23, "is_shared": True, 'payment split': {
                    'oscar': 16.04,
                    'manu': 6.96,
                    'percent': f'{0.85}%',
                    'together': 23
                }},
            "manu lingerie": {"cost": 21.91},
            "pride": {"cost": 19},
            "petrol": {"cost": 18.80},
            "manu's dublin flights": {"cost": 15},
            "total": round(58 + 23 + 21.91 + 19 + 18.8 + 15, 2)
        }

        result_complete_dictionary = complete_dictionary(earnings=earnings, parent_dict=flex)

        self.assertEqual(result_complete_dictionary, expected_complete_dictionary)

    def test_calculate_left_to_pay_value(self):
        flex = {
            "manu's phone": {"cost": 58},
            "h&m elisa": {"cost": 23, "is_shared": True, 'payment split': {
                    'oscar': 16.04,
                    'manu': 6.96,
                    'percent': f'{0.85}%',
                    'together': 23
                }},
            "manu lingerie": {"cost": 21.91},
            "pride": {"cost": 19},
            "petrol": {"cost": 18.80},
            "manu's dublin flights": {"cost": 15},
            "total": round(58 + 23 + 21.91 + 19 + 18.8 + 15, 2)
        }
        direct_debits = {
            "ee": {"cost": 10.0, "date": 2},
            "google storage": {"cost": 1.59, "date": 5},
            "the gym": {"cost": 24.99, "date": 7},
            "spotify": {"cost": 17.99, "date": 29},
            "mum rent": {"cost": 700, "date": 29, "is_shared": True, 'payment split': {
                    'oscar': 488.13,
                    'manu': 211.87,
                    'percent': f'{25.84}%',
                    'together': 700
                }},
            'total': round(10.0 + 1.59 + 24.99 + 17.99 + 700, 2)
        }
        allowance = 350

        expected_left_to_pay_value = round(allowance + direct_debits['total'] + flex['total'], 2)

        result_left_to_pay_value = calculate_left_to_pay_value(
            allowance=allowance,
            direct_debits=direct_debits,
            flex=flex
        )

        self.assertEqual(result_left_to_pay_value, expected_left_to_pay_value)

if __name__ == '__main__':
    unittest.main()
