"""
=========================================================
MetaTrader 5 Connection
=========================================================

Responsible only for connecting to and disconnecting from
the MetaTrader 5 terminal.

Portfolio project
=========================================================
"""

import MetaTrader5 as mt5

from config import (
    MT5_PATH,
    MT5_TIMEOUT,
    MT5_PORTABLE,
)


# =========================================================
# Connect
# =========================================================

def connect():
    """
    Initialize MT5 and verify an account is logged in.

    Returns
    -------
    AccountInfo
        MT5 account information.

    Raises
    ------
    RuntimeError
        If MT5 cannot be initialized or no account is logged in.
    """

    connected = mt5.initialize(
        path=MT5_PATH,
        timeout=MT5_TIMEOUT,
        portable=MT5_PORTABLE,
    )

    if not connected:
        raise RuntimeError(
            f"MT5 initialization failed: {mt5.last_error()}"
        )

    account = mt5.account_info()

    if account is None:
        mt5.shutdown()
        raise RuntimeError(
            f"No MT5 account is logged in: {mt5.last_error()}"
        )

    print("=" * 60)
    print("MetaTrader 5 Connected")
    print("=" * 60)
    print(f"Login   : {account.login}")
    print(f"Server  : {account.server}")
    print(f"Company : {account.company}")
    print("=" * 60)

    return account


# =========================================================
# Disconnect
# =========================================================

def disconnect():
    """Close the MT5 connection."""
    mt5.shutdown()


# =========================================================
# Connection Status
# =========================================================

def is_connected() -> bool:
    """Return True if MT5 is connected."""
    return mt5.account_info() is not None