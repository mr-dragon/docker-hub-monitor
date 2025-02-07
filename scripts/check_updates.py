import os
import json
import requests
from datetime import datetime
from dateutil import parser
import smtplib
import pytz  # 添加时区支持
from email.mime.text import MIMEText
from email.header import Header
import logging

def read_images():
    # 直接从工作目录读取
    try:
        with open('images.txt', 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        # 如果文件不存在，创建一个包含示例镜像的文件
        example_images = [
            'nginx',
            'cloudnas/clouddrive2',
            'linuxserver/transmission:4.0.5'
        ]
        os.makedirs(os.path.dirname('images.txt'), exist_ok=True)
        with open('images.txt', 'w') as f:
            f.write('\n'.join(example_images))
        return example_images

def get_last_updated(image_name):
    filename = f"last_updated/{image_name.replace('/', '_')}.txt"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return f.read().strip()
    return None

def save_last_updated(image_name, timestamp):
    os.makedirs('last_updated', exist_ok=True)
    filename = f"last_updated/{image_name.replace('/', '_')}.txt"
    with open(filename, 'w') as f:
        f.write(timestamp)

def get_docker_hub_info(image):
    if image.startswith('library/'):
        url = f"https://hub.docker.com/v2/repositories/{image}/tags/latest"
    else:
        parts = image.split(':')
        image_name = parts[0]
        tag = parts[1] if len(parts) > 1 else 'latest'
        url = f"https://hub.docker.com/v2/repositories/{image_name}/tags/{tag}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('last_updated')
    return None

def send_wecom_notification(webhook_url, content):
    if not webhook_url:
        return
    
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    requests.post(webhook_url, json=data)

def send_email_notification(to_email, content):
    if not all([os.getenv('EMAIL_FROM'), os.getenv('EMAIL_PASSWORD'), to_email]):
        return
    
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header('Docker镜像更新通知', 'utf-8')
    msg['From'] = os.getenv('EMAIL_FROM')
    msg['To'] = to_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv('EMAIL_FROM'), os.getenv('EMAIL_PASSWORD'))
        server.sendmail(os.getenv('EMAIL_FROM'), to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")

def generate_changelog(images_status):
    os.makedirs('logs', exist_ok=True)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    content = [
        f"# Docker Images Update Check - {current_time}\n",
        "## 检查结果\n"
    ]
    
    for image, status in images_status.items():
        content.append(f"### {image}")
        content.append(f"- 当前更新时间: {status['current_time']}")
        content.append(f"- 上次检查时间: {status['last_time'] or '首次检查'}")
        content.append(f"- 状态: {'有更新' if status['updated'] else '无更新'}\n")
    
    changelog_path = 'logs/changelog.md'
    # 读取现有的changelog内容
    existing_content = []
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            existing_content = f.readlines()
    
    # 将新内容添加到文件开头
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
        if existing_content:
            f.write('\n' + '---\n' + ''.join(existing_content))

def generate_changelog(images_status):
    os.makedirs('logs', exist_ok=True)
    
    # 设置时区为上海时间
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(shanghai_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    content = [
        f"# Docker Images Update Check - {current_time}\n",
        "## 检查结果\n"
    ]
    
    for image, status in images_status.items():
        # 转换 Docker Hub 返回的 UTC 时间到上海时间
        current_update_time = parser.parse(status['current_time'])
        if current_update_time.tzinfo is None:
            current_update_time = pytz.utc.localize(current_update_time)
        current_update_time = current_update_time.astimezone(shanghai_tz)
        
        # 转换上次检查时间（如果存在）
        last_update_time = status['last_time']
        if last_update_time:
            last_update_time = parser.parse(last_update_time)
            if last_update_time.tzinfo is None:
                last_update_time = pytz.utc.localize(last_update_time)
            last_update_time = last_update_time.astimezone(shanghai_tz)
            last_time_str = last_update_time.strftime('%Y-%m-%d %H:%M:%S %z')
        else:
            last_time_str = '首次检查'

        content.append(f"### {image}")
        content.append(f"- 当前更新时间: {current_update_time.strftime('%Y-%m-%d %H:%M:%S %z')}")
        content.append(f"- 上次检查时间: {last_time_str}")
        content.append(f"- 状态: {'有更新' if status['updated'] else '无更新'}\n")
    
    changelog_path = os.path.join('logs', 'changelog.md')
    # 读取现有的changelog内容
    existing_content = []
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            existing_content = f.readlines()
    
    # 将新内容添加到文件开头
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
        if existing_content:
            f.write('\n' + '---\n' + ''.join(existing_content))

def main():
    images = read_images()
    updates = []
    images_status = {}

    for image in images:
        current_time = get_docker_hub_info(image)
        if not current_time:
            continue

        last_time = get_last_updated(image)
        is_updated = False
        
        if not last_time or parser.parse(current_time) > parser.parse(last_time):
            updates.append(f"镜像 {image} 有更新\n上次更新时间: {last_time}\n当前更新时间: {current_time}")
            save_last_updated(image, current_time)
            is_updated = True
            
        images_status[image] = {
            'current_time': current_time,
            'last_time': last_time,
            'updated': is_updated
        }

    # 生成changelog
    generate_changelog(images_status)

    # 发送通知（如果配置了的话）
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    webhook_url = os.getenv('WEBHOOK_URL')  # 提取 WEBHOOK_URL
    logging.info(f"Webhook URL: {webhook_url}")  # 临时打印日志
    if updates and webhook_url:
        notification = "\n\n".join(updates)
        send_wecom_notification(webhook_url, notification)
    
    if updates and os.getenv('EMAIL_TO'):
        notification = "\n\n".join(updates)
        send_email_notification(os.getenv('EMAIL_TO'), notification)

if __name__ == "__main__":
    main()
