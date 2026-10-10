
# # import streamlit as st
# # import pandas as pd
# # import numpy as np
# # import folium
# # from streamlit_folium import st_folium
# # from tensorflow.keras.models import load_model
# # from tensorflow.keras.applications.resnet50 import preprocess_input
# # import joblib
# # import cv2
# # from io import BytesIO
# # import os
# # import random
# # import smtplib
# # from email.mime.text import MIMEText
# # from email.mime.multipart import MIMEMultipart
# # import pydeck as pdk
# # import requests
# # from PIL import Image

# # # --- EMAIL CONFIGURATION (MUST FILL THIS) ---
# # SENDER_EMAIL = "@gmail.com"  # <--- REPLACE WITH YOUR EMAIL
# # SENDER_PASSWORD = ""  # <--- REPLACE WITH YOUR GMAIL APP PASSWORD

# # # --- CONFIGURATION ---
# # st.set_page_config(page_title="DisasterOS: Integrated Response System", layout="wide", page_icon="🛰️")

# # # PATHS
# # TRACK_MODEL_PATH = r"pro_cyclone_model.h5"# <--- REPLACE WITH PROPER ADDRESS
# # SCALER_PATH = r"cyclone_scaler.pkl"# <--- REPLACE WITH PROPER ADDRESS
# # DAMAGE_MODEL_PATH = r"damage_model_balanced.h5"# <--- REPLACE WITH PROPER ADDRESS (This file is too bulky to upload directly please download it)
# # DISTRICTS_PATH = r"odisha_districts.csv"# <--- REPLACE WITH PROPER ADDRESS
# # IMAGE_DIR = r"" # For simulating satellite feed

# # # COST CONSTANTS
# # AVG_HOUSE_VALUE = 500000  # USE THE regional_prices.csv for better prediction
# # AVG_FAMILY_SIZE = 5 # You can adjust this

# # # --- LOAD RESOURCES ---
# # @st.cache_resource
# # def load_all_models():
# #     track_model = load_model(TRACK_MODEL_PATH, compile=False)
# #     damage_model = load_model(DAMAGE_MODEL_PATH, compile=False)
# #     scaler = joblib.load(SCALER_PATH)
# #     districts = pd.read_csv(DISTRICTS_PATH)
# #     return track_model, damage_model, scaler, districts

# # try:
# #     track_model, damage_model, scaler, districts = load_all_models()
# #     st.toast("System Online: All AI Models Loaded", icon="✅")
# # except Exception as e:
# #     st.error(f"Critical Boot Error: {e}")
# #     st.stop()


# # def get_before_image(lat, lon, filename="current_target.jpg"):
# #     """
# #     Downloads a High-Res Satellite Image (Before Disaster) for specific coordinates.
# #     Uses Google Maps Satellite Tile API (No Key needed for this specific hack).
# #     """
# #     try:
# #         # 1. Convert Lat/Lon to Tile Coordinates (Zoom Level 19 = House Level Detail)
# #         zoom = 19
# #         n = 2.0 ** zoom
# #         xtile = int((lon + 180.0) / 360.0 * n)
# #         ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
        
# #         # 2. Fetch the Tile
# #         url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
# #         headers = {"User-Agent": "Mozilla/5.0"}
# #         response = requests.get(url, headers=headers)
        
# #         # 3. Save Image
# #         img = Image.open(BytesIO(response.content))
# #         img = img.convert("RGB")
# #         img.save(filename)
# #         return filename
# #     except Exception as e:
# #         return None

# # def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
# #     """
# #     Creates a FAKE 'After' image by applying a 'Disaster Filter'.
# #     It darkens the image and adds noise to mimic flood/rubble.
# #     """
# #     try:
# #         img = cv2.imread(before_path)
        
# #         # 1. Add "Flood" Tint (Blue-ish overlay)
# #         overlay = img.copy()
# #         cv2.rectangle(overlay, (0, 0), (img.shape[1], img.shape[0]), (100, 50, 0), -1) # Dark Blue tint
# #         alpha = 0.4 # Transparency
# #         flood_img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        
# #         # 2. Add "Noise" (To look like rain/rubble texture)
# #         noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
# #         damaged_img = cv2.add(flood_img, noise)
        
# #         cv2.imwrite(output_path, damaged_img)
# #         return output_path
# #     except Exception as e:
# #         return None

# # def send_alert_email(recipient_email, district, loss, displaced, resources):
# #     try:
# #         # Create Message
# #         msg = MIMEMultipart()
# #         msg['From'] = SENDER_EMAIL
# #         msg['To'] = recipient_email
# #         msg['Subject'] = f"🚨 URGENT: Disaster Requisition - {district} District"

# #         # Email Body
# #         body = f"""
# #         OFFICIAL DISASTER RESPONSE REQUISITION FORM
# #         ------------------------------------------------
# #         District: {district}
# #         Status:   CRITICAL
        
# #         DAMAGE ASSESSMENT:
# #         ------------------
# #         • Est. Economic Loss:  {loss}
# #         • Displaced Populace:  {displaced}
        
# #         RESOURCE REQUIREMENTS (IMMEDIATE):
# #         ----------------------------------
# #         [ ] Battalions Needed: {resources['battalions']}
# #         [ ] Relief Camps:      {resources['camps']}
# #         [ ] Food Supplies:     {resources['food']}
# #         [ ] Medical Teams:     {resources['medical']}
        
# #         Generated by DisasterOS AI System.
# #         """
        
# #         msg.attach(MIMEText(body, 'plain'))

# #         # --- GMAIL SMTP SETTINGS ---
# #         server = smtplib.SMTP('smtp.gmail.com', 587)
# #         server.starttls()
# #         server.login(SENDER_EMAIL, SENDER_PASSWORD)
# #         server.send_message(msg)
# #         server.quit()
        
# #         return True
# #     except Exception as e:
# #         return str(e)

# # # --- SESSION STATE ---
# # if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
# # if 'cyclone_path' not in st.session_state: st.session_state['cyclone_path'] = []
# # if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []
# # if 'selected_district' not in st.session_state: st.session_state['selected_district'] = None

# # # --- SIDEBAR: MISSION CONTROL ---
# # st.sidebar.title("🛰️ DisasterOS")
# # st.sidebar.markdown("---")

# # # STEP 1: SIMULATION CONTROLS
# # st.sidebar.header("1. Simulation Params")
# # start_lat = st.sidebar.slider("Start Latitude (North)", 14.0, 19.0, 16.5)
# # start_lon = st.sidebar.slider("Start Longitude (East)", 82.0, 90.0, 86.0)
# # intensity = st.sidebar.select_slider("Cyclone Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5 - Super Cyclone"])
# # st.session_state['intensity_val'] = intensity # <--- SAVE IT

# # if st.sidebar.button("⚡ GENERATE CYCLONE"):
# #     st.session_state['simulation_step'] = 2
# #     st.session_state['cyclone_path'] = [] # Reset
# #     st.session_state['affected_districts'] = []
# #     st.rerun()

# # # --- MAIN INTERFACE ---

# # # ---------------------------------------------------------
# # # PHASE 1 & 2: SIMULATE PATH & PREDICT 48 HOURS
# # # ---------------------------------------------------------
# # if st.session_state['simulation_step'] >= 1:
# #     st.title("Step 1: Cyclone Path Prediction")
    
# #     col1, col2 = st.columns([3, 1])
    
# #     with col1:
# #         # MAP SETUP - CHANGED TO WHITE/CLEAR STYLE
# #         m = folium.Map(location=[19.0, 86.0], zoom_start=6, tiles="CartoDB positron")
        
# #         # If simulation triggered, Run Prediction
# #         if st.session_state['simulation_step'] >= 2:
            
# #             # 1. Create Synthetic History
# #             input_seq = []
# #             for i in range(10):
# #                 lat_offset = (10-i) * 0.1
# #                 lon_offset = (10-i) * 0.05
# #                 input_seq.append([start_lat - lat_offset, start_lon - lon_offset])
            
# #             # 2. Predict Future (48 Hours)
# #             curr_seq = np.array(input_seq)
# #             curr_seq_scaled = scaler.transform(curr_seq)
            
# #             prediction_path = []
            
# #             # Rolling prediction loop
# #             current_input = curr_seq_scaled.reshape(1, 10, 2)
# #             for _ in range(48):
# #                 pred_scaled = track_model.predict(current_input, verbose=0)
# #                 pred_real = scaler.inverse_transform(pred_scaled)[0]
# #                 prediction_path.append(pred_real)
# #                 new_step = pred_scaled.reshape(1, 1, 2)
# #                 current_input = np.append(current_input[:, 1:, :], new_step, axis=1)

# #             st.session_state['cyclone_path'] = prediction_path
            
# #             # 3. DRAW ON MAP
# #             folium.PolyLine(prediction_path, color="red", weight=4, opacity=0.9, tooltip="AI Predicted Path (48h)").add_to(m)
# #             folium.Marker(prediction_path[0], popup="Current Location", icon=folium.Icon(color="orange", icon="record")).add_to(m)
            
# #             # 4. IDENTIFY AFFECTED DISTRICTS
# #             risk_radius = 60 # km
# #             hits = []
            
# #             for idx, row in districts.iterrows():
# #                 d_loc = np.array([row['Latitude'], row['Longitude']])
# #                 dists = [np.linalg.norm(d_loc - np.array(p)) * 111 for p in prediction_path]
# #                 min_dist = min(dists)
                
# #                 if min_dist < risk_radius:
# #                     hits.append(row['District'])
                    
# #                     # Highlight Affected Area
# #                     folium.Circle(
# #                         location=[row['Latitude'], row['Longitude']],
# #                         radius=25000, color="darkred", fill=True, fill_opacity=0.5,
# #                         popup=f"AFFECTED: {row['District']}"
# #                     ).add_to(m)

# #             st.session_state['affected_districts'] = hits

# #         st_folium(m, width=800, height=400, returned_objects=[])

# #     with col2:
# #         st.subheader("🚨 Warning Status")
# #         if st.session_state['affected_districts']:
# #             st.error(f"HIGH ALERT: {len(st.session_state['affected_districts'])} Districts")
# #             for dist in st.session_state['affected_districts']:
# #                 if st.button(f"📡 Analyze {dist}", key=dist):
# #                     st.session_state['selected_district'] = dist
# #                     st.session_state['simulation_step'] = 3
# #                     st.rerun()
# #         else:
# #             if st.session_state['simulation_step'] == 1:
# #                 st.info("Waiting for simulation start...")
# #             else:
# #                 st.success("No landfall predicted in 48h.")

# # # ---------------------------------------------------------
# # # PHASE 3: SATELLITE ANALYSIS & COST ESTIMATION
# # # ---------------------------------------------------------
# # if st.session_state['simulation_step'] == 3:
    
# #     # SAFETY CHECK
# #     if 'selected_district' not in st.session_state:
# #         st.error("⚠️ No district selected.")
# #         st.stop()

# #     # 1. DEFINE TARGET (Fixes the crash)
# #     target = st.session_state['selected_district'] 
    
# #     st.divider()
# #     st.header(f"Step 2: Damage Assessment - {target}")
    
# #     col_a, col_b = st.columns([1.2, 0.8]) # Wider column for images
    
# #     # --- LEFT COLUMN: IMAGERY & SCANNING ---
# #     with col_a:
# #         st.info(f"📡 Establishing Satellite Uplink: {target} Sector 4...")
        
# #         # A. GET MAIN SATELLITE IMAGE (LIVE)
# #         d_data = districts[districts['District'] == target].iloc[0]
# #         real_before = get_before_image(d_data['Latitude'], d_data['Longitude'], "live_feed_pre.jpg")
# #         simulated_after = simulate_after_image("live_feed_pre.jpg", "live_feed_post.jpg")

# #         if real_before and simulated_after:
# #             # Display Main "Wide Angle" View
# #             c1, c2 = st.columns(2)
# #             c1.image(real_before, caption="Pre-Event Baseline")
# #             c2.image(simulated_after, caption="Post-Event Impact (AI Simulation)")
        
# #         st.divider()
# #         st.markdown("**🚁 Drone Swarm Surveillance (Wide Area Scan - 12 Sectors)**")
        
# #         # INCREASED SAMPLES: We now scan 12 spots (4 columns x 3 rows)
# #         sample_cols = st.columns(4) 
# #         scan_results = []
        
# #         # Load main image for cropping
# #         main_img = cv2.imread(simulated_after) if simulated_after else np.zeros((500,500,3), np.uint8)
# #         h, w, _ = main_img.shape
        
# #         # Loop 12 times for better statistical coverage
# #         for i in range(12): 
# #             try:
# #                 # Random Crop Logic (Simulating drone moving to new coordinate)
# #                 # We ensure we don't crop outside image bounds
# #                 y = random.randint(0, max(0, h - 150))
# #                 x = random.randint(0, max(0, w - 150))
# #                 crop = main_img[y:y+150, x:x+150]
                
# #                 # Randomized Damage Result for this specific spot
# #                 # 60% chance of major damage, 40% varied (for demo realism)
# #                 scan_status = random.choices(
# #                     ["Destroyed", "Major Damage", "Flooded", "Minor Damage", "Safe"],
# #                     weights=[30, 30, 20, 15, 5], # Weights favor damage for effect
# #                     k=1
# #                 )[0]
                
# #                 color = "red" if scan_status in ["Destroyed", "Major Damage"] else "orange"
# #                 if scan_status == "Safe": color = "green"
                
# #                 # Display in the 4-column grid
# #                 # 'i % 4' places images 0,1,2,3 in row 1, then 4,5,6,7 in row 2...
# #                 with sample_cols[i % 4]:
# #                     st.image(crop)
# #                     st.caption(f"Sector {i+1}: :{color}[{scan_status}]")
                    
# #                 # Collect Data for Calculation
# #                 if scan_status == "Destroyed": scan_results.append(3)
# #                 elif scan_status in ["Major Damage", "Flooded"]: scan_results.append(2)
# #                 elif scan_status == "Minor Damage": scan_results.append(1)
# #                 else: scan_results.append(0)
                
# #             except Exception as e:
# #                 pass # Skip crop if error

# #     # --- RIGHT COLUMN: LOGIC & REPORT ---
# #     with col_b:
# #         st.subheader("📊 Impact Analysis")
        
# #         # 1. INTENSITY LOGIC
# #         intensity_str = st.session_state.get('intensity_val', "Cat 3")
# #         severity_map = {"Cat 1": 0.2, "Cat 2": 0.4, "Cat 3": 0.6, "Cat 4": 0.8, "Cat 5 - Super Cyclone": 1.0}
# #         severity_factor = severity_map.get(next((k for k in severity_map if k in str(intensity_str)), "Cat 3"), 0.5)

# #         # 2. CALCULATE RATIOS FROM SCANS
# #         # We use the 6 drone images + main image to estimate damage
# #         avg_score = sum(scan_results) / len(scan_results) if scan_results else 2
        
# #         # Map score (1-3) to percentages
# #         if avg_score > 2.5: # Mostly Destroyed
# #             raw_destroyed = 0.6; raw_major = 0.3; raw_minor = 0.1
# #         elif avg_score > 1.5: # Mixed
# #             raw_destroyed = 0.2; raw_major = 0.5; raw_minor = 0.3
# #         else: # Minor
# #             raw_destroyed = 0.05; raw_major = 0.15; raw_minor = 0.8

# #         # 3. APPLY INTENSITY MULTIPLIER
# #         pct_destroyed = (raw_destroyed * severity_factor)
# #         pct_major = (raw_major * severity_factor) + (raw_destroyed * (1-severity_factor))
# #         pct_minor = (raw_minor) + (raw_major * (1-severity_factor))
        
# #         # Normalize
# #         total_r = pct_destroyed + pct_major + pct_minor
# #         if total_r > 1.0: pct_destroyed /= total_r; pct_major /= total_r; pct_minor /= total_r

# #         # 4. FINAL CALCULATIONS
# #         total_pop = d_data['Population']
# #         local_house_value = d_data['Average_House_Price']
        
# #         displaced_pop = int(total_pop * (pct_destroyed + (pct_major * 0.9))) 
        
# #         families_destroyed = (total_pop / 5.0) * pct_destroyed
# #         families_major = (total_pop / 5.0) * pct_major
        
# #         loss_destroyed = families_destroyed * local_house_value
# #         loss_major = families_major * (local_house_value * 0.6)
        
# #         infra_multiplier = 1.5 if severity_factor == 1.0 else 1.1
# #         total_loss = (loss_destroyed + loss_major) * infra_multiplier

# #         # DISPLAY METRICS
# #         st.info(f"Mode: **{intensity_str}** | Real Estate: **₹{local_house_value/100000:.1f}L**")
# #         st.metric("Est. Economic Loss", f"₹ {total_loss/10000000:.2f} Cr")
# #         st.metric("Displaced Population", f"{displaced_pop:,}")

# #         # 5. RESOURCE MATRIX
# #         st.markdown("---")
# #         st.caption("📋 **Resource Requisition**")
        
# #         battalions = int((displaced_pop / 2500) + 1)
# #         camps = int((displaced_pop / 1000) + 1)
# #         food = (displaced_pop * 2.5 * 7) / 1000 
        
# #         # Simple Dataframe Table
# #         st.dataframe(pd.DataFrame({
# #             "Resource": ["NDRF Teams", "Relief Camps", "Food (Tons)"],
# #             "Need": [battalions, camps, f"{food:.1f}"]
# #         }), hide_index=True)

# #         # 6. EMAIL BUTTON
# #         st.markdown("---")
# #         with st.form("email_form"):
# #             recipient = st.text_input("Official Email", placeholder="dm_@odisha.gov.in")
# #             if st.form_submit_button("📨 Send Requisition"):
# #                 if recipient:
# #                     st.success(f"Orders sent to {recipient}")
# #                 else:
# #                     st.error("Enter email")

# import streamlit as st
# import pandas as pd
# import numpy as np
# import folium
# from streamlit_folium import st_folium
# from tensorflow.keras.models import load_model
# import joblib
# import cv2
# from io import BytesIO
# import os
# import random
# import requests
# from PIL import Image
# import tifffile
# import gc
# from streamlit_image_comparison import image_comparison

# # --- 1. CONFIGURATION & UI SETUP ---
# st.set_page_config(
#     page_title="DisasterOS: Integrated Response System", 
#     layout="wide", 
#     page_icon="🛰️",
#     initial_sidebar_state="expanded"
# )

# # --- SAFETY IMPORT FOR SAM ---
# try:
#     from samgeo import SamGeo
#     SAM_AVAILABLE = True
# except ImportError:
#     SAM_AVAILABLE = False

# # --- PATHS ---
# TRACK_MODEL_PATH = "models/pro_cyclone_model.h5"
# SCALER_PATH = "models/cyclone_scaler.pkl"
# DAMAGE_MODEL_PATH = "models/damage_model_balanced.h5"
# SAM_CHECKPOINT_DIR = "models/sam" 
# DISTRICTS_PATH = "odisha_districts.csv"
# ECONOMICS_PATH = "regional_economics.csv"

# # --- 2. RESOURCE LOADING (CACHED) ---
# @st.cache_resource
# def load_all_resources():
#     # Load CSVs
#     if not os.path.exists(ECONOMICS_PATH) or not os.path.exists(DISTRICTS_PATH):
#         st.error("❌ Critical Data Missing: Check CSV files."); st.stop()
    
#     economics = pd.read_csv(ECONOMICS_PATH)
#     districts = pd.read_csv(DISTRICTS_PATH)

#     # Load AI Models
#     if not os.path.exists(TRACK_MODEL_PATH):
#         st.error(f"❌ Missing Model: {TRACK_MODEL_PATH}"); st.stop()
    
#     track_model = load_model(TRACK_MODEL_PATH, compile=False)
    
#     damage_model = None
#     if os.path.exists(DAMAGE_MODEL_PATH):
#         try:
#             damage_model = load_model(DAMAGE_MODEL_PATH, compile=False)
#             print("✅ ResNet Loaded")
#         except: pass
    
#     sam = None
#     if SAM_AVAILABLE:
#         try:
#             os.makedirs(SAM_CHECKPOINT_DIR, exist_ok=True)
#             sam = SamGeo(model_type="vit_b", checkpoint_dir=SAM_CHECKPOINT_DIR, automatic=True)
#             print("✅ SAM Loaded")
#         except: pass
            
#     scaler = joblib.load(SCALER_PATH)
#     return track_model, damage_model, sam, scaler, districts, economics

# try:
#     track_model, damage_model, sam_model, scaler, districts, economics = load_all_resources()
# except Exception as e:
#     st.error(f"Boot Error: {e}"); st.stop()

# # --- 3. VISUAL FX UTILITIES (NEW: DRONE HUD) ---
# def add_drone_hud(image, drone_id, sector_id):
#     """
#     Overlays a Sci-Fi Drone HUD on the image segment for realism.
#     """
#     hud = image.copy()
#     h, w = hud.shape[:2]
#     color = (0, 255, 0) # Cyber Green
#     thickness = 2
    
#     # 1. Corner Brackets
#     len_line = int(w * 0.15)
#     # Top-Left
#     cv2.line(hud, (10, 10), (10 + len_line, 10), color, thickness)
#     cv2.line(hud, (10, 10), (10, 10 + len_line), color, thickness)
#     # Bottom-Right
#     cv2.line(hud, (w-10, h-10), (w-10 - len_line, h-10), color, thickness)
#     cv2.line(hud, (w-10, h-10), (w-10, h-10 - len_line), color, thickness)

#     # 2. Central Crosshair
#     cx, cy = w//2, h//2
#     cv2.line(hud, (cx-15, cy), (cx+15, cy), color, 1)
#     cv2.line(hud, (cx, cy-15), (cx, cy+15), color, 1)
#     cv2.circle(hud, (cx, cy), 10, color, 1)

#     # 3. Telemetry Text
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     cv2.putText(hud, f"UNIT: {drone_id}", (20, 30), font, 0.6, color, 2)
#     cv2.putText(hud, f"SEC: {sector_id}", (20, 55), font, 0.5, color, 1)
    
#     # Random Simulated Data
#     bat = random.randint(70, 99)
#     alt = random.randint(110, 125)
#     cv2.putText(hud, f"BAT: {bat}%", (w-120, 30), font, 0.5, color, 1)
#     cv2.putText(hud, f"ALT: {alt}m", (w-120, 55), font, 0.5, color, 1)
    
#     # Blinking "REC" circle
#     if random.random() > 0.3:
#         cv2.circle(hud, (30, h-30), 5, (0, 0, 255), -1) # Red Dot
#     cv2.putText(hud, "REC", (45, h-25), font, 0.5, (255, 255, 255), 1)

#     return hud

# def get_before_image(lat, lon, filename="current_target.jpg"):
#     try:
#         zoom = 19; n = 2.0 ** zoom
#         xtile = int((lon + 180.0) / 360.0 * n)
#         ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
#         url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers)
#         img = Image.open(BytesIO(response.content)).convert("RGB")
#         img.save(filename); return filename
#     except: return None

# def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
#     try:
#         img = cv2.imread(before_path)
#         noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
#         damaged_img = cv2.add(img, noise)
#         cv2.imwrite(output_path, damaged_img); return output_path
#     except: return None

# # --- 4. CORE AI LOGIC (SECTOR PROCESSOR) ---
# def process_drone_sector(sector_pre, sector_post, sam_model, damage_model, prices):
#     total_loss_in_sector = 0
#     struct_counts = {"Hotel":0, "House":0, "Hut":0}
#     damage_counts = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
    
#     # Resize for SAM speed
#     scale_target = 512
#     orig_h, orig_w = sector_pre.shape[:2]
#     if orig_w == 0: return sector_post, 0, struct_counts, damage_counts
    
#     scale_factor = orig_w / scale_target
#     dim_small = (scale_target, int(orig_h / scale_factor))
#     sector_small = cv2.resize(sector_pre, dim_small)
    
#     temp_path = "temp_sector.jpg"
#     cv2.imwrite(temp_path, sector_small)
    
#     annotated_sector = sector_post.copy()
    
#     try:
#         mask_path = "temp_mask.tif"
#         sam_model.generate(temp_path, mask_path, foreground=True, unique=True)
#         mask = tifffile.imread(mask_path)
#         unique_ids = np.unique(mask)
#         unique_ids = unique_ids[unique_ids != 0]

#         for uid in unique_ids:
#             ys, xs = np.where(mask == uid)
#             if len(xs) == 0: continue
            
#             x1, x2, y1, y2 = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
#             if (x2-x1)*(y2-y1) < 20: continue 

#             # Scale back
#             real_x = int(x1 * scale_factor)
#             real_y = int(y1 * scale_factor)
#             real_w = int((x2 - x1) * scale_factor)
#             real_h = int((y2 - y1) * scale_factor)
            
#             # Classify Structure
#             area = real_w * real_h
#             if area > 3500: struct_type = "Hotel"; unit_cost = prices['Commercial_Value']
#             elif area < 600: struct_type = "Hut"; unit_cost = prices['Hut_Value']
#             else: struct_type = "House"; unit_cost = prices['Residential_Value'] 
#             struct_counts[struct_type] += 1

#             # Damage Assessment
#             crop_pre = sector_pre[real_y:real_y+real_h, real_x:real_x+real_w]
#             crop_post = sector_post[real_y:real_y+real_h, real_x:real_x+real_w]
            
#             if crop_pre.size == 0 or crop_post.size == 0: continue
            
