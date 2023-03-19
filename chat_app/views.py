from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Chat
import openai
from decouple import config

openai.api_key = config('openai_key')

@login_required
def chat(request):
    if request.method == 'POST':
        message = request.POST['message']
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"User: {message}\nAssistant:",
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response_text = response.choices[0].text.strip()

        Chat.objects.create(user=request.user, message=message, response=response_text)

    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat.html', {'chats': chats})
