# Third-party imports
import attr
from openai import OpenAI
from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from utils import send_message, logger
import requests
from aliexpress_api import AliexpressApi, models
import re

from parsel import Selector
from typing import Dict
import httpx
import json

app = FastAPI()
welcome_msg = f"question: 'Hi there, I'm your shopping buddy, an expert that can help you find the product that best suits your needs and limits. You can ask me to recommend a product or you can specify what you are looking for. I will give you recommendations, explain the reasoning behind them and even direct you to the cheapest site to purchase that product.'"
aliexpress = AliexpressApi('510446', 'mo9VdZB7r3807hwwuev0x9tOhDrUf0CB', models.Language.EN, models.Currency.EUR, 'BOB')
# Set up the OpenAI API client
client = OpenAI(
    # This is the default and can be omitted
    api_key=config("OPENAI_API_KEY"),
)
# whatsapp_number = config("TO_NUMBER")

def split_by_numbered_list(data):
    lines = data.splitlines()
    array = []
    for line in lines:
        item = line[line.index('.') + 2:]
        array.append(item)
    return array

def get_product_ids(product_names):
    product_ids = []
    for product_name in product_names:
        
        try:
            hotproducts = aliexpress.get_hotproducts(keywords=product_name)
            product_id = hotproducts.products[0].product_id
            product_ids.append(product_id)
        except:
            product_ids = product_names
            break
    return product_ids

def get_affiliate_link(product_id):
    affiliate_link = aliexpress.get_affiliate_links(f"https://aliexpress.com/item/{product_id}.html")
    return affiliate_link[0].promotion_link

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
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.1
        )

    chatgpt_response = response.choices[0].message.content

    messages = [
        {
        "role": "system",
        "content": "You are an AI model that provides information based on general market trends and known products. You can try on google search as well."
        },
        {
        "role": "user",
        "content": f"{chatgpt_response}." 
                    f"just give me top three product name without any description and start text from the above text. I don't need any other text. only 3 product name."
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.1
        )

    
    chatgpt_response = response.choices[0].message.content
    length = 0

    while True:
        if (len(chatgpt_response) - length) > 1500:
            token_message = chatgpt_response[length:1500]
            length = length + 1500
            product_names = split_by_numbered_list(token_message)
            product_ids = get_product_ids(product_names)
            if(product_ids==product_names):
                send_message(whatsapp_number, product_names)
            else:
                product_ids = get_product_ids(product_names)
                for product_id in product_ids:
                    link_text = (get_affiliate_link(product_id))
                    send_message(whatsapp_number, link_text)

        if (len(chatgpt_response) - length) <= 1500: 
            token_message = chatgpt_response[length:1500]
            product_names = split_by_numbered_list(token_message)
            product_ids = get_product_ids(product_names)
            if(product_ids==product_names):
                send_message(whatsapp_number, product_names)
            else:
                product_ids = get_product_ids(product_names)
                for product_id in product_ids:
                    link_text = (get_affiliate_link(product_id))
                    send_message(whatsapp_number, link_text)
            break

    return ""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)