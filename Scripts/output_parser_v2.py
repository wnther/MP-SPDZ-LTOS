import re

with open('SecondRunTerminal.out') as f:
    text = f.read()

protocol_matches = list(re.finditer(r'running (\w+) with n=(\d+) and m=(\d+)', text))

with open('grouped_data.out', 'w') as f:
    for i, match in enumerate(protocol_matches):
        proto_name, n, m_base = match.groups()
        start = match.end()
        end = protocol_matches[i + 1].start() if i + 1 < len(protocol_matches) else len(text)
        chunk = text[start:end]

        rounds = re.findall(r'~(\d+)', chunk)
        times = re.findall(r'Time\s*=\s*(\d+(?:\.\d+)?)', chunk)
        times = [float(t) for t in times]

        f.write(f"{proto_name}, n={n}, m={m_base}\n")
        for r, t in zip(rounds, times):
            f.write(f"{r},{t}\n")
        f.write("\n")  # optional spacer between groups