import re

file = open('SecondRunTerminal.out', 'r')
text = file.read()
file.close()

rounds = re.findall(r'~(\d+)', text)
times = re.findall(r'Time\s*=\s*(\d+(?:\.\d+)?)', text)
times = [float(t) for t in times]

rounds_and_times = list(zip(rounds, times))
rounds_and_times_str = [str(t) for t in rounds_and_times]
file = open('rounds_and_times.out', 'w')
file.write("\n".join(rounds_and_times_str))
file.close()

protocol_n_m = re.findall(r'running (\w+) with n=(\d+) and m=(\d+)', text)
protocol_n_m_str = [str(t) for t in protocol_n_m]
file = open('protocol_n_m.out', 'w')
file.write("\n".join(protocol_n_m_str))
file.close()