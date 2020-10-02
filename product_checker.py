#!/usr/bin/python3

import sys
from lxml import html
import requests
from time import sleep
import time
import schedule
import logging
import yaml
import urllib.parse
import random
from retry import retry
import os
import socket


## Logging Config
logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

## Validations
serverName=socket.gethostname()
botToken = 'TELEGRAM_BOT_TOKEN'
botChatId = 'TELEGRAM_BOT_CHAT_ID'
if botToken not in os.environ or botChatId not in os.environ:
  logger.error("Environment variables TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_CHAT_ID are mandatory.")
  exit(1)

if len(sys.argv) > 1:
  config_file = sys.argv[1]
else:
  config_file = "config.yml"

if (not os.path.isfile(config_file)):
  logger.error(f'Products database {config_file} does not exists.')
  exit(1)

logger.info(f"Using config.yml as products database on server {serverName}.")
with open(config_file) as file:
  # The FullLoader parameter handles the conversion from YAML
  # scalar values to Python the dictionary format
  config = yaml.load(file, Loader=yaml.FullLoader)

  user_agent = config["userAgent"]
  logger.info(f'Working with user agent: {user_agent}')

def sendMessage(bot_message):
  bot_message = bot_message.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
  bot_token = os.environ.get(botToken)
  bot_chatID = os.environ.get(botChatId)
  send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + urllib.parse.quote(bot_message)

  response = requests.get(send_text)
  logger.debug("Telegram response: ")

  json_response = response.json()
  if json_response["ok"] == False:
    logger.error(f'Error sending telegram message: {json_response}')

  return json_response

def sendAvailableProductMessage(product):
  logger.info(f'Sending Available Message!!! >> {product["Url"]}')
  return sendMessage(f'The product {product["Url"]} is available! HURRY UP!!')

def check_availability(store, productUrl):
  randomInt =random.randint(1, 100)
  # headers = ({'User-Agent': "Mozilla/5.0 (X11; Linux x86_64{randomInt}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36{randomInt}', 'Accept-Language': 'en-US, en;q=0.5".format(randomInt=randomInt)})
  headers = ({'User-Agent':
            user_agent.format(randomInt=randomInt),
            'Accept-Language': 'en-US, en;q=0.5'})

  if store == "Amazon":
    xpath_availability = '//div[@id ="availability"]//text()'
  elif store == "NewEgg":
    xpath_availability = '//div[@id ="availability"]//text()'
    logger.error("Newegg is not supported yet...")
    return False
  else:
    logger.info(f'Unknown store {store}.')
    return False

  # Checking availability
  logger.debug(f'Loading {productUrl}')
  page = requests.get(productUrl, headers = headers)

  # parsing the html content
  doc = html.fromstring(page.content)
  logger.debug(f'response: {page.content}')

  raw_availability = doc.xpath(xpath_availability)
  availability = ''.join(raw_availability).strip().replace('\n', '') if raw_availability else None
  if availability is not None:
    logger.info(f'Product Availability: {availability}')
    # If is unavailable
    # return availability.lower().find("unavailable") == -1
    # If has the word in the stock and do not has the word unavailable
    return availability.lower().find("in stock") != -1 and availability.lower().find("unavailable") == -1
  else:
    logger.error(f'We have a problem scrapping this url: {productUrl}, sending Message')
    logger.error(f'{page.content}')
    sendMessage(f'Error on server {serverName}, problem parsing {productUrl}, please check!')
    raise Exception('Error Parsing', f'product {productUrl}')

  return False

# scheduling same code to run multiple
# times after every 1 minute
#@retry(delay=10, backoff=2, logger=logger, max_delay=300)
def job():
  print("-------------------------------------------------------------------------------------------")
  logger.info("Loading products from {products}".format(products=config_file))
  with open(config_file) as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    config = yaml.load(file, Loader=yaml.FullLoader)

  logger.info("Starting Tracking....")
  products = config["products"]
  for store in products:
    i = 0
    total = len(products[store])
    logger.info(f'Working with {store}, tracking {total} products.')
    for product in products[store]:
      i = i+1
      logger.info(f'Checking availability of product {product["Name"] if "Name" in product else product["Url"]} ({i} of {total}).')
      result = check_availability(store, product["Url"])
      if result:
        logger.info("Product AVAILABLE HURRY UP!!!")
        sendAvailableProductMessage(product)
      else:
        logger.info("Product unavailable :(...")

      # because continuous checks in milliseconds or few seconds blocks your request
      sleep(2)
    #ReadAsin()

# Run the job The first time, then schedule next executions.
job();
schedule.every(30).seconds.do(job)

while True:

    # running all pending tasks/jobs
    schedule.run_pending()
    time.sleep(1)