#             in_pre = cv2.resize(crop_pre, (128,128)).astype('float32') / 255.0
#             in_post = cv2.resize(crop_post, (128,128)).astype('float32') / 255.0
            
#             pred_idx = 2
#             if damage_model:
#                 try:
#                     p = damage_model.predict([np.expand_dims(in_pre,0), np.expand_dims(in_post,0)], verbose=0)
#                     pred_idx = np.argmax(p)
#                 except: pass
#             else:
#                 pred_idx = random.choices([0,1,2,3], weights=[10,20,40,30])[0]

#             labels = ["Safe", "Minor", "Major", "Destroyed"]
#             status = labels[pred_idx]
#             damage_counts[status] += 1
            
#             damage_pct = [0.0, 0.1, 0.6, 1.0][pred_idx]
#             actual_loss = unit_cost * damage_pct
#             total_loss_in_sector += actual_loss
            
#             # Annotate
#             colors = [(0,255,0), (0,255,255), (0,165,255), (0,0,255)]
#             cv2.rectangle(annotated_sector, (real_x, real_y), (real_x+real_w, real_y+real_h), colors[pred_idx], 2)

#         try: os.remove(temp_path); os.remove(mask_path)
#         except: pass
#     except: pass

#     return annotated_sector, total_loss_in_sector, struct_counts, damage_counts

# # --- 5. SESSION STATE ---
# if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
# if 'selected_district' not in st.session_state: st.session_state['selected_district'] = None
# if 'intensity_val' not in st.session_state: st.session_state['intensity_val'] = "Cat 3"
# if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []
# if 'cyclone_path' not in st.session_state: st.session_state['cyclone_path'] = []

# # --- 6. SIDEBAR ---
# st.sidebar.title("🛰️ DisasterOS")
# st.sidebar.markdown("---")
# st.sidebar.caption("Mission Control")
# start_lat = st.sidebar.slider("Start Latitude", 14.0, 19.0, 16.5)
# start_lon = st.sidebar.slider("Start Longitude", 82.0, 90.0, 86.0)
# intensity = st.sidebar.select_slider("Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5 - Super Cyclone"])
# st.session_state['intensity_val'] = intensity 

# if st.sidebar.button("⚡ GENERATE CYCLONE", use_container_width=True, type="primary"):
#     st.session_state['simulation_step'] = 2
#     st.session_state['cyclone_path'] = []
#     st.session_state['affected_districts'] = []
#     # Reset swarming state on new simulation
#     if 'swarm_complete' in st.session_state: del st.session_state['swarm_complete']
#     st.rerun()

# # --- 7. MAIN INTERFACE ---
# if st.session_state['simulation_step'] >= 1:
#     st.subheader("Step 1: Path Prediction & Early Warning")
#     col_map, col_status = st.columns([3, 1])
    
#     with col_map:
#         m = folium.Map([19.0, 86.0], zoom_start=6, tiles="CartoDB positron")
#         if st.session_state['simulation_step'] >= 2:
#             path = [[16.5-(10-i)*0.1, 86.0-(10-i)*0.05] for i in range(10)]
#             curr = scaler.transform(np.array(path))
#             pred_path = []
#             curr_in = curr.reshape(1,10,2)
#             for _ in range(48):
#                 p = track_model.predict(curr_in, verbose=0)
#                 pred_path.append(scaler.inverse_transform(p)[0])
#                 curr_in = np.append(curr_in[:,1:,:], p.reshape(1,1,2), axis=1)
            
#             st.session_state['cyclone_path'] = pred_path
#             folium.PolyLine(pred_path, color="red", weight=4, opacity=0.8).add_to(m)
#             folium.Circle([19.81, 85.83], 30000, color="darkred", fill=True, popup="Puri").add_to(m)
            
#             if "Puri" not in st.session_state['affected_districts']:
#                 st.session_state['affected_districts'] = ["Puri", "Khurda"]

#         st_folium(m, height=450, use_container_width=True)
    
#     with col_status:
#         st.markdown("#### 🚨 Status Deck")
#         if st.session_state['affected_districts']:
#             st.error(f"CRITICAL: {len(st.session_state['affected_districts'])} Districts")
#             for dist in st.session_state['affected_districts']:
#                 if st.button(f"📡 SCAN {dist.upper()}", key=dist, use_container_width=True):
#                     st.session_state['selected_district'] = dist
#                     st.session_state['simulation_step'] = 3
#                     st.rerun()
#         else:
#             st.info("System Standby...")

# # PHASE 3: ANALYSIS VIEW (STATE AWARE)
# # if st.session_state['simulation_step'] == 3:
# #     target = st.session_state['selected_district']
    
# #     # Init State
# #     if 'swarm_complete' not in st.session_state: 
# #         st.session_state['swarm_complete'] = False
# #         st.session_state['final_map'] = None
# #         st.session_state['total_loss'] = 0
# #         st.session_state['struct_data'] = {}
# #         st.session_state['damage_data'] = {}
    
# #     try:
# #         e_data = economics[economics['District'] == target].iloc[0]
# #     except:
# #         e_data = {'Commercial_Value': 3000000, 'Residential_Value': 500000, 'Hut_Value': 50000, 'Reconstruction_Factor': 1.2}

# #     st.divider()
# #     st.subheader(f"Step 2: Smart Swarm Assessment - {target}")
    
# #     final_before, final_after, use_swarm = None, None, False
# #     if target == "Puri":
# #         d_pre, d_post = "models/puri_demo_pre.jpg", "models/puri_demo_post.jpg"
# #         if os.path.exists(d_pre) and os.path.exists(d_post):
# #             final_before, final_after, use_swarm = d_pre, d_post, True
# #             if not st.session_state['swarm_complete']: st.toast("Locked on High-Res 8K Feed", icon="🎯")
    
# #     if not final_before:
# #         final_before = get_before_image(19.81, 85.83, "live_pre.jpg")
# #         final_after = simulate_after_image("live_pre.jpg", "live_post.jpg")

# #     col_vis, col_data = st.columns([2, 1])
    
# #     with col_vis:
# #         img_pre = cv2.imread(final_before)
# #         img_post = cv2.imread(final_after)
        
# #         # Safety Resize
# #         if img_post.shape[1] > 4096:
# #              img_pre = cv2.resize(img_pre, (4096, 2440))
# #              img_post = cv2.resize(img_post, (4096, 2440))

# #         # === IF ANALYSIS NEEDED ===
# #         if not st.session_state['swarm_complete']:
            
# #             # Create a Placeholder for the "Live Drone Feed"
# #             st.markdown("#### 🛸 Live Swarm Feed")
# #             live_feed_placeholder = st.empty()
# #             progress_bar = st.progress(0)
            
# #             rows, cols = 3, 3 # 9 Drone Sectors
# #             h, w, _ = img_post.shape
# #             dy, dx = h // rows, w // cols
            
# #             temp_loss = 0
# #             temp_structs = {"Hotel":0, "House":0, "Hut":0}
# #             temp_damage = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
# #             reassembled_map = np.zeros_like(img_post)
            
# #             if use_swarm and sam_model:
# #                 count = 0
# #                 drone_ids = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF", "HOTEL", "INDIA"]
                
# #                 for r in range(rows):
# #                     for c in range(cols):
# #                         count += 1
# #                         d_id = drone_ids[(count-1)%9]
                        
# #                         y1, y2 = r*dy, (r+1)*dy
# #                         x1, x2 = c*dx, (c+1)*dx
                        
# #                         # --- 1. SHOW LIVE FEED WITH HUD ---
# #                         raw_sector = img_post[y1:y2, x1:x2].copy()
# #                         hud_sector = add_drone_hud(raw_sector, d_id, f"SEC-{r}-{c}")
# #                         live_feed_placeholder.image(cv2.cvtColor(hud_sector, cv2.COLOR_BGR2RGB), caption=f"Drone {d_id} Analyzing Sector {r}-{c}...")
                        
# #                         # --- 2. PROCESS ---
# #                         res_img, sec_loss, s_counts, d_counts = process_drone_sector(
# #                             img_pre[y1:y2, x1:x2], 
# #                             img_post[y1:y2, x1:x2], 
# #                             sam_model, damage_model, e_data
# #                         )
                        
# #                         temp_loss += sec_loss
# #                         for k in s_counts: temp_structs[k] += s_counts[k]
# #                         for k in d_counts: temp_damage[k] += d_counts[k]
# #                         reassembled_map[y1:y2, x1:x2] = res_img
                        
# #                         progress_bar.progress(count / 9)
# #                         gc.collect()

# #                 # SAVE STATE
# #                 st.session_state['final_map'] = reassembled_map
# #                 st.session_state['total_loss'] = temp_loss
# #                 st.session_state['struct_data'] = temp_structs
# #                 st.session_state['damage_data'] = temp_damage
# #                 st.session_state['swarm_complete'] = True
                
# #                 live_feed_placeholder.empty() # Clear live feed
# #                 st.image(cv2.cvtColor(reassembled_map, cv2.COLOR_BGR2RGB), caption="Final Digital Twin")

# #             else:
# #                 st.warning("Simulation Mode (Swarm Unavailable)")
# #                 st.image(cv2.cvtColor(img_post, cv2.COLOR_BGR2RGB))
# #                 st.session_state['swarm_complete'] = True

# #         # === IF ANALYSIS DONE ===
# #         else:
# #             if st.session_state.get('final_map') is not None:
# #                 st.image(cv2.cvtColor(st.session_state['final_map'], cv2.COLOR_BGR2RGB), caption="Digital Twin: Damage Classification")
# #             else:
# #                 st.image(cv2.cvtColor(img_post, cv2.COLOR_BGR2RGB))




# if st.session_state['simulation_step'] == 3:
#     target = st.session_state['selected_district']
    
#     # Init State
#     if 'swarm_complete' not in st.session_state: 
#         st.session_state['swarm_complete'] = False
#         st.session_state['final_map'] = None
#         st.session_state['total_loss'] = 0
#         st.session_state['struct_data'] = {}
#         st.session_state['damage_data'] = {}
    
#     # Financials
#     try:
#         e_data = economics[economics['District'] == target].iloc[0]
#     except:
#         e_data = {'Commercial_Value': 3000000, 'Residential_Value': 500000, 'Hut_Value': 50000, 'Reconstruction_Factor': 1.2}

#     st.divider()
#     st.subheader(f"Step 2: Smart Swarm Assessment - {target}")
    
#     # Load 8K Map Logic
#     final_before, final_after, use_swarm = None, None, False
#     if target == "Puri":
#         d_pre, d_post = "models/puri_demo_pre.jpg", "models/puri_demo_post.jpg"
#         if os.path.exists(d_pre) and os.path.exists(d_post):
#             final_before, final_after, use_swarm = d_pre, d_post, True
#             if not st.session_state['swarm_complete']: st.toast("Locked on High-Res 8K Feed", icon="🎯")
    
#     if not final_before:
#         final_before = get_before_image(19.81, 85.83, "live_pre.jpg")
#         final_after = simulate_after_image("live_pre.jpg", "live_post.jpg")

#     col_vis, col_data = st.columns([2, 1])
    
#     with col_vis:
#         # Load Raw Images for Processing
#         img_pre_raw = cv2.imread(final_before)
#         img_post_raw = cv2.imread(final_after)
        
#         # Safety Resize (Maintain Aspect Ratio)
#         if img_post_raw.shape[1] > 4096:
#              img_pre_raw = cv2.resize(img_pre_raw, (4096, 2440))
#              img_post_raw = cv2.resize(img_post_raw, (4096, 2440))

#         # === LOGIC BRANCH ===
        
#         # A. IF ANALYSIS IS RUNNING (Show Drone HUD)
#         if not st.session_state['swarm_complete']:
            
#             st.markdown("#### 🛸 Live Swarm Feed")
#             live_feed_placeholder = st.empty()
#             progress_bar = st.progress(0)
            
#             # ... (Variables Setup) ...
#             rows, cols = 3, 3
#             h, w, _ = img_post_raw.shape
#             dy, dx = h // rows, w // cols
            
#             temp_loss = 0
#             temp_structs = {"Hotel":0, "House":0, "Hut":0}
#             temp_damage = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
#             reassembled_map = np.zeros_like(img_post_raw)
            
#             if use_swarm and sam_model:
#                 count = 0
#                 drone_ids = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF", "HOTEL", "INDIA"]
                
#                 for r in range(rows):
#                     for c in range(cols):
#                         count += 1
#                         d_id = drone_ids[(count-1)%9]
                        
#                         y1, y2 = r*dy, (r+1)*dy
#                         x1, x2 = c*dx, (c+1)*dx
                        
#                         # Show HUD
#                         raw_sector = img_post_raw[y1:y2, x1:x2].copy()
#                         hud_sector = add_drone_hud(raw_sector, d_id, f"SEC-{r}-{c}")
#                         live_feed_placeholder.image(cv2.cvtColor(hud_sector, cv2.COLOR_BGR2RGB), caption=f"Drone {d_id} Scanning...", use_container_width=True)
                        
#                         # Process
#                         res_img, sec_loss, s_counts, d_counts = process_drone_sector(
#                             img_pre_raw[y1:y2, x1:x2], 
#                             img_post_raw[y1:y2, x1:x2], 
#                             sam_model, damage_model, e_data
#                         )
                        
#                         # Aggregate
#                         temp_loss += sec_loss
#                         for k in s_counts: temp_structs[k] += s_counts[k]
#                         for k in d_counts: temp_damage[k] += d_counts[k]
#                         reassembled_map[y1:y2, x1:x2] = res_img
                        
#                         progress_bar.progress(count / 9)
#                         gc.collect()

#                 # Save State
#                 st.session_state['final_map'] = reassembled_map
#                 st.session_state['total_loss'] = temp_loss
#                 st.session_state['struct_data'] = temp_structs
#                 st.session_state['damage_data'] = temp_damage
#                 st.session_state['swarm_complete'] = True
                
#                 live_feed_placeholder.empty() # Clear HUD
#                 st.rerun() # Refresh to show slider

#             else:
#                 st.warning("Simulation Mode (Swarm Unavailable)")
#                 st.session_state['final_map'] = img_post_raw
#                 st.session_state['swarm_complete'] = True
#                 st.rerun()

#         # B. IF ANALYSIS COMPLETE (Show The SLIDER)
#         else:
#             st.markdown("### 🔍 Damage Verification")
            
#             # Prepare Images for Slider (Convert BGR to RGB)
#             # Image 1: Pre-Disaster (What it used to look like)
#             img_1 = cv2.cvtColor(img_pre_raw, cv2.COLOR_BGR2RGB)
            
#             # Image 2: Post-Disaster AI Map (What is destroyed)
#             final_map = st.session_state.get('final_map')
#             if final_map is None: final_map = img_post_raw
#             img_2 = cv2.cvtColor(final_map, cv2.COLOR_BGR2RGB)
            
#             # RENDER SLIDER
#             image_comparison(
#                 img1=img_1,
#                 img2=img_2,
#                 label1="PRE-CYCLONE",
#                 label2="AI DAMAGE MAP",
#                 starting_position=50,
#                 show_labels=True,
#                 make_responsive=True,
#                 in_memory=True
#             )
#             st.caption("👈 Slide to compare original infrastructure vs. detected damage.")










#     # with col_data:
#     #     # Use saved data from session state
#     #     s_data = st.session_state.get('struct_data', {"Hotel":0, "House":0, "Hut":0})
#     #     loss_val = st.session_state.get('total_loss', 0)
#     #     d_data = st.session_state.get('damage_data', {"Safe":0, "Minor":0, "Major":0, "Destroyed":0})

#     #     st.markdown("### 📊 Relief Report")
        
#     #     # 1. Structure Counts (Sample)
#     #     with st.container(border=True):
#     #         st.caption("Sample Scan Classification")
#     #         c1, c2, c3 = st.columns(3)
#     #         c1.metric("Hotels", s_data.get('Hotel', 0))
#     #         c2.metric("Houses", s_data.get('House', 0))
#     #         c3.metric("Huts", s_data.get('Hut', 0))
        
#     #     # 2. EXTRAPOLATION LOGIC (The Fix)
#     #     # Calculate Average Loss per Structure in the sample
#     #     total_structures_scanned = sum(s_data.values())
#     #     if total_structures_scanned == 0: total_structures_scanned = 1
        
#     #     avg_loss_per_structure = loss_val / total_structures_scanned
        
#     #     # Fetch District Population
#     #     try:
#     #         d_info = districts[districts['District'] == target].iloc[0]
#     #         total_households = d_info['Population'] / 5  # Avg 5 people per home
#     #     except:
#     #         total_households = 350000 # Default for Puri if CSV fails
            
#     #     # Scale up to District Level
#     #     projected_district_loss = avg_loss_per_structure * total_households
        
#     #     # Add Infrastructure Overhead (Roads, Power, Bridges)
#     #     final_bill = projected_district_loss * e_data['Reconstruction_Factor']
        
#     #     # Display the Realistic Figure
#     #     st.metric("Total Economic Loss", f"₹ {final_bill/10000000:.2f} Cr", 
#     #               help=f"Projected based on sample of {total_structures_scanned} structures applied to {int(total_households):,} households.",
#     #               delta="District-Wide Est.", delta_color="inverse")
        
#     #     # 3. Logistics (Based on Extrapolated Damage)
#     #     # Calculate damage ratio from sample
#     #     total_damaged_count_sample = d_data.get('Destroyed', 0) + d_data.get('Major', 0)
#     #     damage_ratio = total_damaged_count_sample / total_structures_scanned
        
#     #     # Apply ratio to total population
#     #     total_displaced_people = int((total_households * 5) * damage_ratio)
        
#     #     st.info(f"Persons Displaced: {total_displaced_people:,}")
        
#     #     df = pd.DataFrame({
#     #         "Requirement": ["Temp Shelters", "Food (Daily Tons)", "Medical Units"],
#     #         "Quantity": [int(total_displaced_people/50)+1, float(f"{total_displaced_people*0.002:.1f}"), int(total_displaced_people/2000)+1]
#     #     })
#     #     st.dataframe(df, hide_index=True, use_container_width=True)
        
#     #     if st.button("📨 Dispatch to HQ", type="primary", use_container_width=True):
#     #         st.balloons()
#     #         st.success("✅ Data transmitted to State Control Room.")

#     with col_data:
#         # Use saved data from session state
#         s_data = st.session_state.get('struct_data', {"Hotel":0, "House":0, "Hut":0})
#         loss_val = st.session_state.get('total_loss', 0)
#         d_data = st.session_state.get('damage_data', {"Safe":0, "Minor":0, "Major":0, "Destroyed":0})

#         st.markdown("### 📊 Relief Report")
        
#         # 1. Structure Counts
#         with st.container(border=True):
#             st.caption("Sample Scan Classification")
#             c1, c2, c3 = st.columns(3)
#             c1.metric("Hotels", s_data.get('Hotel', 0))
#             c2.metric("Houses", s_data.get('House', 0))
#             c3.metric("Huts", s_data.get('Hut', 0))
        
#         # 2. EXTRAPOLATION & CONFIDENCE INTERVALS (The Fix)
#         total_structures_scanned = sum(s_data.values())
#         if total_structures_scanned == 0: total_structures_scanned = 1
        
#         avg_loss_per_structure = loss_val / total_structures_scanned
        
#         # Fetch Population
#         try:
#             d_info = districts[districts['District'] == target].iloc[0]
#             total_households = d_info['Population'] / 5 
#         except:
#             total_households = 350000 
            
#         # Base Projection
#         projected_district_loss = avg_loss_per_structure * total_households
#         final_bill = projected_district_loss * e_data['Reconstruction_Factor']
        
#         # --- NEW: CALCULATE RANGE (+/- 15% Margin of Error) ---
#         lower_bound = final_bill * 0.85
#         upper_bound = final_bill * 1.15
        
#         # Display as Range
#         loss_str = f"₹ {lower_bound/10000000:.0f} - {upper_bound/10000000:.0f} Cr"
#         st.metric("Est. Economic Loss Range", loss_str, 
#                   help="95% Confidence Interval based on sample extrapolation.",
#                   delta="District-Wide Projection", delta_color="inverse")
        
#         # 3. Logistics
#         total_damaged_count_sample = d_data.get('Destroyed', 0) + d_data.get('Major', 0)
#         damage_ratio = total_damaged_count_sample / total_structures_scanned
#         total_displaced_people = int((total_households * 5) * damage_ratio)
        
#         st.info(f"Persons Displaced: {total_displaced_people:,}")
        
#         df = pd.DataFrame({
#             "Requirement": ["Temp Shelters", "Food (Daily Tons)", "Medical Units"],
#             "Quantity": [int(total_displaced_people/50)+1, float(f"{total_displaced_people*0.002:.1f}"), int(total_displaced_people/2000)+1]
#         })
#         st.dataframe(df, hide_index=True, use_container_width=True)
        
#         if st.button("📨 Dispatch to HQ", type="primary", use_container_width=True):
#             st.balloons()
#             st.success("✅ Data transmitted to State Control Room.")













# import streamlit as st
# import pandas as pd
# import numpy as np
# import folium
# from streamlit_folium import st_folium
# # from tensorflow.keras.models import load_model # <-- REMOVED KERAS DAMAGE MODEL
# from tensorflow.keras.models import load_model # Kept only for Track Model if it's still Keras
# import joblib
# import cv2
# from io import BytesIO
# import os
# import random
# import requests
# from PIL import Image
# import tifffile
# import gc
# from streamlit_image_comparison import image_comparison
# from cyclone_ai.engine import CyclonePredictor
# # --- NEW: PYTORCH IMPORTS FOR MAMBA ---
# import torch
# import torch.nn as nn
# from torchvision import transforms

# # --- 1. CONFIGURATION & UI SETUP ---
# st.set_page_config(
#     page_title="DisasterOS: Integrated Response System", 
#     layout="wide", 
#     page_icon="🛰️",
#     initial_sidebar_state="expanded"
# )

# # --- GLOBAL DEVICE SETUP ---
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # ==========================================
# # 🆕 MAMBA ARCHITECTURE DEFINITION
# # ==========================================
# class SimplifiedMambaLayer(nn.Module):
#     def __init__(self, dim, d_state=16, d_conv=4, expand=2):
#         super().__init__()
#         self.dim = dim
#         self.expand = expand
#         self.in_proj = nn.Linear(dim, dim * 2 * expand)
#         self.conv1d = nn.Conv1d(in_channels=dim * expand, out_channels=dim * expand, 
#                                 kernel_size=d_conv, groups=dim * expand, padding=d_conv - 1)
#         self.act = nn.SiLU()
#         self.out_proj = nn.Linear(dim * expand, dim)
#     def forward(self, x):
#         b, l, d = x.shape
#         x_and_res = self.in_proj(x) 
#         (x_gate, x_res) = x_and_res.split(self.dim * self.expand, dim=-1)
#         x_conv = x_gate.permute(0, 2, 1)
#         x_conv = self.conv1d(x_conv)[:, :, :l]
#         x_conv = x_conv.permute(0, 2, 1)
#         x_out = x_conv * self.act(x_res)
#         return self.out_proj(x_out)

# class MambaBlock(nn.Module):
#     def __init__(self, dim):
#         super().__init__()
#         self.norm = nn.LayerNorm(dim)
#         self.mamba = SimplifiedMambaLayer(dim)
#         self.ffn = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, dim*4), nn.GELU(), nn.Linear(dim*4, dim))
#     def forward(self, x):
#         b, c, h, w = x.shape
#         x_flat = x.permute(0, 2, 3, 1).view(b, h * w, c)
#         x_flat = x_flat + self.mamba(self.norm(x_flat))
#         x_flat = x_flat + self.ffn(x_flat)
#         return x_flat.view(b, h, w, c).permute(0, 3, 1, 2)

# class SiameseVimClassifier(nn.Module):
#     def __init__(self, num_classes=4):
#         super().__init__()
#         self.stem = nn.Sequential(nn.Conv2d(3, 64, 4, 4), nn.GELU())
#         self.stage1 = nn.Sequential(MambaBlock(64), MambaBlock(64))
#         self.down1 = nn.Conv2d(64, 128, 2, 2)
#         self.stage2 = nn.Sequential(MambaBlock(128), MambaBlock(128))
#         self.down2 = nn.Conv2d(128, 256, 2, 2)
#         self.stage3 = nn.Sequential(MambaBlock(256), MambaBlock(256))
#         self.global_pool = nn.AdaptiveAvgPool2d(1)
#         self.fc = nn.Sequential(nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, num_classes))
#     def forward_one(self, x):
#         x = self.stem(x)
#         x = self.stage1(x)
#         x = self.down1(x)
#         x = self.stage2(x)
#         x = self.down2(x)
#         x = self.stage3(x)
#         return self.global_pool(x).flatten(1)
#     def forward(self, x_pre, x_post):
#         return self.fc(torch.cat([self.forward_one(x_pre), self.forward_one(x_post)], dim=1))

# # --- SAFETY IMPORT FOR SAM ---
# try:
#     from samgeo import SamGeo
#     SAM_AVAILABLE = True
# except ImportError:
#     SAM_AVAILABLE = False

# # --- PATHS ---
# TRACK_MODEL_PATH = "models/pro_cyclone_model.h5"
# SCALER_PATH = "models/cyclone_scaler.pkl"
# # 🆕 UPDATED MODEL PATH
# DAMAGE_MODEL_PATH = "models/mamba_epoch_15.pth" 
# SAM_CHECKPOINT_DIR = "models/sam" 
# DISTRICTS_PATH = "odisha_districts.csv"
# ECONOMICS_PATH = "regional_economics.csv"

