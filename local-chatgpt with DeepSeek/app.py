from openai import OpenAI
import chainlit as cl
import json,csv,os
from datetime import datetime,timedelta
ollama_client = OpenAI(base_url="http://localhost:11434/v1",api_key="ollama")
ollama_deepseek_model={'client':'OpenAI','api':'ollama','model':'deepseek-r1:1.5b'}
ollama_gemma3_model={'client':'OpenAI','api':'ollama','model':'gemma3:latest'}
def collect_chat_history(response):
  file_exist=os.path.exists(r'D:\Github\AI-Engineering\Pratice\chat_history.csv')
  with open(r'D:\Github\AI-Engineering\Pratice\chat_history.csv','a',newline='', encoding="utf-8-sig") as save_response:
    writer=csv.DictWriter(save_response,fieldnames=response.keys())
    if not file_exist:
      writer.writeheader()
    writer.writerow(response)
def chat_with_openai(client,messages,model,system=None,temperature=0.5,max_tokens=1800):
    params={"model":model['model'],"messages": messages,"temperature": temperature,"max_tokens": max_tokens}
    response = client.chat.completions.create(**params)
    usage = response.usage
    details={"Client": model['client'],'api':model['api'],'model':model['model'],"Time": datetime.now().isoformat(),"id": response.id,"role": response.choices[0].message.role,
        "stop_reason": response.choices[0].finish_reason,"input_tokens": usage.prompt_tokens,"output_tokens": usage.completion_tokens,"total_tokens": usage.total_tokens,
        "user": messages[-1]["content"] ,"assistant": response.choices[0].message.content}
    collect_chat_history(details)
    return response
@cl.on_chat_start
async def start_chat():
    cl.user_session.set("interaction", [{"role": "system","content": "You are a helpful assistant."}])
    msg = cl.Message(content="")
    start_message = "Hello, I'm your 100% local alternative to ChatGPT running on DeepSeek-R1. How can I help you today?"
    for token in start_message:
        await msg.stream_token(token)
    await msg.send()

@cl.step(type='tool')
async def tool(input_message):
    interaction = cl.user_session.get("interaction")
    interaction.append({"role": "user","content": input_message})
    response=chat_with_openai(ollama_client,interaction,ollama_gemma3_model)
    interaction.append({"role": "assistant","content": response.choices[0].message.content})
    return response
@cl.on_message
async def main(message:cl.Message):
    tool_res = await tool(message.content)
    msg = cl.Message(content="")
    for token in tool_res.choices[0].message.content:
        await msg.stream_token(token)
    await msg.send()