import math
import time
import plotly.graph_objects as go
import re
import os
from output_parser_v2 import parse_output
from typing import Tuple, Union
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
all_experiments = parse_output("benchmarks/data_combined.out")


def plot_experiment(
    output_path: str, x: list, y: list[Tuple[list, str, Union[str, None]]], title: str, x_title: str, y_title: str, log_y: bool = False
):
    x_vals = x
    y_vals = y

    fig = go.Figure()

    ltos_colors = ["#0035d4", "#7064e0", "#a695ec", "#d4c9f6"]
    waks_colors = ["#c72020", "#df6453", "#f09989", "#fcccc2"]
    ltos_color_index = 0
    waks_color_index = 0

    def get_line_props(line_type: str) -> str:
        dash = "solid"
        nonlocal ltos_color_index, waks_color_index
        if line_type == "ltos":
            if ltos_color_index != 0:
                dash = "dot"
            color = ltos_colors[ltos_color_index]
            ltos_color_index = (ltos_color_index + 1) % len(ltos_colors)
        else:
            if waks_color_index != 0:
                dash = "dot"
            color = waks_colors[waks_color_index]
            waks_color_index = (waks_color_index + 1) % len(waks_colors)
        return dict(dash=dash, color=color)

    for y_val in y_vals:
        if len(y_val) == 2:
            y_val, name = y_val
            line_type = "solid"
        elif len(y_val) == 3:
            y_val, name, line_type = y_val
        fig.add_trace(go.Scatter(x=x_vals, y=y_val, mode="lines+markers", name=name, line=get_line_props(line_type)))

    
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
        fig.update_layout(yaxis_range=[math.log(min(min(y_val[0]) for y_val in y_vals), 10)-1, 1.1*math.log(max(max(y_val[0]) for y_val in y_vals), 10)])
        fig.update_yaxes(type="log")

    fig.write_image(output_path)


# THE FIRST EXPERIMENT IN THE THESIS
def plot_real_compare():
    plot_experiment(
        "plots/compare_real_m.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_real"]["total_time"], "ltos", "ltos"),
            (all_experiments["waksman_based_real"]["total_time"], "waks"),
        ],
        "Total Time for all phases (offline and online)",
        "Exponent of the vector size 2^i",
        "Total time in seconds",
        log_y=False,
    )

    plot_experiment(
        "plots/compare_m_real_log.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_real"]["total_time"], "ltos", "ltos"),
            (all_experiments["waksman_based_real"]["total_time"], "waks"),
        ],
        "Total Time for all phases (offline and online)",
        "Exponent of the vector size 2^i",
        "Total time in seconds",
        log_y=True,
    )

    plot_experiment(
        "plots/compare_m_real_log_2.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_real"]["total_time"], "ltos", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_real"]["total_time"], all_experiments["ltos_real"]["m"])], "ltos / log m", "ltos"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["ltos_real"]["total_time"], all_experiments["ltos_real"]["m"])], "ltos / m", "ltos"),
            ([i[0]/(i[1]*(2**(i[1]))) for i in zip(all_experiments["ltos_real"]["total_time"], all_experiments["ltos_real"]["m"])], "ltos / (m log m)", "ltos"),
            (all_experiments["waksman_based_real"]["total_time"], "waks"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_real"]["total_time"], all_experiments["waksman_based_real"]["m"])], "waks / log m"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["waksman_based_real"]["total_time"], all_experiments["waksman_based_real"]["m"])], "waks / m"),
            ([i[0]/(i[1]*(2**(i[1]))) for i in zip(all_experiments["waksman_based_real"]["total_time"], all_experiments["waksman_based_real"]["m"])], "waks / (m log m)"),
        ],
        "Total Time for all phases (offline and online)",
        "Exponent of the vector size 2^i",
        "Total time in seconds",
        log_y=True,
    )


    plot_experiment(
        "plots/compare_real_m_rounds.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_real"]["rounds"], "ltos", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_real"]["rounds"], all_experiments["ltos_real"]["m"])], "ltos / log m", "ltos"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["ltos_real"]["rounds"], all_experiments["ltos_real"]["m"])], "ltos / m", "ltos"),
            ([i[0]/(i[1]*(2**(i[1]))) for i in zip(all_experiments["ltos_real"]["rounds"], all_experiments["ltos_real"]["m"])], "ltos / (m log m)", "ltos"),
            (all_experiments["waksman_based_real"]["rounds"], "waks"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_real"]["rounds"], all_experiments["waksman_based_real"]["m"])], "waks / log m"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["waksman_based_real"]["rounds"], all_experiments["waksman_based_real"]["m"])], "waks / m"),
            ([i[0]/(i[1]*(2**(i[1]))) for i in zip(all_experiments["waksman_based_real"]["rounds"], all_experiments["waksman_based_real"]["m"])], "waks / (m log m)"),
        ],
        "Total number of rounds for all phases (offline and online)",
        "Exponent of the vector size 2^i",
        "Number of rounds",
        log_y=True,
    )

    plot_experiment(
        "plots/compare_real_m_data.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_real"]["global_data_sent"], "ltos", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_real"]["global_data_sent"], all_experiments["ltos_real"]["m"])], "ltos / log m", "ltos"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["ltos_real"]["global_data_sent"], all_experiments["ltos_real"]["m"])], "ltos / m", "ltos"),
            ([i[0]/(i[1]*(2**(i[1]))) for i in zip(all_experiments["ltos_real"]["global_data_sent"], all_experiments["ltos_real"]["m"])], "ltos / (m log m)", "ltos"),
            (all_experiments["waksman_based_real"]["global_data_sent"], "waks"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_real"]["global_data_sent"], all_experiments["waksman_based_real"]["m"])], "waks / log m"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["waksman_based_real"]["global_data_sent"], all_experiments["waksman_based_real"]["m"])], "waks / m"),
            ([i[0]/(i[1]*(2**i[1])) for i in zip(all_experiments["waksman_based_real"]["global_data_sent"], all_experiments["waksman_based_real"]["m"])], "waks / (m log m)"),
        ],
        "Total data sent by all parties for all phases (offline and online)",
        "Exponent of the vector size 2^i",
        "Data sent in MB",
        log_y=True,
    )



