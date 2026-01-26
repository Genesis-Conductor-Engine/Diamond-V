const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying QFLOPTokenV2 with account:", deployer.address);
  
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "ETH");
  
  if (balance < ethers.parseEther("0.0001")) {
    console.log("⚠️ Low balance - deployment may fail");
  }
  
  // Deploy with initial supply of 267,348,000 QFLOP (matching current)
  const initialSupply = ethers.parseEther("267348000");
  const minter = deployer.address;
  
  console.log("\nDeploying QFLOPTokenV2...");
  console.log("Initial Supply:", ethers.formatEther(initialSupply), "QFLOP");
  console.log("Minter:", minter);
  
  const QFLOPTokenV2 = await ethers.getContractFactory("QFLOPTokenV2");
  const token = await QFLOPTokenV2.deploy(minter, initialSupply);
  
  await token.waitForDeployment();
  const address = await token.getAddress();
  
  console.log("\n✅ QFLOPTokenV2 deployed to:", address);
  console.log("\nVerify on BaseScan:");
  console.log(`npx hardhat verify --network baseMainnet ${address} "${minter}" "${initialSupply}"`);
  
  return address;
}

main()
  .then((address) => {
    console.log("\n🎉 Deployment complete!");
    process.exit(0);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
