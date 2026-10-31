#!/usr/bin/env python3
"""Give every pad in the KiCad PCB that has no net its own custom net.

Usage: python3 label_pads.py [path/to/board.kicad_pcb]
"""

import re
import sys

DEFAULT_PCB = "ClapDetectorPCB.kicad_pcb"
LABEL_PREFIX = "CUSTOM"


def main():
    pcb = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PCB
    with open(pcb, "r", encoding="utf-8") as f:
        lines = f.readlines()

    ref_re = re.compile(r'\(property "Reference" "([^"]+)"')
    pad_re = re.compile(r'\(pad "([^"]*)"')
    closing_re = re.compile(r"^\t*\)\s*$")

    current_ref = "UNKNOWN"
    labeled = 0
    counter = 0
    in_pad = False
    pad_num = ""
    has_net = False
    layers_idx = -1

    for i, line in enumerate(lines):
        if not in_pad:
            m = ref_re.search(line)
            if m:
                current_ref = m.group(1)
            m = pad_re.match(line.strip())
            if m:
                in_pad = True
                pad_num = m.group(1)
                has_net = False
                layers_idx = -1
        else:
            if "(net " in line:
                has_net = True
            if "(layers " in line and layers_idx == -1:
                layers_idx = i
            if closing_re.match(line):
                if not has_net:
                    if pad_num == "":
                        pad_num = f"pad{i}"
                    counter += 1
                    # Global counter keeps net names unique even when two
                    # footprints share the same reference designator.
                    net_name = f"{LABEL_PREFIX}_{current_ref}-{pad_num}_{counter}"
                    insert_at = layers_idx + 1 if layers_idx != -1 else i
                    lines.insert(insert_at, f'\t\t\t(net "{net_name}")\n')
                    labeled += 1
                    i += 1
                in_pad = False

    with open(pcb, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Added custom nets to {labeled} pad(s) in {pcb}")


if __name__ == "__main__":
    main()
