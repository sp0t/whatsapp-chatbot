# Third-party imports
import attr
from openai import OpenAI
from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
# from models import Conversation, SessionLocal
from utils import send_message, logger


app = FastAPI()
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

    # Call the OpenAI API to generate text with GPT-4.0

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {'role': "user", 'content': Body}
        ]
    )

    print(response.choices[0].message.content)


    # The generated text
    # chat_response = response.choices[0].text.strip()

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
    send_message(whatsapp_number, response.choices[0].message.content)
    return ""
