from dataclasses import dataclass
from typing import List


@dataclass
class ChecklistItem:
    label: str
    checkboxIsFilled: bool


class AnalysisData:
    def __init__(self, data: dict):
        self.items: List[ChecklistItem] = [
            ChecklistItem(**item) for item in data.get("content", [])
        ]

    def get_labels(self) -> List[str]:
        return [item.label for item in self.items]

    def get_checked_items(self) -> List[str]:
        return [item.label for item in self.items if item.checkboxIsFilled]

    def set_checked(self, label: str, checked: bool):
        for item in self.items:
            if item.label == label:
                item.checkboxIsFilled = checked
                break

    def to_json(self) -> dict:
        return {"analysis": {"content": [item.__dict__ for item in self.items]}}
