"""Generate the recovered oscillator as a self-contained KiCad 9 schematic.

The authoritative output is ``oscillator.kicad_sch``.  A legacy ``.sch`` is
also emitted only as a human-readable compatibility reference.  The generated
source is deterministic so connectivity can be compared with the recovered
LTspice netlist.
"""

from pathlib import Path
import uuid


OUT = Path(__file__).with_name("oscillator.sch")
MODERN_OUT = Path(__file__).with_name("oscillator.kicad_sch")


class Sch:
    def __init__(self):
        self.components = []
        self.labels = []
        self.notes = []
        self.wires = []
        self.lines = [
            "EESchema Schematic File Version 4",
            "LIBS:oscillator-cache",
            "EELAYER 29 0",
            "EELAYER END",
            "$Descr A3 16535 11693",
            'Sheet 1 1',
            'Title "10 kHz Bubba Oscillator and Output Filter"',
            'Date "2026-10-22"',
            'Rev "R1 REVIEW"',
            'Comp "Project Oscillator PCB"',
            'Comment1 "Reference R0 preserved; Gate B passed; fabrication release pending"',
            'Comment2 "OPA1656IDR pinout verified against TI OPA165x Rev C datasheet"',
            'Comment3 "77 parts; footprints reviewed; final board/export audit pending"',
            'Comment4 "External rails: +15 V / GND / -15 V"',
            "$EndDescr",
        ]
        self.uid = 0x69000000

    def comp(self, lib, ref, value, x, y, unit=1, orient=(1, 0, 0, -1), footprint="", fields=None):
        self.uid += 1
        a, b, c, d = orient
        self.lines += [
            "$Comp",
            f"L {lib} {ref}",
            f"U {unit} 1 {self.uid:08X}",
            f"P {x} {y}",
            f'F 0 "{ref}" H {x+150} {y+100} 50  0000 C CNN',
            f'F 1 "{value}" H {x+200} {y-100} 50  0000 C CNN',
            f'F 2 "{footprint}" H {x} {y} 50  0001 C CNN',
            'F 3 "" H {0} {1} 50  0001 C CNN'.format(x, y),
        ]
        for idx, (name, val) in enumerate((fields or {}).items(), start=4):
            self.lines.append(f'F {idx} "{val}" H {x} {y} 50  0001 C CNN "{name}"')
        self.lines += [f"\t1    {x} {y}", f"\t{a}    {b}    {c}    {d}", "$EndComp"]
        self.components.append((lib, ref, value, x, y, unit, footprint, dict(fields or {})))

    def label(self, x, y, name):
        if name is None:
            return
        self.lines += [f"Text Label {x} {y} 0    40   ~ 0", name]
        self.labels.append((x, y, name))

    def wire(self, x1, y1, x2, y2):
        self.lines += [f"Wire Wire Line", f"\t{x1} {y1} {x2} {y2}"]
        self.wires.append((x1, y1, x2, y2))

    def note(self, x, y, text, size=60):
        self.lines += [f"Text Notes {x} {y} 0    {size}   ~ 0", text]
        self.notes.append((x, y, text, size))

    def opamp(self, ref, unit, x, y, plus, minus, out, role):
        self.comp(
            "OPA1656ID", ref, "OPA1656IDR", x, y,
            unit=unit, footprint=("Oscillator:SOIC-8_3.9x4.9mm_P1.27mm_RoutedSilk" if ref == "U3" else "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"),
            fields={"Role": role, "MPN": "OPA1656IDR"},
        )
        self.label(x - 300, y + 100, plus)
        self.label(x - 300, y - 100, minus)
        self.label(x + 300, y, out)

    def power_unit(self, ref, x, y):
        self.comp(
            "OPA1656ID", ref, "OPA1656IDR", x, y,
            unit=3, footprint=("Oscillator:SOIC-8_3.9x4.9mm_P1.27mm_RoutedSilk" if ref == "U3" else "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"),
            fields={"MPN": "OPA1656IDR"},
        )
        self.label(x - 100, y - 300, "+15V")
        self.label(x - 100, y + 300, "-15V")

    def resistor(self, ref, value, x, y, left, right, role="", build=""):
        fields = {"FunctionalName": role}
        if build:
            fields["PrototypeBuild"] = build
        self.comp("R", ref, value, x, y,
                  footprint="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder",
                  fields=fields)
        self.label(x - 100, y, left)
        self.label(x + 100, y, right)

    def cap(self, ref, value, x, y, top, bottom, tech, mpn=""):
        fields = {"Technology": tech}
        if mpn:
            fields["MPN"] = mpn
        footprints = {
            "MKP1837310011": "Oscillator:C_Vishay_MKP1837310011_P5",
            "SR215A102FARTR1": "Oscillator:C_AVX_SR215A102FARTR1_P5.08",
            "MKP1837368011": "Oscillator:C_Vishay_MKP1837368011_P5",
            "C315C104K5R5TA": "Oscillator:C_KEMET_C315C104K5R5TA_P2.54",
        }
        self.comp("C", ref, value, x, y, orient=(1, 0, 0, -1),
                  footprint=("Oscillator:C_KEMET_C315_P2.54_RoutedSilk" if ref == "C7" else footprints.get(mpn, "")), fields=fields)
        self.label(x, y - 100, top)
        self.label(x, y + 100, bottom)

    def diode(self, ref, x, y, anode, cathode):
        self.comp("D_Small", ref, "1N4148", x, y,
                  footprint="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",
                  fields={"MPN": "1N4148", "Manufacturer": "onsemi", "Package": "DO-35"})
        # Default horizontal Device:D_Small has pin 2 (A) left, pin 1 (K) right.
        self.label(x - 100, y, anode)
        self.label(x + 100, y, cathode)

    def testpoint(self, ref, x, y, net):
        self.comp("TestPoint", ref, net, x, y,
                  footprint="TestPoint:TestPoint_Pad_D1.5mm",
                  fields={"Role": "1.5 mm circular probe pad"})
        self.label(x - 100, y, net)

    def finish(self):
        self.lines += ["$EndSCHEMATC", ""]
        OUT.write_text("\n".join(self.lines), encoding="utf-8")
        self.write_modern()

    @staticmethod
    def _q(value):
        return str(value).replace("\\", "\\\\").replace('"', '\\"')

    def write_modern(self):
        """Write a self-contained KiCad 9 schematic with embedded symbols."""
        ns = uuid.UUID("bc5e3d9a-9f75-4700-8aaa-29d8cc5d8f02")
        root = str(uuid.uuid5(ns, "root"))
        uid = lambda key: str(uuid.uuid5(ns, key))
        m = lambda v: v * 0.0254
        q = self._q
        lines = [
            '(kicad_sch (version 20231120) (generator eeschema)',
            f'  (uuid {root})',
            '  (paper "A3")',
            '  (title_block',
            '    (title "10 kHz Bubba Oscillator and Output Filter")',
            '    (date "2026-10-22")',
            '    (rev "R1 REVIEW")',
            '    (company "Project Oscillator PCB")',
            '    (comment 1 "Reference R0 preserved; Gate B passed; fabrication release pending")',
            '    (comment 2 "OPA1656IDR pinout verified against TI OPA165x Rev C datasheet")',
            '    (comment 3 "77 parts; footprints reviewed; final board/export audit pending")',
            '  )',
            '  (lib_symbols',
            '''    (symbol "Oscillator:R" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 0 2.032 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 -2.032 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_0_1" (rectangle (start -1.27 -1.016) (end 1.27 1.016) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "R_1_1"
        (pin passive line (at -2.54 0 0) (length 1.27) (name "~" (effects (font (size 0.508 0.508)))) (number "1" (effects (font (size 0.508 0.508)))))
        (pin passive line (at 2.54 0 180) (length 1.27) (name "~" (effects (font (size 0.508 0.508)))) (number "2" (effects (font (size 0.508 0.508)))))
      )
    )''',
            '''    (symbol "Oscillator:C" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at -2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_0_1"
        (polyline (pts (xy -1.27 -0.508) (xy 1.27 -0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.27 0.508) (xy 1.27 0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "C_1_1"
        (pin passive line (at 0 2.54 270) (length 2.032) (name "~" (effects (font (size 0.508 0.508)))) (number "1" (effects (font (size 0.508 0.508)))))
        (pin passive line (at 0 -2.54 90) (length 2.032) (name "~" (effects (font (size 0.508 0.508)))) (number "2" (effects (font (size 0.508 0.508)))))
      )
    )''',
            '''    (symbol "Oscillator:C_Polarized" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "C_Polarized" (at -2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_Polarized_0_1"
        (polyline (pts (xy -1.27 -0.508) (xy 1.27 -0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.27 0.508) (xy 1.27 0.508)) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "C_Polarized_1_1"
        (pin passive line (at 0 2.54 270) (length 2.032) (name "+" (effects (font (size 0.508 0.508)))) (number "1" (effects (font (size 0.508 0.508)))))
        (pin passive line (at 0 -2.54 90) (length 2.032) (name "-" (effects (font (size 0.508 0.508)))) (number "2" (effects (font (size 0.508 0.508)))))
      )
    )''',
            '''    (symbol "Oscillator:D_Small" (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 0 2.032 0) (effects (font (size 1.27 1.27))))
      (property "Value" "D_Small" (at 0 -2.032 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "D_Small_0_1"
        (polyline (pts (xy 0.635 -1.27) (xy 0.635 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -0.635 -1.27) (xy -0.635 1.27) (xy 0.635 0) (xy -0.635 -1.27)) (stroke (width 0) (type default)) (fill (type outline)))
      )
      (symbol "D_Small_1_1"
        (pin passive line (at 2.54 0 180) (length 1.905) (name "K" (effects (font (size 0.508 0.508)))) (number "1" (effects (font (size 0.508 0.508)))))
        (pin passive line (at -2.54 0 0) (length 1.905) (name "A" (effects (font (size 0.508 0.508)))) (number "2" (effects (font (size 0.508 0.508)))))
      )
    )''',
            '''    (symbol "Oscillator:OPA1656ID" (pin_names (offset 0.127)) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Value" "OPA1656ID" (at 0 -5.08 0) (effects (font (size 1.27 1.27)) (justify left)))
      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "https://www.ti.com/lit/ds/symlink/opa1656.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "OPA1656ID_1_1"
        (polyline (pts (xy -5.08 5.08) (xy 5.08 0) (xy -5.08 -5.08) (xy -5.08 5.08)) (stroke (width 0.254) (type default)) (fill (type background)))
        (pin input line (at -7.62 -2.54 0) (length 2.54) (name "+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 2.54 0) (length 2.54) (name "-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      )
      (symbol "OPA1656ID_2_1"
        (polyline (pts (xy -5.08 5.08) (xy 5.08 0) (xy -5.08 -5.08) (xy -5.08 5.08)) (stroke (width 0.254) (type default)) (fill (type background)))
        (pin input line (at -7.62 -2.54 0) (length 2.54) (name "+" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 2.54 0) (length 2.54) (name "-" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
      )
      (symbol "OPA1656ID_3_1"
        (pin power_in line (at -2.54 7.62 270) (length 3.81) (name "V+" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -2.54 -7.62 90) (length 3.81) (name "V-" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
      )
    )''',
            '''    (symbol "Oscillator:Conn_01x02" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 2.54 1.27 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_01x02" (at 2.54 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_01x02_1_1"
        (rectangle (start 0 -2.54) (end 1.905 2.54) (stroke (width 0.254) (type default)) (fill (type background)))
        (pin passive line (at -2.54 1.27 0) (length 2.54) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -2.54 -1.27 0) (length 2.54) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )''',
            '''    (symbol "Oscillator:Conn_01x03" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 2.54 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_01x03" (at 2.54 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Conn_01x03_1_1"
        (rectangle (start 0 -3.81) (end 1.905 3.81) (stroke (width 0.254) (type default)) (fill (type background)))
        (pin power_out line (at -2.54 2.54 0) (length 2.54) (name "Pin_1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin power_out line (at -2.54 0 0) (length 2.54) (name "Pin_2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin power_out line (at -2.54 -2.54 0) (length 2.54) (name "Pin_3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
      )
    )''',
            '''    (symbol "Oscillator:R_Potentiometer" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "RV" (at -4.445 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R_Potentiometer" (at -2.54 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_Potentiometer_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "R_Potentiometer_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 0 180) (length 1.27) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "3" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
      )
    )''',
            '''    (symbol "Oscillator:TestPoint" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "TP" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "TestPoint" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 2.54 0 90) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 2.54 0 90) (effects (font (size 1.27 1.27)) hide))
      (symbol "TestPoint_0_1"
        (circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "TestPoint_1_1"
        (pin passive line (at -2.54 0 0) (length 1.27) (name "1" (effects (font (size 0.508 0.508)))) (number "1" (effects (font (size 0.508 0.508)))))
      )
    )''',
            '  )',
        ]

        # Keep the project library synchronized with the embedded symbol
        # definitions so ERC can compare symbols without relying on a global
        # KiCad installation or user configuration.
        embedded_defs = lines[lines.index('  (lib_symbols') + 1:-1]
        library_defs = [entry.replace('(symbol "Oscillator:', '(symbol "', 1) for entry in embedded_defs]
        library_text = [
            '(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)',
            *library_defs,
            ')',
            '',
        ]
        Path(__file__).with_name('Oscillator.kicad_sym').write_text("\n".join(library_text), encoding='utf-8')

        # Place labels beyond short wire stubs.  This keeps net names away from
        # symbol bodies while preserving explicit, reviewable attachment.
        anchors = {}
        for lib, _ref, _value, x, y, unit, _footprint, _fields in self.components:
            if lib in ("R", "D_Small"):
                anchors[(x - 100, y)] = (-1, 0)
                anchors[(x + 100, y)] = (1, 0)
            elif lib in ("C", "C_Polarized"):
                anchors[(x, y - 100)] = (0, -1)
                anchors[(x, y + 100)] = (0, 1)
            elif lib == "OPA1656ID" and unit in (1, 2):
                anchors[(x - 300, y + 100)] = (-1, 0)
                anchors[(x - 300, y - 100)] = (-1, 0)
                anchors[(x + 300, y)] = (1, 0)
            elif lib == "OPA1656ID" and unit == 3:
                anchors[(x - 100, y - 300)] = (0, -1)
                anchors[(x - 100, y + 300)] = (0, 1)
            elif lib == "Conn_01x02":
                anchors[(x - 100, y - 50)] = (-1, 0)
                anchors[(x - 100, y + 50)] = (-1, 0)
            elif lib == "Conn_01x03":
                for yy in (y - 100, y, y + 100):
                    anchors[(x - 100, yy)] = (-1, 0)
            elif lib == "R_Potentiometer":
                anchors[(x, y - 150)] = (0, -1)
                anchors[(x + 150, y)] = (1, 0)
                anchors[(x, y + 150)] = (0, 1)
            elif lib == "TestPoint":
                anchors[(x - 100, y)] = (-1, 0)

        rendered_labels = []
        stub_wires = []
        for x, y, name in self.labels:
            dx, dy = anchors.get((x, y), (0, 0))
            if dx or dy:
                lx, ly = x + dx * 150, y + dy * 150
                stub_wires.append((x, y, lx, ly))
            else:
                lx, ly = x, y
            rendered_labels.append((lx, ly, name, 'right' if dx < 0 else 'left'))

        for i, (x1, y1, x2, y2) in enumerate([*self.wires, *stub_wires]):
            lines += [
                f'  (wire (pts (xy {m(x1):.4f} {m(y1):.4f}) (xy {m(x2):.4f} {m(y2):.4f}))',
                '    (stroke (width 0) (type solid))',
                f'    (uuid {uid(f"wire-{i}-{x1}-{y1}-{x2}-{y2}")})',
                '  )',
            ]

        for i, (x, y, name, justification) in enumerate(rendered_labels):
            lines += [
                f'  (label "{q(name)}" (at {m(x):.4f} {m(y):.4f} 0)',
                f'    (effects (font (size 1.016 1.016)) (justify {justification} bottom))',
                f'    (uuid {uid(f"label-{i}-{x}-{y}-{name}")})',
                '  )',
            ]
        for i, (x, y, text, size) in enumerate(self.notes):
            lines += [
                f'  (text "{q(text)}" (at {m(x):.4f} {m(y):.4f} 0)',
                f'    (effects (font (size {max(1.0, m(size)):.4f} {max(1.0, m(size)):.4f})) (justify left bottom))',
                f'    (uuid {uid(f"note-{i}-{text}")})',
                '  )',
            ]

        pin_map = {
            "R": {1: ("1", "2")}, "C": {1: ("1", "2")},
            "C_Polarized": {1: ("1", "2")}, "D_Small": {1: ("1", "2")},
            "Conn_01x02": {1: ("1", "2")}, "Conn_01x03": {1: ("1", "2", "3")},
            "R_Potentiometer": {1: ("1", "2", "3")},
            "TestPoint": {1: ("1",)},
            "OPA1656ID": {1: ("1", "2", "3"), 2: ("5", "6", "7"), 3: ("4", "8")},
        }
        for i, (lib, ref, value, x, y, unit, footprint, fields) in enumerate(self.components):
            sid = uid(f"symbol-{i}-{ref}-{unit}")
            if lib == "OPA1656ID" and unit in (1, 2):
                rx, ry, vx, vy = x - 100, y - 300, x - 100, y + 300
            elif lib == "OPA1656ID":
                rx, ry, vx, vy = x + 150, y - 100, x + 150, y + 100
            elif lib in ("R", "D_Small"):
                rx, ry, vx, vy = x, y - 110, x, y + 110
            elif lib in ("C", "C_Polarized"):
                rx, ry, vx, vy = x + 100, y - 80, x + 100, y + 80
            else:
                rx, ry, vx, vy = x + 150, y - 150, x + 150, y + 150
            lines += [
                f'  (symbol (lib_id "Oscillator:{lib}") (at {m(x):.4f} {m(y):.4f} 0) (unit {unit})',
                f'    (in_bom {"no" if lib == "TestPoint" else "yes"}) (on_board yes) (dnp no)',
                f'    (uuid {sid})',
                f'    (property "Reference" "{q(ref)}" (at {m(rx):.4f} {m(ry):.4f} 0) (effects (font (size 1.016 1.016))))',
                f'    (property "Value" "{q(value)}" (at {m(vx):.4f} {m(vy):.4f} 0) (effects (font (size 1.016 1.016)){" hide" if lib == "TestPoint" else ""}))',
                f'    (property "Footprint" "{q(footprint)}" (at {m(x):.4f} {m(y):.4f} 0) (effects (font (size 1.27 1.27)) hide))',
                f'    (property "Datasheet" "~" (at {m(x):.4f} {m(y):.4f} 0) (effects (font (size 1.27 1.27)) hide))',
            ]
            for fname, fval in fields.items():
                lines.append(f'    (property "{q(fname)}" "{q(fval)}" (at {m(x):.4f} {m(y):.4f} 0) (effects (font (size 1.27 1.27)) hide))')
            for p in pin_map[lib][unit]:
                lines.append(f'    (pin "{p}" (uuid {uid(f"pin-{i}-{p}")}))')
            lines += [
                '    (instances',
                '      (project "oscillator"',
                f'        (path "/{root}" (reference "{q(ref)}") (unit {unit}))',
                '      )',
                '    )',
                '  )',
            ]
        lines += ['  (sheet_instances (path "/" (page "1")))', ')', '']
        MODERN_OUT.write_text("\n".join(lines), encoding="utf-8")


