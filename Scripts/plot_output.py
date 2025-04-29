import time
import plotly.graph_objects as go
import re
import os

os.system("mkdir -p plots")
pattern = r"(\w+): n=(\d+)\s+m=2\^(\d+):\s+(\d+)"
file = open("party0.out", "r")
lines = file.readlines()

lists = [[] for _ in range(8)]

lst_num = 0
for i in range(len(lines)):
    line = lines[i].rstrip()
    if line == "-": 
        lst_num += 1

    match = re.search(pattern, line)
    if match:
        n = int(match.group(2))
        m_exp = int(match.group(3))
        time_elapsed = int(match.group(4))
        
        lists[lst_num].append((n, m_exp, time_elapsed))


def best_times_for_size(i, lst):    
    best_times = {}
    
    index = int(i % 2 == 0)
    for tup in lst:
        if tup[index] not in best_times or tup[2] < best_times[tup[index]][2]:
            best_times[tup[index]] = tup
    
    return list(best_times.values())

lists = [best_times_for_size(i, lst) for (i, lst) in enumerate(lists)]


titles = [
    "LTOS with real offline phase scaling w/ vector size",
    "LTOS with real offline phase scaling w/ number of parties",
    "LTOS with fake offline phase scaling w/ vector size",
    "LTOS with fake offline phase scaling w/ number of parties",
    "Waksman based with real offline phase scaling w/ vector size",
    "Waksman based with real offline phase scaling w/ number of parties",
    "Waksman based with fake offline phase scaling w/ vector size",
    "Waksman based with fake offline phase scaling w/ number of parties",
]

for i in range(8):
    x_vals = [t[1] for t in lists[i]] if i % 2 == 0 else [t[0] for t in lists[i]]
    y_vals = [t[2] for t in lists[i]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines+markers',
        name=titles[i]
    ))

    fig.update_layout(
        title=titles[i],
        xaxis_title='m' if i % 2 == 0 else 'n',
        yaxis_title='time',
        margin=dict(l=40, r=20, t=40, b=40),
    )

    fig.write_image("plots/temp_fake_plot.pdf")
    os.remove("plots/temp_fake_plot.pdf")
    time.sleep(1)
    fig.write_image(f"plots/my_plot{i}.pdf")