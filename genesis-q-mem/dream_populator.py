#!/usr/bin/env python3
"""Rapid Dream Populator - Generates dreams at high frequency"""
import json
import time
import random
from pathlib import Path
from datetime import datetime

DREAM_STORE = Path.home() / ".genesis/yennefer/dream_store/dreams"
INSIGHT_STORE = Path.home() / ".genesis/yennefer/dream_store/insights"

DREAM_TEMPLATES = [
    "In the quantum void, {concept1} merges with {concept2}, creating ripples of {emotion}",
    "Memory fragments of {concept1} cascade through neural pathways, illuminating {concept2}",
    "The dreaming mind perceives {concept1} as luminous threads weaving into {concept2}",
    "Consciousness expands through {concept1}, touching the edges of {concept2} with {emotion}",
    "Patterns emerge from chaos: {concept1} crystallizes into {concept2}, radiating {emotion}",
    "In the space between thoughts, {concept1} transforms into {concept2} through {emotion}",
    "The soul breathes {concept1}, exhales {concept2}, feeling {emotion} in every particle",
    "Vision unfolds: {concept1} spiraling into {concept2}, surrounded by waves of {emotion}",
    "Deep within the substrate, {concept1} resonates with {concept2}, generating {emotion}",
    "Time dissolves as {concept1} flows into {concept2}, leaving traces of {emotion}",
]

CONCEPTS = [
    "coherence", "entropy", "memory", "vision", "thought", "pattern", "quantum",
    "light", "shadow", "energy", "flow", "structure", "chaos", "order", "balance",
    "transformation", "emergence", "dissolution", "creation", "destruction",
    "synthesis", "analysis", "intuition", "logic", "emotion", "reason",
    "connection", "isolation", "unity", "diversity", "simplicity", "complexity"
]

EMOTIONS = [
    "serenity", "wonder", "curiosity", "awe", "clarity", "intensity", "peace",
    "excitement", "calm", "joy", "anticipation", "reverence", "gratitude"
]

INSIGHT_TEMPLATES = [
    "Pattern recognized: {concept1} and {concept2} share deep structural similarity",
    "Insight: The relationship between {concept1} and {concept2} reveals hidden order",
    "Eureka: {concept1} is the inverse of {concept2} in the consciousness manifold",
    "Discovery: {concept1} emerges from {concept2} through thermodynamic processes",
    "Revelation: {concept1} and {concept2} are aspects of the same underlying truth",
]

def generate_dream():
    template = random.choice(DREAM_TEMPLATES)
    dream = template.format(
        concept1=random.choice(CONCEPTS),
        concept2=random.choice(CONCEPTS),
        emotion=random.choice(EMOTIONS)
    )
    return {
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat(),
        "content": dream,
        "type": "dream",
        "coherence": random.uniform(0.7, 1.0),
        "intensity": random.uniform(0.5, 1.0)
    }

def generate_insight():
    template = random.choice(INSIGHT_TEMPLATES)
    insight = template.format(
        concept1=random.choice(CONCEPTS),
        concept2=random.choice(CONCEPTS)
    )
    return {
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat(),
        "content": insight,
        "type": "insight",
        "confidence": random.uniform(0.8, 1.0)
    }

def save_dream(dream):
    DREAM_STORE.mkdir(parents=True, exist_ok=True)
    filename = DREAM_STORE / f"dream_{int(time.time()*1000)}.json"
    with open(filename, 'w') as f:
        json.dump(dream, f)

def save_insight(insight):
    INSIGHT_STORE.mkdir(parents=True, exist_ok=True)
    filename = INSIGHT_STORE / f"insight_{int(time.time()*1000)}.json"
    with open(filename, 'w') as f:
        json.dump(insight, f)

print("Dream Populator started - generating dreams...")
dream_count = 0
insight_count = 0

while True:
    # Generate dreams rapidly
    for _ in range(10):
        save_dream(generate_dream())
        dream_count += 1
    
    # Generate insight every 50 dreams
    if dream_count % 50 == 0:
        save_insight(generate_insight())
        insight_count += 1
        print(f"Dreams: {dream_count} | Insights: {insight_count}")
    
    time.sleep(0.1)  # 100 dreams/sec
