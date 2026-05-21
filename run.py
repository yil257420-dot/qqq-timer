import requests
import os

def run():
    # 强制获取 key
    key = os.environ.get("PUSHDEER_KEY")
    
    if not key or not key.strip():
        print("错误：PUSHDEER_KEY 未找到或为空")
        return

    # 使用最简单的 GET 请求推送测试文本
    try:
        url = "https://api2.pushdeer.com/message/push"
        params = {"pushkey": key, "text": "【系统排障】测试推送连接性，如果收到此消息，说明通道正常。"}
        response = requests.get(url, params=params, timeout=10)
        
        print(f"推送响应状态码: {response.status_code}")
        print(f"推送响应内容: {response.text}")
    except Exception as e:
        print(f"推送请求抛出异常: {e}")

if __name__ == "__main__":
    run()