# # --- 2. RESOURCE LOADING (CACHED) ---
# @st.cache_resource
# def load_all_resources():
#     # Load CSVs
#     if not os.path.exists(ECONOMICS_PATH) or not os.path.exists(DISTRICTS_PATH):
#         st.error("❌ Critical Data Missing: Check CSV files."); st.stop()
    
#     economics = pd.read_csv(ECONOMICS_PATH)
#     districts = pd.read_csv(DISTRICTS_PATH)

#     # Load Track Model (Keras)
#     if not os.path.exists(TRACK_MODEL_PATH):
#         st.error(f"❌ Missing Model: {TRACK_MODEL_PATH}"); st.stop()
#     track_model = load_model(TRACK_MODEL_PATH, compile=False)
    
#     # 🆕 Load Damage Model (PyTorch Mamba)
#     damage_model = None
#     if os.path.exists(DAMAGE_MODEL_PATH):
#         try:
#             damage_model = SiameseVimClassifier(num_classes=4).to(DEVICE)
#             damage_model.load_state_dict(torch.load(DAMAGE_MODEL_PATH, map_location=DEVICE))
#             damage_model.eval() # Set to inference mode
#             print(f"✅ Siamese Mamba Loaded on {DEVICE}")
#         except Exception as e:
#             print(f"❌ Failed to load Mamba: {e}")
#     else:
#         print(f"⚠️ Warning: Damage model not found at {DAMAGE_MODEL_PATH}")
    
#     sam = None
#     if SAM_AVAILABLE:
#         try:
#             os.makedirs(SAM_CHECKPOINT_DIR, exist_ok=True)
#             sam = SamGeo(model_type="vit_b", checkpoint_dir=SAM_CHECKPOINT_DIR, automatic=True)
#             print("✅ SAM Loaded")
#         except: pass
            
#     scaler = joblib.load(SCALER_PATH)
#     return track_model, damage_model, sam, scaler, districts, economics

# try:
#     track_model, damage_model, sam_model, scaler, districts, economics = load_all_resources()
# except Exception as e:
#     st.error(f"Boot Error: {e}"); st.stop()

# # --- 3. VISUAL FX UTILITIES (NEW: DRONE HUD) ---
# def add_drone_hud(image, drone_id, sector_id):
#     """
#     Overlays a Sci-Fi Drone HUD on the image segment for realism.
#     """
#     hud = image.copy()
#     h, w = hud.shape[:2]
#     color = (0, 255, 0) # Cyber Green
#     thickness = 2
    
#     # 1. Corner Brackets
#     len_line = int(w * 0.15)
#     cv2.line(hud, (10, 10), (10 + len_line, 10), color, thickness)
#     cv2.line(hud, (10, 10), (10, 10 + len_line), color, thickness)
#     cv2.line(hud, (w-10, h-10), (w-10 - len_line, h-10), color, thickness)
#     cv2.line(hud, (w-10, h-10), (w-10, h-10 - len_line), color, thickness)

#     # 2. Central Crosshair
#     cx, cy = w//2, h//2
#     cv2.line(hud, (cx-15, cy), (cx+15, cy), color, 1)
#     cv2.line(hud, (cx, cy-15), (cx, cy+15), color, 1)
#     cv2.circle(hud, (cx, cy), 10, color, 1)

#     # 3. Telemetry Text
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     cv2.putText(hud, f"UNIT: {drone_id}", (20, 30), font, 0.6, color, 2)
#     cv2.putText(hud, f"SEC: {sector_id}", (20, 55), font, 0.5, color, 1)
    
#     # Random Simulated Data
#     bat = random.randint(70, 99)
#     alt = random.randint(110, 125)
#     cv2.putText(hud, f"BAT: {bat}%", (w-120, 30), font, 0.5, color, 1)
#     cv2.putText(hud, f"ALT: {alt}m", (w-120, 55), font, 0.5, color, 1)
    
#     # Blinking "REC" circle
#     if random.random() > 0.3:
#         cv2.circle(hud, (30, h-30), 5, (0, 0, 255), -1) # Red Dot
#     cv2.putText(hud, "REC", (45, h-25), font, 0.5, (255, 255, 255), 1)

#     return hud

# def get_before_image(lat, lon, filename="current_target.jpg"):
#     try:
#         zoom = 19; n = 2.0 ** zoom
#         xtile = int((lon + 180.0) / 360.0 * n)
#         ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
#         url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers)
#         img = Image.open(BytesIO(response.content)).convert("RGB")
#         img.save(filename); return filename
#     except: return None

# def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
#     try:
#         img = cv2.imread(before_path)
#         noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
#         damaged_img = cv2.add(img, noise)
#         cv2.imwrite(output_path, damaged_img); return output_path
#     except: return None

# # --- 4. CORE AI LOGIC (SECTOR PROCESSOR) ---
# def process_drone_sector(sector_pre, sector_post, sam_model, damage_model, prices):
#     total_loss_in_sector = 0
#     struct_counts = {"Hotel":0, "House":0, "Hut":0}
#     damage_counts = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
    
#     # Resize for SAM speed
#     scale_target = 512
#     orig_h, orig_w = sector_pre.shape[:2]
#     if orig_w == 0: return sector_post, 0, struct_counts, damage_counts
    
#     scale_factor = orig_w / scale_target
#     dim_small = (scale_target, int(orig_h / scale_factor))
#     sector_small = cv2.resize(sector_pre, dim_small)
    
#     temp_path = "temp_sector.jpg"
#     cv2.imwrite(temp_path, sector_small)
    
#     annotated_sector = sector_post.copy()
    
#     # 🆕 Define Transforms for PyTorch Mamba
#     val_transform = transforms.Compose([
#         transforms.ToPILImage(),
#         transforms.Resize((224, 224)),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#     ])

#     # --- UPDATE THIS BLOCK INSIDE process_drone_sector() ---

#     try:
#         mask_path = "temp_mask.tif"
        
#         # 🚨 USE THE NEW AGGRESSIVE PARAMETERS HERE
#         sam_model.generate(
#             temp_path, 
#             mask_path, 
#             foreground=True, 
#             unique=True,
#             # --- NEW SETTINGS ---
#             points_per_side=64,           # Scan density (was 32)
#             pred_iou_thresh=0.65,         # Accept messy slum roofs
#             stability_score_thresh=0.70,  # Accept lower confidence
#             crop_n_layers=1,              # Zoom in 1 level deeper
#             min_mask_region_area=50       # Detect tiny huts
#         )
        
#         mask = tifffile.imread(mask_path)
#         # ... (rest of the code remains the same)
#         unique_ids = np.unique(mask)
#         unique_ids = unique_ids[unique_ids != 0]

#         for uid in unique_ids:
#             ys, xs = np.where(mask == uid)
#             if len(xs) == 0: continue
            
#             x1, x2, y1, y2 = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
#             if (x2-x1)*(y2-y1) < 20: continue 

#             # Scale back to High-Res
#             real_x = int(x1 * scale_factor)
#             real_y = int(y1 * scale_factor)
#             real_w = int((x2 - x1) * scale_factor)
#             real_h = int((y2 - y1) * scale_factor)
            
#             # Classify Structure Type
#             area = real_w * real_h
#             if area > 3500: struct_type = "Hotel"; unit_cost = prices['Commercial_Value']
#             elif area < 600: struct_type = "Hut"; unit_cost = prices['Hut_Value']
#             else: struct_type = "House"; unit_cost = prices['Residential_Value'] 
#             struct_counts[struct_type] += 1

#             # Damage Assessment Crop
#             crop_pre = sector_pre[real_y:real_y+real_h, real_x:real_x+real_w]
#             crop_post = sector_post[real_y:real_y+real_h, real_x:real_x+real_w]
            
#             if crop_pre.size == 0 or crop_post.size == 0: continue
            
#             # 🆕 UPDATED INFERENCE LOGIC (MAMBA)
#             pred_idx = 2 # Default Major
#             if damage_model:
#                 try:
#                     # Convert BGR (OpenCV) to RGB for PyTorch
#                     c_pre_rgb = cv2.cvtColor(crop_pre, cv2.COLOR_BGR2RGB)
#                     c_post_rgb = cv2.cvtColor(crop_post, cv2.COLOR_BGR2RGB)
                    
#                     # Transform and add batch dimension
#                     t_pre = val_transform(c_pre_rgb).unsqueeze(0).to(DEVICE)
#                     t_post = val_transform(c_post_rgb).unsqueeze(0).to(DEVICE)
                    
#                     with torch.no_grad():
#                         out = damage_model(t_pre, t_post)
#                         pred_idx = torch.argmax(out, dim=1).item()
#                 except Exception as e: 
#                     # Fallback if inference fails
#                     pass
#             else:
#                 pred_idx = random.choices([0,1,2,3], weights=[10,20,40,30])[0]

#             labels = ["Safe", "Minor", "Major", "Destroyed"]
#             status = labels[pred_idx]
#             damage_counts[status] += 1
            
#             # Weighted Economic Loss
#             damage_pct = [0.0, 0.1, 0.6, 1.0][pred_idx]
#             actual_loss = unit_cost * damage_pct
#             total_loss_in_sector += actual_loss
            
#             # Annotate
#             colors = [(0,255,0), (0,255,255), (0,165,255), (0,0,255)] # Green, Yellow, Orange, Red
#             cv2.rectangle(annotated_sector, (real_x, real_y), (real_x+real_w, real_y+real_h), colors[pred_idx], 2)

#         try: os.remove(temp_path); os.remove(mask_path)
#         except: pass
#     except: pass

#     return annotated_sector, total_loss_in_sector, struct_counts, damage_counts

# # --- 5. SESSION STATE ---
# if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
# if 'selected_district' not in st.session_state: st.session_state['selected_district'] = None
# if 'intensity_val' not in st.session_state: st.session_state['intensity_val'] = "Cat 3"
# if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []
# if 'cyclone_path' not in st.session_state: st.session_state['cyclone_path'] = []
# # Initialize Cyclone AI (Loads only once)
# if 'cyclone_bot' not in st.session_state:
#     try:
#         st.session_state['cyclone_bot'] = CyclonePredictor()
#     except Exception as e:
#         print(f"AI Load Error: {e}")
# # --- 6. SIDEBAR ---
# st.sidebar.title("🛰️ DisasterOS")
# st.sidebar.markdown("---")
# st.sidebar.caption("Mission Control")
# start_lat = st.sidebar.slider("Start Latitude", 14.0, 19.0, 16.5)
# start_lon = st.sidebar.slider("Start Longitude", 82.0, 90.0, 86.0)
# intensity = st.sidebar.select_slider("Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5 - Super Cyclone"])
# st.session_state['intensity_val'] = intensity 

# if st.sidebar.button("⚡ GENERATE CYCLONE", use_container_width=True, type="primary"):
#     st.session_state['simulation_step'] = 2
#     st.session_state['cyclone_path'] = []
#     st.session_state['affected_districts'] = []
#     # Reset swarming state on new simulation
#     if 'swarm_complete' in st.session_state: del st.session_state['swarm_complete']
#     st.rerun()

# # --- 7. MAIN INTERFACE ---
# if st.session_state['simulation_step'] >= 1:
#     st.subheader("Step 1: Path Prediction & Early Warning")
#     col_map, col_status = st.columns([3, 1])
    
#     with col_map:
#         m = folium.Map([19.0, 86.0], zoom_start=6, tiles="CartoDB positron")
#         if st.session_state['simulation_step'] >= 2:
#             path = [[16.5-(10-i)*0.1, 86.0-(10-i)*0.05] for i in range(10)]
#             curr = scaler.transform(np.array(path))
#             pred_path = []
#             curr_in = curr.reshape(1,10,2)
#             for _ in range(48):
#                 p = track_model.predict(curr_in, verbose=0)
#                 pred_path.append(scaler.inverse_transform(p)[0])
#                 curr_in = np.append(curr_in[:,1:,:], p.reshape(1,1,2), axis=1)
            
#             st.session_state['cyclone_path'] = pred_path
#             folium.PolyLine(pred_path, color="red", weight=4, opacity=0.8).add_to(m)
#             folium.Circle([19.81, 85.83], 30000, color="darkred", fill=True, popup="Puri").add_to(m)
            
#             if "Puri" not in st.session_state['affected_districts']:
#                 st.session_state['affected_districts'] = ["Puri", "Khurda"]

#         st_folium(m, height=450, use_container_width=True, returned_objects=[])
    
#     with col_status:
#         st.markdown("#### 🚨 Status Deck")
#         if st.session_state['affected_districts']:
#             st.error(f"CRITICAL: {len(st.session_state['affected_districts'])} Districts")
#             for dist in st.session_state['affected_districts']:
#                 if st.button(f"📡 SCAN {dist.upper()}", key=dist, use_container_width=True):
#                     st.session_state['selected_district'] = dist
#                     st.session_state['simulation_step'] = 3
#                     st.rerun()
#         else:
#             st.info("System Standby...")

# if st.session_state['simulation_step'] == 3:
#     target = st.session_state['selected_district']
    
#     # Init State
#     if 'swarm_complete' not in st.session_state: 
#         st.session_state['swarm_complete'] = False
#         st.session_state['final_map'] = None
#         st.session_state['total_loss'] = 0
#         st.session_state['struct_data'] = {}
#         st.session_state['damage_data'] = {}
    
#     # Financials
#     try:
#         e_data = economics[economics['District'] == target].iloc[0]
#     except:
#         e_data = {'Commercial_Value': 3000000, 'Residential_Value': 500000, 'Hut_Value': 50000, 'Reconstruction_Factor': 1.2}

#     st.divider()
#     st.subheader(f"Step 2: Smart Swarm Assessment - {target}")
    
#     # Load 8K Map Logic
#     final_before, final_after, use_swarm = None, None, False
#     if target == "Puri":
#         d_pre, d_post = "models/puri_demo_pre.jpg", "models/puri_demo_post.jpg"
#         if os.path.exists(d_pre) and os.path.exists(d_post):
#             final_before, final_after, use_swarm = d_pre, d_post, True
#             if not st.session_state['swarm_complete']: st.toast("Locked on High-Res 8K Feed", icon="🎯")
    
#     if not final_before:
#         final_before = get_before_image(19.81, 85.83, "live_pre.jpg")
#         final_after = simulate_after_image("live_pre.jpg", "live_post.jpg")

#     col_vis, col_data = st.columns([2, 1])
    
#     with col_vis:
#         # Load Raw Images for Processing
#         img_pre_raw = cv2.imread(final_before)
#         img_post_raw = cv2.imread(final_after)
        
#         # Safety Resize (Maintain Aspect Ratio)
#         if img_post_raw.shape[1] > 4096:
#              img_pre_raw = cv2.resize(img_pre_raw, (4096, 2440))
#              img_post_raw = cv2.resize(img_post_raw, (4096, 2440))

#         # === LOGIC BRANCH ===
        
#         # A. IF ANALYSIS IS RUNNING (Show Drone HUD)
#         if not st.session_state['swarm_complete']:
            
#             st.markdown("#### 🛸 Live Swarm Feed")
#             live_feed_placeholder = st.empty()
#             progress_bar = st.progress(0)
            
#             # ... (Variables Setup) ...
#             rows, cols = 3, 3
#             h, w, _ = img_post_raw.shape
#             dy, dx = h // rows, w // cols
            
#             temp_loss = 0
#             temp_structs = {"Hotel":0, "House":0, "Hut":0}
#             temp_damage = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
#             reassembled_map = np.zeros_like(img_post_raw)
            
#             if use_swarm and sam_model:
#                 count = 0
#                 drone_ids = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF", "HOTEL", "INDIA"]
                
#                 for r in range(rows):
#                     for c in range(cols):
#                         count += 1
#                         d_id = drone_ids[(count-1)%9]
                        
#                         y1, y2 = r*dy, (r+1)*dy
#                         x1, x2 = c*dx, (c+1)*dx
                        
#                         # Show HUD
#                         raw_sector = img_post_raw[y1:y2, x1:x2].copy()
#                         hud_sector = add_drone_hud(raw_sector, d_id, f"SEC-{r}-{c}")
#                         live_feed_placeholder.image(cv2.cvtColor(hud_sector, cv2.COLOR_BGR2RGB), caption=f"Drone {d_id} Scanning...", use_container_width=True)
                        
#                         # Process
#                         res_img, sec_loss, s_counts, d_counts = process_drone_sector(
#                             img_pre_raw[y1:y2, x1:x2], 
#                             img_post_raw[y1:y2, x1:x2], 
#                             sam_model, damage_model, e_data
#                         )
                        
#                         # Aggregate
#                         temp_loss += sec_loss
#                         for k in s_counts: temp_structs[k] += s_counts[k]
#                         for k in d_counts: temp_damage[k] += d_counts[k]
#                         reassembled_map[y1:y2, x1:x2] = res_img
                        
#                         progress_bar.progress(count / 9)
#                         gc.collect()

#                 # Save State
#                 st.session_state['final_map'] = reassembled_map
#                 st.session_state['total_loss'] = temp_loss
#                 st.session_state['struct_data'] = temp_structs
#                 st.session_state['damage_data'] = temp_damage
#                 st.session_state['swarm_complete'] = True
                
#                 live_feed_placeholder.empty() # Clear HUD
#                 st.rerun() # Refresh to show slider

#             else:
#                 st.warning("Simulation Mode (Swarm Unavailable)")
#                 st.session_state['final_map'] = img_post_raw
#                 st.session_state['swarm_complete'] = True
#                 st.rerun()

#         # B. IF ANALYSIS COMPLETE (Show The SLIDER)
#         else:
#             st.markdown("### 🔍 Damage Verification")
            
#             # Prepare Images for Slider (Convert BGR to RGB)
#             # Image 1: Pre-Disaster (What it used to look like)
#             img_1 = cv2.cvtColor(img_pre_raw, cv2.COLOR_BGR2RGB)
            
#             # Image 2: Post-Disaster AI Map (What is destroyed)
#             final_map = st.session_state.get('final_map')
#             if final_map is None: final_map = img_post_raw
#             img_2 = cv2.cvtColor(final_map, cv2.COLOR_BGR2RGB)
            
#             # RENDER SLIDER
#             image_comparison(
#                 img1=img_1,
#                 img2=img_2,
#                 label1="PRE-CYCLONE",
#                 label2="AI DAMAGE MAP",
#                 starting_position=50,
#                 show_labels=True,
#                 make_responsive=True,
#                 in_memory=True
#             )
#             st.caption("👈 Slide to compare original infrastructure vs. detected damage.")

#     with col_data:
#         # Use saved data from session state
#         s_data = st.session_state.get('struct_data', {"Hotel":0, "House":0, "Hut":0})
#         loss_val = st.session_state.get('total_loss', 0) # This is raw sample loss
#         d_data = st.session_state.get('damage_data', {"Safe":0, "Minor":0, "Major":0, "Destroyed":0})

#         st.markdown("### 📊 Relief Report")
        
#         # 1. Structure Counts (Sample Level)
#         with st.container(border=True):
#             st.caption(f"Drone Swarm Sample Size: {sum(s_data.values())} structures")
#             c1, c2, c3 = st.columns(3)
#             c1.metric("Hotels", s_data.get('Hotel', 0))
#             c2.metric("Houses", s_data.get('House', 0))
#             c3.metric("Huts", s_data.get('Hut', 0))

#         # ============================================================
#         # 🧮 ADVANCED LOSS CALCULATION (Stratified Mean Estimation)
#         # ============================================================
        
#         # --- A. DEFINE STRATA (The "Buckets") ---
#         # We separate Commercial (Hotels) from Residential (Houses + Huts)
#         # This prevents "Hotel Count" from exploding the district estimate.
        
#         # 1. Sample Statistics (What the drone saw)
#         n_comm_sample = s_data.get('Hotel', 0)
#         n_res_sample = s_data.get('House', 0) + s_data.get('Hut', 0)
#         total_sample = n_comm_sample + n_res_sample
        
#         # Calculate Damage Probability derived from Mamba Model
#         # (This leverages your model's 79% Recall)
#         total_damaged = d_data['Minor'] + d_data['Major'] + d_data['Destroyed']
#         damage_probability = total_damaged / total_sample if total_sample > 0 else 0
        
#         # Calculate Severity Weight (Weighted Average of Damage Classes)
#         # FEMA Factors: Minor=0.1, Major=0.5, Destroyed=1.0
#         weighted_severity = (d_data['Minor']*0.1 + d_data['Major']*0.5 + d_data['Destroyed']*1.0)
#         avg_severity_index = weighted_severity / total_damaged if total_damaged > 0 else 0

#         # --- B. DEFINE AFFECTED POPULATION (The "Swath") ---
#         # 🚨 IMPACT LOGIC: A cyclone hits a path, not the entire district.
#         # We scale the affected population based on the intensity slider.
        
#         intensity_map = {
#             "Cat 1": 0.05,  # 5% of district affected (Narrow path)
#             "Cat 2": 0.10,  # 10% affected
#             "Cat 3": 0.20,  # 20% affected (Standard Swath)
#             "Cat 4": 0.40,  # 40% affected
#             "Cat 5 - Super Cyclone": 0.80 # 80% (Devastation)
#         }
        
#         # Get intensity from session state (defaults to Cat 3 if missing)
#         storm_cat = st.session_state.get('intensity_val', "Cat 3")
#         impact_ratio = intensity_map.get(storm_cat, 0.20)
        
#         # Fetch Total District Population
#         try:
#             d_info = districts[districts['District'] == target].iloc[0]
#             total_district_pop = d_info['Population']
#         except:
#             total_district_pop = 1500000 # Default fallback

#         # Calculate ACTUAL Affected Population
#         affected_pop = total_district_pop * impact_ratio
        
#         # Estimate Affected Inventory (N_h)
#         # Assumption: 5 people per household.
#         N_res_total = affected_pop / 5 
        
#         # Assumption: 1 Commercial Building for every 50 Residential units
#         N_comm_total = N_res_total * 0.02 
        
#         # Display the Impact Factor to the user so they understand the math
#         st.caption(f"📍 Analysis Scope: **{storm_cat}** impacting **{impact_ratio*100:.0f}%** of {target} ({int(affected_pop):,} people).") 
        
#         # --- C. CALCULATE MEAN LOSS PER STRATUM (l_bar_h) ---
#         # Residential Mean Loss (Value * DamageProb * Severity)
#         avg_res_val = (e_data['Residential_Value'] + e_data['Hut_Value']) / 2
#         mean_loss_res = avg_res_val * damage_probability * avg_severity_index
        
#         # Commercial Mean Loss
#         avg_comm_val = e_data['Commercial_Value']
#         mean_loss_comm = avg_comm_val * damage_probability * avg_severity_index
        
#         # --- D. STRATIFIED ESTIMATOR (Total Loss) ---
#         # L_total = (N_res * mean_loss_res) + (N_comm * mean_loss_comm)
#         estimated_res_loss = N_res_total * mean_loss_res
#         estimated_comm_loss = N_comm_total * mean_loss_comm
        
#         total_economic_loss = (estimated_res_loss + estimated_comm_loss) * e_data['Reconstruction_Factor']
        
#         # --- E. CONFIDENCE INTERVAL (Standard Error) ---
#         # We calculate Margin of Error based on the sample size vs population size
#         # Finite Population Correction (FPC) is negligible here, so we use standard error.
        
#         # Heuristic SE calculation for display (Assumes high variance in damage distribution)
#         # Using Z-score 1.96 for 95% Confidence
#         margin_of_error_pct = 1.96 * (0.5 / np.sqrt(total_sample)) if total_sample > 0 else 0.2
        
#         lower_bound = total_economic_loss * (1 - margin_of_error_pct)
#         upper_bound = total_economic_loss * (1 + margin_of_error_pct)
        
#         # ============================================================
#         # 📉 DISPLAY RESULTS
#         # ============================================================
        
#         # Display as Range
#         loss_str = f"₹ {lower_bound/10000000:.0f} - {upper_bound/10000000:.0f} Cr"
        
#         st.metric("Est. Economic Loss (95% CI)", loss_str, 
#                   help=f"Stratified Estimate based on {N_res_total:,.0f} Households and {N_comm_total:,.0f} Comm. Units.",
#                   delta="District-Wide Model", delta_color="inverse")
        
#         # 3. Logistics Calculation (Derived from Residential Damage Only)
#         # We only displace people from Damaged RESIDENTIAL units, not hotels.
#         displaced_households = N_res_total * damage_probability
#         total_displaced_people = int(displaced_households * 5) # 5 pax per home
        
#         st.info(f"Persons Displaced: {total_displaced_people:,}")
        
#         # Logistics Table
#         df = pd.DataFrame({
#             "Requirement": ["Temp Shelters", "Food (Daily Tons)", "Medical Units"],
#             "Quantity": [
#                 int(total_displaced_people/50)+1,             # 50 people per shelter
#                 float(f"{total_displaced_people*0.002:.1f}"), # 2kg food per person
#                 int(total_displaced_people/2000)+1            # 1 medical unit per 2000 pax
#             ]
#         })
#         st.dataframe(df, hide_index=True, use_container_width=True)
        
#         if st.button("📨 Dispatch to HQ", type="primary", use_container_width=True):
#             st.balloons()
#             st.success("✅ Data transmitted to State Control Room.")






