def plot_fake_compare():
    plot_experiment(
        "plots/compare_realvsfake_m.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["total_time"], "ltos - prep from files", "ltos"),
            (all_experiments["ltos_real"]["total_time"], "ltos - prep by MASCOT", "ltos"),
            (all_experiments["waksman_based_fake"]["total_time"], "waks - prep from files"),
            (all_experiments["waksman_based_real"]["total_time"], "waks - prep by MASCOT"),
        ],
        "Total Time comparison between preprocessing from files and MASCOT",
        "Exponent of the vector size 2^i",
        "Total time in seconds",
        log_y=True,
    )
    plot_experiment(
        "plots/compare_realvsfake_m_data.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["global_data_sent"], "ltos - prep from files", "ltos"),
            (all_experiments["ltos_real"]["global_data_sent"], "ltos - prep by MASCOT", "ltos"),
            (all_experiments["waksman_based_fake"]["global_data_sent"], "waks - prep from files"),
            (all_experiments["waksman_based_real"]["global_data_sent"], "waks - prep by MASCOT"),
        ],
        "Total data comparison between preprocessing from files and MASCOT",
        "Exponent of the vector size 2^i",
        "Data sent in MB",
        log_y=True,
    )
    plot_experiment(
        "plots/compare_realvsfake_m_rounds.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["rounds"], "ltos - prep from files", "ltos"),
            (all_experiments["ltos_real"]["rounds"], "ltos - prep by MASCOT", "ltos"),
            (all_experiments["waksman_based_fake"]["rounds"], "waks - prep from files"),
            (all_experiments["waksman_based_real"]["rounds"], "waks - prep by MASCOT"),
        ],
        "Total rounds comparison between preprocessing from files and MASCOT",
        "Exponent of the vector size 2^i",
        "Number of rounds",
        log_y=True,
    )

    plot_experiment(
        "plots/compare_fake_m.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["total_time"], "ltos", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_fake"]["total_time"], all_experiments["ltos_fake"]["m"])], "ltos / log m", "ltos"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["ltos_fake"]["total_time"], all_experiments["ltos_fake"]["m"])], "ltos / m", "ltos"),
            ([i[0]/((i[1]*(2**i[1]))) for i in zip(all_experiments["ltos_fake"]["total_time"], all_experiments["ltos_fake"]["m"])], "ltos / (m log m)", "ltos"),
            (all_experiments["waksman_based_fake"]["total_time"], "waks"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_fake"]["total_time"], all_experiments["waksman_based_fake"]["m"])], "waks / log m"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["waksman_based_fake"]["total_time"], all_experiments["waksman_based_fake"]["m"])], "waks / m"),
            ([i[0]/((i[1]*(2**i[1]))) for i in zip(all_experiments["waksman_based_fake"]["total_time"], all_experiments["waksman_based_fake"]["m"])], "waks / (m log m)"),
        ],
        "Total Time with preprocessing from files",
        "Exponent of the vector size 2^i",
        "Total time in seconds",
        log_y=True,
    )

    plot_experiment(
        "plots/compare_fake_m_rounds.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_fake"]["rounds"], "ltos", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_fake"]["rounds"], all_experiments["ltos_fake"]["m"])], "ltos / log m", "ltos"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["ltos_fake"]["rounds"], all_experiments["ltos_fake"]["m"])], "ltos / m", "ltos"),
            (all_experiments["waksman_based_fake"]["rounds"], "waks"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_fake"]["rounds"], all_experiments["waksman_based_fake"]["m"])], "waks / log m"),
            ([i[0]/(2**(i[1])) for i in zip(all_experiments["waksman_based_fake"]["rounds"], all_experiments["waksman_based_fake"]["m"])], "waks / m"),
        ],
        "Total number of rounds with preprocessing from files",
        "Exponent of the vector size 2^i",
        "Number of rounds",
        log_y=True,
    )

    plot_experiment(
        "plots/compare_fake_m_data.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["global_data_sent"], "ltos", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_fake"]["global_data_sent"], all_experiments["ltos_fake"]["m"])], "ltos / log m", "ltos"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["ltos_fake"]["global_data_sent"], all_experiments["ltos_fake"]["m"])], "ltos / m", "ltos"),
            ([i[0]/((i[1]*(2**i[1]))) for i in zip(all_experiments["ltos_fake"]["global_data_sent"], all_experiments["ltos_fake"]["m"])], "ltos / (m log m)", "ltos"),
            (all_experiments["waksman_based_fake"]["global_data_sent"], "waks"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_fake"]["global_data_sent"], all_experiments["waksman_based_fake"]["m"])], "waks / log m"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["waksman_based_fake"]["global_data_sent"], all_experiments["waksman_based_fake"]["m"])], "waks / m"),
            ([i[0]/((i[1]*(2**i[1]))) for i in zip(all_experiments["waksman_based_fake"]["global_data_sent"], all_experiments["waksman_based_fake"]["m"])], "waks / (m log m)"),
        ],
        "Total data sent by all parties with preprocessing from files",
        "Exponent of the vector size 2^i",
        "Data sent in MB",
        log_y=True,
    )




