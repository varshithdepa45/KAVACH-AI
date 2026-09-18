"""Generate FICTIONAL demo data for the KAVACH AI prototype.

Produces, under this demo-data/ directory:
    * inspection_report.pdf, equipment_manual.pdf, engineering_calculation.pdf
      (via fpdf2 if importable; otherwise readable .txt fallbacks with the same
      base filename).
    * plant_pid.png - a simple P&ID-style schematic (via Pillow) with boxes/circles
      for P-101, P-102, V-204, T-101, HX-301 and connecting pipelines. If Pillow is
      unavailable, writes plant_pid.txt describing it instead.
    * sample_internal_code.py - a fictional internal utility script.

ALL CONTENT IS FICTIONAL. There is no real facility data here.

Run:
    python demo-data/generate_demo_data.py
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent

FACILITY = "KAVACH DEMO REFINERY"
FICTION_BANNER = "*** FICTIONAL DEMONSTRATION DATA - NOT REAL FACILITY DATA ***"

# --- Optional deps (guarded) --------------------------------------------------
try:
    from fpdf import FPDF  # type: ignore
    _FPDF = True
except Exception:  # noqa: BLE001
    _FPDF = False

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
    _PIL = True
except Exception:  # noqa: BLE001
    _PIL = False


DOCS = {
    "inspection_report": [
        f"{FACILITY} - Unit 4 Annual Mechanical Integrity Inspection (2026)",
        FICTION_BANNER,
        "",
        "Page 7 - Feed Pump P-101:",
        "  Minor corrosion observed near the outlet section of feed pump P-101.",
        "  Wall thickness measured at 6.8 mm against a nominal 8.0 mm.",
        "  Recommend follow-up ultrasonic thickness survey within 90 days.",
        "",
        "Page 8 - Control Valve V-204:",
        "  Actuator shows sluggish response; stem packing to be replaced at next turnaround.",
        "",
        "Page 9 - Tank T-101 and Heat Exchanger HX-301:",
        "  Storage tank T-101 floor plates within acceptable limits.",
        "  Heat exchanger HX-301 tube bundle fouling factor trending upward but acceptable.",
        "",
        "Backup Pump P-102: inspected and confirmed standby-ready.",
    ],
    "equipment_manual": [
        f"{FACILITY} - Unit 4 OEM Equipment Manual (Fictional)",
        FICTION_BANNER,
        "",
        "Feed Pumps P-101 / P-102: horizontal centrifugal pumps rated 120 m3/h at 45 m head.",
        "Recommended minimum wall thickness for discharge piping is 6.4 mm.",
        "Control Valve V-204: globe valve; recommended packing replacement interval is 24 months.",
        "Heat Exchanger HX-301: shell-and-tube, design pressure 18 bar.",
        "Storage Tank T-101: atmospheric fixed-roof storage tank.",
    ],
    "engineering_calculation": [
        f"{FACILITY} - Engineering Calculation: P-101 Discharge Line (Fictional)",
        FICTION_BANNER,
        "",
        "Corrosion rate estimated at 0.3 mm/year.",
        "Measured thickness: 6.8 mm. Minimum allowable: 6.4 mm.",
        "Remaining life ~ (6.8 - 6.4) / 0.3 = ~1.3 years.",
        "Recommend scheduling repair or replacement before next inspection cycle.",
        "Safety factor per ASME B31.3 (illustrative only).",
    ],
}

SAMPLE_CODE = '''"""Fictional internal utility for KAVACH DEMO REFINERY inspection ingestion.

THIS IS FICTIONAL DEMONSTRATION CODE - not connected to any real system.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass


EQUIPMENT_TAGS = ["P-101", "P-102", "V-204", "T-101", "HX-301"]


@dataclass
class ThicknessReading:
    equipment_id: str
    measured_mm: float
    minimum_mm: float

    @property
    def margin_mm(self) -> float:
        return round(self.measured_mm - self.minimum_mm, 2)

    def is_flagged(self) -> bool:
        return self.margin_mm < 0.5


def load_readings(path: str) -> list[ThicknessReading]:
    readings: list[ThicknessReading] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            readings.append(ThicknessReading(
                equipment_id=row["equipment_id"],
                measured_mm=float(row["measured_mm"]),
                minimum_mm=float(row["minimum_mm"]),
            ))
    return readings