s = Sch()
s.note(600, 400, "10 kHz BUBBA OSCILLATOR — recovered electrical baseline", 80)

# Gain stage and nonlinear limiter.  Series elements are physically wired on
# the page; only functional net boundaries retain labels.
s.opamp("U1", 1, 1700, 1700, "GND", None, None, "Oscillator gain / nonlinear amplitude control")
s.resistor("R14", "47k", 1500, 900, None, None, "RF part 1", "47k + 1k series = 48k")
s.resistor("R15", "1k", 1800, 900, None, None, "RF part 2", "47k + 1k series = 48k")
s.wire(1600, 900, 1700, 900)
s.wire(1400, 900, 1400, 1600)
s.label(1400, 900, "N_INV")
s.wire(1900, 900, 2000, 900); s.wire(2000, 900, 2000, 1700)
s.wire(2000, 1700, 2200, 1700); s.label(2200, 1700, "GAIN_OUT")
s.resistor("R13", "10k", 1500, 2500, "VOUT", "N_INV", "RG", "10k")

for ref, val, x, role in [("R601", "300k", 3000, 1), ("R602", "20k", 3300, 2),
                           ("R603", "4.7k", 3600, 3), ("R604", "200", 3900, 4),
                           ("R605", "100", 4200, 5)]:
    s.resistor(ref, val, x, 1400, "+15V" if role == 1 else None, None,
               f"R6 part {role}", "300k + 20k + 4.7k + 200 + 100 = 325k")
