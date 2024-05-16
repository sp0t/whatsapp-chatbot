# Third-party imports
import attr
from openai import OpenAI
from fastapi import FastAPI, Form, Depends
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
whatsapp_number = config("TO_NUMBER")

# Dependency
# def get_db():
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()

@app.post("/message")
# async def reply(Body: str = Form(), db: Session = Depends(get_db)):
async def reply(Body: str = Form()):
    # Call the OpenAI API to generate text with GPT-3.5
    print(Body)

    response = client.chat.completions.create(
        messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
        model="gpt-3.5-turbo",
    )

    print(response)


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
    # send_message(whatsapp_number, chat_response)
    return ""
