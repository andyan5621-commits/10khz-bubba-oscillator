# Resistor network build sheet

Board revision: ______  Date: ______  DMM / range: ______

The PCB uses unique physical references. Original circuit names below refer to the LTspice/prototype logical values; they are not all printed as single component references on the PCB. All 44 physical resistors are fitted. The per-component BOM is authoritative for the MPN at each reference.

| Original circuit element | PCB references, in circuit sequence | Values in the same sequence | Nominal equivalent | Measured / checked |
|---|---|---|---:|---|
| R1 | R101, R102, R103, R104 | 1 kΩ, 330 Ω, 270 Ω, 47 Ω; series | 1,647 Ω | ______ |
| R2 | R201, R202, R203, R204 | 1 kΩ, 330 Ω, 270 Ω, 47 Ω; series | 1,647 Ω | ______ |
| R3 | R301, R302, R303, R304 | 1 kΩ, 330 Ω, 270 Ω, 47 Ω; series | 1,647 Ω | ______ |
| R4 | R401, R402, R403, R404 | 1 kΩ, 330 Ω, 270 Ω, 47 Ω; series | 1,647 Ω | ______ |
| RG | R13 | 10 kΩ | 10,000 Ω | ______ |
| RF | R14, R15 | 47 kΩ, 1 kΩ; series | 48,000 Ω | ______ |
| R5 | R501, R502, R503 | 100 kΩ, 20 kΩ, 10 kΩ; series | 130,000 Ω | ______ |
| R6 | R601, R602, R603, R604, R605 | 300 kΩ, 20 kΩ, 4.7 kΩ, 200 Ω, 100 Ω; series | 325,000 Ω | ______ |
| R7 | R701, R702, R703 | 100 kΩ, 20 kΩ, 10 kΩ; series | 130,000 Ω | ______ |
| R8 | R801, R802, R803, R804, R805 | 300 kΩ, 20 kΩ, 4.7 kΩ, 200 Ω, 100 Ω; series | 325,000 Ω | ______ |
| R9 | R901, R902, R903 | 1 kΩ, 680 Ω, 220 Ω; series | 1,900 Ω | ______ |
| R10 | R1001, R1002, R1003 | 1 kΩ, 680 Ω, 220 Ω; series | 1,900 Ω | ______ |
| R11 | R11 and R16 | 2 kΩ and 100 kΩ; parallel | 1,960.784 Ω | ______ |
| R12 | R12 | 1 kΩ | 1,000 Ω | ______ |

Check individual values before fitting. Do not use an in-circuit resistance reading as a component acceptance measurement when other paths load it. Isolate a suitable end or compare individual measured values mathematically. Never measure resistance on a powered board.

The selected resistors are 0.1%, 25 ppm/°C parts. The component tolerance does not include DMM uncertainty or whole-oscillator frequency tolerance. Record actual measurements rather than trimming or substituting values to match the nominal sums.