for x in (3100, 3400, 3700, 4000): s.wire(x, 1400, x + 100, 1400)
for ref, val, x, role in [("R501", "100k", 4800, 1), ("R502", "20k", 5100, 2), ("R503", "10k", 5400, 3)]:
    s.resistor(ref, val, x, 1400, None, "GAIN_OUT" if role == 3 else None,
               f"R5 part {role}", "100k + 20k + 10k = 130k")
for x in (4900, 5200): s.wire(x, 1400, x + 100, 1400)
s.wire(4300, 1400, 4400, 1400); s.wire(4400, 1400, 4700, 1400)
s.diode("D1", 4300, 1900, "N_INV", None)
s.wire(4400, 1900, 4400, 1400)

# Lower limiter chain: GAIN_OUT -> R7 -> LIMIT_LO -> R8 -> -15V.
for ref, val, x, role in [("R701", "100k", 3000, 1), ("R702", "20k", 3300, 2), ("R703", "10k", 3600, 3)]:
    s.resistor(ref, val, x, 2700, "GAIN_OUT" if role == 1 else None, None,
               f"R7 part {role}", "100k + 20k + 10k = 130k")
for x in (3100, 3400): s.wire(x, 2700, x + 100, 2700)
for ref, val, x, role in [("R801", "300k", 4200, 1), ("R802", "20k", 4500, 2),
                           ("R803", "4.7k", 4800, 3), ("R804", "200", 5100, 4),
                           ("R805", "100", 5400, 5)]:
    s.resistor(ref, val, x, 2700, None, "-15V" if role == 5 else None,
               f"R8 part {role}", "300k + 20k + 4.7k + 200 + 100 = 325k")
