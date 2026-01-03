# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from typing import List, Dict

# -------------------- SETUP --------------------

load_dotenv()

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found in environment variables.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(
    page_title="CodeCraft",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .task-card {
        # background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .task-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .task-1 { border-left-color: #10B981; }
    .task-2 { border-left-color: #F59E0B; }
    .task-3 { border-left-color: #EF4444; }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .status-completed { background: #D1FAE5; color: #065F46; }
    .status-pending { background: #FEF3C7; color: #92400E; }
    
    .code-editor {
        font-family: 'Courier New', monospace;
        background: #1E1E1E;
        color: #D4D4D4;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #374151;
    }
    
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        position: relative;
    }
    
    .step-indicator::before {
        content: '';
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 2px;
        background: #E5E7EB;
        z-index: 1;
    }
    
    .step {
        text-align: center;
        position: relative;
        z-index: 2;
        flex: 1;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: white;
        border: 2px solid #E5E7EB;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-weight: bold;
    }
    
    .step.active .step-circle {
        background: #667eea;
        border-color: #667eea;
        color: white;
    }
    
    .step.completed .step-circle {
        background: #10B981;
        border-color: #10B981;
        color: white;
    }
    
    .feedback-section {
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #D1D5DB;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "codes" not in st.session_state:
    st.session_state.codes = ["", "", ""]

if "submitted" not in st.session_state:
    st.session_state.submitted = [False, False, False]

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "transcript_locked" not in st.session_state:
    st.session_state.transcript_locked = False

if "current_step" not in st.session_state:
    st.session_state.current_step = 1

# -------------------- TASK GENERATION --------------------

def generate_tasks(transcript: str) -> List[Dict]:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
You are a coding challenge designer.

From the given tutorial transcript, generate EXACTLY 3 coding tasks.

Rules:
- Task 1: Guided application of what was shown
- Task 2: Independent application (no hints)
- Task 3: Design-oriented task with ambiguity

Return STRICTLY in this format:

TASK 1:
Title:
Description:

TASK 2:
Title:
Description:

TASK 3:
Title:
Description:

Do NOT add anything else.
"""
            },
            {
                "role": "user",
                "content": transcript
            }
        ],
        temperature=0.4,
        max_tokens=700
    )

    return parse_tasks(response.choices[0].message.content)


def parse_tasks(content: str) -> List[Dict]:
    tasks = []
    blocks = content.split("TASK ")[1:]
    colors = {1: "🟢", 2: "🟡", 3: "🔴"}

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        level = int(lines[0][0])

        title = lines[1].replace("Title:", "").strip()
        description = "\n".join(lines[2:]).replace("Description:", "").strip()

        tasks.append({
            "level": level,
            "icon": colors[level],
            "title": title,
            "description": description
        })

    return tasks

# -------------------- EVALUATION --------------------

def evaluate_all(codes: List[str]) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
You are a senior software engineer evaluating 3 progressive coding tasks.

Analyze the submissions TOGETHER.

Focus on:
- Progression in thinking
- Code quality
- Decision-making
- Strengths and weaknesses
- What the learner should do next

Return structured markdown.
"""
            },
            {
                "role": "user",
                "content": f"""
TASK 1 CODE:
{codes[0]}

TASK 2 CODE:
{codes[1]}

TASK 3 CODE:
{codes[2]}
"""
            }
        ],
        temperature=0.3,
        max_tokens=900
    )

    return response.choices[0].message.content

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("<div class='main-header'>", unsafe_allow_html=True)
    st.markdown("# 🧠 CodeCraft")
    st.markdown("Turn tutorials into real coding ability")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. **Paste** tutorial transcript
    2. **Complete** 3 progressive tasks
    3. **Get** AI evaluation
    4. **Download** your report
    """)
    
    st.markdown("---")
    
    # Progress tracker
    st.markdown("### 📊 Your Progress")
    
    progress_value = 0
    if st.session_state.transcript_locked:
        progress_value += 25
    progress_value += sum(st.session_state.submitted) * 25
    
    st.progress(min(progress_value, 100))
    
    cols = st.columns(2)
    with cols[0]:
        st.metric("Tasks Generated", 
                 len(st.session_state.tasks), 
                 f"{len(st.session_state.tasks)}/3")
    with cols[1]:
        st.metric("Tasks Completed", 
                 sum(st.session_state.submitted), 
                 f"{sum(st.session_state.submitted)}/3")
    
    st.markdown("---")
    
    if st.button("🔄 Reset Session", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -------------------- MAIN CONTENT --------------------

# Step indicator
col1, col2, col3 = st.columns(3)

with col1:
    step1_class = "active" if st.session_state.current_step == 1 else "completed" if st.session_state.transcript_locked else ""
    st.markdown(f"""
    <div class="step {step1_class}">
        <div class="step-circle">1</div>
        <div><strong>Transcript</strong></div>
        <div>Paste & Lock</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    step2_class = "active" if st.session_state.current_step == 2 else "completed" if any(st.session_state.submitted) else ""
    st.markdown(f"""
    <div class="step {step2_class}">
        <div class="step-circle">2</div>
        <div><strong>Code Tasks</strong></div>
        <div>Complete 3 Tasks</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    step3_class = "active" if st.session_state.current_step == 3 else "completed" if st.session_state.feedback else ""
    st.markdown(f"""
    <div class="step {step3_class}">
        <div class="step-circle">3</div>
        <div><strong>Evaluation</strong></div>
        <div>Get Feedback</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Step 1: Transcript
if not st.session_state.transcript_locked:
    st.session_state.current_step = 1
    st.markdown("### 📝 Step 1: Tutorial Transcript")
    
    with st.container():
        transcript = st.text_area(
            "**Paste your tutorial transcript below**",
            height=250,
            placeholder="""Paste your YouTube or course transcript here...
            
Example:
"This tutorial covers Python list comprehensions. We'll learn how to create new lists by applying operations to existing lists..."
            """,
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ Generate Coding Tasks", type="primary", use_container_width=True):
                if transcript.strip():
                    with st.spinner("🤖 Generating tailored coding tasks..."):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            # Simulate progress
                            progress_bar.progress(i + 1)
                        st.session_state.tasks = generate_tasks(transcript)
                        st.session_state.transcript_locked = True
                        st.session_state.current_step = 2
                        st.rerun()
                else:
                    st.warning("Please paste a transcript first.")
else:
    st.session_state.current_step = 2
    st.success("✅ Transcript locked - Tasks are ready!")

# Step 2: Tasks
if st.session_state.tasks:
    st.markdown("### 💻 Step 2: Coding Challenges")
    st.markdown(f"*Complete all 3 tasks for comprehensive evaluation*")
    
    # Create tabs with improved styling
    tab_titles = [
        f"{task['icon']} **Task {i+1}**: {task['title']}" 
        for i, task in enumerate(st.session_state.tasks)
    ]
    
    tabs = st.tabs(tab_titles)
    
    for i, tab in enumerate(tabs):
        with tab:
            task = st.session_state.tasks[i]
            
            # Task card
            st.markdown(f"""
            <div class="task-card task-{i+1}">
                <span class="status-badge {'status-completed' if st.session_state.submitted[i] else 'status-pending'}">
                    {'✅ Submitted' if st.session_state.submitted[i] else '📝 In Progress'}
                </span>
                <h4>{task['icon']} Task {i+1}: {task['title']}</h4>
                <p>{task['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Code editor
            st.markdown("**Your Solution:**")
            code = st.text_area(
                "",
                value=st.session_state.codes[i],
                height=280,
                key=f"code_{i}",
                placeholder=f"""# Write your solution for Task {i+1} here
# You can use any language
# Make sure to test your code
                
# Example for Python:
# def solution():
#     # Your code here
#     pass""",
                label_visibility="collapsed"
            )
            
            st.session_state.codes[i] = code
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button(f"💾 Save Task {i+1}", 
                           key=f"save_{i}",
                           type="primary" if not st.session_state.submitted[i] else "secondary",
                           use_container_width=True):
                    st.session_state.submitted[i] = True
                    st.success(f"Task {i+1} saved successfully!")
                    st.rerun()
    
    # Step 3: Evaluation
    st.markdown("### 📊 Step 3: Get Evaluation")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🤖 Analyze All Tasks & Generate Report", 
                    type="primary", 
                    use_container_width=True):
            if any(st.session_state.submitted):
                st.session_state.current_step = 3
                with st.spinner("🔍 Analyzing your code... This may take a moment."):
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    for i in range(3):
                        progress_text.text(f"Analyzing Task {i+1}...")
                        progress_bar.progress((i + 1) * 33)
                    
                    st.session_state.feedback = evaluate_all(st.session_state.codes)
                    progress_bar.progress(100)
                    progress_text.text("✅ Analysis complete!")
                    
                st.rerun()
            else:
                st.warning("Please complete and save at least one task first.")

# Feedback Section
if st.session_state.feedback:
    st.markdown("---")
    
    with st.container():
        st.markdown("### 🎯 AI Evaluation Report")
        
        # Report stats
        completed_tasks = sum(st.session_state.submitted)
        cols = st.columns(4)
        with cols[0]:
            st.metric("Tasks Analyzed", completed_tasks)
        with cols[1]:
            st.metric("Progress Level", 
                     f"Task {completed_tasks}/3" if completed_tasks < 3 else "Complete")
        
        # Feedback display
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown(st.session_state.feedback)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download and Next Steps
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.download_button(
                "📥 Download Full Report",
                st.session_state.feedback,
                file_name="codecraft_feedback.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col2:
            if st.button("🔄 Try New Tasks", use_container_width=True):
                st.session_state.tasks = []
                st.session_state.codes = ["", "", ""]
                st.session_state.submitted = [False, False, False]
                st.session_state.feedback = ""
                st.session_state.transcript_locked = False
                st.session_state.current_step = 1
                st.rerun()
        with col3:
            if st.button("📝 Edit Solutions", use_container_width=True):
                st.session_state.feedback = ""
                st.session_state.current_step = 2
                st.rerun()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.caption("Made with ❤️ using Streamlit & Groq AI")