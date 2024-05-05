import asyncio, threading, json, os, aiohttp, re
from config import PLAYERX_API_KEY, PLAYERX_EMAIL, PLAYERX_PASSWORD
from utils.jsRunner import evaluate_js
from pyrogram.types import Message
from utils.Logger import Logger
from utils.jsRunner import evaluate_js
from bs4 import BeautifulSoup
from pathlib import Path
from io import BufferedReader
from urllib.parse import quote
from bs4 import BeautifulSoup as bs
from playwright.async_api import async_playwright

logger = Logger(__name__)

DECODE_PASSWORD = ""
COOKIES = ""
USERAGENT = ""
PLAYERX_DATA = {}


async def old_playerxstream_updater():
    global PLAYERX_DATA

    async with aiohttp.ClientSession() as session:
        try:
            for slug in PLAYERX_DATA:
                status = PLAYERX_DATA[slug]["status"]

                if (status != "ACTIVE") and (status != "ERROR"):
                    video_url = "https://vectorx.top/v/" + slug

                    async with session.get(video_url) as response:
                        data = (await response.text()).lower()

                    if "video is not ready" in data:
                        pattern = r"\b(\d+)%\b"
                        match = re.search(pattern, data)
                        if match:
                            percentage = match.group(1)
                            PLAYERX_DATA[slug]["progress"] = f"{percentage}%"
                            PLAYERX_DATA[slug]["status"] = "PROCESSING"
                        else:
                            PLAYERX_DATA[slug]["progress"] = "0%"
                            PLAYERX_DATA[slug]["status"] = "PROCESSING"
        except Exception as e:
            logger.error(e)


async def playerxstream_updater():
    global COOKIES, USERAGENT, PLAYERX_DATA

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        logger.info("Attempting To Login")
        await page.goto("https://www.playerx.stream/panel/login/", timeout=60000)
        USERAGENT = await page.evaluate("navigator.userAgent")
        await page.fill("input[name='jc_email']", PLAYERX_EMAIL)
        await page.fill("input[name='jc_password']", PLAYERX_PASSWORD)
        await page.click("text=LOGIN")

        # wait for page url to change
        await asyncio.sleep(10)
        logger.info("Logged In")

        # get cookies
        cookies = await page.context.cookies()
        text = ""
        for cookie in cookies:
            if cookie["name"] in ["PHPSESSID", "TADA"]:
                text += f"{cookie['name']}={cookie['value']}; "
        COOKIES = text.strip(" ;")
        logger.info(f"Got Cookies: {COOKIES}")

        await context.close()

        context = await browser.new_context(java_script_enabled=False)
        page = await context.new_page()
        await context.add_cookies(cookies)

        while True:
            await asyncio.sleep(30)
            try:
                await page.goto("https://www.playerx.stream/panel/videos/")
            except Exception as e:
                logger.error(e)
                await old_playerxstream_updater()
                continue
            try:
                # get page html
                html = await page.inner_html("body")
                soup = bs(html, "html.parser")

                table = soup.find("table", {"id": "manage_video"})
                tr = table.find_all("tr")
                for i in tr[1:]:
                    try:
                        td = i.find_all("td")

                        status = td[4].text.strip()

                        x = td[5].find("span")

                        if x.get("title", ""):
                            progress = (
                                x.text.strip()
                                + " - "
                                + x.get("title", "").split("-")[0].strip()
                            )
                        else:
                            progress = x.text.strip()

                        for a in i.find_all("a"):
                            if a.get("data-slug") is not None:
                                slug = a["data-slug"]
                                break
                        PLAYERX_DATA[slug] = {"status": status, "progress": progress}
                    except Exception as e:
                        continue
            except Exception as e:
                logger.error(e)
                await old_playerxstream_updater()
                continue


# From https://stackoverflow.com/a/73728849/22334440


