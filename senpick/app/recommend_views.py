from django.http import JsonResponse
from app.models import ChatRecommend, Product
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

def index(request):
    chat_id = request.GET.get('chat_id')
    if chat_id is None:
        return JsonResponse({"error": "chat_id is required"}, status=400)
    
    # 추천 목록 가져오기
    recommend_products = ChatRecommend.objects.filter(chat_id=chat_id)

    # product_id 값만 뽑기 → 리스트 만들기
    product_ids = recommend_products.values_list('product_id', flat=True)

    # Product 쿼리 → IN 조회 (쿼리 1번으로 해결)
    products_qs = Product.objects.filter(product_id__in=product_ids)

    # product_id → Product 객체 dict 로 변환 (빠른 lookup 용)
    products_dict = {p.product_id: p for p in products_qs}

    # 최종 products list 구성
    products = []
    for recommend in recommend_products:
        product = products_dict.get(recommend.product_id_id)
        if product:
            products.append({
                "recommend_id": recommend.rcmd_id,
                # "product_id": product.product_id,
                "title": product.name,
                "image_url": product.image_url,
                "price": product.price,
                "product_url": product.product_url,
                "is_liked": recommend.is_liked,
            })

    return JsonResponse({"products": products})

@csrf_exempt
@require_POST
def like(request, recommend_id):
    data = json.loads(request.body)
    is_liked = data.get("is_liked", False)
    print(data)
    print(is_liked)
    
    if recommend_id is None:
        return JsonResponse({"error": "recommend_id are required"}, status=400)
    
    # 추천 목록에 추가
    chatRecommend = ChatRecommend.objects.get(rcmd_id=recommend_id)
    # is_liked 필드 업데이트
    chatRecommend.is_liked = is_liked

    chatRecommend.save()
    return JsonResponse({"message": "Product liked successfully"})