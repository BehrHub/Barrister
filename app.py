import streamlit as st

st.set_page_config(page_title="Barrister Dash", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 480px;}

.status-bar {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 12px;
    margin-bottom: 8px;
}
.status-pill {
    background: #1e1e24;
    border: 1px solid #2e2e38;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
    color: #c0c0d0;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
}
.status-pill .emoji {font-size: 13px;}

.hero-card {
    background: linear-gradient(160deg, #1a1a22 0%, #121218 100%);
    border: 1px solid #2a2a35;
    border-radius: 24px;
    padding: 20px 20px 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
}
.hero-card::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -30%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(236,72,153,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
}
.career-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.6px;
    color: #a0a0b0;
}
.pink-dot {
    width: 8px;
    height: 8px;
    background: #ec4899;
    border-radius: 50%;
    box-shadow: 0 0 8px #ec4899;
}
.tabs {display: flex; gap: 6px;}
.tab {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    color: #8888a0;
    background: transparent;
    border: 1px solid transparent;
}
.tab.active {
    color: #fff;
    background: rgba(236,72,153,0.15);
    border-color: #ec4899;
    box-shadow: 0 0 12px rgba(236,72,153,0.25);
}
.hero-body {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 22px;
}
.number-wrap {
    position: relative;
    width: 140px;
    height: 140px;
    flex-shrink: 0;
}
.progress-ring {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: conic-gradient(#ec4899 0% 72%, #2a2a35 72% 100%);
    mask: radial-gradient(farthest-side, transparent 62%, #000 63%);
    -webkit-mask: radial-gradient(farthest-side, transparent 62%, #000 63%);
}
.number-center {
    position: absolute;
    inset: 14px;
    background: #16161e;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.big-number {
    font-size: 48px;
    font-weight: 800;
    color: #fff;
    line-height: 1;
    letter-spacing: -1px;
}
.big-label {
    font-size: 13px;
    font-weight: 600;
    color: #ec4899;
    margin-top: 2px;
    letter-spacing: 0.5px;
}
.next-up {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 14px 16px;
    backdrop-filter: blur(8px);
}
.next-label {
    font-size: 11px;
    font-weight: 600;
    color: #8888a0;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.next-name {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 2px;
}
.next-date {
    font-size: 15px;
    font-weight: 600;
    color: #ec4899;
}
.metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}
.metric {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 12px 6px;
    text-align: center;
}
.metric-value {
    font-size: 20px;
    font-weight: 700;
    color: #fff;
    line-height: 1.1;
}
.metric-label {
    font-size: 11px;
    font-weight: 500;
    color: #8888a0;
    margin-top: 3px;
    letter-spacing: 0.3px;
}
.metric.highlight .metric-value {color: #ec4899;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-bar">
    <div class="status-pill"><span class="emoji">🔥</span> 13-DAY STREAK</div>
    <div class="status-pill"><span class="emoji">🏆</span> BEST MONTH JUL · 34 EVENTS</div>
    <div class="status-pill"><span class="emoji">🎯</span> 90 CAREER EVENTS</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="hero-header">
        <div class="career-label">
            <div class="pink-dot"></div>
            CAREER TO DATE
        </div>
        <div class="tabs">
            <div class="tab active">EVENTS</div>
            <div class="tab">CLIENTS</div>
            <div class="tab">REVENUE</div>
        </div>
    </div>

    <div class="hero-body">
        <div class="number-wrap">
            <div class="progress-ring"></div>
            <div class="number-center">
                <div class="big-number">90</div>
                <div class="big-label">EVENTS</div>
            </div>
        </div>

        <div class="next-up">
            <div class="next-label">NEXT UP</div>
            <div class="next-name">MARSHALLS</div>
            <div class="next-date">8/3</div>
        </div>
    </div>

    <div class="metrics">
        <div class="metric">
            <div class="metric-value">13</div>
            <div class="metric-label">STREAK</div>
        </div>
        <div class="metric">
            <div class="metric-value">5</div>
            <div class="metric-label">JURISD.</div>
        </div>
        <div class="metric">
            <div class="metric-value">6</div>
            <div class="metric-label">UPCOMING</div>
        </div>
        <div class="metric highlight">
            <div class="metric-value">JUL</div>
            <div class="metric-label">BEST MO.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
