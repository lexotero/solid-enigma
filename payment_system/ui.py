from __future__ import annotations

from typing import Callable, Final, TypedDict

from rich import print
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table

from payment_system.models import Invoice, Payment


class ErrorProcessingAction(Exception):
    """
    Exception class for all errors raised by the UI
    """


class Action(TypedDict):
    description: str
    method: Callable


class UI:
    def __init__(self) -> None:
        self.invoices: list[Invoice] = []
        self.payments: list[Payment] = []
        self.actions: Final[dict[str, Action]] = {
            "0": {"description": "Create a new invoice", "method": self.create_invoice},
            "1": {"description": "Process a payment", "method": self.process_payment},
            "2": {"description": "Show invoices", "method": self.show_invoices},
            "3": {"description": "Show payments", "method": self.show_payments},
        }

    def run(self) -> None:
        try:
            self._run()
        except KeyboardInterrupt:
            print("You've exited the system. Thanks for using it!")

    def _run(self) -> None:
        while True:
            self._print_actions_table()
            action_id = Prompt.ask(
                "What do you want to do? Select an action ID",
                choices=[str(k) for k in self.actions.keys()],
            )
            try:
                action = self.actions[action_id]
                action["method"]()
            except ErrorProcessingAction as error:
                print(
                    "We've encountered an error while processing your action. "
                    f'Please, try gain! Error: "{error}"'
                )

    def create_invoice(self) -> None:
        amount: float = FloatPrompt.ask("Invoice amount")
        invoice = Invoice.create(amount=amount)
        print(f"Created invoice {invoice}")
        self.invoices.append(invoice)

    def process_payment(self) -> None:
        if not self.invoices:
            raise ErrorProcessingAction("There are no invoices to process payments!")
        payee = Prompt.ask("Payee name")
        transactions = []
        finished = False
        while not finished:
            self._print_invoices_table()
            invoice_index = IntPrompt.ask(
                "For what invoice do you want to process a payment (index)?"
            )
            amount: float = FloatPrompt.ask(
                "How much is being paid towards that invoice?"
            )
            invoice = self.invoices[invoice_index]
            transactions.append((invoice, amount))
            finished = Confirm.ask("Is that all?")
        payment = Payment.create(payee=payee, transactions=transactions)
        print("New payment created!")
        print(payment)
        confirmed = Confirm.ask("Are you sure you want to execute this payment?")
        if not confirmed:
            print("Payment processing cancelled!")
            return
        payment.execute()
        self.payments.append(payment)

    def show_invoices(self) -> None:
        self._print_invoices_table()

    def show_payments(self) -> None:
        self._print_payments_table()

    def _print_actions_table(self) -> None:
        table = Table(title="Actions")
        table.add_column("Action ID", justify="right", style="cyan")
        table.add_column("Description", style="magenta")
        for action_id, action in self.actions.items():
            table.add_row(action_id, action["description"])
        print(table)

    def _print_invoices_table(self) -> None:
        table = Table(title="Invoices")
        table.add_column("Invoice Index", justify="right", style="cyan")
        table.add_column("Details", style="magenta")
        for index, invoice in enumerate(self.invoices):
            table.add_row(str(index), str(invoice))
        print(table)

    def _print_payments_table(self) -> None:
        table = Table(title="Payments")
        table.add_column("Payment Index", justify="right", style="cyan")
        table.add_column("Details", style="magenta")
        for index, payment in enumerate(self.payments):
            table.add_row(str(index), str(payment))
        print(table)
