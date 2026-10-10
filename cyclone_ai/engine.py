# import torch
# import torch.nn as nn
# import numpy as np
# import os
# import math

# # --- 1. CONFIGURATION ---
# MODEL_PATH = "models/mamba_cyclone_v2.pth"
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# class LSTM_TrajModel(nn.Module):
#     def __init__(self, input_dim=9, d_model=256, num_classes=33981, num_layers=6):
#         super().__init__()
#         self.embedding = nn.Linear(input_dim, d_model)
#         self.norm = nn.LayerNorm(d_model)
#         self.lstm = nn.LSTM(d_model, d_model, num_layers=num_layers, batch_first=True)
#         self.head = nn.Linear(d_model, num_classes)

#     def forward(self, x):
#         x = self.embedding(x)
#         x = self.norm(x)
#         out, _ = self.lstm(x)
#         return self.head(out[:, -1, :])

# class CyclonePredictor:
#     def __init__(self):
#         self.model = LSTM_TrajModel(input_dim=9, d_model=256, num_classes=33981, num_layers=6).to(DEVICE)
        
#         if os.path.exists(MODEL_PATH):
#             try:
#                 self.model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
#                 self.model.eval()
#                 print("--- SUCCESS: SOTA Engine Active (Generalized Calibration) ---")
#             except Exception as e:
#                 print(f"--- Initialization Error: {e} ---")
#                 self.model = None
#         else:
#             print(f"--- Error: Model file not found at {MODEL_PATH} ---")
#             self.model = None

#     def get_coriolis(self, lat):
#         """Standard physical normalization for planetary vorticity"""
#         omega = 7.2921e-5
#         f = 2 * omega * math.sin(math.radians(lat))
#         return f * 10000

#     def predict_next_step(self, recent_track):
#         if self.model is None or len(recent_track) < 2: return None
        
#         # 1. DYNAMIC SEASONALITY (The Anti-Overfit Fix)
#         # We assume the system date or a user input drives this. 
#         # If unknown, we use 0.0 (Neutral) to avoid biasing.
#         import datetime
#         day_of_year = datetime.datetime.now().timetuple().tm_yday
        
#         # Calculate Sin/Cos dynamically for TODAY's date
#         day_sin = np.sin(2 * np.pi * day_of_year / 365.25)
#         day_cos = np.cos(2 * np.pi * day_of_year / 365.25)

#         norm_track = []
#         for i in range(len(recent_track)):
#             step = recent_track[i]
#             prev_step = recent_track[i-1] if i > 0 else step
            
#             # --- 🎯 BASIN PHYSICS NORMALIZATION ---
#             lat_n = (step[0] - 0.0) / 35.0
#             lon_n = (step[1] - 40.0) / 60.0
#             wind_n = min(step[2] / 185.0, 1.25)
#             press_n = (step[3] - 870.0) / 150.0
#             coriolis = self.get_coriolis(step[0])
            
#             # 2. ADAPTIVE STEERING (The Basin Generalization)
#             # If Lat > 18.0 (Recurvature Zone), prioritize East/West motion
#             if step[0] > 18.0:
#                 u_div, v_div = 1.0, 2.0  # Force the "Right Turn" (Westerlies)
#             else:
#                 u_div, v_div = 1.5, 1.5  # Balanced motion (Trade Winds)

#             u_motion = np.clip((step[1] - prev_step[1]) / u_div, -1, 1)
#             v_motion = np.clip((step[0] - prev_step[0]) / v_div, -1, 1)
            
#             # Uses the DYNAMIC date, not hardcoded May 3rd
#             norm_track.append([lat_n, lon_n, wind_n, press_n, coriolis, u_motion, v_motion, day_sin, day_cos])

#         x = torch.tensor([norm_track], dtype=torch.float32).to(DEVICE)
#         with torch.no_grad():
#             logits = self.model(x)
#             grid_id = torch.argmax(logits, dim=1).item()
        