def plot_phases():
    plot_experiment(
        "plots/ltos_verification.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            ([i*1000000 for i in all_experiments["ltos_fake"]["total_time"]], "Total time", "ltos"), #total time is in seconds
            (all_experiments["ltos_fake"]["full_online_time"], "Total online time", "ltos"),
            (all_experiments["ltos_fake"]["time_size_dependent_prep"], "Size dependent prep", "ltos"),
            (all_experiments["ltos_fake"]["online_time_without_verification"], "Time without verification", "ltos"),
        ],
        "Time of different phases for ltos with preprocessing from files",
        "Exponent of the vector size 2^i",
        "Total time in microseconds (μs)",
        log_y=True,
    )




def plot_parties():
    plot_experiment(
        "plots/parties_fake_time.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties"]["total_time"], "ltos","ltos"),
            ([i[0]/i[1] for i in zip(all_experiments["ltos_fake_parties"]["total_time"], all_experiments["ltos_fake_parties"]["n"])], "ltos / n","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties"]["total_time"], all_experiments["ltos_fake_parties"]["n"])], "ltos / n^2","ltos"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["ltos_fake_parties"]["total_time"], all_experiments["ltos_fake_parties"]["n"])], "ltos / n^3","ltos"),
            (all_experiments["waksman_based_fake_parties"]["total_time"], "waks"),
            ([i[0]/i[1] for i in zip(all_experiments["waksman_based_fake_parties"]["total_time"], all_experiments["ltos_fake_parties"]["n"])], "waks / n"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties"]["total_time"], all_experiments["ltos_fake_parties"]["n"])], "waks / n^2"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["waksman_based_fake_parties"]["total_time"], all_experiments["ltos_fake_parties"]["n"])], "waks / n^3"),
        ],
        "Time comparison over parties for m=2^12, preprocessing from files",
        "Number of parties",
        "Total time in seconds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_fake_rounds.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties"]["rounds"], "ltos","ltos"),
            ([i[0]/i[1] for i in zip(all_experiments["ltos_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "ltos / n","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "ltos / n^2","ltos"),
            (all_experiments["waksman_based_fake_parties"]["rounds"], "waks"),
            ([i[0]/i[1] for i in zip(all_experiments["waksman_based_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "waks / n"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "waks / n^2"),
        ],
        "Rounds comparison over parties for m=2^12, preprocessing from files",
        "Number of parties",
        "Number of rounds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_fake_data.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties"]["global_data_sent"], "ltos","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "ltos / n^2","ltos"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["ltos_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "ltos / n^3","ltos"),
            (all_experiments["waksman_based_fake_parties"]["global_data_sent"], "waks"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "waks / n^2"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["waksman_based_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "waks / n^3"),
        ],
        "Total data sent by parties for m=2^12, preprocessing from files",
        "Exponent of the vector size 2^i",
        "Data sent in MB",
        log_y=True,
    )

    plot_experiment(
        "plots/parties_real_time.pdf",
        all_experiments["ltos_real_parties"]["n"],
        [
            (all_experiments["ltos_real_parties"]["total_time"], "ltos", "ltos"),
            ([i[0]/i[1] for i in zip(all_experiments["ltos_real_parties"]["total_time"], all_experiments["ltos_real_parties"]["n"])], "ltos / n","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_real_parties"]["total_time"], all_experiments["ltos_real_parties"]["n"])], "ltos / n^2","ltos"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["ltos_real_parties"]["total_time"], all_experiments["ltos_real_parties"]["n"])], "ltos / n^3","ltos"),
            (all_experiments["waksman_based_real_parties"]["total_time"], "waks"),
            ([i[0]/i[1] for i in zip(all_experiments["waksman_based_real_parties"]["total_time"], all_experiments["waksman_based_real_parties"]["n"])], "waks / n"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_real_parties"]["total_time"], all_experiments["waksman_based_real_parties"]["n"])], "waks / n^2"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["waksman_based_real_parties"]["total_time"], all_experiments["waksman_based_real_parties"]["n"])], "waks / n^3"),
        ],
        "Time comparison over parties for m=2^12, using MASCOT",
        "Number of parties",
        "Total time in seconds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_real_rounds.pdf",
        all_experiments["ltos_real_parties"]["n"],
        [
            (all_experiments["ltos_real_parties"]["rounds"], "ltos","ltos"),
            ([i[0]/i[1] for i in zip(all_experiments["ltos_real_parties"]["rounds"], all_experiments["ltos_real_parties"]["n"])], "ltos / n","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_real_parties"]["rounds"], all_experiments["ltos_real_parties"]["n"])], "ltos / n^2","ltos"),
            (all_experiments["waksman_based_real_parties"]["rounds"], "waks"),
            ([i[0]/i[1] for i in zip(all_experiments["waksman_based_real_parties"]["rounds"], all_experiments["waksman_based_real_parties"]["n"])], "waks / n"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_real_parties"]["rounds"], all_experiments["waksman_based_real_parties"]["n"])], "waks / n^2"),
        ],
        "Rounds comparison over parties for m=2^12, using MASCOT",
        "Number of parties",
        "Number of rounds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_real_data.pdf",
        all_experiments["ltos_real_parties"]["n"],
        [
            (all_experiments["ltos_real_parties"]["global_data_sent"], "ltos","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_real_parties"]["global_data_sent"], all_experiments["ltos_real_parties"]["n"])], "ltos / n^2","ltos"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["ltos_real_parties"]["global_data_sent"], all_experiments["ltos_real_parties"]["n"])], "ltos / n^3","ltos"),
            (all_experiments["waksman_based_real_parties"]["global_data_sent"], "waks"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_real_parties"]["global_data_sent"], all_experiments["waksman_based_real_parties"]["n"])], "waks / n^2"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["waksman_based_real_parties"]["global_data_sent"], all_experiments["waksman_based_real_parties"]["n"])], "waks / n^3"),
        ],
        "Total data sent by parties for m=2^12, using MASCOT",
        "Exponent of the vector size 2^i",
        "Data sent in MB",
        log_y=True,
    )

    plot_experiment(
        "plots/parties_fake_time_direct.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties_direct"]["total_time"], "ltos","ltos"),
            ([i[0]/i[1] for i in zip(all_experiments["ltos_fake_parties_direct"]["total_time"], all_experiments["ltos_fake_parties_direct"]["n"])], "ltos / n","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties_direct"]["total_time"], all_experiments["ltos_fake_parties_direct"]["n"])], "ltos / n^2","ltos"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["ltos_fake_parties_direct"]["total_time"], all_experiments["ltos_fake_parties_direct"]["n"])], "ltos / n^3","ltos"),
            (all_experiments["waksman_based_fake_parties_direct"]["total_time"], "waks"),
            ([i[0]/i[1] for i in zip(all_experiments["waksman_based_fake_parties_direct"]["total_time"], all_experiments["waksman_based_fake_parties_direct"]["n"])], "waks / n"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties_direct"]["total_time"], all_experiments["waksman_based_fake_parties_direct"]["n"])], "waks / n^2"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["waksman_based_fake_parties_direct"]["total_time"], all_experiments["waksman_based_fake_parties_direct"]["n"])], "waks / n^3"),
        ],
        "Time comparison for m=2^12 with --direct, preprocessing from files",
        "Number of parties",
        "Total time in seconds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_fake_rounds_direct.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties_direct"]["rounds"], "ltos","ltos"),
            ([i[0]/i[1] for i in zip(all_experiments["ltos_fake_parties_direct"]["rounds"], all_experiments["ltos_fake_parties_direct"]["n"])], "ltos / n","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties_direct"]["rounds"], all_experiments["ltos_fake_parties_direct"]["n"])], "ltos / n^2","ltos"),
            (all_experiments["waksman_based_fake_parties_direct"]["rounds"], "waks"),
            ([i[0]/i[1] for i in zip(all_experiments["waksman_based_fake_parties_direct"]["rounds"], all_experiments["waksman_based_fake_parties_direct"]["n"])], "waks / n"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties_direct"]["rounds"], all_experiments["waksman_based_fake_parties_direct"]["n"])], "waks / n^2"),
        ],
        "Rounds comparison for m=2^12 with --direct, preprocessing from files",
        "Number of parties",
        "Number of rounds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_fake_data_direct.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties_direct"]["global_data_sent"], "ltos","ltos"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties_direct"]["global_data_sent"], all_experiments["ltos_fake_parties_direct"]["n"])], "ltos / n^2","ltos"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["ltos_fake_parties_direct"]["global_data_sent"], all_experiments["ltos_fake_parties_direct"]["n"])], "ltos / n^3","ltos"),
            (all_experiments["waksman_based_fake_parties_direct"]["global_data_sent"], "waks"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties_direct"]["global_data_sent"], all_experiments["waksman_based_fake_parties_direct"]["n"])], "waks / n^2"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["waksman_based_fake_parties_direct"]["global_data_sent"], all_experiments["waksman_based_fake_parties_direct"]["n"])], "waks / n^3"),
        ],
        "Total data sent by parties with --direct, preprocessing from files",
        "Exponent of the vector size 2^i",
        "Data sent in MB",
        log_y=True,
    )

