"""
Lightweight Ultralytics-compatible wrappers for Hailo inference output.
Allows detect() in threadsignDetection to work unchanged with HailoYOLO.
"""
import numpy as np
import torch


class FakeBox:
    """Mimics a single Ultralytics box object."""
    def __init__(self, xyxy, conf, cls_id):
        self.xyxy = [torch.tensor(xyxy, dtype=torch.float32)]
        self.conf = [torch.tensor(conf,  dtype=torch.float32)]
        self.cls  = [torch.tensor(cls_id, dtype=torch.float32)]


class FakeResult:
    """Mimics one Ultralytics Results object (single image)."""
    def __init__(self, detections: list[dict], names: dict):
        self.names = names
        self.boxes = [
            FakeBox(d["xyxy"], d["conf"], d["cls_id"])
            for d in detections
        ]


def to_ultralytics_results(detections: list[dict], names: dict) -> list[FakeResult]:
    """
    Wraps raw HailoYOLO detections into a list[FakeResult],
    matching the return type of model(frame) from Ultralytics.
    """
    return [FakeResult(detections, names)]