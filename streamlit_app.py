import streamlit as st
import time
import threading
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

# ====================== ZALIM BOSS THEME CSS ======================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
    * { font-family: 'Playfair Display', serif; }
    
    .stApp {
        background-image: linear-gradient(rgba(20, 0, 40, 0.92), rgba(40, 0, 80, 0.85)),
                          url('https://i.ibb.co/0mQfX0b/dark-royal-purple-velvet-texture.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .main .block-container {
        background: rgba(30, 10, 60, 0.75);
        backdrop-filter: blur(12px);
        border-radius: 22px;
        padding: 32px;
        border: 2px solid rgba(255, 215, 0, 0.45);
    }
    
    .logs-container {
        background: #1a0033;
        border: 2px solid #b8860b;
        border-radius: 15px;
        padding: 18px;
        height: 450px;
        overflow-y: auto;
        font-family: monospace;
        color: #ffd700;
        font-size: 0.96rem;
        line-height: 1.5;
    }
    
    .log-line {
        margin: 6px 0;
        padding: 6px 10px;
        border-radius: 8px;
        background: rgba(0, 0, 0, 0.3);
    }
    
    .footer {
        background: rgba(30, 10, 60, 0.9);
        border-top: 3px solid #b8860b;
        color: #d4af37;
        font-family: 'Great Vibes', cursive;
        font-size: 1.6rem;
        padding: 2.8rem;
        text-align: center;
        margin-top: 40px;
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
        st.session_state.automation_state.logs.append(formatted_msg)

# ====================== SELENIUM FUNCTIONS ======================
def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        driver = webdriver.Chrome(options=options)
        log_message('✅ Browser launched successfully!', automation_state)
        return driver
    except Exception as e:
        log_message(f'❌ Browser setup failed: {str(e)[:120]}', automation_state)
        raise e

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input box...', automation_state)
    time.sleep(8)

    selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="Message" i]',
        '[role="textbox"]'
    ]

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                try:
                    elem.click()
                    time.sleep(0.8)
                    return elem
                except:
                    continue
        except:
            continue
    log_message(f'{process_id}: Could not find message input!', automation_state)
    return None

def get_next_message(messages, automation_state):
    if not messages:
        return "Hello!"
    msg = messages[automation_state.message_rotation_index % len(messages)]
    automation_state.message_rotation_index += 1
    return msg

def send_messages(config, automation_state, user_id):
    driver = None
    try:
        log_message("🚀 Starting automation by ZALIM BOSS 😈", automation_state)
        driver = setup_browser(automation_state)

        driver.get('https://www.facebook.com/')
        time.sleep(10)

        # Cookies
        if config.get('cookies') and config['cookies'].strip():
            log_message("Adding cookies...", automation_state)
            for cookie in config['cookies'].split(';'):
                if '=' in cookie:
                    name, value = [x.strip() for x in cookie.split('=', 1)]
                    try:
                        driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com'})
                    except:
                        pass

        chat_id = config.get('chat_id', '').strip()
        if chat_id:
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            driver.get('https://www.facebook.com/messages')
        time.sleep(15)

        message_input = find_message_input(driver, "AUTO-1", automation_state)
        if not message_input:
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return

        delay = int(config.get('delay', 30))
        messages_list = [m.strip() for m in config.get('messages', 'Hello!').split('\n') if m.strip()]

        messages_sent = 0
        while automation_state.running:
            base_msg = get_next_message(messages_list, automation_state)
            full_msg = f"{config.get('name_prefix', '')} {base_msg}".strip()

            try:
                driver.execute_script("""
                    const el = arguments[0];
                    const txt = arguments[1];
                    el.focus();
                    el.textContent = txt;
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                """, message_input, full_msg)

                time.sleep(1)
                driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));", message_input)

                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f"✅ Sent #{messages_sent}: {full_msg[:45]}...", automation_state)
                time.sleep(delay)

            except Exception as e:
                log_message(f"⚠️ Send error: {str(e)[:80]}", automation_state)
                time.sleep(5)

    except Exception as e:
        log_message(f"💥 Fatal Error: {str(e)}", automation_state)
    finally:
        if driver:
            try:
                driver.quit()
                log_message("Browser closed.", automation_state)
            except:
                pass

