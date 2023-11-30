@run_async
def gpt(update: Update, context: CallbackContext):
    # Get the text after /gpt command
    query = context.args if context.args else None

    if query:
        # Join the query into a single string
        prompt = ' '.join(query)

        # ChatGPT API URL
        api_url = f"https://chatgpt.apinepdev.workers.dev/?question={prompt}"

        # Make a request to ChatGPT API
        response = requests.get(api_url)

        if response.status_code == 200:
            # Extract the answer from the API response
            api_response = response.json()

            # Check if "join" key is present and remove it
            if "join" in api_response:
                del api_response["join"]

            answer = api_response.get("answer", "No answer received from ChatGPT.")
            
            # Send the answer back to the user
            update.message.reply_text(answer)
        else:
            update.message.reply_text("Error communicating with ChatGPT API.")
    else:
        update.message.reply_text("Please provide a prompt after /gpt command.")
      
