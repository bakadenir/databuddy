"""
DataBuddy UI Components — Modern Soft Design System
Reusable components with consistent styling, spacing, and visual hierarchy.
"""

import streamlit as st
import streamlit.components.v1 as components

# ═════════════════════════════════════════════════════════════════════
# DESIGN TOKENS — Color Palette, Spacing, Typography
# ═════════════════════════════════════════════════════════════════════

COLORS = {
    # Primary accents
    "primary": "#0ea5e9",      # Sky blue
    "primary_light": "#e0f2fe", # Light sky
    "secondary": "#8b5cf6",    # Purple
    "secondary_light": "#f5f3ff", # Light purple

    # Success / Warning / Error
    "success": "#10b981",      # Emerald
    "success_light": "#ecfdf5",
    "warning": "#f59e0b",      # Amber
    "warning_light": "#fffbeb",
    "error": "#ef4444",        # Red
    "error_light": "#fef2f2",

    # Info / Neutral
    "info": "#06b6d4",         # Cyan
    "info_light": "#ecfeff",
    "muted": "#64748b",        # Slate 500
    "muted_light": "#f1f5f9",  # Slate 100

    # Backgrounds
    "bg": "#f8fafc",           # Slate 50
    "bg_gradient_start": "#f0f9ff",  # Light sky tint
    "bg_gradient_end": "#faf5ff",    # Light purple tint
    "card": "#ffffff",
    "card_alt": "#f8fafc",

    # Text
    "text": "#0f172a",         # Slate 900
    "text_light": "#475569",   # Slate 600

    # Borders
    "border": "#e2e8f0",       # Slate 200
    "border_light": "#f1f5f9", # Slate 100

    # Gradients
    "gradient_primary": "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
    "gradient_warm": "linear-gradient(135deg, #f97316 0%, #eab308 100%)",
    "gradient_cool": "linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%)",
    "gradient_soft": "linear-gradient(135deg, #f0f9ff 0%, #faf5ff 100%)",
}

SPACING = {
    "xs": "0.25rem",   # 4px
    "sm": "0.5rem",    # 8px
    "md": "1rem",      # 16px
    "lg": "1.5rem",    # 24px
    "xl": "2rem",      # 32px
    "2xl": "3rem",     # 48px
}

SHADOWS = {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
}

BORDER_RADIUS = {
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "20px",
    "full": "9999px",
}

# ═════════════════════════════════════════════════════════════════════
# COMPONENT FUNCTIONS — Reusable UI Elements
# ═════════════════════════════════════════════════════════════════════

def apply_custom_css():
    """Apply modern CSS styling to the entire app."""
    # Lucide Icons
    st.markdown("""
    <script src="https://unpkg.com/lucide@latest"></script>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* Base styles */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Background gradient */
        .stApp {
            background: linear-gradient(135deg, #f0f9ff 0%, #faf5ff 50%, #f8fafc 100%);
            background-attachment: fixed;
        }

        /* Main container */
        .main .block-container,
        .block-container {
            max-width: 1400px;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
            border-right: 1px solid #334155;
        }

        section[data-testid="stSidebar"] * {
            color: #e2e8f0 !important;
        }

        section[data-testid="stSidebar"] .stPageLink a {
            color: #94a3b8 !important;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            transition: all 0.2s ease;
        }

        section[data-testid="stSidebar"] .stPageLink a:hover {
            background: rgba(255,255,255,0.08) !important;
            color: #f1f5f9 !important;
        }

        section[data-testid="stSidebar"] .stPageLink a[aria-current="page"] {
            background: rgba(99, 102, 241, 0.2) !important;
            color: #a5b4fc !important;
            font-weight: 600;
        }

        /* Metric cards */
        div[data-testid="metric-container"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
            transition: all 0.2s ease;
        }

        div[data-testid="metric-container"]:hover {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border-color: #f1f5f9;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 12px;
            transition: all 0.2s ease;
            font-weight: 600;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Dividers */
        hr {
            border-color: #e2e8f0 !important;
            border-style: solid !important;
            border-width: 1px !important;
            opacity: 0.5 !important;
        }

        /* Smooth transitions */
        * {
            transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
        }
    </style>
    """, unsafe_allow_html=True)


