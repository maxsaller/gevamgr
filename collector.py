"""Simple compute-node load collector."""
import os
import sys
import time
import numpy as np
import argparse as ag
from fabric import Connection
import matplotlib
import matplotlib.pyplot as plt
import mpld3


class LoadCollector(object):
    """Load collector."""

    def __init__(self, *args, **kwargs):
        """Initialize."""
        self.load = {}
        self.temp = {}
        self.hosts = [
            "geva01.chem.lsa.umich.edu",
            "geva02.chem.lsa.umich.edu",
            "geva03.chem.lsa.umich.edu",
            "geva04.chem.lsa.umich.edu"
        ]
        self.user = "msaller"
        self.pkey = "/home/max/.ssh/id_rsa.pub"
        self.last_gather = None

        matplotlib.rcParams["backend"] = "qtagg"
        matplotlib.rcParams["toolbar"] = "None"
        plt.style.use("dark_background")

        # Make SSH connection to compute-nodes.
        self.connects = {h: Connection(host=h, user=self.user) for h in self.hosts}

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
        """Collect load from hosts."""
        for h in self.hosts:
            temp = self.connects[h].run("sensors", hide="both")
            self.temp[h] = float([i for i in temp.stdout.split("\n") if "Package id 0" in i][0].split(":")[1].split("°")[0])

            load = self.connects[h].run("uptime", hide="both")
            ld = load.stdout.split(",")
            self.load[h] = np.array([
                                        float(ld[-3].split(":")[-1]),
                                        float(ld[-2]),
                                        float(ld[-1])
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
        plt.show(block=True)

        # Close connections
        for connect in self.connects:
            connect.close()

    def monitor(self):
        """Plot and continuously update load-set of hosts."""
        # Create single load array
        self.gather()
        load = np.array([self.load[i] for i in self.hosts])
        temp = np.array([self.temp[i] for i in self.hosts])

        labels = [i.split(".")[0] for i in self.hosts]
        x = np.arange(len(labels))
        width = 0.2

        fig, ax = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]})
        fig.canvas.manager.set_window_title("Geva Manager")
        one = ax[0].bar(x - width, load[:, 0], width, color="tab:blue")
        five = ax[0].bar(x, load[:, 1], width, color="tab:orange")
        fifteen = ax[0].bar(x + width, load[:, 2], width, color="tab:green")

        ax[0].plot([-1, 4], [20, 20], color="white", ls="--", lw=0.5)
        ax[0].plot([-1, 4], [24, 24], color="white", ls="--", lw=0.5)

        ax[0].set_xlim([-0.5, 3.5])
        ax[0].set_ylim([0, 25])
        ax[0].set_ylabel("Average Load", fontsize="x-large")
        ax[0].set_xticks(x, labels)
        ax[0].set_yticks([0, 4, 8, 12, 16, 20, 24])

        tbar = ax[1].bar(0.25*x, temp, width, color="tab:red")
        ax[1].plot([-0.75, 1.5], [100, 100], color="white", ls="--", lw=0.5)

        ax[1].set_xlim([-0.25, 1])
        ax[1].set_xticks(0.25*x, labels, rotation=90, color="black")
        ax[1].tick_params(axis="x", direction="in", pad=-45)
        ax[1].set_ylim([25, 105])
        ax[1].set_yticks([25, 50, 75, 100])
        ax[1].set_ylabel("Temperature (°C)", fontsize="x-large")
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()

        fig.suptitle(self.last_gather, y=0.91, va="bottom", fontsize="x-large")

        fig.tight_layout()
        plt.show(block=False)

        with plt.ion():
            while plt.fignum_exists(fig.number):
                # plt.pause(1)
                self.gather()
                load = np.array([self.load[i] for i in self.hosts])
                temp = np.array([self.temp[i] for i in self.hosts])
                for i, bar in enumerate([one, five, fifteen]):
                    for j, b in enumerate(bar):
                        b.set_height(load[j, i])
                for j, b in enumerate(tbar):
                    b.set_height(temp[j])
                fig.suptitle(self.last_gather, y=0.91, va="bottom", fontsize="x-large")
                fig.canvas.draw()
                fig.canvas.flush_events()

        # Close connections
        for h in self.hosts:
            self.connects[h].close()


if __name__ == "__main__":
    lc = LoadCollector()
    lc.monitor()