def plot_network():
    plot_experiment(
        "plots/net_latency.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-inf"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-0_B-inf"]["total_time"], "ltos 0 latency", "ltos"),
            (all_experiments["ltos_fake_network_local_L-50_B-inf"]["total_time"], "ltos 50 latency", "ltos"),
            (all_experiments["ltos_fake_network_local_L-100_B-inf"]["total_time"], "ltos 100 latency", "ltos"),
            (all_experiments["ltos_fake_network_local_L-150_B-inf"]["total_time"], "ltos 150 latency", "ltos"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-inf"]["total_time"], "waks 0 latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-50_B-inf"]["total_time"], "waks 50 latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-100_B-inf"]["total_time"], "waks 100 latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["total_time"], "waks 150 latency"),
        ],
        "Time for simualted network with different bandwidth, preprocessing from files",
        "Exponent of vector size",
        "Time",
        log_y=True,
    )
    plot_experiment(
        "plots/net_latency_div.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-inf"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-150_B-inf"]["total_time"], "ltos 150 latency", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_fake_network_local_L-150_B-inf"]["total_time"], all_experiments["ltos_fake_network_local_L-150_B-inf"]["m"])], "ltos 150 latency / log m", "ltos"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["ltos_fake_network_local_L-150_B-inf"]["total_time"], all_experiments["ltos_fake_network_local_L-150_B-inf"]["m"])], "ltos 150 latency / m", "ltos"),
    	    (all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["total_time"], "waks 150 latency"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["total_time"], all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["m"])], "waks 150 latency / log m"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["total_time"], all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["m"])], "waks 150 latency / m"),
        ],
        "Time for simualted network with different latency, preprocessing from files",
        "Exponent of vector size",
        "Time",
        log_y=True,
    )
    plot_experiment(
        "plots/net_bandwidth.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-inf"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-0_B-inf"]["total_time"], "ltos unlimited", "ltos"),
            (all_experiments["ltos_fake_network_local_L-0_B-100Mbps"]["total_time"], "ltos 100Mbps", "ltos"),
            (all_experiments["ltos_fake_network_local_L-0_B-10Mbps"]["total_time"], "ltos 10Mbps", "ltos"),
            (all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "ltos 1.544Mbps", "ltos"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-inf"]["total_time"], "waks 0_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-100Mbps"]["total_time"], "waks 100Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-10Mbps"]["total_time"], "waks 10Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "waks 1.544Mbps"),
        ],
        "Time for simualted network with different bandwidth preprocessing from files",
        "Exponent of vector size",
        "Time",
        log_y=True,
    )
    plot_experiment(
        "plots/net_bandwidth_div.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "ltos 1.544Mbps", "ltos"),
            ([i[0]/((i[1])) for i in zip(all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["total_time"], all_experiments["ltos_fake_network_local_L-150_B-inf"]["m"])], "ltos 1.544Mbps / log m", "ltos"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["total_time"], all_experiments["ltos_fake_network_local_L-150_B-inf"]["m"])], "ltos 1.544Mbps / m", "ltos"),
            ([i[0]/((i[1]*(2**i[1]))) for i in zip(all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["total_time"], all_experiments["ltos_fake_network_local_L-150_B-inf"]["m"])], "ltos 1.544Mbps / (m log m)", "ltos"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "waks 1.544Mbps"),
            ([i[0]/((i[1])) for i in zip(all_experiments["waksman_based_fake_network_local_L-0_B-1.544Mbps"]["total_time"], all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["m"])], "waks 1.544Mbps / log m"),
            ([i[0]/((2**i[1])) for i in zip(all_experiments["waksman_based_fake_network_local_L-0_B-1.544Mbps"]["total_time"], all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["m"])], "waks 1.544Mbps / m"),
            ([i[0]/((i[1]*(2**i[1]))) for i in zip(all_experiments["waksman_based_fake_network_local_L-0_B-1.544Mbps"]["total_time"], all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["m"])], "waks 1.544Mbps / (m log m)"),
        ],
        "Time for simualted network with different latency, preprocessing from files",
        "Exponent of vector size",
        "Time",
        log_y=True,
    )


