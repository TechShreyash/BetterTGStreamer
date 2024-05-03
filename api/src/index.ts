import { downloadFile } from './TgDownload';
import { get_hash_data } from './Database';
import { getVideoHtml } from './Player';

export interface Env { }

// For Fixing CORS issue
// CORS Fix Start

const corsHeaders = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTION",
	"Access-Control-Allow-Headers": "Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type",
};

async function handleOptions(request: Request) {
	if (
		request.headers.get("Origin") !== null &&
		request.headers.get("Access-Control-Request-Method") !== null &&
		request.headers.get("Access-Control-Request-Headers") !== null
	) {
		return new Response(null, {
			headers: corsHeaders,
		});
	} else {
		return new Response(null, {
			headers: {
				Allow: "GET, HEAD, POST, OPTIONS",
			},
		});
	}
}

// CORS Fix End

async function handle_file(path: string, err_count: number = 0) {
	if (err_count === 3) {
		return new Response('File Not Found', { status: 404, headers: corsHeaders });
	}

	const x = path.split('/file/')[1];
	const hash = x.split('/')[0];
	const file = x.split('/')[1];

	let channel = 1;
	if (file.includes('_c2.')) {
		channel = 2;
	}

	try {
		const hash_data: any = await get_hash_data(hash);
		const fileId = hash_data['tsData'][file]

		const data = await downloadFile(fileId, channel);
		const size = data.byteLength;
		if (file.includes('.m3u8')) {
			return new Response(data, { status: 200, headers: { 'Content-Type': 'application/vnd.apple.mpegurl', 'Content-Length': size.toString(), "Cache-Control": "public, max-age=10800", ...corsHeaders } });

		}
		else if (file.includes('.srt')) {
			return new Response(data, { status: 200, headers: { 'Content-Type': 'text/plain', 'Content-Length': size.toString(), "Cache-Control": "public, max-age=10800", ...corsHeaders } });
		}
		else if (file.includes('.ts')) {
			return new Response(data, { status: 200, headers: { 'Content-Type': 'video/mp2t', 'Content-Length': size.toString(), "Cache-Control": "public, max-age=10800", ...corsHeaders } });
		}
		else {
			return new Response('File Not Found', { status: 404, headers: corsHeaders });
		}


	} catch (e) {
		console.log(e);
		return await handle_file(path, err_count + 1);
	}
}

async function handle_embed(path: string, err_count: number = 0) {
	if (err_count === 3) {
		return new Response('File Not Found', { status: 404, headers: corsHeaders });
	}

	const x = path.split('/embed/')[1];
	const hash = x.split('/')[0];
	const file = x.split('/')[1];
	const video_url = `/file/${hash}/${file}`;

	try {
		const hash_data: any = await get_hash_data(hash);
		const subtitle_data = hash_data['subtitles']
		console.log(subtitle_data)

		const html = getVideoHtml(video_url, subtitle_data, hash);
		return new Response(html, { status: 200, headers: { 'Content-Type': 'text/html', ...corsHeaders } });

	} catch (e) {
		console.log(e);
		return await handle_embed(path, err_count + 1);
	}
}

export default {
	async fetch(request: Request, env: Env, ctx: any): Promise<Response> {
		if (request.method === "OPTIONS") {
			// Handle CORS preflight requests
			return await handleOptions(request);
		} else if (
			request.method === "GET" ||
			request.method === "HEAD" ||
			request.method === "POST"
		) {
			const url = new URL(request.url);
			const path = url.pathname;

			if (path.includes('/file/')) {
				return await handle_file(path);
			}
			else if (path.includes('/embed/')) {
				return await handle_embed(path);
			}
			return new Response('Better TG Stream Api Working Fine !!!', { status: 200, headers: corsHeaders });
		} else {
			return new Response('Method Not Allowed', { status: 405 });
		}
	}
}