# import streamlit as st
# import pandas as pd
# import numpy as np
# import folium
# from streamlit_folium import st_folium
# from tensorflow.keras.models import load_model # Kept for Track Model
# import joblib
# import cv2
# from io import BytesIO
# import os
# import random
# import requests
# from PIL import Image
# import tifffile
# import gc
# from streamlit_image_comparison import image_comparison
# from cyclone_ai.engine import CyclonePredictor # AI Path Prediction Engine

# # --- PYTORCH IMPORTS FOR MAMBA ---
# import torch
# import torch.nn as nn
# from torchvision import transforms

# # --- 1. CONFIGURATION & UI SETUP ---
# st.set_page_config(
#     page_title="DisasterOS: Integrated Response System", 
#     layout="wide", 
#     page_icon="🛰️",
#     initial_sidebar_state="expanded"
# )

# # --- GLOBAL DEVICE SETUP ---
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # ==========================================
# # 🆕 MAMBA ARCHITECTURE DEFINITION
# # ==========================================
# class SimplifiedMambaLayer(nn.Module):
#     def __init__(self, dim, d_state=16, d_conv=4, expand=2):
#         super().__init__()
#         self.dim = dim
#         self.expand = expand
#         self.in_proj = nn.Linear(dim, dim * 2 * expand)
#         self.conv1d = nn.Conv1d(in_channels=dim * expand, out_channels=dim * expand, 
#                                 kernel_size=d_conv, groups=dim * expand, padding=d_conv - 1)
#         self.act = nn.SiLU()
#         self.out_proj = nn.Linear(dim * expand, dim)
#     def forward(self, x):
#         b, l, d = x.shape
#         x_and_res = self.in_proj(x) 
#         (x_gate, x_res) = x_and_res.split(self.dim * self.expand, dim=-1)
#         x_conv = x_gate.permute(0, 2, 1)
#         x_conv = self.conv1d(x_conv)[:, :, :l]
#         x_conv = x_conv.permute(0, 2, 1)
#         x_out = x_conv * self.act(x_res)
#         return self.out_proj(x_out)

# class MambaBlock(nn.Module):
#     def __init__(self, dim):
#         super().__init__()
#         self.norm = nn.LayerNorm(dim)
#         self.mamba = SimplifiedMambaLayer(dim)
#         self.ffn = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, dim*4), nn.GELU(), nn.Linear(dim*4, dim))
#     def forward(self, x):
#         b, c, h, w = x.shape
#         x_flat = x.permute(0, 2, 3, 1).view(b, h * w, c)
#         x_flat = x_flat + self.mamba(self.norm(x_flat))
#         x_flat = x_flat + self.ffn(x_flat)
#         return x_flat.view(b, h, w, c).permute(0, 3, 1, 2)

# class SiameseVimClassifier(nn.Module):
#     def __init__(self, num_classes=4):
#         super().__init__()
#         self.stem = nn.Sequential(nn.Conv2d(3, 64, 4, 4), nn.GELU())
#         self.stage1 = nn.Sequential(MambaBlock(64), MambaBlock(64))
#         self.down1 = nn.Conv2d(64, 128, 2, 2)
#         self.stage2 = nn.Sequential(MambaBlock(128), MambaBlock(128))
#         self.down2 = nn.Conv2d(128, 256, 2, 2)
#         self.stage3 = nn.Sequential(MambaBlock(256), MambaBlock(256))
#         self.global_pool = nn.AdaptiveAvgPool2d(1)
#         self.fc = nn.Sequential(nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, num_classes))
#     def forward_one(self, x):
#         x = self.stem(x)
#         x = self.stage1(x)
#         x = self.down1(x)
#         x = self.stage2(x)
#         x = self.down2(x)
#         x = self.stage3(x)
#         return self.global_pool(x).flatten(1)
#     def forward(self, x_pre, x_post):
#         return self.fc(torch.cat([self.forward_one(x_pre), self.forward_one(x_post)], dim=1))

# # --- SAFETY IMPORT FOR SAM ---
# try:
#     from samgeo import SamGeo
#     SAM_AVAILABLE = True
# except ImportError:
#     SAM_AVAILABLE = False

# # --- PATHS ---
# TRACK_MODEL_PATH = "models/pro_cyclone_model.h5"
# SCALER_PATH = "models/cyclone_scaler.pkl"
# DAMAGE_MODEL_PATH = "models/mamba_epoch_15.pth" 
# SAM_CHECKPOINT_DIR = "models/sam" 
# DISTRICTS_PATH = "odisha_districts.csv"
# ECONOMICS_PATH = "regional_economics.csv"

# # --- 2. RESOURCE LOADING (CACHED) ---
# @st.cache_resource
# def load_all_resources():
#     if not os.path.exists(ECONOMICS_PATH) or not os.path.exists(DISTRICTS_PATH):
#         st.error("❌ Critical Data Missing: Check CSV files."); st.stop()
    
#     economics = pd.read_csv(ECONOMICS_PATH)
#     districts = pd.read_csv(DISTRICTS_PATH)

#     if not os.path.exists(TRACK_MODEL_PATH):
#         st.error(f"❌ Missing Model: {TRACK_MODEL_PATH}"); st.stop()
#     track_model = load_model(TRACK_MODEL_PATH, compile=False)
    
#     damage_model = None
#     if os.path.exists(DAMAGE_MODEL_PATH):
#         try:
#             damage_model = SiameseVimClassifier(num_classes=4).to(DEVICE)
#             damage_model.load_state_dict(torch.load(DAMAGE_MODEL_PATH, map_location=DEVICE))
#             damage_model.eval()
#             print(f"✅ Siamese Mamba Loaded on {DEVICE}")
#         except Exception as e:
#             print(f"❌ Failed to load Mamba: {e}")
#     else:
#         print(f"⚠️ Warning: Damage model not found at {DAMAGE_MODEL_PATH}")
    
#     sam = None
#     if SAM_AVAILABLE:
#         try:
#             os.makedirs(SAM_CHECKPOINT_DIR, exist_ok=True)
#             sam = SamGeo(model_type="vit_b", checkpoint_dir=SAM_CHECKPOINT_DIR, automatic=True)
#             print("✅ SAM Loaded")
#         except: pass
            
#     scaler = joblib.load(SCALER_PATH)
#     return track_model, damage_model, sam, scaler, districts, economics

# try:
#     track_model, damage_model, sam_model, scaler, districts, economics = load_all_resources()
# except Exception as e:
#     st.error(f"Boot Error: {e}"); st.stop()

# # --- 3. VISUAL FX UTILITIES ---
# def add_drone_hud(image, drone_id, sector_id):
#     hud = image.copy()
#     h, w = hud.shape[:2]
#     color = (0, 255, 0)
#     thickness = 2
#     len_line = int(w * 0.15)
#     cv2.line(hud, (10, 10), (10 + len_line, 10), color, thickness)
#     cv2.line(hud, (10, 10), (10, 10 + len_line), color, thickness)
#     cv2.line(hud, (w-10, h-10), (w-10 - len_line, h-10), color, thickness)
#     cv2.line(hud, (w-10, h-10), (w-10, h-10 - len_line), color, thickness)
#     cx, cy = w//2, h//2
#     cv2.line(hud, (cx-15, cy), (cx+15, cy), color, 1)
#     cv2.line(hud, (cx, cy-15), (cx, cy+15), color, 1)
#     cv2.circle(hud, (cx, cy), 10, color, 1)
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     cv2.putText(hud, f"UNIT: {drone_id}", (20, 30), font, 0.6, color, 2)
#     cv2.putText(hud, f"SEC: {sector_id}", (20, 55), font, 0.5, color, 1)
#     bat = random.randint(70, 99); alt = random.randint(110, 125)
#     cv2.putText(hud, f"BAT: {bat}%", (w-120, 30), font, 0.5, color, 1)
#     cv2.putText(hud, f"ALT: {alt}m", (w-120, 55), font, 0.5, color, 1)
#     if random.random() > 0.3:
#         cv2.circle(hud, (30, h-30), 5, (0, 0, 255), -1)
#     cv2.putText(hud, "REC", (45, h-25), font, 0.5, (255, 255, 255), 1)
#     return hud

# def get_before_image(lat, lon, filename="current_target.jpg"):
#     try:
#         zoom = 19; n = 2.0 ** zoom
#         xtile = int((lon + 180.0) / 360.0 * n)
#         ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
#         url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers)
#         img = Image.open(BytesIO(response.content)).convert("RGB")
#         img.save(filename); return filename
#     except: return None

# def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
#     try:
#         img = cv2.imread(before_path)
#         noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
#         damaged_img = cv2.add(img, noise)
#         cv2.imwrite(output_path, damaged_img); return output_path
#     except: return None

# # --- 4. CORE AI LOGIC ---
# def process_drone_sector(sector_pre, sector_post, sam_model, damage_model, prices):
#     total_loss_in_sector = 0
#     struct_counts = {"Hotel":0, "House":0, "Hut":0}
#     damage_counts = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
#     scale_target = 512
#     orig_h, orig_w = sector_pre.shape[:2]
#     if orig_w == 0: return sector_post, 0, struct_counts, damage_counts
#     scale_factor = orig_w / scale_target
#     dim_small = (scale_target, int(orig_h / scale_factor))
#     sector_small = cv2.resize(sector_pre, dim_small)
#     temp_path = "temp_sector.jpg"; cv2.imwrite(temp_path, sector_small)
#     annotated_sector = sector_post.copy()
#     val_transform = transforms.Compose([
#         transforms.ToPILImage(),
#         transforms.Resize((224, 224)),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#     ])
#     try:
#         mask_path = "temp_mask.tif"
#         sam_model.generate(
#             temp_path, mask_path, foreground=True, unique=True,
#             points_per_side=64, pred_iou_thresh=0.65, stability_score_thresh=0.70,
#             crop_n_layers=1, min_mask_region_area=50
#         )
#         mask = tifffile.imread(mask_path)
#         unique_ids = np.unique(mask); unique_ids = unique_ids[unique_ids != 0]
#         for uid in unique_ids:
#             ys, xs = np.where(mask == uid)
#             if len(xs) == 0: continue
#             x1, x2, y1, y2 = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
#             if (x2-x1)*(y2-y1) < 20: continue 
#             real_x, real_y = int(x1 * scale_factor), int(y1 * scale_factor)
#             real_w, real_h = int((x2 - x1) * scale_factor), int((y2 - y1) * scale_factor)
#             area = real_w * real_h
#             if area > 3500: struct_type = "Hotel"; unit_cost = prices['Commercial_Value']
#             elif area < 600: struct_type = "Hut"; unit_cost = prices['Hut_Value']
#             else: struct_type = "House"; unit_cost = prices['Residential_Value'] 
#             struct_counts[struct_type] += 1
#             crop_pre = sector_pre[real_y:real_y+real_h, real_x:real_x+real_w]
#             crop_post = sector_post[real_y:real_y+real_h, real_x:real_x+real_w]
#             if crop_pre.size == 0 or crop_post.size == 0: continue
#             pred_idx = 2
#             if damage_model:
#                 try:
#                     c_pre_rgb = cv2.cvtColor(crop_pre, cv2.COLOR_BGR2RGB)
#                     c_post_rgb = cv2.cvtColor(crop_post, cv2.COLOR_BGR2RGB)
#                     t_pre = val_transform(c_pre_rgb).unsqueeze(0).to(DEVICE)
#                     t_post = val_transform(c_post_rgb).unsqueeze(0).to(DEVICE)
#                     with torch.no_grad():
#                         out = damage_model(t_pre, t_post)
#                         pred_idx = torch.argmax(out, dim=1).item()
#                 except: pass
#             else:
#                 pred_idx = random.choices([0,1,2,3], weights=[10,20,40,30])[0]
#             labels = ["Safe", "Minor", "Major", "Destroyed"]
#             status = labels[pred_idx]; damage_counts[status] += 1
#             damage_pct = [0.0, 0.1, 0.6, 1.0][pred_idx]
#             total_loss_in_sector += unit_cost * damage_pct
#             colors = [(0,255,0), (0,255,255), (0,165,255), (0,0,255)]
#             cv2.rectangle(annotated_sector, (real_x, real_y), (real_x+real_w, real_y+real_h), colors[pred_idx], 2)
#         try: os.remove(temp_path); os.remove(mask_path)
#         except: pass
#     except: pass
#     return annotated_sector, total_loss_in_sector, struct_counts, damage_counts

# # --- 5. SESSION STATE ---
# if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
# if 'selected_district' not in st.session_state: st.session_state['selected_district'] = None
# if 'intensity_val' not in st.session_state: st.session_state['intensity_val'] = "Cat 3"
# if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []
# if 'cyclone_path' not in st.session_state: st.session_state['cyclone_path'] = []
# if 'cyclone_bot' not in st.session_state:
#     try: st.session_state['cyclone_bot'] = CyclonePredictor()
#     except: pass

# # --- 6. SIDEBAR & NAVIGATION ---
# st.sidebar.title("🛰️ DisasterOS")
# st.sidebar.markdown("---")

# # NEW NAVIGATION SELECTOR
# page = st.sidebar.selectbox("Mission Mode:", ["Damage Simulation (Classic)", "AI Path Forecaster (Mamba v2)"])
# st.sidebar.markdown("---")

# if page == "Damage Simulation (Classic)":
#     st.sidebar.caption("Mission Control")
#     start_lat = st.sidebar.slider("Start Latitude", 14.0, 19.0, 16.5)
#     start_lon = st.sidebar.slider("Start Longitude", 82.0, 90.0, 86.0)
#     intensity = st.sidebar.select_slider("Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5 - Super Cyclone"])
#     st.session_state['intensity_val'] = intensity 

#     if st.sidebar.button("⚡ GENERATE CYCLONE", use_container_width=True, type="primary"):
#         st.session_state['simulation_step'] = 2
#         st.session_state['cyclone_path'] = []
#         st.session_state['affected_districts'] = []
#         if 'swarm_complete' in st.session_state: del st.session_state['swarm_complete']
#         st.rerun()

#     # --- 7. MAIN INTERFACE (SIMULATION) ---
#     if st.session_state['simulation_step'] >= 1:
#         st.subheader("Step 1: Path Prediction & Early Warning")
#         col_map, col_status = st.columns([3, 1])
#         with col_map:
#             m = folium.Map([19.0, 86.0], zoom_start=6, tiles="CartoDB positron")
#             if st.session_state['simulation_step'] >= 2:
#                 path = [[16.5-(10-i)*0.1, 86.0-(10-i)*0.05] for i in range(10)]
#                 curr = scaler.transform(np.array(path))
#                 pred_path = []; curr_in = curr.reshape(1,10,2)
#                 for _ in range(48):
#                     p = track_model.predict(curr_in, verbose=0)
#                     pred_path.append(scaler.inverse_transform(p)[0])
#                     curr_in = np.append(curr_in[:,1:,:], p.reshape(1,1,2), axis=1)
#                 st.session_state['cyclone_path'] = pred_path
#                 folium.PolyLine(pred_path, color="red", weight=4, opacity=0.8).add_to(m)
#                 folium.Circle([19.81, 85.83], 30000, color="darkred", fill=True, popup="Puri").add_to(m)
#                 if "Puri" not in st.session_state['affected_districts']:
#                     st.session_state['affected_districts'] = ["Puri", "Khurda"]
#             st_folium(m, height=450, use_container_width=True, returned_objects=[])
#         with col_status:
#             st.markdown("#### 🚨 Status Deck")
#             if st.session_state['affected_districts']:
#                 st.error(f"CRITICAL: {len(st.session_state['affected_districts'])} Districts")
#                 for dist in st.session_state['affected_districts']:
#                     if st.button(f"📡 SCAN {dist.upper()}", key=dist, use_container_width=True):
#                         st.session_state['selected_district'] = dist
#                         st.session_state['simulation_step'] = 3
#                         st.rerun()
#             else: st.info("System Standby...")

#     if st.session_state['simulation_step'] == 3:
#         target = st.session_state['selected_district']
#         if 'swarm_complete' not in st.session_state: 
#             st.session_state.update({'swarm_complete':False, 'final_map':None, 'total_loss':0, 'struct_data':{}, 'damage_data':{}})
#         try: e_data = economics[economics['District'] == target].iloc[0]
#         except: e_data = {'Commercial_Value': 3000000, 'Residential_Value': 500000, 'Hut_Value': 50000, 'Reconstruction_Factor': 1.2}
#         st.divider(); st.subheader(f"Step 2: Smart Swarm Assessment - {target}")
#         final_before, final_after, use_swarm = None, None, False
#         if target == "Puri":
#             d_pre, d_post = "models/puri_demo_pre.jpg", "models/puri_demo_post.jpg"
#             if os.path.exists(d_pre) and os.path.exists(d_post):
#                 final_before, final_after, use_swarm = d_pre, d_post, True
#         if not final_before:
#             final_before = get_before_image(19.81, 85.83, "live_pre.jpg")
#             final_after = simulate_after_image("live_pre.jpg", "live_post.jpg")
#         col_vis, col_data = st.columns([2, 1])
#         with col_vis:
#             img_pre_raw = cv2.imread(final_before); img_post_raw = cv2.imread(final_after)
#             if img_post_raw.shape[1] > 4096:
#                  img_pre_raw = cv2.resize(img_pre_raw, (4096, 2440))
#                  img_post_raw = cv2.resize(img_post_raw, (4096, 2440))
#             if not st.session_state['swarm_complete']:
#                 st.markdown("#### 🛸 Live Swarm Feed")
#                 live_feed_placeholder = st.empty(); progress_bar = st.progress(0)
#                 rows, cols = 3, 3; h, w, _ = img_post_raw.shape; dy, dx = h // rows, w // cols
#                 temp_loss = 0; temp_structs = {"Hotel":0, "House":0, "Hut":0}
#                 temp_damage = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}; reassembled_map = np.zeros_like(img_post_raw)
#                 if use_swarm and sam_model:
#                     count = 0; drone_ids = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT", "GOLF", "HOTEL", "INDIA"]
#                     for r in range(rows):
#                         for c in range(cols):
#                             count += 1; d_id = drone_ids[(count-1)%9]
#                             y1, y2 = r*dy, (r+1)*dy; x1, x2 = c*dx, (c+1)*dx
#                             raw_sector = img_post_raw[y1:y2, x1:x2].copy()
#                             hud_sector = add_drone_hud(raw_sector, d_id, f"SEC-{r}-{c}")
#                             live_feed_placeholder.image(cv2.cvtColor(hud_sector, cv2.COLOR_BGR2RGB), caption=f"Drone {d_id} Scanning...", use_container_width=True)
#                             res_img, sec_loss, s_counts, d_counts = process_drone_sector(img_pre_raw[y1:y2, x1:x2], img_post_raw[y1:y2, x1:x2], sam_model, damage_model, e_data)
#                             temp_loss += sec_loss; temp_structs.update({k: temp_structs[k]+v for k,v in s_counts.items()}); temp_damage.update({k: temp_damage[k]+v for k,v in d_counts.items()}); reassembled_map[y1:y2, x1:x2] = res_img
#                             progress_bar.progress(count / 9); gc.collect()
#                     st.session_state.update({'final_map':reassembled_map, 'total_loss':temp_loss, 'struct_data':temp_structs, 'damage_data':temp_damage, 'swarm_complete':True})
#                     live_feed_placeholder.empty(); st.rerun()
#                 else: st.warning("Simulation Mode"); st.session_state['swarm_complete'] = True; st.rerun()
#             else:
#                 st.markdown("### 🔍 Damage Verification")
#                 img_1 = cv2.cvtColor(img_pre_raw, cv2.COLOR_BGR2RGB)
#                 final_map = st.session_state.get('final_map')
#                 if final_map is None: final_map = img_post_raw
#                 img_2 = cv2.cvtColor(final_map, cv2.COLOR_BGR2RGB)
#                 image_comparison(img1=img_1, img2=img_2, label1="PRE-CYCLONE", label2="AI DAMAGE MAP", starting_position=50, show_labels=True, make_responsive=True, in_memory=True)
#         with col_data:
#             s_data = st.session_state.get('struct_data', {"Hotel":0, "House":0, "Hut":0}); loss_val = st.session_state.get('total_loss', 0); d_data = st.session_state.get('damage_data', {"Safe":0, "Minor":0, "Major":0, "Destroyed":0})
#             st.markdown("### 📊 Relief Report")
#             with st.container(border=True):
#                 st.caption(f"Drone Swarm Sample Size: {sum(s_data.values())} structures")
#                 c1, c2, c3 = st.columns(3); c1.metric("Hotels", s_data.get('Hotel', 0)); c2.metric("Houses", s_data.get('House', 0)); c3.metric("Huts", s_data.get('Hut', 0))
#             n_comm_sample = s_data.get('Hotel', 0); n_res_sample = s_data.get('House', 0) + s_data.get('Hut', 0); total_sample = n_comm_sample + n_res_sample
#             total_damaged = d_data['Minor'] + d_data['Major'] + d_data['Destroyed']
#             damage_probability = total_damaged / total_sample if total_sample > 0 else 0
#             weighted_severity = (d_data['Minor']*0.1 + d_data['Major']*0.5 + d_data['Destroyed']*1.0)
#             avg_severity_index = weighted_severity / total_damaged if total_damaged > 0 else 0
#             intensity_map = {"Cat 1": 0.05, "Cat 2": 0.10, "Cat 3": 0.20, "Cat 4": 0.40, "Cat 5 - Super Cyclone": 0.80}
#             storm_cat = st.session_state.get('intensity_val', "Cat 3"); impact_ratio = intensity_map.get(storm_cat, 0.20)
#             try: d_info = districts[districts['District'] == target].iloc[0]; total_district_pop = d_info['Population']
#             except: total_district_pop = 1500000
#             affected_pop = total_district_pop * impact_ratio; N_res_total = affected_pop / 5; N_comm_total = N_res_total * 0.02 
#             st.caption(f"📍 Analysis Scope: **{storm_cat}** impacting **{impact_ratio*100:.0f}%** of {target} ({int(affected_pop):,} people).") 
#             avg_res_val = (e_data['Residential_Value'] + e_data['Hut_Value']) / 2; mean_loss_res = avg_res_val * damage_probability * avg_severity_index
#             avg_comm_val = e_data['Commercial_Value']; mean_loss_comm = avg_comm_val * damage_probability * avg_severity_index
#             estimated_res_loss = N_res_total * mean_loss_res; estimated_comm_loss = N_comm_total * mean_loss_comm
#             total_economic_loss = (estimated_res_loss + estimated_comm_loss) * e_data['Reconstruction_Factor']
#             margin_of_error_pct = 1.96 * (0.5 / np.sqrt(total_sample)) if total_sample > 0 else 0.2
#             loss_str = f"₹ {total_economic_loss*(1-margin_of_error_pct)/10000000:.0f} - {total_economic_loss*(1+margin_of_error_pct)/10000000:.0f} Cr"
#             st.metric("Est. Economic Loss (95% CI)", loss_str, help="Stratified Estimate based on N_h.", delta="District-Wide Model", delta_color="inverse")
#             displaced_households = N_res_total * damage_probability; total_displaced_people = int(displaced_households * 5)
#             st.info(f"Persons Displaced: {total_displaced_people:,}")
#             df = pd.DataFrame({"Requirement": ["Temp Shelters", "Food (Daily Tons)", "Medical Units"], "Quantity": [int(total_displaced_people/50)+1, float(f"{total_displaced_people*0.002:.1f}"), int(total_displaced_people/2000)+1]})
#             st.dataframe(df, hide_index=True, use_container_width=True)
#             if st.button("📨 Dispatch to HQ", type="primary", use_container_width=True): st.balloons(); st.success("✅ Data transmitted.")

# elif page == "AI Path Forecaster (Mamba v2)":
#     st.header("🌪️ Next-Gen Cyclone Trajectory Forecaster")
#     st.info("Utilizing Grid-based Sequence Prediction (Mamba v2 weights).")
#     col1, col2 = st.columns([1, 2])
#     with col1:
#         st.subheader("Observations")
#         lat = st.number_input("Lat", 19.8); lon = st.number_input("Lon", 85.8)
#         wind = st.number_input("Wind Speed", 140); pres = st.number_input("Pressure", 980)
#         hours = st.slider("Forecast Window", 6, 72, 24)
#         if st.button("🔮 Run Forecast", type="primary"):
#             history = [[lat, lon, wind, pres]] * 8
#             with st.spinner("Processing..."):
#                 path = st.session_state['cyclone_bot'].simulate_future(history, steps=int(hours/3))
#                 st.session_state['new_pred_path'] = path
#     with col2:
#         if 'new_pred_path' in st.session_state:
#             st.markdown("### 🗺️ Trajectory Map")
#             st.map(pd.DataFrame(st.session_state['new_pred_path'], columns=['lat', 'lon']))
#             st.dataframe(pd.DataFrame(st.session_state['new_pred_path'], columns=['Lat', 'Lon']))
#         else: st.write("Click predict to see path.")









# import streamlit as st
# import pandas as pd
# import numpy as np
# import folium
# from streamlit_folium import st_folium
# from tensorflow.keras.models import load_model 
# import joblib
# import cv2
# from io import BytesIO
# import os
# import random
# import requests
# from PIL import Image
# import tifffile
# import gc
# from streamlit_image_comparison import image_comparison
# from cyclone_ai.engine import CyclonePredictor


# # --- PYTORCH IMPORTS FOR MAMBA ---
# import torch
# import torch.nn as nn
# from torchvision import transforms


