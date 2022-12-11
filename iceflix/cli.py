"""Submodule containing the CLI command handlers."""

import logging
import sys
import os

from iceflix.authenticator import AuthenticatorApp


LOG_FORMAT = '%(asctime)s - %(levelname)-7s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'


def setup_logging():
    """Configure the logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
    )


def authentication_service():
    """Handles the `authenticationservice` CLI command."""
    setup_logging()
    logging.info("Authentication service")
    authenticatorapp = AuthenticatorApp()
    try:
        sys.exit(authenticatorapp.main(sys.argv))
    except:
        logging.info("Error durante la ejecución. Cerrando el authenticator.")
        os._exit(1)
    return 0
    
authentication_service()