import sys

from payment_system.ui import UI


def main() -> int:
    # Run a simple CLI-based user interface to create invoices and make
    # payments.
    # Note that there is no persistency layer, so invoices and payments
    # created will not persist when the process terminates.
    system_ui = UI()
    system_ui.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
