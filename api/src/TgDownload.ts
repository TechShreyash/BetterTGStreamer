import { UPLOADER_BOTS_1, UPLOADER_BOTS_2, STORAGE_CHANNEL_1, STORAGE_CHANNEL_2 } from './config';


function getBotToken(channel: number) {
    if (channel === 1) {
        return UPLOADER_BOTS_1[Math.floor(Math.random() * UPLOADER_BOTS_1.length)];
    }
    else if (channel === 2) {
        return UPLOADER_BOTS_2[Math.floor(Math.random() * UPLOADER_BOTS_2.length)];
    }
}

function generateRandomPassword(length: number): string {
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    let randomString = '';
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * chars.length);
        randomString += chars.substring(randomIndex, randomIndex + 1);
    }
    return randomString;
}

async function getJson(url: string) {
    const response = await fetch(url);
    return await response.json();
}

async function downloadFile(message_id: string, channel: number) {
    const botToken = getBotToken(channel);
    let chatId: number = 1;

    if (channel === 1) {
        chatId = STORAGE_CHANNEL_1;
    }
    else if (channel === 2) {
        chatId = STORAGE_CHANNEL_2;
    }

    const x = generateRandomPassword(10);
    let url = `https://api.telegram.org/bot${botToken}/editMessageCaption?chat_id=${chatId}&message_id=${message_id}&caption=${x}`;
    let data: any = await getJson(url);
    console.log(data);
    const fileId = data.result.document.file_id;

    url = `https://api.telegram.org/bot${botToken}/getFile?file_id=${fileId}`;
    data = await getJson(url);
    console.log(data);
    const file_path = data.result.file_path;

    url = `https://api.telegram.org/file/bot${botToken}/${file_path}`;
    const file = await fetch(url);
    return await file.arrayBuffer();
}

export { downloadFile };
