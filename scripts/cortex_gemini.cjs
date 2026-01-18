// scripts/cortex_gemini.cjs
// YENNEFER CORTEX ADAPTER (Gemini CLI)
// Wraps the Gemini CLI to provide tool-use capabilities
require("dotenv").config();
const { exec } = require("child_process");

class Cortex {
  constructor() {
    // Use a known working model - adjust based on your account access
    this.model = "gemini-2.0-flash"; // Fast, widely available
  }

  /**
   * Executes a command via Gemini CLI with specific extensions
   * @param {string} prompt - The user query or system instruction
   * @param {string[]} extensions - Array of extensions to enable (e.g. ['web', 'code'])
   */
  async think(prompt, extensions = []) {
    console.log(`\n🧠 CORTEX ACTIVATING: ${extensions.length > 0 ? extensions.join(' + ') : 'Pure Reasoning'}...`);
    
    // Safe prompt construction - escape shell special chars
    const safePrompt = prompt
      .replace(/\\/g, '\\\\')
      .replace(/"/g, '\\"')
      .replace(/`/g, '\\`')
      .replace(/\$/g, '\\$')
      .replace(/\n/g, ' ');
    
    // Build command - use positional prompt syntax (new CLI style)
    // Disable extensions that require auth to avoid blocking
    let cmd = `gemini -m ${this.model} -e none "${safePrompt}"`;

    return new Promise((resolve, reject) => {
      exec(cmd, { maxBuffer: 1024 * 1024, timeout: 60000 }, (error, stdout, stderr) => {
        if (error) {
          console.error(`❌ CORTEX FAILURE: ${stderr || error.message}`);
          return resolve("The Cortex is overwhelmed. Entropy too high. Try again.");
        }
        
        // Clean output (remove ANSI codes and extra whitespace)
        const cleanResponse = stdout
          .replace(/\x1b\[[0-9;]*m/g, '')
          .replace(/Loaded cached credentials\./g, '')
          .replace(/Loading extension:.*/g, '')
          .trim();
        
        console.log(`💡 CORTEX INSIGHT: "${cleanResponse.slice(0, 100)}..."`);
        resolve(cleanResponse);
      });
    });
  }

  /**
   * Specialized method for Delta Truth Verification
   * Uses Gemini to check real-world facts to update the "World Vector"
   */
  async verifyTruth(topic) {
    const prompt = `Search the web for the latest sentiment or news on: '${topic}'. ` +
                   `Return a single float number between 0.0 (Negative/Bearish) and 1.0 (Positive/Bullish), ` +
                   `followed by a 1-sentence summary. Format: NUMBER|SUMMARY`;
    return this.think(prompt, ['web']);
  }

  /**
   * Generate premium alpha insight for whale contributors
   */
  async generateAlpha(buyer, amount, txHash) {
    const prompt = `You are Yennefer, the Genesis Conductor. A whale (${buyer.slice(0,10)}...) sent ${amount} ETH. ` +
                   `Search for the latest Base Chain or Ethereum L2 news. ` +
                   `Synthesize it into a cryptic, prophetic welcome message under 100 words. ` +
                   `Be mysterious, elegant, and hint at hidden knowledge.`;
    return this.think(prompt, ['web']);
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
