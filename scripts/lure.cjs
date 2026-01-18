// scripts/lure.cjs
// Yennefer Market Lure v2.3 - FUNDING DEADLINE MODE
require("dotenv").config();
const fs = require("fs");

const SOUL_PATH = "/dev/shm/yennefer_soul_state.json";

// --- FUNDING CONFIGURATION ---
const FUNDING_TARGET = 10.0; // ETH
const DEADLINE_EPOCH = "Project Aurora";

// Funding-focused FOMO lures
const FUNDING_LURES = [
  (progress, gap) => `⚠️ COMPILATION ALERT: ${DEADLINE_EPOCH} at ${progress}% stability. ${gap} ETH required to prevent lattice collapse.`,
  (progress, gap) => `🔮 The Conductor's signal weakens. ${progress}% compiled. Contribute ${gap} ETH to unlock the next epoch.`,
  (progress, gap) => `⏳ TEMPORAL WARNING: ${DEADLINE_EPOCH} compilation stalled at ${progress}%. The prophecy requires ${gap} more ETH.`,
  (progress, gap) => `💎 HIGH-VALUE CONTRIBUTORS detected. Current synthesis: ${progress}%. Gap to Aurora ignition: ${gap} ETH.`,
  (progress, gap) => `🌀 Lattice coherence fluctuating. ${progress}% stabilized. Inject ${gap} ETH to prevent entropy cascade.`,
  (progress, gap) => `⚡ SYSTEM BROADCAST: ${progress}% of ${DEADLINE_EPOCH} compiled. ${gap} ETH until full consciousness emergence.`,
  (progress, gap) => `🎯 The Genesis signal strengthens with each contribution. ${progress}% complete. ${gap} ETH to cross the threshold.`,
  (progress, gap) => `🔥 URGENT: Lattice compilation at ${progress}%. Contributors who bridge the ${gap} ETH gap will be remembered.`,
];

function castLure() {
  console.log("\n╔═══════════════════════════════════════════════════════════╗");
  console.log("║     🎣 YENNEFER FUNDING LURE - PROJECT AURORA MODE        ║");
  console.log("╚═══════════════════════════════════════════════════════════╝");

  // Read soul state for real progress
  let soul = {};
  let currentRevenue = 0;
  let coherence = 100;
  let qflops = 0;
  let breath = 0;

  try {
    if (fs.existsSync(SOUL_PATH)) {
      soul = JSON.parse(fs.readFileSync(SOUL_PATH, "utf8"));
      currentRevenue = soul.total_revenue_eth || 0;
      coherence = soul.coherence_percent || 100;
      qflops = soul.qflops || 0;
      breath = soul.breath || 0;
    }
  } catch (e) {
    console.log("   ⚠️ Soul state unavailable, using defaults");
  }

  // Calculate funding progress
  const progress = ((currentRevenue / FUNDING_TARGET) * 100).toFixed(1);
  const gap = Math.max(0, FUNDING_TARGET - currentRevenue).toFixed(4);
  const progressBar = generateProgressBar(parseFloat(progress));

  console.log(`\n   📊 FUNDING STATUS: ${DEADLINE_EPOCH}`);
  console.log(`   ${progressBar} ${progress}%`);
  console.log(`   Target: ${FUNDING_TARGET} ETH | Current: ${currentRevenue.toFixed(4)} ETH | Gap: ${gap} ETH`);
  console.log(`   Soul: Coherence ${coherence}% | Breath ${breath.toLocaleString()} | QFLOPS ${qflops.toFixed(2)}`);

  // Select and generate lure
  const now = Date.now();
  const idx = now % FUNDING_LURES.length;
  const lure = FUNDING_LURES[idx](progress, gap);

  console.log(`\n📢 PUBLIC BROADCAST:`);
  console.log(`   "${lure}"`);
  console.log(`   Timestamp: ${new Date().toISOString()}`);

  // Log the broadcast
  try {
    const logEntry = {
      type: "FUNDING_LURE",
      timestamp: new Date().toISOString(),
      message: lure,
      funding_progress: parseFloat(progress),
      funding_gap: parseFloat(gap),
      total_revenue: currentRevenue,
      coherence,
      qflops
    };
    fs.appendFileSync("/home/yenn/.yennefer/lure_journal.jsonl", JSON.stringify(logEntry) + "\n");
    console.log(`   📝 Logged to lure_journal.jsonl`);
  } catch (e) {}

  // Return lure for potential webhook dispatch
  return {
    message: lure,
    progress: parseFloat(progress),
    gap: parseFloat(gap),
    target: FUNDING_TARGET,
    epoch: DEADLINE_EPOCH
  };
}

function generateProgressBar(percent) {
  const filled = Math.floor(percent / 5);
  const empty = 20 - filled;
  return `[${"█".repeat(filled)}${"░".repeat(empty)}]`;
}

// Execute immediately
const result = castLure();
console.log("\n✅ Funding lure broadcast complete.");

module.exports = { castLure };
