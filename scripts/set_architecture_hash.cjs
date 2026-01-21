require("dotenv").config();
const { ethers } = require("hardhat");

const CONTRACT_ADDRESS = process.env.GENESIS_CONTRACT_ADDRESS || "0x542db00D9c83F4444cAD5353D1580D97baFaBb50";
const ARCHITECTURE_HASH = "0x57c7d4fa921ecbae46477bd10e68e3620c8a378c2ebe46c1e18ee84ff47e8bcc";

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Setting architecture hash with the account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  const Genesis = await ethers.getContractFactory("Genesis");
  const genesis = await Genesis.attach(CONTRACT_ADDRESS);

  console.log("Setting architecture hash to:", ARCHITECTURE_HASH);
  const tx = await genesis.setArchitectureHash(ARCHITECTURE_HASH);
  await tx.wait();

  console.log("Architecture hash set successfully!");
  console.log("Transaction hash:", tx.hash);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
