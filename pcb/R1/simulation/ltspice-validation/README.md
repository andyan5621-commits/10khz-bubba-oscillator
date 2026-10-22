# LTspice validation workspace

This directory contains an exact working copy of the recovered Desktop
`Oscillator_Final.asc` and the accompanying OPA1656 symbol/model and 1N4148
model. The source copy itself was not edited.

On 2026-10-22, LTspice 26.0.2.1 was found at
`C:\Users\20252928\AppData\Local\Programs\ADI\LTspice\LTspice.exe`.
Two batch invocations of the schematic returned exit code 0 but created no
`.net`, `.log`, or `.raw` file. No fresh numerical result is claimed from those
attempts. The archived generated netlist and archived measurements are assessed
in `reports/circuit-validation.md`.

