import re
from pathlib import Path
from collections import defaultdict

def parse_terminal_output(input_path: Path):
    experiments = {
        "ltos_real_m": defaultdict(list),
        "ltos_real_n": defaultdict(list),
        "ltos_fake_m": defaultdict(list),
        "ltos_fake_n": defaultdict(list),
        "waksman_real_m": defaultdict(list),
        "waksman_real_n": defaultdict(list),
        "waksman_fake_m": defaultdict(list),
        "waksman_fake_n": defaultdict(list),
    }

    with open(input_path, 'r') as f:
        text = f.read()

    protocol_matches = list(re.finditer(r"running (\w+) with n=(\d+) and m=(\d+)", text))
    cuts = []
    unfiltered_experiments = []
    last_n = 0

    for i, match in enumerate(protocol_matches):
        protocol, n, m_base = match.groups()
        start = match.end()
        end = protocol_matches[i + 1].start() if i + 1 < len(protocol_matches) else len(text)
        chunk = text[start:end]

        times = re.findall(r'Time\s*=\s*(\d+(?:\.\d+)?)', chunk)
        rounds = re.search(r'~(\d+)', chunk).group(1)
        data_sent = re.search(r'Data sent\s*=\s*(\d+(?:\.\d+)?)', chunk).group(1)
        
        fastest_time = min([float(t) for t in times])
        
        unfiltered_experiments.append(
            {"protocol": protocol, "n": n, "m": m_base, "rounds": rounds, "data_sent": data_sent, "total_time": fastest_time}
        )
        
        # Possibly stupid solution but good for now :)
        if int(n) == 3:
            cuts.append(i - 1)
        if int(n) < last_n:
            cuts.append(i)

        last_n = int(n)

    cuts.append(len(unfiltered_experiments))

    start = 0
    experiment_keys = list(experiments.keys())
    for i, k in enumerate(experiment_keys):
        for exp in unfiltered_experiments[start:cuts[i]]:
            for key, value in exp.items():
                experiments[k][key].append(value)
        start = cuts[i]

    return {k: dict(v) for k, v in experiments.items()}
    

def parse_party_output(input_path: Path):
    with open(input_path, 'r') as f:
        content = f.read()

    blocks = content.strip().split('-')

    all_results = []

    for block in blocks:
        block_results = {}
        lines = block.strip().splitlines()

        for line in lines:
            match = re.findall(r'n=(\d+)\s+m=2\^(\d+):\s+(\d+)', line)
            if match:
                n_str, m_exp_str, time_str = match[0]
                n = int(n_str)
                m = int(m_exp_str)
                time = int(time_str)
                key = (n, m)
                if key not in block_results or time < block_results[key]['online_time']:
                    block_results[key] = {'n': n, 'm': m, 'online_time': time}

        all_results.append(list(block_results.values()))

    experiment_keys = [
        "ltos_real_m", "ltos_real_n",
        "ltos_fake_m", "ltos_fake_n",
        "waksman_real_m", "waksman_real_n",
        "waksman_fake_m", "waksman_fake_n"
    ]

    experiments = {k: defaultdict(list) for k in experiment_keys}

    for key, results in zip(experiment_keys, all_results):
        for result in results:
            for field, value in result.items():
                experiments[key][field].append(value)

    experiments = {k: dict(v) for k, v in experiments.items()}

    return experiments

def parse_combined(terminal_output_path: Path, party_output_path: Path):
    terminal = parse_terminal_output(terminal_output_path)
    party = parse_party_output(party_output_path)

    for key in terminal:
        for subkey in party[key]:
            if subkey not in terminal[key]:
                terminal[key][subkey] = party[key][subkey]
    return terminal

parse_combined("SecondRunTerminal.out", "SecondRun.out")