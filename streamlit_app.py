import streamlit as st
import time
import threading
import hashlib
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import database as db

st.set_page_config(
    page_title="E2E BY ZALIM BOSS",
    page_icon="😈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== ROYAL DARK THEME CSS ======================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Great+Vibes&family=Playfair+Display:wght@400;700&display=swap');
    * { font-family: 'Playfair Display', serif; }
    .stApp {
        background-image: linear-gradient(rgba(20, 0, 40, 0.88), rgba(40, 0, 80, 0.78)),
                          url('https://i.ibb.co/0mQfX0b/dark-royal-purple-velvet-texture.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main .block-container {
        background: rgba(30, 10, 60, 0.68);
        backdrop-filter: blur(12px);
        border-radius: 22px;
        padding: 32px;
        border: 2px solid rgba(255, 215, 0, 0.38);
        box-shadow: 0 12px 45px rgba(255, 215, 0, 0.18);
    }
    .footer {
        background: rgba(30, 10, 60, 0.75);
        border-top: 3px solid #b8860b;
        color: #d4af37;
        font-family: 'Great Vibes', cursive;
        font-size: 1.5rem;
        padding: 2.8rem;
        text-align: center;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

# ====================== SELENIUM FUNCTIONS ======================
def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed!', automation_state)
        return driver
    except Exception as e:
        log_message(f'Browser setup failed: {e}', automation_state)
        raise e

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(8)

    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="Message" i]',
        '[role="textbox"][contenteditable="true"]',
        'textarea'
    ]

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    element.click()
                    time.sleep(0.5)
                    return element
                except:
                    continue
        except:
            continue
    return None

def get_next_message(messages, automation_state):
    if not messages:
        return 'Hello!'
    msg = messages[automation_state.message_rotation_index % len(messages)]
    automation_state.message_rotation_index += 1
    return msg

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        driver = setup_browser(automation_state)

        driver.get('https://www.facebook.com/')
        time.sleep(10)

        # Add cookies if provided
        if config.get('cookies') and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            cookie_list = config['cookies'].split(';')
            for cookie in cookie_list:
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    try:
                        driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
                    except:
                        pass

        chat_id = config.get('chat_id', '').strip()
        if chat_id:
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            driver.get('https://www.facebook.com/messages')
        time.sleep(15)

        message_input = find_message_input(driver, process_id, automation_state)
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0

        delay = int(config.get('delay', 30))
        messages_list = [msg.strip() for msg in config.get('messages', 'Hello!').split('\n') if msg.strip()]
        messages_sent = 0

        while automation_state.running:
            base_message = get_next_message(messages_list, automation_state)
            full_message = f"{config.get('name_prefix', '')} {base_message}".strip()

            try:
                driver.execute_script("""
                    const el = arguments[0];
                    const text = arguments[1];
                    el.focus();
                    el.click();
                    el.textContent = text;
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                """, message_input, full_message)

                time.sleep(1)

                # Try Enter key
                driver.execute_script("""
                    const el = arguments[0];
                    el.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
                """, message_input)

                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f'{process_id}: Sent #{messages_sent} → {full_message[:40]}...', automation_state)
                time.sleep(delay)

            except Exception as e:
                log_message(f'{process_id}: Send error: {str(e)[:80]}', automation_state)
                time.sleep(5)

        log_message(f'{process_id}: Automation stopped. Total sent: {messages_sent}', automation_state)

    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def start_automation(user_config, user_id):
    state = st.session_state.automation_state
    if state.running:
        st.warning("Automation already running!")
        return
    state.running = True
    state.message_count = 0
    state.logs = []
    state.message_rotation_index = 0
    db.set_automation_running(user_id, True)

    thread = threading.Thread(
        target=send_messages,
        args=(user_config, state, user_id),
        daemon=True
    )
    thread.start()
    st.success("🚀 Automation Started by ZALIM BOSS 😈")

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)
    st.success("⛔ Automation Stopped")

# ====================== LOGIN & MAIN APP ======================
def login_page():
    st.markdown("""
    <div style="text-align:center; padding:30px 0;">
        <h1 style="font-size:3rem;">😈 ZALIM BOSS OFFLINE E2EE 😈</h1>
        <p style="font-size:1.4rem; color:#d4af37;">səvən bıllıon smılə's ın ʈhıs world buʈ ɣour's ıs mɣ fαvourıʈəs___😈</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👑 Login", "👑 Sign Up"])

    with tab1:
        st.markdown("### Welcome Back Boss!")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", key="login_pass", type="password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success(f"😈 Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("❌ Wrong Username or Password!")
            else:
                st.warning("Please fill both fields")

    with tab2:
        st.markdown("### Create New Account")
        new_user = st.text_input("Choose Username", key="new_user")
        new_pass = st.text_input("Choose Password", key="new_pass", type="password")
        confirm_pass = st.text_input("Confirm Password", key="confirm_pass", type="password")
        
        if st.button("Sign Up", use_container_width=True):
            if new_user and new_pass and confirm_pass:
                if new_pass == confirm_pass:
                    success, msg = db.create_user(new_user, new_pass)
                    if success:
                        st.success(msg)
                        st.info("Now login with your credentials")
                    else:
                        st.error(msg)
                else:
                    st.error("Passwords do not match!")
            else:
                st.warning("All fields are required")

def main_app():
    st.markdown(f"""
    <div style="text-align:center;">
        <h1>😈 ZALIM BOSS E2E OFFLINE 😈</h1>
        <p>Welcome, <b>{st.session_state.username}</b> 😈</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 😈 {st.session_state.username}")
        st.markdown(f"**User ID:** {st.session_state.user_id}")
        if st.button("Logout", use_container_width=True):
            stop_automation(st.session_state.user_id)
            st.session_state.logged_in = False
            st.rerun()

    config = db.get_user_config(st.session_state.user_id)
    if not config:
        st.error("Config not found")
        return

    tab1, tab2 = st.tabs(["⚙️ Configuration", "🚀 Automation"])

    with tab1:
        chat_id = st.text_input("Chat ID / Thread ID", value=config.get('chat_id', ''))
        name_prefix = st.text_input("Name Prefix", value=config.get('name_prefix', ''))
        delay = st.number_input("Delay (seconds)", min_value=5, value=config.get('delay', 30))
        messages = st.text_area("Messages (one per line)", value=config.get('messages', ''), height=150)
        cookies = st.text_area("Cookies (optional)", value=config.get('cookies', ''), height=100)

        if st.button("💾 Save Configuration", use_container_width=True):
            db.update_user_config(st.session_state.user_id, chat_id, name_prefix, delay, cookies, messages)
            st.success("Configuration Saved Successfully!")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Sending", use_container_width=True, type="primary"):
                start_automation(config, st.session_state.user_id)
        with col2:
            if st.button("⛔ Stop Sending", use_container_width=True):
                stop_automation(st.session_state.user_id)

        status = "🟢 Running" if st.session_state.automation_state.running else "🔴 Stopped"
        st.metric("Status", status)
        st.metric("Messages Sent", st.session_state.automation_state.message_count)

        st.subheader("Live Logs")
        for log in reversed(st.session_state.automation_state.logs[-20:]):
            st.text(log)

# ====================== RUN THE APP ======================
if not st.session_state.logged_in:
    login_page()
else:
    main_app()

st.markdown('<div class="footer">Made with ❤️ by ZALIM BOSS 😈 | © 2026</div>', unsafe_allow_html=True)
