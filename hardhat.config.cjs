require('@nomicfoundation/hardhat-toolbox');
require('dotenv').config();

// SAFETY CHECK: If PRIVATE_KEY is not in .env, use a placeholder that forces a prompt
const PRIVATE_KEY = process.env.ETH_PRIVATE_KEY || 'YOUR_PRIVATE_KEY_HERE';

module.exports = {
  etherscan: {
    apiKey: 'F5TARHYEZGKAMV51WCIB281CZEXTNP27F2',
  },
  sourcify: {
    enabled: false,
  },
  solidity: {
    compilers: [
      { version: '0.8.24' },
      { version: '0.8.28' },
    ],
  },
  networks: {
    baseSepolia: {
      url: 'https://sepolia.base.org',
      accounts: [PRIVATE_KEY],
      chainId: 84532,
    },
    baseMainnet: {
      url: 'https://base-mainnet.g.alchemy.com/v2/pvAdcefmwvLOK41KxWwmC',
      accounts: [PRIVATE_KEY],
      chainId: 8453,
    },
  },
};