def render_navbar():
    """Render sidebar navigation with logo and page links."""
    apply_custom_css()

    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 0.5rem; margin-bottom: 1.5rem;">
            <div style="width: 42px; height: 42px; background: {COLORS['gradient_primary']}; border-radius: {BORDER_RADIUS['md']}; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.1rem; box-shadow: {SHADOWS['md']}; flex-shrink: 0;">DB</div>
            <div style="line-height: 1.3;">
                <div style="font-weight: 700; font-size: 1.1rem;">DataBuddy</div>
                <div style="font-size: 0.7rem; font-weight: 500; opacity: 0.6;">Shopee Analytics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation links
        st.page_link("pages/0_Home.py", label="Upload & ETL", icon="📥")
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
        st.page_link("pages/3_Chatbox.py", label="AI Chatbox", icon="💬")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---", unsafe_allow_html=True)

        st.page_link("app.py", label="← Landing Page", icon="🏠")


def card(content: str, bg_color: str | None = None, border_color: str | None = None, padding: str | None = None):
    """Render a content card with optional styling."""
    bg = bg_color or COLORS['card']
    border = border_color or COLORS['border']
    pad = padding or SPACING['lg']

    st.markdown(f"""
    <div style="background: {bg}; border: 1px solid {border}; border-radius: {BORDER_RADIUS['lg']}; padding: {pad}; box-shadow: {SHADOWS['sm']};">
        {content}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, icon: str | None = None, description: str | None = None):
    """Render a polished section header with optional icon and description."""
    icon_part = f"{icon} " if icon else ""
    desc_html = f'<p style="color: {COLORS["muted"]}; font-size: 0.9rem; margin: 0.25rem 0 0 0;">{description}</p>' if description else ''

    st.markdown(f"""
    <div style="margin: {SPACING['lg']} 0 {SPACING['md']} 0;">
        <h3 style="color: {COLORS['text']}; font-size: 1.15rem; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 0.5rem;">{icon_part}{title}</h3>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def info_box(title: str, content: str, icon: str = "ℹ️", variant: str = "info"):
    """Render an info/alert box with title and content."""
    color_map = {
        "info": (COLORS['info'], COLORS['info_light']),
        "success": (COLORS['success'], COLORS['success_light']),
        "warning": (COLORS['warning'], COLORS['warning_light']),
        "error": (COLORS['error'], COLORS['error_light']),
    }

    accent, bg = color_map.get(variant, color_map["info"])
    display_icon = icon

    st.markdown(f"""
    <div style="background: {bg}; border-left: 4px solid {accent}; border-radius: {BORDER_RADIUS['md']}; padding: 1rem 1.25rem; margin: 1rem 0;">
        <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
            <div style="font-size: 1.25rem; flex-shrink: 0;">{display_icon}</div>
            <div>
                <div style="color: {accent}; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.25rem;">{title}</div>
                <div style="color: {COLORS['text']}; font-size: 0.85rem; line-height: 1.5;">{content}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def empty_state(title: str, description: str, icon: str = "📂", link_url: str | None = None):
    """Render an empty state placeholder."""
    
    wrapper_start = f'<a href="{link_url}" target="_self" style="text-decoration: none; display: block; transition: transform 0.2s ease, box-shadow 0.2s ease;" onmouseover="this.style.transform=\'translateY(-4px)\'; this.children[0].style.borderColor=\'#0ea5e9\'" onmouseout="this.style.transform=\'translateY(0)\'; this.children[0].style.borderColor=\'{COLORS["border"]}\'">' if link_url else '<div>'
    wrapper_end = '</a>' if link_url else '</div>'
    
    hover_style = " cursor: pointer; transition: border-color 0.2s ease;" if link_url else ""

    st.markdown(f"""
    {wrapper_start}
    <div style="text-align: center; padding: 4rem 2rem; background: {COLORS['card']}; border-radius: {BORDER_RADIUS['xl']}; border: 2px dashed {COLORS['border']};{hover_style}">
        <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.6;">{icon}</div>
        <h3 style="color: {COLORS['text']}; font-size: 1.25rem; font-weight: 700; margin: 0 0 0.5rem 0;">{title}</h3>
        <p style="color: {COLORS['muted']}; font-size: 0.95rem; margin: 0;">{description}</p>
    </div>
    {wrapper_end}
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# EXPORTS — Main components to use in pages
# ═════════════════════════════════════════════════════════════════════

__all__ = [
    "COLORS",
    "SPACING",
    "SHADOWS",
    "BORDER_RADIUS",
    "apply_custom_css",
    "render_navbar",
    "card",
    "section_header",
    "info_box",
    "empty_state",
]
