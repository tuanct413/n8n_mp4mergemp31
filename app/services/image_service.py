import base64
import io
import os
import requests
import logging
from PIL import Image, ImageOps, ImageStat
from app.models.image_models import ImageMergeRequest

logger = logging.getLogger(__name__)

ASSETS_DIR = "app/assets"
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

def process_logo(logo_path: str) -> Image.Image:
    """
    Load the logo and make the black background transparent.
    The logo is white text/graphics on a black background.
    """
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo not found at {logo_path}")
    
    logo = Image.open(logo_path).convert("RGBA")
    
    # Extract the data
    datas = logo.getdata()
    
    new_data = []
    for item in datas:
        # item is (R, G, B, A)
        brightness = sum(item[:3]) / 3
        if brightness < 30:  # Threshold for black
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
            
    logo.putdata(new_data)
    return logo

def get_best_position(image: Image.Image, logo_width: int, logo_height: int, padding: int) -> tuple[int, int]:
    width, height = image.size
    
    # Define candidate positions with a baseline location penalty.
    # Lower penalty = more preferred by default.
    corners = {
        "bottom_right": (width - logo_width - padding, height - logo_height - padding, 0),
        "bottom_left": (padding, height - logo_height - padding, 20),
        "top_right": (width - logo_width - padding, padding, 50),
        "top_left": (padding, padding, 70),
        "bottom_center": ((width - logo_width) // 2, height - logo_height - padding, 40),
        "top_center": ((width - logo_width) // 2, padding, 80),
    }
    
    best_corner = None
    best_score = float('inf')
    
    # Convert image to grayscale for analysis
    gray_image = image.convert("L")
    
    for name, (x, y, loc_penalty) in corners.items():
        # Ensure box is within image bounds
        x = max(0, min(x, width - logo_width))
        y = max(0, min(y, height - logo_height))
        box = (x, y, x + logo_width, y + logo_height)
        
        # Crop region
        region = gray_image.crop(box)
        stat = ImageStat.Stat(region)
        
        mean = stat.mean[0]
        stddev = stat.stddev[0]
        
        # 1. Variance penalty (Detail/Clutter) - penalize heavily to avoid covering faces/objects
        variance_penalty = stddev * 3
        
        # 2. Brightness penalty - Logo is white, so if the background is too bright (>150),
        # the logo will be invisible. Apply massive penalty for bright areas.
        brightness_penalty = mean
        if mean > 180:
            brightness_penalty += (mean - 180) * 10 
            
        # Total score combining all factors (lower is better)
        score = variance_penalty + brightness_penalty + loc_penalty
        
        logger.info(f"Analyzed {name} - M:{mean:.1f}, SD:{stddev:.1f}, LocP:{loc_penalty} -> Score: {score:.1f}")
        
        if score < best_score:
            best_score = score
            best_corner = (x, y)
            
    # Fallback to bottom right if everything fails wildly
    return best_corner or (width - logo_width - padding, height - logo_height - padding)

def merge_logo_to_image(request: ImageMergeRequest) -> io.BytesIO:
    """
    Fetch target image, process logo, and merge them.
    Returns a BytesIO object of the resulting image.
    """
    # 1. Load target image
    if request.image_url:
        logger.info(f"Downloading image from {request.image_url}")
        resp = requests.get(request.image_url, timeout=10)
        resp.raise_for_status()
        target_img = Image.open(io.BytesIO(resp.content))
    elif request.image_base64:
        logger.info("Decoding image from base64")
        base64_data = request.image_base64
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]
        img_data = base64.b64decode(base64_data)
        target_img = Image.open(io.BytesIO(img_data))
    else:
        raise ValueError("Either image_url or image_base64 must be provided")

    target_img = target_img.convert("RGBA")
    width, height = target_img.size

    # 2. Process logo
    logo = process_logo(LOGO_PATH)
    
    # 3. Scale logo
    logo_height = int(height * request.scale)
    aspect_ratio = logo.width / logo.height
    logo_width = int(logo_height * aspect_ratio)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    
    # 4. Calculate position
    if request.auto_position:
        x, y = get_best_position(target_img, logo_width, logo_height, request.padding)
        logger.info(f"Auto-selected position: ({x}, {y})")
    elif request.position_ratio:
        x = int(width * request.position_ratio[0] - logo_width)
        y = int(height * request.position_ratio[1] - logo_height)
    else:
        # Default fallback to bottom-right
        x = int(width * 0.95 - logo_width)
        y = int(height * 0.95 - logo_height)
        
    # Ensure it's within bounds
    x = max(0, min(x, width - logo_width))
    y = max(0, min(y, height - logo_height))
    
    # 5. Paste logo
    target_img.paste(logo, (x, y), logo)
    
    # Convert back to RGB for saving as JPEG
    final_img = target_img.convert("RGB")
    
    output = io.BytesIO()
    final_img.save(output, format="JPEG", quality=95)
    output.seek(0)
    
    return output
