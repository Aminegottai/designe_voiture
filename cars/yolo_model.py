from ultralytics import YOLO
import os
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "best.pt"
yolo_model = YOLO(str(MODEL_PATH))
