# Third-party imports
import attr
from openai import OpenAI
from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
# from models import Conversation, User, SessionLocal
from utils import send_message, logger


app = FastAPI()
welcome_msg = "Hi there, I'm your shopping buddy, an expert that can help you find the product that best suits your needs and limits. You can ask me to recommend a product or you can specify what you are looking for. I will give you recommendations, explain the reasoning behind them and even direct you to the cheapest site to purchase that product."
# Set up the OpenAI API client
client = OpenAI(
    # This is the default and can be omitted
    api_key=config("OPENAI_API_KEY"),
)
# whatsapp_number = config("TO_NUMBER")

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

    #check message validation
    checm_msg = f"Hi there, I'm your shopping buddy, an expert that can help you find the product that best suits your needs and limits. You can ask me to recommend a product or you can specify what you are looking for. I will give you recommendations, explain the reasoning behind them and even direct you to the cheapest site to purchase that product.  the repliy message is the '{Body}'. Is this right question?  answer with only 'Yes' or 'No'."
    
    messages = [{"role": "user", "content": checm_msg}]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5
        )

    chatgpt_response = response.choices[0].message.content


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
    send_message(whatsapp_number, chatgpt_response)
    return ""
