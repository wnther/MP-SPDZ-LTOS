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

    for y_val in y_vals:
        if len(y_val) == 2:
            y_val, name = y_val
            line_type = "solid"
        elif len(y_val) == 3:
            y_val, name, line_type = y_val
        fig.add_trace(go.Scatter(x=x_vals, y=y_val, mode="lines+markers", name=name, line=dict(dash=line_type)))

    
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

def plot_network():
    plot_experiment(
        "plots/latency.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-inf"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-0_B-inf"]["total_time"], "ltos_0_latency"),
            (all_experiments["ltos_fake_network_local_L-50_B-inf"]["total_time"], "ltos_50_latency"),
            (all_experiments["ltos_fake_network_local_L-100_B-inf"]["total_time"], "ltos_100_latency"),
            (all_experiments["ltos_fake_network_local_L-150_B-inf"]["total_time"], "ltos_150_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-inf"]["total_time"], "waksman-based_0_latency", "dot"),
    	    (all_experiments["waksman_based_fake_network_local_L-50_B-inf"]["total_time"], "waksman-based_50_latency", "dot"),
    	    (all_experiments["waksman_based_fake_network_local_L-100_B-inf"]["total_time"], "waksman-based_100_latency", "dot"),
    	    (all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["total_time"], "waksman-based_150_latency", "dot"),
        ],
        "Time for simualted network with different latency, all preprocessing data (triples) is faked",
        "Exponent of vector size",
        "Time",
        log_y=False,
    )
    plot_experiment(
        "plots/latency_log.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-inf"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-0_B-inf"]["total_time"], "ltos_0_latency"),
            (all_experiments["ltos_fake_network_local_L-50_B-inf"]["total_time"], "ltos_50_latency"),
            (all_experiments["ltos_fake_network_local_L-100_B-inf"]["total_time"], "ltos_100_latency"),
            (all_experiments["ltos_fake_network_local_L-150_B-inf"]["total_time"], "ltos_150_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-inf"]["total_time"], "waksman-based_0_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-50_B-inf"]["total_time"], "waksman-based_50_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-100_B-inf"]["total_time"], "waksman-based_100_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-150_B-inf"]["total_time"], "waksman-based_150_latency"),
        ],
        "Time for simualted network with different latency, all preprocessing data (triples) is faked",
        "Exponent of vector size",
        "Time",
        log_y=True,
    )
    plot_experiment(
        "plots/bandwidth.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-inf"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-0_B-inf"]["total_time"], "ltos_unlimited"),
            (all_experiments["ltos_fake_network_local_L-0_B-100Mbps"]["total_time"], "ltos_100Mbps"),
            (all_experiments["ltos_fake_network_local_L-0_B-10Mbps"]["total_time"], "ltos_10Mbps"),
            (all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "ltos_1.544Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-inf"]["total_time"], "waksman-based_0_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-100Mbps"]["total_time"], "waksman-based_100Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-10Mbps"]["total_time"], "waksman-based_10Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "waksman-based_1.544Mbps"),
        ],
        "Time for simualted network with different bandwidth all preprocessing data (triples) is faked",
        "Exponent of vector size",
        "Time",
        log_y=False,
    )
    plot_experiment(
        "plots/bandwidth_log.pdf",
        all_experiments["ltos_fake_network_local_L-0_B-inf"]["m"],
        [
            (all_experiments["ltos_fake_network_local_L-0_B-inf"]["total_time"], "ltos_unlimited"),
            (all_experiments["ltos_fake_network_local_L-0_B-100Mbps"]["total_time"], "ltos_100Mbps"),
            (all_experiments["ltos_fake_network_local_L-0_B-10Mbps"]["total_time"], "ltos_10Mbps"),
            (all_experiments["ltos_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "ltos_1.544Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-inf"]["total_time"], "waksman-based_0_latency"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-100Mbps"]["total_time"], "waksman-based_100Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-10Mbps"]["total_time"], "waksman-based_10Mbps"),
    	    (all_experiments["waksman_based_fake_network_local_L-0_B-1.544Mbps"]["total_time"], "waksman-based_1.544Mbps"),
        ],
        "Time for simualted network with different bandwidth all preprocessing data (triples) is faked",
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
    	    (all_experiments["mascot_batch_fake_5"]["rounds"], "waksman-based_5"),
    	    (all_experiments["mascot_batch_fake_10"]["rounds"], "waksman-based_10"),
    	    (all_experiments["mascot_batch_fake_15"]["rounds"], "waksman-based_15"),
    	    (all_experiments["mascot_batch_fake_20"]["rounds"], "waksman-based_20"),
        ],
        "Number of rounds when changing batch size, all preprocessing data (triples) is faked",
        "batch size",
        "Number of rounds",
        log_y=True,
    )


