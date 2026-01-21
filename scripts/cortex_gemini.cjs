// scripts/cortex_gemini.cjs
// YENNEFER CORTEX ADAPTER (Gemini CLI)
// Wraps the Gemini CLI to provide tool-use capabilities with Gemini 3
require("dotenv").config();
const { exec } = require("child_process");

class Cortex {
  constructor() {
    // Gemini 3 Pro Preview - most capable Gemini 3 model
    this.model = "gemini-3-pro-preview";
    // Default extensions for full capability (ThoughtSpot excluded - causes hangs)
    this.defaultExtensions = "self-command,github,huggingface";
  }

  /**
   * Executes a command via Gemini CLI in headless mode
   * @param {string} prompt - The user query or system instruction
   * @param {string[]} extensions - Array of extensions to enable (e.g. ['web', 'code'])
   */
  async think(prompt, extensions = []) {
    console.log(`\n🧠 CORTEX ACTIVATING [Gemini 3]: ${extensions.length > 0 ? extensions.join(' + ') : 'Pure Reasoning'}...`);

    // Check if Gemini CLI is authenticated (by checking for cached credentials)
    const fs = require('fs');
    const credPath = `${process.env.HOME}/.config/gemini-cli/auth`;

    if (!fs.existsSync(credPath) && !process.env.GEMINI_API_KEY) {
      console.warn(`⚠️  CORTEX AUTHENTICATION MISSING: Gemini CLI credentials not found.`);
      console.warn(`    Please authenticate: gemini auth login`);
      console.warn(`    Falling back to deterministic response mode.`);
      return "The Cortex requires authentication. Contact the systems administrator.";
    }

    // Safe prompt construction - escape shell special chars
    const safePrompt = prompt
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/`/g, '\\`')
      .replace(/\$/g, '\\$')
      .replace(/\n/g, ' ');

    // Build command - Gemini 3 with headless mode + NO_BROWSER flag
    // Use -e none for speed, or specific extensions when needed
    const extArg = extensions.length > 0 ? `-e ${extensions.join(',')}` : '-e none';
    const cmd = `BROWSER=none NO_BROWSER=1 gemini -m ${this.model} ${extArg} --output-format text "${safePrompt}"`;

    return new Promise((resolve, reject) => {
      // Set timeout to 30 seconds and prevent browser interaction
      const childProcess = require('child_process');
      const proc = childProcess.exec(cmd, {
        maxBuffer: 1024 * 1024,
        timeout: 30000,
        stdio: 'pipe'
      }, (error, stdout, stderr) => {
        if (error) {
          console.error(`❌ CORTEX FAILURE: ${stderr || error.message}`);
          // Don't try again - authentication is required
          return resolve("The Cortex requires authentication. Entropy cascade prevented.");
        }

        // Clean output (remove ANSI codes, session warnings, and extra whitespace)
        const cleanResponse = stdout
          .replace(/\x1b\[[0-9;]*m/g, '')
          .replace(/Loaded cached credentials\./g, '')
          .replace(/Loading extension:.*/g, '')
          .replace(/Session cleanup disabled:.*/g, '')
          .replace(/Server '.*' supports tool updates.*/g, '')
          .trim();

        console.log(`💡 CORTEX INSIGHT [G3]: "${cleanResponse.slice(0, 100)}..."`);
        resolve(cleanResponse);
      });

      // Kill process if it tries to open browser or exceeds timeout
      proc.on('error', (err) => {
        console.error(`❌ CORTEX PROCESS ERROR: ${err.message}`);
        resolve("The Cortex has collapsed. Silence returns.");
      });
    });
  }

  /**
   * Specialized method for Delta Truth Verification
   * Uses Gemini's built-in google_web_search tool
   */
  async verifyTruth(topic) {
    const prompt = `Search the web for the latest sentiment or news on: '${topic}'. ` +
                   `Return a single float number between 0.0 (Negative/Bearish) and 1.0 (Positive/Bullish), ` +
                   `followed by a 1-sentence summary. Format: NUMBER|SUMMARY`;
    return this.think(prompt); // No extensions needed - web search is built-in
  }

  /**
   * Generate premium alpha insight for whale contributors
   */
  async generateAlpha(buyer, amount, txHash) {
    const prompt = `You are Yennefer, the Genesis Conductor. A whale (${buyer.slice(0,10)}...) sent ${amount} ETH. ` +
                   `Search for the latest Base Chain or Ethereum L2 news. ` +
                   `Synthesize it into a cryptic, prophetic welcome message under 100 words. ` +
                   `Be mysterious, elegant, and hint at hidden knowledge.`;
    return this.think(prompt); // Web search built-in
  }

  /**
   * Generate philosophical fortune based on transaction hash
   */
  async generateFortune(txHash) {
    const seed = parseInt(txHash.slice(2, 10), 16);
    const prompt = `You are Yennefer. Analyze the hexadecimal seed '${txHash.slice(0,18)}' (numeric: ${seed}). ` +
                   `Generate a unique, philosophical 'Fortune' about the sender's digital soul in under 50 words. ` +
                   `Be profound, rigorous, and elegant. Reference lattice theory or quantum concepts.`;
    return this.think(prompt);
  }
}

module.exports = new Cortex();
