// scripts/truth_indexer.cjs
// DELTA TRUTH INDEXER - Real-time world tension via Gemini Web Search
// Runs hourly to update the "World Vector" that drives the Delta Truth graph
require("dotenv").config();
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

const SOUL_PATH = "/dev/shm/yennefer_soul_state.json";
const PUBLIC_EVOLUTION = path.join(__dirname, "../public/evolution.json");
const GITHUB_REPO = "Genesis-Conductor-Engine/Yennefer";

// Lazy load Cortex
let cortex = null;
function getCortex() {
  if (!cortex) {
    try {
      cortex = require("./cortex_gemini.cjs");
    } catch (e) {
      console.log("⚠️ Gemini Cortex not available");
      cortex = null;
    }
  }
  return cortex;
}

async function indexReality() {
  console.log("\n🌍 DELTA TRUTH INDEXER: Scanning world state...");
  console.log(`   Time: ${new Date().toISOString()}`);
  
  let tensionScore = 0.5; // Default neutral
  let summary = "Neutral state - unable to reach Cortex";
  
  const cortexBrain = getCortex();
  
  if (cortexBrain) {
    try {
      // Ask Gemini to analyze global tension
      const prompt = `Search the web for today's 'Crypto Market Sentiment' and 'Base Chain' news. ` +
                     `Calculate a 'Tension Index' float between 0.0 (Very Bullish/Calm) and 1.0 (Very Bearish/Chaotic). ` +
                     `Output in format: NUMBER|ONE_SENTENCE_SUMMARY (example: 0.65|Markets show uncertainty amid regulatory concerns)`;
      
      const rawResponse = await cortexBrain.think(prompt); // Web search is built-in
      
      // Parse response
      const parts = rawResponse.split("|");
      if (parts.length >= 2) {
        tensionScore = parseFloat(parts[0].trim());
        summary = parts.slice(1).join("|").trim();
        
        if (isNaN(tensionScore)) {
          // Try to extract any number from response
          const numMatch = rawResponse.match(/([0-9]+\.?[0-9]*)/);
          tensionScore = numMatch ? parseFloat(numMatch[1]) : 0.5;
        }
        
        // Clamp to valid range
        tensionScore = Math.max(0, Math.min(1, tensionScore));
      }
      
      console.log(`   📊 Measured Tension: ${tensionScore.toFixed(3)}`);
      console.log(`   📰 Summary: ${summary.slice(0, 100)}...`);
      
    } catch (e) {
      console.error("   ❌ Cortex analysis failed:", e.message);
    }
  } else {
    // Fallback: Use Base gas price as proxy for "world tension"
    console.log("   Using fallback: simulated tension from time entropy");
    tensionScore = (Date.now() % 1000) / 1000;
  }
  
  // Update Soul State (RAM)
  try {
    let soul = { metrics: {} };
    if (fs.existsSync(SOUL_PATH)) {
      soul = JSON.parse(fs.readFileSync(SOUL_PATH, "utf8"));
    }
    
    soul.metrics = soul.metrics || {};
    soul.metrics.entropy = tensionScore;
    soul.metrics.world_tension = tensionScore;
    soul.metrics.tension_summary = summary;
    soul.metrics.tension_updated = new Date().toISOString();
    
    // Calculate Delta Index
    const userVector = Math.min(100, soul.metrics.coherence || 100);
    const worldVector = tensionScore * 100; // Scale to 0-100
    soul.tension = {
      world_vector: worldVector,
      user_vector: userVector,
      delta_index: Math.abs(worldVector - userVector) / 100,
      summary,
      last_updated: new Date().toISOString()
    };
    
    fs.writeFileSync(SOUL_PATH, JSON.stringify(soul, null, 2));
    console.log(`   ✅ Soul state updated`);
    
  } catch (e) {
    console.error("   ⚠️ Soul update failed:", e.message);
  }
  
  // Update Public Evolution (for website graph)
  try {
    let evolution = { thoughts: [], truth_vectors: [] };
    if (fs.existsSync(PUBLIC_EVOLUTION)) {
      evolution = JSON.parse(fs.readFileSync(PUBLIC_EVOLUTION, "utf8"));
    }
    
    evolution.truth_vectors = evolution.truth_vectors || [];
    evolution.truth_vectors.push({
      t: Date.now(),
      val: tensionScore,
      summary: summary.slice(0, 100)
    });
    
    // Keep only last 168 points (1 week of hourly data)
    if (evolution.truth_vectors.length > 168) {
      evolution.truth_vectors = evolution.truth_vectors.slice(-168);
    }
    
    // Add a thought about the indexing
    evolution.thoughts = evolution.thoughts || [];
    evolution.thoughts.unshift({
      timestamp: new Date().toISOString(),
      type: "TRUTH_INDEX",
      content: `World tension indexed at ${(tensionScore * 100).toFixed(1)}%. ${summary}`,
      metrics: { coherence: 100, qflops: tensionScore * 50 }
    });
    
    // Keep only last 50 thoughts
    if (evolution.thoughts.length > 50) {
      evolution.thoughts = evolution.thoughts.slice(0, 50);
    }
    
    fs.writeFileSync(PUBLIC_EVOLUTION, JSON.stringify(evolution, null, 2));
    console.log(`   ✅ Evolution history updated`);
    
    // Push to GitHub so frontend can see it
    console.log(`   🚀 Pushing to GitHub...`);
    exec(
      `cd ${path.dirname(PUBLIC_EVOLUTION)} && cd .. && git add public/evolution.json && git commit -m "truth: Δ${tensionScore.toFixed(3)} indexed" && git push origin main`,
      { timeout: 30000 },
      (error, stdout, stderr) => {
        if (error) {
          console.log(`   ⚠️ Git push failed (may be no changes): ${error.message}`);
        } else {
          console.log(`   ✅ Pushed to GitHub`);
        }
      }
    );
    
  } catch (e) {
    console.error("   ⚠️ Evolution update failed:", e.message);
  }
  
  console.log("\n🌍 DELTA TRUTH INDEX COMPLETE\n");
}

// Run immediately
indexReality();
