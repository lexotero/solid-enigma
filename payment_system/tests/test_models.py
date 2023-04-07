from unittest import TestCase

from payment_system.models import Invoice, Payment, Transaction


class TestInvoice(TestCase):
    def test_create_with_amount_check_outstanding(self):
        invoice = Invoice.create(amount=100.0)
        self.assertEqual(invoice.outstanding, 100.0)

    def test_create_with_amount_check_timestamp(self):
        invoice = Invoice.create(amount=100.0)
        # We cannot use freezegun directly here because
        # of how we use default_factory to set the
        # timestamp. We would need some hacky solution so
        # for now we simply make sure we get a timestamp
        self.assertIsNotNone(invoice.timestamp)

    def test_pay_in_with_payment_amount_less_than_outstanding_check_outstanding(self):
        invoice = Invoice.create(amount=100.0)
        output = invoice.pay_in(payment_amount=10.0)
        self.assertEqual(output, 90.0)
        self.assertEqual(invoice.outstanding, 90.0)

    def test_pay_in_with_payment_amount_equal_to_outstanding_check_outstanding(self):
        invoice = Invoice.create(amount=100.0)
        output = invoice.pay_in(payment_amount=100.0)
        self.assertEqual(output, 0.0)
        self.assertEqual(invoice.outstanding, 0.0)

    def test_pay_in_with_payment_amount_more_than_outstanding_check_exception(self):
        invoice = Invoice.create(amount=100.0)
        with self.assertRaises(Exception) as cm_error:
            invoice.pay_in(payment_amount=900.0)
        # A custom exception would be better here so we don't need
        # to test for the exception message
        self.assertIn("maximum you can pay", str(cm_error.exception))

    def test_pay_in_with_invoice_already_paid_check_exception(self):
        invoice = Invoice.create(amount=100.0)
        invoice.pay_in(payment_amount=100.0)
        with self.assertRaises(Exception) as cm_error:
            invoice.pay_in(payment_amount=50.0)
        # A custom exception would be better here so we don't need
        # to test for the exception message
        self.assertIn("fully paid already", str(cm_error.exception))


class TestPayment(TestCase):
    def test_create_with_payee_and_single_transaction_check_payee(self):
        invoice = Invoice.create(amount=100.0)
        payment = Payment.create(payee="John Doe", transactions=[(invoice, 100.0)])
        self.assertEqual(payment.payee, "John Doe")

    def test_create_with_payee_and_single_transaction_check_timestamp(self):
        invoice = Invoice.create(amount=100.0)
        payment = Payment.create(payee="John Doe", transactions=[(invoice, 100.0)])
        # We cannot use freezegun directly here because
        # of how we use default_factory to set the
        # timestamp. We would need some hacky solution so
        # for now we simply make sure we get a timestamp
        self.assertIsNotNone(payment.timestamp)

    def test_create_with_payee_and_single_transaction_check_transactions(self):
        invoice = Invoice.create(amount=100.0)
        payment = Payment.create(payee="John Doe", transactions=[(invoice, 100.0)])
        self.assertListEqual(
            payment.transactions,
            [
                Transaction(
                    amount=100.0,
                    invoice=invoice,
                )
            ],
        )

    def test_create_with_payee_and_multiple_transaction_check_transactions(self):
        invoice = Invoice.create(amount=100.0)
        payment = Payment.create(
            payee="John Doe",
            transactions=[
                (invoice, 10.0),
                (invoice, 90.0),
            ],
        )
        self.assertListEqual(
            payment.transactions,
            [
                Transaction(
                    amount=10.0,
                    invoice=invoice,
                ),
                Transaction(
                    amount=90.0,
                    invoice=invoice,
                ),
            ],
        )

    def test_create_with_payee_and_no_transactions_check_empty_transactions(self):
        # In the future we probably want this to case an error
        # but for now we lock in the behaviour.
        payment = Payment.create(payee="John Doe", transactions=[])
        self.assertEqual(payment.transactions, [])

    def test_execute_with_all_valid_transactions_check_invoices(self):
        invoice = Invoice.create(amount=100.0)
        payment = Payment.create(
            payee="John Doe",
            transactions=[
                (invoice, 10.0),
                (invoice, 30.0),
                (invoice, 40.0),
            ],
        )
        payment.execute()
        # The transaction amounts should cover 80 out of the
        # 100 of the invoice.
        self.assertEqual(invoice.outstanding, 20.0)

    def test_execute_with_invalid_transactions_check_exception(self):
        invoice = Invoice.create(amount=100.0)
        payment = Payment.create(
            payee="John Doe",
            transactions=[
                (invoice, 10.0),
                (invoice, 30.0),
                # This transaction is invalid
                (invoice, 940.0),
            ],
        )
        with self.assertRaises(Exception):
            payment.execute()

    def test_execute_with_invalid_transactions_check_transactions_not_executed(self):
        invoice = Invoice.create(amount=100.0)
        payment = Payment.create(
            payee="John Doe",
            transactions=[
                (invoice, 10.0),
                (invoice, 30.0),
                # This transaction is invalid
                (invoice, 940.0),
            ],
        )
        with self.assertRaises(Exception):
            payment.execute()
        # No payments were made
        self.assertEqual(invoice.outstanding, invoice.amount)


class TestInteractions(TestCase):
    def setUp(self) -> None:
        self.invoices = [
            Invoice.create(amount=100),
            Invoice.create(amount=999),
            Invoice.create(amount=5553),
        ]

    def test_single_payment_to_multiple_invoices_check_outstanding_amounts(self):
        payment = Payment.create(
            payee="John Doe",
            transactions=[
                (self.invoices[0], 50),
                (self.invoices[1], 66),
                (self.invoices[2], 999),
            ],
        )
        payment.execute()
        self.assertListEqual(
            [invoice.outstanding for invoice in self.invoices], [50, 933, 4554]
        )

    def test_continuos_payments_to_multiple_invoices_check_outstanding_amounts(self):
        first_payment = Payment.create(
            payee="John Doe",
            transactions=[
                (self.invoices[0], 100),
                (self.invoices[1], 66),
                (self.invoices[2], 999),
            ],
        )
        first_payment.execute()
        second_payment = Payment.create(
            payee="John Doe",
            transactions=[
                (self.invoices[1], 933),
                (self.invoices[2], 4554),
            ],
        )
        second_payment.execute()
        self.assertListEqual(
            [invoice.outstanding for invoice in self.invoices], [0, 0, 0]
        )