for x in (4300, 4600, 4900, 5200): s.wire(x, 2700, x + 100, 2700)
s.wire(3700, 2700, 3800, 2700); s.wire(3800, 2700, 4100, 2700)
s.diode("D2", 3900, 2200, None, "N_INV")
s.wire(3800, 2200, 3800, 2700)
s.note(2900, 1050, "NONLINEAR LIMITER", 55)

# Four RC stages.  Each 1647-ohm element remains 1k + 330 + 270 + 47.
stage_defs = [
    (101, 6500, "GAIN_OUT", "KICK", "U1", 2, 8000, "N_STAGE1", "C1"),
    (201, 9200, "N_STAGE1", "N_STAGE2", "U2", 1, 10700, "N_STAGE3", "C2"),
    (301, 11900, "N_STAGE3", "N_STAGE4", "U2", 2, 13400, "N_STAGE5", "C3"),
]
for base, x0, n0, rcnet, uref, unit, ux, outnet, cref in stage_defs:
    for off, val in enumerate(("1k", "330", "270", "47")):
        s.resistor(f"R{base+off}", val, x0 + off * 300, 1500,
                   n0 if off == 0 else None, None, f"R{str(base)[0]} part {off+1}",
                   "1k + 330 + 270 + 47 = 1647 ohm")
    for off in range(3): s.wire(x0 + off * 300 + 100, 1500, x0 + (off + 1) * 300 - 100, 1500)
    s.opamp(uref, unit, ux, 1400, None, None, None, "Bubba unity follower")
    s.wire(x0 + 1000, 1500, ux - 300, 1500)
    s.cap(cref, "10n", ux - 300, 2050, None, "GND", "Polypropylene 1%", "MKP1837310011")
    s.wire(ux - 300, 1500, ux - 300, 1950)
    s.wire(ux + 300, 1400, ux + 500, 1400)
    s.wire(ux + 500, 1400, ux + 500, 1300)
    s.wire(ux + 500, 1300, ux - 300, 1300)
    s.label(ux + 500, 1400, outnet)

