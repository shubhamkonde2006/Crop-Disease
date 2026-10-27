"""
Generates realistic high-quality sample leaf images for instant 1-click testing.
Includes healthy and diseased leaves across multiple crops.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_leaf_base(width=600, height=600, base_color=(45, 135, 55)):
    """Creates a realistic leaf shape with natural green gradation and main veins."""
    img = Image.new("RGBA", (width, height), (245, 247, 244, 255))
    draw = ImageDraw.Draw(img)

    # Elliptical / ovate leaf shape coordinates
    cx, cy = width // 2, height // 2
    leaf_polygon = [
        (cx, 70),                     # Leaf tip
        (cx + 170, cy - 80),          # Right upper lobe
        (cx + 200, cy + 40),          # Right middle
        (cx + 120, cy + 180),         # Right lower
        (cx, cy + 240),               # Leaf base
        (cx - 120, cy + 180),         # Left lower
        (cx - 200, cy + 40),          # Left middle
        (cx - 170, cy - 80),          # Left upper lobe
    ]

    # Fill base leaf
    draw.polygon(leaf_polygon, fill=base_color)

    # Draw primary central vein
    draw.line([(cx, 80), (cx, cy + 240)], fill=(75, 170, 85, 255), width=7)

    # Draw secondary lateral veins
    for dy in range(120, cy + 200, 45):
        # Right side veins
        draw.line([(cx, dy), (cx + 130, dy - 30)], fill=(65, 160, 75, 230), width=3)
        # Left side veins
        draw.line([(cx, dy), (cx - 130, dy - 30)], fill=(65, 160, 75, 230), width=3)

    # Add petiole stem
    draw.line([(cx, cy + 240), (cx, cy + 285)], fill=(85, 130, 60, 255), width=8)

    # Smooth the edges slightly
    img = img.filter(ImageFilter.SMOOTH_MORE)
    return img

def add_early_blight_spots(img: Image.Image) -> Image.Image:
    """Adds target-board concentric spots with yellow halos (Alternaria)."""
    draw = ImageDraw.Draw(img)
    spots = [
        (260, 220, 45),
        (350, 310, 55),
        (220, 380, 40),
        (330, 180, 32),
        (380, 260, 28)
    ]
    for x, y, r in spots:
        # Yellow chlorotic halo
        draw.ellipse([x - r - 12, y - r - 12, x + r + 12, y + r + 12], fill=(185, 175, 45, 180))
        # Outer dark ring
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(60, 42, 20, 255))
        # Inner tan ring
        draw.ellipse([x - r + 8, y - r + 8, x + r - 8, y + r - 8], fill=(110, 80, 45, 255))
        # Bullseye center
        draw.ellipse([x - r + 16, y - r + 16, x + r - 16, y + r - 16], fill=(45, 30, 15, 255))
    return img

def add_common_rust_pustules(img: Image.Image) -> Image.Image:
    """Adds cinnamon-brown powdery pustules with chlorotic borders (Puccinia)."""
    draw = ImageDraw.Draw(img)
    np.random.seed(42)
    for _ in range(60):
        rx = np.random.randint(180, 420)
        ry = np.random.randint(120, 460)
        size = np.random.randint(4, 10)
        # Chlorotic border
        draw.ellipse([rx - size - 2, ry - size - 2, rx + size + 2, ry + size + 2], fill=(200, 180, 40, 150))
        # Rust cinnamon pustule
        draw.ellipse([rx - size, ry - size, rx + size, ry + size], fill=(165, 68, 25, 255))
    return img

def add_apple_scab_lesions(img: Image.Image) -> Image.Image:
    """Adds olive-green to dark brown velvety circular lesions (Venturia)."""
    draw = ImageDraw.Draw(img)
    spots = [
        (280, 200, 40),
        (340, 270, 50),
        (230, 330, 35),
        (310, 390, 45),
        (250, 150, 25)
    ]
    for x, y, r in spots:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(55, 65, 30, 240))
        # Irregular scab texture
        draw.ellipse([x - r + 6, y - r + 6, x + r - 6, y + r - 6], fill=(40, 45, 20, 255))
    return img

def add_grape_black_rot_spots(img: Image.Image) -> Image.Image:
    """Adds reddish-brown lesions with black pycnidia specks (Guignardia)."""
    draw = ImageDraw.Draw(img)
    spots = [
        (270, 240, 42),
        (340, 330, 48),
        (230, 360, 36),
        (360, 210, 30)
    ]
    for x, y, r in spots:
        # Reddish brown lesion
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(130, 55, 35, 255))
        draw.ellipse([x - r + 4, y - r + 4, x + r - 4, y + r - 4], fill=(160, 85, 50, 255))
        # Tiny black specks
        for dx, dy in [(-8, -4), (5, 6), (0, -10), (9, -2)]:
            draw.ellipse([x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2], fill=(20, 15, 10, 255))
    return img

def generate_samples():
    sample_dir = Path(__file__).resolve().parent / "sample_images"
    sample_dir.mkdir(parents=True, exist_ok=True)

    samples = [
        {
            "filename": "tomato_early_blight.jpg",
            "crop": "Tomato",
            "name": "Tomato Early Blight",
            "healthy": False,
            "decorator": add_early_blight_spots,
            "base_color": (50, 125, 45)
        },
        {
            "filename": "potato_healthy.jpg",
            "crop": "Potato",
            "name": "Potato Healthy Leaf",
            "healthy": True,
            "decorator": None,
            "base_color": (35, 140, 50)
        },
        {
            "filename": "corn_common_rust.jpg",
            "crop": "Corn",
            "name": "Corn Common Rust",
            "healthy": False,
            "decorator": add_common_rust_pustules,
            "base_color": (60, 130, 40)
        },
        {
            "filename": "apple_scab.jpg",
            "crop": "Apple",
            "name": "Apple Scab Leaf",
            "healthy": False,
            "decorator": add_apple_scab_lesions,
            "base_color": (40, 120, 50)
        },
        {
            "filename": "bell_pepper_healthy.jpg",
            "crop": "Bell Pepper",
            "name": "Bell Pepper Healthy Leaf",
            "healthy": True,
            "decorator": None,
            "base_color": (30, 145, 60)
        },
        {
            "filename": "grape_black_rot.jpg",
            "crop": "Grape",
            "name": "Grape Black Rot",
            "healthy": False,
            "decorator": add_grape_black_rot_spots,
            "base_color": (55, 135, 45)
        }
    ]

    manifest = []
    for s in samples:
        leaf_img = create_leaf_base(base_color=s["base_color"])
        if s["decorator"]:
            leaf_img = s["decorator"](leaf_img)
        # Convert RGBA to RGB with clean light background
        rgb_img = Image.new("RGB", leaf_img.size, (245, 247, 244))
        rgb_img.paste(leaf_img, mask=leaf_img.split()[3])

        out_path = sample_dir / s["filename"]
        rgb_img.save(out_path, "JPEG", quality=92)
        print(f"Generated sample: {out_path.name}")

        manifest.append({
            "id": Path(s["filename"]).stem,
            "filename": s["filename"],
            "crop": s["crop"],
            "expected_disease": "Healthy" if s["healthy"] else s["name"].replace(f"{s['crop']} ", ""),
            "display_name": s["name"],
            "is_healthy": s["healthy"],
            "image_url": f"/samples/{s['filename']}"
        })

    import json
    with open(sample_dir / "samples_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Sample images generated successfully.")

if __name__ == "__main__":
    generate_samples()
