import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from app.services.recommend_service import get_recommended_products, update_like_status
from app.models import ChatRecommend

def index(request):
    chat_id = request.GET.get('chat_id')
    if chat_id is None:
        return JsonResponse({"error": "chat_id is required"}, status=400)

    products = get_recommended_products(chat_id)
    return JsonResponse({"products": products})

@csrf_exempt
@require_POST
def like(request, recommend_id):
    try:
        data = json.loads(request.body)
        is_liked = data.get("is_liked", False)
        update_like_status(recommend_id, is_liked)
        return JsonResponse({"message": "Product liked successfully"})
    except ChatRecommend.DoesNotExist:
        return JsonResponse({"error": "Recommendation not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
