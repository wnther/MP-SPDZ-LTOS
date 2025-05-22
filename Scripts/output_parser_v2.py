import re
from pathlib import Path

def parse_output(input_path: Path):
    with open(input_path, 'r') as f:
        content = f.read()

    blocks = content.strip().split('NEW_EXPERIMENT: ')[1:]

    all_results = {}

    for block in blocks:
        experiments = block.split("Using statistical security parameter 40")
        name = experiments.pop(0).strip()
        
        block_results = {
                "n": [],
                "m": [],
                "rounds": [],
                "data_sent": [],
                "total_time": [],
                "time_size_dependent_prep": [],
                "full_online_time": [],
                "online_time_without_verification": [],
                "batch_size": []
            }        

        for experiment in experiments:
            n = re.search(r'n=(\d+)', experiment).group(1)
            m = re.search(r'm=2\^(\d+)', experiment).group(1)
            cpp_times = re.findall(r':\s+(\d+)', experiment)
            
            if len(cpp_times) == 2:
                time_size_dependent_prep, online_time = cpp_times
            elif len(cpp_times) == 3:
                time_size_dependent_prep, time_without_verification, online_time = cpp_times

            full_time = re.search(r'Time\s*=\s*(\d+(?:\.\d+)?)', experiment).group(1)
            rounds = re.search(r'~(\d+)', experiment).group(1)
            data_sent = re.search(r'Data sent\s*=\s*(\d+(?:\.\d+)?)', experiment).group(1)
            batch_size = re.search(r'batch\ssize\s(\d+)', experiment).group(1)
            
            block_results["n"].append(int(n))
            block_results["m"].append(int(m))
            block_results["rounds"].append(int(rounds))
            block_results["data_sent"].append(float(data_sent))
            block_results["total_time"].append(float(full_time))
            block_results["time_size_dependent_prep"].append(float(time_size_dependent_prep))
            block_results["full_online_time"].append(float(online_time))
            block_results["batch_size"].append(int(batch_size))
            

            if len(cpp_times) == 3:
                block_results["online_time_without_verification"].append(float(time_without_verification))

        all_results[name] = block_results

    return all_results