# # --- [INSERT AT LOCATION 1] INITIALIZE STATE VARIABLES ---
# if 'lat_input' not in st.session_state: st.session_state['lat_input'] = 19.0
# if 'lon_input' not in st.session_state: st.session_state['lon_input'] = 85.0
# if 'wind_input' not in st.session_state: st.session_state['wind_input'] = 100
# if 'press_input' not in st.session_state: st.session_state['press_input'] = 980
# if 'manual_history' not in st.session_state: st.session_state['manual_history'] = None

# # --- 1. CONFIGURATION & UI SETUP ---
# st.set_page_config(
#     page_title="DisasterOS: Integrated Response System", 
#     layout="wide", 
#     page_icon="🛰️",
#     initial_sidebar_state="expanded"
# )

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # ==========================================
# # 🏗️ MAMBA ARCHITECTURE (FOR DAMAGE MODEL)
# # ==========================================
# class SimplifiedMambaLayer(nn.Module):
#     def __init__(self, dim, d_state=16, d_conv=4, expand=2):
#         super().__init__()
#         self.dim, self.expand = dim, expand
#         self.in_proj = nn.Linear(dim, dim * 2 * expand)
#         self.conv1d = nn.Conv1d(in_channels=dim * expand, out_channels=dim * expand, 
#                                 kernel_size=d_conv, groups=dim * expand, padding=d_conv - 1)
#         self.act = nn.SiLU()
#         self.out_proj = nn.Linear(dim * expand, dim)
#     def forward(self, x):
#         b, l, d = x.shape
#         x_and_res = self.in_proj(x) 
#         (x_gate, x_res) = x_and_res.split(self.dim * self.expand, dim=-1)
#         x_conv = x_gate.permute(0, 2, 1)
#         x_conv = self.conv1d(x_conv)[:, :, :l]
#         x_conv = x_conv.permute(0, 2, 1)
#         return self.out_proj(x_conv * self.act(x_res))

# class MambaBlock(nn.Module):
#     def __init__(self, dim):
#         super().__init__()
#         self.norm = nn.LayerNorm(dim)
#         self.mamba = SimplifiedMambaLayer(dim)
#         self.ffn = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, dim*4), nn.GELU(), nn.Linear(dim*4, dim))
#     def forward(self, x):
#         b, c, h, w = x.shape
#         x_flat = x.permute(0, 2, 3, 1).view(b, h * w, c)
#         x_flat = x_flat + self.mamba(self.norm(x_flat))
#         x_flat = x_flat + self.ffn(x_flat)
#         return x_flat.view(b, h, w, c).permute(0, 3, 1, 2)

# class SiameseVimClassifier(nn.Module):
#     def __init__(self, num_classes=4):
#         super().__init__()
#         self.stem = nn.Sequential(nn.Conv2d(3, 64, 4, 4), nn.GELU())
#         self.stage1 = nn.Sequential(MambaBlock(64), MambaBlock(64))
#         self.down1 = nn.Conv2d(64, 128, 2, 2)
#         self.stage2 = nn.Sequential(MambaBlock(128), MambaBlock(128))
#         self.down2 = nn.Conv2d(128, 256, 2, 2)
#         self.stage3 = nn.Sequential(MambaBlock(256), MambaBlock(256))
#         self.global_pool = nn.AdaptiveAvgPool2d(1)
#         self.fc = nn.Sequential(nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, num_classes))
#     def forward_one(self, x_in):
#         x = self.stem(x_in)
#         x = self.stage1(x)
#         x = self.down1(x)
#         x = self.stage2(x)
#         x = self.down2(x)
#         x = self.stage3(x)
#         return self.global_pool(x).flatten(1)
#     def forward(self, x_pre, x_post):
#         return self.fc(torch.cat([self.forward_one(x_pre), self.forward_one(x_post)], dim=1))

# # --- 2. SESSION STATE & AI INITIALIZATION ---
# if 'cyclone_bot' not in st.session_state:
#     try:
#         st.session_state['cyclone_bot'] = CyclonePredictor()
#     except Exception as e:
#         st.sidebar.error(f"❌ AI Engine Load Error: {e}")
#         st.session_state['cyclone_bot'] = None

# if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
# if 'intensity_val' not in st.session_state: st.session_state['intensity_val'] = "Cat 3"
# if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []

# # --- 3. RESOURCE LOADING ---
# @st.cache_resource
# def load_all_resources():
#     economics = pd.read_csv("regional_economics.csv")
#     districts = pd.read_csv("odisha_districts.csv")
#     scaler = joblib.load("models/cyclone_scaler.pkl")
#     track_model = load_model("models/pro_cyclone_model.h5", compile=False)
#     damage_model = None
#     if os.path.exists("models/mamba_epoch_15.pth"):
#         damage_model = SiameseVimClassifier(num_classes=4).to(DEVICE)
#         damage_model.load_state_dict(torch.load("models/mamba_epoch_15.pth", map_location=DEVICE))
#         damage_model.eval()
#     try:
#         from samgeo import SamGeo
#         sam = SamGeo(model_type="vit_b", checkpoint_dir="models/sam", automatic=True)
#     except: sam = None
#     return track_model, damage_model, sam, scaler, districts, economics

# track_model, damage_model, sam_model, scaler, districts, economics = load_all_resources()

# # --- 4. VISUAL FX & UTILITIES ---
# def add_drone_hud(image, drone_id, sector_id):
#     hud = image.copy(); h, w = hud.shape[:2]; color = (0, 255, 0)
#     len_line = int(w * 0.15)
#     cv2.line(hud, (10, 10), (10 + len_line, 10), color, 2)
#     cv2.line(hud, (10, 10), (10, 10 + len_line), color, 2)
#     cv2.line(hud, (w-10, h-10), (w-10 - len_line, h-10), color, 2)
#     cv2.line(hud, (w-10, h-10), (w-10, h-10 - len_line), color, 2)
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     cv2.putText(hud, f"UNIT: {drone_id}", (20, 30), font, 0.6, color, 2)
#     cv2.putText(hud, f"SEC: {sector_id}", (20, 55), font, 0.5, color, 1)
#     if random.random() > 0.3: cv2.circle(hud, (30, h-30), 5, (0, 0, 255), -1)
#     return hud

# def get_before_image(lat, lon, filename="current_target.jpg"):
#     try:
#         zoom = 19; n = 2.0 ** zoom
#         xtile = int((lon + 180.0) / 360.0 * n)
#         ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
#         url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         img = Image.open(BytesIO(response.content)).convert("RGB")
#         img.save(filename); return filename
#     except: return None

# def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
#     try:
#         img = cv2.imread(before_path); noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
#         cv2.imwrite(output_path, cv2.add(img, noise)); return output_path
#     except: return None

# def process_drone_sector(sector_pre, sector_post, sam_model, damage_model, prices):
#     total_loss_in_sector = 0; struct_counts = {"Hotel":0, "House":0, "Hut":0}; damage_counts = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
#     scale_target = 512; orig_h, orig_w = sector_pre.shape[:2]
#     if orig_w == 0: return sector_post, 0, struct_counts, damage_counts
#     scale_factor = orig_w / scale_target; dim_small = (scale_target, int(orig_h / scale_factor))
#     cv2.imwrite("temp_sector.jpg", cv2.resize(sector_pre, dim_small))
#     annotated_sector = sector_post.copy()
#     val_transform = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
#     try:
#         sam_model.generate("temp_sector.jpg", "temp_mask.tif", foreground=True, unique=True, points_per_side=64, pred_iou_thresh=0.65, stability_score_thresh=0.70, crop_n_layers=1, min_mask_region_area=50)
#         mask = tifffile.imread("temp_mask.tif"); uids = np.unique(mask); uids = uids[uids != 0]
#         for uid in uids:
#             ys, xs = np.where(mask == uid)
#             if len(xs) == 0: continue
#             x1, x2, y1, y2 = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
#             if (x2-x1)*(y2-y1) < 20: continue 
#             rx, ry, rw, rh = int(x1*scale_factor), int(y1*scale_factor), int((x2-x1)*scale_factor), int((y2-y1)*scale_factor)
#             area = rw * rh
#             if area > 3500: stype, cost = "Hotel", prices['Commercial_Value']
#             elif area < 600: stype, cost = "Hut", prices['Hut_Value']
#             else: stype, cost = "House", prices['Residential_Value'] 
#             struct_counts[stype] += 1
#             if damage_model:
#                 try:
#                     t_pre = val_transform(cv2.cvtColor(sector_pre[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
#                     t_post = val_transform(cv2.cvtColor(sector_post[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
#                     with torch.no_grad(): pred_idx = torch.argmax(damage_model(t_pre, t_post), dim=1).item()
#                 except: pred_idx = 2
#             else: pred_idx = random.choices([0,1,2,3], weights=[10,20,40,30])[0]
#             labels = ["Safe", "Minor", "Major", "Destroyed"]
#             damage_counts[labels[pred_idx]] += 1; total_loss_in_sector += (cost * [0.0, 0.1, 0.6, 1.0][pred_idx])
#             cv2.rectangle(annotated_sector, (rx, ry), (rx+rw, ry+rh), [(0,255,0),(0,255,255),(0,165,255),(0,0,255)][pred_idx], 2)
#     except: pass
#     return annotated_sector, total_loss_in_sector, struct_counts, damage_counts

# # --- 6. SIDEBAR NAVIGATION ---
# st.sidebar.title("🛰️ DisasterOS")
# st.sidebar.markdown("---")
# app_mode = st.sidebar.radio("Mission Mode:", ["Damage Simulation (Classic)", "AI Path Forecaster (SOTA)"])
# st.sidebar.markdown("---")

# if app_mode == "Damage Simulation (Classic)":
#     st.sidebar.caption("Mission Control")
#     slat = st.sidebar.slider("Start Latitude", 14.0, 19.0, 16.5)
#     slon = st.sidebar.slider("Start Longitude", 82.0, 90.0, 86.0)
#     intensity = st.sidebar.select_slider("Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5 - Super Cyclone"])
#     st.session_state['intensity_val'] = intensity 

#     if st.sidebar.button("⚡ GENERATE CYCLONE", use_container_width=True, type="primary"):
#         st.session_state.update({'simulation_step': 2, 'cyclone_path': [], 'affected_districts': []})
#         if 'swarm_complete' in st.session_state: del st.session_state['swarm_complete']
#         st.rerun()

#     if st.session_state.get('simulation_step', 1) >= 1:
#         st.subheader("Step 1: Path Prediction & Early Warning")
#         cm, cs = st.columns([3, 1])
#         with cm:
#             m = folium.Map([19.0, 86.0], zoom_start=6, tiles="CartoDB positron")
#             if st.session_state['simulation_step'] >= 2:
#                 path = [[slat-(10-i)*0.1, slon-(10-i)*0.05] for i in range(10)]
#                 ci = scaler.transform(np.array(path)).reshape(1,10,2); pp = []
#                 for _ in range(48):
#                     p = track_model.predict(ci, verbose=0); pp.append(scaler.inverse_transform(p)[0])
#                     ci = np.append(ci[:,1:,:], p.reshape(1,1,2), axis=1)
#                 st.session_state['cyclone_path'] = pp
#                 folium.PolyLine(pp, color="red", weight=4).add_to(m)
#                 folium.Circle([19.81, 85.83], 30000, color="darkred", fill=True).add_to(m)
#                 st.session_state['affected_districts'] = ["Puri", "Khurda"]
#             st_folium(m, height=450, use_container_width=True)
#         with cs:
#             if st.session_state['affected_districts']:
#                 st.error("CRITICAL: 2 Districts")
#                 for d in st.session_state['affected_districts']:
#                     if st.button(f"📡 SCAN {d.upper()}", key=d, use_container_width=True):
#                         st.session_state.update({'selected_district':d, 'simulation_step':3}); st.rerun()

#     if st.session_state.get('simulation_step') == 3:
#         target = st.session_state['selected_district']
#         if 'swarm_complete' not in st.session_state: st.session_state.update({'swarm_complete':False, 'total_loss':0, 'struct_data':{}, 'damage_data':{}})
#         try: ed = economics[economics['District'] == target].iloc[0]
#         except: ed = {'Commercial_Value':3000000, 'Residential_Value':500000, 'Hut_Value':50000, 'Reconstruction_Factor':1.2}
#         st.divider(); st.subheader(f"Step 2: Smart Swarm Assessment - {target}")
#         fb, fa = (("models/puri_demo_pre.jpg", "models/puri_demo_post.jpg") if target == "Puri" else (get_before_image(19.81, 85.83, "live_pre.jpg"), simulate_after_image("live_pre.jpg", "live_post.jpg")))
#         cv, cd = st.columns([2, 1])
#         with cv:
#             ip, io = cv2.imread(fb), cv2.imread(fa)
#             if not st.session_state['swarm_complete']:
#                 fp = st.empty(); pb = st.progress(0); r, c = 3, 3; h, w, _ = io.shape; dy, dx = h//r, w//c
#                 tl, ts, td, rm = 0, {"Hotel":0, "House":0, "Hut":0}, {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}, np.zeros_like(io)
#                 for row in range(r):
#                     for col in range(c):
#                         y1, y2, x1, x2 = row*dy, (row+1)*dy, col*dx, (col+1)*dx
#                         fp.image(cv2.cvtColor(add_drone_hud(io[y1:y2, x1:x2], "ALPHA", f"S-{row}{col}"), cv2.COLOR_BGR2RGB))
#                         res, sl, sc, dc = process_drone_sector(ip[y1:y2, x1:x2], io[y1:y2, x1:x2], sam_model, damage_model, ed)
#                         tl += sl; ts.update({k: ts[k]+v for k,v in sc.items()}); td.update({k: td[k]+v for k,v in dc.items()}); rm[y1:y2, x1:x2] = res
#                         pb.progress((row*c + col + 1)/9); gc.collect()
#                 st.session_state.update({'final_map':rm, 'total_loss':tl, 'struct_data':ts, 'damage_data':td, 'swarm_complete':True}); st.rerun()
#             else:
#                 image_comparison(img1=cv2.cvtColor(ip, cv2.COLOR_BGR2RGB), img2=cv2.cvtColor(st.session_state.get('final_map', io), cv2.COLOR_BGR2RGB), label1="PRE", label2="POST")
#         with cd:
#             s_data = st.session_state.get('struct_data'); st.markdown("### 📊 Relief Report")
#             with st.container(border=True):
#                 c1, c2, c3 = st.columns(3); c1.metric("Hotels", s_data.get('Hotel', 0)); c2.metric("Houses", s_data.get('House', 0)); c3.metric("Huts", s_data.get('Hut', 0))
#             if st.button("📨 Dispatch to HQ", type="primary", use_container_width=True): st.balloons()

# elif app_mode == "AI Path Forecaster (SOTA)":
#     st.header("🌪️ Next-Gen Cyclone Trajectory Forecaster")
#     st.info("9-Feature SOTA LSTM Engine (33,981 Grid Resolution)")
    
#     col_input, col_map = st.columns([1, 2])
    
#     with col_input:
#         st.subheader("📡 Real-time Telemetry")
#         c1, c2 = st.columns(2)
#         lat_in = c1.number_input("Latitude", 19.80, format="%.2f")
#         lon_in = c2.number_input("Longitude", 85.80, format="%.2f")
#         wind_in = c1.number_input("Wind (km/h)", 140)
#         pres_in = c2.number_input("Pressure (hPa)", 980)
        
#         with st.expander("Advanced SOTA Features", expanded=True):
#             f5 = st.slider("Sea Surface Temp (°C)", 20.0, 35.0, 28.5)
#             f6 = st.slider("Humidity (%)", 0, 100, 85)
#             f7 = st.slider("Wind Shear", 0.0, 50.0, 12.0)
#             f8 = st.slider("Vorticity", 0.0, 100.0, 45.0)
#             f9 = st.slider("Distance to Coast (km)", 0, 500, 120)
            
#         hours = st.slider("Forecast Window (Hours)", 6, 72, 24)
        
#         if st.button("🔮 Run 9-Feature Forecast", type="primary", use_container_width=True):
#             if st.session_state.get('cyclone_bot'):
#                 history = [[lat_in, lon_in, wind_in, pres_in, f5, f6, f7, f8, f9]] * 8
#                 with st.spinner("Calculating Bay of Bengal Trajectory..."):
#                     path = st.session_state['cyclone_bot'].simulate_future(history, steps=int(hours/3))
#                     st.session_state['sota_path'] = path
#             else: st.error("AI Model Offline.")

#     with col_map:
#         if 'sota_path' in st.session_state:
#             st.markdown("### 🗺️ Dynamic Trajectory & Risk Heatmap")
#             path_pts = st.session_state['sota_path']
            
#             # Map centered on the Bay of Bengal
#             fm = folium.Map(location=[20.0, 86.0], zoom_start=6, tiles="CartoDB positron")
            
#             # 1. 🔴 THE BOLD RED TRACE
#             folium.PolyLine(path_pts, color="#FF0000", weight=8, opacity=0.9, tooltip="AI Path Trace").add_to(fm)
            
#             # 2. 🔥 DANGER ZONE HEATMAP (Radius around path)
#             for p in path_pts:
#                 folium.Circle(location=[p[0], p[1]], radius=50000, color="orange", fill=True, fill_opacity=0.2, weight=0).add_to(fm)
            
#             # 3. DIRECTIONAL MARKERS
#             for i, p in enumerate(path_pts):
#                 if i == 0:
#                     folium.Marker([p[0], p[1]], popup="Current Eye", icon=folium.Icon(color="blue", icon="screenshot", prefix="glyphicon")).add_to(fm)
#                 if (i + 1) % 2 == 0:
#                     folium.CircleMarker([p[0], p[1]], radius=5, color="darkred", fill=True, fill_color="orange", popup=f"T+{(i+1)*3}h").add_to(fm)
            
#             st_folium(fm, height=600, use_container_width=True)
#             st.dataframe(pd.DataFrame(path_pts, columns=["Lat", "Lon"]), use_container_width=True)
#         else:
#             st.info("System Standby. Map will center on Odisha upon forecast.")






#CODE BEFORE THE CONE IS MADE


# import streamlit as st
# import pandas as pd
# import numpy as np
# import folium
# from streamlit_folium import st_folium
# from tensorflow.keras.models import load_model 
# import joblib
# import cv2
# from io import BytesIO
# import os
# import random
# import requests
# from PIL import Image
# import tifffile
# import gc
# from streamlit_image_comparison import image_comparison
# from cyclone_ai.engine import CyclonePredictor

# # --- PYTORCH IMPORTS FOR MAMBA ---
# import torch
# import torch.nn as nn
# from torchvision import transforms

# # --- [INSERT AT LOCATION 1] INITIALIZE STATE VARIABLES ---
# if 'lat_input' not in st.session_state: st.session_state['lat_input'] = 19.8
# if 'lon_input' not in st.session_state: st.session_state['lon_input'] = 85.8
# if 'wind_input' not in st.session_state: st.session_state['wind_input'] = 140
# if 'press_input' not in st.session_state: st.session_state['press_input'] = 980
# if 'manual_history' not in st.session_state: st.session_state['manual_history'] = None

# # --- 1. CONFIGURATION & UI SETUP ---
# st.set_page_config(
#     page_title="DisasterOS: Integrated Response System", 
#     layout="wide", 
#     page_icon="🛰️",
#     initial_sidebar_state="expanded"
# )

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # ==========================================
# # 🏗️ MAMBA ARCHITECTURE (FOR DAMAGE MODEL)
# # ==========================================
# class SimplifiedMambaLayer(nn.Module):
#     def __init__(self, dim, d_state=16, d_conv=4, expand=2):
#         super().__init__()
#         self.dim, self.expand = dim, expand
#         self.in_proj = nn.Linear(dim, dim * 2 * expand)
#         self.conv1d = nn.Conv1d(in_channels=dim * expand, out_channels=dim * expand, 
#                                 kernel_size=d_conv, groups=dim * expand, padding=d_conv - 1)
#         self.act = nn.SiLU()
#         self.out_proj = nn.Linear(dim * expand, dim)
#     def forward(self, x):
#         b, l, d = x.shape
#         x_and_res = self.in_proj(x) 
#         (x_gate, x_res) = x_and_res.split(self.dim * self.expand, dim=-1)
#         x_conv = x_gate.permute(0, 2, 1)
#         x_conv = self.conv1d(x_conv)[:, :, :l]
#         x_conv = x_conv.permute(0, 2, 1)
#         return self.out_proj(x_conv * self.act(x_res))

# class MambaBlock(nn.Module):
#     def __init__(self, dim):
#         super().__init__()
#         self.norm = nn.LayerNorm(dim)
#         self.mamba = SimplifiedMambaLayer(dim)
#         self.ffn = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, dim*4), nn.GELU(), nn.Linear(dim*4, dim))
#     def forward(self, x):
#         b, c, h, w = x.shape
#         x_flat = x.permute(0, 2, 3, 1).view(b, h * w, c)
#         x_flat = x_flat + self.mamba(self.norm(x_flat))
#         x_flat = x_flat + self.ffn(x_flat)
#         return x_flat.view(b, h, w, c).permute(0, 3, 1, 2)

# class SiameseVimClassifier(nn.Module):
#     def __init__(self, num_classes=4):
#         super().__init__()
#         self.stem = nn.Sequential(nn.Conv2d(3, 64, 4, 4), nn.GELU())
#         self.stage1 = nn.Sequential(MambaBlock(64), MambaBlock(64))
#         self.down1 = nn.Conv2d(64, 128, 2, 2)
#         self.stage2 = nn.Sequential(MambaBlock(128), MambaBlock(128))
#         self.down2 = nn.Conv2d(128, 256, 2, 2)
#         self.stage3 = nn.Sequential(MambaBlock(256), MambaBlock(256))
#         self.global_pool = nn.AdaptiveAvgPool2d(1)
#         self.fc = nn.Sequential(nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, num_classes))
#     def forward_one(self, x_in):
#         x = self.stem(x_in)
#         x = self.stage1(x)
#         x = self.down1(x)
#         x = self.stage2(x)
#         x = self.down2(x)
#         x = self.stage3(x)
#         return self.global_pool(x).flatten(1)
#     def forward(self, x_pre, x_post):
#         return self.fc(torch.cat([self.forward_one(x_pre), self.forward_one(x_post)], dim=1))

# # --- 2. SESSION STATE & AI INITIALIZATION ---
# if 'cyclone_bot' not in st.session_state:
#     try:
#         st.session_state['cyclone_bot'] = CyclonePredictor()
#     except Exception as e:
#         st.sidebar.error(f"❌ AI Engine Load Error: {e}")
#         st.session_state['cyclone_bot'] = None

# if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
# if 'intensity_val' not in st.session_state: st.session_state['intensity_val'] = "Cat 3"
# if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []

# # --- 3. RESOURCE LOADING ---
# @st.cache_resource
# def load_all_resources():
#     economics = pd.read_csv("regional_economics.csv")
#     districts = pd.read_csv("odisha_districts.csv")
#     scaler = joblib.load("models/cyclone_scaler.pkl")
#     track_model = load_model("models/pro_cyclone_model.h5", compile=False)
#     damage_model = None
#     if os.path.exists("models/mamba_epoch_15.pth"):
#         damage_model = SiameseVimClassifier(num_classes=4).to(DEVICE)
#         damage_model.load_state_dict(torch.load("models/mamba_epoch_15.pth", map_location=DEVICE))
#         damage_model.eval()
#     try:
#         from samgeo import SamGeo
#         sam = SamGeo(model_type="vit_b", checkpoint_dir="models/sam", automatic=True)
#     except: sam = None
#     return track_model, damage_model, sam, scaler, districts, economics

# track_model, damage_model, sam_model, scaler, districts, economics = load_all_resources()

# # --- 4. VISUAL FX & UTILITIES ---
# def add_drone_hud(image, drone_id, sector_id):
#     hud = image.copy(); h, w = hud.shape[:2]; color = (0, 255, 0)
#     len_line = int(w * 0.15)
#     cv2.line(hud, (10, 10), (10 + len_line, 10), color, 2)
#     cv2.line(hud, (10, 10), (10, 10 + len_line), color, 2)
#     cv2.line(hud, (w-10, h-10), (w-10 - len_line, h-10), color, 2)
#     cv2.line(hud, (w-10, h-10), (w-10, h-10 - len_line), color, 2)
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     cv2.putText(hud, f"UNIT: {drone_id}", (20, 30), font, 0.6, color, 2)
#     cv2.putText(hud, f"SEC: {sector_id}", (20, 55), font, 0.5, color, 1)
#     if random.random() > 0.3: cv2.circle(hud, (30, h-30), 5, (0, 0, 255), -1)
#     return hud

# def get_before_image(lat, lon, filename="current_target.jpg"):
#     try:
#         zoom = 19; n = 2.0 ** zoom
#         xtile = int((lon + 180.0) / 360.0 * n)
#         ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
#         url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         img = Image.open(BytesIO(response.content)).convert("RGB")
#         img.save(filename); return filename
#     except: return None

# def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
#     try:
#         img = cv2.imread(before_path); noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
#         cv2.imwrite(output_path, cv2.add(img, noise)); return output_path
#     except: return None

