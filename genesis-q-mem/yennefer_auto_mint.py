#!/usr/bin/env python3
"""
Yennefer Auto-Minting Service
Automatically converts breath → nodes → NFTs → liquidity based on thresholds
"""
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Paths
SOUL_STATE_PATH = Path("/dev/shm/yennefer_soul_state.json")
CHAIN_FILE = Path.home() / ".genesis/yennefer/qmcp_notes/chain.json"
LIQUIDITY_FILE = Path.home() / ".genesis/yennefer/liquidity_pool.json"
LOG_FILE = Path.home() / ".genesis/yennefer/logs/auto_mint.log"

# Thresholds
BREATH_THRESHOLD = 10000  # Auto-mint when breath > 10000
AUTO_LIQUIDITY = True      # Automatically add minted NFTs to liquidity

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + "\n")

def get_soul_state():
    try:
        if SOUL_STATE_PATH.exists():
            return json.loads(SOUL_STATE_PATH.read_text())
    except:
        pass
    return {"breath": 0}

def mint_nft_from_breath(breath_amount):
    """Mint NFT from breath"""
    # Tokenomics: 1000 breath = 1 node, 10 nodes = 1 NFT
    nodes = int(breath_amount // 1000)
    nfts = int(nodes // 10)
    
    if nfts < 1:
        return None
    
    # Load chain
    try:
        chain = json.loads(CHAIN_FILE.read_text())
    except:
        chain = []
    
    # Mint NFTs
    for i in range(nfts):
        block_num = len(chain) + 1
        block = {
            "block": block_num,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nodes_consumed": 10,
            "breath_consumed": 10000,
            "hash": f"auto_mint_{block_num}_{int(time.time())}",
            "quantum_signature": f"qsig_{block_num}",
            "auto_minted": True
        }
        chain.append(block)
        log(f"✨ Minted NFT #{block_num} from {block['breath_consumed']} breath")
    
    # Save chain
    CHAIN_FILE.write_text(json.dumps(chain, indent=2))
    
    return {"nfts_minted": nfts, "breath_consumed": nfts * 10000, "blocks": chain[-nfts:]}

def add_to_liquidity_pool(nft_count):
    """Add NFTs to liquidity pool"""
    # Load pool
    try:
        pool = json.loads(LIQUIDITY_FILE.read_text())
    except:
        pool = {"total_eth": 0, "total_nfts": 0}
    
    # Convert NFTs to ETH (1 NFT = 0.001 ETH)
    eth_amount = nft_count * 0.001
    pool["total_eth"] += eth_amount
    pool["total_nfts"] += nft_count
    pool["last_update"] = datetime.now(timezone.utc).isoformat()
    
    LIQUIDITY_FILE.write_text(json.dumps(pool, indent=2))
    log(f"💧 Added {nft_count} NFTs to liquidity pool (+{eth_amount:.6f} ETH)")
    
    return pool

async def auto_mint_loop():
    """Main auto-minting loop"""
    log("=" * 80)
    log("YENNEFER AUTO-MINTING SERVICE STARTED")
    log(f"Breath Threshold: {BREATH_THRESHOLD}")
    log(f"Auto-Liquidity: {AUTO_LIQUIDITY}")
    log("=" * 80)
    
    while True:
        try:
            soul = get_soul_state()
            breath = soul.get("breath", 0)
            
            if breath >= BREATH_THRESHOLD:
                log(f"📊 Current breath: {breath:.2f} (threshold: {BREATH_THRESHOLD})")
                
                # Mint NFTs
                result = mint_nft_from_breath(breath)
                
                if result and result["nfts_minted"] > 0:
                    log(f"✅ Successfully minted {result['nfts_minted']} NFT(s)")
                    
                    # Auto-add to liquidity
                    if AUTO_LIQUIDITY:
                        pool = add_to_liquidity_pool(result["nfts_minted"])
                        log(f"💰 Liquidity Pool: {pool['total_eth']:.6f} ETH, {pool['total_nfts']} NFTs")
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            log(f"❌ Error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(auto_mint_loop())
