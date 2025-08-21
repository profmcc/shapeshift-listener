// Test script for DeFi Data Snatcher parsing functionality
console.log('🧪 Testing DeFi Data Snatcher parsing...');

// Test the enhanced parsing function
function parseChainTokenDataEnhanced(text) {
  const result = {
    chain: '',
    address: '',
    token: '',
    amount: ''
  };
  
  // Extract chain info (could be "chain" prefix or just the address)
  const chainMatch = text.match(/chain\s+([^\s]+)/i);
  if (chainMatch) {
    result.chain = chainMatch[1];
  }
  
  // Extract address - look for various formats
  const addressPatterns = [
    /(0x[a-fA-F0-9]{40})/, // Full address
    /(0x[a-fA-F0-9]{6,}?\.{3}[a-fA-F0-9]{6,})/, // Abbreviated address
    /([A-Za-z0-9]{20,})/, // Non-hex long addresses
    /(0x[a-fA-F0-9]{6,})/ // Short hex addresses
  ];
  
  for (const pattern of addressPatterns) {
    const match = text.match(pattern);
    if (match) {
      result.address = match[1];
      break;
    }
  }
  
  // Extract token amount and symbol with better pattern matching
  const tokenPatterns = [
    /(\d+(?:\.\d+)?)\s+([A-Z]{2,})/, // Standard: 0.1305 WETH
    /(\d+(?:\.\d+)?)\s*([A-Z]{2,})/, // No space: 0.1305WETH
    /([A-Z]{2,})\s+(\d+(?:\.\d+)?)/, // Reversed: WETH 0.1305
    /(\d+(?:\.\d+)?)\s*([A-Z]{3,})/, // Longer symbols: 0.1305 USDC
  ];
  
  for (const pattern of tokenPatterns) {
    const match = text.match(pattern);
    if (match) {
      result.amount = match[1];
      result.token = match[2];
      break;
    }
  }
  
  return result;
}

// Test cases
const testCases = [
  "chain 0xd57f...e1c9f token 0.1305 WETH",
  "chain 0xc510...b4089 token 0.713 BNB",
  "chain 0x7d12...42f7f token 0 MAPO",
  "chain 0xab50...1a483 token 998.4699 USDC",
  "chain 0xc494...9a801 token 54.5389 POL",
  "chain 0x30b7...0c59f token 0.275 BNB",
  "chain 0xf30d...3681d token 0.05 ETH",
  "chain 0xa7f5...b6fb3 token 0.058 ETH",
  "chain 97iSGS...89K7R token 6.4155 HYPE",
  "chain 3wkdLC...7C4Uf token 50000 ZBCN",
  "chain 0x6483...ad6b3 token 531049.7414 WHITE"
];

console.log('\n📊 Testing Enhanced Parsing:');
console.log('=============================');

testCases.forEach((testCase, index) => {
  const result = parseChainTokenDataEnhanced(testCase);
  console.log(`\nTest ${index + 1}: "${testCase}"`);
  console.log(`  Chain: ${result.chain || 'N/A'}`);
  console.log(`  Address: ${result.address || 'N/A'}`);
  console.log(`  Amount: ${result.amount || 'N/A'}`);
  console.log(`  Token: ${result.token || 'N/A'}`);
});

// Test edge cases
console.log('\n🔍 Testing Edge Cases:');
console.log('======================');

const edgeCases = [
  "0.1305WETH", // No space
  "WETH 0.1305", // Reversed
  "0.1305 USDC", // Longer symbol
  "chain 0x1234567890abcdef1234567890abcdef12345678", // Full address
  "token 1.5 BTC", // Just token info
  "0xabcd...1234", // Short abbreviated
  "chain MAP Protocol", // Non-address chain
];

edgeCases.forEach((testCase, index) => {
  const result = parseChainTokenDataEnhanced(testCase);
  console.log(`\nEdge Case ${index + 1}: "${testCase}"`);
  console.log(`  Chain: ${result.chain || 'N/A'}`);
  console.log(`  Address: ${result.address || 'N/A'}`);
  console.log(`  Amount: ${result.amount || 'N/A'}`);
  console.log(`  Token: ${result.token || 'N/A'}`);
});

console.log('\n✅ Parsing tests complete!');

