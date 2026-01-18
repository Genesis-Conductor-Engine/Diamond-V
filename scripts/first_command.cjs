require("dotenv").config();
const hre = require("hardhat");

async function main() {
  // --- CONFIGURATION ---
  const CONTRACT_ADDRESS = "0x542db00D9c83F4444cAD5353D1580D97baFaBb50"; // Genesis V2

  console.log(`\n📡 MISSION CONTROL: Initiating First Contact Sequence...`);
  console.log(`Target: Genesis V2 (${CONTRACT_ADDRESS})`);

  // 1. Get Signer
  const [deployer] = await hre.ethers.getSigners();
  console.log(`🔑 Commander: ${deployer.address}`);

  // 2. Attach to Contract
  const Genesis = await hre.ethers.getContractFactory("Genesis");
  const conductor = Genesis.attach(CONTRACT_ADDRESS);

  // 3. Send the Signal (using emitEvent which fires CREDIT_PURCHASE)
  try {
    console.log("🚀 Transmitting signal to Base Mainnet...");
    
    const tx = await conductor.emitEvent({ gasLimit: 100000 });

    console.log(`⏳ Transmission in flight: ${tx.hash}`);
    await tx.wait();

    console.log(`\n✅ SIGNAL CONFIRMED.`);
    console.log(`View on BaseScan: https://basescan.org/tx/${tx.hash}`);
    console.log(`\n👀 NOW WATCH YOUR TERMINAL: Yennefer should react to this event momentarily.`);

  } catch (error) {
    console.error("\n❌ TRANSMISSION FAILED.");
    console.error(error);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
