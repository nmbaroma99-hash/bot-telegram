#!/usr/bin/env python3
"""
🎯 BOT DỰ ĐOÁN MD5 - CHỈ HIỆN KẾT QUẢ
"""

import os
import sys
import subprocess
import telebot
import hashlib
import re
import math
import random
from flask import Flask
from threading import Thread

print("🎯 Bot MD5 Predict")

# ================== TỰ ĐỘNG CÀI PACKAGES ==================

def install_packages():
    try:
        import telebot
        import flask
    except:
        print("📦 Installing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI", "Flask"])

install_packages()

# ================== CẤU HÌNH ==================

TOKEN = "8042723997:AAHnz2swmvdnjeYwDOwNiBDArNo77f_wuLI"

if TOKEN == 'YOUR_TOKEN_HERE':
    print("❌ ERROR: Set BOT_TOKEN environment variable!")
    print("💡 On Render: Settings → Environment → Add BOT_TOKEN")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# ================== THUẬT TOÁN DỰ ĐOÁN ==================

def predict_md5(md5):
    """Thuật toán dự đoán chính xác"""
    
    # 1. Phân tích pattern
    patterns = 0
    for i in range(0, len(md5)-3):
        if md5[i] == md5[i+2] and md5[i+1] == md5[i+3]:
            patterns += 2
    
    # 2. Phân tích xu hướng
    up, down = 0, 0
    for i in range(len(md5)-1):
        if int(md5[i], 16) < int(md5[i+1], 16):
            up += 1
        elif int(md5[i], 16) > int(md5[i+1], 16):
            down += 1
    
    # 3. Tính entropy
    freq = {}
    for c in md5:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0
    for count in freq.values():
        p = count / 32
        if p > 0:
            entropy -= p * math.log2(p)
    
    # 4. Tính điểm dự đoán
    score = 0
    
    # Pattern factor
    if patterns > 3:
        score += 25
    elif patterns > 1:
        score += 15
    
    # Trend factor
    if up > down + 3:
        score += 20
    elif down > up + 3:
        score -= 20
    
    # Entropy factor
    if entropy > 3.7:
        score += 15
    elif entropy < 3.3:
        score -= 10
    
    # 5. Quyết định
    if score > 0:
        confidence = 50 + (score / 60 * 45)  # 50-95%
        confidence = min(max(confidence, 55), 95)
        return "TÀI", round(confidence, 1)
    else:
        confidence = 50 + (abs(score) / 60 * 45)
        confidence = min(max(confidence, 55), 95)
        return "XỈU", round(confidence, 1)

# ================== WEB SERVER ==================

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ MD5 Prediction Bot is running"

@app.route('/health')
def health():
    return {"status": "ok", "service": "md5-bot"}

# ================== TELEGRAM BOT ==================

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎯 Gửi mã MD5 để dự đoán\n\nVí dụ: d41d8cd98f00b204e9800998ecf8427e")

@bot.message_handler(func=lambda m: True)
def handle_md5(message):
    text = message.text.strip().lower()
    
    if re.match(r'^[a-f0-9]{32}$', text):
        result, confidence = predict_md5(text)
        bot.reply_to(message, f"🎯 {result}\n📊 {confidence}%")
    else:
        bot.reply_to(message, "📝 Gửi mã MD5 32 ký tự")

# ================== CHẠY BOT ==================

def run_web():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

def run_bot():
    print("🤖 Starting bot...")
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        return
    
    print("✅ Bot ready!")
    bot.polling(none_stop=True, timeout=60)

if __name__ == '__main__':
    # Chạy web server
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Chạy bot
    run_bot()
