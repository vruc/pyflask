import json
import os
import re 
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import requests
from bs4 import BeautifulSoup

load_dotenv()

client = MongoClient(os.environ.get('mongo_sht_connection_string'), server_api=ServerApi('1'))
db = client["sht"]

CACHE_DIR = 'cache'

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    start_time = time.time()
    q = request.args.get('q').lower()
    print(q)

    match = re.search(r'[a-zA-Z]+-[a-zA-Z]?\d+', q)
    if match:
        q = match.group(0)
    else:
        return jsonify([]), 400

    q = q.upper()

    cache_file = os.path.join(CACHE_DIR, f"{q}.json")

    # 检查缓存文件是否存在
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"请求耗时: {elapsed_time:.2f} 秒")
                print(f"从缓存文件 {cache_file} 读取数据")
            return cached_data
        except Exception as e:
            print(f"读取缓存文件 {cache_file} 出错: {e}")

    print(q)

    url = "https://javdb.com/search?f=all&q={}".format(q)

    payload = {}
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        'Cookie': 'list_mode=h; theme=auto; locale=en; over18=1; _jdb_session=hbeHkgT0J3VPutVmt2vPe0ggV2VttbW6AzJvryAFs2DA9EvBVBq0EVYLpQV%2Fgg3E1HEPMrtCl5Lj4Vza%2FCjHYN%2Buay4v8VYUgIdkn8atlh8vCURtooV1hX7C5YoX74iNvUzhJzTl%2BVJH0Ks4GZXb76xTm%2Bg3VaQfFJYUXSHnUcESsOzGpopjgbcUiaKe3S8HDbupqFn%2BJRTQ6CEqj9%2B%2B%2BNA1sny9JipEFV5ljBq2Y6M7iEcIi4NBbt7879rZqGl%2BJ54NyG68N2ALhmApIKeyQnrqVQ6CvQahfXmjiKb0CyaVBI9P2Wu5%2BCmC--rp0A6qVefU0l9mpE--87ui9SBzYreUEUFNSpt5OA%3D%3D; cf_clearance=stnkfZbF2Gs1nkQ2VP4FIi7WPMo0jD5ElpvJhQNMmQ4-1745977984-1.2.1.1-1i79H_WBn_YYfW_lVWDX0BcGJX2kgE_PD1UnPbSNKZp.jtCzBA7jGV_ZkiK53J7hTmnR9YEiYGJem0QyUGC6RCHPP9HjM9xh3U6O8LaTMiOcsKqZQBneftWfLlaq33lAYhczlPp._UXveQHl8il_Z_yz3V25TK11WYSWxXt2mAWDErHcruvruFYtXgNlhj4FvCBpWKOoUATCxfAf0.U.kDrWi9QBEysOFeiWHAYNKXlX7YC_IdBtfu19ONxhy6W_Y9hrlHSyVhrUg.NIJLxAEXufDBHPfUPVNBFb9AOPqTwWXTEHHJ2EcKonR6ZUIon35028pKZffnXnlTBsGhleAJn6VioPTyiu8orKWRzPkxA; _jdb_session=Jrj5XddqOvzfwP9S%2FctxhLu9gjh7gvRtfe31LEXrd7lOuTJTCstbBmcs%2Fc186YLcykvJ2BC4TyTrD9EUKamcu3dUmT%2Bjh2ZsHhqsCpNpkEPuZ5K908Z7Pmy54%2B3bwXbOXlLYIv6EaH4jii%2Ba3VoO7IKMxhuXXohCkqkHE%2BzFTluTL9%2BHc1Fp86FmB0caFkvHzVn7TRDgeAFDrUBSEJ1MOWtvL2%2BG%2BVkizTiv6SMTFUcmkuzhT%2B2IxsxkOtCVo%2FEFZeuqvfORAgnGjbvvOKURHBqa%2FohPj1%2B%2BtGePW9tN7ZCcRL0Xcvp3hSte--%2Fz9y0%2FDybPjexVtV--VUbjCd285NVOPbvNarm7Ug%3D%3D; locale=en'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
     # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(response.text, 'html.parser')
    # 查找所有 div.video-title 元素
    video_titles = soup.find_all('div', class_='video-title')
    covers = soup.find_all('div', class_='cover')
    covers = soup.find_all('div', class_='cover')
    # 提取每个 div.cover 下 img 元素的 src 地址
    cover_srcs = []
    for cover in covers:
        img = cover.find('img')
        if img and 'src' in img.attrs:
            cover_srcs.append(img['src'])
    # 提取每个元素的文本内容
    title_texts = [title.get_text(strip=True) for title in video_titles]
    # 过滤出以 q 开头的标题
    if q:
        title_texts = [title for title in title_texts if title.lower().startswith(q.lower())]
    # 在 title_texts中 q 后面添加一个空格
    for index, text in enumerate(title_texts):
        print(text)
        if text.lower().startswith(q.lower()):
            title_texts[index] = f"{q} " + text[len(q):]
    # 打印提取的文本内容
    print(title_texts)

    if len(title_texts) == 0:
        return jsonify([]), 404

    result = { 'title': title_texts[0], 'cover': cover_srcs[0] }

    # 保存结果到缓存文件
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存缓存文件 {cache_file} 出错: {e}")
    end_time = time.time()  # 记录请求结束时间
    elapsed_time = end_time - start_time  # 计算请求耗时
    print(f"请求 {url} 耗时: {elapsed_time:.2f} 秒")  # 打印请求耗时
    return result


def convert_thread_url(url):
    import re
    match = re.match(r"https://www.sehuatang.net/thread-(\d+)-(\d+)-(\d+)\.html", url)
    if match:
        num1 = match.group(1)
        num2 = match.group(2)
        return f"https://www.sehuatang.net/thread-{num1}-{num2}-1.html"
    else:
        return url

def save_data(data):
    try:
        # 将 data 保存到 threads 集合中，如果集合不存在则自动创建，按 url 来判断
        # url = convert_thread_url(data['url'])
        db['threads'].update_one({'url': data['url']}, {'$set': data}, upsert=True)
    except Exception as e:
        print(e)

@app.route('/save', methods=['POST'])
def handle_save():
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Request body must be an array'}), 400

        # 在日志输出 data 的内容
        # print(data)

        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for item in data:
            try:
                if not item or 'title' not in item or 'url' not in item:
                    results['failed'] += 1
                    results['errors'].append(f'Invalid item format: {item}')
                    continue
                
                save_data(item)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return jsonify({
            'message': f'Processed {len(data)} items',
            'results': results
        }), 200 if results['failed'] == 0 else 207
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files/migrate-file', methods=['POST'])
def upload_file():
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ["blobKey", "name", "companyId", "path", "source", "tags", "createdAt", "updatedAt"]
        for field in required_fields:
            if field not in payload:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        mock_id = str(ObjectId())
        result = {
            "data": {
                "id": mock_id,
                "name": payload["name"],
                "companyId": payload["companyId"],
                "source": payload["source"],
                "path": payload["path"],
                "type": None,
                "tags": payload["tags"],
                "versions": {
                    "1": {
                        "createdAt": payload["createdAt"]
                    }
                },
                "createdAt": payload["createdAt"],
                "updatedAt": payload["updatedAt"]
            }
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About, with sht as the secret'