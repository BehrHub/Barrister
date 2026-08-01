import streamlit as st

st.set_page_config(
    page_title="Barrister Dash · Neon Flow",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding-top: 0.8rem;
    padding-bottom: 1rem;
    max-width: 480px;
}

.status-bar {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 14px;
    margin-bottom: 4px;
    scrollbar-width: none;
}

.status-bar::-webkit-scrollbar {
    display: none;
}

.status-pill {
    background: #1c1c24;
    border: 1px solid #2e2e3a;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
    color: #c4c4d4;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
}

.hero {
    background:
        radial-gradient(circle at -10% -20%, rgba(236,72,153,0.16), transparent 44%),
        linear-gradient(165deg, #14141c 0%, #0e0e14 100%);
    border: 1px solid #2a2a38;
    border-radius: 24px;
    padding: 20px 18px 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 48px rgba(0,0,0,0.5);
}

.hero-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    gap: 10px;
}

.career {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.6px;
    color: #a0a0b8;
    white-space: nowrap;
}

.dot {
    width: 8px;
    height: 8px;
    background: #ec4899;
    border-radius: 50%;
    box-shadow: 0 0 10px #ec4899;
}

.tabs {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    scrollbar-width: none;
}

.tabs::-webkit-scrollbar {
    display: none;
}

.tab {
    padding: 5px 13px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    color: #7a7a90;
    background: transparent;
    border: 1px solid transparent;
    white-space: nowrap;
}

.tab.active {
    color: #fff;
    border-color: #ec4899;
    background: rgba(236,72,153,0.12);
    box-shadow: 0 0 14px rgba(236,72,153,0.25);
}

.body {
    display: flex;
    gap: 12px;
    align-items: center;
    margin: 8px 0 20px;
    position: relative;
    min-height: 120px;
}

.neon-wrap {
    position: relative;
    z-index: 2;
}

