import json
import os
import types
from pathlib import Path

import requests


def load_config():
    filename = os.path.join(Path(__file__).parent,"config.py")
    d = types.ModuleType("config")
    d.__file__ = filename
    with open(filename, mode="rb") as config_file:
        exec(compile(config_file.read(), filename, "exec"), d.__dict__)
    config = {}
    for key in dir(d):
        if key.isupper():
            config[key] = getattr(d, key)
    return config


def handle():
    config = load_config()
    payload = {
        "val[ProfileCardID]": config["PROFILE_CARD_ID"],
        "val[PlayerName]": config["PLAYER_NAME"],
        "val[Birthday]": config["BIRTHDAY_M_D"],
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://primagi.jp/mypage/login/",
        "Origin": "https://primagi.jp",
        "Accept": "text/html"
    }
    response = requests.post(
        url="https://primagi.jp/mypage/login/",
        data=payload,
        headers=headers,
    )
    logged_cookies = response.history[-1].cookies

    # 画像一覧取得
    payload = {
        "TargetYM": "202203",
        "LatestPhotoSeq": "",
        "AcquisitionsCount": "10"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://primagi.jp/mypage/myphoto/",
        "Origin": "https://primagi.jp",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }

    more = True
    data = None
    while more:
        payload["LatestPhotoSeq"] = "" if data is None else data["PhotoDataList"][-1]["PhotoSeq"]
        response = requests.post(
            url="https://primagi.jp/mypage/api/myphotolist/",
            data=payload,
            headers=headers,
            cookies=logged_cookies,
        )
        print(json.loads(response.content.decode("utf-8")))
        data = json.loads(response.content.decode("utf-8"))["data"]

        for photo in data["PhotoDataList"]:
            try:
                folder = Path(os.path.curdir, photo["PlayDate"])
                if not folder.exists():
                    folder.mkdir()
                img = requests.get(photo["ImageUrl"])
                with open(os.path.join(folder, photo["ImageUrl"].split("/")[-1]), "wb") as out:
                    out.write(img.content)
            except:
                continue
        more = data["More"] == 1

if __name__ == '__main__':
    handle()
