from PIL import Image, ImageEnhance

def resize_image(in_path, out_path):
    img = Image.open(in_path)
    w, h = img.size
    # Shrink resolution dimensions to 50%
    img_resized = img.resize((int(w * 0.5), int(h * 0.5)), Image.Resampling.LANCZOS)
    
    # Save using explicit JPEG optimization parameters to guarantee downscaling size drops
    if img_resized.mode in ("RGBA", "P"):
        img_resized = img_resized.convert("RGB")
    img_resized.save(out_path, "JPEG", optimize=True, quality=50)

def enhance_image(in_path, out_path):
    img = Image.open(in_path)
    enhancer = ImageEnhance.Contrast(img)
    img_enhanced = enhancer.enhance(1.4) # Amplify matrix contrast grids
    
    # Retain structural file data limits during overwrite
    if img_enhanced.mode in ("RGBA", "P"):
        img_enhanced = img_enhanced.convert("RGB")
    img_enhanced.save(out_path, "JPEG", optimize=True, quality=85)