.neon-number {
    font-size: 72px;
    font-weight: 800;
    line-height: 0.9;
    background: linear-gradient(120deg, #ec4899, #a855f7, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter:
        drop-shadow(0 0 12px rgba(236,72,153,0.6))
        drop-shadow(0 0 24px rgba(34,211,238,0.3));
    letter-spacing: -2px;
}

.neon-label {
    font-size: 14px;
    font-weight: 700;
    color: #ec4899;
    letter-spacing: 1px;
    margin-top: 2px;
    text-shadow: 0 0 12px rgba(236,72,153,0.5);
}

.waves {
    position: absolute;
    right: 70px;
    top: 10px;
    width: 160px;
    height: 90px;
    opacity: 0.85;
    z-index: 1;
    pointer-events: none;
}

.next-card {
    margin-left: auto;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 12px 14px;
    min-width: 110px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    position: relative;
    z-index: 2;
}

.next-label {
    font-size: 10px;
    font-weight: 600;
    color: #8888a0;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.next-name {
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    line-height: 1.2;
}

.next-date {
    font-size: 14px;
    font-weight: 600;
    color: #ec4899;
    margin-top: 2px;
}

.cal-icon {
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 14px;
    opacity: 0.6;
}

.gauges {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
}

.gauge {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 10px 4px 8px;
    text-align: center;
    position: relative;
}

.gauge-value {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
    line-height: 1;
}

.gauge-label {
    font-size: 10px;
    font-weight: 500;
    color: #8888a0;
    margin-top: 3px;
    letter-spacing: 0.3px;
}

.gauge.highlight .gauge-value {
    color: #ec4899;
    text-shadow: 0 0 10px rgba(236,72,153,0.5);
}

.badge {
    position: absolute;
    top: -6px;
    right: 6px;
    background: #ec4899;
    color: white;
    font-size: 10px;
    font-weight: 700;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 8px rgba(236,72,153,0.6);
}

.icon {
    font-size: 12px;
    opacity: 0.7;
    margin-bottom: 2px;
}

@media (max-width: 430px) {
    .block-container {
        padding-left: 12px;
        padding-right: 12px;
    }

    .hero {
        padding: 16px 14px;
    }

    .hero-top {
        flex-direction: column;
    }

    .body {
        min-height: 112px;
    }

    .neon-number {
        font-size: 62px;
    }

    .waves {
        right: 52px;
        width: 130px;
    }

    .next-card {
        min-width: 102px;
        padding: 11px 12px;
    }

    .gauges {
        gap: 7px;
    }

    .gauge {
        padding: 9px 2px 7px;
    }

    .gauge-value {
        font-size: 18px;
    }

    .gauge-label {
        font-size: 9px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

nav1, nav2 = st.columns(2)

with nav1:
    st.page_link(
        "app.py",
        label="← Career Card",
        icon="◀️",
        use_container_width=True,
    )

with nav2:
    st.page_link(
        "pages/2_Performance_Trends.py",
        label="Performance Trends",
        icon="📈",
        use_container_width=True,
    )

status_html = (
    '<div class="status-bar">'
    '<div class="status-pill">🔥 13-DAY STREAK</div>'
    '<div class="status-pill">🏆 BEST MONTH JUL · 34 EVENTS</div>'
    '<div class="status-pill">🎯 90 CAREER EVENTS</div>'
    '</div>'
)

st.markdown(status_html, unsafe_allow_html=True)

hero_html = (
    '<div class="hero">'
        '<div class="hero-top">'
            '<div class="career">'
                '<div class="dot"></div>'
                'CAREER TO DATE'
            '</div>'
            '<div class="tabs">'
                '<div class="tab active">EVENTS</div>'
                '<div class="tab">CLIENTS</div>'
                '<div class="tab">REVENUE</div>'
            '</div>'
        '</div>'
        '<div class="body">'
            '<div class="neon-wrap">'
                '<div class="neon-number">90</div>'
                '<div class="neon-label">EVENTS</div>'
            '</div>'
            '<svg class="waves" viewBox="0 0 160 90" fill="none">'
                '<path d="M0 60 C30 20, 60 80, 90 40 S140 10, 160 50" stroke="url(#g1)" stroke-width="2.5" fill="none" opacity="0.9"/>'
                '<path d="M0 70 C40 30, 70 90, 100 50 S140 20, 160 60" stroke="url(#g2)" stroke-width="2" fill="none" opacity="0.7"/>'
                '<path d="M0 50 C35 10, 65 70, 95 30 S135 0, 160 40" stroke="url(#g3)" stroke-width="1.5" fill="none" opacity="0.5"/>'
                '<defs>'
                    '<linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">'
                        '<stop offset="0%" stop-color="#ec4899"/>'
                        '<stop offset="100%" stop-color="#22d3ee"/>'
                    '</linearGradient>'
                    '<linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="0%">'
                        '<stop offset="0%" stop-color="#a855f7"/>'
                        '<stop offset="100%" stop-color="#22d3ee"/>'
                    '</linearGradient>'
                    '<linearGradient id="g3" x1="0%" y1="0%" x2="100%" y2="0%">'
                        '<stop offset="0%" stop-color="#ec4899"/>'
                        '<stop offset="100%" stop-color="#a855f7"/>'
                    '</linearGradient>'
                '</defs>'
            '</svg>'
            '<div class="next-card">'
                '<div class="cal-icon">📅</div>'
                '<div class="next-label">NEXT UP</div>'
                '<div class="next-name">MARSHALLS</div>'
                '<div class="next-date">8/3</div>'
            '</div>'
        '</div>'
        '<div class="gauges">'
            '<div class="gauge">'
                '<div class="badge">13</div>'
                '<div class="gauge-value">13</div>'
                '<div class="gauge-label">STREAK</div>'
            '</div>'
            '<div class="gauge">'
                '<div class="icon">📍</div>'
                '<div class="gauge-value">5</div>'
                '<div class="gauge-label">JURISD.</div>'
            '</div>'
            '<div class="gauge">'
                '<div class="icon">📅</div>'
                '<div class="gauge-value">6</div>'
                '<div class="gauge-label">UPCOMING</div>'
            '</div>'
            '<div class="gauge highlight">'
                '<div class="icon">🏆</div>'
                '<div class="gauge-value">JUL</div>'
                '<div class="gauge-label">BEST MO.</div>'
            '</div>'
        '</div>'
    '</div>'
)

st.markdown(hero_html, unsafe_allow_html=True)
