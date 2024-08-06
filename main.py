# Third-party imports
import attr
from openai import OpenAI
from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

# Internal imports
# from models import Conversation, User, SessionLocal
from utils import send_message, logger


app = FastAPI()
welcome_msg = f"question: 'Hi there, I'm your shopping buddy, an expert that can help you find the product that best suits your needs and limits. You can ask me to recommend a product or you can specify what you are looking for. I will give you recommendations, explain the reasoning behind them and even direct you to the cheapest site to purchase that product.'"
# Set up the OpenAI API client
client = OpenAI(
    # This is the default and can be omitted
    api_key=config("OPENAI_API_KEY"),
)
# whatsapp_number = config("TO_NUMBER")

def find_product_link(search_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = Request.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a'):
        href = link.get('href')
        return href
    return "No Amazon link found"

# Dependency
# def get_db():
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()

@app.post("/message")
# async def reply(Body: str = Form(), db: Session = Depends(get_db)):
async def reply(request: Request, Body: str = Form()):

    # Extract the phone number from the incoming webhook request
    form_data = await request.form()
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]
    print(f"Sending the ChatGPT response to this number: {whatsapp_number}")

    # Check if the user exists and has received the welcome message
    # user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
    # if not user:
    #     # First time user, send welcome message and store in DB
    #     user = User(whatsapp_number=whatsapp_number, has_received_welcome=True)
    #     db.add(user)
    #     db.commit()
    #     send_message(whatsapp_number, 
    #     "Hi there, I'm your shopping buddy, an expert that can help you find the product that best suits your needs and limits. You can ask me to recommend a product or you can specify what you are looking for (or ask me to ask you questions about a product I want to buy). I will give you recommendations, explain the reasoning behind them and even direct you to the cheapest site to purchase that product."
    #     )
    #     return ""

    # messages = [{"role": "user", "content":Body}]
    messages = [
        {
        "role": "system",
        "content": "You are an AI model that provides information based on general market trends and known products. You can try on google search as well."
        },
        {
        "role": "user",
        "content": f"[{Body}]."
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.2
        )

    chatgpt_response = response.choices[0].message.content
    length = 0

    while True:
        if (len(chatgpt_response) - length) > 1500:
            token_message = chatgpt_response[length:1500]
            length = length + 1500
            print(token_message)
            send_message(whatsapp_number, token_message)

        if (len(chatgpt_response) - length) <= 1500: 
            token_message = chatgpt_response[length:1500]
            print(token_message)
            send_message(whatsapp_number, token_message)
            break



    # Call the OpenAI API to generate text with GPT-4.0

    # messages = [{"role": "user", "content": Body}]
    # messages.append({"role": "system", "content": "You're an investor, a serial founder and you've sold many startups. You understand nothing but business."})
    # response = client.chat.completions.create(
    #     model="gpt-4-turbo",
    #     messages=messages,
    #     max_tokens=200,
    #     n=1,
    #     stop=None,
    #     temperature=0.5
    #     )

    # # The generated text
    # chatgpt_response = response.choices[0].message.content

    # Store the conversation in the database
    # try:
    #     conversation = Conversation(
    #         sender=whatsapp_number,
    #         message=Body,
    #         response=chat_response
    #         )
    #     db.add(conversation)
    #     db.commit()
    #     logger.info(f"Conversation #{conversation.id} stored in database")
    # except SQLAlchemyError as e:
    #     db.rollback()
    #     logger.error(f"Error storing conversation in database: {e}")
    # send_message(whatsapp_number, chatgpt_response)
    return ""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)