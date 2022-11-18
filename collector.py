"""Simple compute-node load collector."""
import os
import sys
import time
import numpy as np
import argparse as ag
from fabric import Connection
import matplotlib.pyplot as plt
import mpld3


class LoadCollector(object):
    """Load collector."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.load = {}
        self.hosts = [
            "geva01.chem.lsa.umich.edu",
            "geva02.chem.lsa.umich.edu",
            "geva03.chem.lsa.umich.edu",
            "geva04.chem.lsa.umich.edu"
        ]
        self.user = "msaller"
        self.pkey = "/home/max/.ssh/id_rsa.pub"
        self.last_gather = None

    def __str__(self):
        """In case of print, gater once, the output load."""
        self.gather()
        repr = ""
        for h in self.hosts:
            repr += f"{h}:    "
            repr += f"{self.load[h][0]:.2f} "
            repr += f"{self.load[h][1]:.2f} "
            repr += f"{self.load[h][2]:.2f}\n"
        return repr

    def gather(self):
        """Make SSH connection to compute-nodes and collect load."""
        for h in self.hosts:
            with Connection(host=h, user=self.user) as c:
                load = c.run("uptime", hide="both")
                self.load[h] = np.array([
                                            float(load.stdout[-18:-13]),
                                            float(load.stdout[-12:-7]),
                                            float(load.stdout[-6:-1])
                                        ], dtype=np.float64)
        # Set time of last gather to current time
        self.last_gather = time.ctime()

    def plot(self):
        """Plot load-set of hosts."""
        # Gather first if necessary
        if self.last_gather is None:
            self.gather()

        # Create single load array
        load = np.array([lc.load[i] for i in lc.hosts])

        labels = [i.split(".")[0] for i in self.hosts]
        x = np.arange(len(labels))
        width = 0.2

        fig, ax = plt.subplots()
        one = ax.bar(x - width, load[:, 0], width, label="1min load")
        five = ax.bar(x, load[:, 1], width, label="5min load")
        fifteen = ax.bar(x + width, load[:, 2], width, label="15min load")

        ax.set_ylim([0, 1.1 * np.nanmax(load)])
        ax.set_xlabel("Host", fontsize="x-large")
        ax.set_ylabel("Load", fontsize="x-large")
        ax.set_xticks(x, labels)
        ax.legend(frameon=False, fontsize="x-large")

        ax.bar_label(one, padding=3, fontsize="small")
        ax.bar_label(five, padding=3, fontsize="small")
        ax.bar_label(fifteen, padding=3, fontsize="small")

        fig.tight_layout()
        plt.show()

    def monitor(self):
        """Plot and continuously update load-set of hosts."""
        # Create single load array
        self.gather()
        load = np.array([lc.load[i] for i in lc.hosts])

        labels = [i.split(".")[0] for i in self.hosts]
        x = np.arange(len(labels))
        width = 0.2

        fig, ax = plt.subplots()
        one = ax.bar(x - width, load[:, 0], width, label="1min load")
        five = ax.bar(x, load[:, 1], width, label="5min load")
        fifteen = ax.bar(x + width, load[:, 2], width, label="15min load")

        ax.set_ylim([0, 1.1 * np.nanmax(load)])
        ax.set_xlabel("Host", fontsize="x-large")
        ax.set_ylabel("Load", fontsize="x-large")
        ax.set_xticks(x, labels)
        ax.legend(frameon=False, fontsize="x-large")

        fig.tight_layout()
        plt.show(block=False)

        with plt.ion():
            while plt.fignum_exists(fig.number):
                plt.pause(30)
                self.gather()
                load = np.array([lc.load[i] for i in lc.hosts])
                for i, bar in enumerate([one, five, fifteen]):
                    for j, b in enumerate(bar):
                        b.set_height(load[j, i])
                ax.set_ylim([0, 1.1 * np.nanmax(load)])
                fig.canvas.draw()
                fig.canvas.flush_events()
                print(f"Last update to load data: {time.ctime()}")


if __name__ == "__main__":
    """Initialize LoadCollector instance and print result of self.gather()."""
    lc = LoadCollector()
    lc.monitor()
