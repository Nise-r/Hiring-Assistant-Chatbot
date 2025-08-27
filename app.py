import gradio as gr
import time
import os
from langchain.chat_models import init_chat_model
from typing import TypedDict,Annotated,Union,List, Literal
from pydantic import BaseModel, Field
from pydantic import ValidationError


os.environ['GROQ_API_KEY'] ='YOUR_API_KEY'

class Parser(BaseModel):
    name: str
    phone: int
    email: str
    years_of_experience: int
    desired_positions: List[str]
    current_location: str
    tech_stack: List[str]
        
class Followup(BaseModel):
    questions: List[str]

class chk_corr_flw(BaseModel):
    verdict: Literal['Correct','False'] = Field(
        description="""Check the answer of candidate according to question if it is correct or even partially correct give 'Correct' else if the answer is entirely wrong or candidate doesn't know the answer give 'False' """
    )
    reasoning: str = Field(
        description="""Give short reasoning for the chosen verdict on candidate answer in 10-15 word maximum."""
    )
    follow_up: Literal['Yes','No'] = Field(
        description="""Check the answer of candidate according to question and give 'Yes' if a followup question can be asked otherwise if the candidate says he doesn't know the answer or similar give 'No' """
    )        

class singleQ(BaseModel):
    question: str

def generateCandidateReport(data,q_l,a_l,v_l,r_l ):
    final_data = {
        "name":data.name,
        "phone":data.phone,
        "email":data.email,
        "years_of_experience":data.years_of_experience,
        "desired_positions":data.desired_positions,
        "current_location":data.current_location,
        "tech_stack":data.tech_stack,
        "questions":q_l,
        "answers":a_l,
        "verdict":v_l,
        "reasoning":r_l
    }
    print(final_data)
        
def generateQuestions(tech_stack,memory):
    llm = init_chat_model('groq:llama-3.3-70b-versatile',temperature=0.1)
    llm_fup = llm.with_structured_output(Followup)
#     response = llm_fup.invoke(f"Generate 1-2 question for interview based on this candidate's tech stack: {tech_stack}")
    response = llm_fup.invoke(
        [
            {"role": "system", "content": "You are a question generator based on candidate tech stack, that generates 1-2 question. Only generate question based on tech stack."},
            {"role": "user", "content":f"This is the candidate tech stack:{tech_stack}"}
        ]
    )
    print(response.questions)
    return response.questions
       
def generateFollowup(question, answer,memory):
    llm = init_chat_model('groq:llama-3.3-70b-versatile',temperature=0.1)
    llm_single = llm.with_structured_output(singleQ)
    
    conversation_context = "\n".join([f"{m['role']}: {m['content']}" for m in memory])
    
    fq = llm_single.invoke(f"This is the context so far:{conversation_context}\n\nGenerate 1 follow up question on this data: Question: {question} \n Answer: {answer}.\n\n Output should be in JSON format.")       
        
    return fq
    
