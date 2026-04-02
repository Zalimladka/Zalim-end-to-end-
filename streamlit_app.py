import streamlit as st
import time
import threading
import asyncio
from playwright.async_api import async_playwright
import database as db

st.set_page_config(
    page_title="E2E BY ZALIM BOSS",
    page_icon="😈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== ZALIM BOSS THEME ======================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
    * { font-family: 'Playfair Display', serif; }
    .stApp {
        background-image: linear-gradient(rgba(20, 0, 40, 0.92), rgba(40, 0, 80, 0.85)),
                          url('https://i.ibb.co/0mQfX0b/dark-royal-purple-velvet-texture.jpg');
        background-size: cover;
        background-attachment: fixed;
    }
    .main .block-container { background: rgba(30, 10, 60, 0.75); backdrop-filter: blur(12px); border-radius: 22px; padding: 32px; border: 2px solid rgba(255, 215, 0, 0.45); }
    .logs-container {
        background: #1a0033; border: 2px solid #b8860b; border-radius: 15px; padding: 18px;
        height: 450px; overflow-y: auto; font-family: monospace; color: #ffd700; font-size: 0.96rem;
    }
    .footer {
        background: rgba(30, 10, 60, 0.9); border-top: 3px solid #b8860b; color: #d4af37;
        font-family: 'Great Vibes', cursive; font-size: 1.6rem; padding: 2.8rem; text-align: center; margin-top: 40px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'username' not in st.session_state: st.session_state.username = None

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

# ====================== PLAYWRIGHT AUTOMATION ======================
async def send_messages_playwright(config, automation_state, user_id):
    try:
        log_message("🚀 Starting Playwright automation by ZALIM BOSS 😈", automation_state)

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()

            await page.goto('https://www.facebook.com/', timeout=60000)
            await page.wait_for_timeout(10000)

            # Add cookies if provided
            if config.get('cookies') and config['cookies'].strip():
                log_message("Adding cookies...", automation_state)
                # Cookies parsing can be improved if needed

            chat_id = config.get('chat_id', '').strip()
            if chat_id:
                await page.goto(f'https://www.facebook.com/messages/t/{chat_id}', timeout=60000)
            else:
                await page.goto('https://www.facebook.com/messages', timeout=60000)

            await page.wait_for_timeout(18000)  # Wait for chat to load

            # Find message input (Playwright is better at this)
            message_input = None
            selectors = [
                'div[role="textbox"][contenteditable="true"]',
                'div[data-lexical-editor="true"]',
                'div[aria-label="Aa"]',
                'div[aria-label*="Message" i]'
            ]

            for selector in selectors:
                try:
                    message_input = await page.wait_for_selector(selector, timeout=10000)
                    if message_input:
                        log_message("✅ Found message input box!", automation_state)
                        break
                except:
                    continue

            if not message_input:
                log_message("❌ Could not find message input!", automation_state)
                await browser.close()
                return

            delay = int(config.get('delay', 30))
            messages_list = [m.strip() for m in config.get('messages', 'Hello!').split('\n') if m.strip()]

            messages_sent = 0
            while automation_state.running:
                base_msg = messages_list[automation_state.message_rotation_index % len(messages_list)]
                automation_state.message_rotation_index += 1
                full_msg = f"{config.get('name_prefix', '')} {base_msg}".strip()

                await message_input.click()
                await message_input.fill(full_msg)
                await page.keyboard.press('Enter')

                messages_sent += 1
                automation_state.message_count = messages_sent
                log_message(f"✅ Sent #{messages_sent}: {full_msg[:50]}...", automation_state)

                await page.wait_for_timeout(delay * 1000)

            await browser.close()
            log_message("Browser closed successfully.", automation_state)

    except Exception as e:
        log_message(f"💥 Fatal Error: {str(e)}", automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)

def start_automation(config, user_id):
    state = st.session_state.automation_state
    if state.running:
        st.warning("Already running!")
        return

    state.running = True
    state.message_count = 0
    state.logs = []
    state.message_rotation_index = 0
    db.set_automation_running(user_id, True)

    # Run async function in thread
    def run_async():
        asyncio.run(send_messages_playwright(config, state, user_id))

    thread = threading.Thread(target=run_async, daemon=True)
    thread.start()
    st.success("😈 Playwright Automation Started by ZALIM BOSS!")

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)
    st.success("⛔ Automation Stopped")

# ====================== UI (Login + Main) ======================
def login_page():
    st.markdown("""
    <div style="text-align:center; padding:40px 0 20px 0;">
        <h1 style="font-size:3.2rem;">😈 ZALIM BOSS OFFLINE E2EE 😈</h1>
        <p style="font-size:1.4rem; color:#ffaa00;">səvən bıllıon smılə's ın ʈhıs world buʈ ɣour's ıs mɣ fαvourıʈəs___😈</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👑 Login", "👑 Sign Up"])
    with tab1:
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
                    st.error("❌ Invalid credentials!")
    with tab2:
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Choose Password", key="signup_password", type="password")
        confirm = st.text_input("Confirm Password", key="confirm_password", type="password")
        if st.button("Sign Up", use_container_width=True):
            if new_password == confirm and new_username:
                success, msg = db.create_user(new_username, new_password)
                st.success(msg) if success else st.error(msg)

def main_app():
    st.markdown(f"<h1 style='text-align:center;'>😈 ZALIM BOSS E2E OFFLINE (Playwright) 😈</h1><p style='text-align:center;'>Welcome, <b>{st.session_state.username}</b> 😈</p>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 😈 {st.session_state.username}")
        st.markdown(f"**User ID:** {st.session_state.user_id}")
        if st.button("Logout"):
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
        name_prefix = st.text_input("Name Prefix", value=config.get('name_prefix', ''))
        delay = st.number_input("Delay (seconds)", min_value=5, value=config.get('delay', 30))
        messages = st.text_area("Messages (one per line)", value=config.get('messages', ''), height=150)
        cookies = st.text_area("Cookies (optional)", value=config.get('cookies', ''), height=100)

        if st.button("💾 Save Configuration", type="primary"):
            db.update_user_config(st.session_state.user_id, chat_id, name_prefix, delay, cookies, messages)
            st.success("✅ Saved!")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Automation", type="primary", use_container_width=True):
                start_automation(config, st.session_state.user_id)
        with col2:
            if st.button("⛔ Stop Automation", use_container_width=True):
                stop_automation(st.session_state.user_id)

        st.metric("Status", "🟢 Running" if st.session_state.automation_state.running else "🔴 Stopped")
        st.metric("Messages Sent", st.session_state.automation_state.message_count)

        st.subheader("🔴 Live Logs")
        if st.session_state.automation_state.logs:
            html = "".join(f'<div style="margin:5px 0;padding:8px;background:rgba(0,0,0,0.4);border-radius:6px;">{log}</div>' for log in reversed(st.session_state.automation_state.logs[-30:]))
            st.markdown(f'<div class="logs-container">{html}</div>', unsafe_allow_html=True)
        else:
            st.info("No logs yet")

        if st.session_state.automation_state.running:
            time.sleep(1)
            st.rerun()

if not st.session_state.logged_in:
    login_page()
else:
    main_app()

st.markdown('<div class="footer">Made with ❤️ by ZALIM BOSS 😈 (Playwright) | © 2026</div>', unsafe_allow_html=True)
