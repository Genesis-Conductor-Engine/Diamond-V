/**
 * QFLOP Mining Daemon
 * 
 * Self-funding system that:
 * 1. Dispatches Dual Bridge compute jobs to generate QFLOPS
 * 2. Mints QFLOP tokens based on accumulated work
 * 3. Transfers minted tokens to MPC Vault
 * 4. Monitors gas levels and bridge status
 */

const { ethers } = require('ethers');
const { execSync, spawn } = require('child_process');
const fs = require('fs');
require('dotenv').config();

// Configuration
const CONFIG = {
    QFLOP_CONTRACT: '0xa8F5e136aa74803B8DB377a14f79F6c8Dd3959c7',
    MPC_VAULT: '0x029472221aBa41446821777136eB82Ad171D04e6',
    LEGACY_MINTER: '0x9545e2439c5c75d3aA723AcaC1AA6B0fa1DB6956',
    GITHUB_REPO: 'Genesis-Conductor-Engine/Yennefer',
    MIN_GAS_ETH: 0.0001,
    MINT_THRESHOLD_QFLOPS: 1000000,  // 1M QFLOPS to trigger mint
    DISPATCH_INTERVAL_MS: 5 * 60 * 1000,  // 5 minutes
    STATUS_INTERVAL_MS: 30 * 1000,  // 30 seconds
};

// QFLOP Token ABI (minimal)
const QFLOP_ABI = [
    'function mint(address to, uint256 amount) external',
    'function balanceOf(address) view returns (uint256)',
    'function transfer(address to, uint256 amount) returns (bool)',
    'function totalSupply() view returns (uint256)'
];

class QFLOPMiningDaemon {
    constructor() {
        this.provider = new ethers.JsonRpcProvider(process.env.BASE_MAINNET_RPC);
        this.wallet = new ethers.Wallet(process.env.ETH_PRIVATE_KEY, this.provider);
        this.qflop = new ethers.Contract(CONFIG.QFLOP_CONTRACT, QFLOP_ABI, this.wallet);
        this.lastDispatch = 0;
        this.accumulatedQflops = 0;
        this.minted = 0n;
    }
    
    async getGasBalance() {
        const bal = await this.provider.getBalance(CONFIG.LEGACY_MINTER);
        return parseFloat(ethers.formatEther(bal));
    }
    
    async getQflopBalance() {
        const bal = await this.qflop.balanceOf(CONFIG.LEGACY_MINTER);
        return parseFloat(ethers.formatEther(bal));
    }
    
    async dispatchDualBridge() {
        console.log('🚀 Dispatching Dual Bridge job...');
        try {
            execSync(`gh workflow run qflop-dual-bridge.yml --repo ${CONFIG.GITHUB_REPO} -f duration_minutes=5 -f power_mode=maxpower`, {
                stdio: 'inherit'
            });
            this.lastDispatch = Date.now();
            return true;
        } catch (e) {
            console.error('❌ Dispatch failed:', e.message);
            return false;
        }
    }
    
    async checkDualBridgeResults() {
        try {
            const result = execSync(`gh run list --workflow qflop-dual-bridge.yml --repo ${CONFIG.GITHUB_REPO} --limit 1 --json conclusion,databaseId -q '.[0]'`, {
                encoding: 'utf-8'
            });
            const run = JSON.parse(result);
            
            if (run.conclusion === 'success') {
                // Fetch logs to extract QFLOPS generated
                const logs = execSync(`gh run view ${run.databaseId} --repo ${CONFIG.GITHUB_REPO} --log 2>/dev/null | grep -i "qflops\\|tflops" | tail -5`, {
                    encoding: 'utf-8'
                });
                
                // Parse QFLOPS from logs
                const match = logs.match(/(\d+(?:,\d+)*)\s*QFLOPS/i);
                if (match) {
                    const qflops = parseInt(match[1].replace(/,/g, ''));
                    this.accumulatedQflops += qflops;
                    console.log(`   ✅ Run ${run.databaseId}: +${qflops.toLocaleString()} QFLOPS`);
                }
            }
        } catch (e) {
            // Ignore errors
        }
    }
    
