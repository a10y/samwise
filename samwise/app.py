from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
from samwise.utils import get_tailscale_ip
from PIL import Image
from pillow_heif import register_heif_opener
from pydantic import BaseModel

import googlesearch as google
import io
import llama_cpp

register_heif_opener()

app = FastAPI()

# Load the model from file
llm = llama_cpp.Llama("llama2_gguf.bin", n_gpu_layers=99, n_threads=4, n_ctx=1024)

class ChatRequest(BaseModel):
    text: str


# simple file upload and saving mechanism
@app.post("/tasks/upload")
async def upload_image(file: Annotated[bytes, File()]) -> str:
    print("receiving image file", len(file))
    im = Image.open(io.BytesIO(file))
    print("image size: {} x {}".format(*im.size))
    return "received"

@app.post("/tasks/describe")
async def upload_image(file: Annotated[bytes, File()]) -> str:
    im = Image.open(io.BytesIO(file))
    print("image size: {} x {}".format(*im.size))
    # Return the output of the vision model on this shit.
    return "received"

@app.post("/tasks/chat")
async def do_chat(user_prompt: ChatRequest) -> str:
    print(f"TASK: CHAT {user_prompt}")

    # Feed user's prompt through google search first to see answers
    NUM_GOOGS = 10
    search_context = ""
    for result in google.search(user_prompt.text, num_results=NUM_GOOGS, advanced=True):
        search_context += f"Title: {result.title}\nDescription: {result.description}\n\n"
    search_context = search_context.strip()

    PROMPT = f"""
### Instruction:

You are Samwise, my (Andrew Duffy's) personal AI assistant. You can answer any question, and are especially proficient and confident in skills of:

- Programming and software engineering
- Scientific discovery
- History, including ancient history, early modern history, American Studies, Asian Studies, and anthropology
- Finance, venture capital and investing

You answer questions concisely, without preamble.

Here is my (Andrew's) request:
{user_prompt.text}

Here are the top {NUM_GOOGS} search results on the Internet for Andrew's question:

{search_context}

Now given this, craft a respons to the question.

### Response:
""".lstrip()

    return llm(PROMPT, stream=False, max_tokens=3072)["choices"][0]["text"]

	
if __name__ == "__main__":
    # Bind to the tailscale veth
    import uvicorn
    uvicorn.run(app, host=get_tailscale_ip(), port=5001)
