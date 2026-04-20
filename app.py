"""
app.py - Smart Resource Finder Agent + Study Planner — Streamlit Interface
"""

import os
import re
import json
from datetime import date, timedelta
import streamlit as st
from agent import ResourceFinderAgent

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Smart Resource Finder",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Session State Init ───────────────────────────────────────────────────────

if "plan" not in st.session_state:
    st.session_state.plan = []
if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }
    .main .block-container { max-width: 860px; padding: 2rem 2rem 4rem; }

    /* Hero */
    .hero { text-align: center; padding: 2.2rem 0 1.2rem; }
    .hero-icon {
        font-size: 3.2rem; display: block; margin-bottom: 0.4rem;
        filter: drop-shadow(0 0 18px rgba(130,80,255,0.8));
    }
    .hero h1 {
        font-family: 'Space Mono', monospace; font-size: 2.1rem; font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0 0 0.4rem; line-height: 1.2;
    }
    .hero p { color: #a0aec0; font-size: 0.95rem; font-weight: 300; margin: 0; }

    /* Card */
    .card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 1.8rem 2rem; margin: 1.2rem 0;
        backdrop-filter: blur(12px);
    }

    /* Step boxes */
    .step-box {
        background: rgba(99,102,241,0.12); border-left: 3px solid #818cf8;
        border-radius: 8px; padding: 0.7rem 1rem; margin: 0.4rem 0;
        font-size: 0.88rem; color: #c7d2fe; font-family: 'Space Mono', monospace;
    }

    /* Result box */
    .result-box {
        background: rgba(16,185,129,0.07); border: 1px solid rgba(16,185,129,0.25);
        border-radius: 14px; padding: 1.6rem 1.8rem; margin-top: 1rem;
        color: #e2e8f0; line-height: 1.75;
    }
    .result-box h2, .result-box h3 { color: #a78bfa; font-family: 'Space Mono', monospace; }
    .result-box a { color: #60a5fa; }
    .result-box strong { color: #f0abfc; }

    /* Planner day card */
    .day-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 12px; padding: 1rem 1.2rem; margin: 0.3rem 0;
    }
    .day-card.done {
        background: rgba(16,185,129,0.08);
        border-color: rgba(16,185,129,0.3); opacity: 0.72;
    }
    .day-label {
        font-family: 'Space Mono', monospace; font-size: 0.76rem;
        color: #818cf8; margin-bottom: 0.2rem;
    }
    .day-task { color: #e2e8f0; font-size: 0.97rem; font-weight: 500; }
    .day-topic { color: #94a3b8; font-size: 0.82rem; margin-top: 0.15rem; }

    .prog-label {
        font-family: 'Space Mono', monospace; font-size: 0.82rem;
        color: #a78bfa; margin-bottom: 0.3rem;
    }
    .exam-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7c3aed33, #2563eb33);
        border: 1px solid #818cf8; border-radius: 20px;
        padding: 0.35rem 1rem; font-size: 0.85rem; color: #c7d2fe;
        font-family: 'Space Mono', monospace; margin-bottom: 1rem;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important; color: #f1f5f9 !important;
        font-size: 1rem !important; padding: 0.75rem 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,0.25) !important;
    }
    .stTextInput label, .stDateInput label, .stTextArea label,
    .stNumberInput label { color: #94a3b8 !important; font-size: 0.9rem !important; }
    .stDateInput > div > div > input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important; color: #f1f5f9 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: 0.7rem 2rem !important;
        font-size: 1rem !important; font-weight: 600 !important;
        width: 100% !important; transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 12px !important; padding: 4px !important;
        border: 1px solid rgba(255,255,255,0.08) !important; gap: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px !important; color: #94a3b8 !important;
        font-weight: 500 !important; font-size: 0.95rem !important;
        padding: 0.5rem 1.5rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
    }

    .api-hint {
        background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.3);
        border-radius: 10px; padding: 0.9rem 1.1rem; color: #fde68a;
        font-size: 0.85rem; margin-bottom: 1rem;
    }
    hr { border-color: rgba(255,255,255,0.08) !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────

st.markdown("""
    <div class="hero">
        <span class="hero-icon">🎓</span>
        <h1>Smart Resource Finder</h1>
        <p>Agentic AI study assistant · Powered by Groq + LLaMA 3.3</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("Get your **free** Groq API key at [console.groq.com](https://console.groq.com/keys)")
    sidebar_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", help="Never stored.")
    st.markdown("---")
    st.markdown("**Agent Loop**\n\n```\nObserve → Think → Act\n```\n\nLLaMA 3.3-70B with tool-use via Groq.")

api_key = sidebar_key or os.getenv("GROQ_API_KEY", "")
# $env:GROQ_API_KEY="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"
if not api_key:
    st.markdown(
        '<div class="api-hint">⚠️ <strong>No API key found.</strong> '
        'Add your Groq key in the sidebar or set <code>GROQ_API_KEY</code> env variable.</div>',
        unsafe_allow_html=True,
    )

# ─── TABS ─────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["🔍  Resource Finder", "📅  Study Planner"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESOURCE FINDER
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    topic = st.text_input(
        "📖 Enter an academic topic",
        placeholder="e.g.  Machine Learning, Fourier Transform, Operating Systems…",
        key="topic_input",
    )
    find_clicked = st.button("🔍  Find Study Resources", disabled=not api_key, key="find_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<p style='color:#64748b; font-size:0.82rem; margin-top:-0.5rem;'>"
        "Try: &nbsp;<em>Convolutional Neural Networks</em> &nbsp;·&nbsp; "
        "<em>Digital Image Processing</em> &nbsp;·&nbsp; "
        "<em>Data Structures</em> &nbsp;·&nbsp; <em>Quantum Computing</em></p>",
        unsafe_allow_html=True,
    )

    if find_clicked and topic.strip():
        with st.spinner("Agent is thinking…"):
            try:
                agent = ResourceFinderAgent(api_key=api_key)
                output = agent.run(topic.strip())

                st.markdown("#### 🤖 Agent Loop")
                for step in output["steps"]:
                    html_step = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', step)
                    st.markdown(f'<div class="step-box">{html_step}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 📚 Study Resources")
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(output["result"])
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as exc:
                st.error(f"❌ Error: {exc}")
                st.info("Check your Groq API key and internet connection.")

    elif find_clicked and not topic.strip():
        st.warning("Please enter a topic before searching.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — STUDY PLANNER
# ══════════════════════════════════════════════════════════════════════════════

with tab2:

    st.markdown("### 📅 AI Study Planner")
    st.markdown(
        "<p style='color:#94a3b8; font-size:0.9rem;'>"
        "Enter your exam date and topics — AI will auto-build a day-by-day "
        "study schedule counting backwards from your exam. "
        "Tick off sessions as you complete them!</p>",
        unsafe_allow_html=True,
    )

    # ── Inputs ────────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        exam_date = st.date_input(
            "🗓️ Exam Date",
            value=date.today() + timedelta(days=14),
            min_value=date.today() + timedelta(days=1),
            key="exam_date",
        )
    with col2:
        hours_per_day = st.number_input(
            "⏰ Study Hours / Day",
            min_value=1, max_value=12, value=3, step=1,
            key="hours_day",
        )

    topics_input = st.text_area(
        "📚 Topics to Study (one per line)",
        placeholder="Machine Learning\nDeep Learning\nConvolutional Neural Networks\nNLP",
        height=130,
        key="topics_area",
    )

    generate_clicked = st.button(
        "🗺️  Generate My Study Plan",
        disabled=not api_key,
        key="gen_plan_btn",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Generate Plan ─────────────────────────────────────────────────────────
    if generate_clicked:
        topics_list = [t.strip() for t in topics_input.strip().splitlines() if t.strip()]
        if not topics_list:
            st.warning("Please enter at least one topic.")
        else:
            days_left = (exam_date - date.today()).days
            with st.spinner("AI is building your personalised study plan…"):
                try:
                    from groq import Groq
                    client = Groq(api_key=api_key)

                    prompt = f"""You are an expert academic study planner.

Student details:
- Days until exam: {days_left} (exam on {exam_date})
- Study hours per day: {hours_per_day}
- Topics to cover: {json.dumps(topics_list)}

Create a day-by-day study plan starting from TODAY ({date.today()}) up to the day BEFORE the exam.
The final day must be: topic="Exam Preparation", task="Full Revision + Mock Test + Rest"

Rules:
1. Distribute topics evenly. Big topics can span multiple days.
2. Tasks must be specific (e.g. "Study Backpropagation & Gradient Descent" not "Study ML").
3. Return ONLY a valid JSON array. No explanation, no markdown, no backticks.

Each object must have exactly these keys:
- "day": integer starting at 1
- "date": "YYYY-MM-DD" string
- "topic": topic name
- "task": specific actionable task
- "hours": integer (equal to {hours_per_day})"""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=2048,
                        temperature=0.3,
                    )

                    raw = response.choices[0].message.content.strip()
                    raw = re.sub(r"```json|```", "", raw).strip()
                    plan_data = json.loads(raw)

                    st.session_state.plan = [{**item, "done": False} for item in plan_data]
                    st.session_state.plan_generated = True
                    st.rerun()

                except json.JSONDecodeError:
                    st.error("❌ AI returned invalid format. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # ── Show Plan ─────────────────────────────────────────────────────────────
    if st.session_state.plan_generated and st.session_state.plan:
        plan = st.session_state.plan
        total  = len(plan)
        done_count = sum(1 for p in plan if p["done"])
        progress_pct = done_count / total if total > 0 else 0

        # Exam badge + progress
        st.markdown(
            f'<div class="exam-badge">🎯 Exam on {exam_date.strftime("%d %B %Y")}'
            f' &nbsp;·&nbsp; {(exam_date - date.today()).days} days left</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="prog-label">📊 Progress — {done_count}/{total} sessions done '
            f'({int(progress_pct*100)}%)</div>',
            unsafe_allow_html=True,
        )
        st.progress(progress_pct)
        st.markdown("<br>", unsafe_allow_html=True)

        # Clear button
        if st.button("🗑️  Clear Plan & Start Over", key="clear_btn"):
            st.session_state.plan = []
            st.session_state.plan_generated = False
            st.rerun()

        st.markdown("---")
        st.markdown(
            "#### 📋 Your Study Schedule &nbsp;"
            "<span style='font-size:0.82rem; color:#64748b;'>"
            "— tick ✅ each session when done</span>",
            unsafe_allow_html=True,
        )

        # Day cards
        for i, item in enumerate(plan):
            is_done = item["done"]
            card_class = "day-card done" if is_done else "day-card"
            done_icon  = "✅" if is_done else "⬜"
            is_revision = any(k in item["task"].lower() for k in ["revision", "mock", "rest", "exam prep"])
            topic_color = "#f59e0b" if is_revision else "#818cf8"

            col_check, col_content = st.columns([0.07, 0.93])
            with col_check:
                checked = st.checkbox(
                    "", value=is_done, key=f"task_{i}",
                    label_visibility="collapsed",
                )
                if checked != is_done:
                    st.session_state.plan[i]["done"] = checked
                    st.rerun()

            with col_content:
                st.markdown(
                    f"""<div class="{card_class}">
                        <div class="day-label">Day {item['day']} &nbsp;·&nbsp; {item['date']} &nbsp;·&nbsp; ⏱ {item.get('hours','—')}h</div>
                        <div class="day-task">{done_icon} {item['task']}</div>
                        <div class="day-topic" style="color:{topic_color};">📌 {item['topic']}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        # All done 🎉
        if done_count == total:
            st.markdown(
                "<div style='text-align:center; padding:2rem; margin-top:1.5rem;"
                "background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.4);"
                "border-radius:16px;'>"
                "<div style='font-size:2.5rem'>🎉</div>"
                "<div style='color:#34d399; font-family:Space Mono,monospace;"
                "font-size:1.1rem; font-weight:700;'>All sessions completed! Go ace that exam!</div>"
                "</div>",
                unsafe_allow_html=True,
            )

# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#475569; font-size:0.8rem;'>"
    "Smart Resource Finder Agent &nbsp;·&nbsp; Built with Groq API + LLaMA 3.3-70B + Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
