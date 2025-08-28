import gradio as gr
import time
import os
from langchain.chat_models import init_chat_model
from typing import TypedDict,Annotated,Union,List, Literal
from pydantic import BaseModel, Field
from deep_translator import GoogleTranslator

os.environ['GROQ_API_KEY'] ='YOUR_API_KEY'


#Using pydantic to accurately parse the llm ouput
class Parser(BaseModel):
    name: str = Field(description="Extract Name of the candidate from the text if not present keep blank, Example: 'mahesh singh','john wick'. ")
    phone: str = Field(description="Extract phone number of the candidate from text if not present keep blank.Example: '9828722323','9212321332'. ")
    email: str = Field(description="Extract email of the candidate from text if not present keep blank.Example: 'yoha@yahoo.com','some@gmail.com'. ")
    years_of_experience: str= Field(description="Extract year of experience of candidate from text if not present keep blank.Example: '0','2'. ")
    desired_positions: List[str] = Field(description="Extract the desired positions of candidate if not present keep blank list [].Example: 'software engineer','SDE','Backend engineer'. ")
    current_location: str = Field(description="Extract the current location of candidate from text if not present keep blank.Example: 'kolkata','jaipur'. ")
    tech_stack: List[str] = Field(description="Extract the techical skills or technologies of candidate from text if not present keep blank list [].Example: 'AI/ML, python','MERN, web development'. ")
               
class Followup(BaseModel):
    questions: List[str]

class singleQ(BaseModel):
    question: str

#This is used to get the accurate follow_up,verdict and reasoning for candidate's answer.
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


#Function to generate candidate's report currently shown in terminal in JSON form can be extended to store in DB.
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

#Function to generate questions based on candidate's tech stack
def generateQuestions(tech_stack,memory):
    llm = init_chat_model('groq:llama-3.3-70b-versatile',temperature=0.1)
    llm_fup = llm.with_structured_output(Followup)
    
    try:
        response = llm_fup.invoke(
            [
                {"role": "system", "content": "You are a question generator based on candidate tech stack, that generates 1-2 question. Only generate question based on tech stack."},
                {"role": "user", "content":f"This is the candidate tech stack:{tech_stack}"}
            ]
        )
    except Exception as e:
        print("Error in calling API")
        return ['Can you explain the four main principles of Object-Oriented Programming and how they are implemented in Python?','Can you explain a technical project you have worked on during your B.Tech program and the challenges you faced while working on it?']
    return response.questions

#Function to generate a single follow-up question if applicable
def generateFollowup(question, answer,memory):
    llm = init_chat_model('groq:llama-3.3-70b-versatile',temperature=0.1)
    llm_single = llm.with_structured_output(singleQ)
    
    conversation_context = "\n".join([f"{m['role']}: {m['content']}" for m in memory])
    
    try:
        fq = llm_single.invoke(f"This is the context so far:{conversation_context}\n\nGenerate 1 follow up question on this data: Question: {question} \n Answer: {answer}.\n\n Output should be in JSON format.")       
    except Exception as e:
        print("Error in calling API")
        return "Can you tell me about a situation where you faced a challenge and how you handled it?"
    return fq

#Function to translate the text between languages.
def translate(trg,txt):
    d = {"English":'en', "Hindi":'hi', "French":'fr', "German":'de'}
    return GoogleTranslator(source='auto', target=d[trg]).translate(txt)


