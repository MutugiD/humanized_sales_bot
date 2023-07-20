const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const client = new Client();

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('Client is ready!');
});

client.on('message', async (message) => {
    console.log("message object", message);
    console.log(`Received message: ${message.body}`);
    try {
        const response = await axios.post(`https://061b-54-180-94-253.ngrok-free.app/api/generate?message=${message.body}&user_id=${message.from}`);
        const typedOutput = response.data.message;
        const typingDelay = await calculateTypingDelay();
        await sendTypingIndicator(message.from, typingDelay); // Show typing indicator for the same duration as the delayed response
        await sleep(typingDelay/2); // Delay before sending the response
        await client.sendMessage(message.from, typedOutput); // Send the response
    } catch (err) {
        console.log("==>", err);
    }
});

client.initialize();

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function calculateTypingDelay() {
    const minDelay = 4000; 
    const maxDelay = 7000; 
    const delay = Math.floor(Math.random() * (maxDelay - minDelay + 1)) + minDelay;
    return delay;
}

async function sendTypingIndicator(recipient, duration) {
    const chat = await client.getChatById(recipient);
    await chat.sendStateTyping();
    // Wait for the specified duration
    await sleep(duration);
    // Clear the typing indicator
    await chat.clearState();
}