def plot_real_batch():
    plot_experiment(
        "plots/batch_real_m.pdf",
        all_experiments["ltos_batch_real_3"]["batch_size"],
        [
            (all_experiments["ltos_batch_real_3"]["rounds"], "ltos_3"),
            (all_experiments["ltos_batch_real_6"]["rounds"], "ltos_6"),
            (all_experiments["ltos_batch_real_9"]["rounds"], "ltos_9"),
            (all_experiments["ltos_batch_real_12"]["rounds"], "ltos_12"),
            (all_experiments["ltos_batch_real_15"]["rounds"], "ltos_15"),
    	    (all_experiments["mascot_batch_real_3"]["rounds"], "waksman-based_3"),
    	    (all_experiments["mascot_batch_real_6"]["rounds"], "waksman-based_6"),
    	    (all_experiments["mascot_batch_real_9"]["rounds"], "waksman-based_9"),
    	    (all_experiments["mascot_batch_real_12"]["rounds"], "waksman-based_12"),
    	    (all_experiments["mascot_batch_real_15"]["rounds"], "waksman-based_15"),
        ],
        "Number of rounds when changing batch size with MASCOT preprocessing",
        "batch size",
        "Number of rounds ",
        log_y=True,
    )

def plot_fake_compare():
    plot_experiment(
        "plots/compare_m_fake_time_log.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["total_time"], "ltos"),
            (all_experiments["waksman_based_fake"]["total_time"], "waksman based"),
        ],
        "Time comparison where all preprocessing data (triples) is faked",
        "exponent of vector_size",
        "Total time in seconds",
        log_y=True,
    )

    plot_experiment(
        "plots/compare_m_time_fake.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["total_time"], "ltos"),
            (all_experiments["waksman_based_fake"]["total_time"], "waksman based"),
        ],
        "Time comparison where all preprocessing data (triples) is faked",
        "exponent of vector_size",
        "Total time in seconds",
        log_y=False,
    )
    plot_experiment(
        "plots/compare_m_fake_rounds_log.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["rounds"], "ltos"),
            (all_experiments["waksman_based_fake"]["rounds"], "waksman based"),
        ],
        "Rounds comparison where triples are read from files",
        "Exponent of vector_size",
        "Number of rounds",
        log_y=True,
    )
    plot_experiment(
        "plots/compare_m_rounds_fake.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["rounds"], "ltos"),
            (all_experiments["waksman_based_fake"]["rounds"], "waksman based"),
        ],
        "Rounds comparison where triples are read from files",
        "Exponent of vector_size",
        "Number of rounds",
        log_y=False,
    )
    plot_experiment(
        "plots/compare_m_rounds_fake_DIVIDED_by_m.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            ([i[0]/(2**i[1]) for i in zip(all_experiments["ltos_fake"]["rounds"], all_experiments["ltos_fake"]["m"])], "ltos"),
            ([i[0]/(2**i[1]) for i in zip(all_experiments["waksman_based_fake"]["rounds"], all_experiments["waksman_based_fake"]["m"])], "waksman based"),
        ],
        "Rounds comparison where triples are read from files",
        "Exponent of vector_size",
        "Number of rounds divided by m",
        log_y=False,
    )
    plot_experiment(
        "plots/compare_m_fake_global_data_sent_log.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["global_data_sent"], "ltos"),
            (all_experiments["waksman_based_fake"]["global_data_sent"], "waksman based"),
        ],
        "Global data sent comparison where triples are read from files",
        "Exponent of vector_size",
        "Global data sent in MB",
        log_y=True,
    )
    plot_experiment(
        "plots/compare_m_global_data_sent_fake.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            (all_experiments["ltos_fake"]["global_data_sent"], "ltos"),
            (all_experiments["waksman_based_fake"]["global_data_sent"], "waksman based"),
        ],
        "Global data sent comparison where triples are read from files",
        "Exponent of vector_size",
        "Global data sent in MB",
        log_y=False,
    )

def plot_real_compare():
    plot_experiment(
        "plots/compare_m_real_log.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_real"]["total_time"], "ltos"),
            (all_experiments["waksman_based_real"]["total_time"], "waksman based"),
        ],
        "Time comparison with all preprocessing triples as in MASCOT",
        "exponent of vector_size",
        "Total time in seconds",
        log_y=True,
    )

    plot_experiment(
        "plots/compare_real_m.pdf",
        all_experiments["ltos_real"]["m"],
        [
            (all_experiments["ltos_real"]["total_time"], "ltos"),
            (all_experiments["waksman_based_real"]["total_time"], "waksman based"),
        ],
        "Time comparison with all preprocessing triples as in MASCOT",
        "exponent of vector_size",
        "Total time in seconds",
        log_y=False,
    )