def plot_fake_batch():
    plot_experiment(
        "plots/small_batch_fake_m.pdf",
        all_experiments["ltos_batch_fake_5"]["batch_size"],
        [
            (all_experiments["ltos_batch_fake_5"]["rounds"], "ltos_5"),
            (all_experiments["ltos_batch_fake_10"]["rounds"], "ltos_10"),
            (all_experiments["ltos_batch_fake_15"]["rounds"], "ltos_15"),
            (all_experiments["ltos_batch_fake_20"]["rounds"], "ltos_20"),
    	    (all_experiments["mascot_batch_fake_5"]["rounds"], "waks_5"),
    	    (all_experiments["mascot_batch_fake_10"]["rounds"], "waks_10"),
    	    (all_experiments["mascot_batch_fake_15"]["rounds"], "waks_15"),
    	    (all_experiments["mascot_batch_fake_20"]["rounds"], "waks_20"),
        ],
        "Number of rounds when changing batch size, all preprocessing data (triples) is faked",
        "batch size",
        "Number of rounds",
        log_y=True,
    )


def plot_real_batch():
    plot_experiment(
        "plots/batch.pdf",
        all_experiments["ltos_batch_real_3"]["batch_size"],
        [
            (all_experiments["ltos_batch_real_15"]["rounds"], "ltos 15", "ltos"),
            (all_experiments["ltos_batch_real_12"]["rounds"], "ltos 12", "ltos"),
            (all_experiments["ltos_batch_real_9"]["rounds"], "ltos 9", "ltos"),
            (all_experiments["ltos_batch_real_6"]["rounds"], "ltos 6", "ltos"),
    	    (all_experiments["mascot_batch_real_15"]["rounds"], "waks 15"),
    	    (all_experiments["mascot_batch_real_12"]["rounds"], "waks 12"),
    	    (all_experiments["mascot_batch_real_9"]["rounds"], "waks 9"),
    	    (all_experiments["mascot_batch_real_6"]["rounds"], "waks 6"),
        ],
        "Number of rounds when changing batch size with MASCOT preprocessing",
        "Batch size",
        "Number of rounds",
        log_y=True,
    )


plot_real_compare()
plot_fake_compare()
plot_phases()
plot_real_batch()
plot_parties()
plot_network()