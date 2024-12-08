import os
import json
import requests
from datetime import datetime
from dateutil import parser
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def read_images():
    # 获取脚本所在目录的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录路径
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    # 构建 images.txt 的完整路径
    images_file = os.path.join(root_dir, 'images.txt')
    with open(images_file, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

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
    if updates and os.getenv('WEBHOOK_URL'):
        notification = "\n\n".join(updates)
        send_wecom_notification(os.getenv('WEBHOOK_URL'), notification)
    
    if updates and os.getenv('EMAIL_TO'):
        notification = "\n\n".join(updates)
        send_email_notification(os.getenv('EMAIL_TO'), notification)

if __name__ == "__main__":
    main()
