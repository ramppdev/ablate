from typing import List

from ablate.blocks import Text
from ablate.core.types import Run
from ablate.report import Report


def make_runs() -> List[Run]:
    return [
        Run(id="a", params={"model": "resnet", "seed": 1}, metrics={"accuracy": 0.7}),
        Run(id="b", params={"model": "resnet", "seed": 2}, metrics={"accuracy": 0.8}),
    ]


def test_report_add() -> None:
    report = Report(make_runs())
    report.add(Text("Test 1"), Text("Test 2"))
    assert len(report.blocks) == 2
    assert isinstance(report.blocks[0], Text)


def test_report_iadd() -> None:
    report = Report(make_runs())
    report += Text("Test")
    assert len(report.blocks) == 1
    assert isinstance(report.blocks[0], Text)


def test_report_add_operator() -> None:
    report = Report(make_runs())
    new_report = report + Text("Test")
    assert len(report.blocks) == 0
    assert len(new_report.blocks) == 1
    assert isinstance(new_report.blocks[0], Text)