    async mintQflop() {
        if (this.accumulatedQflops < CONFIG.MINT_THRESHOLD_QFLOPS) {
            console.log(`   ⏳ Not enough QFLOPS to mint (${this.accumulatedQflops.toLocaleString()} / ${CONFIG.MINT_THRESHOLD_QFLOPS.toLocaleString()})`);
            return false;
        }
        
        const gas = await this.getGasBalance();
        if (gas < CONFIG.MIN_GAS_ETH) {
            console.log(`   ❌ Insufficient gas: ${gas} ETH`);
            return false;
        }
        
        // Mint QFLOP tokens (1:1000 ratio: 1000 QFLOPS = 1 QFLOP token)
        const mintAmount = ethers.parseEther(String(Math.floor(this.accumulatedQflops / 1000)));
        
        console.log(`💎 Minting ${ethers.formatEther(mintAmount)} QFLOP tokens...`);
        
        try {
            const tx = await this.qflop.mint(CONFIG.MPC_VAULT, mintAmount, {
                gasLimit: 100000
            });
            await tx.wait();
            
            this.minted += mintAmount;
            this.accumulatedQflops = 0;
            console.log('   ✅ Minted to MPC Vault');
            return true;
        } catch (e) {
            console.log('   ❌ Mint failed:', e.reason || e.message);
            return false;
        }
    }
    
    async status() {
        const gas = await this.getGasBalance();
        const qflop = await this.getQflopBalance();
        const supply = await this.qflop.totalSupply();
        
        console.log('\n📊 QFLOP MINING DAEMON STATUS');
        console.log('═══════════════════════════════════════════════════════════════');
        console.log(new Date().toISOString());
        console.log(`   Gas Balance:      ${gas.toFixed(8)} ETH ${gas >= CONFIG.MIN_GAS_ETH ? '✅' : '❌ LOW'}`);
        console.log(`   QFLOP Balance:    ${qflop.toLocaleString()} QFLOP`);
        console.log(`   Total Supply:     ${ethers.formatEther(supply)} QFLOP`);
        console.log(`   Accumulated Work: ${this.accumulatedQflops.toLocaleString()} QFLOPS`);
        console.log(`   Minted This Run:  ${ethers.formatEther(this.minted)} QFLOP`);
        console.log('═══════════════════════════════════════════════════════════════');
        
        return { gas, qflop, ready: gas >= CONFIG.MIN_GAS_ETH };
    }
    
    async run() {
        console.log('🔷 QFLOP Mining Daemon Starting...');
        console.log(`   Contract: ${CONFIG.QFLOP_CONTRACT}`);
        console.log(`   Minter: ${CONFIG.LEGACY_MINTER}`);
        console.log(`   Target: ${CONFIG.MPC_VAULT}`);
        
        // Initial status
        const initial = await this.status();
        
        if (!initial.ready) {
            console.log('\n⏳ Waiting for ETH bridge to complete...');
            console.log('   Bridge TX: 0xc6463a1506aef7cd443652eabeb550a2a108415b2d0d5d83675f127b7ae69b66');
        }
        
        // Main loop
        while (true) {
            try {
                const { ready } = await this.status();
                
                if (ready) {
                    // Check Dual Bridge results
                    await this.checkDualBridgeResults();
                    
                    // Dispatch new job if interval passed
                    if (Date.now() - this.lastDispatch > CONFIG.DISPATCH_INTERVAL_MS) {
                        await this.dispatchDualBridge();
                    }
                    
                    // Mint if enough QFLOPS accumulated
                    await this.mintQflop();
                }
                
            } catch (e) {
                console.error('❌ Error:', e.message);
            }
            
            // Wait before next iteration
            await new Promise(r => setTimeout(r, CONFIG.STATUS_INTERVAL_MS));
        }
    }
}

// Run
const daemon = new QFLOPMiningDaemon();
daemon.run().catch(console.error);