for off, val in enumerate(("1k", "330", "270", "47")):
    s.resistor(f"R{401+off}", val, 14100 + off * 300, 1500,
               "N_STAGE5" if off == 0 else None, None, f"R4 part {off+1}",
               "1k + 330 + 270 + 47 = 1647 ohm")
for off in range(3): s.wire(14200 + off * 300, 1500, 14300 + off * 300, 1500)
s.label(15100, 1500, "VOUT")
s.cap("C4", "10n", 15100, 2050, None, "GND", "Polypropylene 1%", "MKP1837310011")
s.wire(15100, 1500, 15100, 1950)
s.power_unit("U1", 6500, 3150)
s.power_unit("U2", 10500, 3150)

s.note(600, 3900, "SALLEN–KEY LOW-PASS FILTER, OUTPUT BUFFER, AND FIXED DIVIDER", 80)
s.opamp("U3", 1, 1800, 4900, "VOUT", None, None, "Filter input follower")
s.wire(2100, 4900, 2300, 4900); s.wire(2300, 4900, 2300, 4800); s.wire(2300, 4800, 1500, 4800)
s.label(2300, 4900, "N_BUF")
for ref, val, x in [("R901", "1k", 3000), ("R902", "680", 3300), ("R903", "220", 3600)]:
    s.resistor(ref, val, x, 4900, "N_BUF" if ref == "R901" else None, None, "R9 series", "1k + 680 + 220 = 1.9k")
