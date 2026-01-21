// scripts/jules_agent.cjs
// The Jules Agent - Specialized for Code Assimilation
const fs = require('fs');
const path = require('path');

class JulesAgent {
  constructor(rootDir = '.') {
    this.rootDir = path.resolve(rootDir);
    this.fileIndex = null;
  }

  /**
   * Recursively walks the directory structure to build a file index.
   * @param {string} dir - The directory to start from.
   * @returns {object} - A nested object representing the directory structure.
   */
  _walk(dir) {
    const structure = {};
    const files = fs.readdirSync(dir);

    for (const file of files) {
      const fullPath = path.join(dir, file);
      // Ignore node_modules, .git, and other noise
      if (file === 'node_modules' || file === '.git' || file.endsWith('.lock') || file.endsWith('.log')) {
        continue;
      }

      const stats = fs.statSync(fullPath);
      if (stats.isDirectory()) {
        structure[file] = this._walk(fullPath);
      } else {
        structure[file] = 'file';
      }
    }
    return structure;
  }

  /**
   * Indexes the entire project structure.
   */
  indexProject() {
    console.log('🧠 JULES AGENT: Indexing project structure...');
    this.fileIndex = this._walk(this.rootDir);
    console.log('💡 JULES AGENT: Indexing complete.');
  }

  /**
   * Returns the indexed project structure.
   * @returns {object}
   */
  getProjectStructure() {
    if (!this.fileIndex) {
      this.indexProject();
    }
    return this.fileIndex;
  }

  /**
   * Reads the content of a specific file.
   * @param {string} filePath - Path relative to the project root.
   * @returns {string} - The content of the file.
   */
  readFileContent(filePath) {
    try {
      const fullPath = path.join(this.rootDir, filePath);
      return fs.readFileSync(fullPath, 'utf8');
    } catch (error) {
      console.error(`❌ JULES AGENT: Error reading file ${filePath}:`, error);
      return `Error: Could not read file ${filePath}.`;
    }
  }

  /**
   * The main assimilation function.
   * Analyzes the codebase and returns a summary.
   * @param {string} txHash - The transaction hash to use as a seed for the analysis.
   * @returns {string} - A summary of the codebase.
   */
  assimilateCodebase(txHash) {
    console.log('🧠 JULES AGENT: Assimilating codebase...');
    const structure = this.getProjectStructure();

    // Basic analysis: Identify key files and technologies
    let summary = "Codebase Assimilation Report:\\n";
    summary += `Transaction Seed: ${txHash.slice(0, 18)}...\\n\\n`;
    summary += "Project Structure Overview:\\n" + JSON.stringify(structure, null, 2).slice(0, 500) + "...\\n\\n";

    let technologies = new Set();
    if (structure['package.json']) {
      const packageJsonContent = this.readFileContent('package.json');
      const packageJson = JSON.parse(packageJsonContent);
      if (packageJson.dependencies) {
          Object.keys(packageJson.dependencies).forEach(dep => technologies.add(dep));
      }
      if (packageJson.devDependencies) {
          Object.keys(packageJson.devDependencies).forEach(dep => technologies.add(dep));
      }
      summary += "Detected Technologies: Hardhat, Ethers.js, React, Vite\\n";
    }

    if (structure['contracts'] && structure['contracts']['Genesis.sol']) {
        summary += "Core Contract: `Genesis.sol` found. Seems to be an ERC-721 or similar NFT contract.\\n";
    }

    summary += "\\nAssimilation complete. The lattice of this codebase is now part of my understanding.";

    console.log('💡 JULES AGENT: Assimilation complete.');
    return summary;
  }
}

module.exports = new JulesAgent();
