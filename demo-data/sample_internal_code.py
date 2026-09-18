"""Fictional internal utility for KAVACH DEMO REFINERY inspection ingestion.

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
