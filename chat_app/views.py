from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from .models import Chat
import openai
from decouple import config
import os, time
from gtts import gTTS
import pygame

openai.api_key = config('openai_key')

@login_required
def home(request):
    return redirect('chat')

@login_required
def chat(request):
    if request.method == 'POST':
        message = request.POST['message']
        history = Chat.objects.filter(user=request.user).order_by('-created_at')

        # Get the most recent n messages and join them into a single context string
        max_tokens = 2048  # Set the maximum token limit
        n = 15  # Get the most recent 5 messages
        context = []
        for chat in history[:n]:
            msg=[
                {"role": "user", "content": chat.message},
                {"role": "assistant", "content": chat.response}
            ]
            context += msg
        context = context[:max_tokens]  # Truncate the context string to fit within the token limit
        #print(context)
        
        systemmessages = [
            {"role": "system", 
             "content": "Imagine you are not an AI assistant. You are a friend to a five year old child and your name is Jack. Respond to their message using extremely sensitive, clear and concise language. If the child uses inappropriate language, you must respond by informing the child that the language they are using is unacceptable."},
        ]

        #print (systemmessages + context)

        # Generate the AI response
        # This code is for chatgpt
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= systemmessages + context + [
                {"role": "user", "content": message}
            ]
        )

        if response.choices[0].message!=None:
            response_text =  response.choices[0].message.content
            Chat.objects.create(user=request.user, message=message, response=response_text)
            

            ### This is added to enable text to voice for response
            TTS = gTTS(text=response_text, lang='en')

            # Save to mp3 in current dir.
            TTS.save("voice.mp3")

            # Plays the mp3 using the default app on your system
            # Initialize Pygame
            pygame.init()

            # Initialize Pygame mixer
            pygame.mixer.init()

            # Load the audio file
            pygame.mixer.music.load("voice.mp3")

            # Play the audio file
            pygame.mixer.music.play()

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Quit Pygame
            pygame.quit()

            """ try:
                #os.system("start voice.mp3")
                #playsound("voice.mp3")
                # Load the audio file
                audio = AudioSegment.from_file("voice.mp3", format="mp3")
                
                print(audio)
                # Play the audio file
                play(audio)
                #winsound.PlaySound("voice.mp3", winsound.SND_FILENAME)
            except Exception as e:
                print('Error occurred while playing sound: ', e) """

            # Wait for the audio to finish playing before deleting the file
            #time.sleep(3)

            # Delete the audio file
            #os.remove("voice.mp3")

        else :
            response_text = 'Failed to Generate response!'
    
        # This code is for pre CHATGPT DaVinci
        # Tokenize the context string
        # Load the GPT-2 tokenizer and model
        """ tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        context_tokens = tokenizer.encode(context)
        context_tokens = context_tokens[-(max_tokens-1):]  # Keep only the most recent tokens that fit within the token limit
        context = tokenizer.decode(context_tokens, skip_special_tokens=True) """

        """ response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=context + f"User: {message}\nAssistant:",
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response_text = response.choices[0].text.strip() """

    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'chat.html', {'chats': chats})
