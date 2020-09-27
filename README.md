# product-availability-checker

## Install  dependencies

`pip3 install schedule requests pyyaml lxml retry --user`

## Configure environment variables

In order to run the script you need to export the following environment variables:

* `TELEGRAM_BOT_TOKEN`: Is the token of the bot you will use, please see section "Creating your bot Section"
* `TELEGRAM_BOT_CHAT_ID`: The id of the chat where the bot will send messages, please see section "Creating your bot Section"

## Creating your bot

On Telegram, search @BotFather, send him a "/start" message
Send another "/newbot" message, then follow the instructions to setup a name and a username
Your bot is now ready, be sure to save a backup of your API token, and correct, this API token is your bot_token.
Export it as your `TELEGRAM_BOT_TOKEN` environment variable

## Configure bot

On Telegram, search your bot (by the username you just created), press the “Start” button or send a “/start” message.

Open a new tab with your browser, enter https://api.telegram.org/bot<yourtoken>/getUpdates , replace <yourtoken> with your API token, press enter and you should see something like this:
{"ok":true,"result":[{"update_id":77xxxxxxx,
"message":{"message_id":550,"from":{"id":34xxxxxxx,"is_bot":false,"first_name":"Man Hay","last_name":"Hong","username":"manhay212","language_code":"en-HK"}

Look for “id”, for instance, 34xxxxxxx above is my chat id. Look for yours and export it as your `TELEGRAM_BOT_CHAT_ID` environment variable.

## Configure Products

Edit `products.yml` and add the products you want to check.

## Run the tool

`./product_checker.py`
