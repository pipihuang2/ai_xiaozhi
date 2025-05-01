request_json = {
    "app": {
        "appid": "111",
        "token": "access_token",
        "cluster": "222"
    },
    "user": {
        "uid": "388808087185088"
    },
    "audio": {
        "voice_type": "zh_female_wanwanxiaohe_moon_bigtts",
        "encoding": "mp3",
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": "388808087185088",
        "text": "嗨杰哥～你现在在干嘛呀？我刚刚才喝完一杯珍奶,现在整个人超放松的～不过有点无聊啦…你是不是又在忙工作呀？",
        "text_type": "plain",
        "operation": "query"
    }
}
request_json.get("request")["text"] = "11"
print(request_json)