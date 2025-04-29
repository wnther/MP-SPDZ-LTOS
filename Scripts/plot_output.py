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



fig = go.Figure()

fig.write_image("plots/temp_fake_plot.pdf")
os.remove("plots/temp_fake_plot.pdf")
time.sleep(1)

# ##
# 
#  Basic plot of each set of data
# 
# ##

titles = [
    "LTOS with real offline phase",
    "LTOS with real offline phase",
    "LTOS with fake offline phase",
    "LTOS with fake offline phase",
    "Waksman based with real offline phase ",
    "Waksman based with real offline phase",
    "Waksman based with fake offline phase ",
    "Waksman based with fake offline phase",
]
file_names = [
    "Ltos_real_m",
    "Ltos_real_n",
    "Ltos_fake_m",
    "Ltos_fake_n",
    "Waksman_real_m",
    "Waksman_real_n",
    "Waksman_fake_m",
    "Waksman_fake_n",
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
        xaxis_title='log(m)' if i % 2 == 0 else 'n',
        yaxis_title='time',
        margin=dict(l=40, r=20, t=40, b=40),
        yaxis_range=[0, 1.1*max(y_vals)],
    )

    fig.write_image(f"plots/{file_names[i]}.pdf")

# ##
# 
#  Comparison plots of the two algorithms
# 
# ##


titles = [
    "Comparison using real offline phase",
    "Comparison using real offline phase",
    "Comparison using fake offline phase",
    "Comparison using fake offline phase",
]
file_names = [
    "Compare_real_m",
    "Compare_real_n",
    "Compare_fake_m",
    "Compare_fake_n",
]

for i in range(4):
    fig = go.Figure()
    x_vals = [t[1] for t in lists[i+4]] if i % 2 == 0 else [t[0] for t in lists[i+4]]
    ltos_y_vals = [t[2] for t in lists[i]]
    waksman_y_vals = [t[2] for t in lists[i + 4]]
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=ltos_y_vals,
        mode='lines+markers',
        name="Ltos"
    ))
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=waksman_y_vals,
        mode='lines+markers',
        name="Waksman Based"
    ))
    fig.update_layout(
        title=titles[i],
        xaxis_title='log(m)' if i % 2 == 0 else 'n',
        yaxis_title='time',
        margin=dict(l=40, r=20, t=40, b=40),
        yaxis_range=[0, 1.1*max(max(ltos_y_vals), max(waksman_y_vals))],
    )
    
    fig.write_image(f"plots/{file_names[i]}.pdf")


# ##
#
#  Time Scaled by expected time in terms of O-notation
#
# ##
title = "Waksman based with real offline phase, time divided by m*log(m)"
to_plot = 4
fig = go.Figure()
x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
y_vals = [(t[2] / (t[1]*(2**t[1]))) for t in lists[to_plot]]
fig.add_trace(go.Scatter(
    x=x_vals,
    y=y_vals,
    mode='lines+markers',
    name="divided by expected time"
))
fig.update_layout(
    title=title,
    xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
    yaxis_title='time / (m * log(m))',
    margin=dict(l=40, r=20, t=40, b=40),
    yaxis_range=[0, 1.1*max(y_vals)],
)

fig.write_image(f"plots/waksman_real_m_divided.pdf")

title = "Waksman based with fake offline phase, time divided by m"
to_plot = 6
fig = go.Figure()
x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
y_vals = [(t[2] / (2**t[1])) for t in lists[to_plot]]
fig.add_trace(go.Scatter(
    x=x_vals,
    y=y_vals,
    mode='lines+markers',
    name="divided by expected time"
))
fig.update_layout(
    title=title,
    xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
    yaxis_title='time / m',
    margin=dict(l=40, r=20, t=40, b=40),
    yaxis_range=[0, 1.1*max(y_vals)],
)

fig.write_image(f"plots/waksman_fake_m_divided.pdf")

title = "Waksman based with real offline phase, time divided by n"
to_plot = 5
fig = go.Figure()
x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
y_vals = [(t[2] / t[0]) for t in lists[to_plot]]
fig.add_trace(go.Scatter(
    x=x_vals,
    y=y_vals,
    mode='lines+markers',
    name="divided by expected time"
))
fig.update_layout(
    title=title,
    xaxis_title='n' if to_plot % 2 == 0 else 'n',
    yaxis_title='time / n',
    margin=dict(l=40, r=20, t=40, b=40),
    yaxis_range=[0, 1.1*max(y_vals)],
)

fig.write_image(f"plots/waksman_real_n_divided.pdf")


title = "Waksman based with fake offline phase, time divided by n"
to_plot = 7
fig = go.Figure()
x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
y_vals = [(t[2] / t[0]) for t in lists[to_plot]]
fig.add_trace(go.Scatter(
    x=x_vals,
    y=y_vals,
    mode='lines+markers',
    name="divided by expected time"
))
fig.update_layout(
    title=title,
    xaxis_title='n' if to_plot % 2 == 0 else 'n',
    yaxis_title='time / n',
    margin=dict(l=40, r=20, t=40, b=40),
    yaxis_range=[0, 1.1*max(y_vals)],
)

fig.write_image(f"plots/waksman_fake_n_divided.pdf")