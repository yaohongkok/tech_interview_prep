from urllib.request import urlopen, Request
import json
import time

URL = 'https://api.restful-api.dev/objects'
TIMEOUT = 10
API_KEY = 'c4a4cc40-ddbe-4bba-8d4a-20c13e178556'
HEADERS = {
    'x-api-key': API_KEY,
    'Content-Type': 'application/json',
    'User-Agent': 'web_call/1.0',
}

def get(id:str):
    request = Request(f'{URL}/{id}', headers=HEADERS)
    with urlopen(request, timeout=TIMEOUT) as response:
        return response.read()

def post(data:dict):
    request = Request(URL,
                      method='POST', 
                      headers=HEADERS,
                      data=json.dumps(data).encode('utf-8'))
    with urlopen(request, timeout=TIMEOUT) as response:
        return response.read()

def put(id:str, data:dict):
    request = Request(f'{URL}/{id}', 
                      method='PUT',
                      headers=HEADERS,
                      data=json.dumps(data).encode('utf-8'))
    with urlopen(request, timeout=TIMEOUT) as response:
        return response.read()

def delete(id:str):
    request = Request(f'{URL}/{id}', 
                      headers=HEADERS,
                      method='DELETE')
    with urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


if __name__ == '__main__':
    post_data = {'name': 'KYH'}
    post_response = post(post_data)
    post_resp_dict = json.loads(post_response)
    print(f'POST Response as Dictionary:\n\n{post_resp_dict}\n')

    data_id = post_resp_dict.get('id')

    time.sleep(5)

    get_response = get(data_id)
    print(f'GET Response:\n\n{get_response.decode("utf-8")}\n')

    time.sleep(5)

    put_data = {'name': 'KYH Updated'}
    put_response = put(data_id, put_data)
    put_resp_dict = json.loads(put_response)
    print(f'PUT Response as Dictionary:\n\n{put_resp_dict}\n')

    time.sleep(5)
    
    get_response = get(data_id)
    print(f'GET Response:\n\n{get_response.decode("utf-8")}\n')

    time.sleep(5)
    
    delete_response = delete(data_id)
    print(f'DELETE Response:\n\n{delete_response.decode("utf-8")}\n')
    
    
