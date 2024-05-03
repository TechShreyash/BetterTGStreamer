import { DB_API_URL } from "./Config";

const CACHE: any = {};

async function get_hash_data(hash: string) {
    if (CACHE[hash]) return CACHE[hash];

    const url = `${DB_API_URL}/get/${hash}`;
    const response = await fetch(url);
    const data: any = await response.json();
    if (data['tsData']) {
        CACHE[hash] = data;
    }
    return data;
}

export { get_hash_data };