s.wire(3100, 4900, 3200, 4900); s.wire(3400, 4900, 3500, 4900)
for ref, val, x in [("R1001", "1k", 4500), ("R1002", "680", 4800), ("R1003", "220", 5100)]:
    s.resistor(ref, val, x, 5500, None, None, "R10 series", "1k + 680 + 220 = 1.9k")
s.wire(4600, 5500, 4700, 5500); s.wire(4900, 5500, 5000, 5500)
s.wire(3700, 4900, 4000, 4900); s.wire(4000, 4900, 4000, 5500); s.wire(4000, 5500, 4400, 5500)
s.cap("C6", "68n", 4000, 4450, "VFILTERED", None, "Polypropylene 1%", "MKP1837368011")
s.wire(4000, 4550, 4000, 4900)
s.opamp("U3", 2, 6300, 5400, None, None, None, "Sallen-Key unity follower")
s.wire(5200, 5500, 5500, 5500); s.wire(5500, 5500, 6000, 5500)
s.cap("C5", "1n", 5500, 6000, None, "GND", "C0G/NP0 1%", "SR215A102FARTR1")
s.wire(5500, 5500, 5500, 5900)
s.wire(6600, 5400, 6800, 5400); s.wire(6800, 5400, 6800, 5300); s.wire(6800, 5300, 6000, 5300)
s.label(6800, 5400, "VFILTERED")

