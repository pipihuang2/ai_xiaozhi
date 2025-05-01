import websockets
import uuid
import gzip
import json
import asyncio
import io

TTS_URL = "wss://openspeech.bytedance.com/api/v1/tts/ws_binary"
TOKEN = "M0CUGPoFeM-eWWpS_DG151hce7X5lQUL"
APPID = "8394079928"
CLUSTER = "volcano_tts"

async def tts_generate(text: str) -> bytes:
    req_json = {
        "app": {"appid": APPID, "token": "access_token", "cluster": CLUSTER},
        "user": {"uid": "123"},
        "audio": {
            "voice_type": "zh_female_wanwanxiaohe_moon_bigtts",
            "encoding": "wav",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "submit"
        }
    }

    payload = gzip.compress(json.dumps(req_json).encode())
    packet = bytearray(b'\x11\x10\x11\x00')
    packet.extend(len(payload).to_bytes(4, 'big'))
    packet.extend(payload)

    audio_buffer = io.BytesIO()
    async with websockets.connect(TTS_URL, extra_headers={"Authorization": f"Bearer; {TOKEN}"}) as ws:
        await ws.send(packet)
        while True:
            res = await ws.recv()
            if parse_tts(res, audio_buffer):
                break
    return audio_buffer.getvalue()

def parse_tts(res, buf: io.BytesIO):
    header_size = res[0] & 0x0F
    message_type = res[1] >> 4
    flags = res[1] & 0x0F
    payload = res[header_size * 4:]
    if message_type == 0xB:
        if flags == 0: return False
        payload = payload[8:]
        buf.write(payload)
        return int.from_bytes(res[header_size*4:header_size*4+4], 'big', signed=True) < 0
    return False