def start_automation(config, user_id):
    state = st.session_state.automation_state
    if state.running:
        st.warning("Automation is already running!")
        return
    
    state.running = True
    state.message_count = 0
    state.logs = []                    # Clear previous logs on new start
    state.message_rotation_index = 0
    db.set_automation_running(user_id, True)

    thread = threading.Thread(target=send_messages, args=(config, state, user_id), daemon=True)
    thread.start()
    st.success("😈 Automation Started by ZALIM BOSS!")

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)
    st.success("⛔ Automation Stopped by ZALIM BOSS")

# ====================== PAGES ======================
def login_page():
    st.markdown("""
    <div style="text-align:center; padding:40px 0 20px 0;">
        <h1 style="font-size:3.2rem;">😈 ZALIM BOSS OFFLINE E2EE 😈</h1>
        <p style="font-size:1.4rem; color:#ffaa00;">səvən bıllıon smılə's ın ʈhıs world buʈ ɣour's ıs mɣ fαvourıʈəs___😈</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👑 Login", "👑 Sign Up"])

    with tab1:
        st.markdown("### Welcome Back Boss!")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", key="login_password", type="password")
        
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
                    st.error("❌ Invalid username or password!")
            else:
                st.warning("Please enter both username and password")

    with tab2:
        st.markdown("### Create New Account")
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Choose Password", key="signup_password", type="password")
        confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password")
        
        if st.button("Sign Up", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = db.create_user(new_username, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Passwords do not match!")
            else:
                st.warning("All fields are required!")

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
        st.error("Configuration not found!")
        return

    tab1, tab2 = st.tabs(["⚙️ Configuration", "🚀 Automation"])

    with tab1:
        chat_id = st.text_input("Chat ID / Thread ID", value=config.get('chat_id', ''))
        name_prefix = st.text_input("Name Prefix (optional)", value=config.get('name_prefix', ''))
        delay = st.number_input("Delay between messages (seconds)", min_value=5, value=config.get('delay', 30))
        messages = st.text_area("Messages (one per line)", value=config.get('messages', ''), height=180)
        cookies = st.text_area("Cookies (optional - one per line)", value=config.get('cookies', ''), height=100)

        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            db.update_user_config(st.session_state.user_id, chat_id, name_prefix, delay, cookies, messages)
            st.success("✅ Configuration Saved!")

    with tab2:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if st.button("🚀 Start Automation", use_container_width=True, type="primary"):
                start_automation(config, st.session_state.user_id)
        with col2:
            if st.button("⛔ Stop Automation", use_container_width=True):
                stop_automation(st.session_state.user_id)
        with col3:
            if st.button("🗑️ Clear Logs"):
                st.session_state.automation_state.logs = []
                st.rerun()

        # Status Metrics
        status = "🟢 Running" if st.session_state.automation_state.running else "🔴 Stopped"
        st.metric("Automation Status", status)
        st.metric("Messages Sent", st.session_state.automation_state.message_count)

        # Improved Live Logs
        st.subheader("🔴 Live Logs")
        logs_container = st.container()
        
        with logs_container:
            if not st.session_state.automation_state.logs:
                st.info("No logs yet. Click Start Automation to begin.")
            else:
                log_html = ""
                for log in list(reversed(st.session_state.automation_state.logs))[-30:]:
                    if "Sent #" in log or "✅" in log:
                        color = "#00ff88"
                    elif "Error" in log or "failed" in log.lower() or "💥" in log:
                        color = "#ff5555"
                    elif "Browser" in log:
                        color = "#ffaa00"
                    else:
                        color = "#ffd700"
                    
                    log_html += f'<div class="log-line" style="color: {color};">{log}</div>'
                
                st.markdown(f'<div class="logs-container">{log_html}</div>', unsafe_allow_html=True)

        # Auto refresh when running
        if st.session_state.automation_state.running:
            time.sleep(1.2)
            st.rerun()

# ====================== APP ENTRY POINT ======================
if not st.session_state.logged_in:
    login_page()
else:
    main_app()

st.markdown('<div class="footer">Made with ❤️ by ZALIM BOSS 😈 | © 2026</div>', unsafe_allow_html=True)
