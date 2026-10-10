import torch
import numpy as np
import pandas as pd
from cyclone_ai.engine import CyclonePredictor

def run_fani_validation():
    print("Starting Cyclone Fani Validation Test...")
    
    # 1. Initialize the Predictor Engine
    predictor = CyclonePredictor()
    if predictor.model is None:
        print(" Error: Model could not be loaded. Check path: models/mamba_cyclone_v2.pth")
        return

    # 2. Historical Data: Cyclone Fani (May 2-3, 2019)
    # Format: [Lat, Lon, Wind, Pressure, SST, Humidity, Shear, Vorticity, CoastDist]
    # We use the 8 steps leading up to the Puri landfall
    fani_history = [
        [16.0, 84.5, 205, 942, 29.0, 85, 12, 45, 100],
        [16.5, 84.7, 210, 938, 29.0, 85, 10, 48, 80],
        [17.1, 84.8, 215, 932, 28.5, 88, 8, 52, 60],
        [17.8, 85.0, 210, 935, 28.5, 88, 12, 50, 40],
        [18.4, 85.2, 205, 937, 28.0, 90, 15, 45, 30],
        [19.0, 85.4, 195, 939, 28.0, 90, 18, 40, 20],
        [19.3, 85.6, 185, 941, 27.5, 92, 20, 35, 10],
        [19.8, 85.8, 175, 943, 27.5, 92, 22, 30, 0] # Real Landfall Point
    ]

    # 3. Target: The Ground Truth (Actual position 3 hours after Step 8)
    # Historical data shows Fani continued inland slightly NNE
    target_lat, target_lon = 20.2, 86.1

    print(f" Input Landfall Coordinate: {fani_history[-1][0]}, {fani_history[-1][1]}")
    
    # 4. Run Prediction
    try:
        # Predict next 3 steps (9 hours total)
        prediction_path = predictor.simulate_future(fani_history, steps=3)
        
        if prediction_path:
            p_lat, p_lon = prediction_path[0] # T+3 Hour prediction
            
            # 5. Calculate Euclidean Distance Error (Approx km)
            # 0.1 degree is roughly 11.1km
            lat_err = abs(p_lat - target_lat)
            lon_err = abs(p_lon - target_lon)
            total_error_km = np.sqrt(lat_err**2 + lon_err**2) * 111.1
            
            print("\n--- VALIDATION RESULTS ---")
            print(f"Predicted Point (T+3h): {p_lat}, {p_lon}")
            print(f"Actual Fani Point:      {target_lat}, {target_lon}")
            print(f"Mathematical Error:      {total_error_km:.2f} km")
            
            if total_error_km < 63:
                print(" RESULT: Within SOTA Target Error Range (<62.84km)")
            else:
                print(" RESULT: Outside SOTA Error Range. Check Normalization constants.")
        
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    run_fani_validation()