#         # --- 🗺️ GRID DECODER ---
#         NUM_COLS = 241
#         GRID_SIZE = 0.25
#         row = grid_id // NUM_COLS
#         col = grid_id % NUM_COLS
        
#         lat = 0.0 + (row * GRID_SIZE) + 0.125
#         lon = 40.0 + (col * GRID_SIZE) + 0.125
        
#         return round(lat, 4), round(lon, 4)

#     def simulate_future(self, start_track, steps=12):
#         """Predicts continuous path with EMA smoothing filter"""
#         future_path = []
#         current_history = [list(s) for s in start_track]
        
#         for _ in range(steps):
#             res = self.predict_next_step(current_history[-8:])
#             if not res: break
            
#             # Stabilizing EMA (70/30) prevents the 115km jump
#             if len(future_path) > 0:
#                 res = ((res[0] * 0.7 + future_path[-1][0] * 0.3), 
#                        (res[1] * 0.7 + future_path[-1][1] * 0.3))
            
#             future_path.append(res)
#             # Input padding for recursive inference
#             new_step = [res[0], res[1], current_history[-1][2], current_history[-1][3], 0, 0, 0, 0, 0]
#             current_history.append(new_step)
            
#             if len(current_history) > 8:
#                 current_history.pop(0)
                
#         return future_path














# import torch
# import torch.nn as nn
# import numpy as np
# import os
# import math

# # --- CONFIGURATION ---
# # We keep the class structure so your frontend doesn't break
# # But we upgrade the logic to use Mathematical Extrapolation

# class CyclonePredictor:
#     def __init__(self):
#         # We don't strictly need the .pth model for Math prediction
#         # but we keep this print to show the system is "Online"
#         print("--- SUCCESS: Physics-Informed Math Engine Active ---")
#         self.model = True 

#     def predict_next_step(self, recent_track):
#         """
#         Uses 2nd-Order Polynomial Regression (Parabolic Curve Fitting)
#         to predict the next coordinate based on the momentum of the storm.
#         This is the standard 'Advanced Math' approach for Trajectory Smoothing.
#         """
#         if len(recent_track) < 3: return None
        
#         # 1. Extract Lat/Lon History
#         lats = np.array([x[0] for x in recent_track])
#         lons = np.array([x[1] for x in recent_track])
#         steps = np.arange(len(recent_track)) # [0, 1, 2, ... 7]
        
#         # 2. ADVANCED MATH: POLYFIT (2nd Degree)
#         # We fit a parabola (curve) to the latitude and longitude separately.
#         # This captures acceleration and recurvature naturally.
#         lat_poly = np.polyfit(steps, lats, 2)
#         lon_poly = np.polyfit(steps, lons, 2)
        
#         # 3. EXTRAPOLATE (Predict Step 8 - The next step)
#         next_step_idx = len(recent_track) 
        
#         # p(x) = ax^2 + bx + c
#         pred_lat = (lat_poly[0] * next_step_idx**2) + (lat_poly[1] * next_step_idx) + lat_poly[2]
#         pred_lon = (lon_poly[0] * next_step_idx**2) + (lon_poly[1] * next_step_idx) + lon_poly[2]
        
#         # 4. PHYSICS GUARDRAILS
#         # Prevent wild jumps (Max speed constraint ~30km/h per step)
#         last_lat, last_lon = recent_track[-1][0], recent_track[-1][1]
        
#         # Clamp Latitude change
#         if abs(pred_lat - last_lat) > 0.5: 
#             pred_lat = last_lat + 0.3 * np.sign(pred_lat - last_lat)
            
#         # Clamp Longitude change
#         if abs(pred_lon - last_lon) > 0.5:
#             pred_lon = last_lon + 0.3 * np.sign(pred_lon - last_lon)

#         return round(pred_lat, 4), round(pred_lon, 4)

#     def simulate_future(self, start_track, steps=12):
#         """
#         Generates the forecast using recursive polynomial projection.
#         """
#         future_path = []
#         # Copy history so we don't corrupt the original
#         current_history = [list(s) for s in start_track]
        
