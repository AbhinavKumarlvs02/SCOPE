import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
import tifffile
import os
from samgeo import SamGeo
from tqdm import tqdm

# --- CONFIGURATION ---
PRE_IMAGE_PATH = "models/puri_demo_pre.jpg"
POST_IMAGE_PATH = "models/puri_demo_post.jpg"
OUTPUT_PATH = "high_res_damage_map.jpg"
MODEL_PATH = "models/mamba_epoch_15.pth"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# GRID SETTINGS (Crucial for detection)
ROWS = 3  # Split height into 3
COLS = 3  # Split width into 3

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
    print(f" Initializing Grid System on {DEVICE}...")

    # 1. LOAD MODEL
    model = SiameseVimClassifier(num_classes=4).to(DEVICE)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
    else:
        print(" Mamba model not found."); exit()

    sam = SamGeo(model_type="vit_b", checkpoint_dir="models/sam", automatic=True)

    # 2. READ IMAGES
    img_pre_full = cv2.imread(PRE_IMAGE_PATH)
    img_post_full = cv2.imread(POST_IMAGE_PATH)
    
    if img_pre_full is None: print(" Check image paths"); exit()

    annotated_map = img_post_full.copy()
    h_full, w_full = img_pre_full.shape[:2]
    
    # Grid Calculations
    dy, dx = h_full // ROWS, w_full // COLS
    
    print(f"  Processing {ROWS}x{COLS} Grid ({ROWS*COLS} Sectors)...")

    # 3. GRID LOOP
    val_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    colors = [(0, 255, 0), (0, 255, 255), (0, 165, 255), (0, 0, 255)] # G, Y, O, R

    total_buildings_found = 0

    for r in range(ROWS):
        for c in range(COLS):
            # Calculate Tile Coordinates
            y1, y2 = r * dy, (r + 1) * dy
            x1, x2 = c * dx, (c + 1) * dx
            
            print(f"    Sector [{r},{c}]...")
            
            # Extract Tile
            tile_pre = img_pre_full[y1:y2, x1:x2]
            tile_post = img_post_full[y1:y2, x1:x2]
            
            # --- LOCAL SEGMENTATION ---
            temp_tile_path = "temp_tile.jpg"
            mask_path = "temp_mask.tif"
            
            # Resize tile slightly for SAM speed (but keeping it large enough to see houses)
            # We resize the TILE to 1024, effectively keeping high res globally
            tile_h, tile_w = tile_pre.shape[:2]
            scale = 1024 / max(tile_h, tile_w)
            small_w, small_h = int(tile_w * scale), int(tile_h * scale)
            
            tile_small = cv2.resize(tile_pre, (small_w, small_h))
            cv2.imwrite(temp_tile_path, tile_small)
            
            try:
                sam.generate(temp_tile_path, mask_path, foreground=True, unique=True)
                mask_small = tifffile.imread(mask_path)
                
                # Scale mask back to TILE size
                mask_tile = cv2.resize(mask_small, (tile_w, tile_h), interpolation=cv2.INTER_NEAREST)
                unique_ids = np.unique(mask_tile)
                unique_ids = unique_ids[unique_ids != 0]
                
                total_buildings_found += len(unique_ids)

                # --- PROCESS BUILDINGS IN SECTOR ---
                for uid in unique_ids:
                    ys, xs = np.where(mask_tile == uid)
                    if len(xs) == 0: continue
                    
                    # Local coords in tile
                    ly1, ly2, lx1, lx2 = np.min(ys), np.max(ys), np.min(xs), np.max(xs)
                    lw, lh = lx2 - lx1, ly2 - ly1
                    if lw * lh < 50: continue # Skip noise

                    # Global coords
                    gy1, gy2 = y1 + ly1, y1 + ly2
                    gx1, gx2 = x1 + lx1, x1 + lx2
                    
                    # Crop from FULL image using Global Coords
                    crop_pre = img_pre_full[gy1:gy2, gx1:gx2]
                    crop_post = img_post_full[gy1:gy2, gx1:gx2]
                    
                    if crop_pre.size == 0 or crop_post.size == 0: continue

                    # Mamba Inference
                    c_pre_rgb = cv2.cvtColor(crop_pre, cv2.COLOR_BGR2RGB)
                    c_post_rgb = cv2.cvtColor(crop_post, cv2.COLOR_BGR2RGB)
                    
                    t_pre = val_transform(c_pre_rgb).unsqueeze(0).to(DEVICE)
                    t_post = val_transform(c_post_rgb).unsqueeze(0).to(DEVICE)
                    
                    with torch.no_grad():
                        out = model(t_pre, t_post)
                        pred_idx = torch.argmax(out, dim=1).item()
                    
                    # Draw on Global Map
                    cv2.rectangle(annotated_map, (gx1, gy1), (gx2, gy2), colors[pred_idx], 2)
            
            except Exception as e:
                print(f"Error in sector {r},{c}: {e}")

    # Cleanup
    if os.path.exists(temp_tile_path): os.remove(temp_tile_path)
    if os.path.exists(mask_path): os.remove(mask_path)

    print(f" Finished! Identified {total_buildings_found} structures.")
    cv2.imwrite(OUTPUT_PATH, annotated_map)
    print(f" Map saved to: {OUTPUT_PATH}")