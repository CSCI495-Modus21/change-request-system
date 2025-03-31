import panel as pn
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

load_dotenv()
HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
print("HF_TOKEN:", HF_TOKEN)
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env file")

try:
    tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder-7b-2", token=HF_TOKEN) # initialize the sqlcoder-7b-2 model and tokenizer
    model = AutoModelForCausalLM.from_pretrained("defog/sqlcoder-7b-2", token=HF_TOKEN)
except Exception as e:
    print(f"Error loading model: {e}")
    raise


device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # check if GPU is available
model = model.to(device)

def get_response(contents, user, instance):
    prompt = contents if isinstance(contents, str) else " ".join(str(msg) for msg in contents)
    
    sql_prompt = f"Translate this to SQL: {prompt}"
    inputs = tokenizer(sql_prompt, return_tensors="pt", max_length=512, truncation=True)
    inputs = inputs.to(device)
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,  
        do_sample=False,    
        temperature=0.1,     
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

chat_interface = pn.chat.ChatInterface(
    callback=get_response,
    user="You",
    show_clear=False,
    show_undo=False,
    width=600,
    height=400,
    placeholder_text="Enter a natural language query (e.g., 'Show me all employees with salary above 50000')",
    name="SQLCoder Chat"
)

app = pn.Column(
    "# Natural Language to SQL Chat Interface",
    chat_interface,
    sizing_mode="stretch_width"
)

pn.extension()
app.servable()