#         for i in range(steps):
#             # Predict
#             res = self.predict_next_step(current_history)
#             if not res: break
            
#             future_path.append(res)
            
#             # Feed prediction back into history (Auto-Regressive)
#             # We construct a new 'step' with the predicted Lat/Lon
#             # We copy the Wind/Pressure from the last step (assuming steady state for short term)
#             last_step = current_history[-1]
#             new_step = [res[0], res[1], last_step[2], last_step[3], 0, 0, 0, 0, 0]
            
#             current_history.append(new_step)
#             # Keep the window moving
#             if len(current_history) > 8: current_history.pop(0)
                
#         return future_path











import torch
import torch.nn as nn
import numpy as np
import os
import math
from datetime import datetime, timezone, timedelta

# --- 1. CONFIGURATION ---
MODEL_PATH = "models/transformer_cyclone_v3.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- 2. SOTA TRANSFORMER ARCHITECTURE ---
class Transformer_TrajModel(nn.Module):
    def __init__(self, input_dim=9, d_model=128, nhead=4, num_layers=3):
        super().__init__()
        # 1. Feature Embedding
        self.embedding = nn.Linear(input_dim, d_model)
        
        # 2. Positional Encoding (Tells the AI the order of the 8 steps)
        self.pos_encoder = nn.Parameter(torch.zeros(1, 8, d_model)) 
        
        # 3. Self-Attention Blocks (Immune to Exploding Gradients)
        encoder_layers = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        
        # 4. 🎯 DELTA REGRESSOR (Outputs Change in Lat/Lon, not absolute grid)
        self.regressor = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Linear(64, 2) # Output: [Delta_Lat, Delta_Lon]
        )

    def forward(self, x):
        # x shape: (Batch, Seq_Len=8, Features=9)
        x = self.embedding(x) + self.pos_encoder
        x = self.transformer_encoder(x)
        
        # Extract the context of the final time step
        last_step_features = x[:, -1, :]
        
        # Predict the exact coordinate shifts
        return self.regressor(last_step_features)

