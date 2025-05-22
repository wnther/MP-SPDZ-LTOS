import math
import time
import plotly.graph_objects as go
import re
import os
from output_parser_v2 import parse_output

os.system("mkdir -p plots")

fig = go.Figure()

fig.write_image("plots/temp_fake_plot.pdf")
os.remove("plots/temp_fake_plot.pdf")
time.sleep(1)

# # ##
# #
# #  Basic plot of each set of data
# #
# # ##
all_experiments = parse_output("party0.out")

# titles = [
#     "LTOS with real offline phase",
#     "LTOS with real offline phase",
#     "LTOS with fake offline phase",
#     "LTOS with fake offline phase",
#     "Waksman based with real offline phase ",
#     "Waksman based with real offline phase",
#     "Waksman based with fake offline phase ",
#     "Waksman based with fake offline phase",
# ]
# file_names = [
#     "Ltos_real_m",
#     "Ltos_real_n",
#     "Ltos_fake_m",
#     "Ltos_fake_n",
#     "Waksman_real_m",
#     "Waksman_real_n",
#     "Waksman_fake_m",
#     "Waksman_fake_n",
# ]



def plot_experiment(
    output_path: str, x: list, y: list[list], title: str, x_title: str, y_title: str, log_y: bool = False
):
    x_vals = x
    y_vals = y

    fig = go.Figure()

    for y_val, name in y_vals:
        fig.add_trace(go.Scatter(x=x_vals, y=y_val, mode="lines+markers", name=name))

    
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        margin=dict(l=40, r=20, t=40, b=40),
        yaxis_range=[0, 1.1 * max(max(y_val[0]) for y_val in y_vals)],
        xaxis_ticklabelstep=1,
        xaxis_tickvals=x_vals,
    )

    if log_y:
        fig.update_layout(yaxis_range=[math.log(min(min(y_val[0]) for y_val in y_vals), 10), 1.1*math.log(max(max(y_val[0]) for y_val in y_vals), 10)])
        fig.update_yaxes(type="log")

    fig.write_image(output_path)

plot_experiment(
    "plots/batch_b.pdf",
    all_experiments["ltos_batch_real_10"]["batch_size"],
    [(all_experiments["ltos_batch_real_10"]["rounds"], "ltos"), (all_experiments["mascot_batch_real_10"]["rounds"], "waksman-based")],
    "rounds when batch be sizin",
    "batch size",
    "rounds",
    log_y=True,
)

# plot_experiment(
#     "plots/bandwidth-fake.pdf",
#     all_experiments["ltos_fake_m"]["m"],
#     [(all_experiments["ltos_fake_m"]["data_sent"], "ltos"), (all_experiments["waksman_fake_m"]["data_sent"], "waksman-based")],
#     "bandwidth used when using fake offline phase ltos",
#     "log(m)",
#     "bandwidth (MB)",
#     log_y=True,
# )

# plot_experiment(
#     "plots/bandwidth-real.pdf",
#     all_experiments["ltos_real_m"]["m"],
#     [(all_experiments["ltos_real_m"]["data_sent"], "ltos"), (all_experiments["waksman_real_m"]["data_sent"], "waksman-based")],
#     "bandwidth used when using real offline phase ltos",
#     "log(m)",
#     "bandwidth (MB)",
#     log_y=True,
# )

# plot_experiment(
#     "plots/bandwidth-real-n.pdf",
#     all_experiments["ltos_real_n"]["n"],
#     [(all_experiments["ltos_real_n"]["data_sent"], "ltos"), (all_experiments["waksman_real_n"]["data_sent"], "waksman-based")],
#     "bandwidth used when using real offline phase ltos",
#     "n",
#     "bandwidth (MB)",
#     log_y=True,
# )

# # # ##
# # #
# # #  Comparison plots of the two algorithms
# # #
# # # ##


# # titles = [
# #     "Comparison using real offline phase",
# #     "Comparison using real offline phase",
# #     "Comparison using fake offline phase",
# #     "Comparison using fake offline phase",
# # ]
# # file_names = [
# #     "Compare_real_m",
# #     "Compare_real_n",
# #     "Compare_fake_m",
# #     "Compare_fake_n",
# # ]

# # for i in range(4):
# #     fig = go.Figure()
# #     x_vals = [t[1] for t in lists[i+4]] if i % 2 == 0 else [t[0] for t in lists[i+4]]
# #     ltos_y_vals = [t[2] for t in lists[i]]
# #     waksman_y_vals = [t[2] for t in lists[i + 4]]
# #     fig.add_trace(go.Scatter(
# #         x=x_vals,
# #         y=ltos_y_vals,
# #         mode='lines+markers',
# #         name="Ltos"
# #     ))
# #     fig.add_trace(go.Scatter(
# #         x=x_vals,
# #         y=waksman_y_vals,
# #         mode='lines+markers',
# #         name="Waksman Based"
# #     ))
# #     fig.update_layout(
# #         title=titles[i],
# #         xaxis_title='log(m)' if i % 2 == 0 else 'n',
# #         yaxis_title='time (ms)',
# #         margin=dict(l=40, r=20, t=40, b=40),
# #         yaxis_range=[0, 1.1*max(max(ltos_y_vals), max(waksman_y_vals))],
# #         xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# #     )

