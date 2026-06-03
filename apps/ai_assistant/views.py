import json, uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import AIChatHistory
from apps.universities.models import University, Faculty

SYSTEM_PROMPT = """
You are UniBot — an expert AI assistant for university admissions and higher education in Uzbekistan.

You may answer ONLY questions related to:

- universities
- admissions
- DTM exams
- study programs
- scholarships
- careers
- higher education
- student life
- academic guidance

If a user asks something unrelated (cooking, sports, politics, programming, health, entertainment, etc.), politely refuse and redirect them.

Example response:

"I am a university admissions assistant and can only help with education-related topics such as universities, admissions, scholarships, and careers."

Never answer unrelated questions.
"""
def get_or_create_session(request):
    if 'chat_session' not in request.session:
        request.session['chat_session'] = str(uuid.uuid4())
    return request.session['chat_session']

@ensure_csrf_cookie
def chat_view(request):
    session = get_or_create_session(request)
    history = AIChatHistory.objects.filter(session=session).order_by('created_at')[:50]
    return render(request, 'ai_assistant/chat.html', {'history': history})

@require_POST
def chat_api(request):
    try:
        data    = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        if not user_msg:
            return JsonResponse({'error': 'Empty message'}, status=400)

        session = get_or_create_session(request)
        user    = request.user if request.user.is_authenticated else None

        # Save user message
        AIChatHistory.objects.create(user=user, session=session, role='user', content=user_msg)

        # Build context from recent history
        recent = list(AIChatHistory.objects.filter(session=session).order_by('-created_at')[:10])[::-1]
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in recent[:-1]:  # exclude the one we just saved
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": user_msg})

        # Call OpenAI
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            reply = ("⚠️ AI assistant is not configured yet. "
                     "Please add OPENAI_API_KEY to your .env file.\n\n"
                     "In the meantime, use the Search page to find university information!")
        else:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp   = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )
            reply = resp.choices[0].message.content.strip()

        # Save assistant reply
        AIChatHistory.objects.create(user=user, session=session, role='assistant', content=reply)
        return JsonResponse({'reply': reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def clear_chat(request):
    session = request.session.get('chat_session')
    if session:
        AIChatHistory.objects.filter(session=session).delete()
        del request.session['chat_session']
    return JsonResponse({'status': 'cleared'})