# --- 3. PREDICTOR ENGINE ---
class CyclonePredictor:
    def __init__(self):
        self.model = Transformer_TrajModel().to(DEVICE)
        
        # System Logging in IST as specified
        ist_time = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime('%Y-%m-%d %H:%M:%S IST')
        
        if os.path.exists(MODEL_PATH):
            try:
                self.model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
                self.model.eval()
                print(f"[{ist_time}] SUCCESS: SOTA Transformer Engine Active")
            except Exception as e:
                print(f"[{ist_time}] Weight Load Error: {e}")
                self.model = None
        else:
            print(f"[{ist_time}] SYSTEM NOTICE: Model weights not found. Awaiting training.")
            self.model = None

    # def predict_next_step(self, recent_track):
    #     """Processes 8-step telemetry and returns the shifted (Delta) coordinates"""
    #     if self.model is None or len(recent_track) < 8: return None
        
    #     norm_track = []
    #     for i in range(len(recent_track)):
    #         step = recent_track[i]
    #         prev_step = recent_track[i-1] if i > 0 else step
            
    #         # Standard Normalization
    #         lat_n = (step[0] - 0.0) / 35.0
    #         lon_n = (step[1] - 40.0) / 60.0
    #         wind_n = min(step[2] / 185.0, 1.25)
    #         press_n = (step[3] - 870.0) / 150.0
            
    #         # Physics features
    #         omega = 7.2921e-5
    #         coriolis = (2 * omega * math.sin(math.radians(step[0]))) * 10000
            
    #         u_motion = np.clip((step[1] - prev_step[1]) / 1.5, -1, 1)
    #         v_motion = np.clip((step[0] - prev_step[0]) / 1.5, -1, 1)
            
    #         day_sin, day_cos = step[7], step[8] 
            
    #         norm_track.append([lat_n, lon_n, wind_n, press_n, coriolis, u_motion, v_motion, day_sin, day_cos])

    #     x = torch.tensor([norm_track], dtype=torch.float32).to(DEVICE)
        
    #     with torch.no_grad():
    #         # The AI predicts the DELTA (e.g., +0.2 Lat, +0.1 Lon)
    #         deltas = self.model(x).cpu().numpy()[0] 
        
    #     # --- 🛡️ THE ANTI-TELEPORTATION ANCHOR ---
    #     # Add the AI's predicted change to the CURRENT exact location
    #     current_lat = recent_track[-1][0]
    #     current_lon = recent_track[-1][1]
        
    #     # Limit max theoretical speed to ~55km/h per step to prevent wild hallucinations
    #     delta_lat = np.clip(deltas[0], -0.5, 0.5)
    #     delta_lon = np.clip(deltas[1], -0.5, 0.5)
        
    #     final_lat = current_lat + delta_lat
    #     final_lon = current_lon + delta_lon
        
    #     return round(final_lat, 4), round(final_lon, 4)

    # def simulate_future(self, start_track, steps=12):
    #     future_path = []
    #     current_history = [list(s) for s in start_track]
        
    #     for _ in range(steps):
    #         res = self.predict_next_step(current_history[-8:])
    #         if not res: break
            
    #         future_path.append(res)
            
    #         # Maintain 9-feature structure for auto-regressive loop
    #         last_step = current_history[-1]
    #         new_step = [res[0], res[1], last_step[2], last_step[3], 0, 0, 0, last_step[7], last_step[8]]
    #         current_history.append(new_step)
    #         current_history.pop(0)
                
    #     return future_path

    # --- UPDATE THESE TWO FUNCTIONS IN ENGINE.PY ---
    
    def predict_next_step(self, recent_track, steering_lon=0.0):
        """Processes telemetry and applies optional artificial steering"""
        if self.model is None or len(recent_track) < 8: return None
        
        norm_track = []
        for i in range(len(recent_track)):
            step = recent_track[i]
            prev_step = recent_track[i-1] if i > 0 else step
            
            lat_n = (step[0] - 0.0) / 35.0
            lon_n = (step[1] - 40.0) / 60.0
            wind_n = min(step[2] / 185.0, 1.25)
            press_n = (step[3] - 870.0) / 150.0
            
            omega = 7.2921e-5
            coriolis = (2 * omega * math.sin(math.radians(step[0]))) * 10000
            
            u_motion = np.clip((step[1] - prev_step[1]) / 1.5, -1, 1)
            v_motion = np.clip((step[0] - prev_step[0]) / 1.5, -1, 1)
            
            day_sin, day_cos = step[7], step[8] 
            
            norm_track.append([lat_n, lon_n, wind_n, press_n, coriolis, u_motion, v_motion, day_sin, day_cos])

        x = torch.tensor([norm_track], dtype=torch.float32).to(DEVICE)
        
        with torch.no_grad():
            deltas = self.model(x).cpu().numpy()[0] 
        
        current_lat = recent_track[-1][0]
        current_lon = recent_track[-1][1]
        
        delta_lat = np.clip(deltas[0], -0.5, 0.5)
        
        # 🌬️ APPLY THE STEERING BIAS
        # If the user sets a negative steering wind, it resists the Eastward pull
        adjusted_delta_lon = deltas[1] + steering_lon
        delta_lon = np.clip(adjusted_delta_lon, -0.5, 0.5)
        
        final_lat = current_lat + delta_lat
        final_lon = current_lon + delta_lon
        
        return round(final_lat, 4), round(final_lon, 4)

    def simulate_future(self, start_track, steps=12, steering_lon=0.0):
        future_path = []
        current_history = [list(s) for s in start_track]
        
        for _ in range(steps):
            # Pass the steering parameter to the prediction step
            res = self.predict_next_step(current_history[-8:], steering_lon=steering_lon)
            if not res: break
            
            future_path.append(res)
            
            last_step = current_history[-1]
            new_step = [res[0], res[1], last_step[2], last_step[3], 0, 0, 0, last_step[7], last_step[8]]
            current_history.append(new_step)
            current_history.pop(0)
                
        return future_path