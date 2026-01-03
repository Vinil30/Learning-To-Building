🧠 CodeCraft

Turn tutorial watching into real coding ability.
CodeCraft is a minimal AI-powered platform that converts programming tutorial transcripts into progressive coding tasks and provides holistic evaluation of a learner’s problem-solving progression.
Instead of teaching more content, CodeCraft focuses on what most tutorials miss: structured, contextual practice.

🚩 The Problem

Learners finish online courses and YouTube tutorials with confidence — until they try to build something on their own.
Most tutorials:
Are fully guided
Remove ambiguity
Make all decisions in advance

Real-world development is the opposite. Learners struggle not because they lack knowledge, but because they lack practice in deciding, structuring, and finishing code independently.

💡 The Idea

CodeCraft bridges the gap between watching and building.

The user pastes a tutorial transcript.
From that exact context, CodeCraft generates three progressive coding tasks and evaluates them together, focusing on how the learner’s thinking evolves.

No generic exercises.
No predefined projects.
Only practice grounded in what the learner just learned.

⚙️ How It Works (Pipeline)
Tutorial Transcript
        ↓
Groq (LLaMA 3)
        ↓
3 Progressive Coding Tasks
        ↓
User Submits Code
        ↓
Combined AI Evaluation


🤖 AI Design

LLM Provider: Groq
Model: llama3-70b-8192
No JSON parsing
Single AI call for task generation
Single AI call for combined evaluation
The system is intentionally simple to ensure reliability and low latency.

🖥️ Tech Stack
Frontend: Streamlit
Backend / AI: Groq API (LLaMA 3)
Language: Python
Environment Management: python-dotenv

