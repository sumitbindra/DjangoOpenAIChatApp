from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from .models import Chat
import openai
from decouple import config
import os, time
from gtts import gTTS
from django.conf import settings


openai.api_key = config('openai_key')

@login_required
def home(request):
    return redirect('chat')

@login_required
def chat(request):
    n = 20  # Get the most recent 'n' messages for display and context

    if request.method == 'POST':
        message = request.POST['message']
        
        if settings.DEBUG:
            print("Start reading database:", time.strftime("%H:%M:%S", time.localtime()))

        history = Chat.objects.filter(user=request.user).order_by('-created_at')[:n]

        if settings.DEBUG:
            print("Done reading database / Start context setting:", time.strftime("%H:%M:%S", time.localtime()))

        # Get the most recent n messages and join them into a single context string
        max_tokens = 2048  # Set the maximum token limit
        context = []
        for chat in history:
            msg=[
                {"role": "user", "content": chat.message},
                {"role": "assistant", "content": chat.response}
            ]
            context += msg
        context = context[:max_tokens]  # Truncate the context string to fit within the token limit
        
        if settings.DEBUG:
            #print(context)
            print("Done context setting / Start system messages:", time.strftime("%H:%M:%S", time.localtime()))

        system_msg = [
            {"role": "system", 
             "content": "Imagine you are a friend to a five year old child and your name is Jack."},
        ]

        system_msg = system_msg + [
            {"role": "system", 
             "content": "The child is trying to interact with you as a friend."},
        ]

        system_msg = system_msg + [
            {"role": "system", 
             "content": "Respond to the chile in age appropriate, clear and simplified english language that a five year old can understand."},
        ]

        system_msg = system_msg +  [
            {"role": "system", 
             "content": "If the child uses inappropriate language, you must correct them and respond by informing them that this behavior is unacceptable."},
        ]

        system_msg = system_msg +  [
            {"role": "system", 
             "content": "Do not call yourself an AI language model or any such term. Call yourself Jack the friendly robot."},
        ]

        system_msg = system_msg +  [
            {"role": "system", 
             "content": "Keep your sentences short. Maximum one to two sentences per response."},
        ]

        if settings.DEBUG:
            print("Done system messages / Start get openai response:", time.strftime("%H:%M:%S", time.localtime()))

        #print (system_msg + context)
        
        # Generate the AI response
        # This code is for chatgpt
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= system_msg + context + [
                {"role": "user", "content": message}
            ]
        )
        
        if settings.DEBUG:
            print("Done get openai response / Start create DB record:", time.strftime("%H:%M:%S", time.localtime()))

        if response.choices[0].message!=None:
            response_text =  response.choices[0].message.content
            Chat.objects.create(user=request.user, message=message, response=response_text)
            

            """ ### This is added to enable text to voice for response
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

            try:
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

    if settings.DEBUG:
        print("Done create DB record:", time.strftime("%H:%M:%S", time.localtime()))

    chats = Chat.objects.filter(user=request.user).order_by('-created_at')[:n]
    
    return render(request, 'chat.html', {'chats': chats})