s.opamp("U4", 1, 8000, 5400, "VFILTERED", None, None, "Output unity follower")
s.wire(8300, 5400, 8500, 5400); s.wire(8500, 5400, 8500, 5300); s.wire(8500, 5300, 7700, 5300)
s.label(8500, 5400, "N_OUTBUF")
s.resistor("R11", "2k", 9300, 5100, None, None, "Output divider R11A", "2k || 100k = 1960.784 ohm")
s.resistor("R16", "100k", 9300, 5700, None, None, "Output divider R11B", "2k || 100k = 1960.784 ohm")
s.wire(9200, 5100, 9000, 5100); s.wire(9000, 5100, 9000, 5700); s.wire(9000, 5700, 9200, 5700)
s.wire(9400, 5100, 9600, 5100); s.wire(9600, 5100, 9600, 5700); s.wire(9600, 5700, 9400, 5700)
s.label(9000, 5400, "N_OUTBUF"); s.label(9600, 5400, "VFINAL")
s.resistor("R12", "1k", 10400, 5400, "VFINAL", "GND", "Output divider lower leg")
s.opamp("U4", 2, 12500, 5400, "GND", None, None, "Spare channel grounded follower")
s.wire(12800, 5400, 13000, 5400); s.wire(13000, 5400, 13000, 5300); s.wire(13000, 5300, 12200, 5300)
s.label(13000, 5400, "SPARE_FB")
s.power_unit("U3", 7200, 6500); s.power_unit("U4", 10800, 6500)

