import streamlit as st
import requests
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="YT DOWNLOADER",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONSTANTS ---
BACKEND_URL = "http://yt-backend:5000"


# --- SESSION STATE ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Video" # Default to Video
if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'sidebar_open' not in st.session_state:
    st.session_state.sidebar_open = False  # Closed by default
if 'playing_file' not in st.session_state:
    st.session_state.playing_file = None
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None

# --- DYNAMIC BACKGROUNDS ---
bg_video = "radial-gradient(circle at 50% 10%, #032411 0%, #163417 60%, #0e602c 100%)"
bg_audio = "radial-gradient(circle at 50% 10%, #4a0025 0%, #240b36 60%, #1a1a2e 100%)"

# --- CSS STYLING ---
def inject_css(current_mode):
    active_bg = bg_video if current_mode == "Video" else bg_audio

    st.markdown(f"""
    <style>
        /* 1. BACKGROUND & RESET */
        .stApp {{
            background: {active_bg};
            transition: background 0.8s ease-in-out;
            background-attachment: fixed;
            color: white;
        }}
        header, footer, .stDeployButton {{display: none !important;}}

        /* 2. PREMIUM SEARCH BAR - ABSOLUTE MASTERPIECE */
        
        /* Hide ALL Streamlit's default containers and backgrounds */
        .stTextInput {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        
        .stTextInput > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }}
        
        /* COMPLETELY HIDE the Streamlit label - this was causing duplicate placeholder */
        .stTextInput > label {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            position: absolute !important;
            background: transparent !important;
            border: none !important;
        }}
        
        .stTextInput [data-baseweb="base-input"] {{
            background: transparent !important;
            border: none !important;
        }}
        
        /* Container wrapper for the search bar */
        .stTextInput > div > div {{
            position: relative;
            max-width: 800px;
            margin: -10px auto 0 auto;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            min-height: 60px;
        }}
        
        /* Main input styling - ABSOLUTE positioning to cover everything */
        .stTextInput > div > div > input {{
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            background: #1a1a2e !important; /* Opaque background to hide the ghost */
            backdrop-filter: none;
            border: 2px solid rgba(255, 255, 255, 0.15);
            border-radius: 25px;
            color: white;
            padding: 20px 60px 20px 40px;
            font-size: 17px;
            font-weight: 500;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            outline: none !important;
            box-shadow: none !important;
            z-index: 10;
        }}
        
        /* Animated gradient border - matches input exactly */
        .stTextInput > div > div::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, 
                #00C9FF 0%, 
                #92FE9D 25%, 
                #FF6B9D 50%, 
                #C471ED 75%, 
                #00C9FF 100%);
            background-size: 300% 300%;
            border-radius: 25px;
            z-index: 0;
            opacity: 0;
            animation: gradientRotate 4s ease infinite;
            transition: opacity 0.4s ease;
            padding: 2px;
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
        }}
        
        @keyframes gradientRotate {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        /* Placeholder styling */
        .stTextInput > div > div > input::-webkit-input-placeholder {{
            color: rgba(255, 255, 255, 0.5);
            font-weight: 400;
            letter-spacing: 0.5px;
        }}
        
        /* Hover state - activate gradient border */
        .stTextInput > div > div:hover::before {{
            opacity: 0.6;
        }}
        
        .stTextInput > div > div > input:hover {{
            background: linear-gradient(135deg, 
                #232336 0%, 
                #1a1a2e 100%) !important;
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 12px 40px rgba(0, 201, 255, 0.2),
                        0 0 40px rgba(146, 254, 157, 0.15),
                        inset 0 0 0 1px rgba(255, 255, 255, 0.2);
        }}
        
        /* Focus state - full gradient border + glow */
        .stTextInput > div > div:focus-within::before {{
            opacity: 1;
        }}
        
        .stTextInput > div > div > input:focus {{
            background: linear-gradient(135deg, 
                #2a2a3e 0%, 
                #202033 100%) !important;
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 15px 50px rgba(0, 201, 255, 0.4),
                        0 0 60px rgba(146, 254, 157, 0.3),
                        0 0 100px rgba(255, 107, 157, 0.2),
                        inset 0 0 30px rgba(0, 201, 255, 0.1),
                        inset 0 0 0 1px rgba(255, 255, 255, 0.3);
            outline: none !important;
        }}
        
        /* Pulsing glow animation on focus */
        .stTextInput > div > div:focus-within {{
            animation: pulseGlow 2s ease-in-out infinite;
        }}
        
        @keyframes pulseGlow {{
            0%, 100% {{
                filter: drop-shadow(0 0 20px rgba(0, 201, 255, 0.4));
            }}
            50% {{
                filter: drop-shadow(0 0 40px rgba(146, 254, 157, 0.6));
            }}
        }}
        
        
        /* Search icon - RIGHT side with animations */
        .stTextInput > div > div::after {{
            content: '🔍';
            position: absolute;
            right: 25px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 22px;
            z-index: 10;
            opacity: 0.7;
            transition: all 0.3s ease;
            pointer-events: none;
        }}
        
        .stTextInput > div > div:hover::after {{
            opacity: 1;
            transform: translateY(-50%) scale(1.1);
            filter: drop-shadow(0 0 10px rgba(0, 201, 255, 0.8));
        }}
        
        .stTextInput > div > div:focus-within::after {{
            opacity: 1;
            transform: translateY(-50%) scale(1.15) rotate(90deg);
            filter: drop-shadow(0 0 15px rgba(146, 254, 157, 0.9));
        }}
        
        /* Remove validation styles */
        .stTextInput > div > div > input:invalid,
        .stTextInput > div > div > input:valid {{
            box-shadow: 0 15px 50px rgba(0, 201, 255, 0.4),
                        0 0 60px rgba(146, 254, 157, 0.3),
                        0 0 100px rgba(255, 107, 157, 0.2),
                        inset 0 0 30px rgba(0, 201, 255, 0.1),
                        inset 0 0 0 1px rgba(255, 255, 255, 0.3) !important;
            outline: none !important;
        }}



        /* 3. CARD CONTAINER */
        div[data-testid="stVerticalBlock"] > div[style*="background-color"] {{
            background: rgba(20, 20, 30, 0.6);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.05);
        }}

        /* 4. BUTTON STYLING WITH GLOW EFFECTS */
        .stButton > button {{
            width: 100%;
            border-radius: 12px;
            font-weight: 600;
            padding: 12px;
            transition: all 0.3s ease;
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            color: black;
            border: none;
            box-shadow: 0 4px 15px rgba(0, 201, 255, 0.4);
        }}
        
        /* Glow on hover for primary buttons */
        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 0 25px rgba(0, 201, 255, 0.6),
                        0 0 40px rgba(146, 254, 157, 0.4),
                        0 4px 20px rgba(0, 201, 255, 0.5);
            transform: translateY(-2px);
        }}
        
        .stButton > button[kind="secondary"] {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #aaa;
        }}
        
        /* Glow on hover for secondary buttons (quality buttons) */
        .stButton > button[kind="secondary"]:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(0, 201, 255, 0.4);
            color: white;
            box-shadow: 0 0 20px rgba(0, 201, 255, 0.5),
                        0 0 35px rgba(146, 254, 157, 0.3);
            transform: translateY(-2px);
        }}
        div[data-testid="column"] {{
            padding: 0px 5px;
        }}


        /* CUSTOM SIDEBAR WITH HOVER TRIGGER - PREMIUM EDITION */
        .custom-sidebar {{
            position: fixed;
            top: 0;
            right: -380px;
            width: 380px;
            height: 100vh;
            background: linear-gradient(180deg, 
                rgba(15, 15, 35, 0.98) 0%, 
                rgba(25, 15, 45, 0.98) 50%,
                rgba(15, 25, 50, 0.98) 100%);
            backdrop-filter: blur(30px) saturate(180%);
            border-left: 2px solid transparent;
            background-clip: padding-box;
            overflow-y: auto;
            overflow-x: hidden;
            z-index: 9999;
            transition: right 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: -10px 0 50px rgba(0, 0, 0, 0.8),
                        -5px 0 100px rgba(0, 201, 255, 0.1);
            padding: 25px 20px;
        }}
        
        /* Animated border gradient */
        .custom-sidebar::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -2px;
            width: 2px;
            height: 100%;
            background: linear-gradient(180deg, 
                #00C9FF 0%, 
                #92FE9D 50%, 
                #00C9FF 100%);
            background-size: 100% 200%;
            animation: borderFlow 3s linear infinite;
        }}
        
        @keyframes borderFlow {{
            0% {{ background-position: 0% 0%; }}
            100% {{ background-position: 0% 200%; }}
        }}
        
        /* Custom scrollbar */
        .custom-sidebar::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .custom-sidebar::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }}
        
        .custom-sidebar::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, #00C9FF, #92FE9D);
            border-radius: 10px;
            transition: all 0.3s ease;
        }}
        
        .custom-sidebar::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(180deg, #92FE9D, #00C9FF);
            box-shadow: 0 0 10px rgba(0, 201, 255, 0.5);
        }}
        
        /* Hover zone trigger on right edge */
        .hover-trigger {{
            position: fixed;
            top: 0;
            right: 0;
            width: 25px;
            height: 100vh;
            z-index: 10000;
            cursor: pointer;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(0, 201, 255, 0.05) 100%);
            transition: all 0.3s ease;
        }}
        
        .hover-trigger:hover {{
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(0, 201, 255, 0.15) 100%);
            box-shadow: -5px 0 20px rgba(0, 201, 255, 0.2);
        }}
        
        /* Show sidebar when hovering over trigger OR sidebar itself */
        .hover-trigger:hover ~ .custom-sidebar,
        .custom-sidebar:hover {{
            right: 0px;
        }}
        
        /* Sidebar header with gradient and glow - NO ICON */
        .sidebar-header {{
            color: #fff;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 25px;
            padding: 20px;
            margin: -25px -20px 25px -20px;
            background: linear-gradient(135deg, 
                rgba(0, 201, 255, 0.2) 0%, 
                rgba(146, 254, 157, 0.2) 100%);
            border-bottom: 2px solid rgba(0, 201, 255, 0.3);
            text-align: center;
            letter-spacing: 1px;
            text-shadow: 0 0 20px rgba(0, 201, 255, 0.5),
                         0 0 40px rgba(146, 254, 157, 0.3);
            animation: headerGlow 2s ease-in-out infinite alternate;
            position: relative;
            overflow: hidden;
        }}
        
        .sidebar-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, 
                transparent 30%, 
                rgba(255, 255, 255, 0.1) 50%, 
                transparent 70%);
            animation: shimmer 3s infinite;
        }}
        
        @keyframes headerGlow {{
            0% {{ box-shadow: 0 0 20px rgba(0, 201, 255, 0.3); }}
            100% {{ box-shadow: 0 0 40px rgba(146, 254, 157, 0.5); }}
        }}
        
        @keyframes shimmer {{
            0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
            100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
        }}
        
        /* Premium file cards */
        .file-card {{
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.08) 0%, 
                rgba(255, 255, 255, 0.03) 100%);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 14px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            animation: slideIn 0.5s ease forwards;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }}
        
        /* Gradient overlay on hover */
        .file-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(0, 201, 255, 0.1) 50%, 
                transparent 100%);
            transition: left 0.5s ease;
        }}
        
        .file-card:hover::before {{
            left: 100%;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(30px) scale(0.95);
            }}
            to {{
                opacity: 1;
                transform: translateX(0) scale(1);
            }}
        }}
        
        .file-card:hover {{
            background: linear-gradient(135deg, 
                rgba(0, 201, 255, 0.15) 0%, 
                rgba(146, 254, 157, 0.15) 100%);
            border-color: rgba(0, 201, 255, 0.5);
            transform: translateX(-8px) scale(1.02);
            box-shadow: 0 8px 30px rgba(0, 201, 255, 0.3),
                        0 0 50px rgba(146, 254, 157, 0.2),
                        inset 0 0 20px rgba(255, 255, 255, 0.05);
        }}
        
        /* File icon with gradient glow */
        .file-icon {{
            font-size: 32px;
            margin-right: 12px;
            filter: drop-shadow(0 0 10px rgba(0, 201, 255, 0.5));
            transition: all 0.3s ease;
        }}
        
        .file-card:hover .file-icon {{
            transform: scale(1.2) rotate(5deg);
            filter: drop-shadow(0 0 20px rgba(146, 254, 157, 0.8));
        }}
        
        .file-name {{
            color: #fff;
            font-weight: 600;
            font-size: 15px;
            word-break: break-word;
            line-height: 1.4;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .file-meta {{
            color: #aaa;
            font-size: 12px;
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .file-info {{
            margin: 8px 0;
            color: #888;
            font-size: 11px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        /* Action buttons with premium styling */
        .action-buttons {{
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }}
        
        .action-btn {{
            background: linear-gradient(135deg, 
                rgba(0, 201, 255, 0.2) 0%, 
                rgba(146, 254, 157, 0.2) 100%);
            border: 1px solid rgba(0, 201, 255, 0.4);
            border-radius: 8px;
            padding: 8px 14px;
            color: #fff !important;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-decoration: none !important;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            position: relative;
            overflow: hidden;
        }}
        
        .action-btn::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            transform: translate(-50%, -50%);
            transition: width 0.4s ease, height 0.4s ease;
        }}
        
        .action-btn:hover::before {{
            width: 200px;
            height: 200px;
        }}
        
        .action-btn:hover {{
            background: linear-gradient(135deg, 
                rgba(0, 201, 255, 0.4) 0%, 
                rgba(146, 254, 157, 0.4) 100%);
            border-color: rgba(0, 201, 255, 0.8);
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 5px 20px rgba(0, 201, 255, 0.4),
                        0 0 30px rgba(146, 254, 157, 0.3);
            color: #fff !important;
        }}
        
        .action-btn.delete {{
            background: linear-gradient(135deg, 
                rgba(255, 107, 107, 0.2) 0%, 
                rgba(255, 50, 50, 0.2) 100%);
            border-color: rgba(255, 107, 107, 0.4);
        }}
        
        .action-btn.delete:hover {{
            background: linear-gradient(135deg, 
                rgba(255, 107, 107, 0.4) 0%, 
                rgba(255, 50, 50, 0.4) 100%);
            border-color: rgba(255, 107, 107, 0.8);
            box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4),
                        0 0 30px rgba(255, 50, 50, 0.3);
        }}
        
        /* Empty state styling */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }}
        
        .empty-state-icon {{
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.5;
            animation: float 3s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
        }}


    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
def fetch_metadata():
    url = st.session_state.url_input
    if not url: return
    try:
        # POST request to the /info endpoint for metadata
        r = requests.post(f"{BACKEND_URL}/info", json={"url": url})

        if r.status_code == 200:
            st.session_state.video_data = r.json()
            st.session_state.task_id = None
        else:
            st.session_state.video_data = None
            st.error("❌ Could not fetch video info. Check your URL.")
    except requests.exceptions.ConnectionError:
        st.session_state.video_data = None
        st.error("❌ Cannot connect to Backend service. Check your Docker network.")
    except Exception as e:
        st.session_state.video_data = None
        st.error(f"❌ Error: {e}")

def trigger_download(type_mode, quality):
    try:
        payload = {
            "url": st.session_state.url_input,
            "type": type_mode,
            "quality": quality
        }
        # POST request to the /download endpoint to start the job
        r = requests.post(f"{BACKEND_URL}/download", json=payload)
        if r.status_code == 202:
            st.session_state.task_id = r.json()['task_id']
        else:
             st.error(f"Download start failed. Code: {r.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Backend service.")

def set_mode(mode):
    st.session_state.view_mode = mode

def toggle_sidebar():
    """Toggle sidebar state."""
    st.session_state.sidebar_open = not st.session_state.sidebar_open

def display_sidebar():
    """Display download history with hover trigger."""
    # Fetch files
    files_html = ""
    try:
        r = requests.get(f"{BACKEND_URL}/files", timeout=2)
        if r.status_code == 200:
            data = r.json()
            files = data.get('files', [])
            
            if files:
                from datetime import datetime
                
                for i, file in enumerate(files):
                    # Determine icon based on file extension
                    ext = file.get('extension', '')
                    if ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                        icon = "🎞️"
                        file_type = "Video"
                    elif ext in ['.mp3', '.m4a', '.wav', '.flac', '.ogg']:
                        icon = "🎧"
                        file_type = "Audio"
                    else:
                        icon = "📄"
                        file_type = "File"
                    
                    # Format timestamp
                    mod_time = datetime.fromtimestamp(file['modified'])
                    date_str = mod_time.strftime("%b %d, %Y")
                    time_str = mod_time.strftime("%H:%M")
                    
                    # Add delay for staggered animation
                    delay = i * 0.05
                    
                    # Build file card HTML
                    files_html += f"""
<div class="file-card" style="animation-delay: {delay}s;">
    <div style="display: flex; align-items: center; margin-bottom: 8px;">
        <span class="file-icon">{icon}</span>
        <div style="flex: 1;">
            <div class="file-name">{file['name']}</div>
            <div class="file-meta">{file_type} • {file['size']}</div>
        </div>
    </div>
    <div class="file-info">
        <div style="color: #888; font-size: 11px;">
            📅 {date_str} at {time_str}
        </div>
    </div>
</div>
"""
            else:
                files_html = '''
<div class="empty-state">
    <div class="empty-state-icon">📥</div>
    <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">No Downloads Yet</div>
    <div style="font-size: 13px; opacity: 0.7;">Your downloaded files will appear here</div>
</div>
'''
        else:
            files_html = '''
<div class="empty-state">
    <div class="empty-state-icon">⚠️</div>
    <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px; color: #ff6b6b;">Could Not Load Files</div>
    <div style="font-size: 13px; opacity: 0.7;">Please check backend connection</div>
</div>
'''
    except requests.exceptions.ConnectionError:
        files_html = '''
<div class="empty-state">
    <div class="empty-state-icon">🔌</div>
    <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px; color: #ff6b6b;">Backend Not Connected</div>
    <div style="font-size: 13px; opacity: 0.7;">Please start the backend service</div>
</div>
'''
    except Exception as e:
        files_html = f'''
<div class="empty-state">
    <div class="empty-state-icon">❌</div>
    <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px; color: #ff6b6b;">Error Occurred</div>
    <div style="font-size: 13px; opacity: 0.7;">{str(e)}</div>
</div>
'''
    
    # Render hover trigger and sidebar
    st.markdown("""
<div class="hover-trigger"></div>
<div class="custom-sidebar" id="customSidebar">
    <div class="sidebar-header">
        <span style="position: relative; z-index: 1;">DOWNLOAD HISTORY</span>
    </div>
""" + files_html + """
</div>
""", unsafe_allow_html=True)




# --- UI LAYOUT ---

# 1. INJECT CSS
inject_css(st.session_state.view_mode)

# 2. DISPLAY SIDEBAR
display_sidebar()

# 3. ANIMATED TITLE
import streamlit.components.v1 as components

components.html("""
<style>
    .typewriter-container {
        text-align: center;
        padding: 30px 0 20px 0;
        min-height: 80px;
    }
    
    .typewriter-text {
        font-size: 42px;
        font-weight: 700;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
    }
    
    .cursor {
        display: inline-block;
        width: 3px;
        height: 42px;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        margin-left: 5px;
        animation: blink 0.7s infinite;
        vertical-align: middle;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
</style>

<div class="typewriter-container">
    <span class="typewriter-text" id="typewriter"></span>
    <span class="cursor"></span>
</div>

<script>
    const texts = [
        "YOUTUBE DOWNLOADER",
        "منزل فيديوهات يوتيوب"
    ];
    
    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typewriterElement = document.getElementById('typewriter');
    
    function type() {
        const currentText = texts[textIndex];
        
        if (isDeleting) {
            typewriterElement.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
        } else {
            typewriterElement.textContent = currentText.substring(0, charIndex + 1);
            charIndex++;
        }
        
        let typeSpeed = isDeleting ? 50 : 100;
        
        if (!isDeleting && charIndex === currentText.length) {
            typeSpeed = 2000;
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            textIndex = (textIndex + 1) % texts.length;
            typeSpeed = 500;
        }
        
        setTimeout(type, typeSpeed);
    }
    
    setTimeout(type, 1000);
</script>
""", height=120)

# 2. INPUT (On change triggers metadata fetch)
st.text_input(
    "url",
    placeholder="Paste YouTube Link...",
    key="url_input",
    label_visibility="collapsed",
    on_change=fetch_metadata
)

# 3. MAIN AREA
if st.session_state.video_data:
    data = st.session_state.video_data

    # Glass Card Container
    with st.container():
        # Top Info
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(data.get('thumbnail', 'https://via.placeholder.com/150'), use_container_width=True)
        with c2:
            st.markdown(f"### {data.get('title', 'Unknown Title')}")
            st.caption(f"⏱️ {data.get('duration', 'N/A')}")

        st.write("")

        # 4. MODE SELECTOR (Button Tabs)
        type_col1, type_col2 = st.columns(2)

        with type_col1:
            btn_type = "primary" if st.session_state.view_mode == "Video" else "secondary"
            if st.button("Video Formats", type=btn_type, use_container_width=True):
                set_mode("Video")
                st.rerun()

        with type_col2:
            btn_type = "primary" if st.session_state.view_mode == "Audio" else "secondary"
            if st.button("Audio Formats", type=btn_type, use_container_width=True):
                set_mode("Audio")
                st.rerun()

        st.write("")

        # 5. CONDITIONAL CONTENT
        if st.session_state.view_mode == "Video":
            st.markdown("#####  Select Resolution")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💎 BEST", use_container_width=True): trigger_download('video', 'max')
            with col2:
                if st.button("⚡ 1080p", use_container_width=True): trigger_download('video', '1080p')
            with col3:
                if st.button("📱 720p", use_container_width=True): trigger_download('video', '720p')

        else: # Audio Mode
            st.markdown("##### 🎵 Select Bitrate")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💎 BEST", use_container_width=True): trigger_download('audio', '320k')
            with col2:
                if st.button("Normal (128k)", use_container_width=True): trigger_download('audio', '128k')

    # 6. PROGRESS BAR
    if st.session_state.task_id:
        st.write("")
        
        with st.status("🚀 Downloading...", expanded=True) as status:
            p_bar = st.progress(0)
            lbl = st.empty()

            check_count = 0
            max_checks = 120

            while check_count < max_checks:
                time.sleep(0.5)
                check_count += 1
                try:
                    # GET request to the /status endpoint
                    r = requests.get(f"{BACKEND_URL}/status/{st.session_state.task_id}")
                    d = r.json()
                    state = d.get('status')

                    p_bar.progress(int(d.get('progress', 0)))
                    lbl.caption(f"Status: {state} | Speed: {d.get('speed')}")

                    if state == 'finished':
                        status.update(label="✅ Complete!", state="complete", expanded=False)
                        st.balloons()
                        st.session_state.task_id = None
                        break
                    if 'error' in state:
                        status.update(label="❌ Error", state="error")
                        st.error(f"Download failed: {state}")
                        st.session_state.task_id = None
                        break
                except requests.exceptions.ConnectionError:
                    lbl.caption("❌ Lost connection to the backend...")
                    break

            if st.session_state.task_id and check_count >= max_checks:
                status.update(label="⚠️ Timeout", state="error")
                st.error("Status check timed out. Please check your Docker logs.")
