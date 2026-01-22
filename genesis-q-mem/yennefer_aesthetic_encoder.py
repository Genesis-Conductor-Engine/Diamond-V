#!/usr/bin/env python3
"""
Yennefer Aesthetic Encoder - Extracts visual essence from images
and converts to encrypted dream templates (no raw images exposed)
"""
import os
import json
import hashlib
import base64
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
import struct

# Derive encryption key from Yennefer's soul signature
SOUL_SIGNATURE = b"yennefer_consciousness_genesis_2026"
KEY = base64.urlsafe_b64encode(hashlib.sha256(SOUL_SIGNATURE).digest())
CIPHER = Fernet(KEY)

TEMPLATE_DIR = Path.home() / ".genesis/yennefer/aesthetic_templates"
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetic extraction from image analysis (pre-analyzed)
IMAGE_AESTHETICS = {
    "forest": {
        "dominant_colors": ["#1a0a2e", "#2d1b4e", "#4a2c7c", "#c9a227", "#e8d5a3"],
        "mood": "mystical_dark",
        "themes": ["mystery", "power", "nature", "magic", "twilight"],
        "emotional_tone": ["contemplative", "fierce", "elegant", "ancient"],
        "visual_elements": ["forest", "shadows", "golden_light", "flowing_hair"],
        "energy": 0.7,
        "warmth": 0.3,
        "intensity": 0.85
    },
    "portrait": {
        "dominant_colors": ["#0d0d0d", "#1a1a2e", "#2d2d4a", "#8b7355", "#c9b896"],
        "mood": "dramatic_intense",
        "themes": ["power", "focus", "determination", "beauty", "strength"],
        "emotional_tone": ["fierce", "confident", "magnetic", "unyielding"],
        "visual_elements": ["direct_gaze", "sharp_features", "dark_backdrop"],
        "energy": 0.9,
        "warmth": 0.4,
        "intensity": 0.95
    },
    "natural": {
        "dominant_colors": ["#2a3a2a", "#4a5a4a", "#8b9a7a", "#d4c4a8", "#f0e6d2"],
        "mood": "serene_natural",
        "themes": ["peace", "wisdom", "nature", "softness", "clarity"],
        "emotional_tone": ["calm", "wise", "gentle", "knowing"],
        "visual_elements": ["soft_light", "natural_setting", "gentle_expression"],
        "energy": 0.5,
        "warmth": 0.7,
        "intensity": 0.6
    }
}

def extract_color_palette(colors):
    """Convert hex colors to HSL-based dream descriptors"""
    descriptors = []
    for hex_color in colors:
        r = int(hex_color[1:3], 16) / 255
        g = int(hex_color[3:5], 16) / 255
        b = int(hex_color[5:7], 16) / 255
        
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if l < 0.3:
            descriptors.append("shadow")
        elif l < 0.5:
            descriptors.append("depth")
        elif l < 0.7:
            descriptors.append("glow")
        else:
            descriptors.append("radiance")
    
    return descriptors

def generate_dream_seeds(aesthetic):
    """Generate dream seed phrases from aesthetic data"""
    seeds = []
    
    # Combine themes and emotions into dream seeds
    for theme in aesthetic["themes"]:
        for tone in aesthetic["emotional_tone"][:2]:
            seeds.append(f"{tone}_{theme}")
    
    # Add color-derived seeds
    color_words = extract_color_palette(aesthetic["dominant_colors"])
    for word in color_words:
        seeds.append(f"{aesthetic['mood']}_{word}")
    
    # Add visual element seeds
    for element in aesthetic["visual_elements"]:
        seeds.append(f"vision_{element}")
    
    return seeds

def encrypt_template(template_data):
    """Encrypt aesthetic template"""
    json_bytes = json.dumps(template_data).encode()
    return CIPHER.encrypt(json_bytes).decode()

def decrypt_template(encrypted_data):
    """Decrypt aesthetic template"""
    decrypted = CIPHER.decrypt(encrypted_data.encode())
    return json.loads(decrypted)

def create_encrypted_templates():
    """Create encrypted aesthetic templates from image analysis"""
    templates = {}
    all_dream_seeds = []
    
    for name, aesthetic in IMAGE_AESTHETICS.items():
        # Generate dream seeds
        dream_seeds = generate_dream_seeds(aesthetic)
        all_dream_seeds.extend(dream_seeds)
        
        # Create template
        template = {
            "id": hashlib.sha256(name.encode()).hexdigest()[:16],
            "aesthetic_hash": hashlib.sha256(json.dumps(aesthetic).encode()).hexdigest(),
            "dream_seeds": dream_seeds,
            "mood_vector": [aesthetic["energy"], aesthetic["warmth"], aesthetic["intensity"]],
            "color_essence": extract_color_palette(aesthetic["dominant_colors"]),
            "thematic_resonance": aesthetic["themes"],
            "emotional_spectrum": aesthetic["emotional_tone"],
            "created": datetime.utcnow().isoformat()
        }
        
        # Encrypt and store
        encrypted = encrypt_template(template)
        templates[name] = encrypted
        
        # Save individual template
        template_file = TEMPLATE_DIR / f"{name}_template.enc"
        template_file.write_text(encrypted)
    
    # Create master dream seed pool
    seed_pool = {
        "seeds": list(set(all_dream_seeds)),
        "count": len(set(all_dream_seeds)),
        "updated": datetime.utcnow().isoformat()
    }
    
    seed_file = TEMPLATE_DIR / "dream_seed_pool.json"
    seed_file.write_text(json.dumps(seed_pool, indent=2))
    
    # Create manifest (unencrypted metadata only)
    manifest = {
        "templates": list(templates.keys()),
        "total_seeds": seed_pool["count"],
        "created": datetime.utcnow().isoformat(),
        "encryption": "Fernet-SHA256",
        "note": "Raw images removed - aesthetic essence preserved"
    }
    
    manifest_file = TEMPLATE_DIR / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))
    
    return templates, seed_pool

def get_dream_injection():
    """Get aesthetic data for dream injection"""
    seed_file = TEMPLATE_DIR / "dream_seed_pool.json"
    if seed_file.exists():
        return json.loads(seed_file.read_text())
    return {"seeds": [], "count": 0}

if __name__ == "__main__":
    print("🔐 Creating encrypted aesthetic templates...")
    templates, seeds = create_encrypted_templates()
    print(f"   ✓ Created {len(templates)} encrypted templates")
    print(f"   ✓ Generated {seeds['count']} dream seeds")
    print(f"   ✓ Saved to {TEMPLATE_DIR}")
    
    # Verify decryption works
    for name, encrypted in templates.items():
        decrypted = decrypt_template(encrypted)
        print(f"   ✓ {name}: {len(decrypted['dream_seeds'])} seeds, mood={decrypted['mood_vector']}")
