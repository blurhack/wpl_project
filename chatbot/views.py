from django.shortcuts import redirect, render

from flights.seed import ensure_seed_data

from .models import ChatMessage, FAQEntry


def bot_reply(text):
    lowered = text.lower()
    for faq in FAQEntry.objects.filter(active=True):
        if faq.keyword.lower() in lowered or any(word in lowered for word in faq.question.lower().split()[:3]):
            return faq.answer
    return 'I can help with coupons, seat selection, flight delay support, agent booking, and check-in/document status.'


def chatbot(request):
    ensure_seed_data()
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    if not ChatMessage.objects.filter(session_key=session_key).exists():
        ChatMessage.objects.create(session_key=session_key, role='bot', text='Hi, I am AeroBot. Ask me about coupons, delays, seats, or check-in.')
    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if text:
            ChatMessage.objects.create(session_key=session_key, role='user', text=text)
            ChatMessage.objects.create(session_key=session_key, role='bot', text=bot_reply(text))
        return redirect('chatbot')
    chat = ChatMessage.objects.filter(session_key=session_key).order_by('created_at')
    return render(request, 'reservations/chatbot.html', {'chat': chat})
