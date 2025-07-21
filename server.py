from fastapi import FastAPI, Request, status
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import RequestValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import List
import os
import json
import traceback
from fastapi import FastAPI, StreamingResponse
from typing import Generator
import asyncio
from mistralai import Mistral
from mistralai.models import UserMessage,SystemMessage

class my_data(BaseModel):
    data_id: int
    data: List[str]

app = FastAPI()

API_KEY = os.getenv("API_KEY")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation error: {exc}")
    print(f"Request body: {await request.body()}")
    return PlainTextResponse(f"Validation Error: {exc}", status_code=422)

@app.api_route("/", methods=["GET", "POST"])
async def main(request: Request):
    if request.method == "GET":
        return PlainTextResponse(f"Hello This is Server, {status.HTTP_200_OK}", status_code=status.HTTP_200_OK)
    elif request.method == "POST":
        return PlainTextResponse(f"This is Post, {status.HTTP_200_OK}", status_code=status.HTTP_200_OK)
    else:
        return PlainTextResponse(f"Error, {status.HTTP_400_BAD_REQUEST}", status_code=status.HTTP_400_BAD_REQUEST)

@app.get("/api-for-ai")
async def get_ai_info():
    return PlainTextResponse(f"Hello this is AI Calling API,{status.HTTP_200_OK}", status_code=status.HTTP_200_OK)

@app.post("/api-for-ai")
async def main_controller(mydata: my_data):
    try:
        print(f"Received data: {mydata}")
        
        if not API_KEY:
            raise RuntimeError("Missing Google GenAI API Key")

        # ✅ Use api_key in config parameter
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=1.0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            google_api_key=API_KEY  # ✅ << USE THIS
        )

        human_message = (
            f"{mydata.data} this is the code for it so please give me the incomplete code, "
            f"don't give me the complete code. I only want the json file with unseen code."
        )

        prompt = [
            (
                "system",
                """you are a main programmer. You have to complete the code based on the partial input from the user. 
                Only return JSON structure with key "unseen_data"."""
            ),
            (
                "human",
                human_message
            )
        ]

        ai_response = llm.invoke(prompt)

        main_data = str(ai_response.content)
        start_idx = main_data.find("{")
        end_idx = main_data.rfind("}")
        json_file = main_data[start_idx:end_idx+1]
        json_cleaned_data = json.loads(json_file.strip())
        the_real_data = json_cleaned_data["unseen_data"]

        return PlainTextResponse(f"{the_real_data}", status_code=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error in main_controller: {e}")
        print(traceback.format_exc())
        return PlainTextResponse(f"Internal server error: {str(e)}", status_code=500)
    


model = "mistral-large-latest"
client = Mistral(api_key=os.getenv("MIST_API"))

async def my_streaming_function(user_input: str):
    response = await client.chat.stream_async(
        model=model,
        messages=[
            SystemMessage(content="Assume you are a good programmer and I will give you the incomplete code. Now you will give me only the unseen complete code, that's it. Don't respond to anything, just give me the final code. and only give me the line code only the single line code based on the given codes please complete the single code in the line like giving the suggestions like intellij just want a one lune to complete only"),
            UserMessage(content=user_input),
        ]
    )

    async def event_generator():
        async for chunk in response:
            if chunk.data.choices[0].delta.content:
                yield chunk.data.choices[0].delta.content

    return event_generator()

@app.api_route("/stream", methods=["POST"])
async def stream_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("user_input", "")
    return StreamingResponse(await my_streaming_function(user_input), media_type="text/plain")