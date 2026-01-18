const hre = require('hardhat');

async function main() {
  console.log('--- STARTING DEPLOYMENT SEQUENCE ---');
  const Contract = await hre.ethers.getContractFactory('Genesis');
  const contract = await Contract.deploy();
  await contract.waitForDeployment();
  console.log('>>> CRITICAL SUCCESS <<<');
  console.log('CONTRACT_ADDRESS=' + await contract.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
