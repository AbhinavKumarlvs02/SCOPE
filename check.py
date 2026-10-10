import torch
import os
from cyclone_ai.engine import CyclonePredictor

# Check 1: Does the file exist?
path = "models/mamba_cyclone_v2.pth"
print(f"Checking file: {os.path.abspath(path)}")
print(f"Exists: {os.path.exists(path)}")

# Check 2: Can the engine load it?
try:
    bot = CyclonePredictor()
    if bot.model is not None:
        print(" SUCCESS: Model loaded into memory.")
        # Test a dummy prediction
        test_data = [[19.8, 85.8, 140, 980]] * 8
        res = bot.predict_next_step(test_data)
        print(f" Prediction Test: {res}")
    else:
        print(" FAILED: model is None. Check weights loading logic in engine.py")
except Exception as e:
    print(f" CRITICAL ERROR: {e}")