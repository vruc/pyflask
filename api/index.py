import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

print(f"VERCEL_ENV {os.getenv('VERCEL_ENV')}")
print(f"1111 {os.getenv('mongo_sht_connection_string')}")
print(f"2222 {os.environ.get('mongo_sht_connection_string')}")

uri = os.environ.get('mongo_sht_connection_string')

print(f"uri {os.getenv('uri')}")

# 如果 password 为空，则停止运行
# if not mongo_sht_connection_string:
#     raise Exception("MongoDB connection is not set")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["sht"]

app = Flask(__name__)

password = os.environ.get('mongo_pwd_sht')

# 如果 password 为空，则停止运行
if not password:
    raise Exception("MongoDB password is not set")

app = Flask(__name__)

def save_data(data):
    try:
        # 将 data 保存到 threads 集合中，如果集合不存在则自动创建，按 url 来判断
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


@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About, with sht as the secret'