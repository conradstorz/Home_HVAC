"""A self contained and systemd service enabled package for monitoring temperatures"""
__version__ = "0.1"

from humidity_and_temps_recorder import main

"""Wrapper around temperature monitor program."""
main()
