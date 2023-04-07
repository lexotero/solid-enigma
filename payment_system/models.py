from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar


@dataclass
class Timestamped:
    # We exclude this argument from the init method because it has a default
    # that doesn't need to change and otherwise the order of the fields when
    # inheriting causes an exception.
    timestamp: datetime = field(default_factory=datetime.utcnow, init=False)


InvoiceType = TypeVar("InvoiceType", bound="Invoice")


@dataclass
class Invoice(Timestamped):
    amount: float
    outstanding: float

    @classmethod
    def create(cls, amount: float) -> InvoiceType:
        return cls(
            amount=amount,
            outstanding=amount,
        )

    @property
    def is_paid(self) -> bool:
        if self.outstanding > 0:
            return False
        return True

    def validate_payment_amount(self, payment_amount: float) -> None:
        if self.is_paid:
            # This could be a custom exception, e.g. InvalidPayment()
            # or something like that
            raise Exception(
                f"The invoice {id(self)} is fully paid already"
            )
        if payment_amount > self.outstanding:
            # We could allow a request to pay more and simply
            # return the difference, but then the caller would have
            # to account for that, so instead in this quick implementation
            # I'm going for considering this case an error.
            raise Exception(
                f"The invoice {id(self)} has {self.outstanding} balance. That "
                "is the maximum you can pay."
            )

    def pay_in(self, payment_amount: float) -> float:
        self.validate_payment_amount(payment_amount=payment_amount)
        self.outstanding -= payment_amount
        # Implementation decision, could be helpful for the caller to return
        # the outstanding amount.
        return self.outstanding


TransactionType = TypeVar("TransactionType", bound="Transaction")


@dataclass
class Transaction(Timestamped):
    amount: float
    invoice: InvoiceType


PaymentType = TypeVar("PaymentType", bound="Payment")


@dataclass
class Payment(Timestamped):
    payee: str
    transactions: list[TransactionType]
    # TODO: We probably want a boolean flag and perhaps
    # a timestamp set when the payment is executed.

    @classmethod
    def create(cls, payee: str, transactions: list[tuple[InvoiceType, float]]) -> PaymentType:
        instance = cls(
            payee=payee,
            # TODO: We should probably guard against payments with no transactions,
            # but let's keep it simple for now.
            transactions=[],
        )
        for (invoice, amount) in transactions:
            t = Transaction(
                amount=amount,
                invoice=invoice,
            )
            instance.transactions.append(t)
            # TODO: There is not much error handling here to avoid creating
            # objects in invalid states.
        # Note we do not execute the transactions, we simply create them.
        # Separating execution could allow us to do verifications before
        # actually paying the invoice (?)
        return instance

    def execute(self) -> None:
        # Implementation decision: double the iterations but
        # we make sure we only pay if all the transactions
        # can be executed.
        for t in self.transactions:
            t.invoice.validate_payment_amount(payment_amount=t.amount)
        for t in self.transactions:
            t.invoice.pay_in(payment_amount=t.amount)
            # TODO: mark someone the payment as executed.