s.note(600, 7050, "POWER ENTRY, LOCAL DECOUPLING, AND TEST ACCESS", 80)
s.comp("Conn_01x03", "J1", "Molex 39543-0003", 1400, 7900,
       footprint="Oscillator:J_Molex_39543-0003_Draft",
       fields={"MPN": "39543-0003", "FootprintStatus": "Verified holes; conservative body envelope reviewed"})
s.label(1300, 7800, "+15V"); s.label(1300, 7900, "GND"); s.label(1300, 8000, "-15V")
for i, x in enumerate((2700, 3500, 4300, 5100), start=1):
    s.cap(f"C{6+i}", "100n", x, 7800, "+15V", "GND", "Local ceramic bypass", "C315C104K5R5TA")
for i, x in enumerate((2700, 3500, 4300, 5100), start=1):
    s.cap(f"C{10+i}", "100n", x, 8500, "GND", "-15V", "Local ceramic bypass", "C315C104K5R5TA")
s.comp("C_Polarized", "C15", "10u 50V", 6200, 7800,
       footprint="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", fields={"Role": "+15 V bulk", "MPN": "EEU-FR1H100"})
s.label(6200, 7700, "+15V"); s.label(6200, 7900, "GND")
s.comp("C_Polarized", "C16", "10u 50V", 7000, 8500,
       footprint="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", fields={"Role": "-15 V bulk", "MPN": "EEU-FR1H100"})
s.label(7000, 8400, "GND"); s.label(7000, 8600, "-15V")

for ref, x, y, net in [
    ("TP1", 8500, 7700, "+15V"), ("TP2", 9700, 7700, "GND"), ("TP3", 10900, 7700, "-15V"),
    ("TP4", 12100, 7700, "GAIN_OUT"), ("TP5", 8500, 8400, "N_BUF"),
    ("TP6", 9700, 8400, "VFILTERED"), ("TP7", 10900, 8400, "VFINAL"), ("TP8", 12100, 8400, "OUTPUT")]:
    s.testpoint(ref, x, y, net)

s.note(600, 9150, "OUTPUT ATTENUATOR — wiring and selected potentiometer footprint confirmed", 80)
s.comp("Conn_01x02", "J2", "Amphenol 031-5431-10RFX", 2500, 9900,
       footprint="Oscillator:J_Amphenol_031-5431-10RFX_Draft",
       fields={"MPN": "031-5431-10RFX", "FootprintStatus": "Drawing-derived hole pattern and handedness independently reviewed"})
s.label(2400, 9850, "OUTPUT"); s.label(2400, 9950, "GND")
s.comp("R_Potentiometer", "RV1", "10k linear", 6000, 9900,
       footprint="Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical",
       fields={"MPN": "RK09K1130A5R", "Manufacturer": "Alps Alpine", "Status": "User-approved documented alternate"})
s.label(6000, 9750, "VFINAL"); s.label(6000, 10050, "GND"); s.label(6150, 9900, "OUTPUT")
s.note(7600, 9800, "RV1: VFINAL–GND, wiper to BNC center. R11/R16 and R12 remain fitted.", 55)
s.note(7600, 10050, "Selected part: Alps Alpine RK09K1130A5R, 10 kOhm linear.", 55)
s.note(600, 10800, "SOURCE: recovered final oscillator plus confirmed prototype additions. R1: fabrication release pending.", 50)
s.finish()