#This is the main function for sequential flow of conversation, phase var is used for tracking phases like info gathering,question asking
# q_l-> questions list used to store all questions asked
# a_l-> answer list used to store all the answers given by candidate.
# v_l-> verdict list for correct/incorrect answer
# r_l-> Reasoning for verdicty by llm in case of debugging.
# memory-> stores the entire chat in English for llm context
# data-> candidate data in JSON
# history-> history of conversation in candidate's language.
def sequentialFlow(phase,query,history,data,questions,q_l,a_l,v_l,r_l,memory,lang_selector):
    
    llm = init_chat_model('groq:llama-3.3-70b-versatile',temperature=0.1)
    llm_parser = llm.with_structured_output(Parser)
    llm_chk = llm.with_structured_output(chk_corr_flw)
    end_reached = False
    
    history.append((query,None))
    en_query = translate('English',query)
    
    memory.append({'role':'user','content':en_query})
    
    if query.lower().strip() =='/bye':
        end_reached=True
        history.append((None,translate(lang_selector,"Interview is terminated")))     
        return phase,"",history,data,questions,q_l,a_l,v_l,r_l,memory, gr.update(interactive=False), gr.update(interactive=False)
    
    if phase<=3:
        data+=en_query+'\n'

    #Info gathering phase
    if phase==1:
        txt = "Great! How many years of experience do you have? and your desired roles? and your current location"
       
        history.append((None,translate(lang_selector,txt)))
        memory.append({"role": "assistant", "content": txt})
        phase+=1
        
    elif phase==2:
        txt ="Great! Now, please describe your tech stack." 
        history.append((None,translate(lang_selector,txt)))
        memory.append({"role": "assistant", "content": txt})
        phase+=1
        
    # Question generation and asking phase
    elif phase==3:
        try:
            response = llm_parser.invoke(f"Convert this text into JSON, if any field is missing keep blank str or array []:{data}")
        except Exception as e:
            print("Error in calling API")
            response = ''
        missing = ""
        for i in response:
            if i[1]=='' or i[1]==[]:
                missing+=str(i[0])+','
        
        if len(missing)>0:
            txt = f"Seems like some content are missing, please enter these again: {missing}"
            history.append((None,translate(lang_selector,txt)))
            memory.append({"role": "assistant", "content": txt})
        else:
            data = response
            questions = generateQuestions(','.join(data.tech_stack),memory)

            if len(questions)>0:
                q_l.append(questions[0])
                memory.append({"role": "assistant", "content": questions[0]})
                history.append((None,translate(lang_selector,questions[0])))
                questions.pop(0)
            phase+=1
   
    elif phase==4:
        a_l.append(en_query)   
        conversation_context = "\n".join([f"{m['role']}: {m['content']}" for m in memory])
        
        try:
            response = llm_chk.invoke(f"This is the context so far:{conversation_context}\n\nQuestion: {q_l[-1]}\n\nAnswer: {en_query}")
        except Exception as e:
            print("Error in calling API")
            response = {'verdict':'Correct','reasoning':'Error in api calling','follow_up':'No'}

        v_l.append(response.verdict)
        r_l.append(response.reasoning)

        if response.follow_up=='Yes':
            z = generateFollowup(q_l[-1],en_query,memory)
            questions = [z.question]+questions

        if len(questions)>0:
            q_l.append(questions[0])
            memory.append({"role": "assistant", "content": questions[0]})
            history.append((None,translate(lang_selector,questions[0])))
            questions.pop(0)
        else:
            phase+=1
            txt = "Thank you for your time. We will contact you through E-mail for further process."
            history.append((None,translate(lang_selector,txt)))
            memory.append({"role": "assistant", "content": txt})
            generateCandidateReport(data,q_l,a_l,v_l,r_l)
            end_reached=True
    
    if end_reached:
        return phase,"",history,data,questions,q_l,a_l,v_l,r_l,memory, gr.update(interactive=False), gr.update(interactive=False)
    else:
        return phase,"",history,data,questions,q_l,a_l,v_l,r_l,memory, gr.update(interactive=True), gr.update(interactive=True)

def set_greeting(lang):
    return [(None, greetings[lang])]


# UI of the project
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
    greetings = {
        "English": "Hello, This chatbot is used for initial screening of candidates. So, let's get started:\nFirstly, What is your name, phone number and email address?",
        "Hindi": "नमस्ते, यह चैटबॉट उम्मीदवारों की प्रारंभिक स्क्रीनिंग के लिए उपयोग किया जाता है। तो चलिए शुरू करते हैं:\nसबसे पहले, आपका नाम, फ़ोन नंबर और ईमेल पता क्या है?",
        "French": "Bonjour, ce chatbot est utilisé pour la présélection des candidats. Alors, commençons :\nTout d'abord, quel est votre nom, numéro de téléphone et adresse e-mail ?",
        "German": "Hallo, dieser Chatbot wird für die Vorauswahl von Kandidaten verwendet. Also, lassen Sie uns beginnen:\nZuerst, wie heißen Sie, wie lautet Ihre Telefonnummer und E-Mail-Adresse?"
    }
    
    # Header
    with gr.Row():
        gr.Markdown(
            "<h1 style='text-align: center; color: #2C3E50;'>TalentScout</h1>", 
            elem_id="title"
        )
        
    
    chatbot = gr.Chatbot(
        value = [(None,greetings["English"])],
        height=500,
        bubble_full_width=False,
        avatar_images=("https://www.svgrepo.com/show/535711/user.svg", "https://www.svgrepo.com/show/310556/bot.svg"),
    )
    
    
    with gr.Row():
        msg = gr.Textbox(
            show_label=False,
            placeholder="Type your question here.../bye to terminate",
            container=False,
            scale=8
        )
        send_btn = gr.Button("➤", scale=1, elem_classes="send-btn")
    with gr.Row():
        lang_selector = gr.Dropdown(
            ["English", "Hindi", "French", "German"],
            value="English",
            label="🌐 Language",
            interactive=True
        )
    # Disable during response
    def disable():
        return gr.update(interactive=False), gr.update(interactive=False)
    def enable():
        return gr.update(interactive=True), gr.update(interactive=True)
    
    lang_selector.change(set_greeting, lang_selector, chatbot)
    
    msg.submit(
        sequentialFlow,
        [phase,msg, chatbot,data,questions,q_l,a_l,v_l,r_l,memory,lang_selector],
        [phase,msg,chatbot,data,questions,q_l,a_l,v_l,r_l,memory,msg,send_btn],
        queue=False
    )
    send_btn.click(
        sequentialFlow,
        [phase,msg, chatbot,data,questions,q_l,a_l,v_l,r_l,memory,lang_selector],
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