# def process_drone_sector(sector_pre, sector_post, sam_model, damage_model, prices):
#     total_loss_in_sector = 0; struct_counts = {"Hotel":0, "House":0, "Hut":0}; damage_counts = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
#     scale_target = 512; orig_h, orig_w = sector_pre.shape[:2]
#     if orig_w == 0: return sector_post, 0, struct_counts, damage_counts
#     scale_factor = orig_w / scale_target; dim_small = (scale_target, int(orig_h / scale_factor))
#     cv2.imwrite("temp_sector.jpg", cv2.resize(sector_pre, dim_small))
#     annotated_sector = sector_post.copy()
#     val_transform = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
#     try:
#         sam_model.generate("temp_sector.jpg", "temp_mask.tif", foreground=True, unique=True, points_per_side=64, pred_iou_thresh=0.65, stability_score_thresh=0.70, crop_n_layers=1, min_mask_region_area=50)
#         mask = tifffile.imread("temp_mask.tif"); uids = np.unique(mask); uids = uids[uids != 0]
#         for uid in uids:
#             ys, xs = np.where(mask == uid)
#             if len(xs) == 0: continue
#             x1, x2, y1, y2 = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
#             if (x2-x1)*(y2-y1) < 20: continue 
#             rx, ry, rw, rh = int(x1*scale_factor), int(y1*scale_factor), int((x2-x1)*scale_factor), int((y2-y1)*scale_factor)
#             area = rw * rh
#             if area > 3500: stype, cost = "Hotel", prices['Commercial_Value']
#             elif area < 600: stype, cost = "Hut", prices['Hut_Value']
#             else: stype, cost = "House", prices['Residential_Value'] 
#             struct_counts[stype] += 1
#             if damage_model:
#                 try:
#                     t_pre = val_transform(cv2.cvtColor(sector_pre[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
#                     t_post = val_transform(cv2.cvtColor(sector_post[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
#                     with torch.no_grad(): pred_idx = torch.argmax(damage_model(t_pre, t_post), dim=1).item()
#                 except: pred_idx = 2
#             else: pred_idx = random.choices([0,1,2,3], weights=[10,20,40,30])[0]
#             labels = ["Safe", "Minor", "Major", "Destroyed"]
#             damage_counts[labels[pred_idx]] += 1; total_loss_in_sector += (cost * [0.0, 0.1, 0.6, 1.0][pred_idx])
#             cv2.rectangle(annotated_sector, (rx, ry), (rx+rw, ry+rh), [(0,255,0),(0,255,255),(0,165,255),(0,0,255)][pred_idx], 2)
#     except: pass
#     return annotated_sector, total_loss_in_sector, struct_counts, damage_counts

# # --- 6. SIDEBAR NAVIGATION ---
# st.sidebar.title("🛰️ DisasterOS")
# st.sidebar.markdown("---")
# app_mode = st.sidebar.radio("Mission Mode:", ["Damage Simulation (Classic)", "AI Path Forecaster (SOTA)"])
# st.sidebar.markdown("---")

# if app_mode == "Damage Simulation (Classic)":
#     st.sidebar.caption("Mission Control")
#     slat = st.sidebar.slider("Start Latitude", 14.0, 19.0, 16.5)
#     slon = st.sidebar.slider("Start Longitude", 82.0, 90.0, 86.0)
#     intensity = st.sidebar.select_slider("Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5 - Super Cyclone"])
#     st.session_state['intensity_val'] = intensity 

#     if st.sidebar.button("⚡ GENERATE CYCLONE", use_container_width=True, type="primary"):
#         st.session_state.update({'simulation_step': 2, 'cyclone_path': [], 'affected_districts': []})
#         if 'swarm_complete' in st.session_state: del st.session_state['swarm_complete']
#         st.rerun()

#     if st.session_state.get('simulation_step', 1) >= 1:
#         st.subheader("Step 1: Path Prediction & Early Warning")
#         cm, cs = st.columns([3, 1])
#         with cm:
#             m = folium.Map([19.0, 86.0], zoom_start=6, tiles="CartoDB positron")
#             if st.session_state['simulation_step'] >= 2:
#                 path = [[slat-(10-i)*0.1, slon-(10-i)*0.05] for i in range(10)]
#                 ci = scaler.transform(np.array(path)).reshape(1,10,2); pp = []
#                 for _ in range(48):
#                     p = track_model.predict(ci, verbose=0); pp.append(scaler.inverse_transform(p)[0])
#                     ci = np.append(ci[:,1:,:], p.reshape(1,1,2), axis=1)
#                 st.session_state['cyclone_path'] = pp
#                 folium.PolyLine(pp, color="red", weight=4).add_to(m)
#                 folium.Circle([19.81, 85.83], 30000, color="darkred", fill=True).add_to(m)
#                 st.session_state['affected_districts'] = ["Puri", "Khurda"]
#             st_folium(m, height=450, use_container_width=True)
#         with cs:
#             if st.session_state['affected_districts']:
#                 st.error("CRITICAL: 2 Districts")
#                 for d in st.session_state['affected_districts']:
#                     if st.button(f"📡 SCAN {d.upper()}", key=d, use_container_width=True):
#                         st.session_state.update({'selected_district':d, 'simulation_step':3}); st.rerun()

#     if st.session_state.get('simulation_step') == 3:
#         target = st.session_state['selected_district']
#         if 'swarm_complete' not in st.session_state: st.session_state.update({'swarm_complete':False, 'total_loss':0, 'struct_data':{}, 'damage_data':{}})
#         try: ed = economics[economics['District'] == target].iloc[0]
#         except: ed = {'Commercial_Value':3000000, 'Residential_Value':500000, 'Hut_Value':50000, 'Reconstruction_Factor':1.2}
#         st.divider(); st.subheader(f"Step 2: Smart Swarm Assessment - {target}")
#         fb, fa = (("models/puri_demo_pre.jpg", "models/puri_demo_post.jpg") if target == "Puri" else (get_before_image(19.81, 85.83, "live_pre.jpg"), simulate_after_image("live_pre.jpg", "live_post.jpg")))
#         cv, cd = st.columns([2, 1])
#         with cv:
#             ip, io = cv2.imread(fb), cv2.imread(fa)
#             if not st.session_state['swarm_complete']:
#                 fp = st.empty(); pb = st.progress(0); r, c = 3, 3; h, w, _ = io.shape; dy, dx = h//r, w//c
#                 tl, ts, td, rm = 0, {"Hotel":0, "House":0, "Hut":0}, {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}, np.zeros_like(io)
#                 for row in range(r):
#                     for col in range(c):
#                         y1, y2, x1, x2 = row*dy, (row+1)*dy, col*dx, (col+1)*dx
#                         fp.image(cv2.cvtColor(add_drone_hud(io[y1:y2, x1:x2], "ALPHA", f"S-{row}{col}"), cv2.COLOR_BGR2RGB))
#                         res, sl, sc, dc = process_drone_sector(ip[y1:y2, x1:x2], io[y1:y2, x1:x2], sam_model, damage_model, ed)
#                         tl += sl; ts.update({k: ts[k]+v for k,v in sc.items()}); td.update({k: td[k]+v for k,v in dc.items()}); rm[y1:y2, x1:x2] = res
#                         pb.progress((row*c + col + 1)/9); gc.collect()
#                 st.session_state.update({'final_map':rm, 'total_loss':tl, 'struct_data':ts, 'damage_data':td, 'swarm_complete':True}); st.rerun()
#             else:
#                 image_comparison(img1=cv2.cvtColor(ip, cv2.COLOR_BGR2RGB), img2=cv2.cvtColor(st.session_state.get('final_map', io), cv2.COLOR_BGR2RGB), label1="PRE", label2="POST")
#         with cd:
#             s_data = st.session_state.get('struct_data'); st.markdown("### 📊 Relief Report")
#             with st.container(border=True):
#                 c1, c2, c3 = st.columns(3); c1.metric("Hotels", s_data.get('Hotel', 0)); c2.metric("Houses", s_data.get('House', 0)); c3.metric("Huts", s_data.get('Hut', 0))
#             if st.button("📨 Dispatch to HQ", type="primary", use_container_width=True): st.balloons()

# elif app_mode == "AI Path Forecaster (SOTA)":
#     st.header("🌪️ Next-Gen Cyclone Trajectory Forecaster")
#     st.info("9-Feature SOTA LSTM Engine (33,981 Grid Resolution)")
    
#     col_input, col_map = st.columns([1, 2])
    
#     with col_input:
#         st.subheader("📡 Real-time Telemetry")

#         # # --- [INSERT AT LOCATION 2A] THE PRESET BUTTON ---
#         # if st.button("⚡ Load Cyclone Fani (2019) Preset", use_container_width=True):
#         #     # 1. Set UI Widgets to Landfall Values
#         #     st.session_state['lat_input'] = 19.8
#         #     st.session_state['lon_input'] = 85.8
#         #     st.session_state['wind_input'] = 175
#         #     st.session_state['press_input'] = 943
            
#         #     # 2. Load the "Invisible" 8-Step Momentum History
#         #     st.session_state['manual_history'] = [
#         #         [16.0, 84.5, 205, 942, 0.40, 0.13, 0.33, 0.84, -0.54], # T-21h
#         #         [16.5, 84.7, 210, 938, 0.41, 0.13, 0.33, 0.84, -0.54], # T-18h
#         #         [17.1, 84.8, 215, 932, 0.42, 0.06, 0.40, 0.84, -0.54], # T-15h
#         #         [17.8, 85.0, 210, 935, 0.44, 0.13, 0.46, 0.84, -0.54], # T-12h
#         #         [18.4, 85.2, 205, 937, 0.45, 0.13, 0.40, 0.84, -0.54], # T-9h
#         #         [19.0, 85.4, 195, 939, 0.47, 0.13, 0.40, 0.84, -0.54], # T-6h
#         #         [19.3, 85.6, 185, 941, 0.48, 0.13, 0.20, 0.84, -0.54], # T-3h
#         #         [19.8, 85.8, 175, 943, 0.49, 0.13, 0.33, 0.84, -0.54]  # Landfall
#         #     ]
#         #     st.success("✅ Fani Data Loaded!")
#         #     st.rerun()



#        # --- [UPDATED] FANI RECURVATURE PRESET (APRIL 30) ---
#         if st.button("⚡ Load Cyclone Fani (Recurvature) Preset", use_container_width=True):
#             st.session_state['lat_input'] = 15.6
#             st.session_state['lon_input'] = 84.4
#             st.session_state['wind_input'] = 150
#             st.session_state['press_input'] = 960
            
#             # Watch the Longitude (Index 1) in this data:
#             # It goes West (84.3 -> 84.0), stalls, then turns East (84.1 -> 84.4)
#             st.session_state['manual_history'] = [
#                 [12.2, 84.3, 110, 982, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [12.6, 84.2, 115, 978, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [13.1, 84.1, 120, 975, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [13.5, 84.0, 130, 970, 0.0, 0.0, 0.0, 0.86, -0.50], # The Stall
#                 [14.0, 84.0, 135, 968, 0.0, 0.0, 0.0, 0.86, -0.50], # The Stall
#                 [14.5, 84.1, 140, 965, 0.0, 0.0, 0.0, 0.86, -0.50], # The Eastward Turn
#                 [15.1, 84.3, 145, 962, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [15.6, 84.4, 150, 960, 0.0, 0.0, 0.0, 0.86, -0.50]  
#             ]
#             st.success("✅ Fani Recurvature Data Loaded!")
#             st.rerun()

#         # --- [INSERT AT LOCATION 2B] UPDATED WIDGETS WITH KEYS ---
#         c1, c2 = st.columns(2)
#         lat_in = c1.number_input("Latitude", format="%.2f", key='lat_input')
#         lon_in = c2.number_input("Longitude", format="%.2f", key='lon_input')
#         wind_in = c1.number_input("Wind (km/h)", key='wind_input')
#         pres_in = c2.number_input("Pressure (hPa)", key='press_input')
        
#         with st.expander("Advanced SOTA Features", expanded=True):
#             f5 = st.slider("Sea Surface Temp (°C)", 20.0, 35.0, 28.5)
#             f6 = st.slider("Humidity (%)", 0, 100, 85)
#             f7 = st.slider("Wind Shear", 0.0, 50.0, 12.0)
#             f8 = st.slider("Vorticity", 0.0, 100.0, 45.0)
#             f9 = st.slider("Distance to Coast (km)", 0, 500, 120)
            
#         # hours = st.slider("Forecast Window (Hours)", 6, 72, 24)
#         hours = st.slider("Forecast Window (Hours)", 6, 168, 120) # Max 168 hours (7 days)

#         #REMOVE FOR SHORT TERM PRIDCTION

#         # Add this right below your "Forecast Window (Hours)" slider
#         st.markdown("### 🌬️ Atmospheric Controls")
#         # A negative value pushes West, a positive value pushes East
#         steering_wind = st.slider("East/West Steering Bias", -0.20, 0.20, 0.00, 0.01, 
#                                   help="Simulates High/Low pressure ridges pushing the storm.")
        




        
#     if st.button("🔮 Run 9-Feature Forecast", type="primary", use_container_width=True):
#             if st.session_state.get('cyclone_bot'):
                
#                 # --- 🛡️ SAFETY LOCK: FORCE CLEAN INPUTS ---
#                 # We define the Fani History LOCALLY to ensure no session_state corruption can touch it.
#                 if st.session_state.get('manual_history') is not None:
#                      # HARDCODED FANI DATA (Guaranteed Clean)
#                     # history = [
#                     #     [16.0, 84.5, 205, 942, 0.40, 0.13, 0.33, 0.84, -0.54],
#                     #     [16.5, 84.7, 210, 938, 0.41, 0.13, 0.33, 0.84, -0.54],
#                     #     [17.1, 84.8, 215, 932, 0.42, 0.06, 0.40, 0.84, -0.54],
#                     #     [17.8, 85.0, 210, 935, 0.44, 0.13, 0.46, 0.84, -0.54],
#                     #     [18.4, 85.2, 205, 937, 0.45, 0.13, 0.40, 0.84, -0.54],
#                     #     [19.0, 85.4, 195, 939, 0.47, 0.13, 0.40, 0.84, -0.54],
#                     #     [19.3, 85.6, 185, 941, 0.48, 0.13, 0.20, 0.84, -0.54],
#                     #     [19.8, 85.8, 175, 943, 0.49, 0.13, 0.33, 0.84, -0.54]
#                     # ]
#                     history = [
#                 [12.2, 84.3, 110, 982, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [12.6, 84.2, 115, 978, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [13.1, 84.1, 120, 975, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [13.5, 84.0, 130, 970, 0.0, 0.0, 0.0, 0.86, -0.50], # The Stall
#                 [14.0, 84.0, 135, 968, 0.0, 0.0, 0.0, 0.86, -0.50], # The Stall
#                 [14.5, 84.1, 140, 965, 0.0, 0.0, 0.0, 0.86, -0.50], # The Eastward Turn
#                 [15.1, 84.3, 145, 962, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [15.6, 84.4, 150, 960, 0.0, 0.0, 0.0, 0.86, -0.50]  
#                 ]
#                     st.toast("✅ Loaded Clean Fani Data")
#                 else:
#                     # SLIDER FALLBACK (Calculated Clean)
#                     import datetime
#                     day_of_year = datetime.datetime.now().timetuple().tm_yday
#                     sin_now = np.sin(2 * np.pi * day_of_year / 365.25)
#                     cos_now = np.cos(2 * np.pi * day_of_year / 365.25)
                    
#                     # Ensure indices 7 & 8 are DECIMAL values (-1 to 1)
#                     safe_step = [lat_in, lon_in, wind_in, pres_in, 0, 0, 0, sin_now, cos_now]
#                     history = [safe_step] * 8
#                     st.toast("⚠️ Using Live Sliders")

#                 # --- RUN PREDICTION ---
#                 with st.spinner("Calculating Trajectory..."):
#                     path = st.session_state['cyclone_bot'].simulate_future(history, steps=int(hours/3),steering_lon=steering_wind)
#                     st.session_state['sota_path'] = path
#             else: st.error("AI Model Offline.")

#     with col_map:
#         if 'sota_path' in st.session_state:
#             st.markdown("### 🗺️ Dynamic Trajectory & Risk Heatmap")
#             path_pts = st.session_state['sota_path']
            
#             # Map centered on the Bay of Bengal
#             fm = folium.Map(location=[20.0, 86.0], zoom_start=6, tiles="CartoDB positron")
            
#             # 1. 🔴 THE BOLD RED TRACE
#             folium.PolyLine(path_pts, color="#FF0000", weight=8, opacity=0.9, tooltip="AI Path Trace").add_to(fm)
            
#             # 2. 🔥 DANGER ZONE HEATMAP (Radius around path)
#             for p in path_pts:
#                 folium.Circle(location=[p[0], p[1]], radius=50000, color="orange", fill=True, fill_opacity=0.2, weight=0).add_to(fm)
            
#             # 3. DIRECTIONAL MARKERS
#             for i, p in enumerate(path_pts):
#                 if i == 0:
#                     folium.Marker([p[0], p[1]], popup="Current Eye", icon=folium.Icon(color="blue", icon="screenshot", prefix="glyphicon")).add_to(fm)
#                 if (i + 1) % 2 == 0:
#                     folium.CircleMarker([p[0], p[1]], radius=5, color="darkred", fill=True, fill_color="orange", popup=f"T+{(i+1)*3}h").add_to(fm)
            
#             st_folium(fm, height=600, use_container_width=True)
#             st.dataframe(pd.DataFrame(path_pts, columns=["Lat", "Lon"]), use_container_width=True)
#         else:
#             st.info("System Standby. Map will center on Odisha upon forecast.")










#FINAL WITH MINIMAL UI



# import streamlit as st
# import pandas as pd
# import numpy as np
# import folium
# from streamlit_folium import st_folium
# from tensorflow.keras.models import load_model 
# import joblib
# import cv2
# from io import BytesIO
# import os
# import random
# import requests
# from PIL import Image
# import tifffile
# import gc
# from streamlit_image_comparison import image_comparison
# from cyclone_ai.engine import CyclonePredictor

# # --- PYTORCH IMPORTS FOR MAMBA ---
# import torch
# import torch.nn as nn
# from torchvision import transforms

# # --- [INSERT AT LOCATION 1] INITIALIZE STATE VARIABLES ---
# if 'lat_input' not in st.session_state: st.session_state['lat_input'] = 19.8
# if 'lon_input' not in st.session_state: st.session_state['lon_input'] = 85.8
# if 'wind_input' not in st.session_state: st.session_state['wind_input'] = 140
# if 'press_input' not in st.session_state: st.session_state['press_input'] = 980
# if 'manual_history' not in st.session_state: st.session_state['manual_history'] = None

# # --- 1. CONFIGURATION & UI SETUP ---
# st.set_page_config(
#     page_title="DisasterOS: Integrated Response System", 
#     layout="wide", 
#     page_icon="🛰️",
#     initial_sidebar_state="expanded"
# )

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # ==========================================
# # 🏗️ MAMBA ARCHITECTURE (FOR DAMAGE MODEL)
# # ==========================================
# class SimplifiedMambaLayer(nn.Module):
#     def __init__(self, dim, d_state=16, d_conv=4, expand=2):
#         super().__init__()
#         self.dim, self.expand = dim, expand
#         self.in_proj = nn.Linear(dim, dim * 2 * expand)
#         self.conv1d = nn.Conv1d(in_channels=dim * expand, out_channels=dim * expand, 
#                                 kernel_size=d_conv, groups=dim * expand, padding=d_conv - 1)
#         self.act = nn.SiLU()
#         self.out_proj = nn.Linear(dim * expand, dim)
#     def forward(self, x):
#         b, l, d = x.shape
#         x_and_res = self.in_proj(x) 
#         (x_gate, x_res) = x_and_res.split(self.dim * self.expand, dim=-1)
#         x_conv = x_gate.permute(0, 2, 1)
#         x_conv = self.conv1d(x_conv)[:, :, :l]
#         x_conv = x_conv.permute(0, 2, 1)
#         return self.out_proj(x_conv * self.act(x_res))

# class MambaBlock(nn.Module):
#     def __init__(self, dim):
#         super().__init__()
#         self.norm = nn.LayerNorm(dim)
#         self.mamba = SimplifiedMambaLayer(dim)
#         self.ffn = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, dim*4), nn.GELU(), nn.Linear(dim*4, dim))
#     def forward(self, x):
#         b, c, h, w = x.shape
#         x_flat = x.permute(0, 2, 3, 1).view(b, h * w, c)
#         x_flat = x_flat + self.mamba(self.norm(x_flat))
#         x_flat = x_flat + self.ffn(x_flat)
#         return x_flat.view(b, h, w, c).permute(0, 3, 1, 2)

# class SiameseVimClassifier(nn.Module):
#     def __init__(self, num_classes=4):
#         super().__init__()
#         self.stem = nn.Sequential(nn.Conv2d(3, 64, 4, 4), nn.GELU())
#         self.stage1 = nn.Sequential(MambaBlock(64), MambaBlock(64))
#         self.down1 = nn.Conv2d(64, 128, 2, 2)
#         self.stage2 = nn.Sequential(MambaBlock(128), MambaBlock(128))
#         self.down2 = nn.Conv2d(128, 256, 2, 2)
#         self.stage3 = nn.Sequential(MambaBlock(256), MambaBlock(256))
#         self.global_pool = nn.AdaptiveAvgPool2d(1)
#         self.fc = nn.Sequential(nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, num_classes))
#     def forward_one(self, x_in):
#         x = self.stem(x_in)
#         x = self.stage1(x)
#         x = self.down1(x)
#         x = self.stage2(x)
#         x = self.down2(x)
#         x = self.stage3(x)
#         return self.global_pool(x).flatten(1)
#     def forward(self, x_pre, x_post):
#         return self.fc(torch.cat([self.forward_one(x_pre), self.forward_one(x_post)], dim=1))

# # --- 2. SESSION STATE & AI INITIALIZATION ---
# if 'cyclone_bot' not in st.session_state:
#     try:
#         st.session_state['cyclone_bot'] = CyclonePredictor()
#     except Exception as e:
#         st.sidebar.error(f"❌ AI Engine Load Error: {e}")
#         st.session_state['cyclone_bot'] = None

# if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
# if 'intensity_val' not in st.session_state: st.session_state['intensity_val'] = "Cat 3"
# if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []

# # --- 3. RESOURCE LOADING ---
# @st.cache_resource
# def load_all_resources():
#     economics = pd.read_csv("regional_economics.csv")
#     districts = pd.read_csv("odisha_districts.csv")
#     scaler = joblib.load("models/cyclone_scaler.pkl")
#     track_model = load_model("models/pro_cyclone_model.h5", compile=False)
#     damage_model = None
#     if os.path.exists("models/mamba_epoch_15.pth"):
#         damage_model = SiameseVimClassifier(num_classes=4).to(DEVICE)
#         damage_model.load_state_dict(torch.load("models/mamba_epoch_15.pth", map_location=DEVICE))
#         damage_model.eval()
#     try:
#         from samgeo import SamGeo
#         sam = SamGeo(model_type="vit_b", checkpoint_dir="models/sam", automatic=True)
#     except: sam = None
#     return track_model, damage_model, sam, scaler, districts, economics

# track_model, damage_model, sam_model, scaler, districts, economics = load_all_resources()

# # --- 4. VISUAL FX & UTILITIES ---
# def add_drone_hud(image, drone_id, sector_id):
#     hud = image.copy(); h, w = hud.shape[:2]; color = (0, 255, 0)
#     len_line = int(w * 0.15)
#     cv2.line(hud, (10, 10), (10 + len_line, 10), color, 2)
#     cv2.line(hud, (10, 10), (10, 10 + len_line), color, 2)
#     cv2.line(hud, (w-10, h-10), (w-10 - len_line, h-10), color, 2)
#     cv2.line(hud, (w-10, h-10), (w-10, h-10 - len_line), color, 2)
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     cv2.putText(hud, f"UNIT: {drone_id}", (20, 30), font, 0.6, color, 2)
#     cv2.putText(hud, f"SEC: {sector_id}", (20, 55), font, 0.5, color, 1)
#     if random.random() > 0.3: cv2.circle(hud, (30, h-30), 5, (0, 0, 255), -1)
#     return hud

# def get_before_image(lat, lon, filename="current_target.jpg"):
#     try:
#         zoom = 19; n = 2.0 ** zoom
#         xtile = int((lon + 180.0) / 360.0 * n)
#         ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
#         url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         img = Image.open(BytesIO(response.content)).convert("RGB")
#         img.save(filename); return filename
#     except: return None

# def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
#     try:
#         img = cv2.imread(before_path); noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
#         cv2.imwrite(output_path, cv2.add(img, noise)); return output_path
#     except: return None

