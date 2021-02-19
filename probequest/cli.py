"""
CLI module.
"""

import logging
from argparse import ArgumentParser, FileType
from logging.handlers import MemoryHandler
from os import geteuid
from sys import exit as sys_exit
from time import sleep

from . import __version__ as VERSION
from .config import Config, Mode
from .ui.pnl import PNLViewer
from .ui.raw import RawProbeRequestViewer

# Used to specify the capacity of the memory handler which will store the logs
# in memory until the argument parser is called to know whether they need to be
# flushed to the console (see "--debug" option) or not.
MEMORY_LOGGER_CAPACITY = 50


def get_arg_parser():
    """
    Returns the argument parser.
    """

    arg_parser = ArgumentParser(
        description="Toolkit for Playing with Wi-Fi Probe Requests",
    )
    arg_parser.add_argument(
        "interface",
        help="wireless interface to use (must be in monitor mode)",
    )
    arg_parser.add_argument(
        "--debug", action="store_true",
        dest="debug",
        help="debug mode",
    )
    arg_parser.add_argument(
        "--fake", action="store_true",
        dest="fake",
        help="display only fake ESSIDs",
    )
    arg_parser.add_argument(
        "--ignore-case", action="store_true",
        dest="ignore_case",
        help="ignore case distinctions in the regex pattern (default: false)",
    )
    arg_parser.add_argument(
        "--mode",
        type=Mode, choices=Mode.__members__.values(),
        dest="mode",
        help="set the mode to use",
    )
    arg_parser.add_argument(
        "-o", "--output",
        type=FileType("a"),
        dest="output_file",
        help="output file to save the captured data (CSV format)",
    )
    arg_parser.add_argument("--version", action="version", version=VERSION)
    arg_parser.set_defaults(debug=False)
    arg_parser.set_defaults(fake=False)
    arg_parser.set_defaults(ignore_case=False)
    arg_parser.set_defaults(mode=Mode.RAW)

    essid_arguments = arg_parser.add_mutually_exclusive_group()
    essid_arguments.add_argument(
        "-e", "--essid",
        nargs="+",
        metavar="ESSID",
        dest="essid_filters",
        help="ESSID of the APs to filter (space-separated list)",
    )
    essid_arguments.add_argument(
        "-r", "--regex",
        metavar="REGEX",
        dest="essid_regex",
        help="regex to filter the ESSIDs",
    )

    station_arguments = arg_parser.add_mutually_exclusive_group()
    station_arguments.add_argument(
        "--exclude",
        nargs="+",
        metavar="STATION",
        dest="mac_exclusions",
        help="MAC addresses of the stations to exclude (space-separated list)",
    )
    station_arguments.add_argument(
        "-s", "--station",
        nargs="+",
        metavar="STATION",
        dest="mac_filters",
        help="MAC addresses of the stations to filter (space-separated list)",
    )

    return arg_parser


def set_up_root_logger(level=logging.DEBUG):
    """
    Sets up the root logger.

    Returns a tuple containing the root logger, the memory handler and the
    console handler.
    """

    root_logger = logging.getLogger("")
    root_logger.setLevel(level)

    console = logging.StreamHandler()

    console_formatter = \
        logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(console_formatter)

    memory_handler = MemoryHandler(MEMORY_LOGGER_CAPACITY)
    root_logger.addHandler(memory_handler)

    return (root_logger, memory_handler, console)


def main():
    """
    Entry point of the command-line tool.
    """

    # pylint: disable=too-many-statements

    root_logger, memory_handler, console = set_up_root_logger()

    logger = logging.getLogger(__name__)

    logger.info("Program started")

    # -------------------------------------------------- #
    # CLI configuration
    # -------------------------------------------------- #
    logger.debug("Creating configuration object")
    config = Config()

    # -------------------------------------------------- #
    # Parsing arguments
    # -------------------------------------------------- #
    logger.debug("Parsing arguments")
    get_arg_parser().parse_args(namespace=config)

    # -------------------------------------------------- #
    # Debug mode
    # -------------------------------------------------- #
    # If the "--debug" option is present, flush the log buffer to the console,
    # remove the memory handler from the root logger and add the console
    # handler directly to the root logger.
    if config.debug:
        logger.debug("Setting the console as target of the memory handler")
        memory_handler.setTarget(console)

        logger.debug("Removing the memory handler from the root logger")
        # The buffer is flushed to the console at close time.
        memory_handler.close()
        root_logger.removeHandler(memory_handler)

        root_logger.addHandler(console)
        logger.debug("Console handler added to the root logger")
    # If the "--debug" option is absent (default), close the memory handler
    # without flushing anything to the console.
    else:
        memory_handler.flushOnClose = False
        memory_handler.close()
        logger.debug("Memory handler closed")

    # -------------------------------------------------- #
    # Checking privileges
    # -------------------------------------------------- #
    if not geteuid() == 0:
        logger.critical("User needs to be root to sniff the traffic")
        sys_exit("[!] You must be root")

    # -------------------------------------------------- #
    # Mode selection
    # -------------------------------------------------- #
    try:
        # Default mode.
        if config.mode == Mode.RAW:
            logger.info("Raw mode selected")

            print("[*] Start sniffing probe requests...")

            logger.debug("Configuring the raw viewer")
            viewer = RawProbeRequestViewer(config)

            logger.info("Starting the raw viewer")
            viewer.start()

            while True:
                sleep(100)
        elif config.mode == Mode.PNL:
            logger.info("PNL mode selected")

            logger.debug("Configuring the PNL viewer")
            viewer = PNLViewer(config)

            logger.info("Starting the PNL viewer")
            viewer.main()
        else:
            logger.critical("Invalid mode: %s", config.mode)
            sys_exit("[x] Invalid mode")
    except OSError as err:
        logger.debug("Stopping the viewer")
        viewer.stop()

        logger.critical(err, exc_info=True)
        sys_exit(
            "[!] Interface {interface} doesn't exist".format(
                interface=config.interface
            )
        )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        logger.info("Stopping the viewer")
        print("[*] Stopping the threads...")
        viewer.stop()
    finally:
        print("[*] Bye!")

        if config.output_file is not None:
            logger.debug("Closing output file")
            config.output_file.close()

        logger.info("Program ended")
