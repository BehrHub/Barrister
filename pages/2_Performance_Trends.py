import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Barrister Dash · Glass Component",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    .stApp {
        background-color: #0b0d14;
    }

    #MainMenu,
    footer,
    header {
        visibility: hidden;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 480px;
    }
</style>
""",
    unsafe_allow_html=True,
)

nav_left, nav_right = st.columns(2)

with nav_left:
    st.page_link(
        "app.py",
        label="← Career Card",
        icon="◀️",
        use_container_width=True,
    )

with nav_right:
    st.page_link(
        "pages/3_Neon_Flow.py",
        label="Neon Flow →",
        icon="🌊",
        use_container_width=True,
    )

hero_card_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                sans-serif;
        }

        html,
        body {
            width: 100%;
            overflow: hidden;
            background: transparent;
        }

        body {
            color: #ffffff;
            padding: 10px;
        }

        .glass-card {
            background:
                radial-gradient(
                    circle at 100% -20%,
                    rgba(244, 114, 182, 0.11),
                    transparent 44%
                ),
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.05) 0%,
                    rgba(255,255,255,0.01) 100%
                );
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border:
                1px solid
                rgba(255, 255, 255, 0.12);
            border-radius: 24px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            box-shadow:
                0 20px 40px rgba(0,0,0,0.6),
                inset 0 1px 0 rgba(255,255,255,0.15);
        }

        .top-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 15px;
            position: relative;
            z-index: 2;
        }

        .section-tag {
            color: #ec4899;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }

        .section-tag::before {
            content: "";
            width: 6px;
            height: 6px;
            background-color: #ec4899;
            border-radius: 50%;
            box-shadow: 0 0 8px #ec4899;
        }

        .pill-group {
            display: flex;
            gap: 6px;
        }

        .pill {
            background: rgba(255, 255, 255, 0.04);
            border:
                1px solid
                rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }

        .pill.active {
            background: rgba(244, 114, 182, 0.1);
            border-color: #f472b6;
            color: #f472b6;
            box-shadow:
                0 0 12px
                rgba(244, 114, 182, 0.3);
        }

        .next-up-box {
            background: rgba(15, 20, 32, 0.6);
            border:
                1px solid
                rgba(244, 114, 182, 0.25);
            border-radius: 14px;
            padding: 8px 14px;
            text-align: right;
            box-shadow:
                0 4px 20px
                rgba(0,0,0,0.4);
            min-width: 112px;
            flex: 0 0 auto;
        }

        .next-up-title {
            color: #64748b;
            font-size: 8px;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .next-up-val {
            font-size: 14px;
            font-weight: 900;
            letter-spacing: 0.5px;
            color: #fff;
        }

        .next-up-sub {
            color: #ec4899;
            font-size: 10px;
            font-weight: 700;
        }

        .hero-metric-section {
            position: relative;
            z-index: 2;
            margin: 10px 0 20px;
            display: flex;
            align-items: baseline;
        }

        .hero-number {
            font-size: 76px;
            font-weight: 900;
            line-height: 1;
            background:
                linear-gradient(
                    135deg,
                    #ffffff 0%,
                    #f472b6 50%,
                    #38bdf8 100%
                );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter:
                drop-shadow(
                    0 0 25px
                    rgba(244, 114, 182, 0.45)
                );
            letter-spacing: -2px;
        }

        .hero-label {
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 2px;
            color: #ec4899;
            margin-left: 12px;
            text-shadow:
                0 0 10px
                rgba(236, 72, 153, 0.5);
        }

        .svg-bg {
            position: absolute;
            top: 20px;
            right: -10px;
            width: 70%;
            height: 100px;
            pointer-events: none;
            z-index: 0;
        }

        .gauges-grid {
            display: grid;
            grid-template-columns:
                repeat(4, minmax(0, 1fr));
            gap: 8px;
            position: relative;
            z-index: 2;
        }

        .gauge-item {
            background:
                linear-gradient(
                    180deg,
                    rgba(255,255,255,0.05) 0%,
                    rgba(255,255,255,0.01) 100%
                );
            border:
                1px solid
                rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 10px 4px;
            text-align: center;
            box-shadow:
                inset 0 1px 0
                rgba(255,255,255,0.1);
        }

        .gauge-item.highlight {
            border-color:
                rgba(244, 114, 182, 0.4);
            box-shadow:
                0 0 15px
                rgba(244, 114, 182, 0.15),
                inset 0 1px 0
                rgba(255,255,255,0.2);
        }

        .gauge-val {
            font-size: 18px;
            font-weight: 800;
            color: #ffffff;
        }

        .gauge-val.pink {
            color: #f472b6;
            text-shadow:
                0 0 8px
                rgba(244, 114, 182, 0.6);
        }

        .gauge-lbl {
            font-size: 8px;
            font-weight: 800;
            color: #64748b;
            letter-spacing: 1px;
            margin-top: 2px;
        }

        @media (max-width: 420px) {
            body {
                padding: 4px;
            }

            .glass-card {
                padding: 16px 14px;
            }

            .top-row {
                gap: 8px;
            }

            .pill {
                padding: 5px 8px;
                font-size: 9px;
            }

            .next-up-box {
                min-width: 100px;
                padding: 7px 10px;
            }

            .hero-number {
                font-size: 64px;
            }

            .hero-label {
                margin-left: 8px;
            }

            .gauges-grid {
                gap: 6px;
            }

            .gauge-item {
                padding: 9px 2px;
            }

            .gauge-val {
                font-size: 17px;
            }

            .gauge-lbl {
                font-size: 7px;
            }
        }
    </style>
</head>

<body>
    <div class="glass-card">
        <svg
            class="svg-bg"
            viewBox="0 0 300 100"
            fill="none"
            aria-hidden="true"
        >
            <path
                d="M 0 80 C 100 80, 120 10, 300 10"
                stroke="url(#pink-grad)"
                stroke-width="3"
                opacity="0.6"
            />
            <path
                d="M 0 90 C 110 90, 130 20, 300 20"
                stroke="url(#blue-grad)"
                stroke-width="2"
                opacity="0.4"
            />

            <defs>
                <linearGradient
                    id="pink-grad"
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="0%"
                >
                    <stop
                        offset="0%"
                        stop-color="#ec4899"
                    />
                    <stop
                        offset="100%"
                        stop-color="#a855f7"
                    />
                </linearGradient>

                <linearGradient
                    id="blue-grad"
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="0%"
                >
                    <stop
                        offset="0%"
                        stop-color="#3b82f6"
                    />
                    <stop
                        offset="100%"
                        stop-color="#06b6d4"
                    />
                </linearGradient>
            </defs>
        </svg>

        <div class="top-row">
            <div>
                <div class="section-tag">
                    CAREER TO DATE
                </div>

                <div class="pill-group">
                    <div class="pill active">
                        EVENTS
                    </div>
                    <div class="pill">
                        CLIENTS
                    </div>
                    <div class="pill">
                        REVENUE
                    </div>
                </div>
            </div>

            <div class="next-up-box">
                <div class="next-up-title">
                    NEXT UP
                </div>
                <div class="next-up-val">
                    MARSHALLS
                </div>
                <div class="next-up-sub">
                    8/3
                </div>
            </div>
        </div>

        <div class="hero-metric-section">
            <span class="hero-number">
                90
            </span>
            <span class="hero-label">
                EVENTS
            </span>
        </div>

        <div class="gauges-grid">
            <div class="gauge-item">
                <div class="gauge-val">
                    13
                </div>
                <div class="gauge-lbl">
                    STREAK
                </div>
            </div>

            <div class="gauge-item">
                <div class="gauge-val">
                    5
                </div>
                <div class="gauge-lbl">
                    JURISD.
                </div>
            </div>

            <div class="gauge-item">
                <div class="gauge-val">
                    6
                </div>
                <div class="gauge-lbl">
                    UPCOMING
                </div>
            </div>

            <div class="gauge-item highlight">
                <div class="gauge-val pink">
                    JUL
                </div>
                <div class="gauge-lbl">
                    BEST MO.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

components.html(
    hero_card_html,
    height=310,
    scrolling=False,
)
