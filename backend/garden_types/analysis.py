from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChecklistItem:
    label: str
    checkboxIsFilled: bool


class AnalysisData:
    def __init__(
        self,
        data: dict,
        notes: Optional[str] = None,
    ):
        self.items: List[ChecklistItem] = [
            ChecklistItem(**item) for item in data.get("content", [])
        ]
        self.notes: Optional[str] = notes

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
        result = {"analysis": {"content": [item.__dict__ for item in self.items]}}
        if self.notes:
            result["notes"] = self.notes
        return result