def sequentialFlow(phase,query,history,data,questions,q_l,a_l,v_l,r_l,memory):
    
    llm = init_chat_model('groq:llama-3.3-70b-versatile',temperature=0.1)
    llm_parser = llm.with_structured_output(Parser)
    llm_chk = llm.with_structured_output(chk_corr_flw)
    end_reached = False
    
    history.append((query,None))
    memory.append({'role':'user','content':query})
    
    
    if phase<3:
        data+=query+'\n'

    if phase==1:
        history.append((None,"Great! How many years of experience do you have? and your desired roles? and your current location"))
        memory.append({"role": "assistant", "content": "Great! How many years of experience do you have? and your desired roles? and your current location"})
        phase+=1
        
    elif phase==2:
        history.append((None,"Great! Now, please describe your tech stack."))
        memory.append({"role": "assistant", "content": "Great! Now, please describe your tech stack."})
        phase+=1
        
    elif phase==3:
        response = llm_parser.invoke(f"Convert this text into JSON: {data}")
        data = response
        questions = generateQuestions(','.join(data.tech_stack),memory)

        if len(questions)>0:
            q_l.append(questions[0])
            memory.append({"role": "assistant", "content": questions[0]})
            history.append((None,questions[0]))
            questions.pop(0)
        phase+=1
   
    elif phase==4:
        a_l.append(query)   
        conversation_context = "\n".join([f"{m['role']}: {m['content']}" for m in memory])
        
        response = llm_chk.invoke(f"This is the context so far:{conversation_context}\n\nQuestion: {q_l[-1]}\n\nAnswer: {query}")

        v_l.append(response.verdict)
        r_l.append(response.reasoning)

        if response.follow_up=='Yes':
            z = generateFollowup(q_l[-1],query,memory)
            questions = [z.question]+questions

        if len(questions)>0:
            q_l.append(questions[0])
            memory.append({"role": "assistant", "content": questions[0]})
            history.append((None,questions[0]))
            questions.pop(0)
        else:
            phase+=1
            history.append((None,"Thank you for your time. We will contact you through E-mail for further process."))
            memory.append({"role": "assistant", "content": "Thank you for your time. We will contact you through E-mail for further process."})
            generateCandidateReport(data,q_l,a_l,v_l,r_l)
            end_reached=True
    
    if end_reached:
        return phase,"",history,data,questions,q_l,a_l,v_l,r_l,memory, gr.update(interactive=False), gr.update(interactive=False)
    else:
        return phase,"",history,data,questions,q_l,a_l,v_l,r_l,memory, gr.update(interactive=True), gr.update(interactive=True)

with gr.Blocks(
    title="TalentScout", 
    theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo")
) as demo:
    
    data = gr.State("")
    phase = gr.State(1)
    questions = gr.State([])
    q_l=gr.State([])
    a_l=gr.State([])
    v_l=gr.State([])
    r_l=gr.State([])
    memory = gr.State([])
    
    # Header
    with gr.Row():
        gr.Markdown(
            "<h1 style='text-align: center; color: #2C3E50;'>TalentScout</h1>", 
            elem_id="title"
        )
    
    chatbot = gr.Chatbot(
        value = [(None,"Hello, This chatbot is used for initial screening of candidates.So, lets get started:\nFirstly, What is your name, phone number and email address?")],
        height=500,
        bubble_full_width=False,
        avatar_images=("https://www.svgrepo.com/show/535711/user.svg", "https://www.svgrepo.com/show/310556/bot.svg"),
    )
    
    with gr.Row():
        msg = gr.Textbox(
            show_label=False,
            placeholder="Type your question here...",
            container=False,
            scale=8
        )
        send_btn = gr.Button("➤", scale=1, elem_classes="send-btn")

    # Disable during response
    def disable():
        return gr.update(interactive=False), gr.update(interactive=False)
    def enable():
        return gr.update(interactive=True), gr.update(interactive=True)
    
    msg.submit(
        sequentialFlow,
        [phase,msg, chatbot,data,questions,q_l,a_l,v_l,r_l,memory],
        [phase,msg,chatbot,data,questions,q_l,a_l,v_l,r_l,memory,msg,send_btn],
        queue=False
    )
    send_btn.click(
        sequentialFlow,
        [phase,msg, chatbot,data,questions,q_l,a_l,v_l,r_l,memory ],
        [phase,msg,chatbot,data,questions,q_l,a_l,v_l,r_l,memory,msg,send_btn],
        queue=False
    )

    demo.css = """
    #title { font-family: 'Segoe UI', sans-serif; margin-bottom: 10px; }
    .send-btn { 
        border-radius: 50%; 
        height: 48px !important; 
        width: 48px !important; 
        font-size: 20px; 
    }
    .wrap.svelte-1ipelgc { 
        border-radius: 18px !important; 
        padding: 10px 14px !important; 
        font-size: 15px; 
    }
    """

demo.queue().launch()
