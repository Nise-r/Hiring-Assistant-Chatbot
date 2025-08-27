# Hiring Assistant Chatbot

An AI-powered Hiring Assistant chatbot that streamlines the candidate evaluation process. The system gathers structured information (name, contact details, skills, experience, tech stack, etc.), stores it in memory for context-aware conversations, and dynamically generates relevant technical follow-up questions based on the candidate’s background.

## Project Overview
This project implements an intelligent interview assistant using LangChain + Groq LLMs + Gradio UI.
Key capabilities include:
- Extracting structured candidate information using Pydantic models.
- Maintaining memory for contextual multi-turn conversations.
- Generating follow-up technical questions tailored to the candidate’s tech stack and experience.
- Providing a simple web-based interface for recruiters to interact with the assistant.

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/Hiring-Assistant-Chatbot.git
cd Hiring-Assistant-Chatbot
```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up API keys**:
   Change directly in code.
   ```bash
    os.environ['GROQ_API_KEY'] ='YOUR_API_KEY'
   ```

3. **Run the application**:
   ```bash
   gradio app.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:7860`)

##  Usage

1. Launch the chatbot via the Gradio interface.
2. Provide your details (name, phone, email, experience, location, etc.).
3. The bot will automatically parse your input into structured fields.
4. Based on your tech stack, it will generate tailored technical interview questions.
5. Recruiters can use these questions to conduct more informed interviews.

## Technical Details
1. Frameworks & Libraries
 - LangChain – Orchestrating LLMs, memory, and structured outputs
 - Groq LLMs – Fast inference with LLaMA 3.1 models
 - Gradio – Interactive web-based interface
 - Pydantic – Enforcing structured outputs
2. Architecture Decisions
 - Structured Parsing → Candidate info extracted using BaseModel (Pydantic).
 - Contextual Memory → Memory ensures continuity across turns.
 - Question Generation → with_structured_output enforces valid JSON for follow-ups.
 - UI → Gradio provides an easy and lightweight way to demo the chatbot.

## Challenges & Solutions
|Challenge	                                                  |Solution                                                                  |
|-------------------------------------------------------------|--------------------------------------------------------------------------|
|LLM output sometimes deviated from required JSON forma       |Used llm.with_structured_output(PydanticModel) to enforce schema          |
|Context loss in multi-turn conversations	                    |Integrated Memory                                                         |
|Generating irrelevant or generic follow-up questions         |Engineered prompts to include candidate’s years of experience + tech stack|
|Strict Groq API parsing errors (tool_use_failed)	           |Debugged raw outputs, adjusted schema + prompts for exact alignment       |

---

**Happy Chatting! 🎉** 