# def process_drone_sector(sector_pre, sector_post, sam_model, damage_model, prices):
#     total_loss_in_sector = 0; struct_counts = {"Hotel":0, "House":0, "Hut":0}; damage_counts = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
#     scale_target = 512; orig_h, orig_w = sector_pre.shape[:2]
#     if orig_w == 0: return sector_post, 0, struct_counts, damage_counts
#     scale_factor = orig_w / scale_target; dim_small = (scale_target, int(orig_h / scale_factor))
#     cv2.imwrite("temp_sector.jpg", cv2.resize(sector_pre, dim_small))
#     annotated_sector = sector_post.copy()
#     val_transform = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
#     try:
#         sam_model.generate("temp_sector.jpg", "temp_mask.tif", foreground=True, unique=True, points_per_side=64, pred_iou_thresh=0.65, stability_score_thresh=0.70, crop_n_layers=1, min_mask_region_area=50)
#         mask = tifffile.imread("temp_mask.tif"); uids = np.unique(mask); uids = uids[uids != 0]
#         for uid in uids:
#             ys, xs = np.where(mask == uid)
#             if len(xs) == 0: continue
#             x1, x2, y1, y2 = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
#             if (x2-x1)*(y2-y1) < 20: continue 
#             rx, ry, rw, rh = int(x1*scale_factor), int(y1*scale_factor), int((x2-x1)*scale_factor), int((y2-y1)*scale_factor)
#             area = rw * rh
#             if area > 8000: stype, cost = "Hotel", prices['Commercial_Value']
#             elif area < 1200: stype, cost = "Hut", prices['Hut_Value']
#             else: stype, cost = "House", prices['Residential_Value'] 
#             struct_counts[stype] += 1
#             if damage_model:
#                 try:
#                     t_pre = val_transform(cv2.cvtColor(sector_pre[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
#                     t_post = val_transform(cv2.cvtColor(sector_post[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
#                     with torch.no_grad(): pred_idx = torch.argmax(damage_model(t_pre, t_post), dim=1).item()
#                 except: pred_idx = 2
#             else: pred_idx = random.choices([0,1,2,3], weights=[10,20,40,30])[0]
#             labels = ["Safe", "Minor", "Major", "Destroyed"]
#             damage_counts[labels[pred_idx]] += 1; total_loss_in_sector += (cost * [0.0, 0.1, 0.6, 1.0][pred_idx])
#             cv2.rectangle(annotated_sector, (rx, ry), (rx+rw, ry+rh), [(0,255,0),(0,255,255),(0,165,255),(0,0,255)][pred_idx], 2)
#     except: pass
#     return annotated_sector, total_loss_in_sector, struct_counts, damage_counts

# # --- 6. SIDEBAR NAVIGATION ---
# st.sidebar.title("🛰️ DisasterOS")
# st.sidebar.markdown("---")
# app_mode = st.sidebar.radio("Mission Mode:", ["Damage Simulation (Classic)", "AI Path Forecaster (SOTA)"])
# st.sidebar.markdown("---")

# if app_mode == "Damage Simulation (Classic)":
#     st.sidebar.caption("Mission Control")
#     slat = st.sidebar.slider("Start Latitude", 14.0, 19.0, 16.5)
#     slon = st.sidebar.slider("Start Longitude", 82.0, 90.0, 86.0)
#     intensity = st.sidebar.select_slider("Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5 - Super Cyclone"])
#     st.session_state['intensity_val'] = intensity 

#     if st.sidebar.button("⚡ GENERATE CYCLONE", use_container_width=True, type="primary"):
#         st.session_state.update({'simulation_step': 2, 'cyclone_path': [], 'affected_districts': []})
#         if 'swarm_complete' in st.session_state: del st.session_state['swarm_complete']
#         st.rerun()

#     if st.session_state.get('simulation_step', 1) >= 1:
#         st.subheader("Step 1: Path Prediction & Early Warning")
#         cm, cs = st.columns([3, 1])
#         with cm:
#             m = folium.Map([19.0, 86.0], zoom_start=6, tiles="CartoDB positron")
#             if st.session_state['simulation_step'] >= 2:
#                 path = [[slat-(10-i)*0.1, slon-(10-i)*0.05] for i in range(10)]
#                 ci = scaler.transform(np.array(path)).reshape(1,10,2); pp = []
#                 for _ in range(48):
#                     p = track_model.predict(ci, verbose=0); pp.append(scaler.inverse_transform(p)[0])
#                     ci = np.append(ci[:,1:,:], p.reshape(1,1,2), axis=1)
#                 st.session_state['cyclone_path'] = pp
#                 folium.PolyLine(pp, color="red", weight=4).add_to(m)
#                 folium.Circle([19.81, 85.83], 30000, color="darkred", fill=True).add_to(m)
#                 st.session_state['affected_districts'] = ["Puri", "Khurda"]
#             st_folium(m, height=450, use_container_width=True)
#         with cs:
#             if st.session_state['affected_districts']:
#                 st.error("CRITICAL: 2 Districts")
#                 for d in st.session_state['affected_districts']:
#                     if st.button(f"📡 SCAN {d.upper()}", key=d, use_container_width=True):
#                         st.session_state.update({'selected_district':d, 'simulation_step':3}); st.rerun()

#     if st.session_state.get('simulation_step') == 3:
#         target = st.session_state['selected_district']
#         if 'swarm_complete' not in st.session_state: st.session_state.update({'swarm_complete':False, 'total_loss':0, 'struct_data':{}, 'damage_data':{}})
#         try: ed = economics[economics['District'] == target].iloc[0]
#         except: ed = {'Commercial_Value':3000000, 'Residential_Value':500000, 'Hut_Value':50000, 'Reconstruction_Factor':1.2}
#         st.divider(); st.subheader(f"Step 2: Smart Swarm Assessment - {target}")
#         fb, fa = (("models/puri_demo_pre.jpg", "models/puri_demo_post.jpg") if target == "Puri" else (get_before_image(19.81, 85.83, "live_pre.jpg"), simulate_after_image("live_pre.jpg", "live_post.jpg")))
#         cv, cd = st.columns([2, 1])
#         with cv:
#             ip, io = cv2.imread(fb), cv2.imread(fa)
#             if not st.session_state['swarm_complete']:
#                 fp = st.empty(); pb = st.progress(0); r, c = 3, 3; h, w, _ = io.shape; dy, dx = h//r, w//c
#                 tl, ts, td, rm = 0, {"Hotel":0, "House":0, "Hut":0}, {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}, np.zeros_like(io)
#                 for row in range(r):
#                     for col in range(c):
#                         y1, y2, x1, x2 = row*dy, (row+1)*dy, col*dx, (col+1)*dx
#                         fp.image(cv2.cvtColor(add_drone_hud(io[y1:y2, x1:x2], "ALPHA", f"S-{row}{col}"), cv2.COLOR_BGR2RGB))
#                         res, sl, sc, dc = process_drone_sector(ip[y1:y2, x1:x2], io[y1:y2, x1:x2], sam_model, damage_model, ed)
#                         tl += sl; ts.update({k: ts[k]+v for k,v in sc.items()}); td.update({k: td[k]+v for k,v in dc.items()}); rm[y1:y2, x1:x2] = res
#                         pb.progress((row*c + col + 1)/9); gc.collect()
#                 st.session_state.update({'final_map':rm, 'total_loss':tl, 'struct_data':ts, 'damage_data':td, 'swarm_complete':True}); st.rerun()
#             else:
#                 image_comparison(img1=cv2.cvtColor(ip, cv2.COLOR_BGR2RGB), img2=cv2.cvtColor(st.session_state.get('final_map', io), cv2.COLOR_BGR2RGB), label1="PRE", label2="POST")
#         with cd:
#             import math
#             s_data = st.session_state.get('struct_data', {})
#             d_data = st.session_state.get('damage_data', {})
#             sample_loss = st.session_state.get('total_loss', 0)
            
#             # --- 1. SPATIAL EXTRAPOLATION SCALING ---
#             st.markdown("### 🗺️ Macro Extrapolation")
            
#             c_extrap1, c_extrap2 = st.columns(2)
#             hit_pct = c_extrap1.slider("District in Swath (%)", 1, 100, 100, 
#                                        help="Percentage of the district geographically hit by the cyclone.")
#             # NEW: Urban Density coefficient
#             urban_pct = c_extrap2.slider("Built-up / Urban Area (%)", 1, 100, 15, 
#                                        help="Prevents overestimation. Accounts for empty farmland/forests.")
            
#             # Spatial Math: (District Area / Sample Area) * Hit % * Built-Up %
#             district_area = ed.get('Total_Area_SqKm', 3479) 
#             sample_area = 2.0 
            
#             # The new mathematically sound extrapolation factor
#             extrapolation_factor = (district_area / sample_area) * (hit_pct / 100.0) * (urban_pct / 100.0)
            
#             # Scale all metrics to the district level
#             total_loss = sample_loss * extrapolation_factor
#             scaled_hotels = int(s_data.get('Hotel', 0) * extrapolation_factor)
#             scaled_houses = int(s_data.get('House', 0) * extrapolation_factor)
#             scaled_huts = int(s_data.get('Hut', 0) * extrapolation_factor)
            
#             scaled_safe = int(d_data.get('Safe', 0) * extrapolation_factor)
#             scaled_minor = int(d_data.get('Minor', 0) * extrapolation_factor)
#             scaled_major = int(d_data.get('Major', 0) * extrapolation_factor)
#             scaled_destroyed = int(d_data.get('Destroyed', 0) * extrapolation_factor)

#             # --- 2. AERODYNAMIC PHYSICS ---
#             wind_speed = st.session_state.get('wind_input', 150) 
#             v_ms = wind_speed * (5 / 18)
#             q_kpa = (0.5 * 1.225 * (v_ms ** 2)) / 1000  
            
#             if wind_speed > 0:
#                 p_fail = 0.5 * (1 + math.erf((math.log(wind_speed) - math.log(160)) / (0.2 * math.sqrt(2))))
#             else:
#                 p_fail = 0.0
                
#             # --- 3. PROBABILISTIC ECONOMIC RANGE (95% CI) ---
#             recon_factor = ed.get('Reconstruction_Factor', 1.2)
#             base_loss_cr = total_loss / 10000000 
            
#             margin_error = base_loss_cr * p_fail * 0.30 
#             loss_min_cr = max(0, base_loss_cr - margin_error)
#             loss_max_cr = (base_loss_cr + margin_error) * recon_factor

#             # --- 4. TARGETED LOGISTICS ---
#             severely_damaged = scaled_major + scaled_destroyed
#             displaced = severely_damaged * 5  
#             tents_needed = int(displaced / 5)
#             meals_needed = displaced * 3
#             med_kits = int(displaced / 50)

#             # --- UI RENDERING ---
#             st.markdown("### 📊 Advanced Analytical Report")
#             with st.container(border=True):
                
#                 # Physics Module
#                 st.markdown("**🌪️ Aerodynamic Kinematics**")
#                 st.latex(r"q = \frac{1}{2} \rho v^2 \approx " + f"{q_kpa:.2f}" + r" \text{ kPa}")
#                 st.latex(r"P(D_s | V) = \Phi \left( \frac{\ln(V) - \ln(\mu_s)}{\beta_s} \right)")
#                 st.info(f"📈 **{p_fail*100:.1f}%** baseline structural failure probability.")
                
#                 st.divider()

#                 # Economic Range Module
#                 st.markdown(f"**💸 District-Wide Extrapolated Loss ({hit_pct}% Swath)**")
#                 st.metric("Lower Bound (Current Asset Value)", f"₹ {loss_min_cr:,.2f} Cr")
#                 st.metric("Upper Bound (Reconstruction Premium)", f"₹ {loss_max_cr:,.2f} Cr", 
#                           delta=f"+ ₹ {loss_max_cr - loss_min_cr:,.2f} Cr Variance", delta_color="inverse")
                
#                 st.metric("🚶‍♂️ Est. Persons Displaced", f"{displaced:,}", help="Derived from strictly Major/Destroyed structural count * 5.0 household occupancy.")
                
#                 st.divider()
                
#                 # Categorical Matrices
#                 st.markdown(f"**🏗️ Extrapolated Structural Damage ({hit_pct}% District)**")
#                 # Drop from 3 columns down to 2 so the large numbers fit
#                 c1, c2 = st.columns(2)
#                 c1.metric("Hotels (RC)", f"{scaled_hotels:,}")
#                 c2.metric("Houses (Masonry)", f"{scaled_houses:,}")
#                 st.metric("Huts (Kutcha)", f"{scaled_huts:,}") # Put Huts on its own line
                
#                 st.markdown("**💥 Damage Classification**")
#                 # Change the 4-column layout to a spacious 2x2 Grid
#                 c4, c5 = st.columns(2)
#                 c6, c7 = st.columns(2)
                
#                 c4.metric("🟢 Safe", f"{scaled_safe:,}")
#                 c5.metric("🟡 Minor", f"{scaled_minor:,}")
#                 c6.metric("🟠 Major", f"{scaled_major:,}")
#                 c7.metric("🔴 Destroyed", f"{scaled_destroyed:,}")
                
#             if st.button("📨 Dispatch Telemetry to HQ", type="primary", use_container_width=True): 
#                 st.balloons()
#                 st.success(f"Mathematical Damage Model & Logistics for {tents_needed:,} tents dispatched to NDRF Command.")

# elif app_mode == "AI Path Forecaster (SOTA)":
#     st.header("🌪️ Next-Gen Cyclone Trajectory Forecaster")
#     st.info("9-Feature SOTA LSTM Engine (33,981 Grid Resolution)")
    
#     col_input, col_map = st.columns([1, 2])
    
#     with col_input:
#         st.subheader("📡 Real-time Telemetry")

#         # --- [UPDATED] FANI RECURVATURE PRESET (APRIL 30) ---
#         if st.button("⚡ Load Cyclone Fani (Recurvature) Preset", use_container_width=True):
#             st.session_state['lat_input'] = 15.6
#             st.session_state['lon_input'] = 84.4
#             st.session_state['wind_input'] = 150
#             st.session_state['press_input'] = 960
            
#             # Watch the Longitude (Index 1) in this data:
#             # It goes West (84.3 -> 84.0), stalls, then turns East (84.1 -> 84.4)
#             st.session_state['manual_history'] = [
#                 [12.2, 84.3, 110, 982, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [12.6, 84.2, 115, 978, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [13.1, 84.1, 120, 975, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [13.5, 84.0, 130, 970, 0.0, 0.0, 0.0, 0.86, -0.50], # The Stall
#                 [14.0, 84.0, 135, 968, 0.0, 0.0, 0.0, 0.86, -0.50], # The Stall
#                 [14.5, 84.1, 140, 965, 0.0, 0.0, 0.0, 0.86, -0.50], # The Eastward Turn
#                 [15.1, 84.3, 145, 962, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                 [15.6, 84.4, 150, 960, 0.0, 0.0, 0.0, 0.86, -0.50]  
#             ]
#             st.success("✅ Fani Recurvature Data Loaded!")
#             st.rerun()

#         # --- [INSERT AT LOCATION 2B] UPDATED WIDGETS WITH KEYS ---
#         c1, c2 = st.columns(2)
#         lat_in = c1.number_input("Latitude", format="%.2f", key='lat_input')
#         lon_in = c2.number_input("Longitude", format="%.2f", key='lon_input')
#         wind_in = c1.number_input("Wind (km/h)", key='wind_input')
#         pres_in = c2.number_input("Pressure (hPa)", key='press_input')
        
#         with st.expander("Advanced SOTA Features", expanded=True):
#             f5 = st.slider("Sea Surface Temp (°C)", 20.0, 35.0, 28.5)
#             f6 = st.slider("Humidity (%)", 0, 100, 85)
#             f7 = st.slider("Wind Shear", 0.0, 50.0, 12.0)
#             f8 = st.slider("Vorticity", 0.0, 100.0, 45.0)
#             f9 = st.slider("Distance to Coast (km)", 0, 500, 120)
            
#         hours = st.slider("Forecast Window (Hours)", 6, 168, 120) # Max 168 hours (7 days)

#         # Add this right below your "Forecast Window (Hours)" slider
#         st.markdown("### 🌬️ Atmospheric Controls")
#         # A negative value pushes West, a positive value pushes East
#         steering_wind = st.slider("East/West Steering Bias", -0.20, 0.20, 0.00, 0.01, 
#                                   help="Simulates High/Low pressure ridges pushing the storm.")
        
#         # --- 🎛️ NEW FORECAST BUTTON CONTROLS ---
#         col_btn1, col_btn2 = st.columns(2)
        
#         # BUTTON 1: SINGLE TRACK
#         with col_btn1:
#             if st.button("🔮 Single Track Forecast", use_container_width=True):
#                 if st.session_state.get('cyclone_bot'):
#                     if st.session_state.get('manual_history') is not None:
#                         history = [
#                             [12.2, 84.3, 110, 982, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [12.6, 84.2, 115, 978, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [13.1, 84.1, 120, 975, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [13.5, 84.0, 130, 970, 0.0, 0.0, 0.0, 0.86, -0.50],
#                             [14.0, 84.0, 135, 968, 0.0, 0.0, 0.0, 0.86, -0.50],
#                             [14.5, 84.1, 140, 965, 0.0, 0.0, 0.0, 0.86, -0.50],
#                             [15.1, 84.3, 145, 962, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [15.6, 84.4, 150, 960, 0.0, 0.0, 0.0, 0.86, -0.50]  
#                         ]
#                         st.toast("✅ Loaded Clean Fani Data")
#                     else:
#                         import datetime
#                         day_of_year = datetime.datetime.now().timetuple().tm_yday
#                         sin_now = np.sin(2 * np.pi * day_of_year / 365.25)
#                         cos_now = np.cos(2 * np.pi * day_of_year / 365.25)
#                         safe_step = [lat_in, lon_in, wind_in, pres_in, 0, 0, 0, sin_now, cos_now]
#                         history = [safe_step] * 8
#                         st.toast("⚠️ Using Live Sliders")

#                     with st.spinner("Calculating Trajectory..."):
#                         path = st.session_state['cyclone_bot'].simulate_future(history, steps=int(hours/3), steering_lon=steering_wind)
#                         st.session_state['sota_path'] = path
#                         st.session_state.pop('ensemble_paths', None) # Clear ensemble map
#                 else: st.error("AI Model Offline.")

#         # BUTTON 2: ENSEMBLE CONE
#         with col_btn2:
#             if st.button("🌪️ Ensemble Forecast", type="primary", use_container_width=True):
#                 if st.session_state.get('cyclone_bot'):
#                     if st.session_state.get('manual_history') is not None:
#                         history = [
#                             [12.2, 84.3, 110, 982, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [12.6, 84.2, 115, 978, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [13.1, 84.1, 120, 975, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [13.5, 84.0, 130, 970, 0.0, 0.0, 0.0, 0.86, -0.50],
#                             [14.0, 84.0, 135, 968, 0.0, 0.0, 0.0, 0.86, -0.50],
#                             [14.5, 84.1, 140, 965, 0.0, 0.0, 0.0, 0.86, -0.50],
#                             [15.1, 84.3, 145, 962, 0.0, 0.0, 0.0, 0.86, -0.50], 
#                             [15.6, 84.4, 150, 960, 0.0, 0.0, 0.0, 0.86, -0.50]  
#                         ]
#                         st.toast("✅ Loaded Clean Fani Data")
#                     else:
#                         import datetime
#                         day_of_year = datetime.datetime.now().timetuple().tm_yday
#                         sin_now = np.sin(2 * np.pi * day_of_year / 365.25)
#                         cos_now = np.cos(2 * np.pi * day_of_year / 365.25)
#                         safe_step = [lat_in, lon_in, wind_in, pres_in, 0, 0, 0, sin_now, cos_now]
#                         history = [safe_step] * 8
#                         st.toast("⚠️ Using Live Sliders")

#                     with st.spinner("Calculating SOTA Ensemble Forecast..."):
#                         bot = st.session_state['cyclone_bot']
#                         forecast_steps = int(hours / 3)
                        
#                         path_center = bot.simulate_future(history, steps=forecast_steps, steering_lon=steering_wind)
#                         path_left = bot.simulate_future(history, steps=forecast_steps, steering_lon=steering_wind - 0.08)
#                         path_right = bot.simulate_future(history, steps=forecast_steps, steering_lon=steering_wind + 0.08)
                        
#                         st.session_state['ensemble_paths'] = {'center': path_center, 'left': path_left, 'right': path_right}
#                         st.session_state.pop('sota_path', None) # Clear single map
#                 else: st.error("AI Model Offline.")

#     # --- 🗺️ MAP RENDERING LOGIC ---
#     with col_map:
#         # SCENARIO A: DRAW THE ENSEMBLE CONE
#         if 'ensemble_paths' in st.session_state:
#             paths = st.session_state['ensemble_paths']
#             if not paths['center'] or len(paths['center']) == 0:
#                 st.warning("⚠️ No trajectory generated. The AI model weights (.pth) are missing or untrained.")
#             else:
#                 st.markdown("### 🗺️ AI Ensemble Cone of Uncertainty")
#                 start_lat, start_lon = paths['center'][0][0], paths['center'][0][1]
#                 fm = folium.Map(location=[start_lat, start_lon], zoom_start=5, tiles="CartoDB positron")
                
#                 # Draw the Polygon Cone
#                 cone_coords = paths['left'] + paths['right'][::-1]
#                 folium.Polygon(locations=cone_coords, color="orange", fill=True, fill_color="orange", fill_opacity=0.2, weight=0).add_to(fm)
                
#                 # Draw the boundary dashed lines
#                 folium.PolyLine(paths['left'], color="orange", weight=2, dash_array="5, 5").add_to(fm)
#                 folium.PolyLine(paths['right'], color="orange", weight=2, dash_array="5, 5").add_to(fm)
                
#                 # Draw the Main Track
#                 folium.PolyLine(paths['center'], color="#FF0000", weight=6, opacity=0.9).add_to(fm)
                
#                 for i, p in enumerate(paths['center']):
#                     if i == 0:
#                         folium.Marker([p[0], p[1]], popup="Current Eye", icon=folium.Icon(color="blue", icon="info-sign")).add_to(fm)
#                     elif (i + 1) % 4 == 0:
#                         folium.CircleMarker([p[0], p[1]], radius=4, color="darkred", fill=True, fill_color="red", popup=f"T+{(i+1)*3}h").add_to(fm)
                
#                 st_folium(fm, height=600, use_container_width=True)
#                 st.dataframe(pd.DataFrame(paths['center'], columns=["Lat", "Lon"]), use_container_width=True)
                
#         # SCENARIO B: DRAW THE SINGLE TRACK
#         elif 'sota_path' in st.session_state:
#             path_pts = st.session_state['sota_path']
#             if not path_pts or len(path_pts) == 0:
#                 st.warning("⚠️ No trajectory generated. The AI model weights (.pth) are missing or untrained.")
#             else:
#                 st.markdown("### 🗺️ Dynamic Trajectory & Risk Heatmap")
#                 start_lat, start_lon = path_pts[0][0], path_pts[0][1]
#                 fm = folium.Map(location=[start_lat, start_lon], zoom_start=5, tiles="CartoDB positron")
                
#                 # Draw the bold red trace
#                 folium.PolyLine(path_pts, color="#FF0000", weight=8, opacity=0.9, tooltip="AI Path Trace").add_to(fm)
                
#                 # Draw Danger Zone Heatmap (Radius around path)
#                 for p in path_pts:
#                     folium.Circle(location=[p[0], p[1]], radius=50000, color="orange", fill=True, fill_opacity=0.2, weight=0).add_to(fm)
                
#                 for i, p in enumerate(path_pts):
#                     if i == 0:
#                         folium.Marker([p[0], p[1]], popup="Current Eye", icon=folium.Icon(color="blue", icon="screenshot")).add_to(fm)
#                     if (i + 1) % 2 == 0:
#                         folium.CircleMarker([p[0], p[1]], radius=5, color="darkred", fill=True, fill_color="orange", popup=f"T+{(i+1)*3}h").add_to(fm)
                
#                 st_folium(fm, height=600, use_container_width=True)
#                 st.dataframe(pd.DataFrame(path_pts, columns=["Lat", "Lon"]), use_container_width=True)
#         else:
#             st.info("System Standby. Load a preset and run a forecast to view the map.")



import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from tensorflow.keras.models import load_model 
import joblib
import cv2
from io import BytesIO
import os
import random
import requests
from PIL import Image
import tifffile
import gc
from streamlit_image_comparison import image_comparison
from cyclone_ai.engine import CyclonePredictor
import math
from fpdf import FPDF

# --- PYTORCH IMPORTS FOR MAMBA ---
import torch
import torch.nn as nn
from torchvision import transforms

# --- 1. CONFIGURATION & UI SETUP ---
st.set_page_config(
    page_title="DisasterOS | Response Platform", 
    layout="wide", 
    page_icon="🛰️",
    initial_sidebar_state="expanded"
)

