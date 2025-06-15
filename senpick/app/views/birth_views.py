from django.shortcuts import render
from django.http import JsonResponse
from app.models import User
from giftgraph.graph import gift_fsm 
import re

def birth(request):
    return render(request, 'birth.html')

def birth_recommend_products(request):
    user_id = request.session.get("user_id")
    user = User.objects.prefetch_related('preferences__prefer_type').filter(user_id=user_id).first()

    if not user:
        return JsonResponse({'error': '사용자를 찾을 수 없습니다.'}, status=404)
    
    # 사용자의 선호 태그를 가져옵니다.
    prefer_types = user.preferences.all() if user and user.preferences.exists() else []
    prefer_tags = [prefer.prefer_type.type_name for prefer in prefer_types]
    
    # 년도로 나이 계산
    if user.birth:
        birth_year = int(user.birth[:4])
        current_year = int(request.session.get('current_year', 2025))  # 현재 연도는 세션에서 가져오거나 기본값 사용
        age = current_year - birth_year
        
    situation_info = {
        "closeness": "본인",
        "emotion": "축하, 기쁨",
        "preferred_style": ",".join(prefer_tags),
        "price_range": "적당한 가격",
    }

    recipient_info = {
        'gender': user.gender,
        'ageGroup': age,
        'relation': "본인",
        'anniversary': "생일",
    }

    state = {
        "chat_history": [],
        "recipient_info": recipient_info,
        "situation_info": situation_info,
        "output": "",
    }
    
    # gift_fsm 함수를 호출하여 추천 상품을 가져옵니다.
    res = gift_fsm.invoke(state)
    if isinstance(res, dict):
        state = res
        output = state.get("output", "").replace("bot: ", "")
        if situation_info:
            _, products = extract_products_from_response(output)
            recommend_products = []
            for product in products:
                if "상품명:" in product["brand"]:
                    product["brand"] = ""
                recommend_products.append({
                    "id": product.get("id", 0),
                    "imageUrl": product.get("imageUrl", ""),
                    "brand": product.get("brand", ""),
                    "title": product.get("title", ""),
                    "reason": product.get("reason", ""),
                })
    
    return JsonResponse({
        'products': recommend_products
    })
    
def extract_products_from_response(data):
    # 상품 블록 분리
    data = re.split(r'\n\d+\.\s*', data.strip())
    msg = data[0]
    blocks = data[1:]

    # JSON 배열 구성
    items = []
    for idx, block in enumerate(blocks):
        brand = re.search(r'-\s*\*?\s*\*?\s*브랜드\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)
        name = re.search(r'-\s*\*?\s*\*?\s*상품명\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)
        price = re.search(r'-\s*\*?\s*\*?\s*가격\s*\*?\s*\*?\s*:\s*₩\s*([\d,]+)', block).group(1)
        # 이미지 robust 패턴
        image_match = re.search(
            r'-\s*\*?\s*\*?\s*이미지\s*\*?\s*\*?\s*:\s*(?:!\[.*?\]\(\s*(.*?)\s*\)|(\S+))',
            block
        )
        image = image_match.group(1) or image_match.group(2) if image_match else None

        # 링크 robust 패턴
        link_match = re.search(
            r'-\s*\*?\s*\*?\s*링크\s*\*?\s*\*?\s*:\s*(?:\[.*?\]\(\s*(.*?)\s*\)|(\S+))',
            block
        )
        product_url = link_match.group(1) or link_match.group(2) if link_match else None

        reason = re.search(r'-\s*\*?\s*\*?\s*추천\s*이유\s*\*?\s*\*?\s*:\s*(.*)', block).group(1)

        items.append({
            # "id": len(st.session_state.all_products) + idx,
            "brand": brand,
            "title": name,
            "price": price,
            "imageUrl": image,
            "product_url": product_url,
            "reason": reason
        })

    return msg, items