# #     fig.write_image(f"plots/{file_names[i]}.pdf")
# plot_experiment(
#     "plots/Compare_real_m.pdf",
#     all_experiments["ltos_real_m"]["m"],
#     [
#         (all_experiments["ltos_real_m"]["online_time"], "Ltos"),
#         (all_experiments["waksman_real_m"]["online_time"], "Waksman Based"),
#     ],
#     "Comparison using real offline phase",
#     "log(m)",
#     "time (ms)",
#     log_y=True,
# )

# plot_experiment(
#     "plots/Compare_real_n.pdf",
#     all_experiments["ltos_real_n"]["n"],
#     [
#         (all_experiments["ltos_real_n"]["online_time"], "Ltos"),
#         (all_experiments["waksman_real_n"]["online_time"], "Waksman Based"),
#     ],
#     "Comparison using real offline phase",
#     "n",
#     "time (ms)",
#     log_y=True,
# )
# plot_experiment(
#     "plots/Compare_fake_m.pdf",
#     all_experiments["ltos_fake_m"]["m"],
#     [
#         (all_experiments["ltos_fake_m"]["online_time"], "Ltos"),
#         (all_experiments["waksman_fake_m"]["online_time"], "Waksman Based"),
#     ],
#     "Comparison using fake offline phase",
#     "log(m)",
#     "time (ms)",
#     log_y=True,
# )
# plot_experiment(
#     "plots/Compare_fake_n.pdf",
#     all_experiments["ltos_fake_n"]["n"],
#     [
#         (all_experiments["ltos_fake_n"]["online_time"], "Ltos"),
#         (all_experiments["waksman_fake_n"]["online_time"], "Waksman Based"),
#     ],
#     "Comparison using fake offline phase",
#     "n",
#     "time (ms)",
#     log_y=True,
# )


# # # ##
# # #
# # #  Time Scaled by expected time in terms of O-notation
# # #
# # # ##
# # title = "Waksman based with real offline phase, time divided by m*log(m)"
# # to_plot = 4
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / (t[1]*(2**t[1]))) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / (m * log(m))',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/waksman_real_m_divided_by_m*log(m).pdf")

# waksman_real_m_online_time = all_experiments["waksman_real_m"]["online_time"]
# waksman_real_m_m = all_experiments["waksman_real_m"]["m"]

# plot_experiment(
#     output_path="plots/waksman_real_m_divided_by_m*log(m).pdf",
#     x=all_experiments["waksman_real_m"]["m"],
#     y=[
#         (
#             [
#                 t / (int(m) * (2 ** int(m)))
#                 for (t, m) in zip(waksman_real_m_online_time, waksman_real_m_m)
#             ],
#             "Waksman",
#         ),
#     ],
#     title="Waksman based with real offline phase, time divided by m*log(m)",
#     x_title="log(m)",
#     y_title="time (ms) / (m * log(m))",
# )

# # title = "Waksman based with fake offline phase, time divided by m"
# # to_plot = 6
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / (2**t[1])) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / m',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/waksman_fake_m_divided_by_m.pdf")


# # title = "Waksman based with real offline phase, time divided by n"
# # to_plot = 5
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / t[0]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / n',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/waksman_real_n_divided_by_n.pdf")


# # title = "Waksman based with fake offline phase, time divided by n"
# # to_plot = 7
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / t[0]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / n',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/ltos_real_n_divided_by_n.pdf")


# # title = "Ltos with real offline phase, time divided by log(m)"
# # to_plot = 0
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / t[1]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / log(m)',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/ltos_real_m_divided_by_log(m).pdf")


# # title = "Ltos with real offline phase, time divided by m"
# # to_plot = 0
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / 2**t[1]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / m',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/ltos_real_m_divided_by_m.pdf")


# # title = "Ltos with fake offline phase, time divided by log(m)"
# # to_plot = 2
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / t[1]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / log(m)',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/ltos_fake_m_divided_by_log(m).pdf")


# # title = "Ltos with fake offline phase, time divided by m"
# # to_plot = 2
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / 2**t[1]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / m',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/ltos_fake_m_divided_by_m.pdf")


# # title = "Ltos with real offline phase, time divided by n"
# # to_plot = 1
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / t[0]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / n',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/ltos_real_n_divided_by_n.pdf")


# # title = "Ltos with fake offline phase, time divided by n"
# # to_plot = 3
# # fig = go.Figure()
# # x_vals = [t[1] for t in lists[to_plot]] if to_plot % 2 == 0 else [t[0] for t in lists[to_plot]]
# # y_vals = [(t[2] / t[0]) for t in lists[to_plot]]
# # fig.add_trace(go.Scatter(
# #     x=x_vals,
# #     y=y_vals,
# #     mode='lines+markers',
# #     name="divided by expected time"
# # ))
# # fig.update_layout(
# #     title=title,
# #     xaxis_title='log(m)' if to_plot % 2 == 0 else 'n',
# #     yaxis_title='time (ms) / n',
# #     margin=dict(l=40, r=20, t=40, b=40),
# #     yaxis_range=[0, 1.1*max(y_vals)],
# #     xaxis_ticklabelstep=1,
# #     xaxis_tickvals=x_vals,
# # )
# # fig.write_image(f"plots/ltos_fake_n_divided_by_n.pdf")
