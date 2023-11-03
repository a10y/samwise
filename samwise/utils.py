from subprocess import Popen, PIPE

import re

INET_ADDR_PAT = r"inet ([\d]+\.[\d]+\.[\d]+\.[\d]+)[^d]"

def get_tailscale_ip() -> str:
    proc = Popen(["ifconfig", "tailscale0"], stdout=PIPE)
    proc.wait(timeout=2.0)
    for line in proc.stdout.readlines():
        matches = re.findall(INET_ADDR_PAT, str(line))
        if len(matches) == 0:
            continue
        return matches[0]
    raise ValueError("No inet4 address found for tailscale0 iface")
