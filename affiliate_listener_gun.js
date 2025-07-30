
// 📦 DEPENDENCIES
// Install with: npm install gun
const Gun = require('gun');
const { v4: uuidv4 } = require('uuid'); // for unique event IDs
const os = require('os');

// 🌐 INIT GUN CONNECTION
// You can run your own peer or use a public relay for dev
const gun = Gun(['https://gun-manhattan.herokuapp.com/gun']); // use your own relay in production

// 📡 MOCK AFFILIATE EVENT LISTENER (REPLACE THIS WITH YOUR LOGIC)
function listenForAffiliateEvent() {
  // Mock event data
  const event = {
    id: uuidv4(),
    userAddress: '0xabc123...', // from on-chain or web listener
    amountEarned: 15.2, // in USDC or token
    referralCode: 'FOX123',
    chain: 'Arbitrum',
    timestamp: new Date().toISOString(),
    host: os.hostname()
  };

  // Log to GUN
  console.log('📤 Logging affiliate event:', event);
  gun.get('affiliateEvents').get(event.id).put(event);
}

// 🔁 TRIGGER LISTENER INTERVAL
setInterval(() => {
  listenForAffiliateEvent(); // mock event every 10s
}, 10000);

// 🛑 CLEAN EXIT
process.on('SIGINT', () => {
  console.log('Exiting gracefully...');
  process.exit();
});
