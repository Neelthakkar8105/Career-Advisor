import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json

HF_API_TOKEN = ""  # 🔁 Replace with your actual Hugging Face token

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            headers = {
                "Authorization": f"Bearer {HF_API_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": user_message
            }

            response = requests.post(
                "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
,
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and "generated_text" in result[0]:
                    bot_reply = result[0]["generated_text"]
                    return JsonResponse({ "reply": bot_reply })
                else:
                    return JsonResponse({ "error": "Unexpected response format from Hugging Face." })

            return JsonResponse({ "error": f"API error ({response.status_code}): {response.text}" })

        except Exception as e:
            return JsonResponse({ "error": f"Something went wrong: {str(e)}" })

    return JsonResponse({ "error": "Invalid request method." })

def chat_page(request):
    return render(request, "chatbot/chat.html")
