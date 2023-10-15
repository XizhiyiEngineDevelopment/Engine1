import requests
import os
# 设置代理
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}
# 配置信任证书
os.environ['REQUESTS_CA_BUNDLE'] = '/Users/yihou/Documents/projects/ai_agent_23_10/certificates.pem'

# 通过代理发送请求
response = requests.get("https://www.baidu.com", proxies=proxies)

# 打印响应内容
print(response.text)