def compare_verification():
    plot_experiment(
        "plots/ltos_fake_verification_log.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            ([i*1000000 for i in all_experiments["ltos_fake"]["total_time"]], "Total time of everything (μs)"), #total time is in seconds
            (all_experiments["ltos_fake"]["full_online_time"], "Total online phase time (μs)"),
            (all_experiments["ltos_fake"]["time_size_dependent_prep"], "Size dependent preprocessing time (μs)"),
            (all_experiments["ltos_fake"]["online_time_without_verification"], "Online phase time but without the verification step (μs)"),
        ],
        "Time benchmarks of the different phases for ltos with faked triples",
        "Exponent of vector_size",
        "Total time in microseconds (μs), ",
        log_y=True,
    )
    plot_experiment(
        "plots/ltos_fake_verification.pdf",
        all_experiments["ltos_fake"]["m"],
        [
            ([i*1000000 for i in all_experiments["ltos_fake"]["total_time"]], "Total time of everything (μs)"), #total time is in seconds
            #(all_experiments["ltos_fake"]["time_size_dependent_prep"], "Size dependent preprocessing time (μs)"),
            (all_experiments["ltos_fake"]["full_online_time"], "Total online phase time (μs)"),
            (all_experiments["ltos_fake"]["online_time_without_verification"], "Online phase time but without the verification step (μs)"),
        ],
        "Time benchmarks of the different phases for ltos with faked triples",
        "exponent of vector_size",
        "Total time in microseconds, except total time which is in seconds",
        log_y=False,
    )

def plot_parties():
    plot_experiment(
        "plots/parties_fake.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties"]["total_time"], "ltos"),
            (all_experiments["waksman_based_fake_parties"]["total_time"], "waksman based"),
        ],
        "Time comparison with different number of parties for m=2^12, all preprocessing data (triples) is faked",
        "Number of parties",
        "Total time in seconds",
        log_y=False,
    )
    plot_experiment(
        "plots/parties_fake_log.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties"]["total_time"], "ltos"),
            (all_experiments["waksman_based_fake_parties"]["total_time"], "waksman based"),
        ],
        "Time comparison with different number of parties for m=2^12, all preprocessing data (triples) is faked",
        "Number of parties",
        "Total time in seconds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_fake_log_rounds.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties"]["rounds"], "ltos","dot"),
            ([i[0]/i[1] for i in zip(all_experiments["ltos_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "ltos divided by n","dot"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "ltos divided by n^2","dot"),
            (all_experiments["waksman_based_fake_parties"]["rounds"], "waksman based"),
            ([i[0]/i[1] for i in zip(all_experiments["waksman_based_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "waksman based divided by n"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties"]["rounds"], all_experiments["ltos_fake_parties"]["n"])], "waksman based divided by n^2"),
        ],
        "Rounds comparison with different number of parties for m=2^12, all preprocessing data (triples) is faked",
        "Number of parties",
        "Number of rounds",
        log_y=True,
    )
    plot_experiment(
        "plots/parties_fake_log_data.pdf",
        all_experiments["ltos_fake_parties"]["n"],
        [
            (all_experiments["ltos_fake_parties"]["global_data_sent"], "ltos","dot"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["ltos_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "ltos divided by n^2","dot"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["ltos_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "ltos divided by n^3","dot"),
            (all_experiments["waksman_based_fake_parties"]["global_data_sent"], "waksman based"),
            ([i[0]/i[1]**2 for i in zip(all_experiments["waksman_based_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "waksman based divided by n^2"),
            ([i[0]/i[1]**3 for i in zip(all_experiments["waksman_based_fake_parties"]["global_data_sent"], all_experiments["ltos_fake_parties"]["n"])], "waksman based divided by n^3"),
        ],
        "Global Data sent comparison with different number of parties for m=2^12, all preprocessing data (triples) is faked",
        "Number of parties",
        "Total data sent in MB",
        log_y=True,
    )

    plot_experiment(
        "plots/parties_real.pdf",
        all_experiments["ltos_real_parties"]["n"],
        [
            (all_experiments["ltos_real_parties"]["total_time"], "ltos"),
            (all_experiments["waksman_based_real_parties"]["total_time"], "waksman based"),
        ],
        "Time comparison with different number of parties for m=2^12, all preprocessing triples as in MASCOT",
        "Number of parties",
        "Total time in seconds",
        log_y=False,
    )
    plot_experiment(
        "plots/parties_real_log.pdf",
        all_experiments["ltos_real_parties"]["n"],
        [
            (all_experiments["ltos_real_parties"]["total_time"], "ltos"),
            (all_experiments["waksman_based_real_parties"]["total_time"], "waksman based"),
        ],
        "Time comparison with different number of parties for m=2^12, all preprocessing triples as in MASCOT",
        "Number of parties",
        "Total time in seconds",
        log_y=True,
    )

plot_fake_batch()
plot_real_batch()
plot_fake_compare()
plot_real_compare()
plot_network()
compare_verification()
plot_parties()