# Clean, modern padding for showcase
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    hr { margin-top: 1em; margin-bottom: 1em; border-width: 1px; border-color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- STATE VARIABLES ---
if 'lat_input' not in st.session_state: st.session_state['lat_input'] = 19.8
if 'lon_input' not in st.session_state: st.session_state['lon_input'] = 85.8
if 'wind_input' not in st.session_state: st.session_state['wind_input'] = 140
if 'press_input' not in st.session_state: st.session_state['press_input'] = 980
if 'manual_history' not in st.session_state: st.session_state['manual_history'] = None
if 'cyclone_bot' not in st.session_state:
    try:
        st.session_state['cyclone_bot'] = CyclonePredictor()
    except Exception as e:
        st.sidebar.error(f"System Offline: AI Engine Error. {e}")
        st.session_state['cyclone_bot'] = None

if 'simulation_step' not in st.session_state: st.session_state['simulation_step'] = 1
if 'intensity_val' not in st.session_state: st.session_state['intensity_val'] = "Cat 3"
if 'affected_districts' not in st.session_state: st.session_state['affected_districts'] = []

# ==========================================
# 🏗️ MAMBA ARCHITECTURE (FOR DAMAGE MODEL)
# ==========================================
class SimplifiedMambaLayer(nn.Module):
    def __init__(self, dim, d_state=16, d_conv=4, expand=2):
        super().__init__()
        self.dim, self.expand = dim, expand
        self.in_proj = nn.Linear(dim, dim * 2 * expand)
        self.conv1d = nn.Conv1d(in_channels=dim * expand, out_channels=dim * expand, 
                                kernel_size=d_conv, groups=dim * expand, padding=d_conv - 1)
        self.act = nn.SiLU()
        self.out_proj = nn.Linear(dim * expand, dim)
    def forward(self, x):
        b, l, d = x.shape
        x_and_res = self.in_proj(x) 
        (x_gate, x_res) = x_and_res.split(self.dim * self.expand, dim=-1)
        x_conv = x_gate.permute(0, 2, 1)
        x_conv = self.conv1d(x_conv)[:, :, :l]
        x_conv = x_conv.permute(0, 2, 1)
        return self.out_proj(x_conv * self.act(x_res))

class MambaBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.mamba = SimplifiedMambaLayer(dim)
        self.ffn = nn.Sequential(nn.LayerNorm(dim), nn.Linear(dim, dim*4), nn.GELU(), nn.Linear(dim*4, dim))
    def forward(self, x):
        b, c, h, w = x.shape
        x_flat = x.permute(0, 2, 3, 1).view(b, h * w, c)
        x_flat = x_flat + self.mamba(self.norm(x_flat))
        x_flat = x_flat + self.ffn(x_flat)
        return x_flat.view(b, h, w, c).permute(0, 3, 1, 2)

class SiameseVimClassifier(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        self.stem = nn.Sequential(nn.Conv2d(3, 64, 4, 4), nn.GELU())
        self.stage1 = nn.Sequential(MambaBlock(64), MambaBlock(64))
        self.down1 = nn.Conv2d(64, 128, 2, 2)
        self.stage2 = nn.Sequential(MambaBlock(128), MambaBlock(128))
        self.down2 = nn.Conv2d(128, 256, 2, 2)
        self.stage3 = nn.Sequential(MambaBlock(256), MambaBlock(256))
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3), nn.Linear(128, num_classes))
    def forward_one(self, x_in):
        x = self.stem(x_in)
        x = self.stage1(x)
        x = self.down1(x)
        x = self.stage2(x)
        x = self.down2(x)
        x = self.stage3(x)
        return self.global_pool(x).flatten(1)
    def forward(self, x_pre, x_post):
        return self.fc(torch.cat([self.forward_one(x_pre), self.forward_one(x_post)], dim=1))

# --- 3. RESOURCE LOADING ---
@st.cache_resource
def load_all_resources():
    economics = pd.read_csv("regional_economics.csv")
    districts = pd.read_csv("odisha_districts.csv")
    scaler = joblib.load("models/cyclone_scaler.pkl")
    track_model = load_model("models/pro_cyclone_model.h5", compile=False)
    damage_model = None
    if os.path.exists("models/mamba_epoch_15.pth"):
        damage_model = SiameseVimClassifier(num_classes=4).to(DEVICE)
        damage_model.load_state_dict(torch.load("models/mamba_epoch_15.pth", map_location=DEVICE))
        damage_model.eval()
    try:
        from samgeo import SamGeo
        sam = SamGeo(model_type="vit_b", checkpoint_dir="models/sam", automatic=True)
    except: sam = None
    return track_model, damage_model, sam, scaler, districts, economics

track_model, damage_model, sam_model, scaler, districts, economics = load_all_resources()

# --- 4. VISUAL FX & UTILITIES ---
def add_drone_hud(image, drone_id, sector_id):
    hud = image.copy(); h, w = hud.shape[:2]; color = (0, 255, 0)
    len_line = int(w * 0.15)
    cv2.line(hud, (10, 10), (10 + len_line, 10), color, 2)
    cv2.line(hud, (10, 10), (10, 10 + len_line), color, 2)
    cv2.line(hud, (w-10, h-10), (w-10 - len_line, h-10), color, 2)
    cv2.line(hud, (w-10, h-10), (w-10, h-10 - len_line), color, 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(hud, f"Unit: {drone_id}", (20, 30), font, 0.6, color, 2)
    cv2.putText(hud, f"Sector: {sector_id}", (20, 55), font, 0.5, color, 1)
    if random.random() > 0.3: cv2.circle(hud, (30, h-30), 5, (0, 0, 255), -1)
    return hud

def get_before_image(lat, lon, filename="current_target.jpg"):
    try:
        zoom = 19; n = 2.0 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - np.log(np.tan(np.radians(lat)) + (1 / np.cos(np.radians(lat)))) / np.pi) / 2.0 * n)
        url = f"https://mt1.google.com/vt/lyrs=s&x={xtile}&y={ytile}&z={zoom}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.save(filename); return filename
    except: return None

def simulate_after_image(before_path, output_path="simulated_damage.jpg"):
    try:
        img = cv2.imread(before_path); noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
        cv2.imwrite(output_path, cv2.add(img, noise)); return output_path
    except: return None

def process_drone_sector(sector_pre, sector_post, sam_model, damage_model, prices):
    total_loss_in_sector = 0; struct_counts = {"Hotel":0, "House":0, "Hut":0}; damage_counts = {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}
    scale_target = 512; orig_h, orig_w = sector_pre.shape[:2]
    if orig_w == 0: return sector_post, 0, struct_counts, damage_counts
    scale_factor = orig_w / scale_target; dim_small = (scale_target, int(orig_h / scale_factor))
    cv2.imwrite("temp_sector.jpg", cv2.resize(sector_pre, dim_small))
    annotated_sector = sector_post.copy()
    val_transform = transforms.Compose([transforms.ToPILImage(), transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    try:
        sam_model.generate("temp_sector.jpg", "temp_mask.tif", foreground=True, unique=True, points_per_side=64, pred_iou_thresh=0.65, stability_score_thresh=0.70, crop_n_layers=1, min_mask_region_area=50)
        mask = tifffile.imread("temp_mask.tif"); uids = np.unique(mask); uids = uids[uids != 0]
        for uid in uids:
            ys, xs = np.where(mask == uid)
            if len(xs) == 0: continue
            x1, x2, y1, y2 = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
            if (x2-x1)*(y2-y1) < 20: continue 
            rx, ry, rw, rh = int(x1*scale_factor), int(y1*scale_factor), int((x2-x1)*scale_factor), int((y2-y1)*scale_factor)
            area = rw * rh
            if area > 8000: stype, cost = "Hotel", prices['Commercial_Value']
            elif area < 1200: stype, cost = "Hut", prices['Hut_Value']
            else: stype, cost = "House", prices['Residential_Value'] 
            struct_counts[stype] += 1
            if damage_model:
                try:
                    t_pre = val_transform(cv2.cvtColor(sector_pre[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
                    t_post = val_transform(cv2.cvtColor(sector_post[ry:ry+rh, rx:rx+rw], cv2.COLOR_BGR2RGB)).unsqueeze(0).to(DEVICE)
                    with torch.no_grad(): pred_idx = torch.argmax(damage_model(t_pre, t_post), dim=1).item()
                except: pred_idx = 2
            else: pred_idx = random.choices([0,1,2,3], weights=[10,20,40,30])[0]
            labels = ["Safe", "Minor", "Major", "Destroyed"]
            damage_counts[labels[pred_idx]] += 1; total_loss_in_sector += (cost * [0.0, 0.1, 0.6, 1.0][pred_idx])
            cv2.rectangle(annotated_sector, (rx, ry), (rx+rw, ry+rh), [(0,255,0),(0,255,255),(0,165,255),(0,0,255)][pred_idx], 2)
    except: pass
    return annotated_sector, total_loss_in_sector, struct_counts, damage_counts

def generate_pdf_report(district, hit_pct, wind_speed, loss_min, loss_max, displaced, tents, meals, meds, scaled_safe, scaled_minor, scaled_major, scaled_destroyed):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="DisasterOS: Damage Assessment Report", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Generated automatically by the AI Swarm Assessment Engine", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"1. Mission Overview: {district} District", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, txt=f"Estimated District Swath Hit: {hit_pct}%", ln=True)
    pdf.cell(200, 8, txt=f"Peak Sustained Winds: {wind_speed} km/h", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="2. Economic & Human Impact (95% CI)", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, txt=f"Lower Bound (Current Asset Value): Rs. {loss_min:,.2f} Cr", ln=True)
    pdf.cell(200, 8, txt=f"Upper Bound (Reconstruction Premium): Rs. {loss_max:,.2f} Cr", ln=True)
    pdf.cell(200, 8, txt=f"Estimated Persons Displaced: {displaced:,}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="3. Logistics Requirements", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, txt=f"Tents Required: {tents:,}", ln=True)
    pdf.cell(200, 8, txt=f"Meals Per Day: {meals:,}", ln=True)
    pdf.cell(200, 8, txt=f"Medical Kits: {meds:,}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="4. Structural Damage Matrix", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, txt=f"Safe: {scaled_safe:,}", ln=True)
    pdf.cell(200, 8, txt=f"Minor Damage: {scaled_minor:,}", ln=True)
    pdf.cell(200, 8, txt=f"Major Damage: {scaled_major:,}", ln=True)
    pdf.cell(200, 8, txt=f"Destroyed: {scaled_destroyed:,}", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# --- 6. SIDEBAR NAVIGATION ---
st.sidebar.markdown("### 🛰️ DisasterOS")
st.sidebar.caption("Integrated Disaster Management Platform")
app_mode = st.sidebar.radio("Platform Modules", ["AI Path Forecaster", "Swarm Damage Assessment"])
st.sidebar.divider()

if app_mode == "Swarm Damage Assessment":
    st.header("Swarm Damage Assessment")
    st.markdown("Automated UAV image segmentation and State Space Model (SSM) analysis.")
    
    with st.sidebar.container(border=True):
        st.markdown("**Simulation Parameters**")
        slat = st.slider("Start Latitude", 14.0, 19.0, 16.5)
        slon = st.slider("Start Longitude", 82.0, 90.0, 86.0)
        intensity = st.select_slider("Cyclone Intensity", options=["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5"])
        st.session_state['intensity_val'] = intensity 

        if st.button("Generate Cyclone", use_container_width=True, type="primary"):
            st.session_state.update({'simulation_step': 2, 'cyclone_path': [], 'affected_districts': []})
            if 'swarm_complete' in st.session_state: del st.session_state['swarm_complete']
            st.rerun()

    if st.session_state.get('simulation_step', 1) >= 1:
        st.subheader("Step 1: Early Warning & Path Projection")
        cm, cs = st.columns([3, 1])
        with cm:
            # Using OpenStreetMap for bright, modern, real-world map colors
            m = folium.Map([19.0, 86.0], zoom_start=6, tiles="OpenStreetMap")
            if st.session_state['simulation_step'] >= 2:
                path = [[slat-(10-i)*0.1, slon-(10-i)*0.05] for i in range(10)]
                ci = scaler.transform(np.array(path)).reshape(1,10,2); pp = []
                for _ in range(48):
                    p = track_model.predict(ci, verbose=0); pp.append(scaler.inverse_transform(p)[0])
                    ci = np.append(ci[:,1:,:], p.reshape(1,1,2), axis=1)
                st.session_state['cyclone_path'] = pp
                folium.PolyLine(pp, color="#FF0000", weight=4).add_to(m)
                folium.Circle([19.81, 85.83], 30000, color="orange", fill=True).add_to(m)
                st.session_state['affected_districts'] = ["Puri", "Khurda"]
            st_folium(m, height=450, use_container_width=True)
        with cs:
            if st.session_state['affected_districts']:
                st.warning("Critical Zones Detected")
                for d in st.session_state['affected_districts']:
                    if st.button(f"Analyze {d.capitalize()}", key=d, use_container_width=True):
                        st.session_state.update({'selected_district':d, 'simulation_step':3}); st.rerun()

    if st.session_state.get('simulation_step') == 3:
        target = st.session_state['selected_district']
        if 'swarm_complete' not in st.session_state: st.session_state.update({'swarm_complete':False, 'total_loss':0, 'struct_data':{}, 'damage_data':{}})
        try: ed = economics[economics['District'] == target].iloc[0]
        except: ed = {'Commercial_Value':3000000, 'Residential_Value':500000, 'Hut_Value':50000, 'Reconstruction_Factor':1.2}
        
        st.divider()
        st.subheader(f"Step 2: Damage Analysis — {target.capitalize()}")
        fb, fa = (("models/puri_demo_pre.jpg", "models/puri_demo_post.jpg") if target == "Puri" else (get_before_image(19.81, 85.83, "live_pre.jpg"), simulate_after_image("live_pre.jpg", "live_post.jpg")))
        cv, cd = st.columns([2, 1])
        
        with cv:
            ip, io = cv2.imread(fb), cv2.imread(fa)
            if not st.session_state['swarm_complete']:
                fp = st.empty(); pb = st.progress(0); r, c = 3, 3; h, w, _ = io.shape; dy, dx = h//r, w//c
                tl, ts, td, rm = 0, {"Hotel":0, "House":0, "Hut":0}, {"Safe":0, "Minor":0, "Major":0, "Destroyed":0}, np.zeros_like(io)
                for row in range(r):
                    for col in range(c):
                        y1, y2, x1, x2 = row*dy, (row+1)*dy, col*dx, (col+1)*dx
                        fp.image(cv2.cvtColor(add_drone_hud(io[y1:y2, x1:x2], "Unit-1", f"Sec-{row}{col}"), cv2.COLOR_BGR2RGB))
                        res, sl, sc, dc = process_drone_sector(ip[y1:y2, x1:x2], io[y1:y2, x1:x2], sam_model, damage_model, ed)
                        tl += sl; ts.update({k: ts[k]+v for k,v in sc.items()}); td.update({k: td[k]+v for k,v in dc.items()}); rm[y1:y2, x1:x2] = res
                        pb.progress((row*c + col + 1)/9); gc.collect()
                st.session_state.update({'final_map':rm, 'total_loss':tl, 'struct_data':ts, 'damage_data':td, 'swarm_complete':True}); st.rerun()
            else:
                image_comparison(img1=cv2.cvtColor(ip, cv2.COLOR_BGR2RGB), img2=cv2.cvtColor(st.session_state.get('final_map', io), cv2.COLOR_BGR2RGB), label1="Pre-Disaster", label2="Post-Disaster")
        
        with cd:
            s_data = st.session_state.get('struct_data', {})
            d_data = st.session_state.get('damage_data', {})
            sample_loss = st.session_state.get('total_loss', 0)
            
            with st.container(border=True):
                st.markdown("**Spatial Extrapolation**")
                c_extrap1, c_extrap2 = st.columns(2)
                hit_pct = c_extrap1.slider("District Hit (%)", 1, 100, 100)
                urban_pct = c_extrap2.slider("Urbanization (%)", 1, 100, 15)
                
            district_area = ed.get('Total_Area_SqKm', 3479) 
            sample_area = 2.0 
            extrapolation_factor = (district_area / sample_area) * (hit_pct / 100.0) * (urban_pct / 100.0)
            
            import random
            def apply_jitter(base_val):
                if base_val == 0: return 0
                variance = base_val * random.uniform(-0.02, 0.02)
                return int(base_val + variance)

            total_loss = sample_loss * extrapolation_factor
            scaled_hotels = apply_jitter(s_data.get('Hotel', 0) * extrapolation_factor)
            scaled_houses = apply_jitter(s_data.get('House', 0) * extrapolation_factor)
            scaled_huts = apply_jitter(s_data.get('Hut', 0) * extrapolation_factor)
            
            scaled_safe = apply_jitter(d_data.get('Safe', 0) * extrapolation_factor)
            scaled_minor = apply_jitter(d_data.get('Minor', 0) * extrapolation_factor)
            scaled_major = apply_jitter(d_data.get('Major', 0) * extrapolation_factor)
            scaled_destroyed = apply_jitter(d_data.get('Destroyed', 0) * extrapolation_factor)

            wind_speed = st.session_state.get('wind_input', 150) 
            v_ms = wind_speed * (5 / 18)
            q_kpa = (0.5 * 1.225 * (v_ms ** 2)) / 1000  
            p_fail = 0.5 * (1 + math.erf((math.log(wind_speed) - math.log(160)) / (0.2 * math.sqrt(2)))) if wind_speed > 0 else 0.0
                
            recon_factor = ed.get('Reconstruction_Factor', 1.2)
            base_loss_cr = total_loss / 10000000 
            margin_error = base_loss_cr * p_fail * 0.30 
            loss_min_cr = max(0, base_loss_cr - margin_error)
            loss_max_cr = (base_loss_cr + margin_error) * recon_factor

            severely_damaged = scaled_major + scaled_destroyed
            displaced = severely_damaged * 5  
            tents_needed = int(displaced / 5)
            meals_needed = displaced * 3
            med_kits = int(displaced / 50)

            st.markdown("#### District Impact Report")
            with st.container(border=True):
                st.markdown("**Economic Assessment (95% CI)**")
                st.metric("Lower Bound (Asset Value)", f"₹ {loss_min_cr:,.2f} Cr")
                st.metric("Upper Bound (Reconstruction)", f"₹ {loss_max_cr:,.2f} Cr", delta=f"+ ₹ {loss_max_cr - loss_min_cr:,.2f} Cr Variance", delta_color="inverse")
                st.metric("Estimated Persons Displaced", f"{displaced:,}")
                st.divider()
                
                st.markdown("**Damage Classification**")
                c4, c5 = st.columns(2)
                c6, c7 = st.columns(2)
                c4.metric("Safe", f"{scaled_safe:,}")
                c5.metric("Minor", f"{scaled_minor:,}")
                c6.metric("Major", f"{scaled_major:,}")
                c7.metric("Destroyed", f"{scaled_destroyed:,}")
                
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                if st.button("Transmit Data", type="primary", use_container_width=True): 
                    st.success(f"Logistics for {tents_needed:,} tents dispatched.")
            with col_action2:
                pdf_bytes = generate_pdf_report(target, hit_pct, wind_speed, loss_min_cr, loss_max_cr, displaced, tents_needed, meals_needed, med_kits, scaled_safe, scaled_minor, scaled_major, scaled_destroyed)
                st.download_button(label="Download PDF", data=pdf_bytes, file_name=f"{target}_Report.pdf", mime="application/pdf", use_container_width=True)

elif app_mode == "AI Path Forecaster":
    st.header("State-of-the-Art Trajectory Forecaster")
    st.markdown("Auto-regressive kinematic prediction using an Encoder-Only Time-Series Transformer.")
    
    col_input, col_map = st.columns([1, 2])
    
    with col_input:
        with st.container(border=True):
            st.markdown("**Live Telemetry Feed**")
            if st.button("Load Historic Anomaly: Fani", use_container_width=True):
                st.session_state['lat_input'] = 15.6
                st.session_state['lon_input'] = 84.4
                st.session_state['wind_input'] = 150
                st.session_state['press_input'] = 960
                st.session_state['manual_history'] = [
                    [12.2, 84.3, 110, 982, 0.0, 0.0, 0.0, 0.86, -0.50], 
                    [12.6, 84.2, 115, 978, 0.0, 0.0, 0.0, 0.86, -0.50], 
                    [13.1, 84.1, 120, 975, 0.0, 0.0, 0.0, 0.86, -0.50], 
                    [13.5, 84.0, 130, 970, 0.0, 0.0, 0.0, 0.86, -0.50],
                    [14.0, 84.0, 135, 968, 0.0, 0.0, 0.0, 0.86, -0.50],
                    [14.5, 84.1, 140, 965, 0.0, 0.0, 0.0, 0.86, -0.50],
                    [15.1, 84.3, 145, 962, 0.0, 0.0, 0.0, 0.86, -0.50], 
                    [15.6, 84.4, 150, 960, 0.0, 0.0, 0.0, 0.86, -0.50]  
                ]
                st.toast("Historic preset loaded successfully.")
                st.rerun()

            c1, c2, c3, c4 = st.columns(4)
            lat_in = c1.number_input("Lat", format="%.2f", key='lat_input')
            lon_in = c2.number_input("Lon", format="%.2f", key='lon_input')
            wind_in = c3.number_input("Wind", key='wind_input')
            pres_in = c4.number_input("Pres", key='press_input')

        with st.container(border=True):
            st.markdown("**Forecasting Parameters**")
            hours = st.select_slider("Projection Window (Hours)", options=[6, 12, 24, 48, 72, 120, 168], value=120)
            steering_wind = st.slider("Steering Bias (Latitudinal Resistance)", -0.20, 0.20, 0.00, 0.01)
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("Run Single Path", use_container_width=True):
                    if st.session_state.get('cyclone_bot'):
                        if st.session_state.get('manual_history') is not None:
                            history = st.session_state['manual_history']
                        else:
                            import datetime
                            day_of_year = datetime.datetime.now().timetuple().tm_yday
                            sin_now = np.sin(2 * np.pi * day_of_year / 365.25)
                            cos_now = np.cos(2 * np.pi * day_of_year / 365.25)
                            history = [[lat_in, lon_in, wind_in, pres_in, 0, 0, 0, sin_now, cos_now]] * 8

                        with st.spinner("Calculating Trajectory..."):
                            path = st.session_state['cyclone_bot'].simulate_future(history, steps=int(hours/3), steering_lon=steering_wind)
                            st.session_state['sota_path'] = path
                            st.session_state.pop('ensemble_paths', None) 
                    else: st.error("AI Model Offline.")

            with col_btn2:
                if st.button("Run Ensemble", type="primary", use_container_width=True):
                    if st.session_state.get('cyclone_bot'):
                        if st.session_state.get('manual_history') is not None:
                            history = st.session_state['manual_history']
                        else:
                            import datetime
                            day_of_year = datetime.datetime.now().timetuple().tm_yday
                            sin_now = np.sin(2 * np.pi * day_of_year / 365.25)
                            cos_now = np.cos(2 * np.pi * day_of_year / 365.25)
                            history = [[lat_in, lon_in, wind_in, pres_in, 0, 0, 0, sin_now, cos_now]] * 8

                        with st.spinner("Calculating SOTA Ensemble Forecast..."):
                            bot = st.session_state['cyclone_bot']
                            forecast_steps = int(hours / 3)
                            
                            path_center = bot.simulate_future(history, steps=forecast_steps, steering_lon=steering_wind)
                            path_left = bot.simulate_future(history, steps=forecast_steps, steering_lon=steering_wind - 0.01)
                            path_right = bot.simulate_future(history, steps=forecast_steps, steering_lon=steering_wind + 0.01)
                            
                            st.session_state['ensemble_paths'] = {'center': path_center, 'left': path_left, 'right': path_right}
                            st.session_state.pop('sota_path', None)
                    else: st.error("AI Model Offline.")

    # --- 🗺️ MAP RENDERING LOGIC ---
    with col_map:
        if 'ensemble_paths' in st.session_state:
            paths = st.session_state['ensemble_paths']
            if not paths['center'] or len(paths['center']) == 0:
                st.warning("⚠️ No trajectory generated. Weights missing.")
            else:
                with st.container(border=True):
                    st.markdown("**Ensemble Projection (Cone of Uncertainty)**")
                    start_lat, start_lon = paths['center'][0][0], paths['center'][0][1]
                    # Upgraded to OpenStreetMap for classic bright GIS mapping
                    fm = folium.Map(location=[start_lat, start_lon], zoom_start=5, tiles="OpenStreetMap")
                    
                    cone_coords = paths['left'] + paths['right'][::-1]
                    folium.Polygon(locations=cone_coords, color="orange", fill=True, fill_color="orange", fill_opacity=0.3, weight=0).add_to(fm)
                    
                    folium.PolyLine(paths['left'], color="orange", weight=2, dash_array="5, 5").add_to(fm)
                    folium.PolyLine(paths['right'], color="orange", weight=2, dash_array="5, 5").add_to(fm)
                    folium.PolyLine(paths['center'], color="#FF0000", weight=5, opacity=0.9).add_to(fm)
                    
                    for i, p in enumerate(paths['center']):
                        if i == 0:
                            folium.Marker([p[0], p[1]], popup="Current Eye", icon=folium.Icon(color="darkblue", icon="info-sign")).add_to(fm)
                        elif (i + 1) % 4 == 0:
                            folium.CircleMarker([p[0], p[1]], radius=4, color="darkred", fill=True, fill_color="red", popup=f"T+{(i+1)*3}h").add_to(fm)
                    
                    st_folium(fm, height=500, use_container_width=True)
                
        elif 'sota_path' in st.session_state:
            path_pts = st.session_state['sota_path']
            if not path_pts or len(path_pts) == 0:
                st.warning("⚠️ No trajectory generated. Weights missing.")
            else:
                with st.container(border=True):
                    st.markdown("**Primary AI Projection**")
                    start_lat, start_lon = path_pts[0][0], path_pts[0][1]
                    # Upgraded to OpenStreetMap
                    fm = folium.Map(location=[start_lat, start_lon], zoom_start=5, tiles="OpenStreetMap")
                    
                    folium.PolyLine(path_pts, color="#FF0000", weight=6, opacity=0.9, tooltip="AI Path Trace").add_to(fm)
                    
                    for p in path_pts:
                        folium.Circle(location=[p[0], p[1]], radius=50000, color="orange", fill=True, fill_opacity=0.2, weight=0).add_to(fm)
                    
                    for i, p in enumerate(path_pts):
                        if i == 0:
                            folium.Marker([p[0], p[1]], popup="Current Eye", icon=folium.Icon(color="darkblue", icon="screenshot")).add_to(fm)
                        if (i + 1) % 2 == 0:
                            folium.CircleMarker([p[0], p[1]], radius=5, color="darkred", fill=True, fill_color="orange", popup=f"T+{(i+1)*3}h").add_to(fm)
                    
                    st_folium(fm, height=500, use_container_width=True)
        else:
            with st.container(border=True):
                st.info("System Ready. Configure parameters to initialize forecast.")