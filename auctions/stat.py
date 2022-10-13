import datetime
import json
import time

import matplotlib.pyplot as plt
import numpy as np

# read_loc = "auctions/graphs/data.txt"
# write_loc = "auctions/graphs/graph.png"
read_loc = "C:/Users/ravin/CS361/BBay Auction/auctions/graphs/data.txt"
write_loc = "C:/Users/ravin/CS361/BBay Auction/auctions/graphs/graph.png"

print("Success ✅: Initializing Statistics Service 🚀 ...")
while True:
    time.sleep(0.5)
    try:
        with open(read_loc, "r+") as f:
            data = json.load(f)
            f.truncate(0)
    except:
        # print("Error 💥: Couldn't read data file... ")
        continue

    # Decide if profit or expense graph
    if data["type"] == "profit":
        plotType = "profit"
        plotName = "Profit"
    else:
        plotType = "expense"
        plotName = "Expense"

    # Get the data
    print("Success ✅: Getting data ...")

    # Calculate the profit for each Month and Year

    # Dictionary of months and their respective profits
    months = {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0, "June": 0,
              "July": 0, "August": 0, "September": 0, "October": 0, "November": 0, "December": 0}

    for i in range(len(data["data"])):
        value = data["data"][i][plotType]

        date = datetime.datetime.strptime(
            data["data"][i]["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        month = date.month
        year = date.year
        print(plotName + ": " + str(value) + " for Month: " + str(month))

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
    print(val)
    total = sum(val)

    print(total)

    fig, ax = plt.subplots()
    ax.bar(mon, val, color="#66c2a5")
    ax.set_title(plotName + " for each Month for Year: " + str(year))
    ax.set_ylabel(plotName)
    ax.set_xticklabels(mon, rotation=45)

    for bars in ax.containers:
        ax.bar_label(bars, rotation=45, label_type='edge', color='black')

    fig.set_size_inches(8, 6)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    fig.savefig(write_loc,
                dpi=100,  bbox_inches='tight')
