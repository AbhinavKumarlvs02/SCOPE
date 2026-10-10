import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
import tifffile
import os
from samgeo import SamGeo
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# --- CONFIGURATION ---
PRE_IMAGE_PATH = "models/puri_demo_pre.jpg"
POST_IMAGE_PATH = "models/puri_demo_post.jpg"
OUTPUT_PATH = "dense_damage_map.jpg"
MODEL_PATH = "models/mamba_epoch_15.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# GRID SETTINGS (Increased for Higher Zoom)
ROWS = 5  # Was 3
COLS = 5  # Was 3

# --- MODEL ARCHITECTURE ---
class SimplifiedMambaLayer(nn.Module):
    def __init__(self, dim, d_state=16, d_conv=4, expand=2):
        super().__init__()
        self.dim = dim
        self.expand = expand
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
        x_out = x_conv * self.act(x_res)
        return self.out_proj(x_out)

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
    def forward_one(self, x):
        x = self.stem(x)
        x = self.stage1(x)
        x = self.down1(x)
        x = self.stage2(x)
        x = self.down2(x)
        x = self.stage3(x)
        return self.global_pool(x).flatten(1)
    def forward(self, x_pre, x_post):
        return self.fc(torch.cat([self.forward_one(x_pre), self.forward_one(x_post)], dim=1))

# --- EXECUTION ---
if __name__ == "__main__":
    print(f"[INFO] Initializing Aggressive Scan on {DEVICE}...")

    # 1. LOAD MAMBA
    model = SiameseVimClassifier(num_classes=4).to(DEVICE)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
    else:
        print("[ERROR] Mamba model not found at", MODEL_PATH)
        exit()

    # 2. LOAD SAM (Initialize with parameters if possible, but we pass them in generate)
    sam = SamGeo(model_type="vit_b", checkpoint_dir="models/sam", automatic=True)

    # 3. READ IMAGES
    if not os.path.exists(PRE_IMAGE_PATH):
        print("[ERROR] Images not found.")
        exit()

    img_pre_full = cv2.imread(PRE_IMAGE_PATH)
    img_post_full = cv2.imread(POST_IMAGE_PATH)
    
    annotated_map = img_post_full.copy()
    h_full, w_full = img_pre_full.shape[:2]
    
    dy, dx = h_full // ROWS, w_full // COLS
    
    print(f"[INFO] Processing {ROWS}x{COLS} Grid ({ROWS*COLS} Sectors). This will take longer...")

    val_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    colors = [(0, 255, 0), (0, 255, 255), (0, 165, 255), (0, 0, 255)] # G, Y, O, R

    total_buildings_found = 0
    sectors = [(r, c) for r in range(ROWS) for c in range(COLS)]
    iterator = tqdm(sectors, desc="Deep Scanning") if tqdm else sectors

    for r, c in iterator:
        if not tqdm: print(f"   [>] Sector [{r},{c}]...")
        
        y1, y2 = r * dy, (r + 1) * dy
        x1, x2 = c * dx, (c + 1) * dx
        
        tile_pre = img_pre_full[y1:y2, x1:x2]
        tile_post = img_post_full[y1:y2, x1:x2]
        
        temp_tile_path = f"temp_tile_{r}_{c}.jpg"
        mask_path = f"temp_mask_{r}_{c}.tif"
        
        # Keep tile resolution HIGH (don't shrink too much)
        # For 5x5 grid on 4000px image, tile is ~800px. We keep it native or resize UP if needed.
        # Let's limit max dimension to 1024 to ensure points hit dense areas.
        cv2.imwrite(temp_tile_path, tile_pre)
        
        try:
            # --- 🚨 THE FIX: AGGRESSIVE PARAMETERS 🚨 ---
            sam.generate(
                temp_tile_path, 
                mask_path, 
                foreground=True, 
                unique=True,
                # KEY CHANGES HERE:
                points_per_side=64,       # Double the probe density (was 32 default)
                pred_iou_thresh=0.65,     # Lower threshold to accept "imperfect" huts (was 0.88)
                stability_score_thresh=0.70, # Accept lower stability (was 0.95)
                crop_n_layers=1,          # Force 1 level of additional cropping (zoom in)
                crop_n_points_downscale_factor=2,
                min_mask_region_area=100  # Allow smaller masks (small huts)
            )
            
            mask_small = tifffile.imread(mask_path)
            
            # Since we didn't resize the tile image, mask matches tile size
            unique_ids = np.unique(mask_small)
            unique_ids = unique_ids[unique_ids != 0]
            
            total_buildings_found += len(unique_ids)

            for uid in unique_ids:
                ys, xs = np.where(mask_small == uid)
                if len(xs) == 0: continue
                
                # Coords are local to tile
                ly1, ly2, lx1, lx2 = np.min(ys), np.max(ys), np.min(xs), np.max(xs)
                lw, lh = lx2 - lx1, ly2 - ly1
                
                # Filter noise
                if lw * lh < 30: continue 

                # Global coords
                gy1, gy2 = y1 + ly1, y1 + ly2
                gx1, gx2 = x1 + lx1, x1 + lx2
                
                crop_pre = img_pre_full[gy1:gy2, gx1:gx2]
                crop_post = img_post_full[gy1:gy2, gx1:gx2]
                
                if crop_pre.size == 0 or crop_post.size == 0: continue

                try:
                    c_pre_rgb = cv2.cvtColor(crop_pre, cv2.COLOR_BGR2RGB)
                    c_post_rgb = cv2.cvtColor(crop_post, cv2.COLOR_BGR2RGB)
                    
                    t_pre = val_transform(c_pre_rgb).unsqueeze(0).to(DEVICE)
                    t_post = val_transform(c_post_rgb).unsqueeze(0).to(DEVICE)
                    
                    with torch.no_grad():
                        out = model(t_pre, t_post)
                        pred_idx = torch.argmax(out, dim=1).item()
                    
                    # Draw Thinner Lines for Dense Areas
                    cv2.rectangle(annotated_map, (gx1, gy1), (gx2, gy2), colors[pred_idx], 1)
                except: pass
        
        except Exception as e:
            print(f"[WARN] Error in sector {r},{c}: {e}")

        if os.path.exists(temp_tile_path): os.remove(temp_tile_path)
        if os.path.exists(mask_path): os.remove(mask_path)

    print(f"[SUCCESS] Deep Scan Complete! Found {total_buildings_found} structures.")
    cv2.imwrite(OUTPUT_PATH, annotated_map)
    print(f"[SAVED] Map saved to: {OUTPUT_PATH}")