if __name__ == "__main__":
    demo = ThicknessReading("P-101", 6.8, 6.4)
    print(f"{demo.equipment_id} margin={demo.margin_mm}mm flagged={demo.is_flagged()}")
'''


def write_pdf_or_txt(base: str, lines: list[str]) -> str:
    if _FPDF:
        try:
            pdf = FPDF()
            pdf.set_margins(15, 15, 15)
            pdf.add_page()
            pdf.set_font("Helvetica", size=11)
            for line in lines:
                safe = line.encode("latin-1", "replace").decode("latin-1") or " "
                pdf.multi_cell(0, 6, safe, new_x="LMARGIN", new_y="NEXT")
            out = HERE / f"{base}.pdf"
            pdf.output(str(out))
            return str(out)
        except Exception as exc:  # noqa: BLE001
            print(f"  fpdf2 failed for {base} ({exc}); writing .txt fallback")
    out = HERE / f"{base}.txt"
    out.write_text("\n".join(lines) + "\n(Note: PDF library unavailable; .txt fallback)\n",
                   encoding="utf-8")
    return str(out)


def draw_pid() -> str:
    if not _PIL:
        out = HERE / "plant_pid.txt"
        out.write_text(
            f"{FACILITY} - Unit 4 P&ID (text description; Pillow unavailable)\n"
            f"{FICTION_BANNER}\n\n"
            "Flow: P-101 (feed pump) with backup P-102 -> V-204 (control valve) -> "
            "T-101 (storage tank) -> HX-301 (heat exchanger).\n"
            "Instrumentation: FT-101 (flow), PI-204 (pressure).\n",
            encoding="utf-8")
        return str(out)

    W, H = 900, 460
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
        big = ImageFont.truetype("arial.ttf", 20)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()
        big = ImageFont.load_default()

    d.text((20, 12), f"{FACILITY} - Unit 4 P&ID  (FICTIONAL)", fill="black", font=big)
    d.rectangle([10, 8, W - 10, H - 10], outline="black", width=2)

    def box(x, y, w, h, label, sub):
        d.rectangle([x, y, x + w, y + h], outline="black", width=2, fill="#eef3fb")
        d.text((x + 8, y + 8), label, fill="black", font=big)
        d.text((x + 8, y + 34), sub, fill="#333333", font=font)

    def circle(cx, cy, r, label):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=2, fill="#fdeeee")
        d.text((cx - r + 6, cy - 10), label, fill="black", font=font)

    # Equipment layout
    circle(90, 220, 42, "P-101")
    circle(90, 330, 42, "P-102")
    d.text((60, 375), "feed pumps", fill="#333333", font=font)
    box(210, 190, 110, 70, "V-204", "ctrl valve")
    box(400, 170, 130, 110, "T-101", "tank")
    box(620, 190, 150, 90, "HX-301", "heat exch.")

    def pipe(x1, y1, x2, y2):
        d.line([x1, y1, x2, y2], fill="black", width=3)

    pipe(132, 220, 210, 225)   # P-101 -> V-204
    pipe(132, 330, 205, 250)   # P-102 -> V-204 (join)
    pipe(320, 225, 400, 225)   # V-204 -> T-101
    pipe(530, 225, 620, 235)   # T-101 -> HX-301
    pipe(770, 235, 830, 235)   # HX-301 -> out
    d.text((790, 210), "out", fill="black", font=font)

    # Instrumentation bubbles
    circle(360, 120, 22, "FT")
    d.text((345, 145), "FT-101", fill="#333333", font=font)
    circle(275, 130, 22, "PI")
    d.text((258, 155), "PI-204", fill="#333333", font=font)

    d.text((20, H - 30), FICTION_BANNER, fill="#8a1f1f", font=font)

    out = HERE / "plant_pid.png"
    img.save(str(out))
    return str(out)


def main() -> None:
    print(f"Generating demo data in {HERE}")
    print(f"  fpdf2 available: {_FPDF} | Pillow available: {_PIL}")
    created = []
    for base, lines in DOCS.items():
        created.append(write_pdf_or_txt(base, lines))
    created.append(draw_pid())
    code_path = HERE / "sample_internal_code.py"
    code_path.write_text(SAMPLE_CODE, encoding="utf-8")
    created.append(str(code_path))
    print("Created:")
    for c in created:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
