import os
import json
import requests
from datetime import datetime
from dateutil import parser
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ... (保持其他函数不变) ...

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