class ProgressFileReader(BufferedReader):
    def __init__(self, filename, read_callback, hash):
        f = open(filename, "rb")
        self.__read_callback = read_callback
        super().__init__(raw=f)
        self.length = Path(filename).stat().st_size
        self.hash = hash

    def read(self, size=None):
        calc_sz = size
        if not calc_sz:
            calc_sz = self.length - self.tell()
        if self.__read_callback:
            self.__read_callback(self.tell(), self.length, self.hash)
        return super(ProgressFileReader, self).read(size)


UPLOAD_PROGRESS = {}


def progress_callback(current, total, hash):
    global UPLOAD_PROGRESS
    UPLOAD_PROGRESS[hash] = (current, total)


class PlayerxStream:
    def __init__(self):
        self.cryptojs1 = False
        self.cryptojs2 = False

    # find CryptoJSAesJson in the js_code
    def _find_password_code(self, js_code):
        pattern = r"return [^\;]*?CryptoJSAesJson[^\;]*?;"
        code1 = re.search(pattern, js_code).group(0).strip()

        pattern = r"\(JScripts,.*?\)\);"
        code2 = re.search(pattern, code1).group(0).strip()[10:-3]

        return code1, code2

    async def _get_crypto_files(self, session: aiohttp.ClientSession):
        if not self.cryptojs1:
            if os.path.exists("cryptojs1.js"):
                with open("cryptojs1.js", "r") as f:
                    self.cryptojs1 = f.read()
            else:
                print("Downloading cryptojs1")
                async with session.get(
                    "https://vectorx.top/assets/js/crypto-js_4.2.0.min.js"
                ) as r:
                    self.cryptojs1 = await r.text()

                with open("cryptojs1.js", "w") as f:
                    f.write(self.cryptojs1)

        if not self.cryptojs2:
            if os.path.exists("cryptojs2.js"):
                with open("cryptojs2.js", "r") as f:
                    self.cryptojs2 = f.read()
            else:
                print("Downloading cryptojs2")
                async with session.get(
                    "https://vectorx.top/assets/js/cryptojs-aes-format.js"
                ) as r:
                    self.cryptojs2 = await r.text()

                with open("cryptojs2.js", "w") as f:
                    f.write(self.cryptojs2)

        return self.cryptojs1, self.cryptojs2

    async def _decrypt_js(self, cryptojs1, cryptojs2, encrypted_json, password_code):
        password = await self._get_decrypt_password(password_code)
        js_code = (
            cryptojs1
            + "\n\n"
            + cryptojs2
            + "\n\nconst "
            + encrypted_json
            + f"\n\nCryptoJSAesJson.decrypt(JScripts, '{password}')"
        )

        res_2 = await evaluate_js(js_code)
        return res_2

    async def _get_decrypt_password(self, js_code):
        global DECODE_PASSWORD
        if DECODE_PASSWORD != "":
            return DECODE_PASSWORD

        code1, code2 = self._find_password_code(js_code)
        code2 = f"return {code2}"
        js_code = js_code.replace(code1, code2)
        DECODE_PASSWORD = await evaluate_js(js_code)
        return DECODE_PASSWORD

    def _start_background_upload(self, file_path: str, hash: str):
        asyncio.run(self._background_upload(file_path, hash))

    async def _background_upload(self, file_path: str, hash: str):
        global UPLOAD_PROGRESS

        try:
            with ProgressFileReader(
                filename=file_path, read_callback=progress_callback, hash=hash
            ) as file:
                upload_payload = {
                    "api_key": PLAYERX_API_KEY,
                    "action": "upload_video",
                    "raw": "0",
                    "files[]": file,
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://www.playerx.stream/api.php", data=upload_payload
                    ) as response:
                        resp = await response.text()
                        logger.info(f"{hash} {resp}")
                        data = await response.json()

            UPLOAD_PROGRESS[hash] = ("completed", data)
        except Exception as e:
            logger.error(f"{hash} {e}")
            UPLOAD_PROGRESS[hash] = ("error", e)

    async def is_video_ready(self, session: aiohttp.ClientSession, url: str):
        global PLAYERX_DATA

        slug = url.strip(" /").split("/")[-1]
        data = PLAYERX_DATA.get(slug, None)
        if data:
            return data["status"], data["progress"]
        else:
            return "PROCESSING", "0%"

    async def upload_file(
        self, session: aiohttp.ClientSession, file_path: str, proc: Message, hash: str
    ) -> str:
        global UPLOAD_PROGRESS

        logger.info(f"Uploading File To Server {hash}")
        await asyncio.sleep(5)
        try:
            await proc.edit(
                "📤 **Uploading File to Server for Encoding...**\n\n⚠️ **Note:** This message will not update until the file is completely uploaded. Please wait patiently."
            )
        except Exception as e:
            logger.warning(f"{hash} {e}")

        await asyncio.sleep(1)

        UPLOAD_PROGRESS[hash] = (0, 0)
        threading.Thread(
            target=self._start_background_upload, args=(file_path, hash)
        ).start()
        if UPLOAD_PROGRESS[hash][0] == "error":
            raise Exception(UPLOAD_PROGRESS[hash][1])

        err_count = 0
        while UPLOAD_PROGRESS[hash][0] != "completed":
            if err_count > 15:
                raise Exception("Failed, Too many errors")

            await asyncio.sleep(10)

            try:
                current, total = UPLOAD_PROGRESS[hash]
                current = round(current / 1024 / 1024)
                total = round(total / 1024 / 1024)
                await proc.edit(
                    f"📤 **Uploading File to Server for Encoding...**\n\n🧲 **Uploaded {current} MB / {total} MB**\n\n⚠️ **Note :** If the file is too large, it may take some time to upload all files. Please be patient."
                )
            except Exception as e:
                err_count += 1
                logger.warning(f"{hash} {e}")

        data = UPLOAD_PROGRESS[hash][1]
        logger.info(f"File Uploaded To Server {hash} {data}")
        try:
            await proc.edit("📤 **File Uploaded To Encode Server Successfully**")
        except Exception as e:
            logger.warning(f"{hash} {e}")
        await asyncio.sleep(1)

        if not data.get("slug", None):
            raise Exception("Failed to upload file to server")

        logger.info(f"File Uploaded To Server Successfully {hash} {data['slug']}")
        await asyncio.sleep(5)
        return data["slug"]

    async def _raw_remote_request(
        self, session: aiohttp.ClientSession, url: str, hash: str
    ):
        global COOKIES, USERAGENT
        data = {
            "url": url,
            "form": "remote_url",
            "check_duplicate": "yes",
        }
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Cookie": COOKIES,
            "Origin": "https://www.playerx.stream",
            "Priority": "u=1, i",
            "Referer": "https://www.playerx.stream/panel/video/remote_url/",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": USERAGENT,
        }

        async with session.post(
            "https://www.playerx.stream/panel/ajax_v2/", data=data, headers=headers
        ) as response:
            data = await response.text()
            logger.info(f"{hash} {data}")
            data = json.loads(data)
        return data

    async def url_upload(
        self, session: aiohttp.ClientSession, file_url: str, proc: Message, hash: str
    ) -> str:
        logger.info(f"Adding Remote Url {hash} {file_url}")
        await asyncio.sleep(5)
        try:
            await proc.edit("📤 **Adding Remote Url For Upload...**")
        except Exception as e:
            logger.warning(f"{hash} {e}")

        await asyncio.sleep(2)

        try:
            # Using Raw Request
            data = await self._raw_remote_request(session, file_url, hash)

            if data["player"] == "None":
                raise Exception(data["result"])

            logger.info(f"Remote Upload Added {hash} {data}")
            try:
                await proc.edit("🔄 **Remote Url Upload Added Successfully**")
            except Exception as e:
                logger.warning(f"{hash} {e}")

            await asyncio.sleep(5)
            slug = data["player"].replace("\\", "")
            return slug

        except Exception as e:
            logger.info(f"Failed using raw api {hash} {file_url} {e}")
            # Using Playerxstream API

            file_url = quote(file_url)

            if "drive.google.com" in file_url:
                # Extract file id from google drive url
                pattern = r"drive\.google\.com/file/d/([^/]+)"
                match = re.search(pattern, file_url)
                if match:
                    file_url = "https://drive.google.com/file/d/" + match.group(1)
                else:
                    raise Exception(
                        f"Invalid Google Drive URL\n\nMake sure it of the format `https://drive.google.com/file/d/FILE_ID`"
                    )

                async with session.get(
                    f"https://www.playerx.stream/api.php?url={file_url}&api_key={PLAYERX_API_KEY}"
                ) as response:
                    resp = await response.text()
                    logger.info(f"{hash} {resp}")
                    data = await response.json()

                if str(data["result"]) == "false":
                    raise Exception(
                        "Failed to gdrive url for conversion\n\n💠 **Supported URL Formats :** https://t.me/TechZBots/813"
                    )

                logger.info(f"Remote Upload Added {hash} {data}")
                try:
                    await proc.edit("🔄 **Remote Url Upload Added Successfully**")
                except Exception as e:
                    logger.warning(f"{hash} {e}")

                await asyncio.sleep(5)
                slug = data["content"]
                return slug
            else:
                async with session.get(
                    f"https://www.playerx.stream/api.php?api_key={PLAYERX_API_KEY}&url={file_url}&action=add_remote_url"
                ) as response:
                    resp = await response.text()
                    logger.info(f"{hash} {resp}")
                    data = await response.json()

                if data["player"] == "None":
                    raise Exception(
                        str(data["result"])
                        + "\n\n💠 **Supported URL Formats :** https://t.me/TechZBots/813"
                    )

                logger.info(f"Remote Upload Added {hash} {data}")
                try:
                    await proc.edit("🔄 **Remote Url Upload Added Successfully**")
                except Exception as e:
                    logger.warning(f"{hash} {e}")

                await asyncio.sleep(5)
                slug = data["player"].replace("\\", "")
                return slug

    async def extract_video(self, session: aiohttp.ClientSession, url: str, hash: str):
        logger.info(f"Extracting Video Data {url} {hash}")
        host = url.split("/v/")[0]
        headers = {
            "Origin": host,
            "Referer": url + "/",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        async with session.get(url, headers=headers) as r:
            content = await r.text()
        soup = BeautifulSoup(content, "html.parser")

        subtitles = soup.find_all("track", {"kind": "captions"})
        video_subtitles = []

        for i in subtitles:
            label = i.get("label", "Unknown")
            lang = i.get("srclang", "").upper()
            src = i.get("src")
            video_subtitles.append((f"{lang} - {label}", src))

        scripts = soup.find_all("script")
        encrypted_json = False

        for i in scripts:
            code: str = i.text.strip()

            if code.startswith("JScripts"):
                encrypted_json = code
                continue

            if encrypted_json:
                password_code = code
                break

        if (not encrypted_json) or (not password_code):
            raise Exception("Failed to extract video data")

        cryptojs1, cryptojs2 = await self._get_crypto_files(session)
        video_code = await self._decrypt_js(
            cryptojs1, cryptojs2, encrypted_json, password_code
        )

        # parse video code to get urls
        sources = re.findall(r'"(https://[^"]+)"', video_code)

        for i in sources:
            if "video.m3u8" in i:
                video_url = i.strip()
                continue
            if i.endswith(".jpg"):
                video_preview = i.strip()
                continue

            if i.endswith("thumbnail.vtt"):
                video_thumb = i.strip()
                continue

        data = {
            "video_url": video_url,
            "video_preview": video_preview,
            "video_thumb": video_thumb,
            "video_subtitle": video_subtitles,
        }
        logger.info(f"Extracted Video Data {hash} {data} ")
        return data, headers
