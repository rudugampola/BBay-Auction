import datetime
import json
import time

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# read_loc = "auctions/graphs/data.txt"
# write_loc = "auctions/graphs/graph.png"
read_loc = "C:/Users/ravin/CS361/BBay Auction/auctions/graphs/data.txt"
write_loc = "C:/Users/ravin/CS361/BBay Auction/auctions/graphs/graph.png"

print(bcolors.OKGREEN + "Success ✅: Initializing Statistics Service 🚀 ..." + bcolors.ENDC)
print("*" * 50)
while True:
    time.sleep(1)
    try:
        with open(read_loc, "r+") as f:
            data = json.load(f)
            f.truncate(0)
    except:
        # print(bcolors.WARNING + "Error 💥: Couldn't read data file... ")
        continue

    # Decide if profit or expense graph
    if data["type"] == "profit":
        plotType = "profit"
        plotName = "Profit"
    else:
        plotType = "expense"
        plotName = "Expense"

    # Get the data
    print(bcolors.HEADER + "Success ✅: Getting data ..." + bcolors.ENDC)

    # Calculate the profit for each Month and Year

    # Dictionary of months and their respective profits
    months = {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0, "June": 0,
              "July": 0, "August": 0, "September": 0, "October": 0, "November": 0, "December": 0}
    year = 0

    for i in range(len(data["data"])):
        value = data["data"][i][plotType]

        # Get the month and year
        # date = datetime.datetime.strptime(
        #     data["data"][i]["date"], "%Y-%m-%dT%H:%M:%S.%fZ")

        date = data["data"][i]["date"].split("T")[0]
        month = int(date.split("-")[1].lstrip("0"))
        year = date.split("-")[0].lstrip("0")
        print(bcolors.OKCYAN + plotName + ": $" + str('{0:.2f}'.format(value)) +
              " for Month: " + str(month) + bcolors.ENDC)

        # Update the dictionary with the profit for the month
        # for key in months:
        if month == 1:
            months["January"] += value
        elif month == 2:
            months["February"] += value
        elif month == 3:
            months["March"] += value
        elif month == 4:
            months["April"] += value
        elif month == 5:
            months["May"] += value
        elif month == 6:
            months["June"] += value
        elif month == 7:
            months["July"] += value
        elif month == 8:
            months["August"] += value
        elif month == 9:
            months["September"] += value
        elif month == 10:
            months["October"] += value
        elif month == 11:
            months["November"] += value
        elif month == 12:
            months["December"] += value

    # Plot the data in a bar graph, save it as a png, and display it
    # X-axis is the months of the year and Y-axis is the profit
    mon = list(months.keys())
    val = list(months.values())
    # print(months["October"])
    total = sum(val)

    print(bcolors.OKGREEN + "Total: $" +
          str('{0:.2f}'.format(total)) + bcolors.ENDC)
    print("*" * 50)

    fig, ax = plt.subplots()
    ax.bar(mon, val, color="#66c2a5")
    ax.set_title(plotName + " for each Month for Year: " + str(year))
    ax.set_ylabel(plotName)
    ax.set
    # fixing xticks with FixedLocator and FixedFormatter
    ax.xaxis.set_major_locator(
        mticker.FixedLocator(range(len(mon))))
    ax.set_xticklabels(mon, rotation=45, ha="right")

    for bars in ax.containers:
        ax.bar_label(bars, rotation=45, label_type='edge', color='black')

    fig.set_size_inches(8, 6)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    fig.savefig(write_loc,
                dpi=100,  bbox_inches='tight')
    time.sleep(1)