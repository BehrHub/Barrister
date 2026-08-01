import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Barrister Dash · Performance",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
.stApp {
    background-color: #0d0f17;
    color: #e2e8f0;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 680px;
}

.hero-card {
    background: rgba(23, 27, 40, 0.7);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
}

.pill-btn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    color: #94a3b8;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-right: 6px;
}

.pill-btn-active {
    background: rgba(244, 114, 182, 0.15);
    border: 1px solid #f472b6;
    color: #f472b6;
    box-shadow: 0 0 12px rgba(244, 114, 182, 0.3);
}

.hero-metric-container {
    text-align: left;
    padding: 15px 0;
}

.hero-number {
    font-size: 72px;
    font-weight: 900;
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    display: inline-block;
}

.hero-label {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #f472b6;
    margin-left: 10px;
    text-transform: uppercase;
}

.next-up-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(244, 114, 182, 0.2);
    border-radius: 14px;
    padding: 12px 16px;
    text-align: right;
}

.next-up-title {
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

.next-up-val {
    color: #ffffff;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 1px;
}

.next-up-sub {
    color: #ec4899;
    font-size: 12px;
    font-weight: 600;
}

.gauge-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 50px;
    padding: 12px 6px;
    text-align: center;
}

.gauge-val {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
}

.gauge-lbl {
    font-size: 10px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 1px;
}

.section-title {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: #f8fafc;
    margin-bottom: 15px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.page_link(
    "app.py",
    label="← Back to Career Card",
    icon="◀️",
    use_container_width=True,
)

st.markdown('<div class="hero-card">', unsafe_allow_html=True)

col_nav, col_next = st.columns([2, 1])

with col_nav:
    st.markdown(
        '<div style="margin-bottom:15px;color:#ec4899;font-size:10px;font-weight:700;letter-spacing:1px;">● CAREER TO DATE</div>'
        '<div><span class="pill-btn pill-btn-active">EVENTS</span>'
        '<span class="pill-btn">CLIENTS</span>'
        '<span class="pill-btn">REVENUE</span></div>',
        unsafe_allow_html=True,
    )

with col_next:
    st.markdown(
        '<div class="next-up-card">'
        '<div class="next-up-title">NEXT UP</div>'
        '<div class="next-up-val">MARSHALLS</div>'
        '<div class="next-up-sub">8/3</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="hero-metric-container">'
    '<span class="hero-number">90</span>'
    '<span class="hero-label">EVENTS</span>'
    '</div>',
    unsafe_allow_html=True,
)

g1, g2, g3, g4 = st.columns(4)

for column, value, label, highlight in [
    (g1, "13", "STREAK", False),
    (g2, "5", "JURISD.", False),
    (g3, "6", "UPCOMING", False),
    (g4, "JUL", "BEST MO.", True),
]:
    with column:
        color = ' style="color:#f472b6;"' if highlight else ""
        st.markdown(
            f'<div class="gauge-card">'
            f'<div class="gauge-val"{color}>{value}</div>'
            f'<div class="gauge-lbl">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="hero-card">', unsafe_allow_html=True)

h_left, h_right = st.columns([1, 1])

with h_left:
    st.markdown(
        '<div class="section-title">PERFORMANCE TRENDS</div>'
        '<div><span class="pill-btn pill-btn-active">EVENTS</span>'
        '<span class="pill-btn">REVENUE</span></div>',
        unsafe_allow_html=True,
    )

with h_right:
    st.markdown(
        '<div style="text-align:right;margin-bottom:10px;">'
        '<span class="pill-btn">WEEKLY</span>'
        '<span class="pill-btn">MONTHLY</span>'
        '<span class="pill-btn pill-btn-active">WEEKDAY</span>'
        '</div>'
        '<div style="text-align:right;font-size:11px;color:#64748b;font-weight:600;">'
        'Peak <b style="color:#f472b6;">WED • 23</b> &nbsp;|&nbsp; '
        'Avg <b>18</b> &nbsp;|&nbsp; Total <b>88</b>'
        '</div>',
        unsafe_allow_html=True,
    )

days = ["MON", "TUE", "WED", "THU", "FRI"]
current_vals = [16, 17, 23, 20, 12]
trend_vals = [0, 9, 8, 18, 12]

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=days,
        y=trend_vals,
        mode="lines",
        line=dict(color="#06b6d4", width=3, shape="spline"),
        name="Trend",
    )
)

fig.add_trace(
    go.Scatter(
        x=days,
        y=current_vals,
        mode="lines+text+markers",
        text=current_vals,
        textposition="top center",
        textfont=dict(color="#ffffff", size=12),
        line=dict(color="#ec4899", width=4, shape="spline"),
        fill="tonexty",
        fillcolor="rgba(236, 72, 153, 0.08)",
        name="Current",
    )
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=30, b=10),
    height=240,
    showlegend=False,
    xaxis=dict(
        showgrid=False,
        color="#64748b",
        tickfont=dict(size=11, family="Inter"),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.05)",
        color="#64748b",
        range=[0, 28],
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False},
)

b1, b2 = st.columns(2)

with b1:
    st.button("Show Jurisdictions Map", use_container_width=True)

with b2:
    st.button("View All Events Log", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
