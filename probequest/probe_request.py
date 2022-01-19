"""
A Wi-Fi probe request.
"""

from time import localtime, strftime
from netaddr import EUI, NotRegisteredError
import sys
import os

def getdir():
    directory = open("/usr/local/bin/probequestdata/config/installdirectory.dnt", "r").read().strip("\n")
    return directory

def getwatchlist():
    watchlist = []
    watchlistparse = ([x.strip() for x in open(f"{getdir()}/config/watchlist.conf", "r").readlines() if not x.startswith("#") and not ""])
    for entry in watchlistparse:
        if len(entry) >= 17:
            watchlist.append(entry)

    return watchlist

class colors:
    LIGHTPURPLE = '\033[1;35m'
    BROWN = "\033[0;33m"
    PURPLE = "\033[1;34m"
    LIGHTGREEN = "\033[1;32m"
    CYAN = "\033[0;36m"
    LIGHTRED = "\033[1;31m"
    LIGHTCYAN = "\033[1;36m"
    LIGHTWHITE = "\033[1;37m"
    LIGHTYELLOW = "\x1b[93m"
    PINK = "\x1b[95m"
    END = "\033[0m"

class ProbeRequest:
    """
    Probe request class.
    """

    def __init__(self, timestamp, s_mac, essid, signal, frequency):
        self.timestamp = timestamp
        self.s_mac = str(s_mac)
        self.essid = str(essid)
        self.signal = str(signal)
        self.frequency = str(frequency)

        self._s_mac_oui = None

    def __str__(self):
        timestamp = strftime(
                "%Y-%m-%d %H:%M:%S",
                localtime(self.timestamp)
                )
        s_mac = self.s_mac
        s_mac_oui = self.s_mac_oui
        essid = self.essid
        signal = self.signal
        frequency = self.frequency

        database = open(f"{getdir()}/database/masswatchlist.data", "a+")
        database.write(f"{timestamp} - {s_mac} ({s_mac_oui}) -> {essid} <-> ([{signal}]dBm) > (FREQ[{frequency}mHz])\n"); database.close()

        wlist = getwatchlist()
        for data in wlist:
            data = data.split(); w_mac = data[0].strip().lower()
            if s_mac.lower() == w_mac:
                try:
                    os.mkdir(f"{getdir()}/database/watchlist/{s_mac.upper()}")
                except OSError:
                    pass
                else:
                    print(f"\n{colors.LIGHTRED}[CRITICAL-ERROR!] {colors.LIGHTWHITE}Unable to create directory: {getdir()/database/watchlist/{s_mac.upper()}}\n")

                database = open(f"{getdir()}/database/watchlist/{s_mac.upper()}/watchlist.data", "a+")
                database.write(f"{timestamp} - {s_mac} ({s_mac_oui}) -> {essid} <-> ([{signal}]dBm) > (FREQ[{frequency}mHz])\n"); database.close()


                return f"{colors.LIGHTRED}[!WATCHLIST-HIT!{colors.LIGHTPURPLE}{colors.LIGHTWHITE}({colors.LIGHTPURPLE}{' '.join(data[1:])}{colors.LIGHTWHITE}){colors.LIGHTRED}]{colors.LIGHTWHITE} - {colors.LIGHTGREEN}[{timestamp}] {colors.LIGHTWHITE}- {colors.LIGHTCYAN}{s_mac} {colors.LIGHTWHITE}({s_mac_oui}) {colors.LIGHTWHITE}-> {colors.LIGHTCYAN}{essid} {colors.LIGHTWHITE}<=>{colors.LIGHTRED} ([{signal}]dBm){colors.END} {colors.LIGHTWHITE}> (FREQ[{colors.LIGHTYELLOW}{frequency}mHz{colors.LIGHTWHITE}])"

        return f"{colors.LIGHTGREEN}[{timestamp}] {colors.LIGHTWHITE}- {colors.LIGHTCYAN}{s_mac} {colors.LIGHTWHITE}({s_mac_oui}) {colors.LIGHTWHITE}-> {colors.LIGHTCYAN}{essid} {colors.LIGHTWHITE}<=>{colors.LIGHTRED} ([{signal}]dBm){colors.END} {colors.LIGHTWHITE}> (FREQ[{colors.LIGHTYELLOW}{frequency}mHz{colors.LIGHTWHITE}])"

    @property
    def s_mac_oui(self):
        """
        OUI of the station's MAC address as a string.

        The value is cached once computed.
        """

        # pylint: disable=no-member

        if self._s_mac_oui is None:
            try:
                self._s_mac_oui = EUI(self.s_mac).oui.registration().org
            except NotRegisteredError:
                self._s_mac_oui = "Unknown OUI"

        return self._s_mac_oui
