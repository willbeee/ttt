import base64
import json
import time
from urllib import parse
import requests
from tabulate import tabulate
from pywidevine.L3.cdm import deviceconfig
from pywidevine.L3.decrypt.wvdecryptcustom import WvDecrypt
from tools import dealck, md5, get_size, get_pssh


def get_key(pssh):
    LicenseUrl = "https://drml.video.iqiyi.com/drm/widevine?ve=0"
    wvdecrypt = WvDecrypt(init_data_b64=pssh, cert_data_b64="",device=deviceconfig.device_android_generic)
    widevine_license = requests.post(url=LicenseUrl, data=wvdecrypt.get_challenge())
    license_b64 = base64.b64encode(widevine_license.content)
    wvdecrypt.update_license(license_b64)
    correct, keys = wvdecrypt.start_process()
    for key in keys:
        print('--key ' + key)
    key_string = ' '.join([f"--key {key}" for key in keys])
    return key_string


class iqy:
    def __init__(self, aqy):
        self.ck = aqy
        ckjson = dealck(aqy)
        self.P00003 = ckjson.get('P00003', "1008611")
        self.pck = ckjson.get('P00001')
        self.dfp = ckjson.get('__dfp', "").split("@")[0]
        self.QC005 = ckjson.get('QC005', "")
        self.requests = requests.Session()
        self.requests.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })
        self.bop = f"{{\"version\":\"10.0\",\"dfp\":\"{self.dfp}\",\"b_ft1\":8}}"

    @staticmethod
    def parse(shareurl):
        try:
            url = "https://iface2.iqiyi.com/video/3.0/v_play"
            params = {
                "app_k": "20168006319fc9e201facfbd7c2278b7",
                "app_v": "8.9.5",
                "platform_id": "10",
                "dev_os": "8.0.1",
                "dev_ua": "Android",
                "net_sts": "1",
                "secure_p": "GPhone",
                "secure_v": "1",
                "dev_hw": "{\"cpu\":0,\"gpu\":\"\",\"mem\":\"\"}",
                "app_t": "0",
                "h5_url": shareurl
            }
            response = requests.get(url, params=params)
            data = response.json()
            pid = data['play_pid']
            aid = data['play_aid']
            tvid = data['play_tvid']
            Album = data['album']
            Title = Album['_t']
            Cid = Album['_cid']
            return pid, aid, tvid, Title, Cid
        except Exception as e:
            print(e)
            return None, None, None, None, None

    @staticmethod
    def get_avlistinfo(title, albumId, cid, pid):
        rets = []
        page = 1
        size = 200

        def getlist6():
            url = "https://pcw-api.iqiyi.com/album/source/svlistinfo"
            params = {
                "cid": "6",
                "sourceid": pid,
                "timelist": ",".join([str(i) for i in range(2000, 2026)]),
            }
            response = requests.get(url, params=params)
            data = response.json()['data']
            for a, b in data.items():
                for i in b:
                    ret = {
                        "album": title,
                        "name": i['name'],
                        "tvId": i['tvId'],
                    }
                    rets.append(ret)

        def getlist():
            aid = albumId
            url = "https://pcw-api.iqiyi.com/albums/album/avlistinfo"
            params = {
                "aid": aid,
                "page": page,
                "size": size
            }
            response = requests.get(url, params=params).json()
            if response['code'] != 'A00000':
                return None
            data = response['data']
            total = data['total']
            if total > size:
                for i in range(2, total // size + 2):
                    params['page'] = i
                    response = requests.get(url, params=params).json()
                    data['epsodelist'].extend(response['data']['epsodelist'])
            for i in data['epsodelist']:
                ret = {
                    "album": title,
                    "name": i['name'],
                    "tvId": i['tvId'],
                }
                rets.append(ret)

        if cid == 1:
            ret = {
                "album": title,
                "name": title,
                "tvId": albumId,
            }
            rets.append(ret)
        elif cid == 6:
            getlist6()
        else:
            getlist()
        return rets

    def get_param(self, tvid="", vid=""):
        tm = str(int(time.time() * 1000))
        authKey = md5("d41d8cd98f00b204e9800998ecf8427e" + tm + str(tvid))
        params = {
            "tvid": tvid,
            "bid": "800",
            "src": "01010031010000000000",
            "uid": self.P00003,
            "k_uid": self.QC005,
            "authKey": authKey,
            "dfp": self.dfp,
            "pck": self.pck,
            "vid": "",
            "tm": tm,
            "vt": "0",
            "rs": "1",
            "ori": "pcw",
            "ps": "1",
            "pt": "0",
            "d": "0",
            "s": "",
            "lid": "0",
            "cf": "0",
            "ct": "0",
            "k_tag": "1",
            "locale": "zh_cn",
            "k_err_retries": "0",
            "up": "",
            "sr": "1",
            "qd_v": "5",
            "qdy": "u",
            "qds": "0",
            "k_ft1": "706436220846084",
            "k_ft4": "1162321298202628",
            "k_ft2": "262335",
            "k_ft5": "134217729",
            "k_ft6": "128",
            "k_ft7": "688390148",
            "fr_300": "120_120_120_120_120_120",
            "fr_500": "120_120_120_120_120_120",
            "fr_600": "120_120_120_120_120_120",
            "fr_800": "120_120_120_120_120_120",
            "fr_1020": "120_120_120_120_120_120",
        }
        dash = f'/dash?'
        for a, b in params.items():
            dash += f"{a}={b}&"
        dash = dash[:-1] + "&bop=" + parse.quote(self.bop) + "&ut=14"
        vf = md5(dash + "tle8orw4vetejc62int3uewiniecr18i")
        dash += f"&vf={vf}"
        return dash

    def get_dash(self, tvid="", vid=""):
        params = self.get_param(tvid=tvid, vid=vid)
        url = "https://cache.video.iqiyi.com" + params
        res = self.requests.get(url)
        return res.json()

    def run(self, url=None):
        url = input("请输入爱奇艺分享链接：") if url is None else url
        pid, aid, tvid, title, cid = self.parse(url)
        if pid is None:
            print("解析失败")
            return
        avlist = self.get_avlistinfo(title, aid, cid, pid)
        if avlist is None:
            print("获取列表失败")
            return
        table = tabulate(avlist, headers="keys", tablefmt="grid", showindex=range(1, len(avlist) + 1))
        print(table)
        index = input("请输入序号：")
        index = index.split(",")
        for i in index:
            if i.isdigit():
                i = int(i)
                if i > len(avlist):
                    print("序号错误")
                    continue
                tvId = avlist[i - 1]['tvId']
                name = avlist[i - 1]['name']
                ctitle = avlist[i - 1]['album']
                print(f"正在获取{ctitle} {name}的m3u8")
                response = self.get_dash(tvid=tvId)
                try:
                    if response['data']['boss_ts']['code'] != 'A00000':
                        print(f'获取m3u8失败\n')
                        print(response['data']['boss_ts']['msg'])
                        continue
                except:
                    pass
                data = response['data']
                program = data['program']
                if 'video' not in program:
                    print("无视频")
                    continue
                video = program['video']
                audio = program['audio']
                stl = program.get("stl", [])
                '''
                                list = []
                for a in video:
                    scrsz = a.get('scrsz', '')
                    size = a['vsize']
                    vid = a['vid']
                    list.append((scrsz, vid, size))
                list.sort(key=lambda x: x[-1], reverse=True)
                tb = tabulate(list, headers=["分辨率", "vid", "大小"], tablefmt="grid",
                              showindex=range(1, len(list) + 1))
                print(tb)
                index = input("请输入序号：")
                index = index.split(",")
                for i in index:
                    vid = list[int(i) - 1][1]
                    response = self.get_dash(tvid=tvId, vid=vid)
                    try:
                        if response['data']['boss_ts']['code'] != 'A00000':
                            print(f'获取m3u8失败\n')
                            print(response['data']['boss_ts']['msg'])
                            continue
                    except:
                        pass
                    data = response['data']
                    program = data['program']
                    if 'video' not in program:
                        print("无视频")
                        continue
                    video = program['video']
                '''
                for a in video:
                    try:
                        scrsz = a.get('scrsz', '')
                        vsize = get_size(a['vsize'])
                        m3u8data = a['m3u8']
                        fr = str(a['fr'])
                        name = name + "_" + scrsz + "_" + vsize + "_" + fr + 'fps'
                        name = name.replace(' ', '_')
                        file = f"./chache/{name}.m3u8"
                        savepath = f"./download/iqy/{ctitle}"
                        with open(file, 'w') as f:
                            f.write(m3u8data)
                        if m3u8data.startswith('{"payload"'):
                            m3u8data = json.loads(m3u8data)
                            init = m3u8data['payload']['wm_a']['audio_track1']['codec_init']
                            pssh = get_pssh(init)
                            key_string = get_key(pssh)
                            cmd = f"N_m3u8DL-RE.exe \"{file} \" --tmp-dir ./cache --save-name \"{name}\" --save-dir \"{savepath}\" --thread-count 16 --download-retry-count 30 --auto-select --check-segments-count " + key_string + " --decryption-binary-path ./mp4decrypt.exe  -M format=mp4"
                        if m3u8data.startswith('<?xml'):
                            pssh = m3u8data.split('<cenc:pssh>')[1].split('</cenc:pssh>')[0]
                            key_string = get_key(pssh)
                            cmd = f"N_m3u8DL-RE.exe \"{file} \" --tmp-dir ./cache --save-name \"{name}\" --save-dir \"{savepath}\" --thread-count 16 --download-retry-count 30 --auto-select --check-segments-count " + key_string + " --decryption-binary-path ./mp4decrypt.exe  -M format=mp4"
                        else:
                            cmd = f"N_m3u8DL-RE.exe \"{file} \" --tmp-dir ./cache --save-name \"{name}\" --save-dir \"{savepath}\" --thread-count 16 --download-retry-count 30 --auto-select --check-segments-count "
                        with open(f"{ctitle}.bat", 'a', encoding='gbk') as f:
                            f.write(cmd)
                            f.write("\n")
                        print(f"获取{name}成功")
                    except:
                        continue
            else:
                continue


if __name__ == '__main__':
    ck = "QC006=82xoyqrjtjwyrd7nehudmriw; TQC030=1; QP0030=1; T00404=2343543dc6c1a4c989afc26634bc4035; QC173=0; QC196=1.25; P00004=.1683876317.d77101f60b; QC005_NATIVE=qayesqutkr24xan2kkxftxrs7bffuyrk; QP0034=%7B%22v%22%3A15%2C%22dp%22%3A1%2C%22dm%22%3A%7B%22wv%22%3A1%7D%2C%22m%22%3A%7B%22wm-vp9%22%3A1%2C%22wm-av1%22%3A1%2C%22m4-hevc%22%3A1%7D%2C%22hvc%22%3Atrue%7D; QC206=29801f279c097b36f32fcb79c40a860e; QC207=51bca9c79cb8d92b7a08b1c06031293b; QC212=d67d53a5e61387e5763058e76f3b829c; QC211=ff9431e4d428e01287bf5b7305795a33; QC005_PCA=qayesqutkr24xan2kkxftxrs7bffuyrk; P00003_PCA=1086805810091691; isRefreshAuth=1; QC021=%5B%7B%22key%22%3A%22%E7%8B%AC%E5%AE%B6%E4%BF%AE%E5%A4%8D%E7%89%88%22%7D%5D; QC008=1683260350.1698390017.1698745904.19; QC007=DIRECT; QC191=; nu=0; P00040=Cl5GWWhCNmpPJTJCNDZrVnRXNlJIV0thTEFuYzZydjFwbUtuZDB3UFJvWFRvaVE2SUEyVzh6S1U2WlB5bHRvc1Y2RU93U0huOERYeVZmZUUyOHJVR2IyZ0F3JTNEJTNEEAEqATEwAFAEYABqIHFheWVzcXV0a3IyNHhhbjJra3hmdHhyczdiZmZ1eXJrggFCaHR0cHM6Ly9wYXNzcG9ydC5pcWl5aS5jb20vYXBpcy90aGlyZHBhcnR5L25jYWxsYmFjay5hY3Rpb24/ZnJvbT00iAEBkAEAyAEB2gEUMDEwMTAwMjEwMTAwMDAwMDAwMDCaAitodHRwczovL3d3dy5pcWl5aS5jb20vdGhpcmRsb2dpbi9jbG9zZS5odG1sogIraHR0cHM6Ly93d3cuaXFpeWkuY29tL3RoaXJkbG9naW4vY2xvc2UuaHRtbKoCATG6AgEx; P111114=1698745914; QC160=%7B%22type%22%3A-1%2C%22conformLoginType%22%3A0%7D; QP0037=30; T00700=EgcI9L-tIRABEgcI58DtIRABEgcIq8HtIRABEgcIrcHtIRAB; P00001=c7pbpYvm3XYJHm1YwBT6um2BjOhDqm117ReL29jpSXlCoJaxtm3vQaZbgrNwRpYsbi3vv812b; P00007=c7pbpYvm3XYJHm1YwBT6um2BjOhDqm117ReL29jpSXlCoJaxtm3vQaZbgrNwRpYsbi3vv812b; P00003=1086805810091691; P00002=%7B%22uid%22%3A1086805810091691%2C%22pru%22%3A1086805810091691%2C%22user_name%22%3A%22199****6024%22%2C%22nickname%22%3A%22%5Cu7528%5Cu62373dc71b24016ab%22%2C%22pnickname%22%3A%22%5Cu7528%5Cu62373dc71b24016ab%22%2C%22type%22%3A11%2C%22email%22%3A%22%22%7D; P00010=1086805810091691; P01010=1698768000; P00PRU=1086805810091691; __dfp=a10658c0bdc3fd4e3c91a7f23a29c5fc2d62d8a52f4d88a3ad44132c1bd1e30c9e@1699586507505@1698290508505; QC175=%7B%22upd%22%3Afalse%2C%22ct%22%3A1698745952424%7D; QC170=1; QC179=%7B%22vipTypes%22%3A%2214%2C13%2C4%22%2C%22vipType%22%3A%224%22%2C%22userIcon%22%3A%22%2F%2Fimg7.iqiyipic.com%2Fpassport%2F20230104%2Fce%2Fdf%2Fpassport_1086805810091691_167280232017376_130_130.jpg%22%2C%22uid%22%3A1086805810091691%2C%22iconPendant%22%3A%22%22%2C%22bannedVip%22%3Afalse%2C%22allVip%22%3Atrue%2C%22validVip%22%3Atrue%7D; QC163=1; QP0013=13%2C4%2C5%2C14; QP0014=3; QC188=false; QY_PUSHMSG_ID=erf75cgwo524xan2kkxftxrs7b6tsf5k; QP0033=1; QP0035=5; QP0025=1; QC189=5257_B%2C6082_B%2C5335_B%2C5465_B%2C6843_B%2C6832_C%2C5924_D%2C6151_C%2C5468_B%2C7074_C%2C5592_B%2C6031_B%2C7024_A%2C6629_B%2C5670_B%2C7301_B%2C6050_B%2C6578_B%2C6312_B%2C6091_B%2C7090_B%2C6237_B%2C6249_C%2C6704_C%2C6752_C%2C7150_B%2C7332_B; QC186=true; QC187=true; QC005=erf75cgwo524xan2kkxftxrs7b6tsf5k; QC010=247102720; QP0027=26; QC208=ba461b3854181e46273ed0a3d00b79a2; websocket=true; QY00001=1086805810091691; IMS=IggQABj_yISqBioqCiAzMGJiNmFlZTBkNjMxMGY3MGZjNmMwMDVkNDliNjQ2NRAAIgAoRDAFciQKIDMwYmI2YWVlMGQ2MzEwZjcwZmM2YzAwNWQ0OWI2NDY1EACCAQCKASQKIgogMzBiYjZhZWUwZDYzMTBmNzBmYzZjMDA1ZDQ5YjY0NjU; QP008=120; QC193=7791938234030700%2C1964%2C123%3B5652561918212800%2C2198%2C79%3B2904341724243800%2C2788%2C97%3B1810989673848200%2C2755%2C96%3B6822119723349900%2C6354%2C0; QP0036=20231031%7C84.512"
    iq = iqy(ck)
    iq.run()
