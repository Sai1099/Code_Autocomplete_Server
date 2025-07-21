import asyncio
from mistralai import Mistral
from mistralai.models import UserMessage,SystemMessage




async def main():
    api_key = "J3Zf3rv43EDL9vVWJdMZgyjRC95SXHJI"
    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)
    for _ in range(10):
        user_input = str(input())
        response = await client.chat.stream_async(
            model=model,
            messages = [
                SystemMessage(content="Assume you are a good programmer and I will give you the incomplete code. Now you will give me only the unseen complete code, that's it. Don't respond to anything, just give me the final code. and only give me the line code only the single line code based on the given codes please complete the single code in the line like giving the suggestions like intellij just want a one lune to complete only "),
                UserMessage(content=user_input),
            ]
        )
        async for chunk in response:
            if chunk.data.choices[0].delta.content is not None:
                print(chunk.data.choices[0].delta.content, end="")

if __name__ == "__main__":
    asyncio.run(main())
